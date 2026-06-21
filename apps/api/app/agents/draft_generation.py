import json
import os
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from app.agents.drafts import (
    build_public_notice_draft,
    build_recovery_explanation_draft,
    build_review_summary_draft,
    now_iso,
)
from app.agents.guards import (
    UnsafeMutationAttempt,
    assert_no_unsafe_mutation,
    evaluate_public_copy,
)
from app.agents.qwen_draft_provider import DashScopeQwenDraftProvider, QwenDraftProvider
from app.schemas import (
    AgentDraft,
    AgentEvaluation,
    AgentModelCall,
    Incident,
    OperationalMetric,
    PublicNotice,
    RecoveryProposal,
)


class UnsafeModelMutationError(ValueError):
    pass


class QwenDraftCandidate(BaseModel):
    content: str = Field(min_length=1)
    locale: Literal["zh-Hans", "zh-Hant", "en", "mixed"]
    structured_payload: dict
    evidence_refs: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


UNSAFE_PROMPT_KEYS = {
    "approval_status",
    "approved_by",
    "plan_patch",
    "merchant_task_patch",
    "publish_status",
    "status_transition",
    "approved_at",
    "published_at",
}


@dataclass
class CandidateParseResult:
    candidate: QwenDraftCandidate | None
    response_status: str
    error_summary: str | None = None


@dataclass
class DraftGenerationContext:
    run_id: str
    event_id: str
    draft_type: str
    input_refs: list[str]
    incident: Incident | None = None
    proposal_payload: dict | None = None
    metrics: list[OperationalMetric] | None = None
    incidents: list[Incident] | None = None
    notices: list[PublicNotice] | None = None
    proposals: list[RecoveryProposal] | None = None


@dataclass
class DraftGenerationResult:
    draft: AgentDraft
    model_call: AgentModelCall | None
    evaluation: AgentEvaluation | None
    fallback_used: bool
    fallback_reason: str | None


class DeterministicDraftGenerator:
    mode = "deterministic"

    def generate_recovery_explanation(
        self, context: DraftGenerationContext
    ) -> DraftGenerationResult:
        assert context.incident is not None
        draft = build_recovery_explanation_draft(
            context.run_id,
            context.incident,
            context.proposal_payload or {},
        )
        return DraftGenerationResult(
            draft=draft,
            model_call=None,
            evaluation=None,
            fallback_used=False,
            fallback_reason=None,
        )

    def generate_public_notice(self, context: DraftGenerationContext) -> DraftGenerationResult:
        assert context.incident is not None
        draft = build_public_notice_draft(
            context.run_id,
            context.incident,
            context.proposal_payload or {},
        )
        evaluation = evaluate_public_copy(
            run_id=context.run_id,
            content=draft.content,
            human_approval_required=True,
            fallback_used=False,
        )
        return DraftGenerationResult(
            draft=draft,
            model_call=None,
            evaluation=evaluation,
            fallback_used=False,
            fallback_reason=None,
        )

    def generate_review_summary(self, context: DraftGenerationContext) -> DraftGenerationResult:
        draft = build_review_summary_draft(
            run_id=context.run_id,
            event_id=context.event_id,
            metrics=context.metrics or [],
            incidents=context.incidents or [],
            notices=context.notices or [],
            proposals=context.proposals or [],
        )
        return DraftGenerationResult(
            draft=draft,
            model_call=None,
            evaluation=None,
            fallback_used=False,
            fallback_reason=None,
        )


def reject_unsafe_mutation(payload: object) -> None:
    try:
        assert_no_unsafe_mutation(payload)
    except UnsafeMutationAttempt as exc:
        raise UnsafeModelMutationError(str(exc)) from exc


