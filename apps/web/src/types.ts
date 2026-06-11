export type ApprovalStatus = "draft" | "approved" | "pending" | "rejected";

export type UserRole = "organizer" | "merchant" | "tourist";

export interface AuthUser {
  user_id: string;
  username: string;
  role: UserRole;
  display_name: string;
  merchant_id: string | null;
}

export interface AuthResponse {
  user: AuthUser;
}

export interface BudgetPlan {
  total_mop: number;
  marketing_mop: number;
  merchant_support_mop: number;
  staffing_mop: number;
  contingency_mop: number;
}

export interface MerchantAssignment {
  merchant_id: string;
  role: string;
  time_slot: string;
  rationale: string;
}

export interface RiskItem {
  risk_id: string;
  level: "low" | "medium" | "high";
  description: string;
  trigger_condition: string;
  mitigation: string;
}

export interface EventPlan {
  event_id: string;
  theme: string;
  narrative: string;
  route: string[];
  schedule: string[];
  merchant_assignments: MerchantAssignment[];
  budget_plan: BudgetPlan;
  marketing_content: string[];
  risk_plan: RiskItem[];
  execution_checklist: string[];
  version: number;
  approval_status: "draft" | "approved";
}

export interface MerchantPack {
  merchant_id: string;
  event_id: string;
  role: string;
  time_slot: string;
  visitor_task: string;
  preparation_items: string[];
  promo_text: string;
  fallback_instruction: string;
}

export interface MerchantRuntimeState {
  merchant_id: string;
  inventory_status: "normal" | "low" | "sold_out";
  queue_status: "normal" | "busy" | "overloaded";
  available_for_visitors: boolean;
  temporary_note: string;
  updated_at: string;
}

export interface RecoveryAction {
  action_id: string;
  event_id: string;
  trigger_type: "inventory" | "weather";
  trigger_detail: string;
  recommended_changes: string[];
  affected_merchants: string[];
  tourist_notification: string;
  merchant_notification: string;
  requires_approval: boolean;
  approval_status: "pending" | "approved" | "rejected";
}

export interface ReviewReport {
  event_id: string;
  summary: string;
  route_result: string;
  merchant_result: string;
  incident_summary: string;
  agent_actions: string[];
  human_approvals: string[];
  lessons_learned: string[];
  next_event_recommendations: string[];
}

export interface PublicEvent {
  event_id: string;
  theme: string;
  route: string[];
  marketing_content: string[];
  notices: string[];
  checkin_tasks: string[];
}

export interface AuditLog {
  log_id: string;
  event_id: string;
  actor_type: string;
  actor_id: string;
  action_type: string;
  timestamp: string;
  note: string;
}

export interface EventSummary {
  event_id: string;
  title: string;
  area: string;
  date: string;
  time_window: string;
  status: "draft" | "pending_approval" | "active" | "ended";
  current_plan_version: number;
  public_release_status: "draft" | "published" | "stale";
}

export interface RoutePoint {
  point_id: string;
  name: string;
  type: string;
  is_indoor: boolean;
  estimated_stay_minutes: number;
  story: string;
  linked_merchants: string[];
  visitor_task: string;
  rainy_day_score: number;
  crowd_risk: "low" | "medium" | "high";
  current_status: "active" | "paused" | "replaced";
}

export interface PlanVersion {
  plan_id: string;
  event_id: string;
  version: number;
  status: "draft" | "approved" | "superseded";
  created_by: string;
  created_reason: string;
  route_points: RoutePoint[];
  merchant_assignments: string[];
  budget_plan: Record<string, unknown>;
  risk_plan: string[];
  diff_from_previous: string[];
  approved_by?: string | null;
  approved_at?: string | null;
}

export interface MerchantTask {
  task_id: string;
  event_id: string;
  merchant_id: string;
  plan_version: number;
  role: string;
  time_slot: string;
  visitor_task: string;
  preparation_items: string[];
  promo_text: string;
  fallback_instruction: string;
  task_status: "draft" | "active" | "paused" | "replaced" | "completed";
}

export interface Incident {
  incident_id: string;
  event_id: string;
  type: "inventory" | "queue" | "weather" | "merchant_unavailable";
  severity: "low" | "medium" | "high";
  source: "merchant" | "weather_tool" | "organizer" | "system";
  trigger_detail: string;
  affected_route_points: string[];
  affected_merchants: string[];
  status: "open" | "proposal_ready" | "approved" | "closed";
  created_at: string;
}

export interface RecoveryProposal {
  proposal_id: string;
  incident_id: string;
  event_id: string;
  recommended_changes: string[];
  plan_patch: Record<string, unknown>;
  merchant_task_patch: Record<string, unknown>;
  public_notice_patch: string;
  impact_summary: string;
  requires_approval: boolean;
  approval_status: "pending" | "approved" | "rejected";
}

