from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.schemas import AgentToolCall


class ToolPermission(StrEnum):
    READ_ONLY = "read_only"
    DRAFT_ONLY = "draft_only"
    APPROVAL_REQUIRED = "approval_required"
    FORBIDDEN = "forbidden"


ALLOWED_SHADOW_PERMISSIONS = {ToolPermission.READ_ONLY, ToolPermission.DRAFT_ONLY}


@dataclass
class ToolDefinition:
    name: str
    permission: ToolPermission
    input_schema_name: str
    output_schema_name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]


@dataclass
class ToolRequest:
    tool_name: str
    requested_by_agent: str
    input_payload: dict[str, Any]


@dataclass
class ToolDecision:
    allowed: bool
    permission: ToolPermission
    reason: str

    def model_dump(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "permission": self.permission.value,
            "reason": self.reason,
        }


@dataclass
class ToolExecutionResult:
    decision: ToolDecision
    output_payload: dict[str, Any]
    tool_call: AgentToolCall


class ToolRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        self._definitions[definition.name] = definition

    def request(
        self,
        run_id: str,
        step_id: str,
        request: ToolRequest,
    ) -> ToolExecutionResult:
        definition = self._definitions[request.tool_name]
        allowed = definition.permission in ALLOWED_SHADOW_PERMISSIONS
        reason = (
            f"tool permission {definition.permission.value} is allowed for shadow orchestration"
            if allowed
            else f"tool permission {definition.permission.value} is denied in shadow orchestration"
        )
        decision = ToolDecision(allowed=allowed, permission=definition.permission, reason=reason)
        output_payload = definition.handler(request.input_payload) if allowed else {}
        tool_call = AgentToolCall(
            tool_call_id=f"{run_id}:{step_id}:{request.tool_name}",
            run_id=run_id,
            step_id=step_id,
            tool_name=request.tool_name,
            input_payload={
                "requested_by_agent": request.requested_by_agent,
                "payload": request.input_payload,
            },
            output_payload={
                **output_payload,
                "permission_decision": decision.model_dump(),
            },
            status="success" if allowed else "failed",
            latency_ms=0,
            error_summary=None if allowed else reason,
        )
        return ToolExecutionResult(
            decision=decision,
            output_payload=output_payload,
            tool_call=tool_call,
        )
