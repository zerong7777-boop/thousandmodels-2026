from datetime import UTC, datetime

from app.schemas import (
    CouponRule,
    InShopTouchpoint,
    MerchantInteractionPackage,
    MerchantProfile,
    MerchantTask,
    PlanVersion,
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


def _merchant_tasks(
    merchant_id: str,
    plan_version: PlanVersion,
    tasks: list[MerchantTask],
) -> list[MerchantTask]:
    return [
        task
        for task in tasks
        if task.merchant_id == merchant_id
        and task.event_id == plan_version.event_id
        and task.plan_version == plan_version.version
    ]


def generate_merchant_interaction_packages(
    event_id: str,
    plan_version: PlanVersion,
    merchants: list[MerchantProfile],
    tasks: list[MerchantTask],
    run_id: str | None = None,
) -> list[MerchantInteractionPackage]:
    now = _now()
    assigned_ids = set(plan_version.merchant_assignments)
    packages: list[MerchantInteractionPackage] = []

    for merchant in merchants:
        if merchant.merchant_id not in assigned_ids:
            continue

        merchant_tasks = _merchant_tasks(merchant.merchant_id, plan_version, tasks)
        if not merchant_tasks:
            continue

        merchant_id = merchant.merchant_id
        package_id = f"mip-{event_id}-{merchant_id}-v{plan_version.version}"
        signature = ", ".join(merchant.signature_products[:2]) or merchant.name
        primary_task = merchant_tasks[0]
        task_ids = [task.task_id for task in merchant_tasks]
        evidence_refs = [
            f"plan:{event_id}:v{plan_version.version}",
            *[f"merchant_task:{task.task_id}" for task in merchant_tasks],
        ]

        qr_touchpoint = InShopTouchpoint(
            id=f"tp-{event_id}-{merchant_id}-qr-v{plan_version.version}",
            event_id=event_id,
            merchant_id=merchant_id,
            package_id=package_id,
            touchpoint_type="in_shop_qr",
            label=f"{merchant.name} event QR",
            public_copy=f"Scan here at {merchant.name} to continue the event route and unlock the shop task.",
            token=f"qr-{_slug(event_id)}-{merchant_id}-v{plan_version.version}",
            metrics={},
            created_at=now,
        )
        coupon_touchpoint = InShopTouchpoint(
            id=f"tp-{event_id}-{merchant_id}-coupon-v{plan_version.version}",
            event_id=event_id,
            merchant_id=merchant_id,
            package_id=package_id,
            touchpoint_type="coupon",
            label=f"{merchant.name} visitor coupon",
            public_copy=f"Show this event page at {merchant.name} for a limited {signature} offer.",
            token=f"coupon-{_slug(event_id)}-{merchant_id}-v{plan_version.version}",
            metrics={},
            created_at=now,
        )
        coupon_rule = CouponRule(
            id=f"cr-{event_id}-{merchant_id}-v{plan_version.version}",
            event_id=event_id,
            merchant_id=merchant_id,
            package_id=package_id,
            title=f"{merchant.name} event visitor offer",
            description=f"One visitor can claim one in-shop offer tied to {primary_task.role}.",
            max_redemptions=80,
            per_anonymous_interaction_limit=1,
            status="active",
            created_at=now,
        )

        packages.append(
            MerchantInteractionPackage(
                id=package_id,
                event_id=event_id,
                merchant_id=merchant_id,
                plan_version=plan_version.version,
                status="active",
                operator_brief=(
                    f"Prepare {signature}, display the QR near the counter, and guide visitors through: "
                    f"{primary_task.visitor_task}"
                ),
                visitor_pitch=f"Visit {merchant.name} for {signature} and complete a local event task.",
                task_ids=task_ids,
                touchpoints=[qr_touchpoint, coupon_touchpoint],
                coupon_rules=[coupon_rule],
                evidence_refs=evidence_refs,
                generated_from_run_id=run_id,
                created_at=now,
                updated_at=now,
            )
        )

    return packages
