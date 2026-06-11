import type { AgentRun } from "../../types";
import { Badge } from "../../ui/badge";
import { useI18n } from "../../i18n";

export function AgentRunSummary({ run }: { run: AgentRun }) {
  const { t } = useI18n();
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
            {t("organizer.agentEvidence.runSummary")}
          </div>
          <h3 className="mt-1 text-base font-semibold text-ink">
            {t(`organizer.agentEvidence.trigger.${run.trigger}`)}
          </h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="neutral">{run.mode}</Badge>
          <Badge variant={run.status === "completed" ? "success" : "neutral"}>{run.status}</Badge>
          <Badge variant={run.fallback_used ? "warning" : "success"}>
            {run.fallback_used ? t("organizer.agentEvidence.fallbackUsed") : t("organizer.agentEvidence.noFallback")}
          </Badge>
        </div>
      </div>
      <div className="mt-3 grid gap-2 text-sm text-slate-600 md:grid-cols-2">
        <span>{t("organizer.agentEvidence.started", { time: run.started_at })}</span>
        <span>{t("organizer.agentEvidence.completed", { time: run.completed_at ?? "-" })}</span>
        <span className="md:col-span-2">
          {t("organizer.agentEvidence.finalOutput", { ref: run.final_output_ref ?? "-" })}
        </span>
      </div>
      <p className="mt-3 text-sm font-medium text-slate-700">
        {t("organizer.agentEvidence.approvalRequired")}
      </p>
    </div>
  );
}
