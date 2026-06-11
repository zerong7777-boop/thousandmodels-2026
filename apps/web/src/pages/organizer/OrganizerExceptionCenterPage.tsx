import { useMemo, useState } from "react";
import { api } from "../../api";
import type { AgentToolCall, Incident, RecoveryProposal } from "../../types";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { AgentEvidencePanel, latestRunForTrigger, toolCallsForRun } from "../../components/agent";
import { ApprovalPanel, ProductPageHeader, RecoveryDiff, StatusPill } from "../../components/product";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

export function OrganizerExceptionCenterPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: exceptions } = useAsyncData(() => api.getIncidents(eventId), []);
  const { data: agentRuns } = useAsyncData(() => api.getAgentRuns(eventId), [], [eventId]);
  const recoveryRun = latestRunForTrigger(asArray(agentRuns), "incident_recovery");
  const { data: recoveryDrafts } = useAsyncData(() => api.getAgentDrafts(eventId), [], [eventId]);
  const { data: recoveryToolCalls } = useAsyncData<AgentToolCall[]>(
    () => (recoveryRun ? api.getAgentToolCalls(eventId, recoveryRun.run_id) : Promise.resolve([])),
    [],
    [eventId, recoveryRun?.run_id]
  );
  const incidents = asArray(exceptions) as Incident[];
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [proposal, setProposal] = useState<RecoveryProposal | null>(null);
  const [confirmationMessage, setConfirmationMessage] = useState<string | null>(null);
  const selectedIncident = useMemo(
    () => incidents.find((item) => item.incident_id === selectedIncidentId) ?? incidents[0],
    [incidents, selectedIncidentId]
  );

  const fallbackChanges = [
    t("organizer.exceptions.after1"),
    t("organizer.exceptions.after2"),
    t("organizer.exceptions.after3")
  ];
  const before = [
    t("organizer.exceptions.before1"),
    t("organizer.exceptions.before2"),
    t("organizer.exceptions.before3")
  ];
  const after = proposal?.recommended_changes?.length
    ? proposal.recommended_changes.map((item) => localizedDemoText(item, t))
    : fallbackChanges;

  const prepareProposal = async (incident: Incident) => {
    const nextProposal = await api.createRecoveryProposal(eventId, incident.incident_id);
    setProposal(nextProposal);
    setSelectedIncidentId(incident.incident_id);
    setConfirmationMessage(null);
  };

  const confirmRecovery = async () => {
    if (!proposal?.proposal_id) {
      setConfirmationMessage(t("organizer.exceptions.proposalRequired"));
      return;
    }
    await api.approveRecoveryProposal(eventId, proposal.proposal_id);
    setConfirmationMessage(t("organizer.exceptions.confirmedMessage"));
  };

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("organizer.exceptions.eyebrow")}
        title={t("organizer.exceptions.title")}
        description={t("organizer.exceptions.description")}
        meta={[t("organizer.exceptions.metaDecision"), t("organizer.exceptions.metaRoute"), t("organizer.exceptions.metaRelease")]}
        status={selectedIncident?.status ?? "open"}
      />

      <AgentEvidencePanel
        title={t("organizer.agentEvidence.recoveryTitle")}
        description={t("organizer.agentEvidence.recoveryDescription")}
        runs={recoveryRun ? [recoveryRun] : []}
        steps={[]}
        toolCalls={toolCallsForRun(asArray(recoveryToolCalls), recoveryRun?.run_id)}
        drafts={asArray(recoveryDrafts).filter(
          (draft) =>
            draft.source_run_id === recoveryRun?.run_id &&
            (draft.draft_type === "recovery_explanation" || draft.draft_type === "public_notice")
        )}
        emptyMessage={t("organizer.agentEvidence.emptyRecovery")}
      />

      <div className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.exceptions.queueTitle")}</CardTitle>
            <CardDescription>{t("organizer.exceptions.queueDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {incidents.map((item) => (
              <button
                className="w-full rounded-lg border border-slate-200 bg-white p-3 text-left transition hover:border-teal-300 hover:bg-teal-50"
                key={item.incident_id ?? item.event_id}
                onClick={() => {
                  setSelectedIncidentId(item.incident_id);
                  setConfirmationMessage(null);
                }}
                type="button"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="font-medium text-ink">
                      {localizedDemoText(item.trigger_detail ?? t("organizer.exceptions.merchantStatusChanged"), t)}
                    </div>
                    <div className="mt-1 text-sm text-slate-600">
                      {t("organizer.exceptions.affectedMerchant")}: {asArray(item.affected_merchants).join(", ") || "m001"}
                    </div>
                  </div>
                  <StatusPill tone={item.severity === "high" ? "danger" : "warning"}>
                    {localizedStatus(item.status ?? "open", t)}
                  </StatusPill>
                </div>
              </button>
            ))}
            {!incidents.length ? (
              <div className="rounded-md border border-dashed border-slate-200 p-4 text-sm text-slate-500">
                {t("organizer.exceptions.emptyQueue")}
              </div>
            ) : null}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("organizer.exceptions.impactScope")}</CardTitle>
              <CardDescription>{t("organizer.exceptions.impactDescription")}</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                  {t("organizer.exceptions.affectedMerchant")}
                </div>
                <div className="mt-2 text-lg font-semibold text-ink">
                  {asArray(selectedIncident?.affected_merchants).join(", ") || "m001"}
                </div>
                <p className="mt-2 text-sm leading-5 text-slate-600">{t("organizer.exceptions.merchantImpactDetail")}</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                  {t("organizer.exceptions.affectedStop")}
                </div>
                <div className="mt-2 text-lg font-semibold text-ink">
                  {asArray(selectedIncident?.affected_route_points).join(", ") || "rp001"}
                </div>
                <p className="mt-2 text-sm leading-5 text-slate-600">{t("organizer.exceptions.stopImpactDetail")}</p>
              </div>
            </CardContent>
          </Card>

          <RecoveryDiff before={before} after={after} />
        </div>

        <div className="space-y-4">
          <ApprovalPanel
            actionLabel={t("organizer.exceptions.confirmAction")}
            consequence={t("organizer.exceptions.confirmConsequence")}
            description={t("organizer.exceptions.confirmDescription")}
            onApprove={() => void confirmRecovery()}
            title={t("organizer.exceptions.confirmTitle")}
          >
            {selectedIncident ? (
              <Button size="sm" variant="secondary" onClick={() => void prepareProposal(selectedIncident)}>
                {t("organizer.exceptions.prepareSuggestion")}
              </Button>
            ) : null}
          </ApprovalPanel>

          <Card>
            <CardHeader>
              <CardTitle>{t("organizer.exceptions.publicNoticePreview")}</CardTitle>
              <CardDescription>{t("organizer.exceptions.publicNoticeDescription")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm leading-5 text-blue-900">
                {proposal?.public_notice_patch
                  ? localizedDemoText(proposal.public_notice_patch, t)
                  : t("organizer.exceptions.fallbackNotice")}
              </div>
              {confirmationMessage ? <StatusPill tone="success">{confirmationMessage}</StatusPill> : null}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
