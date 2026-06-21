import hashlib
import json
from datetime import UTC, datetime

from app.schemas import OperationSuggestion, PlanVersion, PublicNotice
from app.services.touchpoints import summarize_touchpoint_metrics
from app.store import STORE


def _now() -> str:
    return datetime.now(UTC).isoformat()


ACTIVE_INCIDENT_STATUSES = {"open", "proposal_ready"}


class OperationSuggestionError(ValueError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _current_approved_plan(event_id: str) -> PlanVersion:
    event = STORE.get_event_summary(event_id)
    if event is None:
        raise OperationSuggestionError("event not found", status_code=404)
    plan = STORE.get_plan_version(event_id, event.current_plan_version)
    if plan is None:
        raise OperationSuggestionError("current plan not found", status_code=404)
    if plan.status != "approved":
        raise OperationSuggestionError("current plan is not approved", status_code=400)
    return plan


def _allowed_merchant_ids(plan: PlanVersion) -> set[str]:
    return set(plan.merchant_assignments)


def _route_points_for_merchants(plan: PlanVersion, merchant_ids: list[str]) -> list[str]:
    merchant_set = set(merchant_ids)
    return [
        point.point_id
        for point in plan.route_points
        if merchant_set.intersection(point.linked_merchants)
    ]


def _payload_signature(suggestion: OperationSuggestion) -> str:
    payload = suggestion.model_dump()
    payload.pop("status", None)
    payload.pop("created_at", None)
    payload.pop("approved_at", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _payload_matches(left: OperationSuggestion, right: OperationSuggestion) -> bool:
    return _payload_signature(left) == _payload_signature(right)


def _refresh_id(suggestion: OperationSuggestion) -> str:
    digest = hashlib.sha1(_payload_signature(suggestion).encode("utf-8")).hexdigest()[:10]
    return f"{suggestion.id}_refresh_{digest}"


def _merge_current_with_existing(
    suggestion: OperationSuggestion,
    *,
    persist: bool,
) -> OperationSuggestion:
    existing = STORE.get_operation_suggestion(suggestion.event_id, suggestion.id)
    if existing is None:
        return STORE.save_operation_suggestion(suggestion) if persist else suggestion
    if existing.status in {"draft", "pending_approval"}:
        suggestion.status = existing.status
        suggestion.created_at = existing.created_at
        suggestion.approved_at = None
        return STORE.save_operation_suggestion(suggestion) if persist else suggestion
    if _payload_matches(existing, suggestion):
        return existing

    suggestion.id = _refresh_id(suggestion)
    refreshed = STORE.get_operation_suggestion(suggestion.event_id, suggestion.id)
    if refreshed and refreshed.status in {"approved", "applied"} and _payload_matches(refreshed, suggestion):
        return refreshed
    if refreshed and refreshed.status in {"draft", "pending_approval"}:
        suggestion.status = refreshed.status
        suggestion.created_at = refreshed.created_at
    return STORE.save_operation_suggestion(suggestion) if persist else suggestion


def _runtime_suggestions(
    event_id: str,
    plan: PlanVersion,
    allowed_merchant_ids: set[str],
) -> list[OperationSuggestion]:
    suggestions: list[OperationSuggestion] = []
    incidents = [
        incident
        for incident in STORE.list_incidents(event_id)
        if incident.status in ACTIVE_INCIDENT_STATUSES
    ]
    incident_refs_by_merchant: dict[str, list[str]] = {}
    for incident in incidents:
        for merchant_id in incident.affected_merchants:
            incident_refs_by_merchant.setdefault(merchant_id, []).append(
                f"incident:{incident.incident_id}"
            )

    for state in STORE.list_runtime_states():
        merchant_id = state.merchant_id
        if merchant_id not in allowed_merchant_ids:
            continue
        route_points = _route_points_for_merchants(plan, [merchant_id])
        evidence_refs = [
            f"runtime_state:{merchant_id}",
            *incident_refs_by_merchant.get(merchant_id, []),
        ]
        if state.inventory_status == "sold_out" or not state.available_for_visitors:
            suggestions.append(
                OperationSuggestion(
                    id=f"os_{event_id}_{merchant_id}_merchant_capacity",
                    event_id=event_id,
                    suggestion_type="merchant_capacity",
                    status="pending_approval",
                    title=f"Pause visitor flow for {merchant_id}",
                    rationale=(
                        f"{merchant_id} reported inventory_status={state.inventory_status} "
                        f"and available_for_visitors={state.available_for_visitors}."
                    ),
                    recommended_actions=[
                        {
                            "action": "pause_or_reduce_assignment",
                            "merchant_id": merchant_id,
                            "requires_recovery_proposal": True,
                        },
                        {
                            "action": "prepare_backup_capacity",
                            "route_points": route_points,
                            "requires_recovery_proposal": True,
                        },
                    ],
                    impacted_merchants=[merchant_id],
                    impacted_route_points=route_points,
                    evidence_refs=evidence_refs,
                    created_at=_now(),
                )
            )
        if state.queue_status in {"busy", "overloaded"}:
            suggestions.append(
                OperationSuggestion(
                    id=f"os_{event_id}_{merchant_id}_queue_notice",
                    event_id=event_id,
                    suggestion_type="public_notice",
                    status="pending_approval",
                    title=f"Warn visitors about queue pressure at {merchant_id}",
                    rationale=f"{merchant_id} reported queue_status={state.queue_status}.",
                    recommended_actions=[
                        {
                            "action": "publish_queue_notice",
                            "merchant_id": merchant_id,
                            "message": (
                                f"{merchant_id} is experiencing a {state.queue_status} queue. "
                                "Please follow organizer guidance and use nearby route points first."
                            ),
                        }
                    ],
                    impacted_merchants=[merchant_id],
                    impacted_route_points=route_points,
                    evidence_refs=[f"runtime_state:{merchant_id}"],
                    created_at=_now(),
                )
            )
    return suggestions


def _touchpoint_suggestions(
    event_id: str,
    plan: PlanVersion,
    allowed_merchant_ids: set[str],
) -> list[OperationSuggestion]:
    summary = summarize_touchpoint_metrics(event_id)
    suggestions: list[OperationSuggestion] = []
    for row in summary["merchant_outcomes"]:
        merchant_id = row["merchant_id"]
        if not merchant_id or merchant_id not in allowed_merchant_ids:
            continue
        scans = summary["by_merchant"].get(merchant_id, {}).get("scan", 0)
        claims = row["coupon_claims"]
        redemptions = row["coupon_redemptions"]
        evidence_refs = [
            f"touchpoint_metrics:{event_id}:{merchant_id}",
            "touchpoint_summary:coupon_claims",
            "touchpoint_summary:coupon_redemptions",
        ]
        if claims >= 3 and redemptions == 0:
            suggestions.append(
                OperationSuggestion(
                    id=f"os_{event_id}_{merchant_id}_coupon_rebalance",
                    event_id=event_id,
                    suggestion_type="coupon_rebalance",
                    status="pending_approval",
                    title=f"Rebalance coupon follow-up for {merchant_id}",
                    rationale=(
                        f"{merchant_id} has {claims} coupon claims and "
                        f"{redemptions} redemptions."
                    ),
                    recommended_actions=[
                        {
                            "action": "review_coupon_offer",
                            "merchant_id": merchant_id,
                            "claims": claims,
                            "redemptions": redemptions,
                        }
                    ],
                    impacted_merchants=[merchant_id],
                    impacted_route_points=_route_points_for_merchants(plan, [merchant_id]),
                    evidence_refs=evidence_refs,
                    created_at=_now(),
                )
            )
        if scans >= 3 and redemptions == 0:
            suggestions.append(
                OperationSuggestion(
                    id=f"os_{event_id}_{merchant_id}_extension_task",
                    event_id=event_id,
                    suggestion_type="extension_task",
                    status="pending_approval",
                    title=f"Create conversion follow-up task for {merchant_id}",
                    rationale=(
                        f"{merchant_id} has {scans} scans but "
                        f"{redemptions} coupon redemptions."
                    ),
                    recommended_actions=[
                        {
                            "action": "create_follow_up_task",
                            "merchant_id": merchant_id,
                            "scans": scans,
                            "redemptions": redemptions,
                        }
                    ],
                    impacted_merchants=[merchant_id],
                    impacted_route_points=_route_points_for_merchants(plan, [merchant_id]),
                    evidence_refs=evidence_refs,
                    created_at=_now(),
                )
            )
    return suggestions


def _current_generated_suggestions(event_id: str) -> list[OperationSuggestion]:
    plan = _current_approved_plan(event_id)
    allowed_merchant_ids = _allowed_merchant_ids(plan)
    return [
        *_runtime_suggestions(event_id, plan, allowed_merchant_ids),
        *_touchpoint_suggestions(event_id, plan, allowed_merchant_ids),
    ]


def list_current_operation_suggestions(event_id: str) -> list[OperationSuggestion]:
    return [
        _merge_current_with_existing(suggestion, persist=False)
        for suggestion in _current_generated_suggestions(event_id)
    ]


def generate_operation_suggestions(event_id: str) -> list[OperationSuggestion]:
    return [
        _merge_current_with_existing(suggestion, persist=True)
        for suggestion in _current_generated_suggestions(event_id)
    ]


def _notice_message(suggestion: OperationSuggestion) -> str:
    for action in suggestion.recommended_actions:
        message = action.get("message")
        if message:
            return str(message)
    return suggestion.title


def approve_operation_suggestion(event_id: str, suggestion_id: str) -> OperationSuggestion:
    current = {
        suggestion.id: suggestion
        for suggestion in list_current_operation_suggestions(event_id)
    }
    suggestion = current.get(suggestion_id)
    if suggestion is None:
        raise ValueError("operation suggestion not found")
    if suggestion.status in {"approved", "applied"}:
        return suggestion

    suggestion.approved_at = _now()
    if suggestion.suggestion_type == "public_notice":
        event = STORE.get_event_summary(event_id)
        plan_version = event.current_plan_version if event and event.current_plan_version else 1
        notice = PublicNotice(
            notice_id=f"notice_{suggestion.id}",
            event_id=event_id,
            plan_version=plan_version,
            audience="tourist",
            message=_notice_message(suggestion),
            reason=suggestion.rationale,
            publish_status="draft",
        )
        STORE.save_public_notice(notice)
        suggestion.status = "applied"
    else:
        suggestion.status = "approved"
    return STORE.save_operation_suggestion(suggestion)
