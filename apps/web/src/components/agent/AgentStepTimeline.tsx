import type { AgentStep } from "../../types";
import { Badge } from "../../ui/badge";
import { useI18n } from "../../i18n";
import { percentConfidence } from "./agentEvidenceUtils";

export function AgentStepTimeline({ steps }: { steps: AgentStep[] }) {
  const { t } = useI18n();
  if (!steps.length) {
    return <p className="text-sm text-slate-500">{t("organizer.agentEvidence.partialEvidence")}</p>;
  }
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-ink">{t("organizer.agentEvidence.specialistSteps")}</h3>
      {steps.map((step, index) => (
        <div key={step.step_id ?? `${step.agent_name}-${index}`} className="rounded-lg border border-slate-200 bg-white p-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <div className="font-medium text-ink">{step.agent_name}</div>
              {step.objective ? <p className="mt-1 text-sm text-slate-600">{step.objective}</p> : null}
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="neutral">
                {t("organizer.agentEvidence.confidence", { value: percentConfidence(step.confidence) })}
              </Badge>
              {step.requires_human_approval ? (
                <Badge variant="warning">{t("organizer.agentEvidence.requiresApproval")}</Badge>
              ) : null}
            </div>
          </div>
          <p className="mt-2 text-sm text-slate-700">{step.decision_reason}</p>
          <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
            <span>{t("organizer.agentEvidence.inputRefs", { count: step.input_refs?.length ?? 0 })}</span>
            <span>
              {t("organizer.agentEvidence.toolCalls", {
                count: step.tool_call_refs?.length ?? step.tool_calls?.length ?? 0
              })}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
