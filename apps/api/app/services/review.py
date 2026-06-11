from app.schemas import AuditLog, EventPlan, OperationalMetric, RecoveryAction, ReviewReport


def generate_review_report(
    plan: EventPlan,
    recovery_actions: list[RecoveryAction],
    audit_logs: list[AuditLog],
    metrics: list[OperationalMetric] | None = None,
) -> ReviewReport:
    approved = [action for action in recovery_actions if action.approval_status == "approved"]
    incidents = "；".join(action.trigger_detail for action in recovery_actions) or "未触发异常"
    approvals = [
        f"{action.action_id}: {action.tourist_notification}" for action in approved
    ] or ["本次演示未执行恢复审批"]
    metric_map = {metric.name: metric for metric in metrics or []}
    metric_lessons = []
    if "h5_visits" in metric_map:
        metric_lessons.append(
            f"H5 访问量 h5_visits={metric_map['h5_visits'].value:.0f}，说明游客端可作为通知主通道。"
        )
    if "incident_response_minutes" in metric_map:
        metric_lessons.append(
            "异常处理耗时 "
            f"incident_response_minutes={metric_map['incident_response_minutes'].value:.0f} 分钟，"
            "后续可把库存阈值前置到商户端。"
        )
    return ReviewReport(
        event_id=plan.event_id,
        summary=f"{plan.theme} 已完成从方案生成、商户执行包、游客端通知到复盘的演示闭环。",
        route_result=f"主路线包含 {len(plan.route)} 个点位；雨天或库存异常可通过 Recovery Agent 切换。",
        merchant_result=f"共生成 {len(plan.merchant_assignments)} 个商户角色分配，覆盖补给、文创、讲解和收尾。",
        incident_summary=incidents,
        agent_actions=[
            "总策划 Agent 生成 EventPlan。",
            "商户匹配和路线规则生成执行包。",
            "Recovery Agent 根据状态触发恢复建议。",
            "复盘 Agent 汇总计划、异常和审计记录。",
        ],
        human_approvals=approvals,
        lessons_learned=[
            *metric_lessons,
            "热门商户需要提前设置库存阈值和备用商户。",
            "雨天路线应优先使用室内点位和高容量商户。",
            "游客端更新必须由主办方确认后发布。",
            f"本次记录 {len(audit_logs)} 条审计事件，可用于实践文章说明责任边界。",
        ],
        next_event_recommendations=[
            "根据 h5_visits 和 checkins_completed 的 mock 指标调整游客导流节奏。",
            "根据 incident_response_minutes 指标缩短商户上报到主办方审批的链路。",
            "接入真实商户状态前，先扩充 mock 数据和异常脚本。",
            "增加居民影响和路线拥堵的人工审核项。",
            "在 deterministic loop 稳定后再接入 Qwen/QwenPaw。",
        ],
    )
