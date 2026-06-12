import json

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import login_as


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


class FakeQwenProvider:
    def __init__(self, raw: str):
        self.raw = raw

    def complete_json(self, prompt_template_id: str, payload: dict) -> str:
        return self.raw


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


def test_qwen_missing_key_records_skipped_model_calls_and_keeps_v1(monkeypatch):
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    client = TestClient(app)
    prepare_active_event(client)

    response = report_sold_out(client)

    assert response.status_code == 200
    assert response.json()["agent_run"]["mode"] == "qwen_draft"
    assert response.json()["agent_run"]["status"] == "fallback_completed"
    assert response.json()["agent_run"]["fallback_used"] is True

    login_as(client, "organizer.demo")
    run_id = response.json()["agent_run"]["run_id"]
    model_calls = client.get(f"/api/events/demo-night-tour/agent-runs/{run_id}/model-calls")
    assert model_calls.status_code == 200
    assert {call["response_status"] for call in model_calls.json()} == {"skipped"}
    assert all(call["fallback_used"] is True for call in model_calls.json())

    public_event = client.get("/api/public/events/demo-night-tour")
    assert public_event.json()["current_plan_version"] == 1


def test_qwen_public_notice_forbidden_terms_fall_back(monkeypatch):
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    raw = json.dumps(
        {
            "content": "Qwen created a RecoveryProposal fallback for this backend route.",
            "locale": "en",
            "structured_payload": {"requires_organizer_approval": True},
            "evidence_refs": ["incident:inc_inventory_m001"],
            "safety_notes": [],
        }
    )
    monkeypatch.setattr(
        "app.agents.draft_generation.DashScopeQwenDraftProvider",
        lambda: FakeQwenProvider(raw),
    )
    client = TestClient(app)
    prepare_active_event(client)

    response = report_sold_out(client)

    assert response.status_code == 200
    assert response.json()["agent_run"]["fallback_used"] is True
    login_as(client, "organizer.demo")
    public_notice_drafts = [
        draft
        for draft in client.get("/api/events/demo-night-tour/agent-drafts").json()
        if draft["draft_type"] == "public_notice"
    ]
    assert public_notice_drafts
    assert "Qwen" not in public_notice_drafts[0]["content"]
    assert "RecoveryProposal" not in public_notice_drafts[0]["content"]


def test_qwen_recovery_success_does_not_create_v2_before_approval(monkeypatch):
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    raw = json.dumps(
        {
            "content": "Explain the merchant capacity issue and ask the organizer to confirm the backup stop.",
            "locale": "en",
            "structured_payload": {
                "requires_organizer_approval": True,
                "affected_merchants": ["m001"],
            },
            "evidence_refs": ["incident:inc_inventory_m001"],
            "safety_notes": ["no publication action included"],
        }
    )
    monkeypatch.setattr(
        "app.agents.draft_generation.DashScopeQwenDraftProvider",
        lambda: FakeQwenProvider(raw),
    )
    client = TestClient(app)
    prepare_active_event(client)

    response = report_sold_out(client)

    assert response.status_code == 200
    assert response.json()["agent_run"]["mode"] == "qwen_draft"
    assert response.json()["agent_run"]["status"] in {"completed", "fallback_completed"}
    login_as(client, "organizer.demo")
    current_plan = client.get("/api/events/demo-night-tour/plans/current")
    assert current_plan.json()["version"] == 1


def complete_review_event(client: TestClient):
    prepare_active_event(client)
    report_sold_out(client)
    login_as(client, "organizer.demo")
    incident = client.get("/api/events/demo-night-tour/incidents").json()[0]
    proposal = client.post(
        f"/api/events/demo-night-tour/incidents/{incident['incident_id']}/recovery-proposals",
        headers=MUTATION_HEADERS,
    ).json()
    client.post(
        f"/api/events/demo-night-tour/recovery-proposals/{proposal['proposal_id']}/approve",
        headers=MUTATION_HEADERS,
    )


def test_qwen_review_summary_uses_existing_metric_refs(monkeypatch):
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    raw = json.dumps(
        {
            "content": "Evidence: h5_visits was observed. Recommendation: keep backup thresholds visible.",
            "locale": "en",
            "structured_payload": {"metrics": ["h5_visits"], "evidence_backed": True},
            "evidence_refs": ["metrics"],
            "safety_notes": ["no invented conversion metric"],
        }
    )
    monkeypatch.setattr(
        "app.agents.draft_generation.DashScopeQwenDraftProvider",
        lambda: FakeQwenProvider(raw),
    )
    client = TestClient(app)
    complete_review_event(client)

    response = client.post("/api/events/demo-night-tour/review-report", headers=MUTATION_HEADERS)

    assert response.status_code == 200
    assert response.json()["agent_run"]["mode"] == "qwen_draft"
    drafts = client.get("/api/events/demo-night-tour/agent-drafts?draft_type=review_summary").json()
    assert drafts
    assert "h5_visits" in drafts[0]["structured_payload"]["metrics"]
    assert "conversion_rate" not in drafts[0]["content"]


def test_qwen_review_schema_failure_falls_back_to_metric_backed_summary(monkeypatch):
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.agents.draft_generation.DashScopeQwenDraftProvider",
        lambda: FakeQwenProvider('{"content": "", "locale": "en"}'),
    )
    client = TestClient(app)
    complete_review_event(client)

    response = client.post("/api/events/demo-night-tour/review-report", headers=MUTATION_HEADERS)

    assert response.status_code == 200
    assert response.json()["agent_run"]["status"] == "fallback_completed"
    drafts = client.get("/api/events/demo-night-tour/agent-drafts?draft_type=review_summary").json()
    assert "h5_visits" in drafts[0]["structured_payload"]["metrics"]
