from app.agents.tool_registry import (
    ToolDefinition,
    ToolPermission,
    ToolRegistry,
    ToolRequest,
)


def test_tool_registry_executes_read_only_tool_and_records_success():
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="incident.get_active_incident_snapshot",
            permission=ToolPermission.READ_ONLY,
            input_schema_name="IncidentSnapshotInput",
            output_schema_name="IncidentSnapshot",
            handler=lambda payload: {"incident_id": payload["incident_id"], "status": "open"},
        )
    )

    result = registry.request(
        run_id="run_demo",
        step_id="field_ops",
        request=ToolRequest(
            tool_name="incident.get_active_incident_snapshot",
            requested_by_agent="FieldOpsWorker",
            input_payload={"incident_id": "i001"},
        ),
    )

    assert result.decision.allowed is True
    assert result.output_payload == {"incident_id": "i001", "status": "open"}
    assert result.tool_call.tool_name == "incident.get_active_incident_snapshot"
    assert result.tool_call.status == "success"
    assert result.tool_call.output_payload["permission_decision"] == {
        "allowed": True,
        "permission": "read_only",
        "reason": "tool permission read_only is allowed for shadow orchestration",
    }


def test_tool_registry_denies_approval_required_tool_without_executing_handler():
    executed = {"value": False}

    def mutate(payload):
        executed["value"] = True
        return {"applied": True}

    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="operation.apply_suggestion",
            permission=ToolPermission.APPROVAL_REQUIRED,
            input_schema_name="OperationSuggestionApplyInput",
            output_schema_name="OperationSuggestionApplyResult",
            handler=mutate,
        )
    )

    result = registry.request(
        run_id="run_demo",
        step_id="field_ops",
        request=ToolRequest(
            tool_name="operation.apply_suggestion",
            requested_by_agent="FieldOpsWorker",
            input_payload={"suggestion_id": "os_demo_m001"},
        ),
    )

    assert executed["value"] is False
    assert result.decision.allowed is False
    assert result.decision.permission == ToolPermission.APPROVAL_REQUIRED
    assert result.tool_call.status == "failed"
    assert result.tool_call.error_summary == "tool permission approval_required is denied in shadow orchestration"
    assert result.tool_call.output_payload["permission_decision"]["allowed"] is False
