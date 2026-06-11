from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def prepare_active_event(client: TestClient):
    login_as(client, "organizer.demo")
    client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)


def report_sold_out(client: TestClient):
    login_as(client, "merchant.m001.demo")
    return client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "sold out during demo",
        },
        headers=MUTATION_HEADERS,
    )


def test_merchant_sold_out_creates_agent_recovery_drafts_without_approval():
    client = TestClient(app)
    prepare_active_event(client)

    state = report_sold_out(client)

    assert state.status_code == 200
    assert state.json()["incident"]["type"] == "inventory"
    assert state.json()["agent_run"]["trigger"] == "incident_recovery"
    assert state.json()["agent_run"]["status"] == "completed"

    login_as(client, "organizer.demo")
    drafts = client.get("/api/events/demo-night-tour/agent-drafts")
    assert drafts.status_code == 200
    draft_types = {draft["draft_type"] for draft in drafts.json()}
    assert {"recovery_explanation", "public_notice"}.issubset(draft_types)

    public_notice_drafts = [draft for draft in drafts.json() if draft["draft_type"] == "public_notice"]
    assert public_notice_drafts
    forbidden = ["PlanVersion", "RecoveryProposal", "Incident", "Qwen", "runtime state"]
    for term in forbidden:
        assert term not in public_notice_drafts[0]["content"]

    current_plan = client.get("/api/events/demo-night-tour/plans/current")
    assert current_plan.status_code == 200
    assert current_plan.json()["version"] == 1

    public_event = client.get("/api/public/events/demo-night-tour")
    assert public_event.status_code == 200
    assert public_event.json()["current_plan_version"] == 1


def test_recovery_proposal_still_requires_organizer_approval_for_v2():
    client = TestClient(app)
    prepare_active_event(client)
    report_sold_out(client)

    login_as(client, "organizer.demo")
    incident = client.get("/api/events/demo-night-tour/incidents").json()[0]

    before_approval = client.get("/api/public/events/demo-night-tour")
    assert before_approval.json()["current_plan_version"] == 1

    proposal = client.post(
        f"/api/events/demo-night-tour/incidents/{incident['incident_id']}/recovery-proposals",
        headers=MUTATION_HEADERS,
    )
    assert proposal.status_code == 200
    assert proposal.json()["approval_status"] == "pending"

    still_before_approval = client.get("/api/public/events/demo-night-tour")
    assert still_before_approval.json()["current_plan_version"] == 1

    approved = client.post(
        f"/api/events/demo-night-tour/recovery-proposals/{proposal.json()['proposal_id']}/approve",
        headers=MUTATION_HEADERS,
    )
    assert approved.status_code == 200
    assert approved.json()["current_plan"]["version"] == 2
    assert approved.json()["notice"]["publish_status"] == "published"

    public_after = client.get("/api/public/events/demo-night-tour")
    assert public_after.json()["current_plan_version"] == 2
