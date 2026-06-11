from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_public_event_uses_route_points_and_notices():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)

    response = client.get("/api/public/events/demo-night-tour")
    assert response.status_code == 200
    body = response.json()
    assert body["event_id"] == "demo-night-tour"
    assert body["current_plan_version"] == 1
    assert body["route_points"]
    assert {"name", "story", "visitor_task", "linked_merchants"}.issubset(body["route_points"][0])
