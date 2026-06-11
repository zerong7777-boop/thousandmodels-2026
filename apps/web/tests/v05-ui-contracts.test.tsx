import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { mockAppFetch } from "./authTestUtils";

const eventSummary = {
  event_id: "demo-night-tour",
  title: "Historic District Night Tour",
  area: "Rua da Felicidade",
  date: "2026-07-18",
  time_window: "18:00-21:30",
  status: "active",
  current_plan_version: 2,
  public_release_status: "published"
};

const routePoints = [
  {
    point_id: "rp001",
    name: "Rua da Felicidade",
    type: "heritage",
    is_indoor: false,
    estimated_stay_minutes: 18,
    story: "A restored street story linking old shops and evening foot traffic.",
    linked_merchants: ["m001"],
    visitor_task: "Collect the red facade stamp.",
    rainy_day_score: 0.62,
    crowd_risk: "medium",
    current_status: "active"
  },
  {
    point_id: "rp002",
    name: "Indoor tea stop",
    type: "merchant",
    is_indoor: true,
    estimated_stay_minutes: 20,
    story: "A sheltered stop used after the recovery plan.",
    linked_merchants: ["m002"],
    visitor_task: "Try the heritage tea pairing.",
    rainy_day_score: 0.91,
    crowd_risk: "low",
    current_status: "active"
  }
];

const merchantTask = {
  task_id: "task-m001-v2",
  event_id: "demo-night-tour",
  merchant_id: "m001",
  plan_version: 2,
  role: "Heritage snack stop",
  time_slot: "19:00-20:00",
  visitor_task: "Prepare twenty tasting cards.",
  preparation_items: ["Queue marker", "Stamp card"],
  promo_text: "Tonight only heritage tasting",
  fallback_instruction: "Pause intake and notify organizer.",
  task_status: "active"
};

