import type { AgentDraft, AgentDraftType, AgentRun, AgentRunTrigger, AgentStep, AgentToolCall } from "../../types";

export function latestRunForTrigger(runs: AgentRun[], trigger: AgentRunTrigger): AgentRun | undefined {
  return [...runs]
    .filter((run) => run.trigger === trigger)
    .sort((a, b) => (b.completed_at ?? b.started_at).localeCompare(a.completed_at ?? a.started_at))[0];
}

export function stepsForRun(steps: AgentStep[], runId?: string | null): AgentStep[] {
  if (!runId) return steps;
  return steps.filter((step) => !step.run_id || step.run_id === runId);
}

export function draftsForRun(drafts: AgentDraft[], runId?: string | null, types?: AgentDraftType[]): AgentDraft[] {
  return drafts.filter((draft) => {
    const runMatches = !runId || draft.source_run_id === runId;
    const typeMatches = !types || types.includes(draft.draft_type);
    return runMatches && typeMatches;
  });
}

export function toolCallsForRun(toolCalls: AgentToolCall[], runId?: string | null): AgentToolCall[] {
  if (!runId) return toolCalls;
  return toolCalls.filter((call) => call.run_id === runId);
}

export function compactPayload(payload: Record<string, unknown> | undefined | null): string {
  if (!payload || !Object.keys(payload).length) return "{}";
  return JSON.stringify(payload, null, 0).slice(0, 180);
}

export function percentConfidence(value: number | undefined | null): string {
  if (typeof value !== "number") return "n/a";
  return `${Math.round(value * 100)}%`;
}
