from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import Incident, MerchantSetupSubmitRequest
from app.services.merchant_setup import submit_merchant_setup
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "v34-command-center"
EVENT_IDS = (
    EVENT_ID,
    f"{EVENT_ID}-ready",
    f"{EVENT_ID}-incident",
)


def event_payload(event_id: str = EVENT_ID) -> dict:
    return {
        "event_id": event_id,
        "title": "V34 Command Center",
        "area": "Inner Harbor",
        "date": "2026-10-01",
        "time_window": "16:00-21:00",
        "budget_mop": 92000,
        "target_audience": ["families", "weekend visitors"],
        "event_goal": "Coordinate selected merchants for a live route.",
        "theme_preferences": ["local food", "heritage walk"],
        "constraints": ["keep indoor backup"],
        "priority_rules": ["confirm launch readiness before public release"],
    }


def create_event(client: TestClient, event_id: str = EVENT_ID) -> None:
    response = client.post("/api/events", json=event_payload(event_id), headers=MUTATION_HEADERS)
    assert response.status_code == 200, response.text


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
            merchant_notes="Prepared for command center test.",
        ),
    )


def make_ready_event(client: TestClient, event_id: str) -> None:
    create_event(client, event_id)
    roster = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": ["m001", "m002"]},
        headers=MUTATION_HEADERS,
    )
    assert roster.status_code == 200, roster.text
    for merchant_id in ["m001", "m002"]:
        submit_complete_setup(event_id, merchant_id)
        ready = client.patch(
            f"/api/events/{event_id}/merchant-roster/{merchant_id}",
            json={"participation_status": "confirmed", "readiness_status": "ready"},
            headers=MUTATION_HEADERS,
        )
        assert ready.status_code == 200, ready.text
    generated = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    version = generated.json()["current_plan"]["version"]
    approved = client.post(
        f"/api/events/{event_id}/plans/{version}/approve",
        headers=MUTATION_HEADERS,
    )
    assert approved.status_code == 200, approved.text
    drafted = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert drafted.status_code == 200, drafted.text
    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text
    packages = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert packages.status_code == 200, packages.text


@pytest.fixture(autouse=True)
def clear_v34_events():
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)
    yield
    for event_id in EVENT_IDS:
        STORE.clear_demo(event_id)


def test_operations_summary_blocks_incomplete_event_launch():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client)

    response = client.get(f"/api/events/{EVENT_ID}/operations-summary")

    assert response.status_code == 200, response.text
    payload = response.json()
    checks = {check["check_id"]: check for check in payload["checks"]}
    assert payload["overall_status"] == "blocked"
    assert payload["blocker_count"] >= 2
    assert checks["merchant_setup"]["status"] == "blocked"
    assert checks["plan_approval"]["status"] == "blocked"
    assert any(item["target"] == "Merchant setup" for item in payload["action_items"])


def test_operations_summary_reports_ready_launch_chain_and_timeline():
    event_id = f"{EVENT_ID}-ready"
    client = TestClient(app)
    login_as(client, "organizer.demo")
    make_ready_event(client, event_id)

    response = client.get(f"/api/events/{event_id}/operations-summary")

    assert response.status_code == 200, response.text
    payload = response.json()
    checks = {check["check_id"]: check for check in payload["checks"]}
    assert payload["overall_status"] == "ready"
    assert payload["blocker_count"] == 0
    assert checks["merchant_setup"]["status"] == "ready"
    assert checks["plan_approval"]["status"] == "ready"
    assert checks["event_page"]["status"] == "ready"
    assert checks["merchant_packages"]["status"] == "ready"
    assert payload["package_summary"]["active_package_count"] == len(
        payload["package_summary"]["required_merchant_ids"]
    )
    assert payload["timeline"]
    assert payload["timeline"][0]["timestamp"] >= payload["timeline"][-1]["timestamp"]
    assert any(item["action_type"] == "publish_event_page" for item in payload["timeline"])


def test_high_severity_active_incident_blocks_operations_readiness():
    event_id = f"{EVENT_ID}-incident"
    client = TestClient(app)
    login_as(client, "organizer.demo")
    make_ready_event(client, event_id)
    STORE.save_incident(
        Incident(
            incident_id=f"incident-{event_id}",
            event_id=event_id,
            type="merchant_unavailable",
            severity="high",
            source="organizer",
            trigger_detail="Merchant is temporarily unavailable.",
            affected_route_points=[],
            affected_merchants=["m001"],
            status="open",
            created_at=datetime.now(UTC).isoformat(),
        )
    )

    response = client.get(f"/api/events/{event_id}/operations-summary")

    assert response.status_code == 200, response.text
    payload = response.json()
    checks = {check["check_id"]: check for check in payload["checks"]}
    assert payload["overall_status"] == "blocked"
    assert checks["incident_queue"]["status"] == "blocked"
    assert payload["incident_summary"]["active_high_count"] == 1
    assert any(item["target"] == "Incident queue" for item in payload["action_items"])


def test_operations_summary_rejects_missing_event():
    client = TestClient(app)
    login_as(client, "organizer.demo")

    response = client.get("/api/events/missing-v34/operations-summary")

    assert response.status_code == 404, response.text


def test_demo_event_can_fetch_operations_summary():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    seeded = client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    assert seeded.status_code == 200, seeded.text

    response = client.get("/api/events/demo-night-tour/operations-summary")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["event"]["event_id"] == "demo-night-tour"
    assert payload["overall_status"] in {"ready", "warning", "blocked"}
