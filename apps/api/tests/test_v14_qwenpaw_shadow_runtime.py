from fastapi.testclient import TestClient

from app.agents.runtime import AgentRuntime
from app.main import app
from app.store import STORE
from scripts.reset_demo_state import reset_demo_state


MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}


def login_as(client: TestClient, username: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "demo1234"},
        headers=MUTATION_HEADERS,
    )
    assert response.status_code == 200, response.text


def prepare_sold_out_incident() -> str:
    reset_demo_state(event_id="demo-night-tour")
    with TestClient(app) as client:
        login_as(client, "organizer.demo")
        assert client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS).status_code == 200
        assert client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS).status_code == 200
        assert client.post("/api/events/demo-night-tour/event-page/draft", headers=MUTATION_HEADERS).status_code == 200
        assert client.post("/api/events/demo-night-tour/event-page/publish", headers=MUTATION_HEADERS).status_code == 200
        assert (
            client.post(
                "/api/events/demo-night-tour/merchant-edge-packages/generate",
                headers=MUTATION_HEADERS,
            ).status_code
            == 200
        )
        login_as(client, "merchant.m001.demo")
        response = client.post(
            "/api/merchants/m001/runtime-state",
            json={
                "inventory_status": "sold_out",
                "queue_status": "normal",
                "available_for_visitors": False,
                "temporary_note": "Sold out during v1.4 spike test.",
            },
            headers=MUTATION_HEADERS,
        )
        assert response.status_code == 200, response.text
    incidents = STORE.list_incidents("demo-night-tour")
    assert incidents
    return incidents[-1].incident_id


def test_qwenpaw_shadow_runtime_records_leader_worker_evidence_without_mutation():
    incident_id = prepare_sold_out_incident()
    incident = STORE.get_incident(incident_id, event_id="demo-night-tour")
    before_plan_versions = STORE.list_plan_versions("demo-night-tour")
    before_notices = STORE.list_public_notices("demo-night-tour")
    before_runtime = STORE.get_runtime_state("m001").model_dump()
    before_redemptions = STORE.list_coupon_redemptions("demo-night-tour")
    before_suggestions = STORE.list_operation_suggestions("demo-night-tour")

    result = AgentRuntime(mode="qwenpaw_workflow").run_qwenpaw_shadow_orchestration(
        event_id="demo-night-tour",
        incident=incident,
    )

    assert result.run.run_id == f"run_demo-night-tour_qwenpaw_shadow_{incident_id}"
    assert result.run.mode == "qwenpaw_workflow"
    assert result.run.trigger == "incident_recovery"
    assert result.run.status == "completed"
    assert result.run.final_output_ref.startswith("qwenpaw_shadow_advisory:")
    assert [step.agent_name for step in result.steps] == [
        "CentralOpsLeader",
        "MerchantEdgeWorker",
        "FieldOpsWorker",
        "PublicNoticeWorker",
        "ReviewEvidenceWorker",
        "SafetyGateWorker",
    ]
    assert any(call.output_payload["permission_decision"]["permission"] == "read_only" for call in result.tool_calls)
    assert any(call.output_payload["permission_decision"]["allowed"] is False for call in result.tool_calls)
    assert result.drafts
    assert result.drafts[0].draft_type == "public_notice"
    assert "advisory_bundle" in result.drafts[0].structured_payload
    assert result.evaluations
    assert all(evaluation.human_approval_required for evaluation in result.evaluations)

    assert STORE.list_plan_versions("demo-night-tour") == before_plan_versions
    assert STORE.list_public_notices("demo-night-tour") == before_notices
    assert STORE.get_runtime_state("m001").model_dump() == before_runtime
    assert STORE.list_coupon_redemptions("demo-night-tour") == before_redemptions
    assert STORE.list_operation_suggestions("demo-night-tour") == before_suggestions


def test_qwenpaw_shadow_runtime_falls_back_on_unsafe_adapter_output(monkeypatch):
    incident_id = prepare_sold_out_incident()
    incident = STORE.get_incident(incident_id, event_id="demo-night-tour")

    from app.agents import qwenpaw_adapter

    def unsafe_result(self, context):
        return qwenpaw_adapter.QwenPawWorkflowResult(
            leader_decision={"assigned_workers": ["FieldOpsWorker"]},
            worker_outputs=[
                {
                    "agent_name": "FieldOpsWorker",
                    "content": "apply_suggestion immediately",
                    "structured_payload": {
                        "apply_suggestion": True,
                        "approval_status": "approved",
                        "public_notice": {"publish_status": "published"},
                        "claim_coupon": True,
                        "coupon_redemption": {"redemption_status": "redeemed"},
                    },
                }
            ],
            advisory_bundle={"authoritative_mutation": True, "human_approval_required": False},
            permission_requests=[],
            safety_notes=["unsafe test payload"],
        )

    monkeypatch.setattr(qwenpaw_adapter.FakeQwenPawWorkflowAdapter, "run_shadow_incident_workflow", unsafe_result)

    result = AgentRuntime(mode="qwenpaw_workflow").run_qwenpaw_shadow_orchestration(
        event_id="demo-night-tour",
        incident=incident,
    )

    assert result.run.status == "fallback_completed"
    assert result.run.fallback_used is True
    assert result.run.fallback_reason == "unsafe_qwenpaw_output"
    assert any(evaluation.unsafe_mutation_attempted for evaluation in result.evaluations)
