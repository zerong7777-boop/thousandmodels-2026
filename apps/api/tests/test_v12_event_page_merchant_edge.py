import json

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import MerchantInteractionPackage, MerchantTask, PlanVersion, RoutePoint
from app.services.planning import generate_merchant_tasks
from app.store import STORE
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
EVENT_ID = "demo-night-tour"
FORBIDDEN_PUBLIC_TERMS = (
    "AgentDraft",
    "AgentRun",
    "PlanVersion",
    "RecoveryProposal",
    "qwen",
    "dashscope",
    "schema_failed",
    "approval_status",
)


def seed_and_approve_v1(client: TestClient) -> str:
    login_as(client, "organizer.demo")
    seed = client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    assert seed.status_code == 200, seed.text
    assert seed.json()["event_id"] == EVENT_ID

    generated = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text

    approved = client.post(f"/api/events/{EVENT_ID}/plans/1/approve", headers=MUTATION_HEADERS)
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"
    return EVENT_ID


def test_event_page_draft_publish_updates_public_projection(client: TestClient):
    event_id = seed_and_approve_v1(client)

    draft = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft.status_code == 200, draft.text
    draft_payload = draft.json()
    assert draft_payload["status"] == "draft"
    assert draft_payload["event_id"] == event_id
    assert draft_payload["title"]
    assert draft_payload["story_sections"]

    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "published"

    public = client.get(f"/api/public/events/{event_id}")
    assert public.status_code == 200, public.text
    public_payload = public.json()
    assert public_payload["current_plan_version"] >= 1
    assert public_payload["event_page"]["status"] == "published"
    assert public_payload["event_page"]["title"] == published.json()["title"]
    assert public_payload["event_page"]["story_sections"]


def test_merchant_edge_package_generation_is_exposed_only_to_that_merchant(client: TestClient):
    event_id = seed_and_approve_v1(client)

    generated = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated.status_code == 200, generated.text
    assert generated.json()["agent_run"]["trigger"] == "merchant_edge_package_generation"
    assert generated.json()["agent_trace"]["trigger"] == "merchant_edge_package_generation"
    packages = generated.json()["packages"]
    assert packages
    first = packages[0]
    merchant_id = first["merchant_id"]
    other_package_ids = {package["id"] for package in packages if package["merchant_id"] != merchant_id}

    assert len(first["touchpoints"]) >= 2
    assert first["coupon_rules"]

    login_as(client, f"merchant.{merchant_id}.demo")
    workbench = client.get(f"/api/merchants/{merchant_id}/workbench?event_id={event_id}")
    assert workbench.status_code == 200, workbench.text
    workbench_payload = workbench.json()
    assert workbench_payload["merchant"]["id"] == merchant_id
    assert workbench_payload["interaction_package"]["merchant_id"] == merchant_id
    assert len(workbench_payload["interaction_package"]["touchpoints"]) >= 2
    assert workbench_payload["interaction_package"]["coupon_rules"]
    workbench_text = json.dumps(workbench_payload, ensure_ascii=False)
    for package_id in other_package_ids:
        assert package_id not in workbench_text


def test_public_projection_exposes_safe_event_page_interaction_controls(client: TestClient):
    event_id = seed_and_approve_v1(client)
    draft = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft.status_code == 200, draft.text
    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text
    generated = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated.status_code == 200, generated.text
    package = generated.json()["packages"][0]

    public = client.get(f"/api/public/events/{event_id}")
    assert public.status_code == 200, public.text
    merchant_highlight = next(
        highlight
        for highlight in public.json()["event_page"]["merchant_highlights"]
        if highlight["id"] == package["merchant_id"]
    )

    assert merchant_highlight["touchpoints"]
    assert merchant_highlight["coupon_rules"]
    assert merchant_highlight["touchpoints"][0] == {
        "id": package["touchpoints"][0]["id"],
        "touchpoint_type": package["touchpoints"][0]["touchpoint_type"],
        "label": package["touchpoints"][0]["label"],
        "public_copy": package["touchpoints"][0]["public_copy"],
        "status": package["touchpoints"][0]["status"],
    }
    assert merchant_highlight["coupon_rules"][0] == {
        "id": package["coupon_rules"][0]["id"],
        "title": package["coupon_rules"][0]["title"],
        "description": package["coupon_rules"][0]["description"],
        "status": package["coupon_rules"][0]["status"],
    }
    public_text = json.dumps(public.json(), ensure_ascii=False)
    assert package["id"] not in public_text
    assert "operator_brief" not in public_text
    assert "evidence_refs" not in public_text
    assert "generated_from_run_id" not in public_text


