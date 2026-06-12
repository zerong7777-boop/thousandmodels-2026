import { afterEach, describe, expect, test, vi } from "vitest";
import { api } from "../src/api";
import type { AgentEvaluation, AgentModelCall } from "../src/types";
import { jsonResponse } from "./authTestUtils";

describe("v1.0 Agent model evidence API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("getAgentModelCalls reads organizer model evidence", async () => {
    const payload: AgentModelCall[] = [
      {
        model_call_id: "model_001",
        run_id: "run_demo-night-tour_review",
        provider: "dashscope",
        model: "qwen-plus",
        prompt_template_id: "qwen_review_summary_v1",
        input_refs: ["metrics"],
        response_status: "success",
        parsed_output: { content: "Evidence-backed summary" },
        fallback_used: false,
        error_summary: null,
        created_at: "2026-06-12T10:00:01Z"
      }
    ];
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    const result = await api.getAgentModelCalls("demo-night-tour", "run_demo-night-tour_review");

    expect(result).toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/events/demo-night-tour/agent-runs/run_demo-night-tour_review/model-calls",
      { credentials: "include" }
    );
  });

  test("getAgentEvaluations reads validation evidence", async () => {
    const payload: AgentEvaluation[] = [
      {
        evaluation_id: "eval_001",
        run_id: "run_demo-night-tour_review",
        schema_pass: true,
        fallback_used: false,
        unsafe_mutation_attempted: false,
        human_approval_required: true,
        forbidden_public_terms_present: false,
        public_copy_ready: true,
        notes: ["public copy passed"]
      }
    ];
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    const result = await api.getAgentEvaluations("demo-night-tour", "run_demo-night-tour_review");

    expect(result).toEqual(payload);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/events/demo-night-tour/agent-runs/run_demo-night-tour_review/evaluations",
      { credentials: "include" }
    );
  });
});
