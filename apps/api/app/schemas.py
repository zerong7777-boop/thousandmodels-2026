from typing import Literal

from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float
    lng: float
    label: str


class EventBrief(BaseModel):
    event_id: str
    area: str
    date: str
    time_window: str
    budget_mop: int = Field(gt=0)
    target_audience: list[str]
    event_goal: str
    theme_preferences: list[str]
    constraints: list[str]
    priority_rules: list[str]


class MerchantProfile(BaseModel):
    merchant_id: str
    name: str
    type: str
    location: Location
    opening_hours: str
    capacity_level: Literal["low", "medium", "high"]
    signature_products: list[str]
    story: str
    suitable_activity_types: list[str]
    rainy_day_score: int = Field(ge=1, le=5)
    night_score: int = Field(ge=1, le=5)
    constraints: list[str]


class MerchantRuntimeState(BaseModel):
    merchant_id: str
    inventory_status: Literal["normal", "low", "sold_out"]
    queue_status: Literal["normal", "busy", "overloaded"]
    available_for_visitors: bool
    temporary_note: str = ""
    updated_at: str


class MerchantAssignment(BaseModel):
    merchant_id: str
    role: str
    time_slot: str
    rationale: str


class BudgetPlan(BaseModel):
    total_mop: int
    marketing_mop: int
    merchant_support_mop: int
    staffing_mop: int
    contingency_mop: int


class RiskItem(BaseModel):
    risk_id: str
    level: Literal["low", "medium", "high"]
    description: str
    trigger_condition: str
    mitigation: str


class EventPlan(BaseModel):
    event_id: str
    theme: str
    narrative: str
    route: list[str]
    schedule: list[str]
    merchant_assignments: list[MerchantAssignment]
    budget_plan: BudgetPlan
    marketing_content: list[str]
    risk_plan: list[RiskItem]
    execution_checklist: list[str]
    version: int = 1
    approval_status: Literal["draft", "approved"] = "draft"


class MerchantExecutionPack(BaseModel):
    merchant_id: str
    event_id: str
    role: str
    time_slot: str
    visitor_task: str
    preparation_items: list[str]
    promo_text: str
    fallback_instruction: str


class RecoveryAction(BaseModel):
    action_id: str
    event_id: str
    trigger_type: Literal["inventory", "weather"]
    trigger_detail: str
    recommended_changes: list[str]
    affected_merchants: list[str]
    tourist_notification: str
    merchant_notification: str
    requires_approval: bool = True
    approval_status: Literal["pending", "approved", "rejected"] = "pending"


class ReviewReport(BaseModel):
    event_id: str
    summary: str
    route_result: str
    merchant_result: str
    incident_summary: str
    agent_actions: list[str]
    human_approvals: list[str]
    lessons_learned: list[str]
    next_event_recommendations: list[str]


class AuditLog(BaseModel):
    log_id: str
    event_id: str
    actor_type: Literal["organizer", "merchant", "agent", "tool", "system"]
    actor_id: str
    action_type: str
    input_ref: str = ""
    output_ref: str = ""
    timestamp: str
    note: str


class PublicEvent(BaseModel):
    event_id: str
    theme: str
    route: list[str]
    marketing_content: list[str]
    notices: list[str]
    checkin_tasks: list[str]


class InventoryTriggerRequest(BaseModel):
    merchant_id: str = "m001"


class RuntimeStateUpdate(BaseModel):
    inventory_status: Literal["normal", "low", "sold_out"] | None = None
    queue_status: Literal["normal", "busy", "overloaded"] | None = None
    available_for_visitors: bool | None = None
    temporary_note: str | None = None


class EventSummary(BaseModel):
    event_id: str
    title: str
    area: str
    date: str
    time_window: str
    status: Literal["draft", "pending_approval", "active", "ended"]
    current_plan_version: int
    public_release_status: Literal["draft", "published", "stale"]


class RoutePoint(BaseModel):
    point_id: str
    name: str
    type: str
    is_indoor: bool
    estimated_stay_minutes: int = Field(gt=0)
    story: str
    linked_merchants: list[str]
    visitor_task: str
    rainy_day_score: int = Field(ge=1, le=5)
    crowd_risk: Literal["low", "medium", "high"]
    current_status: Literal["active", "paused", "replaced"]


class PlanVersion(BaseModel):
    plan_id: str
    event_id: str
    version: int = Field(ge=1)
    status: Literal["draft", "approved", "superseded"]
    created_by: str
    created_reason: str
    route_points: list[RoutePoint]
    merchant_assignments: list[str]
    budget_plan: dict
    risk_plan: list[str]
    diff_from_previous: list[str]
    approved_by: str | None = None
    approved_at: str | None = None


class MerchantTask(BaseModel):
    task_id: str
    event_id: str
    merchant_id: str
    plan_version: int
    role: str
    time_slot: str
    visitor_task: str
    preparation_items: list[str]
    promo_text: str
    fallback_instruction: str
    task_status: Literal["draft", "active", "paused", "replaced", "completed"]


