import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { afterEach, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { MerchantDashboardPage } from "../src/pages/merchant/MerchantDashboardPage";
import { OrganizerEventWorkspacePage } from "../src/pages/organizer/OrganizerEventWorkspacePage";
import { OrganizerExceptionCenterPage } from "../src/pages/organizer/OrganizerExceptionCenterPage";
import { OrganizerReviewPage } from "../src/pages/organizer/OrganizerReviewPage";
import { PublicEventPage } from "../src/pages/public/PublicEventPage";

const mockApi = vi.hoisted(() => ({
  getPublicEvent: vi.fn(),
  recordTouchpointInteraction: vi.fn(),
  claimCoupon: vi.fn(),
  redeemCoupon: vi.fn(),
  getMerchantWorkbench: vi.fn(),
  getMyMerchantEvents: vi.fn(),
  getPlanVersions: vi.fn(),
  getAgentTraces: vi.fn(),
  getMerchantTasks: vi.fn(),
  getEventPage: vi.fn(),
  getMerchantEdgePackages: vi.fn(),
  getAgentToolCalls: vi.fn(),
  getReviewReport: vi.fn(),
  getAgentRuns: vi.fn(),
  getAgentDrafts: vi.fn(),
  getAgentModelCalls: vi.fn(),
  getAgentEvaluations: vi.fn(),
  getIncidents: vi.fn(),
  getOperationSuggestions: vi.fn(),
  approveOperationSuggestion: vi.fn(),
  getEventOperationsSummary: vi.fn(),
  generateOperationSuggestions: vi.fn(),
  createRecoveryProposal: vi.fn(),
  approveRecoveryProposal: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

afterEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

test("public event page displays visitor event page title and story", async () => {
  mockApi.getPublicEvent.mockResolvedValue({
    event_id: "demo-night-tour",
    theme: "Historic District Night Tour",
    route: [],
    marketing_content: [],
    notices: [],
    checkin_tasks: [],
    title: "Historic District Night Tour",
    area: "Rua da Felicidade",
    status: "active",
    event_page: {
      title: "Moonlit Heritage Walk",
      subtitle: "Follow three evening stories through the old street.",
      story_sections: [
        {
          title: "Lantern opening",
          body: "Start with the red facade story before visiting nearby shops."
        },
        {
          title: "Quiet bridge",
          body: ""
        }
      ],
      merchant_highlights: [
        {
          name: "Tea House",
          highlight: "Ask for the event pairing."
        }
      ],
      route_highlights: [
        {
          name: "Old Street",
          visitor_task: "A compact route for the evening crowd."
        }
      ],
      notices: [{ message: "Bring your route card." }, { message: "   " }]
    }
  });

  renderWithI18n(<PublicEventPage eventId="demo-night-tour" />);

  expect(await screen.findByText("Moonlit Heritage Walk")).toBeInTheDocument();
  expect(screen.getByText("Lantern opening")).toBeInTheDocument();
  expect(screen.getByText("Start with the red facade story before visiting nearby shops.")).toBeInTheDocument();
  expect(screen.getByText("Tea House")).toBeInTheDocument();
  expect(screen.getByText("Bring your route card.")).toBeInTheDocument();
  expect(screen.getByText("A compact route for the evening crowd.")).toBeInTheDocument();
  expect(screen.queryByText(/^Quiet bridge$/)?.closest("article")?.querySelector("p")).toBeNull();
});

test("merchant dashboard displays interaction package fields and counts", async () => {
  mockApi.getMerchantWorkbench.mockResolvedValue({
    merchant: {
      merchant_id: "m001",
      name: "Merchant m001"
    },
    runtime_state: {
      merchant_id: "m001",
      inventory_status: "normal",
      queue_status: "normal",
      available_for_visitors: true,
      temporary_note: "",
      updated_at: "2026-06-12T10:00:00Z"
    },
    tasks: [],
    interaction_package: {
      id: "pkg-m001",
      event_id: "demo-night-tour",
      merchant_id: "m001",
      plan_version: 1,
      status: "active",
      operator_brief: "Keep stamps ready at the counter.",
      visitor_pitch: "Show your route card for a tea pairing.",
      task_ids: [],
      touchpoints: [
        {
          id: "tp-001",
          event_id: "demo-night-tour",
          merchant_id: "m001",
          package_id: "pkg-m001",
          touchpoint_type: "in_shop_qr",
          label: "Counter QR",
          public_copy: "Scan at the counter.",
          token: "counter",
          status: "active",
          metrics: {},
          created_at: "2026-06-12T10:00:00Z"
        }
      ],
      coupon_rules: [
        {
          id: "coupon-001",
          event_id: "demo-night-tour",
          merchant_id: "m001",
          package_id: "pkg-m001",
          title: "Tea pairing",
          description: "Route visitor offer.",
          max_redemptions: 20,
          per_anonymous_interaction_limit: 1,
          status: "active",
          created_at: "2026-06-12T10:00:00Z"
        }
      ],
      evidence_refs: [],
      created_at: "2026-06-12T10:00:00Z",
      updated_at: "2026-06-12T10:00:00Z"
    },
    touchpoint_summary: { interactions: 12 },
    coupon_summary: { claims: 5, redemptions: 2 }
  });
  mockApi.getMyMerchantEvents.mockResolvedValue([]);

  renderWithI18n(<MerchantDashboardPage merchantId="m001" />);

  expect(await screen.findByText("Keep stamps ready at the counter.")).toBeInTheDocument();
  expect(screen.getByText("Show your route card for a tea pairing.")).toBeInTheDocument();
  expect(screen.getByText("Touchpoints")).toBeInTheDocument();
  expect(screen.getByText("Coupons")).toBeInTheDocument();
  expect(screen.getByText("In-store touchpoints")).toBeInTheDocument();
  expect(screen.getByText("Counter QR")).toBeInTheDocument();
  expect(screen.getByText("Scan at the counter.")).toBeInTheDocument();
  expect(screen.getByText("Token: counter")).toBeInTheDocument();
  expect(screen.getByText("Type: In-store QR")).toBeInTheDocument();
  expect(screen.getByText("Offer rules")).toBeInTheDocument();
  expect(screen.getByText("Tea pairing")).toBeInTheDocument();
  expect(screen.getByText("Route visitor offer.")).toBeInTheDocument();
  expect(screen.getByText("20 redemptions available")).toBeInTheDocument();
  expect(screen.getByText("12")).toBeInTheDocument();
  expect(screen.getByText("5")).toBeInTheDocument();
  expect(screen.getByText("2")).toBeInTheDocument();
});

test("organizer workspace shows package readiness and can request operation suggestions", async () => {
  mockApi.getPlanVersions.mockResolvedValue([
    {
      plan_id: "plan-v1",
      event_id: "demo-night-tour",
      version: 1,
      status: "approved",
      created_by: "agent",
      created_reason: "inventory incident recovery",
      route_points: [],
      merchant_assignments: ["m001"],
      budget_plan: {},
      risk_plan: [],
      diff_from_previous: []
    }
  ]);
  mockApi.getAgentTraces.mockResolvedValue([]);
  mockApi.getMerchantTasks.mockResolvedValue([]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getEventPage.mockResolvedValue({
    id: "ep-001",
    event_id: "demo-night-tour",
    plan_version: 1,
    status: "published",
    title: "Moonlit Heritage Walk",
    subtitle: "Visitor story page",
    story_sections: [],
    route_highlights: [],
    merchant_highlights: [],
    notices: [],
    updated_at: "2026-06-12T10:00:00Z"
  });
  mockApi.getMerchantEdgePackages.mockResolvedValue({
    packages: [
      {
        id: "pkg-m001",
        event_id: "demo-night-tour",
        merchant_id: "m001",
        plan_version: 1,
        status: "active",
        operator_brief: "Keep stamps ready.",
        visitor_pitch: "Show your card.",
        task_ids: [],
        touchpoints: [{ id: "tp-001", status: "active" }],
        coupon_rules: [{ id: "coupon-001", status: "active" }],
        evidence_refs: ["plan:v1", "merchant-task:m001"],
        created_at: "2026-06-12T10:00:00Z",
        updated_at: "2026-06-12T10:00:00Z"
      }
    ]
  });
  mockApi.generateOperationSuggestions.mockResolvedValue({ suggestions: [{ id: "os-001" }] });
  mockApi.getEventOperationsSummary.mockResolvedValue(null);

  renderWithI18n(<OrganizerEventWorkspacePage eventId="demo-night-tour" />);

  expect(await screen.findByText("Package readiness")).toBeInTheDocument();
  expect(await screen.findByText("Package for Merchant m001")).toBeInTheDocument();
  expect(await screen.findByText("1/1 touchpoints active")).toBeInTheDocument();
  expect(await screen.findByText("1/1 offers active")).toBeInTheDocument();
  expect(await screen.findByText("plan:v1")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Generate operation suggestions" }));
  expect(await screen.findByText("1 operation suggestions are ready for review.")).toBeInTheDocument();
  expect(mockApi.generateOperationSuggestions).toHaveBeenCalledWith("demo-night-tour");
});

test("public event page records scan, claim, and redemption actions", async () => {
  mockApi.getPublicEvent.mockResolvedValue({
    event_id: "demo-night-tour",
    theme: "Historic District Night Tour",
    route: [],
    marketing_content: [],
    notices: [],
    checkin_tasks: [],
    title: "Historic District Night Tour",
    area: "Rua da Felicidade",
    status: "active",
    current_plan_version: 2,
    event_page: {
      title: "Moonlit Heritage Walk",
      subtitle: "Follow the public route.",
      story_sections: [],
      route_highlights: [],
      merchant_highlights: [],
      notices: [],
      interaction_package: {
        touchpoints: [{ id: "tp-001", label: "Counter QR" }],
        coupon_rules: [{ id: "coupon-001", title: "Tea pairing" }]
      }
    }
  });
  mockApi.recordTouchpointInteraction.mockResolvedValue({
    id: "interaction-001",
    event_id: "demo-night-tour",
    touchpoint_id: "tp-001",
    interaction_type: "scan",
    source: "public-event-demo",
    anonymous_interaction_id: "anon-001",
    created_at: "2026-06-12T10:00:00Z",
    metadata: {}
  });
  mockApi.claimCoupon.mockResolvedValue({
    id: "redemption-001",
    event_id: "demo-night-tour",
    coupon_rule_id: "coupon-001",
    merchant_id: "m001",
    anonymous_interaction_id: "anon-001",
    status: "claimed",
    claimed_at: "2026-06-12T10:00:01Z"
  });
  mockApi.redeemCoupon.mockResolvedValue({
    id: "redemption-001",
    event_id: "demo-night-tour",
    coupon_rule_id: "coupon-001",
    merchant_id: "m001",
    anonymous_interaction_id: "anon-001",
    status: "redeemed",
    claimed_at: "2026-06-12T10:00:01Z",
    redeemed_at: "2026-06-12T10:00:02Z"
  });

  renderWithI18n(<PublicEventPage eventId="demo-night-tour" />);

  expect(await screen.findByText("Event update v2")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Scan spot" }));
  expect(await screen.findByText("Spot scan recorded.")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Claim offer" }));
  expect(await screen.findByText("Offer claimed.")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Redeem offer" }));
  expect(await screen.findByText("Offer redeemed.")).toBeInTheDocument();
  expect(mockApi.recordTouchpointInteraction).toHaveBeenCalledWith("demo-night-tour", "tp-001", {
    interaction_type: "scan",
    source: "public-event-demo"
  });
  expect(mockApi.claimCoupon).toHaveBeenCalledWith("demo-night-tour", "coupon-001", "anon-001");
  expect(mockApi.redeemCoupon).toHaveBeenCalledWith("demo-night-tour", "redemption-001");
});

test("review page shows business labels instead of raw backend metric keys", async () => {
  mockApi.getReviewReport.mockResolvedValue({
    event_id: "demo-night-tour",
    summary: "H5 visits 428; recovery confirmation reduced confused arrivals.",
    route_result: "Route completed",
    merchant_result: "Merchants completed",
    incident_summary: "Inventory exception recovered",
    agent_actions: [],
    human_approvals: [],
    lessons_learned: [],
    next_event_recommendations: [],
    touchpoint_summary: {
      total_interactions: 42,
      coupon_claims: 9,
      coupon_redemptions: 4,
      redemption_rate: "44%",
      by_type: { in_shop_qr: 31, coupon: 9 },
      by_merchant: { m001: 42 }
    },
    merchant_outcomes: [
      {
        merchant_id: "m001",
        total_interactions: 42,
        coupon_claims: 9,
        coupon_redemptions: 4,
        summary: "Merchant tasks were updated after the exception."
      }
    ],
    extension_tasks: [
      {
        task_type: "merchant_follow_up",
        title: "Confirm backup staffing",
        metric_refs: ["coupon_claims", "redemption_rate"],
        merchant_ids: ["m001"],
        rationale: "Validate staffing coverage before the next route window."
      }
    ]
  });
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentDrafts.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);

  renderWithI18n(<OrganizerReviewPage eventId="demo-night-tour" />);

  expect(await screen.findByText("Total interactions")).toBeInTheDocument();
  expect(screen.getByText("Coupon claims")).toBeInTheDocument();
  expect(screen.getByText("Coupon redemptions")).toBeInTheDocument();
  expect(screen.getByText("By touchpoint")).toBeInTheDocument();
  expect(screen.getByText("By merchant")).toBeInTheDocument();
  expect(screen.getByText("In-store QR 31 | Coupon claim 9")).toBeInTheDocument();
  expect(screen.getByText("Merchant m001")).toBeInTheDocument();
  expect(screen.getByText("Linked metrics: Coupon claims, Redemption rate")).toBeInTheDocument();
  expect(screen.queryByText("total interactions")).not.toBeInTheDocument();
  expect(screen.queryByText("total_interactions")).not.toBeInTheDocument();
  expect(screen.queryByText("coupon_claims")).not.toBeInTheDocument();
  expect(screen.queryByText("coupon_redemptions")).not.toBeInTheDocument();
  expect(screen.queryByText("redemption_rate")).not.toBeInTheDocument();
});

test("exception center shows a warning and reloads suggestions after stale approve failure", async () => {
  mockApi.getIncidents.mockResolvedValue([
    {
      incident_id: "inc-001",
      event_id: "demo-night-tour",
      type: "inventory",
      severity: "high",
      source: "merchant",
      trigger_detail: "Merchant m001 reported sold out.",
      affected_route_points: ["rp001"],
      affected_merchants: ["m001"],
      status: "proposal_ready",
      created_at: "2026-06-12T10:00:00Z"
    }
  ]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentDrafts.mockResolvedValue([]);
  mockApi.getAgentToolCalls.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);
  mockApi.getOperationSuggestions
    .mockResolvedValueOnce({
      suggestions: [
        {
          id: "suggestion-1",
          event_id: "demo-night-tour",
          suggestion_type: "route_adjustment",
          status: "pending_approval",
          title: "Reorder the first two stops",
          rationale: "Avoid the sold-out queue.",
          recommended_actions: [],
          impacted_merchants: ["m001"],
          impacted_route_points: ["rp001"],
          evidence_refs: ["ev-1"],
          created_at: "2026-06-12T10:00:00Z"
        }
      ]
    })
    .mockResolvedValueOnce({
      suggestions: [
        {
          id: "suggestion-1",
          event_id: "demo-night-tour",
          suggestion_type: "route_adjustment",
          status: "approved",
          title: "Use the latest route adjustment",
          rationale: "A newer suggestion already replaced the stale one.",
          recommended_actions: [],
          impacted_merchants: ["m001"],
          impacted_route_points: ["rp001"],
          evidence_refs: ["ev-2"],
          created_at: "2026-06-12T10:01:00Z"
        }
      ]
    });
  mockApi.approveOperationSuggestion.mockRejectedValue(new Error("stale"));

  renderWithI18n(<OrganizerExceptionCenterPage eventId="demo-night-tour" />);

  expect(await screen.findByText("Reorder the first two stops")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Approve suggestion" }));

  expect(await screen.findByText("This suggestion is out of date. The latest suggestions have been reloaded.")).toBeInTheDocument();
  expect(await screen.findByText("Use the latest route adjustment")).toBeInTheDocument();
  await waitFor(() => expect(mockApi.getOperationSuggestions).toHaveBeenCalledTimes(2));
});

test("exception center ignores a stale recovery confirmation after incident switch", async () => {
  let resolveApproval: (() => void) | undefined;
  mockApi.getIncidents.mockResolvedValue([
    {
      incident_id: "inc-001",
      event_id: "demo-night-tour",
      type: "inventory",
      severity: "high",
      source: "merchant",
      trigger_detail: "Merchant m001 reported sold out.",
      affected_route_points: ["rp001"],
      affected_merchants: ["m001"],
      status: "proposal_ready",
      created_at: "2026-06-12T10:00:00Z"
    },
    {
      incident_id: "inc-002",
      event_id: "demo-night-tour",
      type: "queue",
      severity: "medium",
      source: "merchant",
      trigger_detail: "Merchant m002 queue is busy.",
      affected_route_points: ["rp002"],
      affected_merchants: ["m002"],
      status: "open",
      created_at: "2026-06-12T10:01:00Z"
    }
  ]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentDrafts.mockResolvedValue([]);
  mockApi.getAgentToolCalls.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);
  mockApi.getOperationSuggestions.mockResolvedValue({ suggestions: [] });
  mockApi.createRecoveryProposal.mockResolvedValue({
    proposal_id: "proposal-001",
    incident_id: "inc-001",
    event_id: "demo-night-tour",
    recommended_changes: ["Move visitors to the indoor stop."],
    plan_patch: {},
    merchant_task_patch: {},
    public_notice_patch: "Please continue to the indoor tea stop.",
    impact_summary: "Inventory pressure avoided.",
    requires_approval: true,
    approval_status: "pending"
  });
  mockApi.approveRecoveryProposal.mockReturnValue(
    new Promise((resolve) => {
      resolveApproval = () =>
        resolve({
          plan_version: { version: 2, status: "approved" },
          public_notice: { message: "Please continue to the indoor tea stop.", publish_status: "published" }
        });
    })
  );

  renderWithI18n(<OrganizerExceptionCenterPage eventId="demo-night-tour" />);

  expect(await screen.findByText("Merchant m001 reported sold out.")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Prepare recovery suggestion" }));
  await waitFor(() => expect(mockApi.createRecoveryProposal).toHaveBeenCalledWith("demo-night-tour", "inc-001"));

  fireEvent.click(screen.getByRole("button", { name: "Confirm recovery update" }));
  fireEvent.click(screen.getByText("Merchant m002 queue is busy."));
  resolveApproval?.();

  await waitFor(() => expect(mockApi.approveRecoveryProposal).toHaveBeenCalledWith("demo-night-tour", "proposal-001"));
  await new Promise((resolve) => setTimeout(resolve, 0));
  expect(screen.queryByText("Recovery update confirmed. Public notice and route v2 are ready.")).not.toBeInTheDocument();
});
