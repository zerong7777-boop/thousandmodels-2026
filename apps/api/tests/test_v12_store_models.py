import pytest
from pydantic import ValidationError

from app.schemas import (
    AgentEvaluation,
    AgentModelCall,
    AgentRun,
    AgentToolCall,
    CouponRedemption,
    CouponRule,
    EventPage,
    InShopTouchpoint,
    Incident,
    MerchantExecutionPack,
    MerchantInteractionPackage,
    MerchantTask,
    OperationSuggestion,
    RecoveryAction,
    RecoveryProposal,
    ReviewReport,
    TouchpointInteraction,
)
from app.store import MVPStore


EVENT_ID = "demo-night-tour"


def make_event_page(
    page_id: str = "ep-1",
    status: str = "draft",
    event_id: str = EVENT_ID,
    plan_version: int = 1,
    updated_at: str = "2026-06-15T10:00:00Z",
    published_at: str | None = None,
) -> EventPage:
    return EventPage(
        id=page_id,
        event_id=event_id,
        plan_version=plan_version,
        status=status,
        title="Night Tour",
        subtitle="A route through Taipa",
        story_sections=[{"title": "Start", "body": "Begin at the square."}],
        route_highlights=[{"point_id": "rp1", "label": "Square"}],
        merchant_highlights=[{"merchant_id": "m001", "label": "Tea shop"}],
        notices=[{"message": "Bring an umbrella."}],
        published_at=published_at,
        updated_at=updated_at,
    )


def make_touchpoint(
    touchpoint_id: str = "tp-1",
    merchant_id: str = "m001",
    event_id: str = EVENT_ID,
) -> InShopTouchpoint:
    return InShopTouchpoint(
        id=touchpoint_id,
        event_id=event_id,
        merchant_id=merchant_id,
        package_id=f"pkg-{merchant_id}",
        touchpoint_type="in_shop_qr",
        label="Counter QR",
        public_copy="Scan for a story clue.",
        token=f"token-{touchpoint_id}",
        metrics={"scans": 1},
        created_at="2026-06-15T10:05:00Z",
    )


def make_coupon_rule(
    rule_id: str = "cr-1",
    merchant_id: str = "m001",
    event_id: str = EVENT_ID,
    max_redemptions: int = 20,
    per_anonymous_interaction_limit: int = 1,
) -> CouponRule:
    return CouponRule(
        id=rule_id,
        event_id=event_id,
        merchant_id=merchant_id,
        package_id=f"pkg-{merchant_id}",
        title="Tea tasting",
        description="One small tasting for route visitors.",
        max_redemptions=max_redemptions,
        per_anonymous_interaction_limit=per_anonymous_interaction_limit,
        created_at="2026-06-15T10:06:00Z",
    )


def make_package(merchant_id: str = "m001") -> MerchantInteractionPackage:
    return MerchantInteractionPackage(
        id=f"pkg-{merchant_id}",
        event_id=EVENT_ID,
        merchant_id=merchant_id,
        plan_version=1,
        status="active",
        operator_brief="Prepare tasting cups near the counter.",
        visitor_pitch="Scan the QR and claim the tasting.",
        task_ids=["task-1"],
        touchpoints=[make_touchpoint(merchant_id=merchant_id)],
        coupon_rules=[make_coupon_rule(merchant_id=merchant_id)],
        evidence_refs=["plan_versions:demo-night-tour:v1"],
        created_at="2026-06-15T10:10:00Z",
        updated_at="2026-06-15T10:15:00Z",
    )


def make_interaction(interaction_id: str = "ti-1", merchant_id: str = "m001") -> TouchpointInteraction:
    return TouchpointInteraction(
        id=interaction_id,
        event_id=EVENT_ID,
        touchpoint_id="tp-1",
        merchant_id=merchant_id,
        interaction_type="scan",
        source="qr",
        anonymous_interaction_id="anon-1",
        created_at="2026-06-15T10:20:00Z",
        metadata={"device": "mobile"},
    )


def make_redemption(
    redemption_id: str = "red-1",
    merchant_id: str = "m001",
    event_id: str = EVENT_ID,
) -> CouponRedemption:
    return CouponRedemption(
        id=redemption_id,
        event_id=event_id,
        coupon_rule_id="cr-1",
        merchant_id=merchant_id,
        anonymous_interaction_id="anon-1",
        status="claimed",
        claimed_at="2026-06-15T10:21:00Z",
    )


