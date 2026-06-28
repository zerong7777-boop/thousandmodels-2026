from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.schemas import (
    MerchantCreateRequest,
    MerchantDetail,
    MerchantEligibility,
    MerchantOperatingWindow,
    MerchantParticipationHistoryItem,
    MerchantProfile,
    MerchantRuntimeState,
    MerchantUpdateRequest,
)

if TYPE_CHECKING:
    from app.schemas import EventSummary
    from app.store import MVPStore


TIME_WINDOW_RE = re.compile(r"(?P<start>\d{2}:\d{2})-(?P<end>\d{2}:\d{2})")


def parse_minutes(value: str) -> int | None:
    if not re.fullmatch(r"\d{2}:\d{2}", value):
        return None
    hour, minute = (int(part) for part in value.split(":"))
    if hour > 23 or minute > 59:
        return None
    return hour * 60 + minute


def parse_window(value: str) -> tuple[int, int] | None:
    match = TIME_WINDOW_RE.search(value.strip())
    if not match:
        return None
    start = parse_minutes(match.group("start"))
    end = parse_minutes(match.group("end"))
    if start is None or end is None or start >= end:
        return None
    return start, end


def windows_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def normalized_operating_windows(
    payload: MerchantCreateRequest | MerchantProfile,
) -> list[MerchantOperatingWindow]:
    if payload.operating_windows:
        return payload.operating_windows
    parsed = parse_window(payload.opening_hours)
    if not parsed:
        return []
    return [
        MerchantOperatingWindow(
            label="daily",
            start_time=f"{parsed[0] // 60:02d}:{parsed[0] % 60:02d}",
            end_time=f"{parsed[1] // 60:02d}:{parsed[1] % 60:02d}",
        )
    ]


def merchant_from_create(payload: MerchantCreateRequest) -> MerchantProfile:
    data = payload.model_dump()
    data["operating_windows"] = [
        window.model_dump() for window in normalized_operating_windows(payload)
    ]
    return MerchantProfile.model_validate(data)


def apply_merchant_update(
    merchant: MerchantProfile, payload: MerchantUpdateRequest
) -> MerchantProfile:
    updates = payload.model_dump(exclude_unset=True)
    data = merchant.model_dump()
    data.update(updates)
    next_merchant = MerchantProfile.model_validate(data)
    if "operating_windows" not in updates:
        next_merchant.operating_windows = normalized_operating_windows(next_merchant)
    return next_merchant


def default_runtime_state(merchant_id: str) -> MerchantRuntimeState:
    return MerchantRuntimeState(
        merchant_id=merchant_id,
        inventory_status="normal",
        queue_status="normal",
        available_for_visitors=True,
        temporary_note="",
        updated_at=datetime.now(UTC).isoformat(),
    )


def participation_history(
    store: MVPStore, merchant_id: str
) -> list[MerchantParticipationHistoryItem]:
    items: list[MerchantParticipationHistoryItem] = []
    for event in store.list_event_summaries():
        participant = store.get_event_merchant_participant(event.event_id, merchant_id)
        if not participant:
            continue
        versions = store.list_plan_versions(event.event_id)
        latest_plan_version = max((plan.version for plan in versions), default=0)
        packages = store.list_merchant_interaction_packages(event.event_id)
        items.append(
            MerchantParticipationHistoryItem(
                event_id=event.event_id,
                event_title=event.title,
                event_date=event.date,
                participation_status=participant.participation_status,
                readiness_status=participant.readiness_status,
                latest_plan_version=latest_plan_version,
                has_interaction_package=any(
                    package.merchant_id == merchant_id for package in packages
                ),
            )
        )
    items.sort(key=lambda item: (item.event_date, item.event_id), reverse=True)
    return items


def build_merchant_detail(store: MVPStore, merchant: MerchantProfile) -> MerchantDetail:
    return MerchantDetail(
        merchant=merchant,
        participation_history=participation_history(store, merchant.merchant_id),
    )


def evaluate_merchant_for_event(
    event: EventSummary, merchant: MerchantProfile
) -> MerchantEligibility:
    reasons: list[str] = []
    if merchant.status in {"inactive", "suspended"}:
        return MerchantEligibility(
            merchant_id=merchant.merchant_id,
            status="ineligible",
            reasons=[f"merchant status is {merchant.status}"],
        )

    event_window = parse_window(event.time_window)
    merchant_windows = normalized_operating_windows(merchant)
    parsed_merchant_windows = [
        parsed
        for parsed in (
            parse_window(f"{window.start_time}-{window.end_time}")
            for window in merchant_windows
        )
        if parsed is not None
    ]
    if event_window is None:
        reasons.append("event time window needs review")
    elif not parsed_merchant_windows:
        reasons.append("merchant operating window is missing")
    elif not any(
        windows_overlap(event_window, merchant_window)
        for merchant_window in parsed_merchant_windows
    ):
        return MerchantEligibility(
            merchant_id=merchant.merchant_id,
            status="ineligible",
            reasons=["merchant operating window does not overlap event time"],
        )

    if not merchant.contact_name.strip():
        reasons.append("contact owner is missing")
    if not merchant.area.strip():
        reasons.append("merchant area is missing")
    if merchant.participation_constraints:
        reasons.extend(
            f"constraint: {item}" for item in merchant.participation_constraints
        )

    return MerchantEligibility(
        merchant_id=merchant.merchant_id,
        status="needs_review" if reasons else "eligible",
        reasons=reasons,
    )