function stubRole(role: "organizer" | "merchant" | "tourist" | null) {
  vi.stubGlobal(
    "fetch",
    mockAppFetch(role, (url, init) => {
      if (url.endsWith("/api/events")) return [eventSummary];
      if (url.includes("/api/events/demo-night-tour/plans")) {
        return [
          {
            plan_id: "plan-v2",
            event_id: "demo-night-tour",
            version: 2,
            status: "approved",
            created_by: "agent",
            created_reason: "inventory incident recovery",
            route_points: routePoints,
            merchant_assignments: ["m001", "m002"],
            budget_plan: {},
            risk_plan: ["Avoid overloaded merchant"],
            diff_from_previous: ["Pause sold-out stop", "Add indoor tea stop"]
          }
        ];
      }
      if (url.includes("/api/events/demo-night-tour/agent-traces")) {
        return [
          {
            trace_id: "trace-plan-v2",
            event_id: "demo-night-tour",
            trigger: "Merchant inventory incident",
            steps: Array.from({ length: 5 }, (_, index) => ({
              agent_name: `deterministic-step-${index + 1}`,
              input_refs: ["runtime_state", "plan_v1"],
              tool_calls: [],
              structured_output: { step: index + 1 },
              decision_reason: "Rule-based route recovery evidence.",
              confidence: 0.9,
              requires_human_approval: index === 4
            })),
            final_output_ref: "plan-v2"
          }
        ];
      }
      if (url.includes("/api/events/demo-night-tour/merchant-tasks")) return [merchantTask];
      if (url.includes("/api/events/demo-night-tour/incidents")) {
        return [
          {
            incident_id: "inc-inventory-m001",
            event_id: "demo-night-tour",
            type: "inventory",
            severity: "high",
            source: "merchant",
            trigger_detail: "Merchant m001 reported sold out.",
            affected_route_points: ["rp001"],
            affected_merchants: ["m001"],
            status: "proposal_ready",
            created_at: "2026-06-10T12:05:00Z"
          }
        ];
      }
      if (url.includes("/api/merchants/m001/runtime-state")) {
        const body = init?.body ? JSON.parse(String(init.body)) : {};
        return {
          merchant_id: "m001",
          inventory_status: body.inventory_status ?? "sold_out",
          queue_status: body.queue_status ?? "normal",
          available_for_visitors: body.available_for_visitors ?? false,
          temporary_note: body.temporary_note ?? "Sold out",
          updated_at: "2026-06-10T12:10:00Z",
          incident: { incident_id: "inc-inventory-m001", status: "open" }
        };
      }
      if (url.includes("/api/merchants/m001/workbench")) {
        return {
          merchant: { merchant_id: "m001", name: "Merchant m001", type: "food" },
          runtime_state: {
            merchant_id: "m001",
            inventory_status: "normal",
            queue_status: "normal",
            available_for_visitors: true,
            temporary_note: "",
            updated_at: "2026-06-10T12:00:00Z"
          },
          tasks: [merchantTask]
        };
      }
      if (url.includes("/api/public/events/demo-night-tour")) {
        return {
          ...eventSummary,
          theme: "Historic District Night Tour",
          route: ["Rua da Felicidade", "Indoor tea stop"],
          marketing_content: ["Evening heritage walk"],
          notices: ["Please continue to the indoor tea stop."],
          checkin_tasks: ["Collect the red facade stamp."],
          route_points: routePoints,
          public_notices: [
            {
              notice_id: "notice-v2",
              event_id: "demo-night-tour",
              plan_version: 2,
              audience: "tourist",
              message: "Please continue to the indoor tea stop.",
              publish_status: "published"
            }
          ]
        };
      }
      if (url.includes("/api/events/demo-night-tour/review-report")) {
        return {
          event_id: "demo-night-tour",
          summary: "H5 visits 428; recovery confirmation reduced confused arrivals.",
          route_result: "Route v2 kept the visitor flow active.",
          merchant_result: "Merchant tasks were updated after the exception.",
          incident_summary: "One inventory exception was approved into a recovered route.",
          agent_actions: ["Generated initial route", "Generated recovery suggestion"],
          human_approvals: ["Approved initial route", "Confirmed recovery update"],
          lessons_learned: ["Inventory telemetry needs earlier merchant prompts."],
          next_event_recommendations: ["Pre-stage an indoor backup stop."]
        };
      }
      return {};
    })
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("login presents product entry with compact role options", async () => {
  stubRole(null);
  window.history.pushState({}, "", "/login");
  render(<App />);

  expect(await screen.findByRole("heading", { name: /zhiyin haojiang/i })).toBeInTheDocument();
  expect(screen.getByText(/organizer workspace/i)).toBeInTheDocument();
  expect(screen.getByText(/merchant workbench/i)).toBeInTheDocument();
  expect(screen.getByText(/visitor route/i)).toBeInTheDocument();
  expect(screen.queryByText(/choose demo identity/i)).not.toBeInTheDocument();
});

test("organizer dashboard has attention queue metrics and activity timeline", async () => {
  stubRole("organizer");
  window.history.pushState({}, "", "/organizer/dashboard");
  render(<App />);

  expect(await screen.findByText(/needs attention/i)).toBeInTheDocument();
  expect(screen.getByText(/merchant readiness/i)).toBeInTheDocument();
  expect(screen.getByText(/live exceptions/i)).toBeInTheDocument();
  expect(screen.getByText(/activity timeline/i)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /enter event workspace/i })).toBeInTheDocument();
});

test("organizer exception center presents impact diff and confirmation consequence", async () => {
  stubRole("organizer");
  window.history.pushState({}, "", "/organizer/events/demo-night-tour/exceptions");
  render(<App />);

  expect(await screen.findByText(/exception queue/i)).toBeInTheDocument();
  expect(screen.getByText(/impact scope/i)).toBeInTheDocument();
  expect(screen.getByText(/before/i)).toBeInTheDocument();
  expect(screen.getByText(/after/i)).toBeInTheDocument();
  expect(screen.getByText(/public notice preview/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /confirm recovery update/i })).toBeInTheDocument();
});

test("merchant status uses quick actions and sold-out still requests organizer review", async () => {
  stubRole("merchant");
  window.history.pushState({}, "", "/merchant/events/demo-night-tour/status");
  render(<App />);

  expect(await screen.findByRole("button", { name: /accept visitors/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /pause visitors/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /report low stock/i })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /report sold out/i }));
  await waitFor(() => expect(screen.getByText(/organizer review requested/i)).toBeInTheDocument());
});

test("public H5 reads like a visitor route with live updates and progress", async () => {
  stubRole(null);
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);

  expect(await screen.findByText(/tonight's route/i)).toBeInTheDocument();
  expect(screen.getByText(/live update/i)).toBeInTheDocument();
  expect(screen.getByText(/route progress/i)).toBeInTheDocument();
  expect(screen.getByText(/Stop 1/i)).toBeInTheDocument();
  expect(screen.queryByText(/PlanVersion/i)).not.toBeInTheDocument();
});
