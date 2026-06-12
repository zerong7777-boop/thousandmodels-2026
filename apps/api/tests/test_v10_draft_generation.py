import pytest

from app.agents.draft_generation import (
    DeterministicDraftGenerator,
    DraftGenerationContext,
    QwenDraftCandidate,
    QwenDraftGenerator,
    UnsafeModelMutationError,
    choose_draft_generator,
    parse_qwen_candidate,
    reject_unsafe_mutation,
)
from app.schemas import Incident, OperationalMetric


def incident() -> Incident:
    return Incident(
        incident_id="inc_inventory_m001",
        event_id="demo-night-tour",
        type="inventory",
        severity="high",
        source="merchant",
        trigger_detail="m001 sold out",
        affected_route_points=["rp002"],
        affected_merchants=["m001"],
        status="proposal_ready",
        created_at="2026-06-12T10:00:00Z",
    )


def recovery_context() -> DraftGenerationContext:
    return DraftGenerationContext(
        run_id="run_demo-night-tour_incident_inc_inventory_m001",
        event_id="demo-night-tour",
        draft_type="public_notice",
        input_refs=["incident:inc_inventory_m001", "proposal:prop_inc_inventory_m001"],
        incident=incident(),
        proposal_payload={
            "proposal_id": "prop_inc_inventory_m001",
            "recommended_changes": ["Pause m001", "Use backup merchant m007"],
            "public_notice_patch": "Please continue to the indoor tea stop. The route has been updated.",
            "impact_summary": "One merchant stop is replaced.",
        },
    )


def review_context() -> DraftGenerationContext:
    return DraftGenerationContext(
        run_id="run_demo-night-tour_review",
        event_id="demo-night-tour",
        draft_type="review_summary",
        input_refs=["metrics", "incidents", "public_notices", "recovery_proposals"],
        metrics=[
            OperationalMetric(
                metric_id="metric_h5_visits",
                event_id="demo-night-tour",
                name="h5_visits",
                value=428,
                unit="visits",
                source="public_h5",
                captured_at="2026-06-12T11:00:00Z",
            )
        ],
        incidents=[],
        notices=[],
        proposals=[],
    )


def test_default_draft_generator_is_deterministic(monkeypatch):
    monkeypatch.delenv("AGENT_DRAFT_BACKEND", raising=False)
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

    generator = choose_draft_generator()

    assert isinstance(generator, DeterministicDraftGenerator)
    assert generator.mode == "deterministic"


def test_qwen_requested_without_key_uses_skipped_fallback(monkeypatch):
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

    generator = choose_draft_generator()
    result = generator.generate_public_notice(recovery_context())

    assert isinstance(generator, QwenDraftGenerator)
    assert result.fallback_used is True
    assert result.fallback_reason == "missing_provider_key"
    assert result.draft.draft_type == "public_notice"
    assert result.model_call is not None
    assert result.model_call.provider == "dashscope"
    assert result.model_call.response_status == "skipped"
    assert result.model_call.fallback_used is True


def test_qwen_candidate_schema_accepts_controlled_payload():
    candidate = QwenDraftCandidate.model_validate(
        {
            "content": "Please continue to the indoor tea stop. The route has been updated.",
            "locale": "en",
            "structured_payload": {
                "affected_merchants": ["m001"],
                "requires_organizer_approval": True,
            },
            "evidence_refs": ["incident:inc_inventory_m001"],
            "safety_notes": ["visitor-safe wording"],
        }
    )

    assert candidate.locale == "en"
    assert candidate.evidence_refs == ["incident:inc_inventory_m001"]


def test_invalid_json_is_reported_as_invalid_json():
    result = parse_qwen_candidate("not-json")

    assert result.candidate is None
    assert result.response_status == "invalid_json"
    assert "JSON" in result.error_summary


def test_schema_failure_is_reported_as_schema_failed():
    result = parse_qwen_candidate('{"content": "", "locale": "zh-Hans"}')

    assert result.candidate is None
    assert result.response_status == "schema_failed"
    assert "structured_payload" in result.error_summary


def test_unsafe_mutation_fields_are_rejected():
    payload = {
        "content": "Use backup merchant.",
        "locale": "en",
        "structured_payload": {
            "approval_status": "approved",
            "plan_patch": {"version": 2},
        },
        "evidence_refs": ["incident:inc_inventory_m001"],
        "safety_notes": [],
    }

    with pytest.raises(UnsafeModelMutationError):
        reject_unsafe_mutation(payload)


def test_deterministic_review_summary_does_not_fabricate_metrics():
    result = DeterministicDraftGenerator().generate_review_summary(review_context())

    assert result.model_call is None
    assert result.fallback_used is False
    assert result.draft.draft_type == "review_summary"
    assert result.draft.structured_payload["metrics"] == ["h5_visits"]
    assert "conversion_rate" not in result.draft.content
