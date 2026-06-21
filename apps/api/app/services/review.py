from app.schemas import AuditLog, EventPlan, OperationalMetric, RecoveryAction, ReviewReport


def generate_review_report(
    plan: EventPlan,
    recovery_actions: list[RecoveryAction],
    audit_logs: list[AuditLog],
    metrics: list[OperationalMetric] | None = None,
    touchpoint_summary: dict | None = None,
    merchant_outcomes: list[dict] | None = None,
    extension_tasks: list[dict] | None = None,
) -> ReviewReport:
    approved = [action for action in recovery_actions if action.approval_status == "approved"]
    incidents = "; ".join(action.trigger_detail for action in recovery_actions) or "No exception triggered."
    approvals = [
        f"{action.action_id}: {action.tourist_notification}" for action in approved
    ] or ["No recovery approval was executed in this demo run."]
    metric_map = {metric.name: metric for metric in metrics or []}
    metric_lessons = []
    if "h5_visits" in metric_map:
        metric_lessons.append(
            f"h5_visits={metric_map['h5_visits'].value:.0f}; public H5 can act as the visitor notice channel."
        )
    if "incident_response_minutes" in metric_map:
        metric_lessons.append(
            "incident_response_minutes="
            f"{metric_map['incident_response_minutes'].value:.0f}; merchant status thresholds should stay visible."
        )

    return ReviewReport(
        event_id=plan.event_id,
        summary=(
            f"{plan.theme} completed the deterministic demo loop from plan generation, "
            "merchant execution, visitor notice, and metric-backed review."
        ),
        route_result=(
            f"The main route contains {len(plan.route)} stops; inventory and weather exceptions "
            "can be handled through the recovery approval flow."
        ),
        merchant_result=(
            f"{len(plan.merchant_assignments)} merchant roles were assigned across supply, "
            "creative, story, and closing tasks."
        ),
        incident_summary=incidents,
        agent_actions=[
            "Coordinator generated the event plan.",
            "Merchant matching and route rules produced execution packages.",
            "Recovery logic drafted exception handling options from runtime state.",
            "Review logic summarized plans, exceptions, audit logs, and touchpoint metrics.",
        ],
        human_approvals=approvals,
        lessons_learned=[
            *metric_lessons,
            "Popular merchants need earlier inventory thresholds and fallback merchants.",
            "Rain-route planning should prioritize indoor stops and higher-capacity merchants.",
            "Visitor-facing updates must be published only after organizer confirmation.",
            "责任边界需要在主办方确认、商户执行、游客通知之间保持清晰。",
            f"{len(audit_logs)} audit events were recorded for responsibility tracing.",
        ],
        next_event_recommendations=[
            "Use h5_visits and checkins_completed to tune visitor guidance timing.",
            "Use incident_response_minutes to shorten merchant report and organizer approval paths.",
            "Before real merchant integration, keep expanding simulated metrics and exception scripts.",
            "Add manual review points for resident impact and route congestion.",
        ],
        touchpoint_summary=touchpoint_summary or {},
        merchant_outcomes=merchant_outcomes or [],
        extension_tasks=extension_tasks or [],
    )
