import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../../api";
import type {
  AgentToolCall,
  Incident,
  OperationSuggestion,
  OperationSuggestionsResponse,
  RecoveryProposal,
  ShadowOrchestrationResponse
} from "../../types";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { AgentEvidencePanel, latestRunForTrigger, toolCallsForRun } from "../../components/agent";
import { ApprovalPanel, ProductPageHeader, RecoveryDiff, StatusPill } from "../../components/product";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

const suggestionTypeLabels: Record<string, string> = {
  route_adjustment: "organizer.exceptions.suggestionType.routeAdjustment",
  merchant_capacity: "organizer.exceptions.suggestionType.merchantCapacity",
  coupon_rebalance: "organizer.exceptions.suggestionType.couponRebalance",
  public_notice: "organizer.exceptions.suggestionType.publicNotice",
  extension_task: "organizer.exceptions.suggestionType.extensionTask"
};

export function OrganizerExceptionCenterPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: exceptions } = useAsyncData(() => api.getIncidents(eventId), [], [eventId]);
  const { data: agentRuns } = useAsyncData(() => api.getAgentRuns(eventId), [], [eventId]);
  const recoveryRun = latestRunForTrigger(asArray(agentRuns), "incident_recovery");
  const { data: recoveryDrafts } = useAsyncData(() => api.getAgentDrafts(eventId), [], [eventId]);
  const { data: recoveryToolCalls } = useAsyncData<AgentToolCall[]>(
    () => (recoveryRun ? api.getAgentToolCalls(eventId, recoveryRun.run_id) : Promise.resolve([])),
    [],
    [eventId, recoveryRun?.run_id]
  );
  const { data: recoveryModelCalls } = useAsyncData(
    () => (recoveryRun ? api.getAgentModelCalls(eventId, recoveryRun.run_id) : Promise.resolve([])),
    [],
    [eventId, recoveryRun?.run_id]
  );
  const { data: recoveryEvaluations } = useAsyncData(
    () => (recoveryRun ? api.getAgentEvaluations(eventId, recoveryRun.run_id) : Promise.resolve([])),
    [],
    [eventId, recoveryRun?.run_id]
  );
  const incidents = asArray(exceptions) as Incident[];
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [proposal, setProposal] = useState<RecoveryProposal | null>(null);
  const [confirmationMessage, setConfirmationMessage] = useState<string | null>(null);
  const [recoveryError, setRecoveryError] = useState<string | null>(null);
  const [operationSuggestions, setOperationSuggestions] = useState<OperationSuggestion[]>([]);
  const [suggestionMessage, setSuggestionMessage] = useState<string | null>(null);
  const [shadowRun, setShadowRun] = useState<ShadowOrchestrationResponse | null>(null);
  const [shadowError, setShadowError] = useState<string | null>(null);
  const [shadowBusy, setShadowBusy] = useState(false);
  const suggestionsRequestRef = useRef(0);
  const proposalRequestRef = useRef(0);
  const shadowRequestRef = useRef(0);
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

  useEffect(() => {
    let active = true;
    const requestId = ++suggestionsRequestRef.current;
    api
      .getOperationSuggestions(eventId)
      .then((response) => {
        if (active && requestId === suggestionsRequestRef.current) {
          setOperationSuggestions(asArray(response.suggestions));
        }
      })
      .catch(() => {
        if (active && requestId === suggestionsRequestRef.current) {
          setOperationSuggestions([]);
        }
      });
    return () => {
      active = false;
    };
  }, [eventId]);

  const refreshOperationSuggestions = async () => {
    const requestId = ++suggestionsRequestRef.current;
    const response = await api.getOperationSuggestions(eventId);
    if (requestId === suggestionsRequestRef.current) {
      setOperationSuggestions(asArray(response.suggestions));
    }
  };

  const prepareProposal = async (incident: Incident) => {
    setSelectedIncidentId(incident.incident_id);
    setConfirmationMessage(null);
    setRecoveryError(null);
    setShadowRun(null);
    setShadowError(null);
    const requestId = ++proposalRequestRef.current;
    try {
      const nextProposal = await api.createRecoveryProposal(eventId, incident.incident_id);
      if (requestId === proposalRequestRef.current) {
        setProposal(nextProposal);
      }
    } catch {
      if (requestId === proposalRequestRef.current) {
        setRecoveryError(t("organizer.exceptions.prepareSuggestionError"));
      }
    }
  };

  const confirmRecovery = async () => {
    if (!proposal?.proposal_id) {
      setConfirmationMessage(t("organizer.exceptions.proposalRequired"));
      setRecoveryError(null);
      return;
    }
    setRecoveryError(null);
    const requestId = proposalRequestRef.current;
    try {
      await api.approveRecoveryProposal(eventId, proposal.proposal_id);
      if (requestId === proposalRequestRef.current) {
        setConfirmationMessage(t("organizer.exceptions.confirmedMessage"));
      }
    } catch {
      if (requestId === proposalRequestRef.current) {
        setConfirmationMessage(null);
        setRecoveryError(t("organizer.exceptions.confirmRecoveryError"));
      }
    }
  };

  const runShadowOrchestration = async () => {
    const requestId = ++shadowRequestRef.current;
    setShadowBusy(true);
    setShadowError(null);
    try {
      const response = await api.runQwenPawShadowOrchestration(eventId, selectedIncident?.incident_id);
      if (requestId === shadowRequestRef.current) {
        setShadowRun(response);
      }
    } catch {
      if (requestId === shadowRequestRef.current) {
        setShadowRun(null);
        setShadowError(t("organizer.qwenpaw.failed"));
      }
    } finally {
      if (requestId === shadowRequestRef.current) {
        setShadowBusy(false);
      }
    }
  };

  const generateOperationSuggestions = async () => {
    setSuggestionMessage(null);
    const requestId = ++suggestionsRequestRef.current;
    try {
      const response = await api.generateOperationSuggestions(eventId);
      if (requestId === suggestionsRequestRef.current) {
        setOperationSuggestions(asArray(response.suggestions));
      }
    } catch {
      setSuggestionMessage(t("organizer.exceptions.operationSuggestionsRefreshFailed"));
      await refreshOperationSuggestions().catch(() => undefined);
    }
  };

  const approveOperationSuggestion = async (suggestionId: string) => {
    setSuggestionMessage(null);
    try {
      const approved = await api.approveOperationSuggestion(eventId, suggestionId);
      setOperationSuggestions((items) => items.map((item) => (item.id === approved.id ? approved : item)));
    } catch {
      setSuggestionMessage(t("organizer.exceptions.operationSuggestionStale"));
      await refreshOperationSuggestions().catch(() => undefined);
    }
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
        modelCalls={asArray(recoveryModelCalls)}
        evaluations={asArray(recoveryEvaluations)}
        emptyMessage={t("organizer.agentEvidence.emptyRecovery")}
      />

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <CardTitle>{t("organizer.exceptions.operationSuggestionsTitle")}</CardTitle>
              <CardDescription>{t("organizer.exceptions.operationSuggestionsDescription")}</CardDescription>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button size="sm" onClick={() => void generateOperationSuggestions()}>
                {t("organizer.exceptions.generateOperationSuggestions")}
              </Button>
              <Button
                disabled={shadowBusy}
                size="sm"
                variant="secondary"
                onClick={() => void runShadowOrchestration()}
              >
                {t("organizer.qwenpaw.run")}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid gap-3 lg:grid-cols-2">
          {shadowError ? (
            <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-900 lg:col-span-2">
              {shadowError}
            </div>
          ) : null}
          {shadowRun ? (
            <div className="rounded-md border border-slate-200 bg-slate-50 p-4 lg:col-span-2">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="font-medium text-ink">{t("organizer.qwenpaw.title")}</div>
                  <div className="mt-1 truncate text-xs text-slate-500">
                    {shadowRun.agent_run.final_output_ref ?? shadowRun.agent_run.run_id}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {shadowRun.advisory_bundle.authoritative_mutation === false ? (
                    <StatusPill tone="info">{t("organizer.qwenpaw.advisoryOnly")}</StatusPill>
                  ) : null}
                  {shadowRun.advisory_bundle.human_approval_required === true ? (
                    <StatusPill tone="warning">{t("organizer.qwenpaw.requiresApproval")}</StatusPill>
                  ) : null}
                  {shadowRun.advisory_bundle.authoritative_mutation === false ? (
                    <StatusPill tone="success">{t("organizer.qwenpaw.noMutation")}</StatusPill>
                  ) : null}
                  {shadowRun.agent_run.fallback_used ? (
                    <StatusPill tone="warning">{t("organizer.qwenpaw.fallbackUsed")}</StatusPill>
                  ) : null}
                </div>
              </div>
              <div className="mt-4">
                <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                  {t("organizer.qwenpaw.permissionDecisions")}
                </div>
                {shadowRun.permission_decisions.length ? (
                  <ul className="mt-2 grid gap-2">
                    {shadowRun.permission_decisions.map((decision, index) => (
                      <li
                        className="flex flex-wrap items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700"
                        key={`${decision.permission}-${decision.reason}-${index}`}
                      >
                        <Badge variant={decision.allowed ? "success" : "danger"}>{decision.permission}</Badge>
                        <span>{decision.reason}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="mt-2 rounded-md border border-dashed border-slate-200 bg-white p-3 text-sm text-slate-500">
                    {t("organizer.qwenpaw.empty")}
                  </div>
                )}
              </div>
            </div>
          ) : null}
          {suggestionMessage ? (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900 lg:col-span-2">
              {suggestionMessage}
            </div>
          ) : null}
          {operationSuggestions.map((suggestion) => (
            <div key={suggestion.id} className="rounded-md border border-slate-200 p-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <div className="font-medium">{localizedDemoText(suggestion.title, t)}</div>
                  <div className="mt-1 text-sm text-slate-600">
                    {t(suggestionTypeLabels[suggestion.suggestion_type] ?? "organizer.exceptions.suggestionType.other")}
                  </div>
                </div>
                <Badge variant={suggestion.status === "approved" || suggestion.status === "applied" ? "success" : "neutral"}>
                  {localizedStatus(suggestion.status === "pending_approval" ? "pending" : suggestion.status, t)}
                </Badge>
              </div>
              <p className="mt-2 text-sm leading-5 text-slate-700">{localizedDemoText(suggestion.rationale, t)}</p>
              <div className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                <span>
                  {t("organizer.exceptions.impactedMerchants", {
                    value: asArray(suggestion.impacted_merchants).join(", ") || t("common.unavailable")
                  })}
                </span>
                <span>{t("organizer.exceptions.evidenceCount", { count: asArray(suggestion.evidence_refs).length })}</span>
              </div>
              <Button
                className="mt-3"
                disabled={suggestion.status === "approved" || suggestion.status === "applied"}
                size="sm"
                variant="secondary"
                onClick={() => void approveOperationSuggestion(suggestion.id)}
              >
                {t("organizer.exceptions.approveSuggestion")}
              </Button>
            </div>
          ))}
          {!operationSuggestions.length ? (
            <div className="rounded-md border border-dashed border-slate-200 p-4 text-sm text-slate-500">
              {t("organizer.exceptions.operationSuggestionsEmpty")}
            </div>
          ) : null}
        </CardContent>
      </Card>

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
                  ++proposalRequestRef.current;
                  ++shadowRequestRef.current;
                  setSelectedIncidentId(item.incident_id);
                  setProposal(null);
                  setConfirmationMessage(null);
                  setRecoveryError(null);
                  setShadowRun(null);
                  setShadowError(null);
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
              {recoveryError ? <StatusPill tone="danger">{recoveryError}</StatusPill> : null}
              {confirmationMessage ? <StatusPill tone="success">{confirmationMessage}</StatusPill> : null}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
