from collections import Counter, defaultdict
from datetime import UTC, datetime
from uuid import uuid4

from app.schemas import CouponRedemption, TouchpointInteraction
from app.store import STORE

IDENTITY_METADATA_KEYS = {
    "visitor_id",
    "visitor_profile",
    "user_id",
    "session_id",
    "phone",
    "email",
    "openid",
    "open_id",
    "device_id",
    "payment_id",
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _coupon_touchpoint_id(event_id: str, merchant_id: str, package_id: str | None) -> str | None:
    touchpoints = STORE.list_touchpoints(event_id, merchant_id=merchant_id)
    for touchpoint in touchpoints:
        if touchpoint.touchpoint_type == "coupon" and touchpoint.package_id == package_id:
            return touchpoint.id
    return touchpoints[0].id if touchpoints else None


def sanitize_public_metadata(metadata: dict | None) -> dict:
    clean = {}
    for key, value in (metadata or {}).items():
        key_text = str(key)
        normalized = key_text.lower()
        if normalized in IDENTITY_METADATA_KEYS:
            continue
        if normalized.endswith("_id") and normalized not in {"coupon_rule_id", "redemption_id"}:
            continue
        clean[key_text] = value
    return clean


def record_touchpoint_interaction(
    event_id: str,
    touchpoint_id: str,
    interaction_type: str,
    source: str = "demo",
    anonymous_interaction_id: str | None = None,
    metadata: dict | None = None,
) -> TouchpointInteraction:
    touchpoint = STORE.get_touchpoint(event_id, touchpoint_id)
    if not touchpoint:
        raise ValueError("touchpoint not found")
    if touchpoint.status != "active":
        raise ValueError("touchpoint is not active")

    anonymous_id = anonymous_interaction_id or _new_id("anon")
    interaction = TouchpointInteraction(
        id=_new_id("tpi"),
        event_id=event_id,
        touchpoint_id=touchpoint_id,
        merchant_id=touchpoint.merchant_id,
        interaction_type=interaction_type,
        source=source or "demo",
        anonymous_interaction_id=anonymous_id,
        created_at=_now(),
        metadata=sanitize_public_metadata(metadata),
    )
    metrics = dict(touchpoint.metrics or {})
    metrics["total_interactions"] = metrics.get("total_interactions", 0) + 1
    metrics[interaction_type] = metrics.get(interaction_type, 0) + 1
    touchpoint.metrics = metrics
    STORE.save_touchpoint(touchpoint)
    return STORE.save_touchpoint_interaction(interaction)


def claim_coupon(
    event_id: str,
    coupon_rule_id: str,
    anonymous_interaction_id: str,
) -> CouponRedemption:
    if not anonymous_interaction_id:
        raise ValueError("anonymous_interaction_id is required")
    rule = STORE.get_coupon_rule(event_id, coupon_rule_id)
    if not rule:
        raise ValueError("coupon rule not found")
    if rule.status != "active":
        raise ValueError("coupon rule is not active")

    existing = [
        redemption
        for redemption in STORE.list_coupon_redemptions(event_id, merchant_id=rule.merchant_id)
        if redemption.coupon_rule_id == coupon_rule_id
        and redemption.status in {"claimed", "redeemed"}
    ]
    if len(existing) >= rule.max_redemptions:
        raise ValueError("coupon max redemptions reached")
    anonymous_claims = [
        redemption
        for redemption in existing
        if redemption.anonymous_interaction_id == anonymous_interaction_id
    ]
    if len(anonymous_claims) >= rule.per_anonymous_interaction_limit:
        raise ValueError("anonymous coupon limit reached")

    redemption = CouponRedemption(
        id=_new_id("redemption"),
        event_id=event_id,
        coupon_rule_id=coupon_rule_id,
        merchant_id=rule.merchant_id,
        anonymous_interaction_id=anonymous_interaction_id,
        status="claimed",
        claimed_at=_now(),
    )
    saved = STORE.save_coupon_redemption(redemption)
    touchpoint_id = _coupon_touchpoint_id(event_id, rule.merchant_id, rule.package_id)
    if touchpoint_id:
        record_touchpoint_interaction(
            event_id=event_id,
            touchpoint_id=touchpoint_id,
            interaction_type="claim",
            source="coupon",
            anonymous_interaction_id=anonymous_interaction_id,
            metadata={"coupon_rule_id": coupon_rule_id, "redemption_id": saved.id},
        )
    return saved


def redeem_coupon(event_id: str, redemption_id: str) -> CouponRedemption:
    redemption = STORE.get_coupon_redemption(event_id, redemption_id)
    if not redemption:
        raise ValueError("coupon redemption not found")
    if redemption.status == "redeemed":
        return redemption
    if redemption.status != "claimed":
        raise ValueError("coupon redemption is not claimable")

    rule = STORE.get_coupon_rule(event_id, redemption.coupon_rule_id)
    active_redemptions = [
        item
        for item in STORE.list_coupon_redemptions(event_id, merchant_id=redemption.merchant_id)
        if item.coupon_rule_id == redemption.coupon_rule_id
        and item.status in {"claimed", "redeemed"}
    ]
    if rule and len(active_redemptions) > rule.max_redemptions:
        raise ValueError("coupon max redemptions reached")

    redemption.status = "redeemed"
    redemption.redeemed_at = _now()
    saved = STORE.save_coupon_redemption(redemption)
    if rule:
        touchpoint_id = _coupon_touchpoint_id(event_id, redemption.merchant_id, rule.package_id)
        if touchpoint_id:
            record_touchpoint_interaction(
                event_id=event_id,
                touchpoint_id=touchpoint_id,
                interaction_type="redeem",
                source="coupon",
                anonymous_interaction_id=redemption.anonymous_interaction_id,
                metadata={
                    "coupon_rule_id": redemption.coupon_rule_id,
                    "redemption_id": redemption.id,
                },
            )
    return saved


def summarize_touchpoint_metrics(event_id: str, merchant_id: str | None = None) -> dict:
    interactions = STORE.list_touchpoint_interactions(event_id, merchant_id=merchant_id)
    redemptions = STORE.list_coupon_redemptions(event_id, merchant_id=merchant_id)
    interaction_types = Counter(interaction.interaction_type for interaction in interactions)
    merchant_ids = sorted(
        {
            value
            for value in [
                *(interaction.merchant_id for interaction in interactions),
                *(redemption.merchant_id for redemption in redemptions),
            ]
            if value
        }
    )

    by_merchant: dict[str, dict] = defaultdict(
        lambda: {
            "view": 0,
            "scan": 0,
            "claim": 0,
            "redeem": 0,
            "status_check": 0,
            "coupon_claims": 0,
            "coupon_redemptions": 0,
        }
    )
    merchant_rows: dict[str, dict] = defaultdict(
        lambda: {
            "merchant_id": "",
            "total_interactions": 0,
            "coupon_claims": 0,
            "coupon_redemptions": 0,
        }
    )
    for interaction in interactions:
        if not interaction.merchant_id:
            continue
        by_merchant[interaction.merchant_id][interaction.interaction_type] += 1
        row = merchant_rows[interaction.merchant_id]
        row["merchant_id"] = interaction.merchant_id
        row["total_interactions"] += 1
    for redemption in redemptions:
        by_merchant[redemption.merchant_id]["coupon_claims"] += int(redemption.status in {"claimed", "redeemed"})
        by_merchant[redemption.merchant_id]["coupon_redemptions"] += int(redemption.status == "redeemed")
        row = merchant_rows[redemption.merchant_id]
        row["merchant_id"] = redemption.merchant_id
        if redemption.status in {"claimed", "redeemed"}:
            row["coupon_claims"] += 1
        if redemption.status == "redeemed":
            row["coupon_redemptions"] += 1

    coupon_claims = len(
        [redemption for redemption in redemptions if redemption.status in {"claimed", "redeemed"}]
    )
    coupon_redemptions = len([redemption for redemption in redemptions if redemption.status == "redeemed"])
    by_type = {
        interaction_type: interaction_types.get(interaction_type, 0)
        for interaction_type in ["view", "scan", "claim", "redeem", "status_check"]
    }
    redemption_rate = round(coupon_redemptions / coupon_claims, 4) if coupon_claims else 0.0
    extension_tasks = []
    if interactions or redemptions:
        extension_tasks.append(
            {
                "task_type": "touchpoint_follow_up",
                "title": "Review in-shop touchpoint conversion",
                "metric_refs": [
                    "total_interactions",
                    "coupon_claims",
                    "coupon_redemptions",
                ],
                "merchant_ids": merchant_ids,
                "rationale": (
                    f"{len(interactions)} touchpoint interactions, {coupon_claims} coupon claims, "
                    f"and {coupon_redemptions} coupon redemptions were recorded."
                ),
            }
        )

    return {
        "event_id": event_id,
        "merchant_id": merchant_id,
        "total_interactions": len(interactions),
        "by_type": by_type,
        "by_merchant": dict(sorted(by_merchant.items())),
        "redemption_rate": redemption_rate,
        "interaction_types": dict(sorted(interaction_types.items())),
        "coupon_claims": coupon_claims,
        "coupon_redemptions": coupon_redemptions,
        "merchant_outcomes": sorted(merchant_rows.values(), key=lambda row: row["merchant_id"]),
        "extension_tasks": extension_tasks,
    }
