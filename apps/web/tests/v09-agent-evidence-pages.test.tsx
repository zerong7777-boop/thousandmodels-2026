import { render, screen } from "@testing-library/react";
import { afterEach, test, vi } from "vitest";
import App from "../src/App";
import { mockAppFetch } from "./authTestUtils";

const routePoints = [
  {
    point_id: "rp001",
    name: "Rua da Felicidade",
    type: "heritage",
    is_indoor: false,
    estimated_stay_minutes: 18,
    story: "A restored street story.",
    linked_merchants: ["m001"],
    visitor_task: "Collect a stamp.",
    rainy_day_score: 0.62,
    crowd_risk: "medium",
    current_status: "active"
  }
];

const planVersions = [
  {
    plan_id: "plan-v1",
    event_id: "demo-night-tour",
    version: 1,
    status: "approved",
    created_by: "agent",
    created_reason: "initial route planning",
    route_points: routePoints,
    merchant_assignments: ["m001"],
    budget_plan: {},
    risk_plan: ["Monitor inventory"],
    diff_from_previous: ["Initial operating plan"]
  }
];

const merchantTasks = [
  {
    task_id: "task-m001-v1",
    event_id: "demo-night-tour",
    merchant_id: "m001",
    plan_version: 1,
    role: "Heritage snack stop",
    time_slot: "19:00-20:00",
    visitor_task: "Collect a stamp.",
    preparation_items: ["Stamp card"],
    promo_text: "Tonight special",
    fallback_instruction: "Pause intake if sold out.",
    task_status: "active"
  }
];

const planningRun = {
  run_id: "run_demo-night-tour_planning",
  event_id: "demo-night-tour",
  trigger: "planning_generation",
  mode: "deterministic",
  status: "completed",
  started_at: "2026-06-12T10:00:00Z",
  completed_at: "2026-06-12T10:00:01Z",
  fallback_used: false,
  fallback_reason: null,
  final_output_ref: "plan:demo-night-tour:v1",
  error_summary: null
};

const agentTraces = [
  {
    trace_id: "trace-v1",
    event_id: "demo-night-tour",
    trigger: "planning_generation",
    steps: [
      "CoordinatorAgent",
      "CulturalNarrativeAgent",
      "RoutePlanningAgent",
      "MerchantMatchingAgent",
      "RiskRecoveryAgent",
      "PublicNoticeAgent"
    ].map((agentName, index) => ({
      step_id: `step_${index + 1}`,
      run_id: planningRun.run_id,
      agent_name: agentName,
      objective: `${agentName} objective`,
      input_refs: ["event_brief:demo-night-tour"],
      tool_calls: [],
      tool_call_refs: index === 2 ? ["tool_route_001"] : [],
      structured_output: { step: index + 1 },
      decision_reason: `${agentName} produced deterministic evidence.`,
      confidence: 0.88,
      requires_human_approval: agentName === "PublicNoticeAgent",
      schema_name: "AgentStep",
      validation_status: "passed"
    })),
    final_output_ref: "plan:demo-night-tour:v1",
    human_decision_ref: null
  }
];

const toolCalls = [
  {
    tool_call_id: "tool_route_001",
    run_id: planningRun.run_id,
    step_id: "step_3",
    tool_name: "route.build_static_route",
    input_payload: { rainy: false },
    output_payload: { route_count: 6 },
    status: "success",
    latency_ms: 0,
    error_summary: null
  },
  {
    tool_call_id: "tool_merchant_001",
    run_id: planningRun.run_id,
    step_id: "step_4",
    tool_name: "merchant.select_night_merchants",
    input_payload: { event_id: "demo-night-tour" },
    output_payload: { selected: ["m001"] },
    status: "success",
    latency_ms: 0,
    error_summary: null
  }
];

const reviewReport = {
  event_id: "demo-night-tour",
  summary: "H5 visits 428; recovery confirmation reduced confused arrivals.",
  route_result: "Route completed",
  merchant_result: "Merchants completed",
  incident_summary: "Inventory exception recovered",
  agent_actions: ["Evidence summarized"],
  human_approvals: ["Organizer confirmed recovery"],
  lessons_learned: ["H5 visits 428"],
  next_event_recommendations: ["Reduce sold-out merchant routing weight"]
};

function stubOrganizer() {
  localStorage.setItem("zhiyin.locale", "en");
  vi.stubGlobal(
    "fetch",
    mockAppFetch("organizer", (url) => {
      if (url.includes("/api/events/demo-night-tour/plans")) return planVersions;
      if (url.includes("/api/events/demo-night-tour/agent-traces")) return agentTraces;
      if (url.includes("/api/events/demo-night-tour/agent-runs")) {
        if (url.includes("/tool-calls")) return toolCalls;
        return [planningRun];
      }
      if (url.includes("/api/events/demo-night-tour/agent-drafts")) return [];
      if (url.includes("/api/events/demo-night-tour/merchant-tasks")) return merchantTasks;
      if (url.includes("/api/events/demo-night-tour/incidents")) return [];
      if (url.includes("/api/events/demo-night-tour/review-report")) return reviewReport;
      if (url.endsWith("/api/events")) {
        return [
          {
            event_id: "demo-night-tour",
            title: "Historic District Night Tour",
            area: "Rua da Felicidade",
            date: "2026-07-18",
            time_window: "18:00-21:30",
            status: "active",
            current_plan_version: 1,
            public_release_status: "published"
          }
        ];
      }
      return {};
    })
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
  window.history.pushState({}, "", "/");
});

test("organizer workspace shows planning Agent evidence and tool calls", async () => {
  stubOrganizer();
  window.history.pushState({}, "", "/organizer/events/demo-night-tour");
  render(<App />);

  expect(await screen.findByText("Planning Agent evidence")).toBeInTheDocument();
  expect(await screen.findByText("Planning generation")).toBeInTheDocument();
  expect(screen.getByText("RoutePlanningAgent")).toBeInTheDocument();
  expect(screen.getByText("PublicNoticeAgent")).toBeInTheDocument();
  expect(await screen.findByText("route.build_static_route")).toBeInTheDocument();
  expect(screen.getByText("merchant.select_night_merchants")).toBeInTheDocument();
  expect(screen.getByText("Human approval remains required for release actions.")).toBeInTheDocument();
});
