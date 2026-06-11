from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_review_report_creates_metric_backed_agent_draft():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)

    login_as(client, "merchant.m001.demo")
    client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "sold out during demo",
        },
        headers=MUTATION_HEADERS,
    )

    login_as(client, "organizer.demo")
    incident = client.get("/api/events/demo-night-tour/incidents").json()[0]
    proposal = client.post(
        f"/api/events/demo-night-tour/incidents/{incident['incident_id']}/recovery-proposals",
        headers=MUTATION_HEADERS,
    ).json()
    client.post(
        f"/api/events/demo-night-tour/recovery-proposals/{proposal['proposal_id']}/approve",
        headers=MUTATION_HEADERS,
    )

    report = client.post("/api/events/demo-night-tour/review-report", headers=MUTATION_HEADERS)

    assert report.status_code == 200
    assert report.json()["lessons_learned"]
    assert report.json()["agent_run"]["trigger"] == "review_generation"

    drafts = client.get("/api/events/demo-night-tour/agent-drafts?draft_type=review_summary")
    assert drafts.status_code == 200
    assert drafts.json()
    payload = drafts.json()[0]["structured_payload"]
    assert "h5_visits" in payload["metrics"]
    assert incident["incident_id"] in payload["incident_ids"]
    assert proposal["proposal_id"] in payload["proposal_ids"]
    assert payload["notice_ids"]
