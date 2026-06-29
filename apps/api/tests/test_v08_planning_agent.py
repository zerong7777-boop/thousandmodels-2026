from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_generate_plan_persists_agent_run_steps_and_tool_calls(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.setenv("AGENT_BACKEND", "deterministic")

    client = TestClient(app)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)

    response = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_run"]["trigger"] == "planning_generation"
    assert payload["agent_run"]["mode"] == "deterministic"
    assert payload["agent_run"]["fallback_used"] is False
    assert len(payload["agent_trace"]["steps"]) >= 6

    runs = client.get("/api/events/demo-night-tour/agent-runs")
    assert runs.status_code == 200
    assert runs.json()[0]["trigger"] == "planning_generation"

    run_id = runs.json()[0]["run_id"]
    tool_calls = client.get(f"/api/events/demo-night-tour/agent-runs/{run_id}/tool-calls")
    assert tool_calls.status_code == 200
    tool_names = {call["tool_name"] for call in tool_calls.json()}
    assert "route.assemble_route_points" in tool_names
    assert "merchant.score_event_fit" in tool_names
    assert "budget.split_budget" in tool_names
