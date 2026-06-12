from fastapi.testclient import TestClient

from app.main import app
from app.schemas import AgentEvaluation, AgentModelCall, AgentRun
from app.store import STORE
from tests.conftest import login_as


def seed_run_with_model_evidence():
    run = AgentRun(
        run_id="run_demo-night-tour_review",
        event_id="demo-night-tour",
        trigger="review_generation",
        mode="qwen_draft",
        status="fallback_completed",
        started_at="2026-06-12T10:00:00Z",
        completed_at="2026-06-12T10:00:01Z",
        fallback_used=True,
        fallback_reason="schema_failed",
        final_output_ref="draft:draft_review",
        error_summary=None,
    )
    STORE.save_agent_run(run)
    STORE.save_agent_model_call(
        AgentModelCall(
            model_call_id="model_run_demo-night-tour_review_qwen_review_summary_v1",
            run_id=run.run_id,
            provider="dashscope",
            model="qwen-plus",
            prompt_template_id="qwen_review_summary_v1",
            input_refs=["metrics"],
            response_status="schema_failed",
            parsed_output=None,
            fallback_used=True,
            error_summary="structured_payload required",
            created_at="2026-06-12T10:00:01Z",
        )
    )
    STORE.save_agent_evaluation(
        AgentEvaluation(
            evaluation_id="eval_run_demo-night-tour_review_public_copy",
            run_id=run.run_id,
            schema_pass=False,
            fallback_used=True,
            unsafe_mutation_attempted=False,
            human_approval_required=True,
            forbidden_public_terms_present=False,
            public_copy_ready=True,
            notes=["schema fallback used"],
        )
    )
    return run


def test_organizer_can_read_model_calls_and_evaluations():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    run = seed_run_with_model_evidence()

    model_calls = client.get(f"/api/events/demo-night-tour/agent-runs/{run.run_id}/model-calls")
    evaluations = client.get(f"/api/events/demo-night-tour/agent-runs/{run.run_id}/evaluations")

    assert model_calls.status_code == 200
    assert model_calls.json()[0]["response_status"] == "schema_failed"
    assert evaluations.status_code == 200
    assert evaluations.json()[0]["fallback_used"] is True


def test_merchant_cannot_read_model_calls():
    client = TestClient(app)
    run = seed_run_with_model_evidence()
    login_as(client, "merchant.m001.demo")

    response = client.get(f"/api/events/demo-night-tour/agent-runs/{run.run_id}/model-calls")

    assert response.status_code == 403


def test_wrong_event_model_call_lookup_returns_404():
    client = TestClient(app)
    login_as(client, "organizer.demo")
    run = seed_run_with_model_evidence()

    response = client.get(f"/api/events/other-event/agent-runs/{run.run_id}/model-calls")

    assert response.status_code == 404
