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
  EventCreateRequest,
  EventMerchantParticipantUpdateRequest,
  EventMerchantRosterUpdateRequest,
  EventMerchantSetupSummary,
  EventPage,
  EventPlan,
  EventSummary,
  EventUpdateRequest,
  GeneratePlanResponse,
  Incident,
  MerchantEdgePackagesResponse,
  MerchantAssignedEvent,
  MerchantCreateRequest,
  MerchantDetail,
  MerchantPack,
  MerchantProfile,
  MerchantSetupSubmitRequest,
  MerchantTask,
  MerchantUpdateRequest,
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
const CSRF_HEADER = "X-Zhiyin-CSRF";
const READ_OPTIONS = { credentials: "include" as const };

export const isDemoMode = () => import.meta.env.VITE_DEMO_MODE !== "false";

const getCsrfToken = async (): Promise<string> => {
  if (isDemoMode()) {
    return "demo";
  }
  const response = await fetch(`${API_BASE}/api/auth/csrf`, { credentials: "include" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const payload = (await response.json()) as { csrf_token?: string };
  if (!payload.csrf_token) {
    throw new Error("Missing CSRF token");
  }
  return payload.csrf_token;
};

export const mutationOptions = async (body?: unknown): Promise<RequestInit> => ({
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json", [CSRF_HEADER]: await getCsrfToken() },
  ...(body === undefined ? {} : { body: JSON.stringify(body) })
});

const json = async <T,>(request: Promise<Response>): Promise<T> => {
  const response = await request;
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
};

const postJson = async <T,>(path: string, body?: unknown): Promise<T> =>
  json<T>(fetch(`${API_BASE}${path}`, await mutationOptions(body)));

const putJson = async <T,>(path: string, body?: unknown): Promise<T> => {
  const options = await mutationOptions(body);
  return json<T>(fetch(`${API_BASE}${path}`, { ...options, method: "PUT" }));
};

const patchJson = async <T,>(path: string, body?: unknown): Promise<T> => {
  const options = await mutationOptions(body);
  return json<T>(fetch(`${API_BASE}${path}`, { ...options, method: "PATCH" }));
};

export const api = {
  seed: () =>
    postJson<{ status: string; event_id: string }>("/api/events/demo/seed"),
  getEvents: () => json<EventSummary[]>(fetch(`${API_BASE}/api/events`, READ_OPTIONS)),
  getEvent: (eventId = "demo-night-tour") =>
    json<EventSummary>(fetch(`${API_BASE}/api/events/${eventId}`, READ_OPTIONS)),
  createEvent: (payload: EventCreateRequest) =>
    postJson<EventSummary>("/api/events", payload),
  updateEvent: async (eventId: string, payload: EventUpdateRequest) => {
    const options = await mutationOptions(payload);
    return json<EventSummary>(
      fetch(`${API_BASE}/api/events/${eventId}`, { ...options, method: "PATCH" })
    );
  },
  generatePlan: (eventId = "demo-night-tour") =>
    postJson<GeneratePlanResponse>(`/api/events/${eventId}/generate-plan`),
  approvePlan: (eventId = "demo-night-tour") =>
    postJson<EventPlan>(`/api/events/${eventId}/approve-plan`),
  approvePlanVersion: (eventId: string, version: number) =>
    postJson<PlanVersion>(`/api/events/${eventId}/plans/${version}/approve`),
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
    postJson<EventPage>(`/api/events/${eventId}/event-page/draft`),
  publishEventPage: (eventId: string) =>
    postJson<EventPage>(`/api/events/${eventId}/event-page/publish`),
  getEventPage: (eventId: string) =>
    json<EventPage>(fetch(`${API_BASE}/api/events/${eventId}/event-page`, READ_OPTIONS)),
  generateMerchantEdgePackages: (eventId: string) =>
    postJson<MerchantEdgePackagesResponse>(`/api/events/${eventId}/merchant-edge-packages/generate`),
  getMerchantEdgePackages: (eventId: string) =>
    json<MerchantEdgePackagesResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/merchant-edge-packages`, READ_OPTIONS)
    ),
  generateOperationSuggestions: (eventId: string) =>
    postJson<OperationSuggestionsResponse>(`/api/events/${eventId}/operation-suggestions/generate`),
  getOperationSuggestions: (eventId: string) =>
    json<OperationSuggestionsResponse>(
      fetch(`${API_BASE}/api/events/${eventId}/operation-suggestions`, READ_OPTIONS)
    ),
  approveOperationSuggestion: (eventId: string, suggestionId: string) =>
    postJson<OperationSuggestion>(`/api/events/${eventId}/operation-suggestions/${suggestionId}/approve`),
  runQwenPawShadowOrchestration: (eventId: string, incidentId?: string) =>
    postJson<ShadowOrchestrationResponse>(
      `/api/events/${eventId}/qwenpaw-shadow-orchestration/run`,
      incidentId ? { incident_id: incidentId } : {}
    ),
  getRuntimeStates: () =>
    json<MerchantRuntimeState[]>(fetch(`${API_BASE}/api/merchants/runtime-states`, READ_OPTIONS)),
  getMerchants: () =>
    json<MerchantProfile[]>(fetch(`${API_BASE}/api/merchants`, READ_OPTIONS)),
  getMerchant: (merchantId: string) =>
    json<MerchantDetail>(fetch(`${API_BASE}/api/merchants/${merchantId}`, READ_OPTIONS)),
  createMerchant: (payload: MerchantCreateRequest) =>
    postJson<MerchantDetail>("/api/merchants", payload),
  updateMerchant: (merchantId: string, payload: MerchantUpdateRequest) =>
    patchJson<MerchantDetail>(`/api/merchants/${merchantId}`, payload),
  getEventMerchantRoster: (eventId: string) =>
    json<EventMerchantSetupSummary>(
      fetch(`${API_BASE}/api/events/${eventId}/merchant-roster`, READ_OPTIONS)
    ),
  replaceEventMerchantRoster: (eventId: string, payload: EventMerchantRosterUpdateRequest) =>
    putJson<EventMerchantSetupSummary>(`/api/events/${eventId}/merchant-roster`, payload),
  updateEventMerchantParticipant: (
    eventId: string,
    merchantId: string,
    payload: EventMerchantParticipantUpdateRequest
  ) =>
    patchJson<EventMerchantSetupSummary>(
      `/api/events/${eventId}/merchant-roster/${merchantId}`,
      payload
    ),
  getMyMerchantEvents: () =>
    json<MerchantAssignedEvent[]>(fetch(`${API_BASE}/api/merchants/me/events`, READ_OPTIONS)),
  getMyMerchantEventSetup: (eventId: string) =>
    json<MerchantAssignedEvent>(
      fetch(`${API_BASE}/api/merchants/me/events/${eventId}/setup`, READ_OPTIONS)
    ),
  submitMyMerchantEventSetup: (eventId: string, payload: MerchantSetupSubmitRequest) =>
    patchJson<MerchantAssignedEvent>(`/api/merchants/me/events/${eventId}/setup`, payload),
  getMerchantWorkbench: (merchantId: string, eventId = "demo-night-tour") =>
    json<MerchantWorkbench>(
      fetch(`${API_BASE}/api/merchants/${merchantId}/workbench?event_id=${eventId}`, READ_OPTIONS)
    ),
  updateRuntimeState: (
    merchantId: string,
    payload: Partial<Pick<MerchantRuntimeState, "inventory_status" | "queue_status" | "available_for_visitors" | "temporary_note">>
  ) =>
    postJson<RuntimeStateUpdateResponse>(`/api/merchants/${merchantId}/runtime-state`, payload),
  triggerInventory: () =>
    postJson<RecoveryAction>("/api/events/demo-night-tour/trigger/inventory", { merchant_id: "m001" }),
  triggerWeather: () =>
    postJson<RecoveryAction>("/api/events/demo-night-tour/trigger/weather"),
  approveRecovery: (actionId: string) =>
    postJson<RecoveryAction>(`/api/recovery-actions/${actionId}/approve`),
  getIncidents: (eventId: string) =>
    json<Incident[]>(fetch(`${API_BASE}/api/events/${eventId}/incidents`, READ_OPTIONS)),
  createRecoveryProposal: (eventId: string, incidentId: string) =>
    postJson<RecoveryProposal>(`/api/events/${eventId}/incidents/${incidentId}/recovery-proposals`),
  approveRecoveryProposal: (eventId: string, proposalId: string) =>
    postJson<ApproveRecoveryResponse>(`/api/events/${eventId}/recovery-proposals/${proposalId}/approve`),
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
    postJson<TouchpointInteraction>(
      `/api/public/events/${eventId}/touchpoints/${touchpointId}/interactions`,
      payload
    ),
  claimCoupon: (eventId: string, couponRuleId: string, anonymousInteractionId: string) =>
    postJson<CouponRedemption>(
      `/api/public/events/${eventId}/coupons/${couponRuleId}/claim`,
      { anonymous_interaction_id: anonymousInteractionId }
    ),
  redeemCoupon: (eventId: string, redemptionId: string) =>
    postJson<CouponRedemption>(`/api/public/events/${eventId}/coupon-redemptions/${redemptionId}/redeem`),
  generateReport: (eventId = "demo-night-tour") =>
    postJson<ReviewReport>(`/api/events/${eventId}/review-report`),
  getReviewReport: (eventId: string) =>
    json<ReviewReport>(fetch(`${API_BASE}/api/events/${eventId}/review-report`, READ_OPTIONS)),
  getAuditLogs: (eventId = "demo-night-tour") =>
    json<AuditLog[]>(fetch(`${API_BASE}/api/events/${eventId}/audit-logs`, READ_OPTIONS))
};
