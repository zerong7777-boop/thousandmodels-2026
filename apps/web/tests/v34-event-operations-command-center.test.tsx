import { render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { EventOperationsCommandPanel } from "../src/pages/organizer/EventOperationsCommandPanel";
import { OrganizerEventWorkspacePage } from "../src/pages/organizer/OrganizerEventWorkspacePage";
import type { EventOperationsSummary } from "../src/types";

const mockApi = vi.hoisted(() => ({
  getEventOperationsSummary: vi.fn(),
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
  getMerchants: vi.fn(),
  getEventMerchantRoster: vi.fn(),
  generatePlan: vi.fn(),
  approvePlanVersion: vi.fn(),
  draftEventPage: vi.fn(),
  publishEventPage: vi.fn(),
  generateMerchantEdgePackages: vi.fn(),
  generateOperationSuggestions: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

function operationsSummary(overrides: Partial<EventOperationsSummary> = {}): EventOperationsSummary {
  return {
    event: {
      event_id: "v34-command-center",
      title: "V34 Command Center",
      area: "Inner Harbor",
      date: "2026-10-01",
      time_window: "16:00-21:00",
      status: "active",
      current_plan_version: 1,
      public_release_status: "published"
    },
    overall_status: "blocked",
    blocker_count: 2,
    warning_count: 1,
    checks: [
      {
        check_id: "merchant_setup",
        label: "Merchant setup",
        status: "blocked",
        summary: "1/2 selected merchants are planning-ready.",
        blocking: true,
        evidence_refs: ["event_merchant_roster:v34-command-center"]
      },
      {
        check_id: "incident_queue",
        label: "Incident queue",
        status: "warning",
        summary: "1 active incident should be watched by operations.",
        blocking: false,
        evidence_refs: ["incident:inc-1"]
      }
    ],
    action_items: [
      {
        action_id: "action_merchant_setup",
        label: "1/2 selected merchants are planning-ready.",
        status: "todo",
        severity: "critical",
        target: "Merchant setup",
        evidence_refs: ["event_merchant_roster:v34-command-center"]
      },
      {
        action_id: "action_incident_queue",
        label: "1 active incident should be watched by operations.",
        status: "watch",
        severity: "warning",
        target: "Incident queue",
        evidence_refs: ["incident:inc-1"]
      }
    ],
    timeline: [
      {
        item_id: "audit-2",
        actor_type: "organizer",
        actor_id: "usr_org_demo",
        action_type: "publish_event_page",
        summary: "published event page",
        timestamp: "2026-06-30T11:10:00Z",
        evidence_ref: "audit_log:audit-2"
      },
      {
        item_id: "audit-1",
        actor_type: "agent",
        actor_id: "planner",
        action_type: "generate_plan",
        summary: "generated plan",
        timestamp: "2026-06-30T11:00:00Z",
        evidence_ref: "audit_log:audit-1"
      }
    ],
    incident_summary: { active_count: 1, active_high_count: 0 },
    package_summary: { required_merchant_ids: ["m001", "m002"], active_package_count: 1 },
    notice_summary: { total_count: 0, published_count: 0 },
    ...overrides
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getEventOperationsSummary.mockResolvedValue(operationsSummary());
  mockApi.getEvent.mockResolvedValue({
    event_id: "v34-command-center",
    title: "V34 Command Center",
    area: "Inner Harbor",
    date: "2026-10-01",
    time_window: "16:00-21:00",
    status: "active",
    current_plan_version: 1,
    public_release_status: "published"
  });
  mockApi.getPlanVersions.mockResolvedValue([]);
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
  mockApi.generateOperationSuggestions.mockResolvedValue({ suggestions: [] });
});

afterEach(() => {
  localStorage.clear();
});

test("event operations command panel renders blockers warnings checks actions and timeline", () => {
  renderWithI18n(<EventOperationsCommandPanel summary={operationsSummary()} />);

  expect(screen.getByText("Operations command center")).toBeInTheDocument();
  expect(screen.getAllByText(/blocked/i).length).toBeGreaterThan(0);
  expect(screen.getByText("2")).toBeInTheDocument();
  expect(screen.getByText("1")).toBeInTheDocument();
  expect(screen.getAllByText("Merchant setup").length).toBeGreaterThan(0);
  expect(screen.getAllByText("1/2 selected merchants are planning-ready.").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Incident queue").length).toBeGreaterThan(0);
  expect(screen.getByText("Recent action timeline")).toBeInTheDocument();
  expect(screen.getByText("publish_event_page")).toBeInTheDocument();
  expect(screen.getByText("audit_log:audit-2")).toBeInTheDocument();
});

test("organizer workspace loads event operations summary for selected event", async () => {
  renderWithI18n(<OrganizerEventWorkspacePage eventId="v34-command-center" />);

  await waitFor(() => expect(mockApi.getEventOperationsSummary).toHaveBeenCalledWith("v34-command-center"));
  expect(await screen.findByText("Operations command center")).toBeInTheDocument();
});