def test_merchant_workbench_summarizes_only_current_package_children(client: TestClient):
    event_id = seed_and_approve_v1(client)
    generated_v1 = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated_v1.status_code == 200, generated_v1.text
    merchant_id = generated_v1.json()["packages"][0]["merchant_id"]
    old_package_id = generated_v1.json()["packages"][0]["id"]

    plan_v1 = STORE.get_plan_version(event_id, 1)
    assert plan_v1 is not None
    plan_v2_payload = plan_v1.model_dump()
    plan_v2_payload.update(
        {
            "plan_id": f"{event_id}:v2",
            "version": 2,
            "status": "approved",
            "created_reason": "merchant_edge_regeneration",
            "approved_by": "usr_org_demo",
            "approved_at": "2026-06-15T10:30:00Z",
        }
    )
    plan_v2 = PlanVersion.model_validate(plan_v2_payload)
    STORE.save_plan_version(plan_v2)
    STORE.save_merchant_tasks(event_id, generate_merchant_tasks(plan_v2, STORE.list_merchants()))
    event = STORE.get_event_summary(event_id)
    assert event is not None
    event.current_plan_version = 2
    STORE.save_event_summary(event)

    generated_v2 = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated_v2.status_code == 200, generated_v2.text
    current = next(
        package for package in generated_v2.json()["packages"] if package["merchant_id"] == merchant_id
    )
    assert current["id"] != old_package_id

    login_as(client, f"merchant.{merchant_id}.demo")
    workbench = client.get(f"/api/merchants/{merchant_id}/workbench?event_id={event_id}")
    assert workbench.status_code == 200, workbench.text
    payload = workbench.json()
    assert payload["interaction_package"]["id"] == current["id"]
    assert payload["touchpoint_summary"]["total"] == len(current["touchpoints"])
    assert payload["coupon_summary"]["total"] == len(current["coupon_rules"])
    assert payload["touchpoint_summary"]["current_package_interactions"] == 0
    assert payload["coupon_summary"]["current_package_claims"] == 0


