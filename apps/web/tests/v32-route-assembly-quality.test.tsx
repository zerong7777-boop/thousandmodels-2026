import { render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { OrganizerEventWorkspacePage } from "../src/pages/organizer/OrganizerEventWorkspacePage";

const mockApi = vi.hoisted(() => ({
  getPlanVersions: vi.fn(),
  getAgentTraces: vi.fn(),
  getMerchantTasks: vi.fn(),
  getAgentRuns: vi.fn(),
  getAgentToolCalls: vi.fn(),
  getAgentModelCalls: vi.fn(),
  getAgentEvaluations: vi.fn(),
  getEventPage: vi.fn(),
  getMerchantEdgePackages: vi.fn(),
  getEvent: vi.fn(),
  getMerchants: vi.fn(),
  getEventMerchantRoster: vi.fn(),
  generatePlan: vi.fn(),
  approvePlanVersion: vi.fn(),
  draftEventPage: vi.fn(),
  publishEventPage: vi.fn(),
  generateMerchantEdgePackages: vi.fn(),
  getEventOperationsSummary: vi.fn(),
  generateOperationSuggestions: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getEvent.mockResolvedValue({
    event_id: "v32-route",
    title: "V32 Rainy Route",
    area: "Inner Harbor",
    date: "2026-10-10",
    time_window: "18:00-21:00",
    status: "pending_approval",
    current_plan_version: 1,
    public_release_status: "draft"
  });
  mockApi.getPlanVersions.mockResolvedValue([
    {
      plan_id: "v32-route:v1",
      event_id: "v32-route",
      version: 1,
      status: "draft",
      created_by: "OrchestratorAgent",
      created_reason: "initial_plan",
      route_points: [],
      merchant_assignments: ["m930"],
      budget_plan: {},
      risk_plan: [],
      diff_from_previous: [],
      route_fit: [
        {
          point_id: "rp-v32-m930",
          score: 82,
          fit_level: "strong",
          role: "merchant_stop",
          linked_selected_merchants: ["m930"],
          matched_signals: ["linked selected merchant m930"],
          warnings: [],
          rationale: "Harbor Tea Rest Stop is a strong merchant_stop with score 82."
        }
      ],
      route_warnings: ["m999: no route point is linked to this selected merchant"]
    }
  ]);
  mockApi.getAgentTraces.mockResolvedValue([]);
  mockApi.getMerchantTasks.mockResolvedValue([]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentToolCalls.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);
  mockApi.getEventPage.mockRejectedValue(new Error("not found"));
  mockApi.getMerchantEdgePackages.mockResolvedValue({ packages: [] });
  mockApi.getMerchants.mockResolvedValue([]);
  mockApi.getEventMerchantRoster.mockResolvedValue({ ready_for_planning: true, participants: [] });
  mockApi.generatePlan.mockResolvedValue({ current_plan: { version: 1, status: "draft" } });
  mockApi.approvePlanVersion.mockResolvedValue({ version: 1, status: "approved" });
  mockApi.draftEventPage.mockResolvedValue(null);
  mockApi.publishEventPage.mockResolvedValue(null);
  mockApi.generateMerchantEdgePackages.mockResolvedValue({ packages: [] });
  mockApi.getEventOperationsSummary.mockResolvedValue(null);
  mockApi.generateOperationSuggestions.mockResolvedValue({ suggestions: [] });
});

afterEach(() => {
  localStorage.clear();
});

test("organizer workspace renders route assembly warnings and rationales", async () => {
  renderWithI18n(<OrganizerEventWorkspacePage eventId="v32-route" />);

  await waitFor(() => expect(mockApi.getPlanVersions).toHaveBeenCalledWith("v32-route"));
  expect(await screen.findByText("Route warnings")).toBeInTheDocument();
  expect(screen.getByText("m999: no route point is linked to this selected merchant")).toBeInTheDocument();
  expect(screen.getByText(/Harbor Tea Rest Stop is a strong merchant_stop/i)).toBeInTheDocument();
  expect(screen.getAllByText(/Score 82/i).length).toBeGreaterThan(0);
});
