import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import EventCreateRequest, MerchantRuntimeState, PlanVersion
from app.seed import seed_local_catalog
from app.services.events import create_event
from app.services.planning import generate_merchant_tasks
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
REAL_EVENT_ID = "real-harbor-fair"
REAL_EVENT_IDS = (
    REAL_EVENT_ID,
    f"{REAL_EVENT_ID}-duplicate",
    f"{REAL_EVENT_ID}-approval",
    f"{REAL_EVENT_ID}-interactions",
    f"{REAL_EVENT_ID}-pre-publication-guard",
    f"{REAL_EVENT_ID}-required-fields",
    f"{REAL_EVENT_ID}-stale-package",
)


@pytest.fixture(autouse=True)
def clear_real_events():
    for event_id in REAL_EVENT_IDS:
        STORE.clear_demo(event_id)
    yield
    for event_id in REAL_EVENT_IDS:
        STORE.clear_demo(event_id)


def real_event_payload(event_id: str = REAL_EVENT_ID) -> dict:
    return {
        "event_id": event_id,
        "title": "Harbor Community Fair",
        "area": "Inner Harbor",
        "date": "2026-08-15",
        "time_window": "17:00-21:00",
        "budget_mop": 52000,
        "target_audience": ["families", "weekend visitors"],
        "event_goal": "Create a merchant-led evening route for local visitors.",
        "theme_preferences": ["local food", "street stories"],
        "constraints": ["avoid heavy traffic streets", "keep rainy-day fallback"],
        "priority_rules": ["prefer indoor stops during rain", "balance merchant load"],
    }


def _reset_real_event(event_id: str) -> None:
    STORE.clear_demo(event_id)


