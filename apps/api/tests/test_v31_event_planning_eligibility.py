import pytest
from app.main import app
from app.schemas import (
    EventBrief,
    Location,
    MerchantOperatingWindow,
    MerchantProfile,
    MerchantSetupSubmitRequest,
)
from app.services.merchant_fit import score_merchants_for_event
from app.services.merchant_setup import submit_merchant_setup
from app.store import STORE
from fastapi.testclient import TestClient
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "v31-event-planning-eligibility"
EVENT_IDS = (EVENT_ID,)


@pytest.fixture(autouse=True)
def clear_v31_events():
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)
    yield
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)


def event_brief(event_id: str = "v31-fit") -> EventBrief:
    return EventBrief(
        event_id=event_id,
        area="Inner Harbor",
        date="2026-10-10",
        time_window="18:00-21:00",
        budget_mop=120000,
        target_audience=["family"],
        event_goal="Rainy night food walk with covered rest stops.",
        theme_preferences=["tea", "rainy-day"],
        constraints=["covered stop"],
        priority_rules=["prefer family-friendly rest stops"],
    )


def event_payload(event_id: str = EVENT_ID) -> dict:
    return {
        "title": "Family Rainy Food Night",
        **event_brief(event_id).model_dump(),
    }


def merchant(merchant_id: str, **overrides) -> MerchantProfile:
    data = {
        "merchant_id": merchant_id,
        "name": "Harbor Tea Lab",
        "type": "tea",
        "location": Location(lat=22.19, lng=113.53, label="Inner Harbor"),
        "opening_hours": "10:00-22:00",
        "capacity_level": "medium",
        "signature_products": ["tea tasting"],
        "story": "A covered local tea stop for family rainy-day night routes.",
        "suitable_activity_types": ["family", "rainy-day", "rest stop"],
        "rainy_day_score": 5,
        "night_score": 5,
        "constraints": [],
        "contact_name": "Ada",
        "contact_phone": "+853-6000-9000",
        "address_label": "Inner Harbor Shop 9",
        "area": "Inner Harbor",
        "operating_windows": [
            MerchantOperatingWindow(label="daily", start_time="10:00", end_time="22:00")
        ],
        "capacity_notes": "Can handle two guided family groups per hour.",
        "category_tags": ["tea", "family", "rainy-day"],
        "participation_constraints": [],
        "status": "active",
    }
    data.update(overrides)
    return MerchantProfile(**data)


def merchant_payload(merchant_id: str, **overrides) -> dict:
    return merchant(merchant_id, **overrides).model_dump()


def create_event(client: TestClient, event_id: str = EVENT_ID) -> None:
    response = client.post("/api/events", json=event_payload(event_id), headers=MUTATION_HEADERS)
    assert response.status_code == 200, response.text


def create_merchant(client: TestClient, merchant_id: str, **overrides) -> None:
    response = client.post(
        "/api/merchants",
        json=merchant_payload(merchant_id, **overrides),
        headers=MUTATION_HEADERS,
    )
    assert response.status_code == 200, response.text


def ready_roster(client: TestClient, event_id: str, merchant_ids: list[str]) -> None:
    replaced = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": merchant_ids},
        headers=MUTATION_HEADERS,
    )
    assert replaced.status_code == 200, replaced.text
    for merchant_id in merchant_ids:
        submit_merchant_setup(
            STORE,
            merchant_id,
            event_id,
            MerchantSetupSubmitRequest(
                capacity_commitment="medium",
                staffing_ready=True,
                stock_ready=True,
                indoor_backup_ready=True,
                operating_window_confirmed=True,
                merchant_contact_name=f"Contact {merchant_id}",
                merchant_contact_phone="+853-6000-0101",
                merchant_notes="Prepared for planning fit test.",
            ),
        )
        ready = client.patch(
            f"/api/events/{event_id}/merchant-roster/{merchant_id}",
            json={"participation_status": "confirmed", "readiness_status": "ready"},
            headers=MUTATION_HEADERS,
        )
        assert ready.status_code == 200, ready.text


def test_scoring_orders_strong_fit_before_weak_fit():
    results = score_merchants_for_event(
        event_brief(),
        [
            merchant(
                "weak",
                name="Snack Kiosk",
                type="snack",
                category_tags=[],
                suitable_activity_types=[],
                rainy_day_score=1,
                night_score=1,
                contact_name="",
                area="",
                capacity_level="low",
                signature_products=[],
                story="Small takeaway counter.",
                participation_constraints=["needs manual staffing check"],
            ),
            merchant("strong"),
        ],
    )

    assert [item.merchant_id for item in results] == ["strong", "weak"]
    assert results[0].fit_level == "strong"
    assert results[0].matched_signals
    assert results[1].fit_level == "weak"
    assert results[1].warnings


def test_scoring_excludes_ineligible_merchants():
    results = score_merchants_for_event(
        event_brief(),
        [merchant("closed", status="inactive"), merchant("open")],
    )

    assert [item.merchant_id for item in results] == ["open"]


def test_generate_plan_orders_merchants_by_fit_and_records_evidence():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client)
    create_merchant(
        client,
        "m931-weak",
        name="Snack Kiosk",
        type="snack",
        category_tags=[],
        suitable_activity_types=[],
        rainy_day_score=1,
        night_score=1,
        contact_name="",
        area="",
        capacity_level="low",
        signature_products=[],
        story="Small takeaway counter.",
        participation_constraints=["needs manual staffing check"],
    )
    create_merchant(client, "m930-strong")
    ready_roster(client, EVENT_ID, ["m931-weak", "m930-strong"])

    generated = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    payload = generated.json()
    current_plan = payload["current_plan"]

    assert current_plan["merchant_assignments"][0] == "m930-strong"
    assert current_plan["merchant_fit"][0]["merchant_id"] == "m930-strong"
    assert current_plan["merchant_fit"][0]["fit_level"] == "strong"
    assert "strong fit" in current_plan["merchant_fit"][0]["rationale"]
    assert any("m931-weak" in warning for warning in current_plan["planner_warnings"])

    merchant_steps = [
        step for step in payload["agent_trace"]["steps"] if step["step_id"] == "step_merchant"
    ]
    assert merchant_steps
    assert "merchant_fit" in merchant_steps[0]["structured_output"]
    assert merchant_steps[0]["structured_output"]["planner_warnings"] is not None