def test_touchpoint_scan_coupon_claim_redeem_are_anonymous_and_reported(client: TestClient):
    event_id = seed_and_approve_v1(client)
    generated = client.post(
        f"/api/events/{event_id}/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    )
    assert generated.status_code == 200, generated.text
    package = generated.json()["packages"][0]
    touchpoint_id = package["touchpoints"][0]["id"]
    coupon_rule_id = package["coupon_rules"][0]["id"]

    client.post("/api/auth/logout", headers=MUTATION_HEADERS)
    scan = client.post(
        f"/api/public/events/{event_id}/touchpoints/{touchpoint_id}/interactions",
        json={
            "interaction_type": "scan",
            "source": "qr",
            "metadata": {
                "visitor_id": "should-not-persist",
                "visitor_profile": {"name": "private"},
                "phone": "853-0000-0000",
                "display_mode": "counter",
            },
        },
        headers=MUTATION_HEADERS,
    )
    assert scan.status_code == 200, scan.text
    scan_payload = scan.json()
    assert scan_payload["anonymous_interaction_id"]
    assert "visitor_id" not in scan_payload
    assert "visitor_profile" not in scan_payload
    assert "phone" not in json.dumps(scan_payload, ensure_ascii=False)
    assert scan_payload["metadata"] == {"display_mode": "counter"}

    claim = client.post(
        f"/api/public/events/{event_id}/coupons/{coupon_rule_id}/claim",
        json={"anonymous_interaction_id": scan_payload["anonymous_interaction_id"]},
        headers=MUTATION_HEADERS,
    )
    assert claim.status_code == 200, claim.text
    claim_payload = claim.json()
    assert claim_payload["status"] == "claimed"
    assert claim_payload["anonymous_interaction_id"] == scan_payload["anonymous_interaction_id"]
    assert "visitor_id" not in claim_payload

    redeemed = client.post(
        f"/api/public/events/{event_id}/coupon-redemptions/{claim_payload['id']}/redeem",
        headers=MUTATION_HEADERS,
    )
    assert redeemed.status_code == 200, redeemed.text
    assert redeemed.json()["status"] == "redeemed"
    assert "visitor_id" not in redeemed.json()

    login_as(client, "organizer.demo")
    report = client.post(f"/api/events/{event_id}/review-report", headers=MUTATION_HEADERS)
    assert report.status_code == 200, report.text
    report_payload = report.json()
    assert report_payload["touchpoint_summary"]["total_interactions"] >= 1
    assert report_payload["touchpoint_summary"]["by_type"]["scan"] >= 1
    assert report_payload["touchpoint_summary"]["by_merchant"][package["merchant_id"]]["scan"] >= 1
    assert report_payload["touchpoint_summary"]["redemption_rate"] > 0
    assert report_payload["touchpoint_summary"]["coupon_claims"] >= 1
    assert report_payload["touchpoint_summary"]["coupon_redemptions"] >= 1
    assert report_payload["merchant_outcomes"]
    assert report_payload["extension_tasks"]


def test_sold_out_runtime_update_generates_operation_suggestion(client: TestClient):
    event_id = seed_and_approve_v1(client)

    login_as(client, "merchant.m001.demo")
    update = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "sold out during v1.2 merchant edge test",
        },
        headers=MUTATION_HEADERS,
    )
    assert update.status_code == 200, update.text
    assert update.json()["incident"]["status"] in {"open", "proposal_ready"}

    login_as(client, "organizer.demo")
    suggestions = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert suggestions.status_code == 200, suggestions.text
    suggestions_payload = suggestions.json()
    assert suggestions_payload["suggestions"]
    m001_suggestion = next(
        suggestion
        for suggestion in suggestions_payload["suggestions"]
        if "m001" in suggestion["impacted_merchants"]
    )
    assert m001_suggestion["suggestion_type"] in {"merchant_capacity", "route_adjustment", "public_notice"}
    assert m001_suggestion["evidence_refs"]


def test_operation_suggestion_stale_runtime_clears_and_rejects_approval(client: TestClient):
    event_id = seed_and_approve_v1(client)

    login_as(client, "merchant.m001.demo")
    update = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "normal",
            "available_for_visitors": False,
            "temporary_note": "sold out before stale regression",
        },
        headers=MUTATION_HEADERS,
    )
    assert update.status_code == 200, update.text
    active_incident_id = update.json()["incident"]["incident_id"]

    login_as(client, "organizer.demo")
    first_generate = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert first_generate.status_code == 200, first_generate.text
    capacity = next(
        suggestion
        for suggestion in first_generate.json()["suggestions"]
        if suggestion["suggestion_type"] == "merchant_capacity"
        and "m001" in suggestion["impacted_merchants"]
    )
    old_suggestion_id = capacity["id"]
    assert f"incident:{active_incident_id}" in capacity["evidence_refs"]

    incident = STORE.get_incident(active_incident_id, event_id=event_id)
    assert incident is not None
    incident.status = "closed"
    STORE.save_incident(incident)
    still_sold_out = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert still_sold_out.status_code == 200, still_sold_out.text
    refreshed_capacity = next(
        suggestion
        for suggestion in still_sold_out.json()["suggestions"]
        if suggestion["id"] == old_suggestion_id
    )
    assert f"incident:{active_incident_id}" not in refreshed_capacity["evidence_refs"]

    login_as(client, "merchant.m001.demo")
    reset = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "normal",
            "queue_status": "normal",
            "available_for_visitors": True,
            "temporary_note": "recovered before stale regression approval",
        },
        headers=MUTATION_HEADERS,
    )
    assert reset.status_code == 200, reset.text

    login_as(client, "organizer.demo")
    second_generate = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert second_generate.status_code == 200, second_generate.text
    assert all(
        "m001" not in suggestion["impacted_merchants"]
        for suggestion in second_generate.json()["suggestions"]
    )
    listed = client.get(f"/api/events/{event_id}/operation-suggestions")
    assert listed.status_code == 200, listed.text
    assert all(
        "m001" not in suggestion["impacted_merchants"]
        for suggestion in listed.json()["suggestions"]
    )
    approval = client.post(
        f"/api/events/{event_id}/operation-suggestions/{old_suggestion_id}/approve",
        headers=MUTATION_HEADERS,
    )
    assert approval.status_code == 404


