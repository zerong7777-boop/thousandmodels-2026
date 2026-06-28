from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.schemas import (
    EventMerchantParticipant,
    EventMerchantParticipantUpdateRequest,
    EventMerchantSetupSummary,
)
from app.services.merchant_network import evaluate_merchant_for_event

if TYPE_CHECKING:
    from app.schemas import MerchantProfile
    from app.store import MVPStore


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def unique_merchant_ids(merchant_ids: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for merchant_id in merchant_ids:
        normalized = merchant_id.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def summarize_event_merchants(store: MVPStore, event_id: str) -> EventMerchantSetupSummary:
    participants = store.list_event_merchant_participants(event_id)
    participants.sort(key=lambda item: item.merchant_id)
    event = store.get_event_summary(event_id)
    eligibility = {}
    if event:
        for participant in participants:
            merchant = store.get_merchant(participant.merchant_id)
            if merchant:
                eligibility[participant.merchant_id] = evaluate_merchant_for_event(event, merchant)
    ready_count = sum(
        1
        for item in participants
        if item.participation_status == "confirmed" and item.readiness_status == "ready"
    )
    needs_setup_count = sum(1 for item in participants if item.readiness_status == "needs_setup")
    missing_count = sum(1 for item in participants if item.readiness_status == "missing")
    declined_count = sum(1 for item in participants if item.participation_status == "declined")
    ready_for_planning = (
        bool(participants)
        and ready_count == len(participants)
        and declined_count == 0
        and missing_count == 0
        and needs_setup_count == 0
        and not any(item.status == "ineligible" for item in eligibility.values())
    )
    return EventMerchantSetupSummary(
        event_id=event_id,
        participants=participants,
        total_count=len(participants),
        ready_count=ready_count,
        needs_setup_count=needs_setup_count,
        missing_count=missing_count,
        declined_count=declined_count,
        ready_for_planning=ready_for_planning,
        eligibility=eligibility,
    )


def replace_event_merchant_roster(
    store: MVPStore, event_id: str, merchant_ids: list[str]
) -> EventMerchantSetupSummary:
    selected_ids = unique_merchant_ids(merchant_ids)
    timestamp = now_iso()
    for merchant_id in selected_ids:
        if not store.get_merchant(merchant_id):
            raise LookupError("merchant not found")
    store.delete_event_merchant_participants_except(event_id, set(selected_ids))
    for merchant_id in selected_ids:
        existing = store.get_event_merchant_participant(event_id, merchant_id)
        participant = existing or EventMerchantParticipant(
            event_id=event_id,
            merchant_id=merchant_id,
            participation_status="confirmed",
            readiness_status="needs_setup",
            role_hint=None,
            notes="",
            created_at=timestamp,
            updated_at=timestamp,
        )
        participant.updated_at = timestamp
        store.save_event_merchant_participant(participant)
    return summarize_event_merchants(store, event_id)


def update_event_merchant_participant(
    store: MVPStore,
    event_id: str,
    merchant_id: str,
    payload: EventMerchantParticipantUpdateRequest,
) -> EventMerchantSetupSummary:
    participant = store.get_event_merchant_participant(event_id, merchant_id)
    if not participant:
        raise LookupError("event merchant not found")
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("readiness_status") == "ready":
        event = store.get_event_summary(event_id)
        merchant = store.get_merchant(merchant_id)
        if event and merchant:
            eligibility = evaluate_merchant_for_event(event, merchant)
            if eligibility.status == "ineligible":
                raise ValueError("merchant is not eligible for this event")
    for key, value in updates.items():
        setattr(participant, key, value)
    participant.updated_at = now_iso()
    store.save_event_merchant_participant(participant)
    return summarize_event_merchants(store, event_id)


def ready_event_merchants(store: MVPStore, event_id: str) -> list[MerchantProfile]:
    participants = summarize_event_merchants(store, event_id).participants
    ready_ids = [
        participant.merchant_id
        for participant in participants
        if participant.participation_status == "confirmed"
        and participant.readiness_status == "ready"
    ]
    merchants = [store.get_merchant(merchant_id) for merchant_id in ready_ids]
    return [merchant for merchant in merchants if merchant is not None]


def merchant_scope_for_planning(store: MVPStore, event_id: str) -> list[MerchantProfile]:
    if event_id == "demo-night-tour" and not store.list_event_merchant_participants(event_id):
        return store.list_merchants()
    summary = summarize_event_merchants(store, event_id)
    if not summary.ready_for_planning:
        raise RuntimeError("event merchant setup required")
    return ready_event_merchants(store, event_id)


def merchant_scope_for_plan_ids(
    store: MVPStore, event_id: str, merchant_ids: list[str]
) -> list[MerchantProfile]:
    merchants = [store.get_merchant(merchant_id) for merchant_id in merchant_ids]
    scoped = [merchant for merchant in merchants if merchant is not None]
    if scoped:
        return scoped
    return merchant_scope_for_planning(store, event_id)
