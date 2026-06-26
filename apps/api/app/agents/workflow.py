from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.schemas import AgentDraft, AgentEvaluation, AgentModelCall, AgentStep, AgentToolCall


@dataclass
class WorkflowState:
    run_id: str
    event_id: str
    trigger: str
    input_refs: list[str]
    snapshots: dict[str, Any] = field(default_factory=dict)
    steps: list[AgentStep] = field(default_factory=list)
    tool_calls: list[AgentToolCall] = field(default_factory=list)
    drafts: list[AgentDraft] = field(default_factory=list)
    model_calls: list[AgentModelCall] = field(default_factory=list)
    evaluations: list[AgentEvaluation] = field(default_factory=list)
    advisory_bundle: dict[str, Any] | None = None


@dataclass
class WorkflowNodeResult:
    step_id: str
    agent_name: str
    objective: str
    structured_output: dict[str, Any]
    decision_reason: str
    confidence: float
    requires_human_approval: bool
    input_refs: list[str] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call_refs: list[str] = field(default_factory=list)
    model_call_ref: str | None = None
    schema_name: str | None = None
    validation_status: str = "passed"


@dataclass
class WorkflowNode:
    node_id: str
    run: Callable[[WorkflowState], WorkflowNodeResult]


@dataclass
class WorkflowSpec:
    workflow_id: str
    trigger: str
    nodes: list[WorkflowNode]
    edges: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class WorkflowExecutionResult:
    steps: list[AgentStep]
    tool_calls: list[AgentToolCall]
    drafts: list[AgentDraft]
    model_calls: list[AgentModelCall]
    evaluations: list[AgentEvaluation]
    advisory_bundle: dict[str, Any] | None


class WorkflowExecutor:
    def execute(self, spec: WorkflowSpec, state: WorkflowState) -> WorkflowExecutionResult:
        for node in spec.nodes:
            node_result = node.run(state)
            step = AgentStep(
                step_id=node_result.step_id,
                run_id=state.run_id,
                agent_name=node_result.agent_name,
                objective=node_result.objective,
                input_refs=node_result.input_refs or state.input_refs,
                tool_calls=node_result.tool_calls,
                tool_call_refs=node_result.tool_call_refs,
                structured_output=node_result.structured_output,
                decision_reason=node_result.decision_reason,
                confidence=node_result.confidence,
                requires_human_approval=node_result.requires_human_approval,
                model_call_ref=node_result.model_call_ref,
                schema_name=node_result.schema_name or "QwenPawShadowWorkflow",
                validation_status=node_result.validation_status,
            )
            state.steps.append(step)

            advisory_bundle = node_result.structured_output.get("advisory_bundle")
            if isinstance(advisory_bundle, dict):
                state.advisory_bundle = advisory_bundle

        return WorkflowExecutionResult(
            steps=state.steps,
            tool_calls=state.tool_calls,
            drafts=state.drafts,
            model_calls=state.model_calls,
            evaluations=state.evaluations,
            advisory_bundle=state.advisory_bundle,
        )
