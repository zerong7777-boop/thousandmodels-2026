import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import MerchantSetupSubmitRequest
from app.services.merchant_setup import submit_merchant_setup
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "v29-harbor-fair"
EVENT_IDS = (
    EVENT_ID,
    f"{EVENT_ID}-unknown-merchant",
    f"{EVENT_ID}-planning-guard",
    f"{EVENT_ID}-planning-scope",
)


def event_payload(event_id: str = EVENT_ID) -> dict:
    return {
        "event_id": event_id,
        "title": "V29 Harbor Fair",
        "area": "Inner Harbor",
        "date": "2026-09-05",
        "time_window": "16:00-21:00",
        "budget_mop": 68000,
        "target_audience": ["families", "weekend visitors"],
        "event_goal": "Coordinate selected merchants for a public evening route.",
        "theme_preferences": ["local food", "street stories"],
        "constraints": ["avoid narrow traffic streets", "keep indoor backup"],
        "priority_rules": ["balance merchant load", "prefer ready merchants"],
    }


def create_event(client: TestClient, event_id: str = EVENT_ID) -> None:
    response = client.post("/api/events", json=event_payload(event_id), headers=MUTATION_HEADERS)
    assert response.status_code == 200, response.text


def ready_roster(client: TestClient, event_id: str, merchant_ids: list[str]) -> dict:
    replaced = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": merchant_ids},
        headers=MUTATION_HEADERS,
    )
    assert replaced.status_code == 200, replaced.text
    for merchant_id in merchant_ids:
        submit_complete_setup(event_id, merchant_id)
        patched = client.patch(
            f"/api/events/{event_id}/merchant-roster/{merchant_id}",
            json={"participation_status": "confirmed", "readiness_status": "ready"},
            headers=MUTATION_HEADERS,
        )
        assert patched.status_code == 200, patched.text
    return patched.json()


def submit_complete_setup(event_id: str, merchant_id: str) -> None:
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
            merchant_notes="Prepared for event test.",
        ),
    )


@pytest.fixture(autouse=True)
def clear_v29_events():
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)
    yield
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)


def test_event_merchant_roster_can_be_replaced_and_marked_ready():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client)

    empty = client.get(f"/api/events/{EVENT_ID}/merchant-roster")
    assert empty.status_code == 200, empty.text
    assert empty.json()["total_count"] == 0
    assert empty.json()["ready_for_planning"] is False

    replaced = client.put(
        f"/api/events/{EVENT_ID}/merchant-roster",
        json={"merchant_ids": ["m001", "m002", "m001"]},
        headers=MUTATION_HEADERS,
    )
    assert replaced.status_code == 200, replaced.text
    payload = replaced.json()
    assert payload["total_count"] == 2
    assert [item["merchant_id"] for item in payload["participants"]] == ["m001", "m002"]
    assert payload["needs_setup_count"] == 2
    assert payload["ready_for_planning"] is False
    submit_complete_setup(EVENT_ID, "m001")
    submit_complete_setup(EVENT_ID, "m002")

    ready = client.patch(
        f"/api/events/{EVENT_ID}/merchant-roster/m001",
        json={
            "participation_status": "confirmed",
            "readiness_status": "ready",
            "role_hint": "snack stop",
            "notes": "Has staff for evening crowd",
        },
        headers=MUTATION_HEADERS,
    )
    assert ready.status_code == 200, ready.text
    assert ready.json()["ready_count"] == 1
    assert ready.json()["ready_for_planning"] is False

    second_ready = client.patch(
        f"/api/events/{EVENT_ID}/merchant-roster/m002",
        json={"participation_status": "confirmed", "readiness_status": "ready"},
        headers=MUTATION_HEADERS,
    )
    assert second_ready.status_code == 200, second_ready.text
    assert second_ready.json()["ready_count"] == 2
    assert second_ready.json()["ready_for_planning"] is True


def test_event_merchant_roster_rejects_unknown_event_and_merchant():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client, f"{EVENT_ID}-unknown-merchant")

    missing_event = client.get("/api/events/missing-event/merchant-roster")
    assert missing_event.status_code == 404, missing_event.text

    unknown_merchant = client.put(
        f"/api/events/{EVENT_ID}-unknown-merchant/merchant-roster",
        json={"merchant_ids": ["missing-merchant"]},
        headers=MUTATION_HEADERS,
    )
    assert unknown_merchant.status_code == 404, unknown_merchant.text


def test_merchant_catalog_endpoint_initializes_local_catalog_without_demo_event():
    client = TestClient(app)
    login_as(client, "organizer.demo")

    response = client.get("/api/merchants")
    assert response.status_code == 200, response.text
    assert {merchant["merchant_id"] for merchant in response.json()} >= {"m001", "m002"}
    assert STORE.get_event_summary("demo-night-tour") is None


def test_non_demo_plan_generation_requires_ready_event_merchant_roster():
    event_id = f"{EVENT_ID}-planning-guard"
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client, event_id)

    blocked_empty = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert blocked_empty.status_code == 400, blocked_empty.text
    assert "event merchant setup required" in blocked_empty.text

    setup = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": ["m001"]},
        headers=MUTATION_HEADERS,
    )
    assert setup.status_code == 200, setup.text

    blocked_not_ready = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert blocked_not_ready.status_code == 400, blocked_not_ready.text
    assert "event merchant setup required" in blocked_not_ready.text


def test_non_demo_plan_generation_uses_only_ready_event_merchants():
    event_id = f"{EVENT_ID}-planning-scope"
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client, event_id)
    ready_roster(client, event_id, ["m001", "m002"])

    generated = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    plan = generated.json()["current_plan"]
    assert set(plan["merchant_assignments"]) <= {"m001", "m002"}
    assert set(plan["merchant_assignments"])
    for route_point in plan["route_points"]:
        assert set(route_point["linked_merchants"]) <= {"m001", "m002"}

    tasks = client.get(f"/api/events/{event_id}/merchant-tasks")
    assert tasks.status_code == 200, tasks.text
    assert {task["merchant_id"] for task in tasks.json()} <= {"m001", "m002"}


def test_demo_event_can_still_generate_plan_without_manual_roster():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    seeded = client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    assert seeded.status_code == 200, seeded.text

    generated = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    assert generated.json()["current_plan"]["merchant_assignments"]
