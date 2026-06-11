from app.seed import seed_demo
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_public_projection_remains_public(client):
    seed_demo(STORE)
    login_as(client, "organizer.demo")
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)
    client.post("/api/auth/logout", headers=MUTATION_HEADERS)

    response = client.get("/api/public/events/demo-night-tour")
    assert response.status_code == 200


def test_organizer_api_requires_login(client):
    response = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    assert response.status_code == 401


def test_merchant_and_tourist_cannot_generate_or_approve_plan(client):
    login_as(client, "merchant.m001.demo")
    merchant = client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    assert merchant.status_code == 403

    client.post("/api/auth/logout", headers=MUTATION_HEADERS)
    login_as(client, "tourist.demo")
    tourist = client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)
    assert tourist.status_code == 403


def test_merchant_can_update_own_runtime_state_and_triggers_incident(client):
    seed_demo(STORE)
    login_as(client, "merchant.m001.demo")

    response = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
        },
        headers=MUTATION_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["incident"]["type"] == "inventory"


def test_merchant_cannot_access_another_merchant_workbench_or_runtime_state(client):
    seed_demo(STORE)
    login_as(client, "merchant.m001.demo")

    read_response = client.get("/api/merchants/m002/workbench?event_id=demo-night-tour")
    write_response = client.post(
        "/api/merchants/m002/runtime-state",
        json={"inventory_status": "low"},
        headers=MUTATION_HEADERS,
    )

    assert read_response.status_code == 403
    assert write_response.status_code == 403


def test_audit_actor_comes_from_authenticated_user(client):
    seed_demo(STORE)
    login_as(client, "organizer.demo")

    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS)
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS)

    logs = STORE.list_audit_logs("demo-night-tour")
    approval_logs = [log for log in logs if log.action_type == "approve_plan_version"]

    assert approval_logs
    assert approval_logs[-1].actor_type == "organizer"
    assert approval_logs[-1].actor_id == "usr_org_demo"
