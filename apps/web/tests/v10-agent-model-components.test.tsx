import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { beforeEach, describe, expect, test } from "vitest";
import { AgentEvidencePanel, AgentModelEvidenceCard } from "../src/components/agent";
import { I18nProvider } from "../src/i18n";
import type { AgentEvaluation, AgentModelCall, AgentRun } from "../src/types";

const run: AgentRun = {
  run_id: "run_demo-night-tour_review",
  event_id: "demo-night-tour",
  trigger: "review_generation",
  mode: "qwen_draft",
  status: "fallback_completed",
  started_at: "2026-06-12T10:00:00Z",
  completed_at: "2026-06-12T10:00:01Z",
  fallback_used: true,
  fallback_reason: "schema_failed",
  final_output_ref: "draft:draft_review",
  error_summary: null
};

const modelCall: AgentModelCall = {
  model_call_id: "model_001",
  run_id: run.run_id,
  provider: "dashscope",
  model: "qwen-plus",
  prompt_template_id: "qwen_review_summary_v1",
  input_refs: ["metrics"],
  response_status: "schema_failed",
  parsed_output: null,
  fallback_used: true,
  error_summary: "structured_payload required",
  created_at: "2026-06-12T10:00:01Z"
};

const evaluation: AgentEvaluation = {
  evaluation_id: "eval_001",
  run_id: run.run_id,
  schema_pass: false,
  fallback_used: true,
  unsafe_mutation_attempted: false,
  human_approval_required: true,
  forbidden_public_terms_present: false,
  public_copy_ready: true,
  notes: ["schema fallback used"]
};

function renderEnglish(ui: ReactElement) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{ui}</I18nProvider>);
}

beforeEach(() => {
  localStorage.clear();
});

describe("v1.0 model evidence components", () => {
  test("AgentModelEvidenceCard shows provider status and fallback", () => {
    renderEnglish(<AgentModelEvidenceCard modelCalls={[modelCall]} evaluations={[evaluation]} />);

    expect(screen.getByText("Model draft evidence")).toBeInTheDocument();
    expect(screen.getByText("dashscope")).toBeInTheDocument();
    expect(screen.getByText("qwen-plus")).toBeInTheDocument();
    expect(screen.getByText("schema_failed")).toBeInTheDocument();
    expect(screen.getByText("Deterministic fallback used")).toBeInTheDocument();
    expect(screen.getByText("Validation evidence")).toBeInTheDocument();
  });

  test("AgentEvidencePanel renders deterministic empty model evidence state", () => {
    renderEnglish(
      <AgentEvidencePanel
        title="Review Agent evidence"
        description="Evidence created by specialist Agents."
        runs={[{ ...run, mode: "deterministic", fallback_used: false, fallback_reason: null }]}
        steps={[]}
        toolCalls={[]}
        drafts={[]}
        modelCalls={[]}
        evaluations={[]}
        emptyMessage="Generate a report to create review evidence."
      />
    );

    expect(screen.getAllByText("No model call recorded for this deterministic run.").length).toBeGreaterThan(0);
  });

  test("AgentEvidencePanel does not show deterministic no-model badge when model evidence exists", () => {
    renderEnglish(
      <AgentEvidencePanel
        title="Review Agent evidence"
        description="Evidence created by specialist Agents."
        runs={[run]}
        steps={[]}
        toolCalls={[]}
        drafts={[]}
        modelCalls={[modelCall]}
        evaluations={[evaluation]}
        emptyMessage="Generate a report to create review evidence."
      />
    );

    expect(screen.queryByText("No model call recorded for this deterministic run.")).not.toBeInTheDocument();
  });
});