def test_operation_suggestion_queue_notice_refreshes_payload(client: TestClient):
    event_id = seed_and_approve_v1(client)

    login_as(client, "merchant.m001.demo")
    busy = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "normal",
            "queue_status": "busy",
            "available_for_visitors": True,
            "temporary_note": "busy queue before refresh regression",
        },
        headers=MUTATION_HEADERS,
    )
    assert busy.status_code == 200, busy.text

    login_as(client, "organizer.demo")
    first_generate = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert first_generate.status_code == 200, first_generate.text
    notice = next(
        suggestion
        for suggestion in first_generate.json()["suggestions"]
        if suggestion["suggestion_type"] == "public_notice"
        and "m001" in suggestion["impacted_merchants"]
    )
    assert "busy" in notice["rationale"]
    assert "busy" in notice["recommended_actions"][0]["message"]

    login_as(client, "merchant.m001.demo")
    overloaded = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "normal",
            "queue_status": "overloaded",
            "available_for_visitors": True,
            "temporary_note": "overloaded queue after refresh regression",
        },
        headers=MUTATION_HEADERS,
    )
    assert overloaded.status_code == 200, overloaded.text

    login_as(client, "organizer.demo")
    second_generate = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert second_generate.status_code == 200, second_generate.text
    refreshed_notice = next(
        suggestion
        for suggestion in second_generate.json()["suggestions"]
        if suggestion["id"] == notice["id"]
    )
    assert "overloaded" in refreshed_notice["rationale"]
    assert "overloaded" in refreshed_notice["recommended_actions"][0]["message"]


def test_operation_suggestions_require_approved_current_plan(client: TestClient):
    login_as(client, "organizer.demo")
    seed = client.post("/api/events/demo/seed", headers=MUTATION_HEADERS)
    assert seed.status_code == 200, seed.text
    generated = client.post(f"/api/events/{EVENT_ID}/generate-plan", headers=MUTATION_HEADERS)
    assert generated.status_code == 200, generated.text
    event = STORE.get_event_summary(EVENT_ID)
    assert event is not None
    event.current_plan_version = 1
    STORE.save_event_summary(event)

    suggestions = client.post(
        f"/api/events/{EVENT_ID}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert suggestions.status_code == 400
    assert suggestions.json()["detail"] == "current plan is not approved"


def test_operation_suggestions_use_current_plan_scope(client: TestClient):
    event_id = seed_and_approve_v1(client)
    current_plan = STORE.get_plan_version(event_id, 1)
    assert current_plan is not None
    assert "m007" not in current_plan.merchant_assignments
    STORE.save_route_point(
        RoutePoint(
            point_id="rp999",
            name="Unapproved global route point",
            type="test",
            is_indoor=True,
            estimated_stay_minutes=10,
            story="Should not be used by operation suggestion evidence.",
            linked_merchants=["m001"],
            visitor_task="Ignore this point",
            rainy_day_score=5,
            crowd_risk="low",
            current_status="active",
        )
    )
    state = STORE.get_runtime_state("m007")
    assert state is not None
    state.inventory_status = "sold_out"
    state.available_for_visitors = False
    STORE.save_runtime_state(state)
    STORE.save_merchant_tasks(
        event_id,
        [
            *STORE.list_merchant_tasks(event_id),
            MerchantTask(
                task_id="task_stale_m007_v0",
                event_id=event_id,
                merchant_id="m007",
                plan_version=0,
                role="stale backup",
                time_slot="stale",
                visitor_task="stale task outside current plan",
                preparation_items=[],
                promo_text="stale",
                fallback_instruction="stale",
                task_status="active",
            ),
        ],
    )
    STORE.save_merchant_interaction_package(
        MerchantInteractionPackage(
            id="pkg_stale_m007_v0",
            event_id=event_id,
            merchant_id="m007",
            plan_version=0,
            status="active",
            operator_brief="stale package outside current plan",
            visitor_pitch="stale",
            task_ids=["task_stale_m007_v0"],
            touchpoints=[],
            coupon_rules=[],
            evidence_refs=["stale:test"],
            created_at="2026-06-15T00:00:00+00:00",
            updated_at="2026-06-15T00:00:00+00:00",
        )
    )

    login_as(client, "merchant.m001.demo")
    update = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "normal",
            "available_for_visitors": False,
            "temporary_note": "sold out for plan scope regression",
        },
        headers=MUTATION_HEADERS,
    )
    assert update.status_code == 200, update.text
    closed_incident_ids = []
    for incident in STORE.list_incidents(event_id):
        incident.status = "closed"
        STORE.save_incident(incident)
        closed_incident_ids.append(incident.incident_id)

    login_as(client, "organizer.demo")
    suggestions = client.post(
        f"/api/events/{event_id}/operation-suggestions/generate",
        headers=MUTATION_HEADERS,
    )
    assert suggestions.status_code == 200, suggestions.text
    suggestions_payload = suggestions.json()["suggestions"]
    assert all("m007" not in item["impacted_merchants"] for item in suggestions_payload)
    m001_suggestion = next(
        item for item in suggestions_payload if "m001" in item["impacted_merchants"]
    )
    assert "rp999" not in m001_suggestion["impacted_route_points"]
    for incident_id in closed_incident_ids:
        assert f"incident:{incident_id}" not in m001_suggestion["evidence_refs"]


