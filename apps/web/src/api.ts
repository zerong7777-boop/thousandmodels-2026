import type {
  AuditLog,
  AgentDraft,
  AgentDraftType,
  AgentEvaluation,
  AgentModelCall,
  AgentRun,
  AgentTrace,
  AgentToolCall,
  ApproveRecoveryResponse,
  CouponRedemption,
  EventPage,
  EventPlan,
  EventSummary,
  GeneratePlanResponse,
  Incident,
  MerchantEdgePackagesResponse,
  MerchantPack,
  MerchantTask,
  MerchantWorkbench,
  MerchantRuntimeState,
  OperationSuggestion,
  OperationSuggestionsResponse,
  PlanVersion,
  PublicEvent,
  PublicEventV2,
  RecoveryAction,
  RecoveryProposal,
  RuntimeStateUpdateResponse,
  ReviewReport,
  ShadowOrchestrationResponse,
  TouchpointInteraction
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const MUTATION_HEADERS = { "Content-Type": "application/json", "X-Zhiyin-CSRF": "demo" };
const READ_OPTIONS = { credentials: "include" as const };

const mutationOptions = (body?: unknown): RequestInit => ({
  method: "POST",
  credentials: "include",
  headers: MUTATION_HEADERS,
  ...(body === undefined ? {} : { body: JSON.stringify(body) })
});

const json = async <T,>(request: Promise<Response>): Promise<T> => {
  const response = await request;
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
};

export const api = {
  seed: () =>
    json<{ status: string; event_id: string }>(
      fetch(`${API_BASE}/api/events/demo/seed`, mutationOptions())
    ),
  getEvents: () => json<EventSummary[]>(fetch(`${API_BASE}/api/events`, READ_OPTIONS)),
  getEvent: (eventId = "demo-night-tour") =>
    json<EventSummary>(fetch(`${API_BASE}/api/events/${eventId}`, READ_OPTIONS)),
  generatePlan: (eventId = "demo-night-tour") =>
    json<GeneratePlanResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/generate-plan`, mutationOptions())
    ),
  approvePlan: (eventId = "demo-night-tour") =>
    json<EventPlan>(fetch(`${API_BASE}/api/events/${eventId}/approve-plan`, mutationOptions())),
  approvePlanVersion: (eventId: string, version: number) =>
    json<PlanVersion>(
      fetch(`${API_BASE}/api/events/${eventId}/plans/${version}/approve`, mutationOptions())
    ),
  getPlan: (eventId = "demo-night-tour") =>
    json<EventPlan>(fetch(`${API_BASE}/api/events/${eventId}/plan`, READ_OPTIONS)),
  getCurrentPlan: (eventId: string) =>
    json<PlanVersion>(fetch(`${API_BASE}/api/events/${eventId}/plans/current`, READ_OPTIONS)),
  getPlanVersions: (eventId: string) =>
    json<PlanVersion[]>(fetch(`${API_BASE}/api/events/${eventId}/plans`, READ_OPTIONS)),
  getAgentTraces: (eventId: string) =>
    json<AgentTrace[]>(fetch(`${API_BASE}/api/events/${eventId}/agent-traces`, READ_OPTIONS)),
  getAgentRuns: (eventId: string) =>
    json<AgentRun[]>(fetch(`${API_BASE}/api/events/${eventId}/agent-runs`, READ_OPTIONS)),
  getAgentDrafts: (eventId: string, draftType?: AgentDraftType) => {
    const query = draftType ? `?draft_type=${encodeURIComponent(draftType)}` : "";
    return json<AgentDraft[]>(
      fetch(`${API_BASE}/api/events/${eventId}/agent-drafts${query}`, READ_OPTIONS)
    );
  },
  getAgentToolCalls: (eventId: string, runId: string) =>
    json<AgentToolCall[]>(
      fetch(`${API_BASE}/api/events/${eventId}/agent-runs/${runId}/tool-calls`, READ_OPTIONS)
    ),
  getAgentModelCalls: (eventId: string, runId: string) =>
    json<AgentModelCall[]>(
      fetch(`${API_BASE}/api/events/${eventId}/agent-runs/${runId}/model-calls`, READ_OPTIONS)
    ),
  getAgentEvaluations: (eventId: string, runId: string) =>
    json<AgentEvaluation[]>(
      fetch(`${API_BASE}/api/events/${eventId}/agent-runs/${runId}/evaluations`, READ_OPTIONS)
    ),
  getMerchantTasks: (eventId: string) =>
    json<MerchantTask[]>(fetch(`${API_BASE}/api/events/${eventId}/merchant-tasks`, READ_OPTIONS)),
  getPacks: (eventId = "demo-night-tour") =>
    json<MerchantPack[]>(fetch(`${API_BASE}/api/events/${eventId}/merchant-packs`, READ_OPTIONS)),
  draftEventPage: (eventId: string) =>
    json<EventPage>(
      fetch(`${API_BASE}/api/events/${eventId}/event-page/draft`, mutationOptions())
    ),
  publishEventPage: (eventId: string) =>
    json<EventPage>(
      fetch(`${API_BASE}/api/events/${eventId}/event-page/publish`, mutationOptions())
    ),
  getEventPage: (eventId: string) =>
    json<EventPage>(fetch(`${API_BASE}/api/events/${eventId}/event-page`, READ_OPTIONS)),
  generateMerchantEdgePackages: (eventId: string) =>
    json<MerchantEdgePackagesResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/merchant-edge-packages/generate`, mutationOptions())
    ),
  getMerchantEdgePackages: (eventId: string) =>
    json<MerchantEdgePackagesResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/merchant-edge-packages`, READ_OPTIONS)
    ),
  generateOperationSuggestions: (eventId: string) =>
    json<OperationSuggestionsResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/operation-suggestions/generate`, mutationOptions())
    ),
  getOperationSuggestions: (eventId: string) =>
    json<OperationSuggestionsResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/operation-suggestions`, READ_OPTIONS)
    ),
  approveOperationSuggestion: (eventId: string, suggestionId: string) =>
    json<OperationSuggestion>(
      fetch(
        `${API_BASE}/api/events/${eventId}/operation-suggestions/${suggestionId}/approve`,
        mutationOptions()
      )
    ),
  runQwenPawShadowOrchestration: (eventId: string, incidentId?: string) =>
    json<ShadowOrchestrationResponse>(
      fetch(
        `${API_BASE}/api/events/${eventId}/qwenpaw-shadow-orchestration/run`,
        mutationOptions(incidentId ? { incident_id: incidentId } : {})
      )
    ),
  getRuntimeStates: () =>
    json<MerchantRuntimeState[]>(fetch(`${API_BASE}/api/merchants/runtime-states`, READ_OPTIONS)),
  getMerchantWorkbench: (merchantId: string, eventId = "demo-night-tour") =>
    json<MerchantWorkbench>(
      fetch(`${API_BASE}/api/merchants/${merchantId}/workbench?event_id=${eventId}`, READ_OPTIONS)
    ),
  updateRuntimeState: (
    merchantId: string,
    payload: Partial<Pick<MerchantRuntimeState, "inventory_status" | "queue_status" | "available_for_visitors" | "temporary_note">>
  ) =>
    json<RuntimeStateUpdateResponse>(
      fetch(`${API_BASE}/api/merchants/${merchantId}/runtime-state`, mutationOptions(payload))
    ),
  triggerInventory: () =>
    json<RecoveryAction>(
      fetch(`${API_BASE}/api/events/demo-night-tour/trigger/inventory`, mutationOptions({ merchant_id: "m001" }))
    ),
  triggerWeather: () =>
    json<RecoveryAction>(
      fetch(`${API_BASE}/api/events/demo-night-tour/trigger/weather`, mutationOptions())
    ),
  approveRecovery: (actionId: string) =>
    json<RecoveryAction>(
      fetch(`${API_BASE}/api/recovery-actions/${actionId}/approve`, mutationOptions())
    ),
  getIncidents: (eventId: string) =>
    json<Incident[]>(fetch(`${API_BASE}/api/events/${eventId}/incidents`, READ_OPTIONS)),
  createRecoveryProposal: (eventId: string, incidentId: string) =>
    json<RecoveryProposal>(
      fetch(`${API_BASE}/api/events/${eventId}/incidents/${incidentId}/recovery-proposals`, mutationOptions())
    ),
  approveRecoveryProposal: (eventId: string, proposalId: string) =>
    json<ApproveRecoveryResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/recovery-proposals/${proposalId}/approve`, mutationOptions())
    ),
  getPublicEvent: (eventId = "demo-night-tour") =>
    json<PublicEventV2 & PublicEvent>(fetch(`${API_BASE}/api/public/events/${eventId}`)),
  recordTouchpointInteraction: (
    eventId: string,
    touchpointId: string,
    payload: {
      interaction_type?: TouchpointInteraction["interaction_type"];
      source?: string;
      anonymous_interaction_id?: string;
      metadata?: Record<string, unknown>;
    }
  ) =>
    json<TouchpointInteraction>(
      fetch(
        `${API_BASE}/api/public/events/${eventId}/touchpoints/${touchpointId}/interactions`,
        mutationOptions(payload)
      )
    ),
  claimCoupon: (eventId: string, couponRuleId: string, anonymousInteractionId: string) =>
    json<CouponRedemption>(
      fetch(
        `${API_BASE}/api/public/events/${eventId}/coupons/${couponRuleId}/claim`,
        mutationOptions({ anonymous_interaction_id: anonymousInteractionId })
      )
    ),
  redeemCoupon: (eventId: string, redemptionId: string) =>
    json<CouponRedemption>(
      fetch(
        `${API_BASE}/api/public/events/${eventId}/coupon-redemptions/${redemptionId}/redeem`,
        mutationOptions()
      )
    ),
  generateReport: (eventId = "demo-night-tour") =>
    json<ReviewReport>(
      fetch(`${API_BASE}/api/events/${eventId}/review-report`, mutationOptions())
    ),
  getReviewReport: (eventId: string) =>
    json<ReviewReport>(fetch(`${API_BASE}/api/events/${eventId}/review-report`, READ_OPTIONS)),
  getAuditLogs: (eventId = "demo-night-tour") =>
    json<AuditLog[]>(fetch(`${API_BASE}/api/events/${eventId}/audit-logs`, READ_OPTIONS))
};