def _create_real_event(client: TestClient, event_id: str = REAL_EVENT_ID) -> dict:
    response = client.post(
        "/api/events",
        json=real_event_payload(event_id),
        headers=MUTATION_HEADERS,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _ready_real_event_roster(client: TestClient, event_id: str) -> None:
    setup = client.put(
        f"/api/events/{event_id}/merchant-roster",
        json={"merchant_ids": ["m001", "m002"]},
        headers=MUTATION_HEADERS,
    )
    assert setup.status_code == 200, setup.text
    for merchant_id in ["m001", "m002"]:
        ready = client.patch(
            f"/api/events/{event_id}/merchant-roster/{merchant_id}",
            json={"participation_status": "confirmed", "readiness_status": "ready"},
            headers=MUTATION_HEADERS,
        )
        assert ready.status_code == 200, ready.text


def _publish_real_event(client: TestClient, event_id: str) -> None:
    _create_real_event(client, event_id)
    _ready_real_event_roster(client, event_id)

    generated = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text

    approved = client.post(f"/api/events/{event_id}/plans/1/approve", headers=MUTATION_HEADERS)
    assert approved.status_code == 200, approved.text

    draft = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft.status_code == 200, draft.text

    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text


def _metric_counter(client: TestClient, name: str) -> int:
    response = client.get("/api/metrics")
    assert response.status_code == 200, response.text
    return response.json()["counters"].get(name, 0)


def _advance_real_event_to_approved_v2(event_id: str) -> None:
    plan_v1 = STORE.get_plan_version(event_id, 1)
    assert plan_v1 is not None
    plan_v2_payload = plan_v1.model_dump()
    plan_v2_payload.update(
        {
            "plan_id": f"{event_id}:v2",
            "version": 2,
            "status": "approved",
            "created_reason": "stale_package_guard_regression",
            "approved_by": "usr_org_demo",
            "approved_at": "2026-06-15T11:30:00Z",
        }
    )
    plan_v2 = PlanVersion.model_validate(plan_v2_payload)
    STORE.save_plan_version(plan_v2)
    STORE.save_merchant_tasks(event_id, generate_merchant_tasks(plan_v2, STORE.list_merchants()))
    event = STORE.get_event_summary(event_id)
    assert event is not None
    event.current_plan_version = 2
    STORE.save_event_summary(event)


def test_seed_local_catalog_preserves_existing_runtime_state():
    seed_local_catalog(STORE)
    existing = STORE.get_runtime_state("m001")
    assert existing is not None
    STORE.save_runtime_state(
        MerchantRuntimeState(
            merchant_id="m001",
            inventory_status="sold_out",
            queue_status="busy",
            available_for_visitors=False,
            temporary_note="manual operator hold",
            updated_at=existing.updated_at,
        )
    )

    seed_local_catalog(STORE)

    preserved = STORE.get_runtime_state("m001")
    assert preserved is not None
    assert preserved.inventory_status == "sold_out"
    assert preserved.queue_status == "busy"
    assert preserved.available_for_visitors is False
    assert preserved.temporary_note == "manual operator hold"


def test_create_event_rejects_explicit_id_that_slugifies_empty():
    payload = EventCreateRequest.model_validate(real_event_payload(event_id="活动"))

    try:
        with pytest.raises(ValueError, match="event_id is invalid"):
            create_event(STORE, payload)
    finally:
        STORE.clear_demo("event")


def test_update_event_rejects_invalid_path_event_id():
    client = TestClient(app)
    login_as(client, "organizer.demo")

    updated = client.patch(
        "/api/events/活动",
        json={"title": "Invalid"},
        headers=MUTATION_HEADERS,
    )

    assert updated.status_code == 400, updated.text


def test_create_and_update_real_event_without_demo_seed():
    _reset_real_event(REAL_EVENT_ID)
    client = TestClient(app)
    login_as(client, "organizer.demo")

    created = client.post(
        "/api/events",
        json=real_event_payload(),
        headers=MUTATION_HEADERS,
    )
    assert created.status_code == 200, created.text
    created_payload = created.json()
    assert created_payload["event_id"] == REAL_EVENT_ID
    assert created_payload["status"] == "draft"
    assert created_payload["current_plan_version"] == 0
    assert created_payload["public_release_status"] == "draft"

    assert STORE.get_event_summary("demo-night-tour") is None
    stored_brief = STORE.get_event_brief(REAL_EVENT_ID)
    assert stored_brief is not None
    assert stored_brief.event_goal.startswith("Create a merchant-led")

    updated = client.patch(
        f"/api/events/{REAL_EVENT_ID}",
        json={"title": "Harbor Community Fair Updated", "budget_mop": 61000},
        headers=MUTATION_HEADERS,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Harbor Community Fair Updated"
    stored_brief = STORE.get_event_brief(REAL_EVENT_ID)
    assert stored_brief is not None
    assert stored_brief.budget_mop == 61000
    assert STORE.get_event_summary("demo-night-tour") is None


def test_create_event_requires_constraints_and_priority_rules():
    event_id = f"{REAL_EVENT_ID}-required-fields"
    _reset_real_event(event_id)
    client = TestClient(app)
    login_as(client, "organizer.demo")

    missing_constraints = real_event_payload(event_id)
    missing_constraints.pop("constraints")
    constraints_response = client.post(
        "/api/events",
        json=missing_constraints,
        headers=MUTATION_HEADERS,
    )
    assert constraints_response.status_code == 422, constraints_response.text

    missing_priority_rules = real_event_payload(event_id)
    missing_priority_rules.pop("priority_rules")
    priority_response = client.post(
        "/api/events",
        json=missing_priority_rules,
        headers=MUTATION_HEADERS,
    )
    assert priority_response.status_code == 422, priority_response.text


def test_real_event_duplicate_and_missing_plan_do_not_seed_demo():
    event_id = f"{REAL_EVENT_ID}-duplicate"
    _reset_real_event(event_id)
    client = TestClient(app)
    login_as(client, "organizer.demo")

    first = client.post(
        "/api/events",
        json=real_event_payload(event_id),
        headers=MUTATION_HEADERS,
    )
    assert first.status_code == 200, first.text

    duplicate = client.post(
        "/api/events",
        json=real_event_payload(event_id),
        headers=MUTATION_HEADERS,
    )
    assert duplicate.status_code == 409, duplicate.text

    missing = client.post(
        "/api/events/missing-real-event/generate-plan",
        headers=MUTATION_HEADERS,
    )
    assert missing.status_code == 404, missing.text
    assert STORE.get_event_summary("demo-night-tour") is None


def test_real_event_plan_approval_does_not_publish_until_event_page_publish():
    event_id = f"{REAL_EVENT_ID}-approval"
    _reset_real_event(event_id)
    client = TestClient(app)
    login_as(client, "organizer.demo")
    _create_real_event(client, event_id)
    _ready_real_event_roster(client, event_id)

    generated = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    event = STORE.get_event_summary(event_id)
    assert event is not None
    assert event.status == "pending_approval"
    assert event.public_release_status == "draft"

    approved = client.post(f"/api/events/{event_id}/plans/1/approve", headers=MUTATION_HEADERS)
    assert approved.status_code == 200, approved.text
    event = STORE.get_event_summary(event_id)
    assert event is not None
    assert event.status == "active"
    assert event.current_plan_version == 1
    assert event.public_release_status == "draft"

    public_before_publish = client.get(f"/api/public/events/{event_id}")
    assert public_before_publish.status_code == 404, public_before_publish.text

    drafted = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert drafted.status_code == 200, drafted.text

    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text
    event = STORE.get_event_summary(event_id)
    assert event is not None
    assert event.public_release_status == "published"

    public_after_publish = client.get(f"/api/public/events/{event_id}")
    assert public_after_publish.status_code == 200, public_after_publish.text
    assert public_after_publish.json()["event_id"] == event_id


def test_real_event_public_interactions_are_idempotent_and_reported():
    event_id = f"{REAL_EVENT_ID}-interactions"
    _reset_real_event(event_id)
    client = TestClient(app)
    login_as(client, "organizer.demo")
    _publish_real_event(client, event_id)

    generated_packages = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated_packages.status_code == 200, generated_packages.text
    package = generated_packages.json()["packages"][0]
    touchpoint_id = package["touchpoints"][0]["id"]
    coupon_rule_id = package["coupon_rules"][0]["id"]
    anonymous_id = "anon-real-v27"

    client.post("/api/auth/logout", headers=MUTATION_HEADERS)
    scan_payload = {
        "interaction_type": "scan",
        "source": "qr",
        "anonymous_interaction_id": anonymous_id,
    }
    scan_metric_before = _metric_counter(client, "public_touchpoint_interactions_total")
    first_scan = client.post(
        f"/api/public/events/{event_id}/touchpoints/{touchpoint_id}/interactions",
        json=scan_payload,
        headers=MUTATION_HEADERS,
    )
    assert first_scan.status_code == 200, first_scan.text
    second_scan = client.post(
        f"/api/public/events/{event_id}/touchpoints/{touchpoint_id}/interactions",
        json=scan_payload,
        headers=MUTATION_HEADERS,
    )
    assert second_scan.status_code == 200, second_scan.text
    assert second_scan.json()["id"] == first_scan.json()["id"]
    assert _metric_counter(client, "public_touchpoint_interactions_total") == scan_metric_before + 1

    claim_payload = {"anonymous_interaction_id": anonymous_id}
    claim_metric_before = _metric_counter(client, "public_coupon_claims_total")
    first_claim = client.post(
        f"/api/public/events/{event_id}/coupons/{coupon_rule_id}/claim",
        json=claim_payload,
        headers=MUTATION_HEADERS,
    )
    assert first_claim.status_code == 200, first_claim.text
    second_claim = client.post(
        f"/api/public/events/{event_id}/coupons/{coupon_rule_id}/claim",
        json=claim_payload,
        headers=MUTATION_HEADERS,
    )
    assert second_claim.status_code == 200, second_claim.text
    assert second_claim.json()["id"] == first_claim.json()["id"]
    assert _metric_counter(client, "public_coupon_claims_total") == claim_metric_before + 1

    redeem_metric_before = _metric_counter(client, "public_coupon_redemptions_total")
    first_redeem = client.post(
        f"/api/public/events/{event_id}/coupon-redemptions/{first_claim.json()['id']}/redeem",
        headers=MUTATION_HEADERS,
    )
    assert first_redeem.status_code == 200, first_redeem.text
    second_redeem = client.post(
        f"/api/public/events/{event_id}/coupon-redemptions/{first_claim.json()['id']}/redeem",
        headers=MUTATION_HEADERS,
    )
    assert second_redeem.status_code == 200, second_redeem.text
    assert second_redeem.json()["id"] == first_redeem.json()["id"]
    assert second_redeem.json()["status"] == "redeemed"
    assert _metric_counter(client, "public_coupon_redemptions_total") == redeem_metric_before + 1

    login_as(client, "organizer.demo")
    report = client.post(f"/api/events/{event_id}/review-report", headers=MUTATION_HEADERS)
    assert report.status_code == 200, report.text
    touchpoint_summary = report.json()["touchpoint_summary"]
    assert touchpoint_summary["total_interactions"] == 3
    assert touchpoint_summary["by_type"]["scan"] == 1
    assert touchpoint_summary["by_type"]["claim"] == 1
    assert touchpoint_summary["by_type"]["redeem"] == 1
    assert touchpoint_summary["coupon_claims"] == 1
    assert touchpoint_summary["coupon_redemptions"] == 1


def test_real_event_public_mutations_require_published_event_page():
    event_id = f"{REAL_EVENT_ID}-pre-publication-guard"
    _reset_real_event(event_id)
    client = TestClient(app)
    login_as(client, "organizer.demo")
    _create_real_event(client, event_id)
    _ready_real_event_roster(client, event_id)

    generated = client.post(f"/api/events/{event_id}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text

    approved = client.post(f"/api/events/{event_id}/plans/1/approve", headers=MUTATION_HEADERS)
    assert approved.status_code == 200, approved.text

    generated_packages = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated_packages.status_code == 200, generated_packages.text
    package = generated_packages.json()["packages"][0]
    touchpoint_id = package["touchpoints"][0]["id"]
    coupon_rule_id = package["coupon_rules"][0]["id"]

    client.post("/api/auth/logout", headers=MUTATION_HEADERS)
    scan = client.post(
        f"/api/public/events/{event_id}/touchpoints/{touchpoint_id}/interactions",
        json={
            "interaction_type": "scan",
            "source": "qr",
            "anonymous_interaction_id": "anon-real-v27-pre-publication",
        },
        headers=MUTATION_HEADERS,
    )
    assert scan.status_code == 404, scan.text

    claim = client.post(
        f"/api/public/events/{event_id}/coupons/{coupon_rule_id}/claim",
        json={"anonymous_interaction_id": "anon-real-v27-pre-publication"},
        headers=MUTATION_HEADERS,
    )
    assert claim.status_code == 404, claim.text


def test_real_event_public_mutations_reject_stale_package_children_after_current_package_changes():
    event_id = f"{REAL_EVENT_ID}-stale-package"
    _reset_real_event(event_id)
    client = TestClient(app)
    login_as(client, "organizer.demo")
    _publish_real_event(client, event_id)

    generated_v1 = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated_v1.status_code == 200, generated_v1.text
    old_package = generated_v1.json()["packages"][0]
    old_touchpoint_id = old_package["touchpoints"][0]["id"]
    old_coupon_rule_id = old_package["coupon_rules"][0]["id"]

    _advance_real_event_to_approved_v2(event_id)
    draft_v2 = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft_v2.status_code == 200, draft_v2.text
    published_v2 = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published_v2.status_code == 200, published_v2.text
    generated_v2 = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated_v2.status_code == 200, generated_v2.text
    current_package = next(
        package
        for package in generated_v2.json()["packages"]
        if package["merchant_id"] == old_package["merchant_id"]
    )
    assert current_package["id"] != old_package["id"]

    client.post("/api/auth/logout", headers=MUTATION_HEADERS)
    stale_scan = client.post(
        f"/api/public/events/{event_id}/touchpoints/{old_touchpoint_id}/interactions",
        json={
            "interaction_type": "scan",
            "source": "qr",
            "anonymous_interaction_id": "anon-real-v27-stale-package",
        },
        headers=MUTATION_HEADERS,
    )
    assert stale_scan.status_code == 400, stale_scan.text

    stale_claim = client.post(
        f"/api/public/events/{event_id}/coupons/{old_coupon_rule_id}/claim",
        json={"anonymous_interaction_id": "anon-real-v27-stale-package"},
        headers=MUTATION_HEADERS,
    )
    assert stale_claim.status_code == 400, stale_claim.text
