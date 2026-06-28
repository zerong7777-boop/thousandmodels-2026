import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed_local_catalog
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "v30-merchant-network"


def merchant_payload(merchant_id: str = "m900") -> dict:
    return {
        "merchant_id": merchant_id,
        "name": "Harbor Tea Lab",
        "type": "tea",
        "location": {"lat": 22.192, "lng": 113.538, "label": "Inner Harbor"},
        "opening_hours": "10:00-22:00",
        "capacity_level": "medium",
        "signature_products": ["Cold brew tea"],
        "story": "A local tea stop for night routes.",
        "suitable_activity_types": ["rest stop", "coupon"],
        "rainy_day_score": 4,
        "night_score": 5,
        "constraints": ["needs crowd notice"],
        "contact_name": "Ada Wong",
        "contact_phone": "+853-6000-9000",
        "address_label": "Inner Harbor Shop 9",
        "area": "Inner Harbor",
        "operating_windows": [{"label": "daily", "start_time": "10:00", "end_time": "22:00"}],
        "capacity_notes": "Can handle two guided groups per hour.",
        "category_tags": ["tea", "rainy-day"],
        "participation_constraints": ["needs 24h notice"],
        "status": "active",
    }


def event_payload(event_id: str = EVENT_ID, time_window: str = "16:00-21:00") -> dict:
    return {
        "event_id": event_id,
        "title": "V30 Harbor Night",
        "area": "Inner Harbor",
        "date": "2026-09-09",
        "time_window": time_window,
        "budget_mop": 70000,
        "target_audience": ["families"],
        "event_goal": "Use merchant network data for roster readiness.",
        "theme_preferences": ["local food"],
        "constraints": ["avoid narrow streets"],
        "priority_rules": ["prefer eligible merchants"],
    }


def create_event(client: TestClient, event_id: str = EVENT_ID, time_window: str = "16:00-21:00") -> None:
    response = client.post("/api/events", json=event_payload(event_id, time_window), headers=MUTATION_HEADERS)
    assert response.status_code == 200, response.text


@pytest.fixture(autouse=True)
def clear_v30_state():
    STORE.clear_demo(EVENT_ID)
    STORE.clear_demo(f"{EVENT_ID}-closed")
    STORE.clear_demo(f"{EVENT_ID}-history")
    yield
    STORE.clear_demo(EVENT_ID)
    STORE.clear_demo(f"{EVENT_ID}-closed")
    STORE.clear_demo(f"{EVENT_ID}-history")


def test_organizer_can_create_read_and_update_network_merchant():
    client = TestClient(app)
    login_as(client, "organizer.demo")

    created = client.post("/api/merchants", json=merchant_payload(), headers=MUTATION_HEADERS)
    assert created.status_code == 200, created.text
    detail = created.json()
    assert detail["merchant"]["merchant_id"] == "m900"
    assert detail["merchant"]["contact_name"] == "Ada Wong"
    assert detail["merchant"]["operating_windows"][0]["start_time"] == "10:00"
    assert detail["participation_history"] == []

    duplicate = client.post("/api/merchants", json=merchant_payload(), headers=MUTATION_HEADERS)
    assert duplicate.status_code == 409, duplicate.text

    patched = client.patch(
        "/api/merchants/m900",
        json={
            "contact_name": "Ben Lei",
            "capacity_notes": "One guided group per 30 minutes.",
            "category_tags": ["tea", "family"],
        },
        headers=MUTATION_HEADERS,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["merchant"]["contact_name"] == "Ben Lei"
    assert patched.json()["merchant"]["category_tags"] == ["tea", "family"]

    fetched = client.get("/api/merchants/m900")
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["merchant"]["capacity_notes"] == "One guided group per 30 minutes."
    assert STORE.get_runtime_state("m900") is not None


def test_merchant_network_rejects_invalid_payload_and_unknown_update():
    client = TestClient(app)
    login_as(client, "organizer.demo")

    invalid = merchant_payload("m901")
    invalid["operating_windows"] = [{"label": "bad", "start_time": "22:00", "end_time": "10:00"}]
    response = client.post("/api/merchants", json=invalid, headers=MUTATION_HEADERS)
    assert response.status_code == 422, response.text

    missing = client.patch("/api/merchants/missing", json={"contact_name": "No One"}, headers=MUTATION_HEADERS)
    assert missing.status_code == 404, missing.text


def test_merchant_user_cannot_manage_merchant_network():
    client = TestClient(app)
    login_as(client, "merchant.m001.demo")

    response = client.post("/api/merchants", json=merchant_payload("m902"), headers=MUTATION_HEADERS)
    assert response.status_code == 403, response.text


def test_merchant_detail_includes_participation_history_from_event_roster():
    event_id = f"{EVENT_ID}-history"
    client = TestClient(app)
    login_as(client, "organizer.demo")
    seed_local_catalog(STORE)
    create_event(client, event_id)

    roster = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": ["m001"]},
        headers=MUTATION_HEADERS,
    )
    assert roster.status_code == 200, roster.text

    ready = client.patch(
        f"/api/events/{event_id}/merchant-roster/m001",
        json={"participation_status": "confirmed", "readiness_status": "ready"},
        headers=MUTATION_HEADERS,
    )
    assert ready.status_code == 200, ready.text

    detail = client.get("/api/merchants/m001")
    assert detail.status_code == 200, detail.text
    history = detail.json()["participation_history"]
    assert history
    assert history[0]["event_id"] == event_id
    assert history[0]["participation_status"] == "confirmed"
    assert history[0]["readiness_status"] == "ready"


def test_roster_summary_reports_merchant_eligibility():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client)
    created = client.post("/api/merchants", json=merchant_payload(), headers=MUTATION_HEADERS)
    assert created.status_code == 200, created.text

    roster = client.put(
        f"/api/events/{EVENT_ID}/merchant-roster",
        json={"merchant_ids": ["m900"]},
        headers=MUTATION_HEADERS,
    )
    assert roster.status_code == 200, roster.text
    eligibility = roster.json()["eligibility"]["m900"]
    assert eligibility["status"] in {"eligible", "needs_review"}
    assert isinstance(eligibility["reasons"], list)


def test_ineligible_merchant_cannot_be_marked_ready():
    event_id = f"{EVENT_ID}-closed"
    client = TestClient(app)
    login_as(client, "organizer.demo")
    create_event(client, event_id, time_window="18:00-21:00")
    payload = merchant_payload("m903")
    payload["operating_windows"] = [{"label": "morning", "start_time": "08:00", "end_time": "12:00"}]
    created = client.post("/api/merchants", json=payload, headers=MUTATION_HEADERS)
    assert created.status_code == 200, created.text
    roster = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": ["m903"]},
        headers=MUTATION_HEADERS,
    )
    assert roster.status_code == 200, roster.text
    assert roster.json()["eligibility"]["m903"]["status"] == "ineligible"

    ready = client.patch(
        f"/api/events/{event_id}/merchant-roster/m903",
        json={"participation_status": "confirmed", "readiness_status": "ready"},
        headers=MUTATION_HEADERS,
    )
    assert ready.status_code == 400, ready.text
    assert "merchant is not eligible" in ready.text
