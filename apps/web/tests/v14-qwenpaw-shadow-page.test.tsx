import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { afterEach, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { OrganizerExceptionCenterPage } from "../src/pages/organizer/OrganizerExceptionCenterPage";

const mockApi = vi.hoisted(() => ({
  getIncidents: vi.fn(),
  getAgentRuns: vi.fn(),
  getAgentDrafts: vi.fn(),
  getAgentToolCalls: vi.fn(),
  getAgentModelCalls: vi.fn(),
  getAgentEvaluations: vi.fn(),
  getOperationSuggestions: vi.fn(),
  approveOperationSuggestion: vi.fn(),
  generateOperationSuggestions: vi.fn(),
  createRecoveryProposal: vi.fn(),
  approveRecoveryProposal: vi.fn(),
  runQwenPawShadowOrchestration: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

function setupExceptionCenter() {
  mockApi.getIncidents.mockResolvedValue([
    {
      incident_id: "incident_demo_m001_inventory",
      event_id: "demo-night-tour",
      type: "inventory",
      severity: "high",
      source: "merchant",
      trigger_detail: "Merchant m001 reported sold out.",
      affected_route_points: ["rp001"],
      affected_merchants: ["m001"],
      status: "proposal_ready",
      created_at: "2026-06-21T00:00:00Z"
    }
  ]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentDrafts.mockResolvedValue([]);
  mockApi.getAgentToolCalls.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);
  mockApi.getOperationSuggestions.mockResolvedValue({ suggestions: [] });
}

afterEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

test("organizer can run QwenPaw shadow orchestration for the selected incident", async () => {
  setupExceptionCenter();
  mockApi.runQwenPawShadowOrchestration.mockResolvedValue({
    agent_run: {
      run_id: "run_demo-night-tour_qwenpaw_shadow_incident_demo_m001_inventory",
      event_id: "demo-night-tour",
      trigger: "incident_recovery",
      mode: "qwenpaw_workflow",
      status: "completed",
      started_at: "2026-06-21T00:00:00Z",
      completed_at: "2026-06-21T00:00:01Z",
      fallback_used: false,
      fallback_reason: null,
      final_output_ref: "qwenpaw_shadow_advisory:demo-night-tour:incident_demo_m001_inventory",
      error_summary: null
    },
    advisory_bundle: {
      authoritative_mutation: false,
      human_approval_required: true
    },
    steps: [],
    permission_decisions: [
      {
        allowed: false,
        permission: "approval_required",
        reason: "mutation denied"
      }
    ]
  });

  renderWithI18n(<OrganizerExceptionCenterPage eventId="demo-night-tour" />);

  const button = await screen.findByRole("button", { name: /run shadow orchestration/i });
  fireEvent.click(button);

  await waitFor(() => {
    expect(mockApi.runQwenPawShadowOrchestration).toHaveBeenCalledWith(
      "demo-night-tour",
      "incident_demo_m001_inventory"
    );
  });
  expect(await screen.findByText(/qwenpaw shadow orchestration/i)).toBeInTheDocument();
  expect(screen.getByText(/advisory only/i)).toBeInTheDocument();
  expect(screen.getByText(/requires organizer approval/i)).toBeInTheDocument();
  expect(screen.getByText(/no authoritative mutation/i)).toBeInTheDocument();
  expect(screen.getByText(/permission decisions/i)).toBeInTheDocument();
});

test("organizer sees fallback shadow orchestration status", async () => {
  setupExceptionCenter();
  mockApi.runQwenPawShadowOrchestration.mockResolvedValue({
    agent_run: {
      run_id: "run_demo-night-tour_qwenpaw_shadow_incident_demo_m001_inventory",
      event_id: "demo-night-tour",
      trigger: "incident_recovery",
      mode: "qwenpaw_workflow",
      status: "fallback_completed",
      started_at: "2026-06-21T00:00:00Z",
      completed_at: "2026-06-21T00:00:01Z",
      fallback_used: true,
      fallback_reason: "missing_live_provider",
      final_output_ref: "qwenpaw_shadow_advisory:demo-night-tour:incident_demo_m001_inventory",
      error_summary: null
    },
    advisory_bundle: {
      authoritative_mutation: false,
      human_approval_required: true
    },
    steps: [],
    permission_decisions: []
  });

  renderWithI18n(<OrganizerExceptionCenterPage eventId="demo-night-tour" />);
  fireEvent.click(await screen.findByRole("button", { name: /run shadow orchestration/i }));

  expect(await screen.findByText(/fallback used/i)).toBeInTheDocument();
});
