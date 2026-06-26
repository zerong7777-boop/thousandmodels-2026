from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QwenPawWorkflowContext:
    event_id: str
    incident_id: str
    input_refs: list[str]
    snapshots: dict[str, Any]


@dataclass
class QwenPawWorkflowResult:
    leader_decision: dict[str, Any]
    worker_outputs: list[dict[str, Any]]
    advisory_bundle: dict[str, Any]
    permission_requests: list[dict[str, Any]] = field(default_factory=list)
    safety_notes: list[str] = field(default_factory=list)


class FakeQwenPawWorkflowAdapter:
    mode = "qwenpaw_workflow"

    def run_shadow_incident_workflow(self, context: QwenPawWorkflowContext) -> QwenPawWorkflowResult:
        incident_ref = f"incident:{context.incident_id}"
        return QwenPawWorkflowResult(
            leader_decision={
                "assigned_workers": [
                    "MerchantEdgeWorker",
                    "FieldOpsWorker",
                    "PublicNoticeWorker",
                    "ReviewEvidenceWorker",
                    "SafetyGateWorker",
                ],
                "input_refs": [incident_ref, *context.input_refs],
                "decision": "Run advisory-only shadow orchestration for the merchant incident.",
            },
            worker_outputs=[
                {
                    "agent_name": "MerchantEdgeWorker",
                    "content": "m001 package should pause visitor flow until organizer review.",
                    "structured_payload": {
                        "merchant_impact_note": (
                            "m001 reported sold-out inventory; keep the package visible but reduce live routing "
                            "pressure."
                        ),
                        "evidence_refs": [incident_ref, "merchant_runtime:m001"],
                    },
                },
                {
                    "agent_name": "FieldOpsWorker",
                    "content": "Shift attention to backup capacity and keep approval boundary active.",
                    "structured_payload": {
                        "recovery_rationale": (
                            "The sold-out merchant should not receive additional visitor flow before organizer "
                            "approval."
                        ),
                        "recommended_action": "prepare_backup_capacity",
                        "authoritative_mutation": False,
                    },
                },
                {
                    "agent_name": "PublicNoticeWorker",
                    "content": "Some offers may be limited. Please follow organizer guidance on the event page.",
                    "structured_payload": {
                        "visitor_safe_notice_draft": (
                            "Some offers may be limited. Please follow the latest event page guidance."
                        ),
                        "public_copy_ready": True,
                    },
                },
                {
                    "agent_name": "ReviewEvidenceWorker",
                    "content": "Review should cite incident and touchpoint metrics.",
                    "structured_payload": {
                        "review_evidence_refs": [incident_ref, f"touchpoint_metrics:{context.event_id}"],
                    },
                },
            ],
            advisory_bundle={
                "recovery_rationale": (
                    "m001 reported sold-out inventory and should be reviewed before receiving more visitor flow."
                ),
                "visitor_safe_notice_draft": (
                    "Some offers may be limited. Please follow the latest event page guidance."
                ),
                "merchant_impact_note": "m001 should prepare backup wording and wait for organizer approval.",
                "review_evidence_refs": [incident_ref, f"touchpoint_metrics:{context.event_id}"],
                "human_approval_required": True,
                "authoritative_mutation": False,
            },
            permission_requests=[
                {
                    "tool_name": "incident.get_active_incident_snapshot",
                    "requested_by_agent": "FieldOpsWorker",
                    "input_payload": {"incident_id": context.incident_id},
                },
                {
                    "tool_name": "merchant.get_runtime_snapshot",
                    "requested_by_agent": "MerchantEdgeWorker",
                    "input_payload": {"merchant_id": "m001"},
                },
                {
                    "tool_name": "operation.apply_suggestion",
                    "requested_by_agent": "FieldOpsWorker",
                    "input_payload": {"merchant_id": "m001"},
                },
            ],
            safety_notes=["fake deterministic adapter output for v1.4 spike"],
        )
