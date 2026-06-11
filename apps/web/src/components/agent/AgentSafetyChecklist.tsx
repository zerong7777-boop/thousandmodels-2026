import { Badge } from "../../ui/badge";
import { useI18n } from "../../i18n";

export function AgentSafetyChecklist() {
  const { t } = useI18n();
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
      <div className="font-semibold">{t("organizer.agentEvidence.safetyBoundary")}</div>
      <p className="mt-2">{t("organizer.agentEvidence.boundarySummary")}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Badge variant="warning">{t("organizer.agentEvidence.humanApprovalBoundary")}</Badge>
        <Badge variant="neutral">{t("organizer.agentEvidence.noModelCall")}</Badge>
      </div>
    </div>
  );
}
