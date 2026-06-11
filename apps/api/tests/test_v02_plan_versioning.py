from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_generate_and_approve_plan_version_v1():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)

    response = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["current_plan"]["version"] == 1
    assert len(body["agent_trace"]["steps"]) >= 5

    plans = client.get("/api/events/demo-night-tour/plans")
    assert plans.status_code == 200
    assert plans.json()[0]["version"] == 1

    approved = client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    current = client.get("/api/events/demo-night-tour/plans/current")
    assert current.status_code == 200
    assert current.json()["version"] == 1
    assert current.json()["status"] == "approved"
