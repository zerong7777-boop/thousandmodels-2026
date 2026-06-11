from datetime import UTC, datetime

from app.schemas import (
    Incident,
    MerchantRuntimeState,
    MerchantTask,
    PlanVersion,
    PublicNotice,
    RecoveryAction,
    RecoveryProposal,
    RoutePoint,
)


def build_inventory_recovery(
    event_id: str,
    state: MerchantRuntimeState,
    fallback_merchant_id: str = "m007",
) -> RecoveryAction:
    return RecoveryAction(
        action_id=f"rec_inventory_{state.merchant_id}",
        event_id=event_id,
        trigger_type="inventory",
        trigger_detail=f"{state.merchant_id} 库存状态变为 {state.inventory_status}",
        recommended_changes=[
            f"暂停向 {state.merchant_id} 推送试吃/购买任务。",
            f"将导流和优惠任务转移到备用商户 {fallback_merchant_id}。",
            "游客端显示临时通知，避免继续排队。",
        ],
        affected_merchants=[state.merchant_id, fallback_merchant_id],
        tourist_notification="福隆老饼家库存紧张，手信优惠已临时切换到新街手信铺。",
        merchant_notification="请更新库存状态，暂停接收新增导流，等待主办方确认恢复。",
    )


def build_weather_recovery(event_id: str, weather_status: str = "heavy_rain") -> RecoveryAction:
    return RecoveryAction(
        action_id="rec_weather_heavy_rain",
        event_id=event_id,
        trigger_type="weather",
        trigger_detail=f"天气工具返回 {weather_status}",
        recommended_changes=[
            "切换为内港咖啡室、内港小展馆、旧区社区客厅组成的雨天路线。",
            "减少户外停留点和街口集合时间。",
            "游客端发布雨天路线通知，商户端同步备用接待安排。",
        ],
        affected_merchants=["m002", "m005", "m008"],
        tourist_notification="受强降雨影响，路线已切换至室内雨天版本，请按 H5 最新点位前往。",
        merchant_notification="请按雨天执行包准备室内接待和分流。",
    )


def build_recovery_proposal(incident: Incident) -> RecoveryProposal:
    if incident.type == "inventory":
        return RecoveryProposal(
            proposal_id=f"rec_{incident.incident_id}",
            incident_id=incident.incident_id,
            event_id=incident.event_id,
            recommended_changes=[
                "暂停库存售罄商户导流",
                "启用新街手信铺作为备用点",
                "向游客 H5 发布路线调整说明",
            ],
            plan_patch={"replace_route_points": [{"from": "rp001", "to": "rp007"}]},
            merchant_task_patch={incident.affected_merchants[0]: "paused", "m007": "active_backup"},
            public_notice_patch="福隆老饼家库存售罄，路线临时调整至新街手信铺。",
            impact_summary="影响 1 个路线点、2 个商户任务和游客端路线提示。",
            requires_approval=True,
            approval_status="pending",
        )
    return RecoveryProposal(
        proposal_id=f"rec_{incident.incident_id}",
        incident_id=incident.incident_id,
        event_id=incident.event_id,
        recommended_changes=["切换室内备用路线", "减少户外停留点", "通知游客按最新 H5 前往"],
        plan_patch={"rain_route": True},
        merchant_task_patch={"m008": "activate_backup"},
        public_notice_patch="因强降雨，活动切换至室内备用路线。",
        impact_summary="影响户外路线点和雨天备用点。",
        requires_approval=True,
        approval_status="pending",
    )


def apply_recovery_proposal(
    current_plan: PlanVersion,
    proposal: RecoveryProposal,
    route_points: list[RoutePoint],
    current_tasks: list[MerchantTask],
) -> tuple[PlanVersion, list[MerchantTask], PublicNotice]:
    next_version = current_plan.version + 1
    route_by_id = {point.point_id: point for point in route_points}
    next_points = list(current_plan.route_points)
    for replacement in proposal.plan_patch.get("replace_route_points", []):
        old_id = replacement.get("from")
        new_id = replacement.get("to")
        if old_id and new_id and new_id in route_by_id:
            next_points = [route_by_id[new_id] if point.point_id == old_id else point for point in next_points]
    if proposal.plan_patch.get("rain_route"):
        indoor = [point for point in route_points if point.is_indoor]
        next_points = indoor[: max(3, min(len(indoor), len(next_points)))]

    next_plan = PlanVersion(
        plan_id=f"{current_plan.event_id}:v{next_version}",
        event_id=current_plan.event_id,
        version=next_version,
        status="approved",
        created_by="RecoveryAgent",
        created_reason=proposal.incident_id,
        route_points=next_points,
        merchant_assignments=current_plan.merchant_assignments,
        budget_plan=current_plan.budget_plan,
        risk_plan=current_plan.risk_plan,
        diff_from_previous=proposal.recommended_changes,
        approved_by="demo-organizer",
        approved_at=datetime.now(UTC).isoformat(),
    )
    patched_tasks = []
    for task in current_tasks:
        payload = task.model_dump()
        payload["plan_version"] = next_version
        payload["task_id"] = f"task_{task.event_id}_{task.merchant_id}_v{next_version}"
        if task.merchant_id in proposal.merchant_task_patch:
            patch_value = proposal.merchant_task_patch[task.merchant_id]
            payload["task_status"] = "paused" if patch_value == "paused" else "active"
            payload["fallback_instruction"] = proposal.impact_summary
        patched_tasks.append(MerchantTask.model_validate(payload))
    notice = PublicNotice(
        notice_id=f"notice_{proposal.proposal_id}",
        event_id=proposal.event_id,
        plan_version=next_version,
        audience="tourist",
        message=proposal.public_notice_patch,
        reason=proposal.incident_id,
        publish_status="published",
        published_at=datetime.now(UTC).isoformat(),
    )
    return next_plan, patched_tasks, notice
