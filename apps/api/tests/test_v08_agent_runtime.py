from app.agents.guards import evaluate_public_copy, find_forbidden_public_terms
from app.agents.tool_recorder import ToolRecorder


def test_tool_recorder_captures_successful_tool_call():
    recorder = ToolRecorder(run_id="run_001")

    result = recorder.call(
        step_id="step_route",
        tool_name="route.build_static_route",
        input_payload={"rainy": False},
        fn=lambda: ["rp001", "rp002"],
    )

    assert result == ["rp001", "rp002"]
    assert len(recorder.calls) == 1
    call = recorder.calls[0]
    assert call.tool_name == "route.build_static_route"
    assert call.status == "success"
    assert call.output_payload == {"result": ["rp001", "rp002"]}


def test_public_copy_guard_flags_backend_terms():
    terms = find_forbidden_public_terms("PlanVersion v2 is published by RecoveryProposal.")
    assert "PlanVersion" in terms
    assert "RecoveryProposal" in terms

    evaluation = evaluate_public_copy(
        run_id="run_notice_001",
        content="Tonight's route has been adjusted. Please follow the latest route.",
        human_approval_required=True,
        fallback_used=False,
    )
    assert evaluation.schema_pass is True
    assert evaluation.public_copy_ready is True
    assert evaluation.forbidden_public_terms_present is False
