from fastapi.testclient import TestClient

from app.main import app
from app.seed import DEMO_AUTH_USERS
from app.store import STORE
from scripts.reset_demo_state import reset_demo_state
from tests.conftest import login_as


EVENT_ID = "demo-night-tour"
MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def test_reset_demo_state_seeds_event_summary_and_demo_accounts():
    if hasattr(STORE, "clear_auth_for_tests"):
        STORE.clear_auth_for_tests()
    STORE.clear_demo(EVENT_ID)

    result = reset_demo_state()

    assert result["status"] == "reset"
    assert result["event_id"] == EVENT_ID
    assert result["demo_accounts"] == [
        account["username"] for account in DEMO_AUTH_USERS
    ]

    summary = STORE.get_event_summary(EVENT_ID)
    assert summary is not None
    assert summary.event_id == EVENT_ID
    assert summary.current_plan_version == 0

    for username in result["demo_accounts"]:
        user = STORE.get_user_by_username(username)
        assert user is not None
        assert user.status == "active"


def test_reset_demo_state_clears_event_runtime_records_created_by_api(monkeypatch):
    monkeypatch.setenv("AGENT_BACKEND", "deterministic")
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("AGENT_DRAFT_BACKEND", raising=False)

    reset_demo_state()
    client = TestClient(app)

    login_as(client, "organizer.demo")
    generated = client.post(
        f"/api/events/{EVENT_ID}/generate-plan",
        headers=MUTATION_HEADERS,
    )
    assert generated.status_code == 200, generated.text
    approved = client.post(
        f"/api/events/{EVENT_ID}/plans/1/approve",
        headers=MUTATION_HEADERS,
    )
    assert approved.status_code == 200, approved.text
    packages = client.post(
        f"/api/events/{EVENT_ID}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert packages.status_code == 200, packages.text
    first_package = packages.json()["packages"][0]
    touchpoint_id = first_package["touchpoints"][0]["id"]
    coupon_rule_id = first_package["coupon_rules"][0]["id"]

    client.post("/api/auth/logout", headers=MUTATION_HEADERS)
    scan = client.post(
        f"/api/public/events/{EVENT_ID}/touchpoints/{touchpoint_id}/interactions",
        json={"interaction_type": "scan", "source": "qr", "metadata": {}},
        headers=MUTATION_HEADERS,
    )
    assert scan.status_code == 200, scan.text
    claim = client.post(
        f"/api/public/events/{EVENT_ID}/coupons/{coupon_rule_id}/claim",
        json={"anonymous_interaction_id": scan.json()["anonymous_interaction_id"]},
        headers=MUTATION_HEADERS,
    )
    assert claim.status_code == 200, claim.text
    redeemed = client.post(
        f"/api/public/events/{EVENT_ID}/coupon-redemptions/{claim.json()['id']}/redeem",
        headers=MUTATION_HEADERS,
    )
    assert redeemed.status_code == 200, redeemed.text

    login_as(client, "merchant.m001.demo")
    incident = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "normal",
            "available_for_visitors": False,
            "temporary_note": "reset script regression fixture",
        },
        headers=MUTATION_HEADERS,
    )
    assert incident.status_code == 200, incident.text

    assert STORE.list_plan_versions(EVENT_ID)
    assert STORE.list_incidents(EVENT_ID)
    assert STORE.list_merchant_interaction_packages(EVENT_ID)
    assert STORE.list_touchpoint_interactions(EVENT_ID)
    assert STORE.list_coupon_redemptions(EVENT_ID)

    reset_demo_state()

    assert STORE.get_event_summary(EVENT_ID) is not None
    assert STORE.list_plan_versions(EVENT_ID) == []
    assert STORE.list_incidents(EVENT_ID) == []
    assert STORE.list_merchant_interaction_packages(EVENT_ID) == []
    assert STORE.list_touchpoint_interactions(EVENT_ID) == []
    assert STORE.list_coupon_redemptions(EVENT_ID) == []
