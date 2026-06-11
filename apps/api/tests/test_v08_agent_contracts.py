from app.schemas import (
    AgentDraft,
    AgentEvaluation,
    AgentModelCall,
    AgentRun,
    AgentStep,
    AgentToolCall,
)
from app.store import MVPStore


def test_v08_agent_contracts_validate_core_fields(tmp_path):
    run = AgentRun(
        run_id="run_demo_plan_001",
        event_id="demo-night-tour",
        trigger="planning_generation",
        mode="deterministic",
        status="completed",
        started_at="2026-06-12T10:00:00Z",
        completed_at="2026-06-12T10:00:01Z",
        fallback_used=False,
        fallback_reason=None,
        final_output_ref="plan:demo-night-tour:v1",
        error_summary=None,
    )
    tool_call = AgentToolCall(
        tool_call_id="tool_run_demo_plan_001_route_001",
        run_id=run.run_id,
        step_id="step_route",
        tool_name="route.build_static_route",
        input_payload={"rainy": False},
        output_payload={"route_count": 6},
        status="success",
        latency_ms=0,
        error_summary=None,
    )
    step = AgentStep(
        step_id="step_route",
        run_id=run.run_id,
        agent_name="RoutePlanningAgent",
        objective="Build a deterministic route candidate.",
        input_refs=["event_brief:demo-night-tour", "route_points"],
        tool_calls=[tool_call.model_dump()],
        tool_call_refs=[tool_call.tool_call_id],
        model_call_ref=None,
        schema_name="PlanVersion",
        validation_status="passed",
        structured_output={"route_points": ["rp001", "rp002"]},
        decision_reason="Route uses the seeded old-district points.",
        confidence=0.9,
        requires_human_approval=False,
    )
    draft = AgentDraft(
        draft_id="draft_notice_001",
        event_id="demo-night-tour",
        source_run_id=run.run_id,
        draft_type="public_notice",
        locale="zh-Hans",
        content="Tonight's route has been adjusted. Please follow the latest route to the next stop.",
        structured_payload={"affected_merchants": ["m001", "m007"]},
        status="draft",
        reviewed_by=None,
        reviewed_at=None,
        created_at="2026-06-12T10:00:01Z",
    )
    model_call = AgentModelCall(
        model_call_id="model_skipped_001",
        run_id=run.run_id,
        provider="deterministic",
        model="deterministic-template",
        prompt_template_id="public_notice_v1",
        input_refs=["incident:inc_inventory_m001"],
        response_status="skipped",
        parsed_output=None,
        fallback_used=False,
        error_summary=None,
        created_at="2026-06-12T10:00:01Z",
    )
    evaluation = AgentEvaluation(
        evaluation_id="eval_notice_001",
        run_id=run.run_id,
        schema_pass=True,
        fallback_used=False,
        unsafe_mutation_attempted=False,
        human_approval_required=True,
        forbidden_public_terms_present=False,
        public_copy_ready=True,
        notes=["public notice draft is visitor-safe"],
    )

    assert step.validation_status == "passed"
    assert draft.status == "draft"
    assert model_call.response_status == "skipped"
    assert evaluation.human_approval_required is True


def test_v08_agent_store_round_trips_new_objects(tmp_path):
    store = MVPStore(tmp_path / "agent.sqlite3")
    run = AgentRun(
        run_id="run_demo_review_001",
        event_id="demo-night-tour",
        trigger="review_generation",
        mode="deterministic",
        status="completed",
        started_at="2026-06-12T10:00:00Z",
        completed_at="2026-06-12T10:00:01Z",
        fallback_used=False,
        fallback_reason=None,
        final_output_ref="review:demo-night-tour",
        error_summary=None,
    )
    draft = AgentDraft(
        draft_id="draft_review_001",
        event_id="demo-night-tour",
        source_run_id=run.run_id,
        draft_type="review_summary",
        locale="mixed",
        content="Evidence: h5_visits=428. Recommendation: adjust backup merchant threshold.",
        structured_payload={"metrics": ["h5_visits"], "incidents": []},
        status="draft",
        reviewed_by=None,
        reviewed_at=None,
        created_at="2026-06-12T10:00:01Z",
    )

    store.save_agent_run(run)
    store.save_agent_draft(draft)

    assert store.list_agent_runs("demo-night-tour")[0].run_id == run.run_id
    assert store.list_agent_drafts("demo-night-tour")[0].draft_type == "review_summary"