def sanitize_qwen_prompt_payload(payload: object) -> object:
    if isinstance(payload, dict):
        sanitized: dict = {}
        for key, value in payload.items():
            normalized_key = key.lower() if isinstance(key, str) else key
            if key in UNSAFE_PROMPT_KEYS or normalized_key in UNSAFE_PROMPT_KEYS:
                continue
            sanitized[key] = sanitize_qwen_prompt_payload(value)
        return sanitized
    if isinstance(payload, list):
        return [sanitize_qwen_prompt_payload(item) for item in payload]
    return payload


def normalize_qwen_candidate_payload(parsed: object) -> object:
    if (
        isinstance(parsed, dict)
        and set(parsed.keys()) == {"agent_draft"}
        and isinstance(parsed["agent_draft"], dict)
    ):
        return parsed["agent_draft"]
    return parsed


def parse_qwen_candidate(raw: str) -> CandidateParseResult:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return CandidateParseResult(None, "invalid_json", f"JSON parse failed: {exc.msg}")
    normalized = normalize_qwen_candidate_payload(parsed)
    if isinstance(parsed, dict) and "agent_draft" in parsed and normalized is parsed:
        return CandidateParseResult(
            None,
            "schema_failed",
            "ambiguous agent_draft wrapper must not include top-level candidate fields",
        )
    try:
        reject_unsafe_mutation(normalized)
        return CandidateParseResult(QwenDraftCandidate.model_validate(normalized), "success", None)
    except UnsafeModelMutationError as exc:
        return CandidateParseResult(None, "schema_failed", f"unsafe mutation fields: {exc}")
    except ValidationError as exc:
        return CandidateParseResult(None, "schema_failed", str(exc))


