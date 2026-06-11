import { afterEach, describe, expect, test, vi } from "vitest";
import { api } from "../src/api";
import type { AgentDraft, AgentRun, AgentToolCall } from "../src/types";
import { jsonResponse } from "./authTestUtils";

describe("v0.9 Agent evidence API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("getAgentRuns reads organizer Agent runs", async () => {
    const payload: AgentRun[] = [
      {
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
      }
    ];
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    const result = await api.getAgentRuns("demo-night-tour");

    expect(result).toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith("/api/events/demo-night-tour/agent-runs", {
      credentials: "include"
    });
  });

  test("getAgentDrafts supports draft_type filtering", async () => {
    const payload: AgentDraft[] = [
      {
        draft_id: "draft_review_001",
        event_id: "demo-night-tour",
        source_run_id: "run_demo-night-tour_review",
        draft_type: "review_summary",
        locale: "mixed",
        content: "Evidence: metrics=h5_visits; Recommendation: improve backup threshold.",
        structured_payload: { metrics: ["h5_visits"], incidents: ["inc_inventory_m001"] },
        status: "draft",
        reviewed_by: null,
        reviewed_at: null,
        created_at: "2026-06-12T10:00:01Z"
      }
    ];
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    const result = await api.getAgentDrafts("demo-night-tour", "review_summary");

    expect(result).toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/events/demo-night-tour/agent-drafts?draft_type=review_summary",
      { credentials: "include" }
    );
  });

  test("getAgentToolCalls reads calls for a specific run", async () => {
    const payload: AgentToolCall[] = [
      {
        tool_call_id: "tool_route_001",
        run_id: "run_demo-night-tour_plan",
        step_id: "step_route",
        tool_name: "route.build_static_route",
        input_payload: { rainy: false },
        output_payload: { route_count: 6 },
        status: "success",
        latency_ms: 0,
        error_summary: null
      }
    ];
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    const result = await api.getAgentToolCalls("demo-night-tour", "run_demo-night-tour_plan");

    expect(result).toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/events/demo-night-tour/agent-runs/run_demo-night-tour_plan/tool-calls",
      { credentials: "include" }
    );
  });
});
