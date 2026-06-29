from __future__ import annotations

import re
from typing import Literal

from app.schemas import EventBrief, RouteFitResult, RoutePoint


FitLevel = Literal["strong", "medium", "weak"]
RouteRole = Literal["start", "story", "merchant_stop", "rest", "backup", "finish"]
RAINY_TOKENS = {"rain", "rainy", "rainy-day", "covered", "indoor", "backup", "rest", "family"}
CROWD_PENALTY = {"low": 0, "medium": 5, "high": 12}


def tokenize(values: list[str]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(part for part in re.split(r"[^a-zA-Z0-9-]+", value.lower()) if part)
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


def route_tokens(point: RoutePoint) -> set[str]:
    return tokenize([point.name, point.type, point.story, point.visitor_task])


def is_rainy_or_backup_event(event: EventBrief) -> bool:
    return bool(event_tokens(event) & RAINY_TOKENS)


def fit_level(score: int) -> FitLevel:
    if score >= 75:
        return "strong"
    if score >= 55:
        return "medium"
    return "weak"


def append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def route_role(point: RoutePoint, linked_selected_merchants: list[str]) -> RouteRole:
    if linked_selected_merchants:
        return "merchant_stop"
    if point.type in {"backup", "rest"} or point.is_indoor and point.rainy_day_score >= 4:
        return "backup"
    if point.type in {"culture", "creative"}:
        return "story"
    if point.type in {"shopping", "finish"}:
        return "finish"
    return "start"


def score_route_point_for_event(
    event: EventBrief,
    point: RoutePoint,
    selected_merchant_ids: list[str],
) -> RouteFitResult:
    selected_set = set(selected_merchant_ids)
    linked_selected = [
        merchant_id for merchant_id in point.linked_merchants if merchant_id in selected_set
    ]
    matched: list[str] = []
    warnings: list[str] = []
    score = 40

    if point.current_status != "active":
        append_unique(warnings, f"route point status is {point.current_status}")
        score -= 20

    if linked_selected:
        score += min(len(linked_selected) * 16, 32)
        for merchant_id in linked_selected[:4]:
            append_unique(matched, f"linked selected merchant {merchant_id}")
    else:
        append_unique(warnings, "no selected merchant linkage")
        score -= 8

    token_matches = sorted(event_tokens(event) & route_tokens(point))
    for token in token_matches[:6]:
        append_unique(matched, f"matches {token}")
    score += min(len(token_matches), 6) * 4

    if is_rainy_or_backup_event(event):
        score += point.rainy_day_score * 3
        if point.is_indoor:
            score += 10
            append_unique(matched, "indoor rainy-day backup")
        elif point.rainy_day_score <= 2:
            append_unique(warnings, "weak rainy-day backup")
            score -= 8
    else:
        score += point.rainy_day_score

    if 10 <= point.estimated_stay_minutes <= 30:
        score += 8
        append_unique(matched, "stay duration fits guided route")
    elif point.estimated_stay_minutes > 45:
        append_unique(warnings, "estimated stay is long for the event window")
        score -= 8

    crowd_penalty = CROWD_PENALTY.get(point.crowd_risk, 0)
    score -= crowd_penalty
    if point.crowd_risk == "high":
        append_unique(warnings, "high crowd risk")

    bounded_score = max(0, min(score, 100))
    level = fit_level(bounded_score)
    if level == "weak":
        append_unique(warnings, "weak route fit for this event brief")

    role = route_role(point, linked_selected)
    rationale = (
        f"{point.name} is a {level} {role} with score {bounded_score}. "
        f"{'; '.join(matched[:3]) if matched else 'No strong route-event match was found.'}"
    )
    return RouteFitResult(
        point_id=point.point_id,
        score=bounded_score,
        fit_level=level,
        role=role,
        linked_selected_merchants=linked_selected,
        matched_signals=matched,
        warnings=warnings,
        rationale=rationale,
    )


def score_route_points_for_event(
    event: EventBrief,
    route_points: list[RoutePoint],
    selected_merchant_ids: list[str],
) -> list[RouteFitResult]:
    results = [
        score_route_point_for_event(event, point, selected_merchant_ids)
        for point in route_points
    ]
    return sorted(results, key=lambda item: (-item.score, item.point_id))


def route_warnings_for_missing_links(
    selected_merchant_ids: list[str],
    fit: list[RouteFitResult],
) -> list[str]:
    linked = {
        merchant_id
        for item in fit
        for merchant_id in item.linked_selected_merchants
    }
    return [
        f"{merchant_id}: no route point is linked to this selected merchant"
        for merchant_id in selected_merchant_ids
        if merchant_id not in linked
    ]


def assemble_route_points_for_plan(
    event: EventBrief,
    route_points: list[RoutePoint],
    selected_merchant_ids: list[str],
    limit: int = 6,
) -> tuple[list[RoutePoint], list[RouteFitResult], list[str]]:
    active_points = [point for point in route_points if point.current_status == "active"]
    candidates = active_points or route_points
    fit = score_route_points_for_event(event, candidates, selected_merchant_ids)
    selected_ids: list[str] = []
    used: set[str] = set()

    for merchant_id in selected_merchant_ids:
        linked_candidates = [
            item
            for item in fit
            if item.point_id not in used and merchant_id in item.linked_selected_merchants
        ]
        if linked_candidates:
            chosen = linked_candidates[0]
            selected_ids.append(chosen.point_id)
            used.add(chosen.point_id)
        if len(selected_ids) >= limit:
            break

    for item in fit:
        if len(selected_ids) >= limit:
            break
        if item.point_id in used:
            continue
        selected_ids.append(item.point_id)
        used.add(item.point_id)

    selected_set = set(selected_ids)
    selected_merchant_set = set(selected_merchant_ids)
    selected_points = [
        RoutePoint.model_validate(
            {
                **point.model_dump(),
                "linked_merchants": [
                    merchant_id
                    for merchant_id in point.linked_merchants
                    if merchant_id in selected_merchant_set
                ],
            }
        )
        for point in candidates
        if point.point_id in selected_set
    ]

    warnings = route_warnings_for_missing_links(selected_merchant_ids, fit)
    warnings.extend(
        f"{item.point_id}: {warning}"
        for item in fit
        for warning in item.warnings
        if item.point_id in selected_set
    )
    if not active_points and route_points:
        warnings.append("no active route points were available; non-active route points were used")
    if len(selected_points) < min(limit, len(selected_merchant_ids)):
        warnings.append("route coverage is thinner than selected merchant coverage")

    return selected_points, fit, warnings