export interface PublicNotice {
  notice_id?: string;
  event_id?: string;
  plan_version?: number;
  audience?: "tourist" | "merchant" | "organizer";
  message: string;
  reason?: string;
  publish_status: "draft" | "published";
  published_at?: string | null;
}

export type AgentRunTrigger =
  | "planning_generation"
  | "incident_recovery"
  | "public_notice_draft"
  | "review_generation";

export type AgentRunMode = "deterministic" | "qwen_draft" | "qwenpaw_workflow";
export type AgentRunStatus = "running" | "completed" | "failed" | "fallback_completed";
export type AgentValidationStatus = "passed" | "failed" | "fallback";
export type AgentToolStatus = "success" | "failed";
export type AgentDraftType =
  | "plan_candidate"
  | "route_story"
  | "recovery_explanation"
  | "public_notice"
  | "review_summary";
export type AgentDraftStatus = "draft" | "accepted" | "rejected" | "superseded";
export type AgentDraftLocale = "zh-Hans" | "zh-Hant" | "en" | "mixed";
export type AgentModelProvider = "deterministic" | "dashscope";
export type AgentModelResponseStatus =
  | "skipped"
  | "success"
  | "invalid_json"
  | "schema_failed"
  | "provider_error";

export interface AgentRun {
  run_id: string;
  event_id: string;
  trigger: AgentRunTrigger;
  mode: AgentRunMode;
  status: AgentRunStatus;
  started_at: string;
  completed_at?: string | null;
  fallback_used: boolean;
  fallback_reason?: string | null;
  final_output_ref?: string | null;
  error_summary?: string | null;
}

export interface AgentToolCall {
  tool_call_id: string;
  run_id: string;
  step_id: string;
  tool_name: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  status: AgentToolStatus;
  latency_ms?: number | null;
  error_summary?: string | null;
}

export interface AgentDraft {
  draft_id: string;
  event_id: string;
  source_run_id: string;
  draft_type: AgentDraftType;
  locale: AgentDraftLocale;
  content: string;
  structured_payload: Record<string, unknown>;
  status: AgentDraftStatus;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at: string;
}

export interface AgentModelCall {
  model_call_id: string;
  run_id: string;
  provider: AgentModelProvider;
  model: string;
  prompt_template_id: string;
  input_refs: string[];
  response_status: AgentModelResponseStatus;
  parsed_output?: Record<string, unknown> | null;
  fallback_used: boolean;
  error_summary?: string | null;
  created_at: string;
}

export interface AgentEvaluation {
  evaluation_id: string;
  run_id: string;
  schema_pass: boolean;
  fallback_used: boolean;
  unsafe_mutation_attempted: boolean;
  human_approval_required: boolean;
  forbidden_public_terms_present: boolean;
  public_copy_ready: boolean;
  notes: string[];
}

export interface AgentStep {
  agent_name: string;
  input_refs: string[];
  tool_calls: Array<Record<string, unknown>>;
  structured_output: Record<string, unknown>;
  decision_reason: string;
  confidence: number;
  requires_human_approval: boolean;
  step_id?: string | null;
  run_id?: string | null;
  objective?: string | null;
  tool_call_refs?: string[];
  model_call_ref?: string | null;
  schema_name?: string | null;
  validation_status?: AgentValidationStatus;
}

export interface AgentTrace {
  trace_id: string;
  event_id: string;
  trigger: string;
  steps: AgentStep[];
  final_output_ref: string;
  human_decision_ref?: string | null;
}

export interface OperationalMetric {
  metric_id: string;
  event_id: string;
  name: string;
  value: number;
  unit: string;
  source: "mock" | "system" | "merchant" | "public_h5";
  captured_at: string;
}

export interface GeneratePlanResponse extends EventPlan {
  current_plan: PlanVersion;
  agent_trace: AgentTrace;
  merchant_tasks: MerchantTask[];
}

export interface MerchantWorkbench {
  merchant?: {
    merchant_id: string;
    name: string;
    type?: string;
    category?: string;
  };
  runtime_state?: MerchantRuntimeState;
  tasks: MerchantTask[];
}

export interface RuntimeStateUpdateResponse extends MerchantRuntimeState {
  runtime_state?: MerchantRuntimeState;
  incident?: Incident | null;
}

export interface ApproveRecoveryResponse {
  proposal: RecoveryProposal;
  current_plan: PlanVersion;
  notice: PublicNotice;
}

export interface PublicEventV2 extends PublicEvent {
  title?: string;
  area?: string;
  status?: string;
  current_plan_version?: number;
  route_points?: RoutePoint[];
  public_notices?: PublicNotice[];
}
