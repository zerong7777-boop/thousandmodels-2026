from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_complete_demo_loop():
    client = TestClient(app)
    login_as(client, "organizer.demo")

    seed = client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    assert seed.status_code == 200
    assert seed.json()["event_id"] == "demo-night-tour"

    plan = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    assert plan.status_code == 200
    assert plan.json()["approval_status"] == "draft"

    approved_plan = client.post("/api/events/demo-night-tour/approve-plan", headers=MUTATION_HEADERS)
    assert approved_plan.status_code == 200
    assert approved_plan.json()["approval_status"] == "approved"

    packs = client.get("/api/events/demo-night-tour/merchant-packs")
    assert packs.status_code == 200
    assert len(packs.json()) >= 2

    public_before = client.get("/api/public/events/demo-night-tour")
    assert public_before.status_code == 200
    assert public_before.json()["notices"] == []

    inventory = client.post(
        "/api/events/demo-night-tour/trigger/inventory",
        json={"merchant_id": "m001"},
        headers=MUTATION_HEADERS,
    )
    assert inventory.status_code == 200
    action_id = inventory.json()["action_id"]
    assert inventory.json()["approval_status"] == "pending"

    approved_recovery = client.post(
        f"/api/recovery-actions/{action_id}/approve",
        headers=MUTATION_HEADERS,
    )
    assert approved_recovery.status_code == 200
    assert approved_recovery.json()["approval_status"] == "approved"

    weather = client.post("/api/events/demo-night-tour/trigger/weather", headers=MUTATION_HEADERS)
    assert weather.status_code == 200

    public_after = client.get("/api/public/events/demo-night-tour")
    assert public_after.status_code == 200
    assert public_after.json()["notices"]

    report = client.post("/api/events/demo-night-tour/review-report", headers=MUTATION_HEADERS)
    assert report.status_code == 200
    assert report.json()["lessons_learned"]
