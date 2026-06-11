import type { AgentDraft } from "../../types";
import { Badge } from "../../ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { useI18n } from "../../i18n";
import { compactPayload } from "./agentEvidenceUtils";

export function AgentDraftCard({ draft }: { draft: AgentDraft }) {
  const { t } = useI18n();
  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle>{t(`organizer.agentEvidence.draft.${draft.draft_type}`)}</CardTitle>
          <div className="flex flex-wrap gap-2">
            <Badge variant="neutral">{draft.locale}</Badge>
            <Badge variant="warning">{draft.status}</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm leading-6 text-slate-700">{draft.content}</p>
        <Badge variant="warning">{t("organizer.agentEvidence.notPublished")}</Badge>
        <div>
          <div className="mb-1 text-xs font-semibold uppercase tracking-normal text-slate-500">
            {t("organizer.agentEvidence.payloadSummary")}
          </div>
          <code className="block rounded bg-slate-100 p-2 text-xs text-slate-700">
            {compactPayload(draft.structured_payload)}
          </code>
        </div>
      </CardContent>
    </Card>
  );
}
