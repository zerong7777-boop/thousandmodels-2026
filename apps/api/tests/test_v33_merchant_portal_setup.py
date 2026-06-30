import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "v33-merchant-setup"
EVENT_IDS = (
    EVENT_ID,
    f"{EVENT_ID}-other",
    f"{EVENT_ID}-unassigned",
)


def event_payload(event_id: str = EVENT_ID) -> dict:
    return {
        "event_id": event_id,
        "title": "V33 Merchant Setup",
        "area": "Inner Harbor",
        "date": "2026-09-20",
        "time_window": "16:00-21:00",
        "budget_mop": 88000,
        "target_audience": ["families", "weekend visitors"],
        "event_goal": "Rainy evening route with selected merchants and covered stops.",
        "theme_preferences": ["local food", "rainy-day"],
        "constraints": ["covered backup"],
        "priority_rules": ["confirm merchant setup before planning"],
    }


def setup_event_with_roster(
    client: TestClient, event_id: str = EVENT_ID, merchant_ids: list[str] | None = None
) -> None:
    selected = merchant_ids or ["m001"]
    created = client.post("/api/events", json=event_payload(event_id), headers=MUTATION_HEADERS)
    assert created.status_code == 200, created.text
    roster = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": selected},
        headers=MUTATION_HEADERS,
    )
    assert roster.status_code == 200, roster.text


def merchant_setup_payload(**overrides) -> dict:
    payload = {
        "capacity_commitment": "medium",
        "staffing_ready": True,
        "stock_ready": True,
        "indoor_backup_ready": True,
        "operating_window_confirmed": True,
        "merchant_contact_name": "Ada Chan",
        "merchant_contact_phone": "+853-6000-0101",
        "merchant_notes": "Two staff confirmed and covered queue area ready.",
    }
    payload.update(overrides)
    return payload


@pytest.fixture(autouse=True)
def clear_v33_events():
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)
    yield
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)


def test_merchant_lists_assigned_event_setup_context():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    setup_event_with_roster(client)

    login_as(client, "merchant.m001.demo")
    response = client.get("/api/merchants/me/events")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload[0]["event"]["event_id"] == EVENT_ID
    assert payload[0]["participant"]["merchant_id"] == "m001"
    assert "merchant setup not submitted" in payload[0]["setup_gaps"]
    assert payload[0]["ready_for_planning"] is False


def test_merchant_can_submit_setup_but_not_mark_organizer_ready():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    setup_event_with_roster(client)

    login_as(client, "merchant.m001.demo")
    submitted = client.patch(
        f"/api/merchants/me/events/{EVENT_ID}/setup",
        json=merchant_setup_payload(),
        headers=MUTATION_HEADERS,
    )

    assert submitted.status_code == 200, submitted.text
    participant = submitted.json()["participant"]
    assert participant["setup_status"] == "submitted"
    assert participant["readiness_status"] == "needs_setup"
    assert participant["submitted_by"] == "m001"
    assert participant["merchant_contact_name"] == "Ada Chan"
    assert submitted.json()["setup_gaps"] == []

    login_as(client, "organizer.demo")
    summary = client.get(f"/api/events/{EVENT_ID}/merchant-roster")
    assert summary.status_code == 200, summary.text
    summary_payload = summary.json()
    assert summary_payload["participants"][0]["setup_status"] == "submitted"
    assert summary_payload["participants"][0]["readiness_status"] == "needs_setup"
    assert summary_payload["ready_for_planning"] is False


def test_merchant_cannot_submit_setup_for_unassigned_event():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    setup_event_with_roster(client, f"{EVENT_ID}-unassigned", ["m002"])

    login_as(client, "merchant.m001.demo")
    response = client.patch(
        f"/api/merchants/me/events/{EVENT_ID}-unassigned/setup",
        json=merchant_setup_payload(),
        headers=MUTATION_HEADERS,
    )

    assert response.status_code == 404, response.text


def test_non_demo_planning_requires_setup_and_organizer_ready():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    setup_event_with_roster(client)

    blocked = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert blocked.status_code == 400, blocked.text

    login_as(client, "merchant.m001.demo")
    submitted = client.patch(
        f"/api/merchants/me/events/{EVENT_ID}/setup",
        json=merchant_setup_payload(),
        headers=MUTATION_HEADERS,
    )
    assert submitted.status_code == 200, submitted.text

    login_as(client, "organizer.demo")
    still_blocked = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert still_blocked.status_code == 400, still_blocked.text

    ready = client.patch(
        f"/api/events/{EVENT_ID}/merchant-roster/m001",
        json={"participation_status": "confirmed", "readiness_status": "ready"},
        headers=MUTATION_HEADERS,
    )
    assert ready.status_code == 200, ready.text

    generated = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text


def test_rainy_event_keeps_setup_gap_until_indoor_backup_confirmed():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    setup_event_with_roster(client)

    login_as(client, "merchant.m001.demo")
    submitted = client.patch(
        f"/api/merchants/me/events/{EVENT_ID}/setup",
        json=merchant_setup_payload(indoor_backup_ready=False),
        headers=MUTATION_HEADERS,
    )

    assert submitted.status_code == 200, submitted.text
    assert "indoor backup readiness not confirmed" in submitted.json()["setup_gaps"]


def test_demo_event_can_still_generate_plan_without_manual_merchant_setup():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    seeded = client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    assert seeded.status_code == 200, seeded.text

    generated = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    assert generated.json()["current_plan"]["merchant_assignments"]
