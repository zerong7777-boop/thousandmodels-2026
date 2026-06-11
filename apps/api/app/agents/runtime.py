from dataclasses import dataclass
from datetime import UTC, datetime

from app.agents.drafts import (
    build_public_notice_draft,
    build_recovery_explanation_draft,
    build_review_summary_draft,
)
from app.agents.guards import evaluate_public_copy
from app.agents.tool_recorder import ToolRecorder
from app.schemas import (
    AgentDraft,
    AgentEvaluation,
    AgentModelCall,
    AgentRun,
    AgentStep,
    AgentToolCall,
    EventBrief,
    Incident,
    MerchantProfile,
    MerchantRuntimeState,
    OperationalMetric,
    PlanVersion,
    PublicNotice,
    RecoveryProposal,
)
from app.services.recovery import build_recovery_proposal
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


class AgentRuntime:
    def __init__(self, mode: str = "deterministic"):
        self.mode = mode if mode in {"deterministic", "qwen_draft"} else "deterministic"

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
        recovery_draft = build_recovery_explanation_draft(run_id, incident, proposal_payload)
        notice_draft = build_public_notice_draft(run_id, incident, proposal_payload)
        evaluation = evaluate_public_copy(
            run_id=run_id,
            content=notice_draft.content,
            human_approval_required=True,
            fallback_used=False,
        )
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
                schema_name="RecoveryProposal",
                validation_status="passed",
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
                    "public_copy_ready": evaluation.public_copy_ready,
                },
                decision_reason="Visitors need action guidance without internal operational terms.",
                confidence=0.84,
                requires_human_approval=True,
                schema_name="AgentDraft",
                validation_status="passed" if evaluation.public_copy_ready else "failed",
            ),
        ]
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="incident_recovery",
            mode="deterministic",
            status="completed",
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=False,
            fallback_reason=None,
            final_output_ref=f"draft:{notice_draft.draft_id}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=steps,
            tool_calls=recorder.calls,
            drafts=[recovery_draft, notice_draft],
            model_calls=[],
            evaluations=[evaluation],
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
        draft = build_review_summary_draft(
            run_id=run_id,
            event_id=event_id,
            metrics=metrics,
            incidents=incidents,
            notices=notices,
            proposals=proposals,
        )
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
            schema_name="AgentDraft",
            validation_status="passed",
        )
        run = AgentRun(
            run_id=run_id,
            event_id=event_id,
            trigger="review_generation",
            mode="deterministic",
            status="completed",
            started_at=started_at,
            completed_at=utc_now(),
            fallback_used=False,
            fallback_reason=None,
            final_output_ref=f"draft:{draft.draft_id}",
            error_summary=None,
        )
        return AgentRuntimeResult(
            run=run,
            steps=[step],
            tool_calls=[],
            drafts=[draft],
            model_calls=[],
            evaluations=[],
        )
