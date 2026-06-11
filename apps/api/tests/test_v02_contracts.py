from app.schemas import (
    AgentStep,
    AgentTrace,
    Incident,
    MerchantTask,
    OperationalMetric,
    PlanVersion,
    PublicNotice,
    RecoveryProposal,
    RoutePoint,
)


def test_plan_version_contract_contains_diff_and_route_points():
    route_point = RoutePoint(
        point_id="rp001",
        name="福隆新街开场点",
        type="street",
        is_indoor=False,
        estimated_stay_minutes=20,
        story="以老字号街景作为夜游起点。",
        linked_merchants=["m001"],
        visitor_task="完成老字号问答",
        rainy_day_score=2,
        crowd_risk="medium",
        current_status="active",
    )
    plan = PlanVersion(
        plan_id="demo-night-tour:v1",
        event_id="demo-night-tour",
        version=1,
        status="draft",
        created_by="OrchestratorAgent",
        created_reason="initial_plan",
        route_points=[route_point],
        merchant_assignments=["m001"],
        budget_plan={"total_mop": 50000, "contingency_mop": 5000},
        risk_plan=["inventory", "weather"],
        diff_from_previous=[],
    )
    assert plan.route_points[0].point_id == "rp001"
    assert plan.diff_from_previous == []


def test_incident_recovery_notice_and_trace_contracts():
    incident = Incident(
        incident_id="inc_inventory_m001",
        event_id="demo-night-tour",
        type="inventory",
        severity="high",
        source="merchant",
        trigger_detail="m001 sold_out",
        affected_route_points=["rp001"],
        affected_merchants=["m001"],
        status="open",
        created_at="2026-06-09T12:00:00Z",
    )
    proposal = RecoveryProposal(
        proposal_id="rec_inc_inventory_m001",
        incident_id=incident.incident_id,
        event_id="demo-night-tour",
        recommended_changes=["replace route point rp001 with rp007"],
        plan_patch={"replace_route_points": [{"from": "rp001", "to": "rp007"}]},
        merchant_task_patch={"m001": "pause_visitors", "m007": "activate_backup"},
        public_notice_patch="福隆老饼家库存售罄，路线调整至新街手信铺。",
        impact_summary="影响 1 个路线点和 2 个商户任务。",
        requires_approval=True,
        approval_status="pending",
    )
    notice = PublicNotice(
        notice_id="notice_rec_inc_inventory_m001",
        event_id="demo-night-tour",
        plan_version=2,
        audience="tourist",
        message=proposal.public_notice_patch,
        reason="inventory_recovery",
        publish_status="draft",
    )
    trace = AgentTrace(
        trace_id="trace_plan_v1",
        event_id="demo-night-tour",
        trigger="generate_plan",
        steps=[
            AgentStep(
                agent_name="RoutePlannerAgent",
                input_refs=["event_brief:demo-night-tour"],
                tool_calls=[{"tool": "route.check", "result": "rain backup available"}],
                structured_output={"route_points": ["rp001", "rp002"]},
                decision_reason="route fits night-tour timing",
                confidence=0.88,
                requires_human_approval=False,
            )
        ],
        final_output_ref="plan:demo-night-tour:v1",
        human_decision_ref=None,
    )
    assert proposal.requires_approval is True
    assert notice.publish_status == "draft"
    assert trace.steps[0].agent_name == "RoutePlannerAgent"


def test_merchant_task_and_metric_contracts():
    task = MerchantTask(
        task_id="task_demo_m001_v1",
        event_id="demo-night-tour",
        merchant_id="m001",
        plan_version=1,
        role="集合与开场试吃",
        time_slot="18:10-18:35",
        visitor_task="完成老字号问答",
        preparation_items=["准备 80 份试吃", "张贴活动二维码"],
        promo_text="凭 H5 打卡领取限定优惠。",
        fallback_instruction="库存不足时暂停导流并提示主办方。",
        task_status="active",
    )
    metric = OperationalMetric(
        metric_id="metric_h5_visits",
        event_id="demo-night-tour",
        name="h5_visits",
        value=428,
        unit="visits",
        source="mock",
        captured_at="2026-06-09T12:00:00Z",
    )
    assert task.plan_version == 1
    assert metric.value == 428
