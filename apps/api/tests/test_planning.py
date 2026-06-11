from app.agents.deterministic import DeterministicAgentBackend
from app.schemas import EventBrief, EventPlan, MerchantProfile
from app.services.planning import generate_event_plan, generate_merchant_packs


def demo_brief() -> EventBrief:
    return EventBrief(
        event_id="demo-night-tour",
        area="福隆新街-新马路-内港",
        date="2026-07-18",
        time_window="18:00-21:30",
        budget_mop=50000,
        target_audience=["年轻游客", "亲子游客"],
        event_goal="吸引游客进入旧区，结合美食、文化故事和打卡互动",
        theme_preferences=["夜游", "老字号", "文化故事"],
        constraints=["路线不过长", "避免局部拥堵"],
        priority_rules=["优先室内备用点", "保留主办方确认"],
    )


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
        ),
        MerchantProfile(
            merchant_id="m002",
            name="内港咖啡室",
            type="咖啡店",
            location={"lat": 22.1918, "lng": 113.5368, "label": "内港"},
            opening_hours="09:00-22:00",
            capacity_level="high",
            signature_products=["手冲咖啡", "葡挞"],
            story="雨天休息点。",
            suitable_activity_types=["休息点", "雨天备用"],
            rainy_day_score=5,
            night_score=4,
            constraints=[],
        ),
    ]


def test_event_brief_accepts_demo_event():
    brief = demo_brief()
    assert brief.event_id == "demo-night-tour"
    assert brief.budget_mop == 50000


def test_merchant_profile_has_demo_routing_fields():
    merchant = demo_merchants()[0]
    assert merchant.rainy_day_score == 3
    assert "杏仁饼" in merchant.signature_products


def test_generate_event_plan_contains_core_modules():
    plan = generate_event_plan(demo_brief(), demo_merchants(), DeterministicAgentBackend())
    assert isinstance(plan, EventPlan)
    assert plan.event_id == "demo-night-tour"
    assert plan.route
    assert plan.budget_plan.total_mop == 50000
    assert plan.risk_plan
    assert plan.approval_status == "draft"


def test_generate_merchant_packs_match_assignments():
    merchants = demo_merchants()
    plan = generate_event_plan(demo_brief(), merchants, DeterministicAgentBackend())
    packs = generate_merchant_packs(plan, merchants)
    assert len(packs) == len(plan.merchant_assignments)
    assert all(pack.fallback_instruction for pack in packs)