def make_suggestion(suggestion_id: str = "os-1", event_id: str = EVENT_ID) -> OperationSuggestion:
    return OperationSuggestion(
        id=suggestion_id,
        event_id=event_id,
        suggestion_type="merchant_capacity",
        title="Reduce tea shop load",
        rationale="Queue status is busy and inventory is low.",
        recommended_actions=[{"type": "pause_coupon", "coupon_rule_id": "cr-1"}],
        impacted_merchants=["m001"],
        impacted_route_points=["rp1"],
        evidence_refs=["runtime_states:m001"],
        created_at="2026-06-15T10:25:00Z",
    )


def make_execution_pack(merchant_id: str = "m001") -> MerchantExecutionPack:
    return MerchantExecutionPack(
        merchant_id=merchant_id,
        event_id=EVENT_ID,
        role="story stop",
        time_slot="18:00-19:00",
        visitor_task="Scan the counter card.",
        preparation_items=["Prepare card"],
        promo_text="Route visitors can claim a tasting.",
        fallback_instruction="Pause the offer if overloaded.",
    )


def make_merchant_task(task_id: str = "task-1", merchant_id: str = "m001") -> MerchantTask:
    return MerchantTask(
        task_id=task_id,
        event_id=EVENT_ID,
        merchant_id=merchant_id,
        plan_version=1,
        role="story stop",
        time_slot="18:00-19:00",
        visitor_task="Scan the counter card.",
        preparation_items=["Prepare card"],
        promo_text="Route visitors can claim a tasting.",
        fallback_instruction="Pause the offer if overloaded.",
        task_status="active",
    )


def test_v12_schema_imports_and_defaults_validate():
    page = make_event_page()
    touchpoint = make_touchpoint()
    rule = make_coupon_rule()
    package = make_package()
    interaction = make_interaction()
    redemption = make_redemption()
    suggestion = make_suggestion()
    report = ReviewReport(
        event_id=EVENT_ID,
        summary="Done",
        route_result="Stable",
        merchant_result="Stable",
        incident_summary="None",
        agent_actions=[],
        human_approvals=[],
        lessons_learned=[],
        next_event_recommendations=[],
    )

    assert page.status == "draft"
    assert touchpoint.status == "active"
    assert rule.status == "active"
    assert rule.per_anonymous_interaction_limit == 1
    assert package.touchpoints == [touchpoint]
    assert interaction.metadata["device"] == "mobile"
    assert redemption.redeemed_at is None
    assert suggestion.status == "pending_approval"
    assert report.touchpoint_summary == {}
    assert report.merchant_outcomes == []
    assert report.extension_tasks == []