class Incident(BaseModel):
    incident_id: str
    event_id: str
    type: Literal["inventory", "queue", "weather", "merchant_unavailable"]
    severity: Literal["low", "medium", "high"]
    source: Literal["merchant", "weather_tool", "organizer", "system"]
    trigger_detail: str
    affected_route_points: list[str]
    affected_merchants: list[str]
    status: Literal["open", "proposal_ready", "approved", "closed"]
    created_at: str


class RecoveryProposal(BaseModel):
    proposal_id: str
    incident_id: str
    event_id: str
    recommended_changes: list[str]
    plan_patch: dict
    merchant_task_patch: dict
    public_notice_patch: str
    impact_summary: str
    requires_approval: bool = True
    approval_status: Literal["pending", "approved", "rejected"] = "pending"


class PublicNotice(BaseModel):
    notice_id: str
    event_id: str
    plan_version: int
    audience: Literal["tourist", "merchant", "organizer"]
    message: str
    reason: str
    publish_status: Literal["draft", "published"]
    published_at: str | None = None


AgentTrigger = Literal[
    "planning_generation",
    "incident_recovery",
    "public_notice_draft",
    "review_generation",
]
AgentMode = Literal["deterministic", "qwen_draft", "qwenpaw_workflow"]
AgentRunStatus = Literal["running", "completed", "failed", "fallback_completed"]
AgentValidationStatus = Literal["passed", "failed", "fallback"]
AgentToolStatus = Literal["success", "failed"]
AgentDraftType = Literal[
    "plan_candidate",
    "route_story",
    "recovery_explanation",
    "public_notice",
    "review_summary",
]
AgentDraftStatus = Literal["draft", "accepted", "rejected", "superseded"]
AgentDraftLocale = Literal["zh-Hans", "zh-Hant", "en", "mixed"]
AgentModelProvider = Literal["deterministic", "dashscope"]
AgentModelResponseStatus = Literal[
    "skipped",
    "success",
    "invalid_json",
    "schema_failed",
    "provider_error",
]


class AgentRun(BaseModel):
    run_id: str
    event_id: str
    trigger: AgentTrigger
    mode: AgentMode
    status: AgentRunStatus
    started_at: str
    completed_at: str | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    final_output_ref: str | None = None
    error_summary: str | None = None


class AgentToolCall(BaseModel):
    tool_call_id: str
    run_id: str
    step_id: str
    tool_name: str
    input_payload: dict
    output_payload: dict
    status: AgentToolStatus
    latency_ms: int | None = None
    error_summary: str | None = None


class AgentDraft(BaseModel):
    draft_id: str
    event_id: str
    source_run_id: str
    draft_type: AgentDraftType
    locale: AgentDraftLocale
    content: str
    structured_payload: dict
    status: AgentDraftStatus = "draft"
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    created_at: str


class AgentModelCall(BaseModel):
    model_call_id: str
    run_id: str
    provider: AgentModelProvider
    model: str
    prompt_template_id: str
    input_refs: list[str]
    response_status: AgentModelResponseStatus
    parsed_output: dict | None = None
    fallback_used: bool = False
    error_summary: str | None = None
    created_at: str


class AgentEvaluation(BaseModel):
    evaluation_id: str
    run_id: str
    schema_pass: bool
    fallback_used: bool
    unsafe_mutation_attempted: bool
    human_approval_required: bool
    forbidden_public_terms_present: bool
    public_copy_ready: bool
    notes: list[str] = Field(default_factory=list)


class AgentStep(BaseModel):
    agent_name: str
    input_refs: list[str]
    tool_calls: list[dict]
    structured_output: dict
    decision_reason: str
    confidence: float = Field(ge=0, le=1)
    requires_human_approval: bool
    step_id: str | None = None
    run_id: str | None = None
    objective: str | None = None
    tool_call_refs: list[str] = Field(default_factory=list)
    model_call_ref: str | None = None
    schema_name: str | None = None
    validation_status: AgentValidationStatus = "passed"


class AgentTrace(BaseModel):
    trace_id: str
    event_id: str
    trigger: str
    steps: list[AgentStep]
    final_output_ref: str
    human_decision_ref: str | None = None


class OperationalMetric(BaseModel):
    metric_id: str
    event_id: str
    name: str
    value: float
    unit: str
    source: Literal["mock", "system", "merchant", "public_h5"]
    captured_at: str


class AuthUserRecord(BaseModel):
    user_id: str
    username: str
    password_hash: str
    role: Literal["organizer", "merchant", "tourist"]
    display_name: str
    merchant_id: str | None = None
    status: Literal["active", "disabled"] = "active"
    created_at: str


class AuthSessionRecord(BaseModel):
    session_id: str
    token_hash: str
    user_id: str
    created_at: str
    expires_at: str
    revoked_at: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthUserResponse(BaseModel):
    user_id: str
    username: str
    role: Literal["organizer", "merchant", "tourist"]
    display_name: str
    merchant_id: str | None = None


class AuthResponse(BaseModel):
    user: AuthUserResponse
