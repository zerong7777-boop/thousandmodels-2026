from datetime import UTC, datetime

from app.schemas import AgentDraft, Incident, OperationalMetric, PublicNotice, RecoveryProposal


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_recovery_explanation_draft(
    run_id: str,
    incident: Incident,
    proposal_payload: dict,
) -> AgentDraft:
    changes = proposal_payload.get("recommended_changes", [])
    affected = incident.affected_merchants[0] if incident.affected_merchants else "the affected merchant"
    return AgentDraft(
        draft_id=f"draft_{run_id}_recovery_explanation",
        event_id=incident.event_id,
        source_run_id=run_id,
        draft_type="recovery_explanation",
        locale="en",
        content=(
            f"The live merchant signal shows {affected} can no longer receive visitors as planned. "
            "Pause the affected stop, activate the backup merchant, and ask the organizer to confirm before publishing."
        ),
        structured_payload={
            "incident_id": incident.incident_id,
            "affected_merchants": incident.affected_merchants,
            "recommended_changes": changes,
            "requires_organizer_approval": True,
        },
        status="draft",
        reviewed_by=None,
        reviewed_at=None,
        created_at=now_iso(),
    )


def build_public_notice_draft(
    run_id: str,
    incident: Incident,
    proposal_payload: dict,
) -> AgentDraft:
    content = proposal_payload.get("public_notice_patch") or (
        "Tonight's route has been adjusted. Please follow the latest route to the next stop."
    )
    return AgentDraft(
        draft_id=f"draft_{run_id}_public_notice",
        event_id=incident.event_id,
        source_run_id=run_id,
        draft_type="public_notice",
        locale="zh-Hans",
        content=content,
        structured_payload={
            "affected_merchants": incident.affected_merchants,
            "affected_route_points": incident.affected_route_points,
            "requires_organizer_approval": True,
        },
        status="draft",
        reviewed_by=None,
        reviewed_at=None,
        created_at=now_iso(),
    )


def build_review_summary_draft(
    run_id: str,
    event_id: str,
    metrics: list[OperationalMetric],
    incidents: list[Incident],
    notices: list[PublicNotice],
    proposals: list[RecoveryProposal],
) -> AgentDraft:
    metric_names = [metric.name for metric in metrics]
    return AgentDraft(
        draft_id=f"draft_{run_id}_review_summary",
        event_id=event_id,
        source_run_id=run_id,
        draft_type="review_summary",
        locale="mixed",
        content=(
            f"Evidence: metrics={','.join(metric_names)}; "
            f"incidents={len(incidents)}; notices={len(notices)}. "
            "Recommendation: keep backup merchant thresholds visible before the next event."
        ),
        structured_payload={
            "metrics": metric_names,
            "incident_ids": [incident.incident_id for incident in incidents],
            "notice_ids": [notice.notice_id for notice in notices],
            "proposal_ids": [proposal.proposal_id for proposal in proposals],
            "evidence_backed": True,
        },
        status="draft",
        reviewed_by=None,
        reviewed_at=None,
        created_at=now_iso(),
    )
