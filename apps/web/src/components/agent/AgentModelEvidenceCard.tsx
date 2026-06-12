import type { AgentEvaluation, AgentModelCall } from "../../types";
import { Badge } from "../../ui/badge";
import { useI18n } from "../../i18n";

interface AgentModelEvidenceCardProps {
  modelCalls: AgentModelCall[];
  evaluations: AgentEvaluation[];
}

export function AgentModelEvidenceCard({ modelCalls, evaluations }: AgentModelEvidenceCardProps) {
  const { t } = useI18n();
  const validModelCalls = modelCalls.filter((call) => call.model_call_id);
  const validEvaluations = evaluations.filter((evaluation) => evaluation.evaluation_id);

  return (
    <section className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-ink">{t("organizer.agentEvidence.model.title")}</h3>
        {validModelCalls.length ? (
          <Badge variant={validModelCalls.some((call) => call.fallback_used) ? "warning" : "success"}>
            {validModelCalls.some((call) => call.fallback_used)
              ? t("organizer.agentEvidence.model.fallback")
              : t("organizer.agentEvidence.noFallback")}
          </Badge>
        ) : null}
      </div>

      {!validModelCalls.length ? (
        <p className="mt-3 text-sm text-slate-500">{t("organizer.agentEvidence.model.none")}</p>
      ) : (
        <div className="mt-3 grid gap-3 lg:grid-cols-2">
          {validModelCalls.map((call) => (
            <div key={call.model_call_id} className="rounded-md border border-slate-200 bg-white p-3">
              <div className="flex flex-wrap gap-2">
                <Badge variant="neutral">{call.provider}</Badge>
                <Badge variant="neutral">{call.model}</Badge>
                <Badge variant={call.response_status === "success" ? "success" : "warning"}>
                  {call.response_status}
                </Badge>
              </div>
              <div className="mt-2 text-xs text-slate-500">
                {t("organizer.agentEvidence.model.template", { template: call.prompt_template_id })}
              </div>
              {call.error_summary ? <p className="mt-2 text-sm text-slate-600">{call.error_summary}</p> : null}
            </div>
          ))}
        </div>
      )}

      {validEvaluations.length ? (
        <div className="mt-3 rounded-md border border-slate-200 bg-white p-3">
          <div className="text-sm font-semibold text-ink">{t("organizer.agentEvidence.model.validation")}</div>
          <ul className="mt-2 space-y-1 text-xs text-slate-600">
            {validEvaluations.flatMap((evaluation) => evaluation.notes).map((note, index) => (
              <li key={`${note}-${index}`}>{note}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
