import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { OrganizerEventWorkspacePage } from "../src/pages/organizer/OrganizerEventWorkspacePage";
import type { EventMerchantSetupSummary, EventSummary, MerchantProfile } from "../src/types";

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
    event_id: "v29-harbor-fair",
    title: "V29 Harbor Fair",
    area: "Inner Harbor",
    date: "2026-09-05",
    time_window: "16:00-21:00",
    status: "draft",
    current_plan_version: 0,
    public_release_status: "draft"
  };
}

const merchants: MerchantProfile[] = [
  {
    merchant_id: "m001",
    name: "Snack House",
    type: "food",
    capacity_level: "medium",
    signature_products: ["Tea"],
    suitable_activity_types: ["night market"],
    rainy_day_score: 4,
    night_score: 5,
    constraints: []
  },
  {
    merchant_id: "m002",
    name: "Craft Stall",
    type: "retail",
    capacity_level: "low",
    signature_products: ["Prints"],
    suitable_activity_types: ["market"],
    rainy_day_score: 3,
    night_score: 4,
    constraints: []
  }
];

function roster(overrides: Partial<EventMerchantSetupSummary> = {}): EventMerchantSetupSummary {
  return {
    event_id: "v29-harbor-fair",
    participants: [],
    total_count: 0,
    ready_count: 0,
    needs_setup_count: 0,
    missing_count: 0,
    declined_count: 0,
    ready_for_planning: false,
    ...overrides
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getEvent.mockResolvedValue(eventSummary());
  mockApi.getPlanVersions.mockResolvedValue([]);
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
  mockApi.generateOperationSuggestions.mockResolvedValue({ suggestions: [] });
  mockApi.getMerchants.mockResolvedValue(merchants);
  mockApi.getEventMerchantRoster.mockResolvedValue(roster());
  mockApi.replaceEventMerchantRoster.mockImplementation(
    (_eventId: string, payload: { merchant_ids: string[] }) =>
      Promise.resolve(
        roster({
          participants: payload.merchant_ids.map((merchant_id) => ({
            event_id: "v29-harbor-fair",
            merchant_id,
            participation_status: "confirmed",
            readiness_status: "needs_setup",
            role_hint: null,
            notes: "",
            created_at: "2026-06-28T00:00:00Z",
            updated_at: "2026-06-28T00:00:00Z"
          })),
          total_count: payload.merchant_ids.length,
          needs_setup_count: payload.merchant_ids.length
        })
      )
  );
});

test("workspace shows merchant setup before non-demo planning", async () => {
  renderWithI18n(<OrganizerEventWorkspacePage eventId="v29-harbor-fair" />);

  expect(await screen.findByRole("heading", { name: /Merchant setup/i })).toBeInTheDocument();
  expect(screen.getByText(/0\/0 ready/i)).toBeInTheDocument();
  expect(screen.getAllByRole("button", { name: /Build route plan/i })[0]).toBeDisabled();
});

test("organizer can add merchants to the selected event roster", async () => {
  renderWithI18n(<OrganizerEventWorkspacePage eventId="v29-harbor-fair" />);

  fireEvent.click(await screen.findByRole("checkbox", { name: /Snack House/i }));
  fireEvent.click(screen.getByRole("checkbox", { name: /Craft Stall/i }));
  fireEvent.click(screen.getByRole("button", { name: /Save merchant setup/i }));

  await waitFor(() =>
    expect(mockApi.replaceEventMerchantRoster).toHaveBeenCalledWith("v29-harbor-fair", {
      merchant_ids: ["m001", "m002"]
    })
  );
});

test("ready merchant roster allows selected event plan generation", async () => {
  mockApi.getEventMerchantRoster.mockResolvedValue(
    roster({
      participants: [
        {
          event_id: "v29-harbor-fair",
          merchant_id: "m001",
          participation_status: "confirmed",
          readiness_status: "ready",
          role_hint: null,
          notes: "",
          created_at: "2026-06-28T00:00:00Z",
          updated_at: "2026-06-28T00:00:00Z"
        }
      ],
      total_count: 1,
      ready_count: 1,
      ready_for_planning: true
    })
  );

  renderWithI18n(<OrganizerEventWorkspacePage eventId="v29-harbor-fair" />);

  const build = (await screen.findAllByRole("button", { name: /Build route plan/i }))[0];
  expect(build).toBeEnabled();
  fireEvent.click(build);
  await waitFor(() => expect(mockApi.generatePlan).toHaveBeenCalledWith("v29-harbor-fair"));
});

test("ineligible roster merchants show reasons and cannot be marked ready", async () => {
  mockApi.getEventMerchantRoster.mockResolvedValue(
    roster({
      participants: [
        {
          event_id: "v29-harbor-fair",
          merchant_id: "m001",
          participation_status: "confirmed",
          readiness_status: "needs_setup",
          role_hint: null,
          notes: "",
          created_at: "2026-06-28T00:00:00Z",
          updated_at: "2026-06-28T00:00:00Z"
        }
      ],
      total_count: 1,
      needs_setup_count: 1,
      eligibility: {
        m001: {
          merchant_id: "m001",
          status: "ineligible",
          reasons: ["merchant operating window does not overlap event time"]
        }
      }
    })
  );

  renderWithI18n(<OrganizerEventWorkspacePage eventId="v29-harbor-fair" />);

  expect(await screen.findByText(/merchant operating window does not overlap event time/i)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Mark ready/i })).not.toBeInTheDocument();
});