def test_public_projection_hides_internal_backend_terms(client: TestClient):
    event_id = seed_and_approve_v1(client)
    draft = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft.status_code == 200, draft.text
    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text

    public = client.get(f"/api/public/events/{event_id}")
    assert public.status_code == 200, public.text
    public_text = json.dumps(public.json(), ensure_ascii=False)
    for forbidden in FORBIDDEN_PUBLIC_TERMS:
        assert forbidden not in public_text


def test_public_projection_does_not_attach_stale_event_page_after_recovery(client: TestClient):
    event_id = seed_and_approve_v1(client)
    draft = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft.status_code == 200, draft.text
    published = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert published.status_code == 200, published.text
    assert published.json()["plan_version"] == 1

    login_as(client, "merchant.m001.demo")
    update = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "sold out after page publish",
        },
        headers=MUTATION_HEADERS,
    )
    assert update.status_code == 200, update.text

    login_as(client, "organizer.demo")
    incident = client.get(f"/api/events/{event_id}/incidents").json()[0]
    proposal = client.post(
        f"/api/events/{event_id}/incidents/{incident['incident_id']}/recovery-proposals",
        headers=MUTATION_HEADERS,
    )
    assert proposal.status_code == 200, proposal.text
    approved = client.post(
        f"/api/events/{event_id}/recovery-proposals/{proposal.json()['proposal_id']}/approve",
        headers=MUTATION_HEADERS,
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["current_plan"]["version"] == 2

    public = client.get(f"/api/public/events/{event_id}")
    assert public.status_code == 200, public.text
    assert public.json()["current_plan_version"] == 2
    assert "event_page" not in public.json()


def test_event_page_publish_requires_current_plan_approval(client: TestClient):
    event_id = seed_and_approve_v1(client)
    draft = client.post(f"/api/events/{event_id}/event-page/draft", headers=MUTATION_HEADERS)
    assert draft.status_code == 200, draft.text

    plan_v1 = STORE.get_plan_version(event_id, 1)
    assert plan_v1 is not None
    plan_v2_payload = plan_v1.model_dump()
    plan_v2_payload.update(
        {
            "plan_id": f"{event_id}:v2",
            "version": 2,
            "status": "draft",
            "created_reason": "draft_plan_for_publish_guard",
            "approved_by": None,
            "approved_at": None,
        }
    )
    STORE.save_plan_version(PlanVersion.model_validate(plan_v2_payload))
    event = STORE.get_event_summary(event_id)
    assert event is not None
    event.current_plan_version = 2
    STORE.save_event_summary(event)

    current = client.get(f"/api/events/{event_id}/plans/current")
    assert current.status_code == 200, current.text
    assert current.json()["version"] == 2
    assert current.json()["status"] == "draft"

    publish = client.post(f"/api/events/{event_id}/event-page/publish", headers=MUTATION_HEADERS)
    assert publish.status_code == 400
