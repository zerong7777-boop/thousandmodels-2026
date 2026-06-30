import { render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { OrganizerEventWorkspacePage } from "../src/pages/organizer/OrganizerEventWorkspacePage";
import type { EventMerchantSetupSummary, EventSummary } from "../src/types";

const mockApi = vi.hoisted(() => ({
  getEvent: vi.fn(),
  getPlanVersions: vi.fn(),
  getAgentTraces: vi.fn(),
  getMerchantTasks: vi.fn(),
  getAgentRuns: vi.fn(),
  getAgentToolCalls: vi.fn(),
  getAgentModelCalls: vi.fn(),
  getAgentEvaluations: vi.fn(),
  getEventPage: vi.fn(),
  getMerchantEdgePackages: vi.fn(),
  generatePlan: vi.fn(),
  approvePlanVersion: vi.fn(),
  draftEventPage: vi.fn(),
  publishEventPage: vi.fn(),
  generateMerchantEdgePackages: vi.fn(),
  getEventOperationsSummary: vi.fn(),
  generateOperationSuggestions: vi.fn(),
  getMerchants: vi.fn(),
  getEventMerchantRoster: vi.fn(),
  replaceEventMerchantRoster: vi.fn(),
  updateEventMerchantParticipant: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

function eventSummary(): EventSummary {
  return {
    event_id: "v31-harbor-fair",
    title: "V31 Harbor Fair",
    area: "Inner Harbor",
    date: "2026-10-10",
    time_window: "18:00-21:00",
    status: "pending_approval",
    current_plan_version: 1,
    public_release_status: "draft"
  };
}

function readyRoster(): EventMerchantSetupSummary {
  return {
    event_id: "v31-harbor-fair",
    participants: [],
    total_count: 2,
    ready_count: 2,
    needs_setup_count: 0,
    missing_count: 0,
    declined_count: 0,
    ready_for_planning: true
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getEvent.mockResolvedValue(eventSummary());
  mockApi.getPlanVersions.mockResolvedValue([
    {
      plan_id: "v31-harbor-fair:v1",
      event_id: "v31-harbor-fair",
      version: 1,
      status: "draft",
      created_by: "OrchestratorAgent",
      created_reason: "initial_plan",
      route_points: [],
      merchant_assignments: ["m900", "m901"],
      budget_plan: {},
      risk_plan: [],
      diff_from_previous: [],
      merchant_fit: [
        {
          merchant_id: "m900",
          score: 86,
          fit_level: "strong",
          matched_signals: ["matches family", "operating window covers the event"],
          warnings: [],
          rationale: "Harbor Tea Lab is a strong fit with score 86."
        },
        {
          merchant_id: "m901",
          score: 48,
          fit_level: "weak",
          matched_signals: [],
          warnings: ["contact owner is missing", "weak merchant fit for this event brief"],
          rationale: "Snack Kiosk is a weak fit with score 48."
        }
      ],
      planner_warnings: ["m901: contact owner is missing"]
    }
  ]);
  mockApi.getAgentTraces.mockResolvedValue([]);
  mockApi.getMerchantTasks.mockResolvedValue([]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentToolCalls.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);
  mockApi.getEventPage.mockRejectedValue(new Error("event page not drafted"));
  mockApi.getMerchantEdgePackages.mockResolvedValue({ packages: [] });
  mockApi.generatePlan.mockResolvedValue({ current_plan: { version: 1, status: "draft" } });
  mockApi.approvePlanVersion.mockResolvedValue({ version: 1, status: "approved" });
  mockApi.draftEventPage.mockResolvedValue(null);
  mockApi.publishEventPage.mockResolvedValue(null);
  mockApi.generateMerchantEdgePackages.mockResolvedValue({ packages: [] });
  mockApi.getEventOperationsSummary.mockResolvedValue(null);
  mockApi.generateOperationSuggestions.mockResolvedValue({ suggestions: [] });
  mockApi.getMerchants.mockResolvedValue([]);
  mockApi.getEventMerchantRoster.mockResolvedValue(readyRoster());
});

afterEach(() => {
  localStorage.clear();
});

test("organizer workspace renders planner warnings and merchant fit rationales", async () => {
  renderWithI18n(<OrganizerEventWorkspacePage eventId="v31-harbor-fair" />);

  expect(await screen.findByText("Planner warnings")).toBeInTheDocument();
  expect(screen.getByText("m901: contact owner is missing")).toBeInTheDocument();
  expect(screen.getByText(/Harbor Tea Lab is a strong fit/i)).toBeInTheDocument();
  expect(screen.getAllByText(/score 86/i).length).toBeGreaterThan(0);
});
