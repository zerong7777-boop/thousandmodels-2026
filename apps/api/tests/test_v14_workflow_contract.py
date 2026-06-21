from app.agents.workflow import WorkflowExecutor, WorkflowNode, WorkflowNodeResult, WorkflowSpec, WorkflowState


def test_workflow_executor_records_leader_then_worker_steps():
    def leader(state: WorkflowState) -> WorkflowNodeResult:
        return WorkflowNodeResult(
            step_id="leader_decompose",
            agent_name="CentralOpsLeader",
            objective="Decompose merchant incident into specialist tasks.",
            structured_output={"assigned_workers": ["FieldOpsWorker"]},
            decision_reason="A sold-out merchant affects visitor flow and public copy.",
            confidence=0.91,
            requires_human_approval=False,
        )

    def worker(state: WorkflowState) -> WorkflowNodeResult:
        assert state.steps[0].agent_name == "CentralOpsLeader"
        return WorkflowNodeResult(
            step_id="field_ops_assess_capacity",
            agent_name="FieldOpsWorker",
            objective="Assess merchant capacity and recommend non-authoritative actions.",
            structured_output={"advice": "pause visitor flow for m001"},
            decision_reason="The merchant reported sold_out inventory.",
            confidence=0.87,
            requires_human_approval=True,
        )

    state = WorkflowState(
        run_id="run_demo-night-tour_qwenpaw_shadow_incident_i001",
        event_id="demo-night-tour",
        trigger="incident_recovery",
        input_refs=["incident:i001"],
    )
    spec = WorkflowSpec(
        workflow_id="qwenpaw_shadow_incident_v1",
        trigger="incident_recovery",
        nodes=[
            WorkflowNode(node_id="leader", run=leader),
            WorkflowNode(node_id="field_ops", run=worker),
        ],
        edges=[("leader", "field_ops")],
    )

    result = WorkflowExecutor().execute(spec, state)

    assert [step.agent_name for step in result.steps] == ["CentralOpsLeader", "FieldOpsWorker"]
    assert result.steps[0].step_id == "leader_decompose"
    assert result.steps[1].requires_human_approval is True
    assert result.steps[1].validation_status == "passed"


def test_workflow_executor_preserves_advisory_bundle():
    def leader(state: WorkflowState) -> WorkflowNodeResult:
        return WorkflowNodeResult(
            step_id="leader_bundle",
            agent_name="CentralOpsLeader",
            objective="Aggregate specialist output into advisory bundle.",
            structured_output={
                "advisory_bundle": {
                    "authoritative_mutation": False,
                    "human_approval_required": True,
                    "recovery_rationale": "m001 needs reduced exposure.",
                }
            },
            decision_reason="Shadow orchestration can advise but cannot apply operations.",
            confidence=0.9,
            requires_human_approval=True,
        )

    state = WorkflowState(
        run_id="run_demo-night-tour_qwenpaw_shadow_incident_i001",
        event_id="demo-night-tour",
        trigger="incident_recovery",
        input_refs=["incident:i001"],
    )
    spec = WorkflowSpec(
        workflow_id="qwenpaw_shadow_incident_v1",
        trigger="incident_recovery",
        nodes=[WorkflowNode(node_id="leader", run=leader)],
        edges=[],
    )

    result = WorkflowExecutor().execute(spec, state)

    assert result.advisory_bundle == {
        "authoritative_mutation": False,
        "human_approval_required": True,
        "recovery_rationale": "m001 needs reduced exposure.",
    }
