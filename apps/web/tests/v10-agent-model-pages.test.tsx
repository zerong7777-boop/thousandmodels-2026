import { render, screen } from "@testing-library/react";
import { afterEach, test, vi } from "vitest";
import App from "../src/App";
import { mockAppFetch } from "./authTestUtils";

const qwenRun = {
  run_id: "run_demo-night-tour_recovery",
  event_id: "demo-night-tour",
  trigger: "incident_recovery",
  mode: "qwen_draft",
  status: "fallback_completed",
  started_at: "2026-06-12T10:00:00Z",
  completed_at: "2026-06-12T10:00:01Z",
  fallback_used: true,
  fallback_reason: "schema_failed",
  final_output_ref: "draft:draft_notice_001",
  error_summary: null
};

const reviewRun = {
  ...qwenRun,
  run_id: "run_demo-night-tour_review",
  trigger: "review_generation",
  final_output_ref: "draft:draft_review_001"
};

const deterministicRun = {
  ...qwenRun,
  run_id: "run_demo-night-tour_planning",
  trigger: "planning_generation",
  mode: "deterministic",
  status: "completed",
  fallback_used: false,
  fallback_reason: null,
  final_output_ref: "plan:demo-night-tour:v1"
};

const modelCalls = [
  {
    model_call_id: "model_001",
    run_id: qwenRun.run_id,
    provider: "dashscope",
    model: "qwen-plus",
    prompt_template_id: "qwen_public_notice_v1",
    input_refs: ["incident:inc_inventory_m001"],
    response_status: "schema_failed",
    parsed_output: null,
    fallback_used: true,
    error_summary: "public copy guard rejected model output",
    created_at: "2026-06-12T10:00:01Z"
  }
];

const evaluations = [
  {
    evaluation_id: "eval_001",
    run_id: qwenRun.run_id,
    schema_pass: false,
    fallback_used: true,
    unsafe_mutation_attempted: false,
    human_approval_required: true,
    forbidden_public_terms_present: false,
    public_copy_ready: true,
    notes: ["schema fallback used"]
  }
];

const recoveryDrafts = [
  {
    draft_id: "draft_notice_001",
    event_id: "demo-night-tour",
    source_run_id: qwenRun.run_id,
    draft_type: "public_notice",
    locale: "zh-Hans",
    content: "Please continue to the indoor tea stop. Your route has been updated.",
    structured_payload: { public_copy_ready: true, requires_organizer_approval: true },
    status: "draft",
    reviewed_by: null,
    reviewed_at: null,
    created_at: "2026-06-12T10:00:01Z"
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

function stubOrganizer(route: "exceptions" | "review" | "workspace") {
  localStorage.setItem("zhiyin.locale", "en");
  vi.stubGlobal(
    "fetch",
    mockAppFetch("organizer", (url) => {
      if (url.includes("/api/events/demo-night-tour/agent-runs/") && url.includes("/model-calls")) {
        return route === "workspace" ? [] : modelCalls;
      }
      if (url.includes("/api/events/demo-night-tour/agent-runs/") && url.includes("/evaluations")) {
        return route === "workspace" ? [] : evaluations;
      }
      if (url.includes("/api/events/demo-night-tour/agent-runs/") && url.includes("/tool-calls")) return [];
      if (url.includes("/api/events/demo-night-tour/agent-runs")) {
        if (route === "review") return [reviewRun];
        if (route === "workspace") return [deterministicRun];
        return [qwenRun];
      }
      if (url.includes("/api/events/demo-night-tour/agent-drafts")) {
        if (route === "review") {
          return [
            {
              ...recoveryDrafts[0],
              draft_id: "draft_review_001",
              source_run_id: reviewRun.run_id,
              draft_type: "review_summary",
              locale: "mixed",
              content: "Evidence: h5_visits was observed.",
              structured_payload: { metrics: ["h5_visits"], evidence_backed: true }
            }
          ];
        }
        return recoveryDrafts;
      }
      if (url.includes("/api/events/demo-night-tour/incidents")) {
        return [
          {
            incident_id: "inc_inventory_m001",
            event_id: "demo-night-tour",
            type: "inventory",
            severity: "high",
            source: "merchant",
            trigger_detail: "Merchant m001 reported sold out.",
            affected_route_points: ["rp001"],
            affected_merchants: ["m001"],
            status: "proposal_ready",
            created_at: "2026-06-12T10:00:01Z"
          }
        ];
      }
      if (url.includes("/api/events/demo-night-tour/review-report")) return reviewReport;
      if (url.includes("/api/events/demo-night-tour/plans")) return [];
      if (url.includes("/api/events/demo-night-tour/agent-traces")) return [];
      if (url.includes("/api/events/demo-night-tour/merchant-tasks")) return [];
      return {};
    })
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
  localStorage.clear();
  window.history.pushState({}, "", "/");
});

test("organizer exception center shows model draft evidence", async () => {
  stubOrganizer("exceptions");
  window.history.pushState({}, "", "/organizer/events/demo-night-tour/exceptions");
  render(<App />);

  expect(await screen.findByText("Model draft evidence")).toBeInTheDocument();
  expect(await screen.findByText("qwen-plus")).toBeInTheDocument();
  expect(screen.getByText("schema_failed")).toBeInTheDocument();
  expect(screen.getByText("Deterministic fallback used")).toBeInTheDocument();
});

test("organizer review center shows model draft evidence", async () => {
  stubOrganizer("review");
  window.history.pushState({}, "", "/organizer/events/demo-night-tour/review");
  render(<App />);

  expect(await screen.findByText("Review Agent evidence")).toBeInTheDocument();
  expect(await screen.findByText("qwen-plus")).toBeInTheDocument();
  expect(screen.getByText("schema_failed")).toBeInTheDocument();
});

test("organizer workspace shows deterministic model evidence empty state", async () => {
  stubOrganizer("workspace");
  window.history.pushState({}, "", "/organizer/events/demo-night-tour");
  render(<App />);

  expect(await screen.findByText("Planning Agent evidence")).toBeInTheDocument();
  expect((await screen.findAllByText("No model call recorded for this deterministic run.")).length).toBeGreaterThan(0);
});
