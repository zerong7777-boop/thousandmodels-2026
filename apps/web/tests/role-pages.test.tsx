import { render, screen } from "@testing-library/react";
import App from "../src/App";
import { zhHans as zh } from "../src/i18n/dictionaries/zh-Hans";
import { mockAppFetch } from "./authTestUtils";

const publicPayload = {
  event_id: "demo-night-tour",
  title: "Historic District Night Tour",
  area: "Rua da Felicidade",
  status: "active",
  current_plan_version: 2,
  route_points: [
    {
      point_id: "rp001",
      name: "Rua da Felicidade",
      story: "A street story",
      visitor_task: "Collect a stamp",
      linked_merchants: ["m001"],
      is_indoor: false,
      current_status: "active"
    }
  ],
  notices: ["Route updated for tonight"],
  public_notices: [{ notice_id: "n1", message: "Route updated for tonight", publish_status: "published" }]
};

const planVersions = [
  {
    plan_id: "plan-v2",
    event_id: "demo-night-tour",
    version: 2,
    status: "approved",
    created_by: "agent",
    created_reason: "recovery update",
    route_points: publicPayload.route_points,
    merchant_assignments: ["m001"],
    budget_plan: {},
    risk_plan: ["Monitor inventory"],
    diff_from_previous: ["Moved visitors to sheltered stop", "Paused sold-out merchant"]
  }
];

const agentTraces = [
  {
    trace_id: "trace-v2",
    event_id: "demo-night-tour",
    trigger: "Merchant inventory update",
    steps: Array.from({ length: 5 }, (_, index) => ({
      agent_name: `workflow-step-${index + 1}`,
      input_refs: [],
      tool_calls: [],
      structured_output: {},
      decision_reason: "Evidence-backed deterministic step.",
      confidence: 0.9,
      requires_human_approval: index === 4
    })),
    final_output_ref: "plan-v2"
  }
];

const merchantPayload = {
  merchant: { merchant_id: "m001", name: "Merchant m001", type: "food" },
  tasks: [
    {
      task_id: "task001",
      event_id: "demo-night-tour",
      merchant_id: "m001",
      plan_version: 2,
      role: "Dessert stop",
      time_slot: "19:30-20:20",
      visitor_task: "Collect a stamp",
      preparation_items: ["Prepare tasting set"],
      promo_text: "Tonight special",
      fallback_instruction: "Pause new visitors if sold out",
      task_status: "active"
    }
  ],
  runtime_state: {
    merchant_id: "m001",
    inventory_status: "normal",
    queue_status: "normal",
    available_for_visitors: true,
    temporary_note: "",
    updated_at: "2026-06-10T00:00:00Z"
  }
};

