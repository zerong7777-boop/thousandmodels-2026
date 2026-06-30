import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    EventBrief,
    Location,
    MerchantOperatingWindow,
    MerchantProfile,
    MerchantSetupSubmitRequest,
    RoutePoint,
)
from app.seed import seed_demo
from app.services.route_assembly import score_route_points_for_event
from app.services.merchant_setup import submit_merchant_setup
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "v32-route-assembly-quality"


@pytest.fixture(autouse=True)
def clear_v32_event():
    STORE.clear_route_points()
    STORE.clear_demo(EVENT_ID)
    yield
    STORE.clear_demo(EVENT_ID)
    STORE.clear_route_points()


def event_brief(event_id: str = "v32-route") -> EventBrief:
    return EventBrief(
        event_id=event_id,
        area="Inner Harbor",
        date="2026-10-10",
        time_window="18:00-21:00",
        budget_mop=120000,
        target_audience=["family"],
        event_goal="Rainy night food walk with covered rest stops.",
        theme_preferences=["tea", "street stories", "rainy-day"],
        constraints=["covered stop", "avoid crowd bottleneck"],
        priority_rules=["prefer indoor backup", "cover selected merchants"],
    )


def route_point(point_id: str, **overrides) -> RoutePoint:
    data = {
        "point_id": point_id,
        "name": "Harbor Tea Rest Stop",
        "type": "food",
        "is_indoor": True,
        "estimated_stay_minutes": 20,
        "story": "Covered family tea stop with local street stories.",
        "linked_merchants": ["m930"],
        "visitor_task": "Taste tea and complete the rainy-day story card.",
        "rainy_day_score": 5,
        "crowd_risk": "low",
        "current_status": "active",
    }
    data.update(overrides)
    return RoutePoint(**data)


def test_route_scoring_prefers_linked_indoor_rainy_fit():
    results = score_route_points_for_event(
        event_brief(),
        [
            route_point(
                "weak-unlinked",
                name="Outdoor Plaza",
                type="street",
                is_indoor=False,
                rainy_day_score=1,
                crowd_risk="high",
                linked_merchants=[],
                story="Open plaza.",
                visitor_task="Stand outside.",
            ),
            route_point("strong-linked"),
        ],
        ["m930"],
    )

    assert [item.point_id for item in results] == ["strong-linked", "weak-unlinked"]
    assert results[0].fit_level == "strong"
    assert results[0].role == "merchant_stop"
    assert results[0].linked_selected_merchants == ["m930"]
    assert results[1].fit_level == "weak"
    assert results[1].warnings


def test_route_scoring_warns_for_unlinked_high_crowd_point():
    result = score_route_points_for_event(
        event_brief(),
        [
            route_point(
                "unlinked",
                is_indoor=False,
                rainy_day_score=1,
                crowd_risk="high",
                linked_merchants=["m999"],
            )
        ],
        ["m930"],
    )[0]

    assert "no selected merchant linkage" in result.warnings
    assert "high crowd risk" in result.warnings


def test_demo_seed_replaces_stale_route_catalog_before_assembly():
    STORE.save_route_point(
        route_point(
            "rp-v32-stale-global",
            name="Stale Global Route Point",
            type="test",
            linked_merchants=["m001"],
            story="Should not survive demo seeding.",
        )
    )

    seed_demo(STORE)

    assert "rp-v32-stale-global" not in {point.point_id for point in STORE.list_route_points()}


def event_payload() -> dict:
    return {"title": "V32 Rainy Route", **event_brief(EVENT_ID).model_dump()}


def merchant(merchant_id: str) -> MerchantProfile:
    return MerchantProfile(
        merchant_id=merchant_id,
        name=f"Merchant {merchant_id}",
        type="tea",
        location=Location(lat=22.19, lng=113.53, label="Inner Harbor"),
        opening_hours="10:00-22:00",
        capacity_level="medium",
        signature_products=["tea tasting"],
        story="Covered local tea stop.",
        suitable_activity_types=["family", "rainy-day"],
        rainy_day_score=5,
        night_score=5,
        constraints=[],
        contact_name="Ada",
        contact_phone="+853-6000-9000",
        address_label="Inner Harbor Shop",
        area="Inner Harbor",
        operating_windows=[
            MerchantOperatingWindow(label="daily", start_time="10:00", end_time="22:00")
        ],
        capacity_notes="Two groups per hour.",
        category_tags=["tea", "family", "rainy-day"],
        participation_constraints=[],
        status="active",
    )


