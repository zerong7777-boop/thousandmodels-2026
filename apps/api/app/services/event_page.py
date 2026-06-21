from datetime import UTC, datetime
from typing import Any

from app.schemas import EventPage, EventSummary, MerchantProfile, PlanVersion, PublicNotice, RoutePoint


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _notice_payloads(notices: list[PublicNotice]) -> list[dict[str, Any]]:
    return [
        {
            "message": notice.message,
            "plan_version": notice.plan_version,
            "published_at": notice.published_at,
        }
        for notice in notices
        if notice.audience == "tourist" and notice.publish_status == "published"
    ]


def _merchant_lookup(merchants: list[MerchantProfile]) -> dict[str, MerchantProfile]:
    return {merchant.merchant_id: merchant for merchant in merchants}


def _linked_merchants(
    route_point: RoutePoint,
    merchants_by_id: dict[str, MerchantProfile],
) -> list[dict[str, Any]]:
    highlights: list[dict[str, Any]] = []
    for merchant_id in route_point.linked_merchants:
        merchant = merchants_by_id.get(merchant_id)
        if not merchant:
            continue
        highlights.append(
            {
                "id": merchant.merchant_id,
                "name": merchant.name,
                "type": merchant.type,
                "story": merchant.story,
                "signature_products": merchant.signature_products[:3],
            }
        )
    return highlights


def _public_touchpoints(package: Any) -> list[dict[str, Any]]:
    return [
        {
            "id": touchpoint.id,
            "touchpoint_type": touchpoint.touchpoint_type,
            "label": touchpoint.label,
            "public_copy": touchpoint.public_copy,
            "status": touchpoint.status,
        }
        for touchpoint in getattr(package, "touchpoints", []) or []
        if touchpoint.status == "active"
    ]


def _public_coupon_rules(package: Any) -> list[dict[str, Any]]:
    return [
        {
            "id": rule.id,
            "title": rule.title,
            "description": rule.description,
            "status": rule.status,
        }
        for rule in getattr(package, "coupon_rules", []) or []
        if rule.status == "active"
    ]


def build_event_page_draft(
    event: EventSummary,
    plan_version: PlanVersion,
    route_points: list[RoutePoint],
    merchants: list[MerchantProfile],
    notices: list[PublicNotice],
    run_id: str | None = None,
) -> EventPage:
    merchants_by_id = _merchant_lookup(merchants)
    active_route_points = [
        point for point in route_points if point.current_status != "paused"
    ] or route_points
    now = _now()

    story_sections = [
        {
            "heading": point.name,
            "body": point.story,
            "visitor_task": point.visitor_task,
        }
        for point in active_route_points[:6]
    ]
    route_highlights = [
        {
            "id": point.point_id,
            "name": point.name,
            "type": point.type,
            "estimated_stay_minutes": point.estimated_stay_minutes,
            "visitor_task": point.visitor_task,
            "linked_merchants": _linked_merchants(point, merchants_by_id),
        }
        for point in active_route_points
    ]

    seen_merchants: set[str] = set()
    merchant_highlights: list[dict[str, Any]] = []
    assigned_ids = list(plan_version.merchant_assignments)
    linked_ids = [
        merchant_id
        for point in active_route_points
        for merchant_id in point.linked_merchants
    ]
    for merchant_id in [*assigned_ids, *linked_ids]:
        if merchant_id in seen_merchants:
            continue
        merchant = merchants_by_id.get(merchant_id)
        if not merchant:
            continue
        seen_merchants.add(merchant_id)
        merchant_highlights.append(
            {
                "id": merchant.merchant_id,
                "name": merchant.name,
                "type": merchant.type,
                "story": merchant.story,
                "signature_products": merchant.signature_products[:3],
                "visitor_pitch": f"Stop by {merchant.name} for {', '.join(merchant.signature_products[:2])}.",
            }
        )

    return EventPage(
        id=f"event-page-{event.event_id}-v{plan_version.version}",
        event_id=event.event_id,
        plan_version=plan_version.version,
        status="draft",
        title=event.title,
        subtitle=f"{event.area} · {event.date} {event.time_window}",
        story_sections=story_sections,
        route_highlights=route_highlights,
        merchant_highlights=merchant_highlights,
        notices=_notice_payloads(notices),
        generated_from_run_id=run_id,
        updated_at=now,
    )


def publish_event_page(page: EventPage) -> EventPage:
    payload = page.model_dump()
    now = _now()
    payload["status"] = "published"
    payload["published_at"] = page.published_at or now
    payload["updated_at"] = now
    return EventPage.model_validate(payload)


def build_event_page_projection(
    event: EventSummary,
    page: EventPage,
    plan_version: PlanVersion,
    notices: list[PublicNotice],
    packages: list[Any] | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coupon_count = 0
    package_count = 0
    packages_by_merchant = {}
    for package in packages or []:
        package_count += 1
        coupon_count += len(getattr(package, "coupon_rules", []) or [])
        if getattr(package, "status", None) == "active":
            packages_by_merchant[getattr(package, "merchant_id", "")] = package

    merchant_highlights = []
    for highlight in page.merchant_highlights:
        public_highlight = dict(highlight)
        package = packages_by_merchant.get(str(public_highlight.get("id", "")))
        if package:
            public_highlight["touchpoints"] = _public_touchpoints(package)
            public_highlight["coupon_rules"] = _public_coupon_rules(package)
        merchant_highlights.append(public_highlight)

    return {
        "id": page.id,
        "event_id": event.event_id,
        "status": page.status,
        "title": page.title,
        "subtitle": page.subtitle,
        "story_sections": page.story_sections,
        "route_highlights": page.route_highlights,
        "merchant_highlights": merchant_highlights,
        "notices": page.notices or _notice_payloads(notices),
        "current_plan_version": plan_version.version,
        "interaction_status": {
            "merchant_packages": package_count,
            "coupon_rules": coupon_count,
            "metrics": metrics or {},
        },
        "published_at": page.published_at,
    }