function stubRole(role: "organizer" | "merchant" | "tourist" | null) {
  vi.stubGlobal(
    "fetch",
    mockAppFetch(role, (url) => {
      if (url.includes("/api/public/events")) return publicPayload;
      if (url.includes("/api/events/demo-night-tour/plans")) return planVersions;
      if (url.includes("/api/events/demo-night-tour/agent-traces")) return agentTraces;
      if (url.includes("/api/events/demo-night-tour/merchant-tasks")) return merchantPayload.tasks;
      if (url.includes("/api/merchants/")) return merchantPayload;
      if (url.includes("/api/events") && !url.includes("review-report")) {
        return [
          {
            event_id: "demo-night-tour",
            title: "Historic District Night Tour",
            area: "Rua da Felicidade",
            date: "2026-07-18",
            time_window: "18:00-21:30",
            status: "active",
            current_plan_version: 2,
            public_release_status: "published"
          }
        ];
      }
      return {
        event_id: "demo-night-tour",
        summary: "Event completed",
        route_result: "Route completed",
        merchant_result: "Merchants completed",
        incident_summary: "Inventory exception recovered",
        agent_actions: ["Evidence summarized"],
        human_approvals: ["Organizer confirmed recovery"],
        lessons_learned: ["H5 visits 428"],
        next_event_recommendations: ["Reduce sold-out merchant routing weight"]
      };
    })
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("merchant task status and notification routes render different content", async () => {
  stubRole("merchant");
  window.history.pushState({}, "", "/merchant/dashboard");
  const dashboard = render(<App />);
  expect((await screen.findAllByText(zh["merchant.dashboard.eyebrow"])).length).toBeGreaterThan(0);
  expect(screen.getByText(zh["merchant.dashboard.nextAction"])).toBeInTheDocument();
  expect(screen.getAllByText(zh["merchant.dashboard.beforeVisitors"]).length).toBeGreaterThan(0);
  dashboard.unmount();

  window.history.pushState({}, "", "/merchant/events/demo-night-tour/tasks");
  const first = render(<App />);
  expect(await screen.findByText(zh["merchant.tasks.eyebrow"])).toBeInTheDocument();
  expect((await screen.findAllByText(zh["merchant.tasks.preparation"])).length).toBeGreaterThan(0);
  expect(await screen.findByText(/Prepare tasting set/i)).toBeInTheDocument();
  first.unmount();

  window.history.pushState({}, "", "/merchant/events/demo-night-tour/status");
  const second = render(<App />);
  expect(await screen.findByText(zh["merchant.status.eyebrow"])).toBeInTheDocument();
  second.unmount();

  window.history.pushState({}, "", "/merchant/notifications");
  render(<App />);
  expect((await screen.findAllByText(zh["merchant.notices.eyebrow"])).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["merchant.notices.recoveryNotice"]).length).toBeGreaterThan(0);
});

test("tourist logged-in route is not the same surface as public route", async () => {
  stubRole("tourist");
  window.history.pushState({}, "", "/user/events/demo-night-tour");
  const loggedIn = render(<App />);
  expect(await screen.findByText(zh["tourist.event.eyebrow"])).toBeInTheDocument();
  expect(screen.getAllByText(zh["routeProgress.title"]).length).toBeGreaterThan(0);
  expect(screen.getByText(zh["common.logout"])).toBeInTheDocument();
  loggedIn.unmount();

  window.history.pushState({}, "", "/user/events/demo-night-tour/route");
  const route = render(<App />);
  expect(await screen.findByText(zh["tourist.route.title"])).toBeInTheDocument();
  expect((await screen.findAllByText(zh["routeStop.visitorTask"])).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["routeProgress.title"]).length).toBeGreaterThan(0);
  route.unmount();

  window.history.pushState({}, "", "/user/events/demo-night-tour/points/rp001");
  const point = render(<App />);
  expect((await screen.findAllByText(zh["tourist.event.visitorTask"])).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["tourist.point.eyebrow"]).length).toBeGreaterThan(0);
  point.unmount();

  window.history.pushState({}, "", "/user/events/demo-night-tour/notices");
  const notices = render(<App />);
  expect((await screen.findAllByText(zh["tourist.notices.latest"])).length).toBeGreaterThan(0);
  notices.unmount();

  stubRole(null);
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);
  expect(await screen.findByText(zh["public.event.visitorRoute"])).toBeInTheDocument();
  expect(screen.queryByText(zh["common.logout"])).not.toBeInTheDocument();
});

test("organizer workspace uses product language for internal evidence", async () => {
  stubRole("organizer");
  window.history.pushState({}, "", "/organizer/events/demo-night-tour");
  render(<App />);
  expect(await screen.findByText(zh["organizer.workspace.stepperTitle"])).toBeInTheDocument();
  expect(screen.getAllByText(zh["organizer.workspace.planStatus"]).length).toBeGreaterThan(0);
  expect((await screen.findAllByText(zh["organizer.workspace.evidenceTrail"])).length).toBeGreaterThan(0);
  expect(screen.getAllByText(new RegExp(zh["organizer.dashboard.merchantReadiness"])).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["organizer.workspace.stepApproval"]).length).toBeGreaterThan(0);
  expect(screen.queryByText(/AgentTrace/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/PlanVersion/i)).not.toBeInTheDocument();
});