def create_ready_merchant(client: TestClient, merchant_id: str) -> None:
    response = client.post(
        "/api/merchants",
        json=merchant(merchant_id).model_dump(),
        headers=MUTATION_HEADERS,
    )
    assert response.status_code == 200, response.text


def ready_roster(client: TestClient, merchant_ids: list[str]) -> None:
    replaced = client.put(
        f"/api/events/{EVENT_ID}/merchant-roster",
        json={"merchant_ids": merchant_ids},
        headers=MUTATION_HEADERS,
    )
    assert replaced.status_code == 200, replaced.text
    for merchant_id in merchant_ids:
        submit_merchant_setup(
            STORE,
            merchant_id,
            EVENT_ID,
            MerchantSetupSubmitRequest(
                capacity_commitment="medium",
                staffing_ready=True,
                stock_ready=True,
                indoor_backup_ready=True,
                operating_window_confirmed=True,
                merchant_contact_name=f"Contact {merchant_id}",
                merchant_contact_phone="+853-6000-0101",
                merchant_notes="Prepared for route assembly test.",
            ),
        )
        ready = client.patch(
            f"/api/events/{EVENT_ID}/merchant-roster/{merchant_id}",
            json={"participation_status": "confirmed", "readiness_status": "ready"},
            headers=MUTATION_HEADERS,
        )
        assert ready.status_code == 200, ready.text


def save_route_points() -> None:
    STORE.save_route_point(
        route_point(
            "rp-v32-weak-first",
            name="Outdoor Unlinked Plaza",
            type="street",
            is_indoor=False,
            rainy_day_score=1,
            crowd_risk="high",
            linked_merchants=[],
            story="Open unlinked plaza.",
            visitor_task="Wait outside.",
        )
    )
    STORE.save_route_point(route_point("rp-v32-m930", linked_merchants=["m930"]))
    STORE.save_route_point(
        route_point(
            "rp-v32-m931",
            name="Covered Story Shop",
            type="culture",
            linked_merchants=["m931"],
            visitor_task="Complete the covered story card.",
        )
    )


def test_generate_plan_assembles_route_by_fit_and_records_evidence():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    created = client.post("/api/events", json=event_payload(), headers=MUTATION_HEADERS)
    assert created.status_code == 200, created.text
    create_ready_merchant(client, "m930")
    create_ready_merchant(client, "m931")
    ready_roster(client, ["m930", "m931"])
    save_route_points()

    generated = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    plan = generated.json()["current_plan"]

    point_ids = [point["point_id"] for point in plan["route_points"]]
    assert "rp-v32-m930" in point_ids
    assert "rp-v32-m931" in point_ids
    assert point_ids.index("rp-v32-m930") < point_ids.index("rp-v32-m931")
    assert "rp-v32-weak-first" not in point_ids[:2]
    assert plan["route_fit"]
    assert plan["route_fit"][0]["point_id"] in {"rp-v32-m930", "rp-v32-m931"}
    assert all(
        set(point["linked_merchants"]) <= set(plan["merchant_assignments"])
        for point in plan["route_points"]
    )
    route_steps = [
        step for step in generated.json()["agent_trace"]["steps"] if step["step_id"] == "step_route"
    ]
    assert route_steps
    assert "route_fit" in route_steps[0]["structured_output"]
    assert "route_warnings" in route_steps[0]["structured_output"]


def test_generate_plan_warns_when_selected_merchant_has_no_route_linkage():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    created = client.post("/api/events", json=event_payload(), headers=MUTATION_HEADERS)
    assert created.status_code == 200, created.text
    create_ready_merchant(client, "m930")
    create_ready_merchant(client, "m999")
    ready_roster(client, ["m930", "m999"])
    STORE.save_route_point(route_point("rp-v32-m930", linked_merchants=["m930"]))

    generated = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    route_warnings = generated.json()["current_plan"]["route_warnings"]
    assert any("m999" in warning for warning in route_warnings)
