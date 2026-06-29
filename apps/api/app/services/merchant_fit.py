from __future__ import annotations

import re
from typing import Literal

from app.schemas import EventBrief, EventSummary, MerchantFitResult, MerchantProfile
from app.services.merchant_network import (
    evaluate_merchant_for_event,
    normalized_operating_windows,
    parse_window,
    windows_overlap,
)


CAPACITY_POINTS = {"low": 4, "medium": 10, "high": 16}
FitLevel = Literal["strong", "medium", "weak"]


def tokenize(values: list[str]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(part for part in re.split(r"[^a-zA-Z0-9]+", value.lower()) if part)
    return tokens


def event_tokens(event: EventBrief) -> set[str]:
    return tokenize(
        [
            event.area,
            event.event_goal,
            *event.target_audience,
            *event.theme_preferences,
            *event.constraints,
            *event.priority_rules,
        ]
    )


def merchant_tokens(merchant: MerchantProfile) -> set[str]:
    return tokenize(
        [
            merchant.name,
            merchant.type,
            merchant.story,
            merchant.capacity_notes,
            *merchant.signature_products,
            *merchant.suitable_activity_types,
            *merchant.category_tags,
            *merchant.constraints,
        ]
    )


def eligibility_summary(event: EventBrief) -> EventSummary:
    return EventSummary(
        event_id=event.event_id,
        title=event.event_goal,
        area=event.area,
        date=event.date,
        time_window=event.time_window,
        status="draft",
        current_plan_version=0,
        public_release_status="draft",
    )


def overlap_minutes(event: EventBrief, merchant: MerchantProfile) -> int:
    event_window = parse_window(event.time_window)
    if not event_window:
        return 0
    overlaps = []
    for window in normalized_operating_windows(merchant):
        merchant_window = parse_window(f"{window.start_time}-{window.end_time}")
        if merchant_window and windows_overlap(event_window, merchant_window):
            overlaps.append(
                min(event_window[1], merchant_window[1])
                - max(event_window[0], merchant_window[0])
            )
    return max(overlaps, default=0)


def fit_level(score: int) -> FitLevel:
    if score >= 75:
        return "strong"
    if score >= 55:
        return "medium"
    return "weak"


def append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def score_merchant_for_event(
    event: EventBrief, merchant: MerchantProfile
) -> MerchantFitResult | None:
    eligibility = evaluate_merchant_for_event(eligibility_summary(event), merchant)
    if eligibility.status == "ineligible":
        return None

    matched: list[str] = []
    warnings: list[str] = []
    score = 50
    score += merchant.night_score * 3
    score += merchant.rainy_day_score * 2
    score += CAPACITY_POINTS.get(merchant.capacity_level, 0)

    token_matches = sorted(event_tokens(event) & merchant_tokens(merchant))
    for token in token_matches[:6]:
        append_unique(matched, f"matches {token}")
    score += min(len(token_matches), 6) * 4

    minutes = overlap_minutes(event, merchant)
    if minutes >= 120:
        append_unique(matched, "operating window covers the event")
        score += 8
    elif minutes > 0:
        append_unique(matched, "operating window partially overlaps the event")
        append_unique(warnings, "operating window overlap is tight")
        score += 3
    else:
        append_unique(warnings, "operating window needs organizer review")
        score -= 8

    if not merchant.contact_name.strip():
        append_unique(warnings, "contact owner is missing")
        score -= 8
    if not merchant.area.strip():
        append_unique(warnings, "merchant area is missing")
        score -= 6
    if merchant.participation_constraints:
        for constraint in merchant.participation_constraints:
            append_unique(warnings, f"constraint: {constraint}")
        score -= min(len(merchant.participation_constraints) * 5, 12)
    if eligibility.status == "needs_review":
        for reason in eligibility.reasons:
            append_unique(warnings, reason)
        score -= 5

    bounded_score = max(0, min(score, 100))
    level = fit_level(bounded_score)
    if level == "weak":
        append_unique(warnings, "weak merchant fit for this event brief")

    rationale = (
        f"{merchant.name} is a {level} fit with score {bounded_score}. "
        f"{'; '.join(matched[:3]) if matched else 'No strong profile-event match was found.'}"
    )
    return MerchantFitResult(
        merchant_id=merchant.merchant_id,
        score=bounded_score,
        fit_level=level,
        matched_signals=matched,
        warnings=warnings,
        rationale=rationale,
    )


def score_merchants_for_event(
    event: EventBrief, merchants: list[MerchantProfile]
) -> list[MerchantFitResult]:
    results = [
        result
        for merchant in merchants
        if (result := score_merchant_for_event(event, merchant)) is not None
    ]
    return sorted(results, key=lambda item: (-item.score, item.merchant_id))
