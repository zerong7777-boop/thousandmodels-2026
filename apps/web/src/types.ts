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
  touchpoint_summary?: Record<string, unknown>;
  merchant_outcomes?: Array<Record<string, unknown>>;
  extension_tasks?: Array<Record<string, unknown>>;
}

export type EventPageStatus = "draft" | "published" | "archived";
export type TouchpointType =
  | "event_page"
  | "in_shop_qr"
  | "coupon"
  | "redemption"
  | "status_report"
  | "display";
export type CouponRuleStatus = "active" | "paused" | "expired";
export type CouponRedemptionStatus = "claimed" | "redeemed" | "expired" | "cancelled";
export type OperationSuggestionStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "applied";
export type OperationSuggestionType =
  | "route_adjustment"
  | "merchant_capacity"
  | "coupon_rebalance"
  | "public_notice"
  | "extension_task";

export interface EventPage {
  id: string;
  event_id: string;
  plan_version: number;
  status: EventPageStatus;
  title: string;
  subtitle: string;
  story_sections: Array<Record<string, unknown>>;
  route_highlights: Array<Record<string, unknown>>;
  merchant_highlights: Array<Record<string, unknown>>;
  notices: Array<Record<string, unknown>>;
  generated_from_run_id?: string | null;
  published_at?: string | null;
  updated_at: string;
}

export interface EventPageProjection {
  id?: string;
  event_id?: string;
  plan_version?: number;
  current_plan_version?: number;
  status?: EventPageStatus;
  title?: string;
  subtitle?: string;
  story_sections?: Array<Record<string, unknown>>;
  route_highlights?: Array<Record<string, unknown>>;
  merchant_highlights?: Array<Record<string, unknown>>;
  notices?: Array<Record<string, unknown>>;
  interaction_status?: Record<string, unknown>;
}

export interface InShopTouchpoint {
  id: string;
  event_id: string;
  merchant_id?: string | null;
  package_id?: string | null;
  touchpoint_type: TouchpointType;
  label: string;
  public_copy: string;
  token: string;
  status: "active" | "paused";
  metrics: Record<string, number>;
  created_at: string;
}

export interface CouponRule {
  id: string;
  event_id: string;
  merchant_id: string;
  package_id: string;
  title: string;
  description: string;
  max_redemptions: number;
  per_anonymous_interaction_limit: number;
  status: CouponRuleStatus;
  created_at: string;
}

export interface MerchantInteractionPackage {
  id: string;
  event_id: string;
  merchant_id: string;
  plan_version: number;
  status: "draft" | "active" | "paused";
  operator_brief: string;
  visitor_pitch: string;
  task_ids: string[];
  touchpoints: InShopTouchpoint[];
  coupon_rules: CouponRule[];
  evidence_refs: string[];
  generated_from_run_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TouchpointInteraction {
  id: string;
  event_id: string;
  touchpoint_id: string;
  merchant_id?: string | null;
  interaction_type: "view" | "scan" | "claim" | "redeem" | "status_check";
  source: string;
  anonymous_interaction_id: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface CouponRedemption {
  id: string;
  event_id: string;
  coupon_rule_id: string;
  merchant_id: string;
  anonymous_interaction_id: string;
  status: CouponRedemptionStatus;
  claimed_at: string;
  redeemed_at?: string | null;
}

export interface OperationSuggestion {
  id: string;
  event_id: string;
  suggestion_type: OperationSuggestionType;
  status: OperationSuggestionStatus;
  title: string;
  rationale: string;
  recommended_actions: Array<Record<string, unknown>>;
  impacted_merchants: string[];
  impacted_route_points: string[];
  evidence_refs: string[];
  agent_run_id?: string | null;
  created_at: string;
  approved_at?: string | null;
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
  | "merchant_edge_package_generation"
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
    id?: string;
    merchant_id: string;
    name: string;
    type?: string;
    category?: string;
  };
  runtime_state?: MerchantRuntimeState;
  tasks: MerchantTask[];
  interaction_package?: MerchantInteractionPackage | null;
  touchpoint_summary?: Record<string, unknown>;
  coupon_summary?: Record<string, unknown>;
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
  event_page?: EventPageProjection;
  merchant_highlights?: Array<Record<string, unknown>>;
}

export interface MerchantEdgePackagesResponse {
  packages: MerchantInteractionPackage[];
  agent_run?: AgentRun;
  agent_trace?: AgentTrace;
}

export interface OperationSuggestionsResponse {
  suggestions: OperationSuggestion[];
}
