from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_review_report_cites_operational_metrics():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)

    report = client.post("/api/events/demo-night-tour/review-report", headers=MUTATION_HEADERS)
    assert report.status_code == 200
    body = report.json()
    joined = "\n".join(body["lessons_learned"] + body["next_event_recommendations"])
    assert "h5_visits" in joined or "访问" in joined
    assert "incident_response_minutes" in joined or "异常" in joined
