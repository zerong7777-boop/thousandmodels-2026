from fastapi.testclient import TestClient

from app.main import app
from app.store import STORE
from scripts.reset_demo_state import reset_demo_state


EVENT_ID = "demo-night-tour"
MERCHANT_ID = "m001"
MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
ENDPOINT = f"/api/events/{EVENT_ID}/qwenpaw-shadow-orchestration/run"


def login_as(client: TestClient, username: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "demo1234"},
        headers=MUTATION_HEADERS,
    )
    assert response.status_code == 200, response.text


def prepare_sold_out_incident() -> str:
    reset_demo_state(event_id=EVENT_ID)
    with TestClient(app) as client:
        login_as(client, "organizer.demo")
        assert client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS).status_code == 200
        assert client.post(f"/api/events/{EVENT_ID}/plans/1/approve", headers=MUTATION_HEADERS).status_code == 200
        assert client.post(f"/api/events/{EVENT_ID}/event-page/draft", headers=MUTATION_HEADERS).status_code == 200
        assert client.post(f"/api/events/{EVENT_ID}/event-page/publish", headers=MUTATION_HEADERS).status_code == 200
        assert (
            client.post(
                f"/api/events/{EVENT_ID}/merchant-edge-packages/generate",
                headers=MUTATION_HEADERS,
            ).status_code
            == 200
        )
        login_as(client, f"merchant.{MERCHANT_ID}.demo")
        response = client.post(
            f"/api/merchants/{MERCHANT_ID}/runtime-state",
            json={
                "inventory_status": "sold_out",
                "queue_status": "normal",
                "available_for_visitors": False,
                "temporary_note": "Sold out during v1.4 API test.",
            },
            headers=MUTATION_HEADERS,
        )
        assert response.status_code == 200, response.text
    incidents = STORE.list_incidents(EVENT_ID)
    assert incidents
    return incidents[-1].incident_id


def test_merchant_cannot_run_qwenpaw_shadow_orchestration():
    reset_demo_state(event_id=EVENT_ID)
    with TestClient(app) as client:
        login_as(client, f"merchant.{MERCHANT_ID}.demo")

        response = client.post(
            ENDPOINT,
            json={},
            headers=MUTATION_HEADERS,
        )

    assert response.status_code == 403, response.text


def test_organizer_without_mutation_origin_cannot_run_qwenpaw_shadow_orchestration():
    reset_demo_state(event_id=EVENT_ID)
    with TestClient(app) as client:
        login_as(client, "organizer.demo")

        response = client.post(ENDPOINT, json={})

    assert response.status_code == 403, response.text


def test_organizer_without_origin_but_with_demo_csrf_cannot_run_qwenpaw_shadow_orchestration():
    reset_demo_state(event_id=EVENT_ID)
    with TestClient(app) as client:
        login_as(client, "organizer.demo")

        response = client.post(
            ENDPOINT,
            json={},
            headers={"x-zhiyin-csrf": "demo"},
        )

    assert response.status_code == 403, response.text


def test_organizer_run_returns_advisory_bundle_and_persists_shadow_evidence():
    incident_id = prepare_sold_out_incident()
    with TestClient(app) as client:
        login_as(client, "organizer.demo")

        response = client.post(
            ENDPOINT,
            json={"incident_id": incident_id},
            headers=MUTATION_HEADERS,
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    agent_run = payload["agent_run"]
    run_id = agent_run["run_id"]
    advisory_bundle = payload["advisory_bundle"]
    permission_decisions = payload["permission_decisions"]

    assert agent_run["mode"] == "qwenpaw_workflow"
    assert advisory_bundle["authoritative_mutation"] is False
    assert advisory_bundle["human_approval_required"] is True
    assert payload["steps"]
    assert permission_decisions
    assert any(decision["allowed"] is False for decision in permission_decisions)

    stored_runs = STORE.list_agent_runs(EVENT_ID)
    assert any(run.run_id == run_id for run in stored_runs)
    stored_tool_calls = STORE.list_agent_tool_calls(run_id)
    assert any(
        call.output_payload["permission_decision"]["allowed"] is False
        for call in stored_tool_calls
    )
    traces = STORE.list_agent_traces(EVENT_ID)
    trace = next(trace for trace in traces if trace.trace_id == f"trace_{run_id}")
    assert [step.agent_name for step in trace.steps[:2]] == [
        "CentralOpsLeader",
        "MerchantEdgeWorker",
    ]
