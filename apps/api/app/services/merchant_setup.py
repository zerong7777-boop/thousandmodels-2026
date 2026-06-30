from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.schemas import (
    EventBrief,
    EventMerchantParticipant,
    MerchantAssignedEvent,
    MerchantEligibility,
    MerchantSetupSubmitRequest,
)
from app.services.merchant_network import evaluate_merchant_for_event

if TYPE_CHECKING:
    from app.store import MVPStore


RAINY_SETUP_TOKENS = {
    "rain",
    "rainy",
    "rainy-day",
    "indoor",
    "covered",
    "backup",
    "family",
    "rest",
}


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def event_requires_indoor_backup(brief: EventBrief | None) -> bool:
    if brief is None:
        return False
    text = " ".join(
        [
            brief.event_goal,
            *brief.target_audience,
            *brief.theme_preferences,
            *brief.constraints,
            *brief.priority_rules,
        ]
    ).lower()
    return any(token in text for token in RAINY_SETUP_TOKENS)


def setup_gaps(participant: EventMerchantParticipant, brief: EventBrief | None) -> list[str]:
    gaps: list[str] = []
    if participant.setup_status == "not_started":
        gaps.append("merchant setup not submitted")
    if not participant.capacity_commitment:
        gaps.append("capacity commitment missing")
    if not participant.merchant_contact_name.strip():
        gaps.append("merchant contact name missing")
    if not participant.merchant_contact_phone.strip():
        gaps.append("merchant contact phone missing")
    if not participant.staffing_ready:
        gaps.append("staffing readiness not confirmed")
    if not participant.stock_ready:
        gaps.append("stock readiness not confirmed")
    if not participant.operating_window_confirmed:
        gaps.append("operating window not confirmed")
    if event_requires_indoor_backup(brief) and not participant.indoor_backup_ready:
        gaps.append("indoor backup readiness not confirmed")
    return gaps


def participant_ready_for_planning(
    participant: EventMerchantParticipant,
    brief: EventBrief | None,
    eligibility: MerchantEligibility | None,
) -> bool:
    return (
        participant.participation_status == "confirmed"
        and participant.readiness_status == "ready"
        and not setup_gaps(participant, brief)
        and (eligibility is None or eligibility.status != "ineligible")
    )


def build_assigned_event_context(
    store: MVPStore,
    event_id: str,
    merchant_id: str,
) -> MerchantAssignedEvent:
    event = store.get_event_summary(event_id)
    participant = store.get_event_merchant_participant(event_id, merchant_id)
    if event is None or participant is None:
        raise LookupError("event merchant assignment not found")
    merchant = store.get_merchant(merchant_id)
    eligibility = evaluate_merchant_for_event(event, merchant) if merchant else None
    brief = store.get_event_brief(event_id)
    gaps = setup_gaps(participant, brief)
    participant.setup_gaps = gaps
    return MerchantAssignedEvent(
        event=event,
        participant=participant,
        eligibility=eligibility,
        setup_gaps=gaps,
        ready_for_planning=participant_ready_for_planning(participant, brief, eligibility),
    )


def list_assigned_event_contexts(
    store: MVPStore,
    merchant_id: str,
) -> list[MerchantAssignedEvent]:
    contexts: list[MerchantAssignedEvent] = []
    for event in store.list_event_summaries():
        if store.get_event_merchant_participant(event.event_id, merchant_id):
            contexts.append(build_assigned_event_context(store, event.event_id, merchant_id))
    contexts.sort(key=lambda item: (item.event.date, item.event.event_id))
    return contexts


def get_assigned_event_context(
    store: MVPStore,
    merchant_id: str,
    event_id: str,
) -> MerchantAssignedEvent:
    return build_assigned_event_context(store, event_id, merchant_id)


def submit_merchant_setup(
    store: MVPStore,
    merchant_id: str,
    event_id: str,
    payload: MerchantSetupSubmitRequest,
) -> MerchantAssignedEvent:
    participant = store.get_event_merchant_participant(event_id, merchant_id)
    if participant is None:
        raise LookupError("event merchant assignment not found")
    updates = payload.model_dump()
    for key, value in updates.items():
        setattr(participant, key, value)
    participant.setup_status = "submitted"
    participant.submitted_at = now_iso()
    participant.submitted_by = merchant_id
    participant.updated_at = participant.submitted_at
    participant.setup_gaps = setup_gaps(participant, store.get_event_brief(event_id))
    store.save_event_merchant_participant(participant)
    return build_assigned_event_context(store, event_id, merchant_id)
