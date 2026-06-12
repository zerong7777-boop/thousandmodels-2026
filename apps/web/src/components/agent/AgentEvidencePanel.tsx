import type { AgentDraft, AgentEvaluation, AgentModelCall, AgentRun, AgentStep, AgentToolCall } from "../../types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { useI18n } from "../../i18n";
import { AgentDraftCard } from "./AgentDraftCard";
import { AgentModelEvidenceCard } from "./AgentModelEvidenceCard";
import { AgentRunSummary } from "./AgentRunSummary";
import { AgentSafetyChecklist } from "./AgentSafetyChecklist";
import { AgentStepTimeline } from "./AgentStepTimeline";
import { AgentToolCallList } from "./AgentToolCallList";

interface AgentEvidencePanelProps {
  title: string;
  description: string;
  runs: AgentRun[];
  steps: AgentStep[];
  toolCalls: AgentToolCall[];
  drafts: AgentDraft[];
  modelCalls?: AgentModelCall[];
  evaluations?: AgentEvaluation[];
  emptyMessage: string;
}

export function AgentEvidencePanel({
  title,
  description,
  runs,
  steps,
  toolCalls,
  drafts,
  modelCalls = [],
  evaluations = [],
  emptyMessage
}: AgentEvidencePanelProps) {
  const { t } = useI18n();
  const selectedRun = runs[0];
  if (!selectedRun) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-dashed border-slate-200 p-4 text-sm text-slate-500">
            {emptyMessage}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <AgentRunSummary run={selectedRun} />
        <AgentSafetyChecklist />
        <AgentModelEvidenceCard modelCalls={modelCalls} evaluations={evaluations} />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(320px,0.8fr)]">
          <AgentStepTimeline steps={steps} />
          <AgentToolCallList toolCalls={toolCalls} />
        </div>
        {drafts.length ? (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-ink">{t("organizer.agentEvidence.controlledDrafts")}</h3>
            <div className="grid gap-4 lg:grid-cols-2">
              {drafts.map((draft) => (
                <AgentDraftCard key={draft.draft_id} draft={draft} />
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
