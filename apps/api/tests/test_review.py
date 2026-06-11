from app.agents.deterministic import DeterministicAgentBackend
from app.audit import build_audit_log
from app.schemas import EventBrief, MerchantProfile
from app.services.planning import generate_event_plan
from app.services.recovery import build_weather_recovery
from app.services.review import generate_review_report


def demo_merchants() -> list[MerchantProfile]:
    return [
        MerchantProfile(
            merchant_id="m001",
            name="福隆老饼家",
            type="老字号糕点店",
            location={"lat": 22.193, "lng": 113.539, "label": "福隆新街"},
            opening_hours="10:00-20:00",
            capacity_level="medium",
            signature_products=["杏仁饼", "蛋卷"],
            story="三十多年旧区糕点店。",
            suitable_activity_types=["试吃", "打卡", "老店故事"],
            rainy_day_score=3,
            night_score=5,
            constraints=["19:00 后人手减少"],
        )
    ]


def test_review_report_mentions_approved_actions():
    brief = EventBrief(
        event_id="demo-night-tour",
        area="福隆新街-新马路-内港",
        date="2026-07-18",
        time_window="18:00-21:30",
        budget_mop=50000,
        target_audience=["年轻游客"],
        event_goal="旧区夜游",
        theme_preferences=["夜游"],
        constraints=[],
        priority_rules=["人工确认"],
    )
    plan = generate_event_plan(brief, demo_merchants(), DeterministicAgentBackend())
    action = build_weather_recovery("demo-night-tour")
    action.approval_status = "approved"
    report = generate_review_report(
        plan,
        [action],
        [build_audit_log("demo-night-tour", "organizer", "demo", "approve", "确认恢复")],
    )
    assert report.event_id == "demo-night-tour"
    assert report.human_approvals
    assert "责任边界" in " ".join(report.lessons_learned)
