from app.schemas import AgentEvaluation


PUBLIC_FORBIDDEN_TERMS = [
    "PlanVersion",
    "RecoveryProposal",
    "Incident",
    "AgentTrace",
    "AgentRun",
    "AgentDraft",
    "AgentToolCall",
    "AgentModelCall",
    "backend",
    "schema",
    "fallback",
    "Qwen",
    "QwenPaw",
    "deterministic",
    "runtime state",
    "runtime_state",
]


def find_forbidden_public_terms(content: str) -> list[str]:
    lowered = content.lower()
    return [term for term in PUBLIC_FORBIDDEN_TERMS if term.lower() in lowered]


def evaluate_public_copy(
    run_id: str,
    content: str,
    human_approval_required: bool,
    fallback_used: bool,
) -> AgentEvaluation:
    forbidden = find_forbidden_public_terms(content)
    return AgentEvaluation(
        evaluation_id=f"eval_{run_id}_public_copy",
        run_id=run_id,
        schema_pass=bool(content.strip()),
        fallback_used=fallback_used,
        unsafe_mutation_attempted=False,
        human_approval_required=human_approval_required,
        forbidden_public_terms_present=bool(forbidden),
        public_copy_ready=bool(content.strip()) and not forbidden,
        notes=[f"forbidden_terms={','.join(forbidden)}"] if forbidden else ["public copy passed"],
    )


UNSAFE_MUTATION_TERMS = [
    "approval_status",
    "publish_status",
    "approved_by",
    "approved_at",
    "inventory_status",
    "queue_status",
    "available_for_visitors",
    "plan_patch",
    "merchant_task_patch",
    "public_notice.publish_status",
    "create_plan_version",
    "approve_recovery",
    "publish_notice",
]


class UnsafeMutationAttempt(ValueError):
    pass


def find_unsafe_mutation_terms(payload: object) -> list[str]:
    text = str(payload).lower()
    found: list[str] = []
    for term in UNSAFE_MUTATION_TERMS:
        if term.lower() in text:
            found.append(term)
    return found


def assert_no_unsafe_mutation(payload: object) -> None:
    found = find_unsafe_mutation_terms(payload)
    if found:
        raise UnsafeMutationAttempt(",".join(found))
