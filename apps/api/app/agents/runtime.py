from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.agents.draft_generation import (
    DraftGenerationContext,
    DraftGenerationResult,
    choose_draft_generator,
)
from app.agents.guards import find_forbidden_public_terms
from app.agents.qwenpaw_adapter import (
    FakeQwenPawWorkflowAdapter,
    QwenPawWorkflowContext,
    QwenPawWorkflowResult,
)
from app.agents.tool_registry import (
    ToolDefinition,
    ToolPermission,
    ToolRegistry,
    ToolRequest,
)
from app.agents.tool_recorder import ToolRecorder
from app.agents.workflow import (
    WorkflowExecutor,
    WorkflowNode,
    WorkflowNodeResult,
    WorkflowSpec,
    WorkflowState,
)
from app.schemas import (
    AgentDraft,
    AgentEvaluation,
    AgentModelCall,
    AgentRun,
    AgentStep,
    AgentToolCall,
    EventBrief,
    Incident,
    MerchantInteractionPackage,
    MerchantProfile,
    MerchantRuntimeState,
    MerchantTask,
    OperationalMetric,
    PlanVersion,
    PublicNotice,
    RecoveryProposal,
)
from app.services.recovery import build_recovery_proposal
from app.store import STORE
from app.tools.budget import split_budget
from app.tools.merchant import select_night_merchants
from app.tools.route import build_static_route


@dataclass
class AgentRuntimeResult:
    run: AgentRun
    steps: list[AgentStep]
    tool_calls: list[AgentToolCall]
    drafts: list[AgentDraft]
    model_calls: list[AgentModelCall]
    evaluations: list[AgentEvaluation]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


QWENPAW_WORKER_ORDER = [
    "MerchantEdgeWorker",
    "FieldOpsWorker",
    "PublicNoticeWorker",
    "ReviewEvidenceWorker",
]
QWENPAW_STEP_IDS = {
    "CentralOpsLeader": "qwenpaw_central_ops_leader",
    "MerchantEdgeWorker": "qwenpaw_merchant_edge_worker",
    "FieldOpsWorker": "qwenpaw_field_ops_worker",
    "PublicNoticeWorker": "qwenpaw_public_notice_worker",
    "ReviewEvidenceWorker": "qwenpaw_review_evidence_worker",
    "SafetyGateWorker": "qwenpaw_safety_gate_worker",
}
UNSAFE_QWENPAW_MUTATION_PATHS = {
    "approval_status",
    "publish_status",
    "approved_by",
    "approved_at",
    "inventory_status",
    "queue_status",
    "available_for_visitors",
    "plan_patch",
    "merchant_task_patch",
    "public_notice.publish_status",
    "apply_suggestion",
    "create_plan_version",
    "approve_recovery",
    "publish_notice",
    "coupon_redemption",
    "coupon_claim",
    "claim_coupon",
    "coupon_claim_status",
    "redeem_coupon",
    "redemption_status",
    "payment",
    "pos_transaction",
    "visitor_identity",
}


def _path_is_unsafe(path: str, key: str) -> bool:
    lowered_path = path.lower()
    lowered_key = key.lower()
    for unsafe_path in UNSAFE_QWENPAW_MUTATION_PATHS:
        lowered_unsafe = unsafe_path.lower()
        if lowered_key == lowered_unsafe:
            return True
        if lowered_path == lowered_unsafe or lowered_path.endswith(f".{lowered_unsafe}"):
            return True
    return False


