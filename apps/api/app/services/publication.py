from app.schemas import EventSummary, PlanVersion, PublicNotice


def build_public_event(
    event: EventSummary,
    plan: PlanVersion,
    notices: list[PublicNotice],
    legacy_notices: list[str] | None = None,
) -> dict:
    published_notices = [
        notice.model_dump()
        for notice in notices
        if notice.audience == "tourist" and notice.publish_status == "published"
    ]
    notice_messages = [notice["message"] for notice in published_notices]
    for message in legacy_notices or []:
        if message not in notice_messages:
            notice_messages.append(message)
    return {
        "event_id": event.event_id,
        "title": event.title,
        "area": event.area,
        "status": event.status,
        "theme": "旧城夜光：福隆新街到内港的味觉与故事路线",
        "current_plan_version": plan.version,
        "route": [point.name for point in plan.route_points],
        "route_points": [point.model_dump() for point in plan.route_points],
        "marketing_content": [
            "今晚从福隆新街出发，用一条夜游路线读懂澳门旧区。",
            "完成三处打卡任务，可在参与商户领取限定优惠。",
        ],
        "notices": notice_messages,
        "public_notices": published_notices,
        "checkin_tasks": [point.visitor_task for point in plan.route_points],
    }
