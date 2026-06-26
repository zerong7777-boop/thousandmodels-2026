import { afterEach, describe, expect, test, vi } from "vitest";
import { api } from "../src/api";
import type { ShadowOrchestrationResponse } from "../src/types";
import { jsonResponse } from "./authTestUtils";

const mutationOptions = (body?: unknown) => ({
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json", "X-Zhiyin-CSRF": "demo" },
  ...(body === undefined ? {} : { body: JSON.stringify(body) })
});

describe("v1.4 QwenPaw shadow orchestration API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("runQwenPawShadowOrchestration posts incident id and returns advisory bundle", async () => {
    const payload: ShadowOrchestrationResponse = {
      agent_run: {
        run_id: "run_demo-night-tour_qwenpaw_shadow_i001",
        event_id: "demo-night-tour",
        trigger: "incident_recovery",
        mode: "qwenpaw_workflow",
        status: "completed",
        started_at: "2026-06-21T00:00:00Z",
        completed_at: "2026-06-21T00:00:01Z",
        fallback_used: false,
        fallback_reason: null,
        final_output_ref: "qwenpaw_shadow_advisory:demo-night-tour:i001",
        error_summary: null
      },
      advisory_bundle: {
        authoritative_mutation: false,
        human_approval_required: true
      },
      steps: [],
      permission_decisions: []
    };
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    const result = await api.runQwenPawShadowOrchestration("demo-night-tour", "i001");

    expect(result.agent_run.mode).toBe("qwenpaw_workflow");
    expect(result.advisory_bundle).toEqual({
      authoritative_mutation: false,
      human_approval_required: true
    });
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/events/demo-night-tour/qwenpaw-shadow-orchestration/run",
      mutationOptions({ incident_id: "i001" })
    );
  });
});
