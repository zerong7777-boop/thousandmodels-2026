from app.agents.base import AgentBackend
from app.schemas import (
    EventBrief,
    EventPlan,
    MerchantExecutionPack,
    MerchantProfile,
    MerchantTask,
    PlanVersion,
    RoutePoint,
)


def generate_event_plan(
    brief: EventBrief,
    merchants: list[MerchantProfile],
    backend: AgentBackend,
) -> EventPlan:
    raw_plan = backend.plan_event(brief, merchants)
    return EventPlan.model_validate(raw_plan)


def generate_merchant_packs(
    plan: EventPlan,
    merchants: list[MerchantProfile],
) -> list[MerchantExecutionPack]:
    merchant_by_id = {merchant.merchant_id: merchant for merchant in merchants}
    packs = []
    for assignment in plan.merchant_assignments:
        merchant = merchant_by_id.get(assignment.merchant_id)
        if merchant is None:
            continue
        signature = "、".join(merchant.signature_products[:2])
        packs.append(
            MerchantExecutionPack(
                merchant_id=merchant.merchant_id,
                event_id=plan.event_id,
                role=assignment.role,
                time_slot=assignment.time_slot,
                visitor_task=f"到访 {merchant.name}，完成与 {signature} 相关的打卡或问答。",
                preparation_items=[
                    "确认活动时段人手",
                    "准备活动标识与二维码",
                    f"预留特色产品：{signature}",
                ],
                promo_text=f"{merchant.name} 参与旧区夜游活动，凭游客 H5 可领取限定体验或优惠。",
                fallback_instruction="如库存或排队异常，立即更新商户状态，等待主办方确认导流调整。",
            )
        )
    return packs


def generate_plan_version(
    brief: EventBrief,
    merchants: list[MerchantProfile],
    route_points: list[RoutePoint],
    version: int,
    reason: str,
) -> PlanVersion:
    selected_merchants = [merchant.merchant_id for merchant in merchants[:6]]
    selected_points = route_points[:6]
    contingency = int(brief.budget_mop * 0.15)
    return PlanVersion(
        plan_id=f"{brief.event_id}:v{version}",
        event_id=brief.event_id,
        version=version,
        status="draft",
        created_by="OrchestratorAgent",
        created_reason=reason,
        route_points=selected_points,
        merchant_assignments=selected_merchants,
        budget_plan={
            "total_mop": brief.budget_mop,
            "merchant_support_mop": int(brief.budget_mop * 0.35),
            "marketing_mop": int(brief.budget_mop * 0.25),
            "staffing_mop": int(brief.budget_mop * 0.25),
            "contingency_mop": contingency,
        },
        risk_plan=["inventory", "queue", "weather"],
        diff_from_previous=[] if version == 1 else [f"created version {version}"],
    )


def generate_merchant_tasks(
    plan: PlanVersion,
    merchants: list[MerchantProfile],
) -> list[MerchantTask]:
    merchant_by_id = {merchant.merchant_id: merchant for merchant in merchants}
    role_templates = [
        ("集合与开场试吃", "18:10-18:35"),
        ("文化问答与打卡", "18:35-19:00"),
        ("内港故事讲解", "19:00-19:30"),
        ("夜间补给", "19:30-20:00"),
        ("亲子互动备用点", "20:00-20:35"),
        ("路线收尾与手信优惠", "20:35-21:10"),
    ]
    tasks: list[MerchantTask] = []
    for merchant_id, (role, slot) in zip(plan.merchant_assignments, role_templates, strict=False):
        merchant = merchant_by_id.get(merchant_id)
        if not merchant:
            continue
        signature = "、".join(merchant.signature_products[:2])
        tasks.append(
            MerchantTask(
                task_id=f"task_{plan.event_id}_{merchant_id}_v{plan.version}",
                event_id=plan.event_id,
                merchant_id=merchant_id,
                plan_version=plan.version,
                role=role,
                time_slot=slot,
                visitor_task=f"到访 {merchant.name}，完成与 {signature} 相关的打卡或问答。",
                preparation_items=[
                    "确认活动时段人手",
                    "准备活动标识与二维码",
                    f"预留特色产品：{signature}",
                ],
                promo_text=f"{merchant.name} 参与旧区夜游活动，凭游客 H5 可领取限定体验或优惠。",
                fallback_instruction="如库存或排队异常，立即更新商户状态，等待主办方确认导流调整。",
                task_status="active",
            )
        )
    return tasks
