from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_merchant_inventory_update_creates_incident_and_v2_after_approval():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)

    login_as(client, "merchant.m001.demo")
    state = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "杏仁饼售罄",
        },
        headers=MUTATION_HEADERS,
    )
    assert state.status_code == 200

    login_as(client, "organizer.demo")
    incidents = client.get("/api/events/demo-night-tour/incidents")
    assert incidents.status_code == 200
    incident = incidents.json()[0]
    assert incident["type"] == "inventory"
    assert incident["status"] in {"open", "proposal_ready"}

    proposal = client.post(
        f"/api/events/demo-night-tour/incidents/{incident['incident_id']}/recovery-proposals",
        headers=MUTATION_HEADERS,
    )
    assert proposal.status_code == 200
    assert proposal.json()["approval_status"] == "pending"

    approved = client.post(
        f"/api/events/demo-night-tour/recovery-proposals/{proposal.json()['proposal_id']}/approve",
        headers=MUTATION_HEADERS,
    )
    assert approved.status_code == 200
    assert approved.json()["current_plan"]["version"] == 2
    assert approved.json()["current_plan"]["diff_from_previous"]
    assert approved.json()["notice"]["publish_status"] == "published"

    public_event = client.get("/api/public/events/demo-night-tour")
    assert public_event.status_code == 200
    assert public_event.json()["current_plan_version"] == 2
    assert public_event.json()["notices"]
