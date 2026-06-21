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


def test_tool_registry_generates_unique_call_ids_for_repeated_tool_requests():
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

    first = registry.request(
        run_id="run_demo",
        step_id="field_ops",
        request=ToolRequest(
            tool_name="incident.get_active_incident_snapshot",
            requested_by_agent="FieldOpsWorker",
            input_payload={"incident_id": "i001"},
        ),
    )
    second = registry.request(
        run_id="run_demo",
        step_id="field_ops",
        request=ToolRequest(
            tool_name="incident.get_active_incident_snapshot",
            requested_by_agent="FieldOpsWorker",
            input_payload={"incident_id": "i001"},
        ),
    )

    assert first.tool_call.tool_call_id != second.tool_call.tool_call_id


def test_tool_registry_records_failed_call_when_handler_raises():
    registry = ToolRegistry()

    def fail(payload):
        raise RuntimeError("snapshot service unavailable")

    registry.register(
        ToolDefinition(
            name="incident.get_active_incident_snapshot",
            permission=ToolPermission.READ_ONLY,
            input_schema_name="IncidentSnapshotInput",
            output_schema_name="IncidentSnapshot",
            handler=fail,
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
    assert result.output_payload == {}
    assert result.tool_call.status == "failed"
    assert result.tool_call.error_summary == "snapshot service unavailable"
    assert result.tool_call.output_payload["permission_decision"] == {
        "allowed": True,
        "permission": "read_only",
        "reason": "tool permission read_only is allowed for shadow orchestration",
    }


def test_tool_registry_records_failed_call_for_unknown_tool():
    registry = ToolRegistry()

    result = registry.request(
        run_id="run_demo",
        step_id="field_ops",
        request=ToolRequest(
            tool_name="incident.unknown_tool",
            requested_by_agent="FieldOpsWorker",
            input_payload={"incident_id": "i001"},
        ),
    )

    assert result.decision.allowed is False
    assert result.decision.permission == ToolPermission.FORBIDDEN
    assert result.output_payload == {}
    assert result.tool_call.status == "failed"
    assert result.tool_call.error_summary == "tool incident.unknown_tool is not registered for shadow orchestration"
    assert result.tool_call.output_payload["permission_decision"] == {
        "allowed": False,
        "permission": "forbidden",
        "reason": "tool incident.unknown_tool is not registered for shadow orchestration",
    }