class QwenDraftGenerator:
    mode = "qwen_draft"

    def __init__(self, provider: QwenDraftProvider | None = None):
        self.provider = provider
        self.model = os.getenv("QWEN_MODEL", "qwen-plus")
        self.fallback = DeterministicDraftGenerator()

    def _model_call(
        self,
        run_id: str,
        prompt_template_id: str,
        input_refs: list[str],
        response_status: str,
        parsed_output: dict | None,
        fallback_used: bool,
        error_summary: str | None,
    ) -> AgentModelCall:
        return AgentModelCall(
            model_call_id=f"model_{run_id}_{prompt_template_id}",
            run_id=run_id,
            provider="dashscope",
            model=self.model,
            prompt_template_id=prompt_template_id,
            input_refs=input_refs,
            response_status=response_status,
            parsed_output=parsed_output,
            fallback_used=fallback_used,
            error_summary=error_summary,
            created_at=now_iso(),
        )

    def _fallback_result(
        self,
        context: DraftGenerationContext,
        prompt_template_id: str,
        response_status: str,
        fallback_reason: str,
        error_summary: str | None,
        fallback_method,
    ) -> DraftGenerationResult:
        deterministic = fallback_method(context)
        deterministic.model_call = self._model_call(
            run_id=context.run_id,
            prompt_template_id=prompt_template_id,
            input_refs=context.input_refs,
            response_status=response_status,
            parsed_output=None,
            fallback_used=True,
            error_summary=error_summary,
        )
        deterministic.fallback_used = True
        deterministic.fallback_reason = fallback_reason
        if deterministic.evaluation:
            deterministic.evaluation.fallback_used = True
        return deterministic

    def _draft_from_candidate(
        self,
        context: DraftGenerationContext,
        candidate: QwenDraftCandidate,
    ) -> AgentDraft:
        return AgentDraft(
            draft_id=f"draft_{context.run_id}_{context.draft_type}",
            event_id=context.event_id,
            source_run_id=context.run_id,
            draft_type=context.draft_type,
            locale=candidate.locale,
            content=candidate.content,
            structured_payload={
                **candidate.structured_payload,
                "evidence_refs": candidate.evidence_refs,
            },
            status="draft",
            reviewed_by=None,
            reviewed_at=None,
            created_at=now_iso(),
        )

    def _provider(self) -> QwenDraftProvider:
        return self.provider or DashScopeQwenDraftProvider()

    def _generate(
        self,
        context: DraftGenerationContext,
        prompt_template_id: str,
        fallback_method,
    ) -> DraftGenerationResult:
        if not os.getenv("DASHSCOPE_API_KEY"):
            return self._fallback_result(
                context=context,
                prompt_template_id=prompt_template_id,
                response_status="skipped",
                fallback_reason="missing_provider_key",
                error_summary="DASHSCOPE_API_KEY is not configured",
                fallback_method=fallback_method,
            )
        try:
            payload = sanitize_qwen_prompt_payload(
                {
                    "event_id": context.event_id,
                    "draft_type": context.draft_type,
                    "input_refs": context.input_refs,
                    "incident": context.incident.model_dump() if context.incident else None,
                    "proposal_payload": context.proposal_payload,
                    "metrics": [metric.model_dump() for metric in context.metrics or []],
                    "incidents": [incident.model_dump() for incident in context.incidents or []],
                    "notices": [notice.model_dump() for notice in context.notices or []],
                    "proposals": [proposal.model_dump() for proposal in context.proposals or []],
                }
            )
            raw = self._provider().complete_json(
                prompt_template_id=prompt_template_id,
                payload=payload,
            )
        except Exception as exc:
            return self._fallback_result(
                context=context,
                prompt_template_id=prompt_template_id,
                response_status="provider_error",
                fallback_reason="provider_error",
                error_summary=str(exc)[:240],
                fallback_method=fallback_method,
            )

        parsed = parse_qwen_candidate(raw)
        if parsed.candidate is None:
            return self._fallback_result(
                context=context,
                prompt_template_id=prompt_template_id,
                response_status=parsed.response_status,
                fallback_reason=parsed.response_status,
                error_summary=parsed.error_summary,
                fallback_method=fallback_method,
            )

        draft = self._draft_from_candidate(context, parsed.candidate)
        evaluation = None
        if context.draft_type == "public_notice":
            evaluation = evaluate_public_copy(
                run_id=context.run_id,
                content=draft.content,
                human_approval_required=True,
                fallback_used=False,
            )
            if not evaluation.public_copy_ready:
                return self._fallback_result(
                    context=context,
                    prompt_template_id=prompt_template_id,
                    response_status="schema_failed",
                    fallback_reason="public_copy_guard_failed",
                    error_summary="public copy guard rejected model output",
                    fallback_method=fallback_method,
                )

        return DraftGenerationResult(
            draft=draft,
            model_call=self._model_call(
                run_id=context.run_id,
                prompt_template_id=prompt_template_id,
                input_refs=context.input_refs,
                response_status="success",
                parsed_output=parsed.candidate.model_dump(),
                fallback_used=False,
                error_summary=None,
            ),
            evaluation=evaluation,
            fallback_used=False,
            fallback_reason=None,
        )

    def generate_recovery_explanation(
        self, context: DraftGenerationContext
    ) -> DraftGenerationResult:
        return self._generate(
            context=context,
            prompt_template_id="qwen_recovery_explanation_v1",
            fallback_method=self.fallback.generate_recovery_explanation,
        )

    def generate_public_notice(self, context: DraftGenerationContext) -> DraftGenerationResult:
        return self._generate(
            context=context,
            prompt_template_id="qwen_public_notice_v1",
            fallback_method=self.fallback.generate_public_notice,
        )

    def generate_review_summary(self, context: DraftGenerationContext) -> DraftGenerationResult:
        return self._generate(
            context=context,
            prompt_template_id="qwen_review_summary_v1",
            fallback_method=self.fallback.generate_review_summary,
        )


def choose_draft_generator() -> DeterministicDraftGenerator | QwenDraftGenerator:
    backend = os.getenv("AGENT_DRAFT_BACKEND", "deterministic").lower()
    if backend == "qwen":
        return QwenDraftGenerator(provider=DashScopeQwenDraftProvider())
    return DeterministicDraftGenerator()
