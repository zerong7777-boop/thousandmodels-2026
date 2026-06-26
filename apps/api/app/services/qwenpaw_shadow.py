from __future__ import annotations

from pydantic import BaseModel

from app.agents.runtime import AgentRuntime, AgentRuntimeResult
from app.schemas import AgentRun, AgentStep, Incident
from app.store import STORE


ACTIVE_INCIDENT_STATUSES = {"open", "proposal_ready"}


class QwenPawShadowRunRequest(BaseModel):
    incident_id: str | None = None


class QwenPawShadowRunResponse(BaseModel):
    agent_run: AgentRun
    advisory_bundle: dict
    steps: list[AgentStep]
    permission_decisions: list[dict]


def _latest_active_incident(event_id: str) -> Incident | None:
    incidents = [
        incident
        for incident in STORE.list_incidents(event_id)
        if incident.status in ACTIVE_INCIDENT_STATUSES
    ]
    if not incidents:
        return None
    return max(incidents, key=lambda incident: (incident.created_at, incident.incident_id))


def run_qwenpaw_shadow(
    event_id: str,
    incident_id: str | None,
) -> tuple[AgentRuntimeResult, dict]:
    if incident_id:
        incident = STORE.get_incident(incident_id, event_id=event_id)
        if not incident or incident.status not in ACTIVE_INCIDENT_STATUSES:
            raise LookupError("active incident not found")
    else:
        incident = _latest_active_incident(event_id)
        if not incident:
            raise LookupError("active incident not found")

    runtime_result = AgentRuntime(mode="qwenpaw_workflow").run_qwenpaw_shadow_orchestration(
        event_id=event_id,
        incident=incident,
    )
    advisory_bundle = next(
        (
            draft.structured_payload["advisory_bundle"]
            for draft in runtime_result.drafts
            if isinstance(draft.structured_payload.get("advisory_bundle"), dict)
        ),
        {},
    )
    return runtime_result, advisory_bundle
