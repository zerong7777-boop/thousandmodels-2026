import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { beforeEach, describe, expect, test } from "vitest";
import {
  AgentDraftCard,
  AgentEvidencePanel,
  AgentRunSummary,
  AgentStepTimeline,
  AgentToolCallList
} from "../src/components/agent";
import { I18nProvider } from "../src/i18n";
import type { AgentDraft, AgentRun, AgentStep, AgentToolCall } from "../src/types";

const run: AgentRun = {
  run_id: "run_demo-night-tour_plan",
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

const steps: AgentStep[] = [
  {
    step_id: "step_route",
    run_id: run.run_id,
    agent_name: "RoutePlanningAgent",
    objective: "Build the route candidate.",
    input_refs: ["event_brief:demo-night-tour"],
    tool_calls: [],
    tool_call_refs: ["tool_route_001"],
    structured_output: { route_points: ["rp001", "rp002"] },
    decision_reason: "Route uses seeded old-district points.",
    confidence: 0.91,
    requires_human_approval: false,
    schema_name: "PlanVersion",
    validation_status: "passed"
  },
  {
    step_id: "step_public_notice",
    run_id: run.run_id,
    agent_name: "PublicNoticeAgent",
    objective: "Draft visitor-safe wording.",
    input_refs: ["incident:inc_inventory_m001"],
    tool_calls: [],
    tool_call_refs: [],
    structured_output: { ready: true },
    decision_reason: "Public copy requires organizer approval.",
    confidence: 0.86,
    requires_human_approval: true,
    schema_name: "AgentDraft",
    validation_status: "passed"
  }
];

const toolCalls: AgentToolCall[] = [
  {
    tool_call_id: "tool_route_001",
    run_id: run.run_id,
    step_id: "step_route",
    tool_name: "route.build_static_route",
    input_payload: { rainy: false },
    output_payload: { route_count: 6 },
    status: "success",
    latency_ms: 0,
    error_summary: null
  }
];

const draft: AgentDraft = {
  draft_id: "draft_notice_001",
  event_id: "demo-night-tour",
  source_run_id: run.run_id,
  draft_type: "public_notice",
  locale: "zh-Hans",
  content: "Please continue to the indoor tea stop. Your route has been updated.",
  structured_payload: { affected_merchants: ["m001"], requires_organizer_approval: true },
  status: "draft",
  reviewed_by: null,
  reviewed_at: null,
  created_at: "2026-06-12T10:00:01Z"
};

function renderInEnglish(ui: ReactElement) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{ui}</I18nProvider>);
}

beforeEach(() => {
  localStorage.clear();
});

describe("v0.9 Agent evidence components", () => {
  test("AgentRunSummary renders trigger, mode, status, and approval boundary", () => {
    renderInEnglish(<AgentRunSummary run={run} />);

    expect(screen.getByText("Planning generation")).toBeInTheDocument();
    expect(screen.getByText("deterministic")).toBeInTheDocument();
    expect(screen.getByText("completed")).toBeInTheDocument();
    expect(screen.getByText("No fallback used")).toBeInTheDocument();
    expect(screen.getByText("Human approval remains required for release actions.")).toBeInTheDocument();
  });

  test("AgentStepTimeline renders specialist steps and approval flag", () => {
    renderInEnglish(<AgentStepTimeline steps={steps} />);

    expect(screen.getByText("RoutePlanningAgent")).toBeInTheDocument();
    expect(screen.getByText("PublicNoticeAgent")).toBeInTheDocument();
    expect(screen.getByText("Build the route candidate.")).toBeInTheDocument();
    expect(screen.getByText("Requires organizer approval")).toBeInTheDocument();
  });

  test("AgentToolCallList renders compact tool evidence", () => {
    renderInEnglish(<AgentToolCallList toolCalls={toolCalls} />);

    expect(screen.getByText("route.build_static_route")).toBeInTheDocument();
    expect(screen.getByText("success")).toBeInTheDocument();
    expect(screen.getByText(/route_count/)).toBeInTheDocument();
  });

  test("AgentDraftCard marks controlled draft boundary", () => {
    renderInEnglish(<AgentDraftCard draft={draft} />);

    expect(screen.getByText("Public notice draft")).toBeInTheDocument();
    expect(screen.getByText("draft")).toBeInTheDocument();
    expect(screen.getByText("Controlled draft, not published state")).toBeInTheDocument();
    expect(screen.getByText(/indoor tea stop/)).toBeInTheDocument();
  });

  test("AgentEvidencePanel renders empty and loaded states", () => {
    const { rerender } = renderInEnglish(
      <AgentEvidencePanel
        title="Agent evidence"
        description="Evidence created by specialist Agents."
        runs={[]}
        steps={[]}
        toolCalls={[]}
        drafts={[]}
        emptyMessage="Generate a route plan to create planning evidence."
      />
    );
    expect(screen.getByText("Generate a route plan to create planning evidence.")).toBeInTheDocument();

    rerender(
      <I18nProvider>
        <AgentEvidencePanel
          title="Agent evidence"
          description="Evidence created by specialist Agents."
          runs={[run]}
          steps={steps}
          toolCalls={toolCalls}
          drafts={[draft]}
          emptyMessage="Generate a route plan to create planning evidence."
        />
      </I18nProvider>
    );

    expect(screen.getByText("Agent evidence")).toBeInTheDocument();
    expect(screen.getByText("Specialist steps")).toBeInTheDocument();
    expect(screen.getByText("Tool evidence")).toBeInTheDocument();
    expect(screen.getByText("Controlled drafts")).toBeInTheDocument();
  });
});