def test_save_get_list_event_page(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    first = store.save_event_page(make_event_page("ep-1", "draft"))
    second = store.save_event_page(make_event_page("ep-2", "published"))

    assert store.get_event_page(EVENT_ID, "ep-1") == first
    assert store.list_event_pages(EVENT_ID) == [first, second]
    assert store.get_latest_event_page(EVENT_ID) == second


def test_save_list_package_touchpoints_and_coupon_rules(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    package = store.save_merchant_interaction_package(make_package("m001"))
    other_package = store.save_merchant_interaction_package(make_package("m002"))
    touchpoint = store.save_touchpoint(make_touchpoint("tp-1", "m001"))
    store.save_touchpoint(make_touchpoint("tp-2", "m002"))
    rule = store.save_coupon_rule(make_coupon_rule("cr-1", "m001"))
    store.save_coupon_rule(make_coupon_rule("cr-2", "m002"))

    assert store.list_merchant_interaction_packages(EVENT_ID) == [package, other_package]
    assert store.get_merchant_interaction_package(EVENT_ID, "m001") == package
    assert store.get_touchpoint(EVENT_ID, "tp-1") == touchpoint
    assert store.list_touchpoints(EVENT_ID, merchant_id="m001") == [touchpoint]
    assert store.get_coupon_rule(EVENT_ID, "cr-1") == rule
    assert store.list_coupon_rules(EVENT_ID, merchant_id="m001") == [rule]


def test_save_list_touchpoint_interactions_and_coupon_redemptions(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    interaction = store.save_touchpoint_interaction(make_interaction("ti-1", "m001"))
    store.save_touchpoint_interaction(make_interaction("ti-2", "m002"))
    redemption = store.save_coupon_redemption(make_redemption("red-1", "m001"))
    store.save_coupon_redemption(make_redemption("red-2", "m002"))

    assert store.list_touchpoint_interactions(EVENT_ID, merchant_id="m001") == [interaction]
    assert store.get_coupon_redemption(EVENT_ID, "red-1") == redemption
    assert store.list_coupon_redemptions(EVENT_ID, merchant_id="m001") == [redemption]


def test_save_list_operation_suggestions(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    suggestion = store.save_operation_suggestion(make_suggestion("os-1"))
    other = store.save_operation_suggestion(make_suggestion("os-2"))

    assert store.list_operation_suggestions(EVENT_ID) == [suggestion, other]
    assert store.get_operation_suggestion(EVENT_ID, "os-1") == suggestion


def test_clear_demo_clears_v12_collections(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    store.save_event_page(make_event_page())
    store.save_merchant_interaction_package(make_package())
    store.save_touchpoint(make_touchpoint())
    store.save_coupon_rule(make_coupon_rule())
    store.save_touchpoint_interaction(make_interaction())
    store.save_coupon_redemption(make_redemption())
    store.save_operation_suggestion(make_suggestion())

    store.clear_demo(EVENT_ID)

    assert store.list_event_pages(EVENT_ID) == []
    assert store.list_merchant_interaction_packages(EVENT_ID) == []
    assert store.list_touchpoints(EVENT_ID) == []
    assert store.list_coupon_rules(EVENT_ID) == []
    assert store.list_touchpoint_interactions(EVENT_ID) == []
    assert store.list_coupon_redemptions(EVENT_ID) == []
    assert store.list_operation_suggestions(EVENT_ID) == []


def test_clear_demo_preserves_shared_prefix_event_records(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    other_page = store.save_event_page(make_event_page("ep-1", event_id=EVENT_ID))
    other_touchpoint = store.save_touchpoint(
        make_touchpoint("tp-1", event_id=EVENT_ID)
    )

    store.save_event_page(make_event_page("ep-1", event_id="demo"))
    store.save_touchpoint(make_touchpoint("tp-1", event_id="demo"))

    store.clear_demo("demo")

    assert store.list_event_pages("demo") == []
    assert store.list_touchpoints("demo") == []
    assert store.list_event_pages(EVENT_ID) == [other_page]
    assert store.list_touchpoints(EVENT_ID) == [other_touchpoint]


def test_clear_demo_clears_agent_child_records_with_run_id_keys(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    run_id = f"run_{EVENT_ID}_planning_v1"
    other_run_id = "run_other-event_planning_v1"
    store.save_agent_tool_call(
        AgentToolCall(
            tool_call_id="tool-1",
            run_id=run_id,
            step_id="step-1",
            tool_name="demo.tool",
            input_payload={},
            output_payload={},
            status="success",
        )
    )
    store.save_agent_model_call(
        AgentModelCall(
            model_call_id="model-1",
            run_id=run_id,
            provider="deterministic",
            model="deterministic",
            prompt_template_id="prompt-1",
            input_refs=[],
            response_status="skipped",
            fallback_used=False,
            created_at="2026-06-15T10:00:00Z",
        )
    )
    store.save_agent_evaluation(
        AgentEvaluation(
            evaluation_id="eval-1",
            run_id=run_id,
            schema_pass=True,
            fallback_used=False,
            unsafe_mutation_attempted=False,
            human_approval_required=True,
            forbidden_public_terms_present=False,
            public_copy_ready=True,
        )
    )
    store.save_agent_tool_call(
        AgentToolCall(
            tool_call_id="tool-2",
            run_id=other_run_id,
            step_id="step-1",
            tool_name="demo.tool",
            input_payload={},
            output_payload={},
            status="success",
        )
    )

    store.clear_demo(EVENT_ID)

    assert store.list_agent_tool_calls(run_id) == []
    assert store.list_agent_model_calls(run_id) == []
    assert store.list_agent_evaluations(run_id) == []
    assert [call.tool_call_id for call in store.list_agent_tool_calls(other_run_id)] == ["tool-2"]


def test_legacy_event_scoped_getters_do_not_return_same_id_from_another_event(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    other_event_id = "another-event"
    shared_action_id = "ra-shared"
    shared_incident_id = "inc-shared"
    shared_proposal_id = "rp-shared"
    shared_run_id = "run-shared"
    store.save_recovery_action(
        RecoveryAction(
            action_id=shared_action_id,
            event_id=other_event_id,
            trigger_type="inventory",
            trigger_detail="other",
            recommended_changes=[],
            affected_merchants=[],
            tourist_notification="other",
            merchant_notification="other",
        )
    )
    store.save_incident(
        Incident(
            incident_id=shared_incident_id,
            event_id=other_event_id,
            type="inventory",
            severity="high",
            source="merchant",
            trigger_detail="other",
            affected_route_points=[],
            affected_merchants=[],
            status="open",
            created_at="2026-06-15T10:00:00Z",
        )
    )
    store.save_recovery_proposal(
        RecoveryProposal(
            proposal_id=shared_proposal_id,
            incident_id=shared_incident_id,
            event_id=other_event_id,
            recommended_changes=[],
            plan_patch={},
            merchant_task_patch={},
            public_notice_patch="other",
            impact_summary="other",
        )
    )
    store.save_agent_run(
        AgentRun(
            run_id=shared_run_id,
            event_id=other_event_id,
            trigger="planning_generation",
            mode="deterministic",
            status="completed",
            started_at="2026-06-15T10:00:00Z",
        )
    )

    assert store.get_recovery_action(shared_action_id, event_id=EVENT_ID) is None
    assert store.get_incident(shared_incident_id, event_id=EVENT_ID) is None
    assert store.get_recovery_proposal(shared_proposal_id, event_id=EVENT_ID) is None
    assert store.get_agent_run(shared_run_id, event_id=EVENT_ID) is None


def test_save_packs_and_merchant_tasks_replace_existing_event_children(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    store.save_packs(EVENT_ID, [make_execution_pack("m001"), make_execution_pack("m002")])
    store.save_packs(EVENT_ID, [make_execution_pack("m001")])
    store.save_merchant_tasks(
        EVENT_ID,
        [make_merchant_task("task-1", "m001"), make_merchant_task("task-2", "m002")],
    )
    store.save_merchant_tasks(EVENT_ID, [make_merchant_task("task-1", "m001")])

    assert [pack.merchant_id for pack in store.list_packs(EVENT_ID)] == ["m001"]
    assert [task.task_id for task in store.list_merchant_tasks(EVENT_ID)] == ["task-1"]


def test_event_scoped_getters_do_not_return_same_id_from_another_event(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    other_event_id = "another-event"
    store.save_event_page(make_event_page("shared-id", event_id=other_event_id))
    store.save_touchpoint(make_touchpoint("shared-id", event_id=other_event_id))
    store.save_coupon_rule(make_coupon_rule("shared-id", event_id=other_event_id))
    store.save_coupon_redemption(make_redemption("shared-id", event_id=other_event_id))
    store.save_operation_suggestion(make_suggestion("shared-id", event_id=other_event_id))

    assert store.get_event_page(EVENT_ID, "shared-id") is None
    assert store.get_touchpoint(EVENT_ID, "shared-id") is None
    assert store.get_coupon_rule(EVENT_ID, "shared-id") is None
    assert store.get_coupon_redemption(EVENT_ID, "shared-id") is None
    assert store.get_operation_suggestion(EVENT_ID, "shared-id") is None


def test_latest_event_page_uses_plan_version_before_key_order(tmp_path):
    store = MVPStore(tmp_path / "v12.sqlite3")
    lower_version_later_key = store.save_event_page(
        make_event_page("z-page", plan_version=1, updated_at="2026-06-15T12:00:00Z")
    )
    higher_version_earlier_key = store.save_event_page(
        make_event_page("a-page", plan_version=2, updated_at="2026-06-15T09:00:00Z")
    )

    assert store.list_event_pages(EVENT_ID) == [higher_version_earlier_key, lower_version_later_key]
    assert store.get_latest_event_page(EVENT_ID) == higher_version_earlier_key


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("max_redemptions", 0),
        ("max_redemptions", -1),
        ("per_anonymous_interaction_limit", 0),
        ("per_anonymous_interaction_limit", -1),
    ],
)
def test_coupon_rule_rejects_non_positive_limits(field, value):
    kwargs = {field: value}

    with pytest.raises(ValidationError):
        make_coupon_rule(**kwargs)