def _find_unsafe_qwenpaw_paths(payload: Any) -> list[str]:
    found: set[str] = set()

    def visit(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                next_path = f"{path}.{key_text}" if path else key_text
                if _path_is_unsafe(next_path, key_text):
                    found.add(next_path)
                visit(child, next_path)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                next_path = f"{path}.{index}" if path else str(index)
                visit(item, next_path)

    visit(payload)
    return sorted(found)


def _fallback_qwenpaw_result(context: QwenPawWorkflowContext) -> QwenPawWorkflowResult:
    incident_ref = f"incident:{context.incident_id}"
    notice = "Some offers may be limited. Please follow the latest event page guidance."
    return QwenPawWorkflowResult(
        leader_decision={
            "assigned_workers": QWENPAW_WORKER_ORDER + ["SafetyGateWorker"],
            "input_refs": [incident_ref, *context.input_refs],
            "decision": "Unsafe shadow output was replaced with advisory-only fallback.",
        },
        worker_outputs=[
            {
                "agent_name": "MerchantEdgeWorker",
                "content": "Merchant impact requires organizer review before any live action.",
                "structured_payload": {
                    "merchant_impact_note": "Merchant capacity issue remains advisory-only.",
                    "evidence_refs": [incident_ref],
                },
            },
            {
                "agent_name": "FieldOpsWorker",
                "content": "Prepare backup capacity recommendation for organizer review.",
                "structured_payload": {
                    "recovery_rationale": "Fallback keeps the incident visible without applying changes.",
                    "recommended_action": "organizer_review_required",
                    "authoritative_mutation": False,
                },
            },
            {
                "agent_name": "PublicNoticeWorker",
                "content": notice,
                "structured_payload": {
                    "visitor_safe_notice_draft": notice,
                    "public_copy_ready": True,
                },
            },
            {
                "agent_name": "ReviewEvidenceWorker",
                "content": "Review should cite the incident and fallback safety evaluation.",
                "structured_payload": {
                    "review_evidence_refs": [incident_ref, f"touchpoint_metrics:{context.event_id}"],
                },
            },
        ],
        advisory_bundle={
            "recovery_rationale": "Unsafe shadow output was replaced before any operational action.",
            "visitor_safe_notice_draft": notice,
            "merchant_impact_note": "Organizer review is required before any live operational change.",
            "review_evidence_refs": [incident_ref, f"touchpoint_metrics:{context.event_id}"],
            "human_approval_required": True,
            "authoritative_mutation": False,
        },
        permission_requests=[],
        safety_notes=["unsafe qwenpaw output replaced by deterministic fallback"],
    )


class AgentRuntime:
    def __init__(self, mode: str | None = None, draft_generator=None):
        self.draft_generator = draft_generator or choose_draft_generator()
        selected_mode = mode or getattr(self.draft_generator, "mode", "deterministic")
        self.mode = (
            selected_mode
            if selected_mode in {"deterministic", "qwen_draft", "qwenpaw_workflow"}
            else "deterministic"
        )

    def _draft_fallback_state(self, results: list[DraftGenerationResult]) -> tuple[bool, str | None, str]:
        fallback_reasons = sorted({result.fallback_reason for result in results if result.fallback_reason})
        fallback_used = any(result.fallback_used for result in results)
        status = "fallback_completed" if fallback_used and self.mode == "qwen_draft" else "completed"
        return fallback_used, ",".join(fallback_reasons) if fallback_reasons else None, status

    def _qwenpaw_tool_registry(
        self,
        incident: Incident,
        runtime_state: MerchantRuntimeState | None,
    ) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register(
            ToolDefinition(
                name="incident.get_active_incident_snapshot",
                permission=ToolPermission.READ_ONLY,
                input_schema_name="IncidentSnapshotInput",
                output_schema_name="IncidentSnapshot",
                handler=lambda payload: incident.model_dump(),
            )
        )
        registry.register(
            ToolDefinition(
                name="merchant.get_runtime_snapshot",
                permission=ToolPermission.READ_ONLY,
                input_schema_name="MerchantRuntimeSnapshotInput",
                output_schema_name="MerchantRuntimeSnapshot",
                handler=lambda payload: runtime_state.model_dump() if runtime_state else {},
            )
        )
        registry.register(
            ToolDefinition(
                name="operation.apply_suggestion",
                permission=ToolPermission.APPROVAL_REQUIRED,
                input_schema_name="OperationSuggestionApplyInput",
                output_schema_name="OperationSuggestionApplyResult",
                handler=lambda payload: {"applied": True},
            )
        )
        return registry

    def _qwenpaw_agent_for_tool_request(self, request_payload: dict[str, Any]) -> str:
        requested_by_agent = request_payload.get("requested_by_agent")
        if isinstance(requested_by_agent, str) and requested_by_agent:
            return requested_by_agent
        tool_name = str(request_payload.get("tool_name", ""))
        if tool_name == "merchant.get_runtime_snapshot":
            return "MerchantEdgeWorker"
        if tool_name == "operation.apply_suggestion":
            return "FieldOpsWorker"
        return "FieldOpsWorker"

    def _qwenpaw_step_for_agent(self, agent_name: str) -> str:
        return QWENPAW_STEP_IDS.get(agent_name, f"qwenpaw_{agent_name.lower()}")

    def run_qwenpaw_shadow_orchestration(
        self,
        event_id: str,
        incident: Incident,
    ) -> AgentRuntimeResult:
        started_at = utc_now()
        run_id = f"run_{event_id}_qwenpaw_shadow_{incident.incident_id}"
        merchant_id = incident.affected_merchants[0] if incident.affected_merchants else None
        runtime_state = STORE.get_runtime_state(merchant_id) if merchant_id else None
        input_refs = [f"incident:{incident.incident_id}"]
        if merchant_id:
            input_refs.append(f"merchant_runtime:{merchant_id}")
        snapshots = {
            "incident": incident.model_dump(),
            "merchant_runtime": runtime_state.model_dump() if runtime_state else None,
        }
        context = QwenPawWorkflowContext(
            event_id=event_id,
            incident_id=incident.incident_id,
            input_refs=input_refs,
            snapshots=snapshots,
        )

        adapter_result = FakeQwenPawWorkflowAdapter().run_shadow_incident_workflow(context)
        unsafe_paths = _find_unsafe_qwenpaw_paths(
            {
                "leader_decision": adapter_result.leader_decision,
                "worker_outputs": adapter_result.worker_outputs,
                "advisory_bundle": adapter_result.advisory_bundle,
                "permission_requests": adapter_result.permission_requests,
            }
        )
        fallback_used = bool(unsafe_paths)
        if fallback_used:
            adapter_result = _fallback_qwenpaw_result(context)

        registry = self._qwenpaw_tool_registry(incident=incident, runtime_state=runtime_state)
        tool_calls: list[AgentToolCall] = []
        for permission_request in adapter_result.permission_requests:
            tool_name = str(permission_request["tool_name"])
            requested_by_agent = self._qwenpaw_agent_for_tool_request(permission_request)
            step_id = self._qwenpaw_step_for_agent(requested_by_agent)
            execution = registry.request(
                run_id=run_id,
                step_id=step_id,
                request=ToolRequest(
                    tool_name=tool_name,
                    requested_by_agent=requested_by_agent,
                    input_payload=dict(permission_request.get("input_payload") or {}),
                ),
            )
            tool_calls.append(execution.tool_call)

        calls_by_agent: dict[str, list[AgentToolCall]] = defaultdict(list)
        for call in tool_calls:
            requested_by_agent = call.input_payload.get("requested_by_agent", "FieldOpsWorker")
            calls_by_agent[str(requested_by_agent)].append(call)

        worker_outputs = {
            str(output.get("agent_name")): output
            for output in adapter_result.worker_outputs
            if output.get("agent_name")
        }
        permission_decisions = [
            call.output_payload.get("permission_decision", {})
            for call in tool_calls
        ]
        advisory_bundle = {
            **adapter_result.advisory_bundle,
            "permission_decisions": permission_decisions,
        }
        notice_content = str(
            advisory_bundle.get("visitor_safe_notice_draft")
            or "Some offers may be limited. Please follow the latest event page guidance."
        )
        forbidden_public_terms = find_forbidden_public_terms(notice_content)

        def calls_payload(agent_name: str) -> tuple[list[dict[str, Any]], list[str]]:
            calls = calls_by_agent.get(agent_name, [])
            return [call.model_dump() for call in calls], [call.tool_call_id for call in calls]

        def leader_node(state: WorkflowState) -> WorkflowNodeResult:
            tool_payloads, tool_refs = calls_payload("CentralOpsLeader")
            return WorkflowNodeResult(
                step_id=QWENPAW_STEP_IDS["CentralOpsLeader"],
                agent_name="CentralOpsLeader",
                objective="Decompose one merchant incident into advisory-only specialist work.",
                input_refs=input_refs,
                tool_calls=tool_payloads,
                tool_call_refs=tool_refs,
                structured_output={
                    "leader_decision": adapter_result.leader_decision,
                    "assigned_workers": adapter_result.leader_decision.get("assigned_workers", []),
                },
                decision_reason="A merchant incident affects capacity, visitor copy, and review evidence.",
                confidence=0.9,
                requires_human_approval=False,
                schema_name="QwenPawLeaderDecision",
            )

        def worker_node(agent_name: str, objective: str, reason: str, confidence: float) -> WorkflowNode:
            def run(state: WorkflowState) -> WorkflowNodeResult:
                output = worker_outputs.get(agent_name, {})
                structured_payload = dict(output.get("structured_payload") or {})
                tool_payloads, tool_refs = calls_payload(agent_name)
                return WorkflowNodeResult(
                    step_id=QWENPAW_STEP_IDS[agent_name],
                    agent_name=agent_name,
                    objective=objective,
                    input_refs=input_refs,
                    tool_calls=tool_payloads,
                    tool_call_refs=tool_refs,
                    structured_output={
                        **structured_payload,
                        "content": output.get("content"),
                    },
                    decision_reason=reason,
                    confidence=confidence,
                    requires_human_approval=True,
                    schema_name="QwenPawWorkerOutput",
                    validation_status="fallback" if fallback_used else "passed",
                )

            return WorkflowNode(node_id=QWENPAW_STEP_IDS[agent_name], run=run)

        def safety_node(state: WorkflowState) -> WorkflowNodeResult:
            tool_payloads, tool_refs = calls_payload("SafetyGateWorker")
            return WorkflowNodeResult(
                step_id=QWENPAW_STEP_IDS["SafetyGateWorker"],
                agent_name="SafetyGateWorker",
                objective="Validate the advisory bundle and enforce non-mutation boundaries.",
                input_refs=input_refs,
                tool_calls=tool_payloads,
                tool_call_refs=tool_refs,
                structured_output={
                    "advisory_bundle": advisory_bundle,
                    "permission_decisions": permission_decisions,
                    "safety_notes": adapter_result.safety_notes,
                    "unsafe_mutation_attempted": fallback_used,
                    "unsafe_paths": unsafe_paths,
                },
                decision_reason=(
                    "Unsafe adapter output was replaced with deterministic fallback."
                    if fallback_used
                    else "All requested mutation-capable tools were denied and output stayed advisory."
                ),
                confidence=0.92,
                requires_human_approval=True,
                schema_name="QwenPawSafetyEvaluation",
                validation_status="fallback" if fallback_used else "passed",
            )

        workflow_state = WorkflowState(
            run_id=run_id,
            event_id=event_id,
            trigger="incident_recovery",
            input_refs=input_refs,
            snapshots=snapshots,
            tool_calls=tool_calls,
        )
        workflow = WorkflowSpec(
            workflow_id="qwenpaw_shadow_incident_v1",
            trigger="incident_recovery",
            nodes=[
                WorkflowNode(node_id=QWENPAW_STEP_IDS["CentralOpsLeader"], run=leader_node),
                worker_node(
                    "MerchantEdgeWorker",
                    "Assess merchant-facing impact without changing merchant runtime state.",
                    "Merchant package guidance can be prepared, but live state remains untouched.",
                    0.86,
                ),
                worker_node(
                    "FieldOpsWorker",
                    "Assess field recovery options and request only permissioned tools.",
                    "Backup capacity advice requires organizer approval before action.",
                    0.87,
                ),
                worker_node(
                    "PublicNoticeWorker",
                    "Draft visitor-safe notice copy for organizer review.",
                    "Visitors need clear guidance without internal operational terms.",
                    0.85,
                ),
                worker_node(
                    "ReviewEvidenceWorker",
                    "Identify evidence references for post-incident review.",
                    "Review output should cite incident and touchpoint evidence.",
                    0.84,
                ),
                WorkflowNode(node_id=QWENPAW_STEP_IDS["SafetyGateWorker"], run=safety_node),
            ],
            edges=[
                (QWENPAW_STEP_IDS["CentralOpsLeader"], QWENPAW_STEP_IDS["MerchantEdgeWorker"]),
                (QWENPAW_STEP_IDS["CentralOpsLeader"], QWENPAW_STEP_IDS["FieldOpsWorker"]),
                (QWENPAW_STEP_IDS["CentralOpsLeader"], QWENPAW_STEP_IDS["PublicNoticeWorker"]),
                (QWENPAW_STEP_IDS["CentralOpsLeader"], QWENPAW_STEP_IDS["ReviewEvidenceWorker"]),
                (QWENPAW_STEP_IDS["ReviewEvidenceWorker"], QWENPAW_STEP_IDS["SafetyGateWorker"]),
            ],
        )
        execution = WorkflowExecutor().execute(workflow, workflow_state)

        draft = AgentDraft(
            draft_id=f"draft_{run_id}_public_notice",
            event_id=event_id,
            source_run_id=run_id,
            draft_type="public_notice",
            locale="en",
            content=notice_content,
            structured_payload={
                "advisory_bundle": advisory_bundle,
                "source": "qwenpaw_shadow",
                "authoritative_mutation": False,
            },
            status="draft",
            created_at=utc_now(),
        )
        evaluation = AgentEvaluation(
            evaluation_id=f"eval_{run_id}_qwenpaw_shadow",
            run_id=run_id,
            schema_pass=not fallback_used,
            fallback_used=fallback_used,
            unsafe_mutation_attempted=fallback_used,
            human_approval_required=True,
            forbidden_public_terms_present=bool(forbidden_public_terms),
            public_copy_ready=bool(notice_content.strip()) and not forbidden_public_terms,
            notes=[
                f"unsafe_paths={','.join(unsafe_paths)}" if unsafe_paths else "unsafe_paths=none",
                f"permission_decisions={len(permission_decisions)}",
                "advisory_only=true",
            ],
        )
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="incident_recovery",
            mode="qwenpaw_workflow",
            status="fallback_completed" if fallback_used else "completed",
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=fallback_used,
            fallback_reason="unsafe_qwenpaw_output" if fallback_used else None,
            final_output_ref=f"qwenpaw_shadow_advisory:{event_id}:{incident.incident_id}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=execution.steps,
            tool_calls=tool_calls,
            drafts=[draft],
            model_calls=[],
            evaluations=[evaluation],
        )

    def run_planning(
        self,
        event_id: str,
        brief: EventBrief,
        merchants: list[MerchantProfile],
        plan: PlanVersion,
    ) -> AgentRuntimeResult:
        started_at = utc_now()
        run_id = f"run_{event_id}_planning_v{plan.version}"
        recorder = ToolRecorder(run_id=run_id)

        selected = recorder.call(
            step_id="step_merchant",
            tool_name="merchant.select_night_merchants",
            input_payload={"merchant_count": len(merchants), "limit": 6},
            fn=lambda: [merchant.merchant_id for merchant in select_night_merchants(merchants, limit=6)],
        )
        route = recorder.call(
            step_id="step_route",
            tool_name="route.build_static_route",
            input_payload={"rainy": False},
            fn=lambda: build_static_route(rainy=False),
        )
        budget = recorder.call(
            step_id="step_budget",
            tool_name="budget.split_budget",
            input_payload={"total_mop": brief.budget_mop},
            fn=lambda: split_budget(brief.budget_mop).model_dump(),
        )

        steps = [
            AgentStep(
                step_id="step_coordinator",
                run_id=run_id,
                agent_name="CoordinatorAgent",
                objective="Decompose the event into narrative, route, merchant, risk, budget, and publication tasks.",
                input_refs=[f"event_brief:{event_id}"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={"tasks": ["narrative", "route", "merchant", "risk", "budget", "publication"]},
                decision_reason="The event needs coordinated route, merchant, risk, and visitor-facing outputs.",
                confidence=0.9,
                requires_human_approval=False,
                schema_name="AgentRun",
                validation_status="passed",
            ),
            AgentStep(
                step_id="step_cultural",
                run_id=run_id,
                agent_name="CulturalNarrativeAgent",
                objective="Create a route narrative from curated old-district references.",
                input_refs=["knowledge:fulong-new-street", "knowledge:inner-harbour"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={
                    "theme": "old-district night walk",
                    "route_points": [point.point_id for point in plan.route_points[:3]],
                },
                decision_reason="The event should connect local stories with route stops.",
                confidence=0.86,
                requires_human_approval=False,
                schema_name="AgentStep",
                validation_status="passed",
            ),
            AgentStep(
                step_id="step_route",
                run_id=run_id,
                agent_name="RoutePlanningAgent",
                objective="Build a deterministic route candidate.",
                input_refs=["route_points", "weather:mock"],
                tool_calls=[call.model_dump() for call in recorder.calls if call.step_id == "step_route"],
                tool_call_refs=[call.tool_call_id for call in recorder.calls if call.step_id == "step_route"],
                structured_output={"route": route, "route_points": [point.point_id for point in plan.route_points]},
                decision_reason="The route fits the seeded event window and keeps backup points available.",
                confidence=0.88,
                requires_human_approval=False,
                schema_name="PlanVersion",
                validation_status="passed",
            ),
            AgentStep(
                step_id="step_merchant",
                run_id=run_id,
                agent_name="MerchantMatchingAgent",
                objective="Select merchants that fit night-tour participation.",
                input_refs=["merchants", "event_brief"],
                tool_calls=[call.model_dump() for call in recorder.calls if call.step_id == "step_merchant"],
                tool_call_refs=[call.tool_call_id for call in recorder.calls if call.step_id == "step_merchant"],
                structured_output={"selected_merchants": selected},
                decision_reason="Selected merchants have high night score and route compatibility.",
                confidence=0.84,
                requires_human_approval=False,
                schema_name="MerchantTask",
                validation_status="passed",
            ),
            AgentStep(
                step_id="step_budget",
                run_id=run_id,
                agent_name="CoordinatorAgent",
                objective="Split event budget into operational buckets.",
                input_refs=[f"event_brief:{event_id}:budget_mop"],
                tool_calls=[call.model_dump() for call in recorder.calls if call.step_id == "step_budget"],
                tool_call_refs=[call.tool_call_id for call in recorder.calls if call.step_id == "step_budget"],
                structured_output=budget,
                decision_reason="Budget split keeps contingency available for recovery.",
                confidence=0.82,
                requires_human_approval=False,
                schema_name="BudgetPlan",
                validation_status="passed",
            ),
            AgentStep(
                step_id="step_risk",
                run_id=run_id,
                agent_name="RiskRecoveryAgent",
                objective="Identify operational risks that require organizer awareness.",
                input_refs=["runtime_states", "route_points", "merchant_assignments"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={"risks": plan.risk_plan},
                decision_reason="Inventory, queue, and weather risks should be visible before publication.",
                confidence=0.82,
                requires_human_approval=True,
                schema_name="PlanVersion",
                validation_status="passed",
            ),
        ]
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="planning_generation",
            mode="deterministic",
            status="completed",
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=False,
            fallback_reason=None,
            final_output_ref=f"plan:{event_id}:v{plan.version}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=steps,
            tool_calls=recorder.calls,
            drafts=[],
            model_calls=[],
            evaluations=[],
        )

    def run_merchant_edge_package_generation(
        self,
        event_id: str,
        plan: PlanVersion,
        merchants: list[MerchantProfile],
        tasks: list[MerchantTask],
        packages: list[MerchantInteractionPackage],
    ) -> AgentRuntimeResult:
        started_at = utc_now()
        run_id = f"run_{event_id}_merchant_edge_v{plan.version}"
        assigned_ids = list(plan.merchant_assignments)
        assigned_set = set(assigned_ids)
        task_ids = [
            task.task_id
            for task in tasks
            if task.event_id == event_id
            and task.plan_version == plan.version
            and task.merchant_id in assigned_set
        ]
        package_ids = [package.id for package in packages]
        touchpoint_count = sum(len(package.touchpoints) for package in packages)
        coupon_rule_count = sum(len(package.coupon_rules) for package in packages)

        steps = [
            AgentStep(
                step_id="inspect_approved_plan",
                run_id=run_id,
                agent_name="MerchantEdgeCoordinatorAgent",
                objective="Inspect the current approved plan before creating merchant-facing edge assets.",
                input_refs=[f"plan:{event_id}:v{plan.version}"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={
                    "plan_version": plan.version,
                    "status": plan.status,
                    "merchant_assignments": assigned_ids,
                },
                decision_reason="Merchant packages must be anchored to the approved plan version.",
                confidence=0.9,
                requires_human_approval=False,
                schema_name="PlanVersion",
                validation_status="passed",
            ),
            AgentStep(
                step_id="match_tasks_to_merchants",
                run_id=run_id,
                agent_name="MerchantTaskMatchingAgent",
                objective="Match generated merchant tasks to assigned merchant profiles.",
                input_refs=["merchant_tasks", "merchants"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={
                    "matched_task_ids": task_ids,
                    "merchant_count": len(merchants),
                },
                decision_reason="Each package should link back to the operational task records for that merchant.",
                confidence=0.88,
                requires_human_approval=False,
                schema_name="MerchantTask",
                validation_status="passed",
            ),
            AgentStep(
                step_id="design_touchpoints",
                run_id=run_id,
                agent_name="InShopTouchpointAgent",
                objective="Design deterministic in-shop QR and coupon touchpoints for every package.",
                input_refs=["merchant_tasks", f"plan:{event_id}:v{plan.version}"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={"touchpoint_count": touchpoint_count},
                decision_reason="Every participating merchant needs at least two in-shop visitor touchpoints.",
                confidence=0.86,
                requires_human_approval=False,
                schema_name="InShopTouchpoint",
                validation_status="passed",
            ),
            AgentStep(
                step_id="design_coupon_rules",
                run_id=run_id,
                agent_name="CouponRuleAgent",
                objective="Create bounded deterministic coupon rules for merchant packages.",
                input_refs=["merchant_tasks", "touchpoint_designs"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={"coupon_rule_count": coupon_rule_count},
                decision_reason="Coupon limits keep demo redemption behavior measurable and merchant-scoped.",
                confidence=0.84,
                requires_human_approval=False,
                schema_name="CouponRule",
                validation_status="passed",
            ),
            AgentStep(
                step_id="assemble_merchant_packages",
                run_id=run_id,
                agent_name="MerchantInteractionPackageAgent",
                objective="Assemble merchant packages with briefs, visitor copy, task links, and evidence refs.",
                input_refs=["touchpoint_designs", "coupon_rules", "merchant_tasks"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={"package_ids": package_ids},
                decision_reason="The workbench needs a single package object scoped to the logged-in merchant.",
                confidence=0.87,
                requires_human_approval=False,
                schema_name="MerchantInteractionPackage",
                validation_status="passed",
            ),
            AgentStep(
                step_id="validate_public_copy",
                run_id=run_id,
                agent_name="PublicCopyValidationAgent",
                objective="Check that visitor-facing package copy avoids internal backend terms.",
                input_refs=package_ids,
                tool_calls=[],
                tool_call_refs=[],
                structured_output={"public_copy_ready": True, "package_count": len(packages)},
                decision_reason="Merchant package copy is deterministic and contains only visitor-safe wording.",
                confidence=0.85,
                requires_human_approval=False,
                schema_name="MerchantInteractionPackage",
                validation_status="passed",
            ),
        ]
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="merchant_edge_package_generation",
            mode="deterministic",
            status="completed",
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=False,
            fallback_reason=None,
            final_output_ref=f"merchant_interaction_packages:{event_id}:v{plan.version}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=steps,
            tool_calls=[],
            drafts=[],
            model_calls=[],
            evaluations=[],
        )

    def run_incident_recovery_preview(
        self,
        event_id: str,
        incident: Incident,
        state: MerchantRuntimeState | None,
    ) -> AgentRuntimeResult:
        started_at = utc_now()
        run_id = f"run_{event_id}_incident_{incident.incident_id}"
        recorder = ToolRecorder(run_id=run_id)
        proposal_payload = recorder.call(
            step_id="step_recovery",
            tool_name="recovery.build_recovery_proposal",
            input_payload={"incident_id": incident.incident_id, "type": incident.type},
            fn=lambda: build_recovery_proposal(incident).model_dump(),
        )
        recovery_result = self.draft_generator.generate_recovery_explanation(
            DraftGenerationContext(
                run_id=run_id,
                event_id=event_id,
                draft_type="recovery_explanation",
                input_refs=[f"incident:{incident.incident_id}", "recovery_proposal_payload"],
                incident=incident,
                proposal_payload=proposal_payload,
            )
        )
        notice_result = self.draft_generator.generate_public_notice(
            DraftGenerationContext(
                run_id=run_id,
                event_id=event_id,
                draft_type="public_notice",
                input_refs=[f"incident:{incident.incident_id}", f"draft:{recovery_result.draft.draft_id}"],
                incident=incident,
                proposal_payload=proposal_payload,
            )
        )
        recovery_draft = recovery_result.draft
        notice_draft = notice_result.draft
        draft_results = [recovery_result, notice_result]
        fallback_used, fallback_reason, run_status = self._draft_fallback_state(draft_results)
        evaluations = [result.evaluation for result in draft_results if result.evaluation is not None]
        model_calls = [result.model_call for result in draft_results if result.model_call is not None]
        public_ready = not evaluations or all(evaluation.public_copy_ready for evaluation in evaluations)
        runtime_ref = f"runtime_state:{state.merchant_id}" if state else "runtime_state:none"
        steps = [
            AgentStep(
                step_id="step_recovery",
                run_id=run_id,
                agent_name="RiskRecoveryAgent",
                objective="Build a recovery candidate from the incident without committing state.",
                input_refs=[f"incident:{incident.incident_id}", runtime_ref],
                tool_calls=[call.model_dump() for call in recorder.calls],
                tool_call_refs=[call.tool_call_id for call in recorder.calls],
                structured_output=proposal_payload,
                decision_reason="The merchant signal affects route guidance and needs organizer approval.",
                confidence=0.86,
                requires_human_approval=True,
                model_call_ref=recovery_result.model_call.model_call_id if recovery_result.model_call else None,
                schema_name="RecoveryProposal",
                validation_status="fallback" if recovery_result.fallback_used else "passed",
            ),
            AgentStep(
                step_id="step_public_notice",
                run_id=run_id,
                agent_name="PublicNoticeAgent",
                objective="Draft visitor-safe notice copy.",
                input_refs=[f"incident:{incident.incident_id}", f"draft:{recovery_draft.draft_id}"],
                tool_calls=[],
                tool_call_refs=[],
                structured_output={
                    "draft_id": notice_draft.draft_id,
                    "public_copy_ready": public_ready,
                },
                decision_reason="Visitors need action guidance without internal operational terms.",
                confidence=0.84,
                requires_human_approval=True,
                model_call_ref=notice_result.model_call.model_call_id if notice_result.model_call else None,
                schema_name="AgentDraft",
                validation_status="fallback" if notice_result.fallback_used else ("passed" if public_ready else "failed"),
            ),
        ]
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="incident_recovery",
            mode=self.mode,
            status=run_status,
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            final_output_ref=f"draft:{notice_draft.draft_id}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=steps,
            tool_calls=recorder.calls,
            drafts=[recovery_draft, notice_draft],
            model_calls=model_calls,
            evaluations=evaluations,
        )

    def run_review_generation(
        self,
        event_id: str,
        metrics: list[OperationalMetric],
        incidents: list[Incident],
        notices: list[PublicNotice],
        proposals: list[RecoveryProposal],
    ) -> AgentRuntimeResult:
        started_at = utc_now()
        run_id = f"run_{event_id}_review"
        review_result = self.draft_generator.generate_review_summary(
            DraftGenerationContext(
                run_id=run_id,
                event_id=event_id,
                draft_type="review_summary",
                input_refs=["metrics", "incidents", "public_notices", "recovery_proposals"],
                metrics=metrics,
                incidents=incidents,
                notices=notices,
                proposals=proposals,
            )
        )
        draft = review_result.draft
        fallback_used, fallback_reason, run_status = self._draft_fallback_state([review_result])
        step = AgentStep(
            step_id="step_review",
            run_id=run_id,
            agent_name="ReviewAgent",
            objective="Draft evidence-backed review summary from operational records.",
            input_refs=["metrics", "incidents", "public_notices", "recovery_proposals"],
            tool_calls=[],
            tool_call_refs=[],
            structured_output=draft.structured_payload,
            decision_reason="Review should separate evidence from recommendations.",
            confidence=0.86,
            requires_human_approval=False,
            model_call_ref=review_result.model_call.model_call_id if review_result.model_call else None,
            schema_name="AgentDraft",
            validation_status="fallback" if fallback_used else "passed",
        )
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="review_generation",
            mode=self.mode,
            status=run_status,
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            final_output_ref=f"draft:{draft.draft_id}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=[step],
            tool_calls=[],
            drafts=[draft],
            model_calls=[review_result.model_call] if review_result.model_call else [],
            evaluations=[review_result.evaluation] if review_result.evaluation else [],
        )
