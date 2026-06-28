import { useEffect, useRef, useState } from "react";
import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { localizedDemoList, localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { AgentEvidencePanel, latestRunForTrigger, stepsForRun, toolCallsForRun } from "../../components/agent";
import { MetricTile, ProductPageHeader, WorkflowStepper } from "../../components/product";
import type { AgentToolCall, EventPage, EventSummary, MerchantEdgePackagesResponse } from "../../types";
import { asArray, useAsyncData } from "../productUtils";

function countPackageTouchpoints(packages: MerchantEdgePackagesResponse["packages"]) {
  return packages.reduce((total, item) => total + asArray(item.touchpoints).length, 0);
}

function countPackageCoupons(packages: MerchantEdgePackagesResponse["packages"]) {
  return packages.reduce((total, item) => total + asArray(item.coupon_rules).length, 0);
}

function merchantLabel(merchantId: string, t: (key: string) => string) {
  if (merchantId === "m001") return localizedDemoText("Merchant m001", t);
  return localizedDemoText(merchantId, t) || merchantId;
}

function getEventLoader() {
  return (api as { getEvent?: (eventId: string) => Promise<EventSummary> }).getEvent;
}

function messageFromError(error: unknown, fallback: string): string {
  const raw = error instanceof Error ? error.message : typeof error === "string" ? error : "";
  if (!raw.trim()) return fallback;

  try {
    const parsed = JSON.parse(raw) as { detail?: unknown; message?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (typeof parsed.message === "string") return parsed.message;
  } catch {
    // Non-JSON backend errors are already displayable text.
  }

  return raw;
}

export function OrganizerEventWorkspacePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const [refreshKey, setRefreshKey] = useState(0);
  const [actionFeedback, setActionFeedback] = useState<{ tone: "success" | "danger"; text: string } | null>(null);
  const [suggestionFeedback, setSuggestionFeedback] = useState<{ tone: "success" | "danger"; text: string } | null>(null);
  const [eventSummary, setEventSummary] = useState<EventSummary | null>(null);
  const [eventContextError, setEventContextError] = useState(false);
  const { data: plans } = useAsyncData(() => api.getPlanVersions(eventId), [], [eventId, refreshKey]);
  const { data: traces } = useAsyncData(() => api.getAgentTraces(eventId), [], [eventId, refreshKey]);
  const { data: tasks } = useAsyncData(() => api.getMerchantTasks(eventId), [], [eventId, refreshKey]);
  const { data: agentRuns } = useAsyncData(() => api.getAgentRuns(eventId), [], [eventId, refreshKey]);
  const [eventPage, setEventPage] = useState<EventPage | null>(null);
  const [edgePackages, setEdgePackages] = useState<MerchantEdgePackagesResponse>({ packages: [] });
  const eventPageRequestRef = useRef(0);
  const edgePackagesRequestRef = useRef(0);
  const planList = asArray(plans);
  const traceList = asArray(traces);
  const taskList = asArray(tasks);
  const packageList = asArray(edgePackages.packages);
  const touchpointCount = countPackageTouchpoints(packageList);
  const couponRuleCount = countPackageCoupons(packageList);
  const planningRun = latestRunForTrigger(asArray(agentRuns), "planning_generation");
  const { data: planningToolCalls } = useAsyncData<AgentToolCall[]>(
    () => (planningRun ? api.getAgentToolCalls(eventId, planningRun.run_id) : Promise.resolve([])),
    [],
    [eventId, planningRun?.run_id]
  );
  const { data: planningModelCalls } = useAsyncData(
    () => (planningRun ? api.getAgentModelCalls(eventId, planningRun.run_id) : Promise.resolve([])),
    [],
    [eventId, planningRun?.run_id]
  );
  const { data: planningEvaluations } = useAsyncData(
    () => (planningRun ? api.getAgentEvaluations(eventId, planningRun.run_id) : Promise.resolve([])),
    [],
    [eventId, planningRun?.run_id]
  );
  const planningSteps = stepsForRun(
    traceList.flatMap((trace) => asArray(trace.steps)),
    planningRun?.run_id
  );
  const currentPlan = planList.find((plan) => plan.status === "approved") ?? planList[0];
  const readinessCount = taskList.filter((task) => task.task_status === "active").length;
  const currentStatus = currentPlan?.status ?? "draft";
  const eventStatus = eventSummary?.status ?? currentStatus;
  const workspaceTitle = eventSummary ? localizedDemoText(eventSummary.title, t) : t("organizer.workspace.title");
  const workspaceDescription = eventSummary
    ? `${localizedDemoText(eventSummary.area, t)} / ${eventSummary.date} / ${eventSummary.time_window}`
    : t("organizer.workspace.description");
  const approvalState =
    currentPlan?.status === "approved" ? t("common.status.confirmed") : t("organizer.workspace.needsConfirmation");

  useEffect(() => {
    let active = true;
    const getEvent = getEventLoader();
    setEventContextError(false);

    if (!getEvent) {
      setEventSummary(null);
      return () => {
        active = false;
      };
    }

    getEvent(eventId)
      .then((nextEventSummary) => {
        if (active) setEventSummary(nextEventSummary);
      })
      .catch(() => {
        if (active) {
          setEventSummary(null);
          setEventContextError(true);
        }
      });

    return () => {
      active = false;
    };
  }, [eventId, refreshKey]);

  useEffect(() => {
    let active = true;
    const requestId = ++eventPageRequestRef.current;
    api
      .getEventPage(eventId)
      .then((nextPage) => {
        if (active && requestId === eventPageRequestRef.current) setEventPage(nextPage);
      })
      .catch(() => {
        if (active && requestId === eventPageRequestRef.current) setEventPage(null);
      });
    return () => {
      active = false;
    };
  }, [eventId]);

  useEffect(() => {
    let active = true;
    const requestId = ++edgePackagesRequestRef.current;
    api
      .getMerchantEdgePackages(eventId)
      .then((nextPackages) => {
        if (active && requestId === edgePackagesRequestRef.current) setEdgePackages(nextPackages);
      })
      .catch(() => {
        if (active && requestId === edgePackagesRequestRef.current) setEdgePackages({ packages: [] });
      });
    return () => {
      active = false;
    };
  }, [eventId]);

  const draftEventPage = async () => {
    const requestId = ++eventPageRequestRef.current;
    setActionFeedback(null);
    try {
      const nextPage = await api.draftEventPage(eventId);
      if (requestId === eventPageRequestRef.current) setEventPage(nextPage);
    } catch (error) {
      if (requestId === eventPageRequestRef.current) {
        setActionFeedback({
          tone: "danger",
          text: messageFromError(error, t("organizer.workspace.eventActionError"))
        });
      }
    }
  };

  const publishEventPage = async () => {
    const requestId = ++eventPageRequestRef.current;
    setActionFeedback(null);
    try {
      const nextPage = await api.publishEventPage(eventId);
      if (requestId === eventPageRequestRef.current) setEventPage(nextPage);
    } catch (error) {
      if (requestId === eventPageRequestRef.current) {
        setActionFeedback({
          tone: "danger",
          text: messageFromError(error, t("organizer.workspace.eventActionError"))
        });
      }
    }
  };

  const generateEdgePackages = async () => {
    const requestId = ++edgePackagesRequestRef.current;
    setActionFeedback(null);
    try {
      const nextPackages = await api.generateMerchantEdgePackages(eventId);
      if (requestId === edgePackagesRequestRef.current) setEdgePackages(nextPackages);
    } catch (error) {
      if (requestId === edgePackagesRequestRef.current) {
        setActionFeedback({
          tone: "danger",
          text: messageFromError(error, t("organizer.workspace.eventActionError"))
        });
      }
    }
  };

  const refreshWorkspace = () => setRefreshKey((current) => current + 1);

  const buildPlan = async () => {
    setActionFeedback(null);
    try {
      await api.generatePlan(eventId);
      refreshWorkspace();
      setActionFeedback({ tone: "success", text: t("organizer.workspace.planBuildSuccess") });
    } catch {
      setActionFeedback({ tone: "danger", text: t("organizer.workspace.planBuildError") });
    }
  };

  const approvePlan = async () => {
    setActionFeedback(null);
    try {
      await api.approvePlanVersion(eventId, currentPlan?.version ?? 1);
      refreshWorkspace();
      setActionFeedback({ tone: "success", text: t("organizer.workspace.planApproveSuccess") });
    } catch {
      setActionFeedback({ tone: "danger", text: t("organizer.workspace.planApproveError") });
    }
  };

  const generateOperationSuggestions = async () => {
    setSuggestionFeedback(null);
    try {
      const response = await api.generateOperationSuggestions(eventId);
      setSuggestionFeedback({
        tone: "success",
        text: t("organizer.workspace.operationSuggestionsSuccess", {
          count: asArray(response.suggestions).length
        })
      });
    } catch {
      setSuggestionFeedback({ tone: "danger", text: t("organizer.workspace.operationSuggestionsError") });
    }
  };

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("organizer.workspace.eyebrow")}
        title={workspaceTitle}
        description={workspaceDescription}
        meta={[
          t("organizer.workspace.eventStatusMeta", { status: localizedStatus(eventStatus, t) }),
          eventSummary
            ? t("organizer.events.publicRelease", {
                status: localizedStatus(eventSummary.public_release_status, t)
              })
            : null,
          t("organizer.workspace.planStatusMeta", { status: localizedStatus(currentStatus, t) }),
          t("organizer.workspace.readinessMeta", { ready: readinessCount, total: taskList.length || 1 }),
          t("organizer.workspace.approvalMeta", { state: approvalState })
        ]}
        status={eventStatus}
        actions={
          <div role="region" aria-label={t("organizer.workspace.actionsLabel")} className="flex flex-wrap gap-2">
            <Button onClick={() => void buildPlan()}>{t("organizer.workspace.buildPlan")}</Button>
            <Button variant="secondary" onClick={() => void approvePlan()}>
              {t("organizer.workspace.confirmPlan")}
            </Button>
          </div>
        }
      />

      {eventContextError ? (
        <div
          role="alert"
          className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"
        >
          <span>{t("organizer.workspace.eventContextMissing")}</span>
          <Button asChild size="sm" variant="secondary">
            <a href="/organizer/events">{t("organizer.workspace.backToEvents")}</a>
          </Button>
        </div>
      ) : null}

      {eventSummary && !planList.length ? (
        <section className="rounded-lg border border-dashed border-teal-200 bg-teal-50/60 p-4">
          <h2 className="text-base font-semibold text-ink">{t("organizer.workspace.draftNoPlanTitle")}</h2>
          <p className="mt-1 text-sm leading-5 text-slate-600">
            {t("organizer.workspace.draftNoPlanDescription")}
          </p>
        </section>
      ) : null}

      {actionFeedback ? (
        <div
          role={actionFeedback.tone === "danger" ? "alert" : "status"}
          className={`rounded-md border p-3 text-sm ${
            actionFeedback.tone === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-900"
              : "border-rose-200 bg-rose-50 text-rose-900"
          }`}
        >
          {actionFeedback.text}
        </div>
      ) : null}

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-ink">{t("organizer.workspace.stepperTitle")}</h2>
            <p className="mt-1 text-sm text-slate-600">{t("organizer.workspace.stepperDescription")}</p>
          </div>
        </div>
        <WorkflowStepper
          className="mt-4"
          steps={[
            {
              label: t("organizer.workspace.stepBuild"),
              detail: t("organizer.workspace.stepBuildDetail"),
              state: currentPlan ? "done" : "current"
            },
            {
              label: t("organizer.workspace.stepEvidence"),
              detail: t("organizer.workspace.stepEvidenceDetail", { count: traceList[0]?.steps?.length ?? 0 }),
              state: traceList.length ? "done" : "pending"
            },
            {
              label: t("organizer.workspace.stepApproval"),
              detail:
                currentPlan?.status === "approved"
                  ? t("organizer.workspace.stepApprovalConfirmed")
                  : t("organizer.workspace.stepApprovalWaiting"),
              state: currentPlan?.status === "approved" ? "done" : "current"
            }
          ]}
        />
      </section>

      <AgentEvidencePanel
        title={t("organizer.agentEvidence.planningTitle")}
        description={t("organizer.agentEvidence.planningDescription")}
        runs={planningRun ? [planningRun] : []}
        steps={planningSteps}
        toolCalls={toolCallsForRun(asArray(planningToolCalls), planningRun?.run_id)}
        drafts={[]}
        modelCalls={asArray(planningModelCalls)}
        evaluations={asArray(planningEvaluations)}
        emptyMessage={t("organizer.agentEvidence.emptyPlanning")}
      />

      <div className="grid gap-4 md:grid-cols-3">
        <MetricTile
          label={t("organizer.workspace.planStatus")}
          value={currentPlan ? `v${currentPlan.version}` : localizedStatus("draft", t)}
          detail={
            currentPlan?.created_reason
              ? localizedDemoText(currentPlan.created_reason, t)
              : t("organizer.workspace.noPlanMetricDetail")
          }
          tone={currentPlan?.status === "approved" ? "success" : "warning"}
        />
        <MetricTile
          label={t("organizer.dashboard.merchantReadiness")}
          value={`${readinessCount}/${taskList.length || 1}`}
          detail={t("organizer.workspace.readinessDetail")}
          tone="info"
        />
        <MetricTile
          label={t("organizer.workspace.stepApproval")}
          value={approvalState}
          detail={t("organizer.workspace.approvalDetail")}
          tone={currentPlan?.status === "approved" ? "success" : "warning"}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.workspace.eventPageTitle")}</CardTitle>
            <CardDescription>{t("organizer.workspace.eventPageDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-md border border-slate-200 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-medium">
                  {eventPage?.title ? localizedDemoText(eventPage.title, t) : t("organizer.workspace.eventPageEmpty")}
                </span>
                {eventPage?.status ? <Badge variant="neutral">{localizedStatus(eventPage.status, t)}</Badge> : null}
              </div>
              {eventPage?.subtitle ? (
                <p className="mt-2 text-sm text-slate-600">{localizedDemoText(eventPage.subtitle, t)}</p>
              ) : (
                <p className="mt-2 text-sm text-slate-600">{t("organizer.workspace.eventPageFallback")}</p>
              )}
              {eventPage ? (
                <div className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-3">
                  <span>{t("organizer.workspace.storySectionCount", { count: asArray(eventPage.story_sections).length })}</span>
                  <span>{t("organizer.workspace.routeHighlightCount", { count: asArray(eventPage.route_highlights).length })}</span>
                  <span>{t("organizer.workspace.merchantHighlightCount", { count: asArray(eventPage.merchant_highlights).length })}</span>
                </div>
              ) : null}
            </div>
            <div className="flex flex-wrap gap-3">
              <Button size="sm" onClick={() => void draftEventPage()}>
                {t("organizer.workspace.draftEventPage")}
              </Button>
              <Button size="sm" variant="secondary" onClick={() => void publishEventPage()}>
                {t("organizer.workspace.publishEventPage")}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle>{t("organizer.workspace.edgePackagesTitle")}</CardTitle>
                <CardDescription>{t("organizer.workspace.edgePackagesDescription")}</CardDescription>
              </div>
              <Button size="sm" variant="secondary" onClick={() => void generateOperationSuggestions()}>
                {t("organizer.workspace.generateOperationSuggestions")}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {suggestionFeedback ? (
              <div
                role={suggestionFeedback.tone === "danger" ? "alert" : "status"}
                className={`rounded-md border p-3 text-sm ${
                  suggestionFeedback.tone === "success"
                    ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                    : "border-rose-200 bg-rose-50 text-rose-900"
                }`}
              >
                {suggestionFeedback.text}
              </div>
            ) : null}
            <div className="grid gap-3 sm:grid-cols-3">
              <MetricTile
                label={t("organizer.workspace.edgePackageCount")}
                value={String(packageList.length)}
                detail={t("organizer.workspace.edgePackageCountDetail")}
                tone="info"
              />
              <MetricTile
                label={t("organizer.workspace.touchpointCount")}
                value={String(touchpointCount)}
                detail={t("organizer.workspace.touchpointCountDetail")}
                tone="success"
              />
              <MetricTile
                label={t("organizer.workspace.couponRuleCount")}
                value={String(couponRuleCount)}
                detail={t("organizer.workspace.couponRuleCountDetail")}
                tone="warning"
              />
            </div>
            <Button size="sm" onClick={() => void generateEdgePackages()}>
              {t("organizer.workspace.generateEdgePackages")}
            </Button>
            <div className="space-y-3">
              <div>
                <h3 className="text-sm font-semibold text-ink">{t("organizer.workspace.packageReadinessTitle")}</h3>
                <p className="mt-1 text-sm text-slate-600">{t("organizer.workspace.packageReadinessDescription")}</p>
              </div>
              {packageList.map((pkg) => {
                const activeTouchpoints = asArray(pkg.touchpoints).filter((item) => item.status === "active").length;
                const activeCoupons = asArray(pkg.coupon_rules).filter((item) => item.status === "active").length;
                return (
                  <div key={pkg.id} className="rounded-md border border-slate-200 p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="font-medium">
                        {t("organizer.workspace.packageForMerchant", { merchant: merchantLabel(pkg.merchant_id, t) })}
                      </div>
                      <Badge variant={pkg.status === "active" ? "success" : "neutral"}>
                        {localizedStatus(pkg.status, t)}
                      </Badge>
                    </div>
                    <div className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                      <span>
                        {t("organizer.workspace.packageTouchpointsReady", {
                          ready: activeTouchpoints,
                          total: asArray(pkg.touchpoints).length
                        })}
                      </span>
                      <span>
                        {t("organizer.workspace.packageCouponsReady", {
                          ready: activeCoupons,
                          total: asArray(pkg.coupon_rules).length
                        })}
                      </span>
                    </div>
                    <div className="mt-3 space-y-2 text-sm">
                      <div className="font-medium text-slate-700">{t("organizer.workspace.linkedEvidenceRefs")}</div>
                      {asArray(pkg.evidence_refs).length ? (
                        <div className="flex flex-wrap gap-2">
                          {asArray(pkg.evidence_refs).map((evidenceRef) => (
                            <Badge key={evidenceRef} variant="neutral">
                              {evidenceRef}
                            </Badge>
                          ))}
                        </div>
                      ) : (
                        <p className="text-slate-500">{t("organizer.workspace.packageEvidenceEmpty")}</p>
                      )}
                    </div>
                  </div>
                );
              })}
              {!packageList.length ? <p className="text-sm text-slate-500">{t("organizer.workspace.packageReadinessEmpty")}</p> : null}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap gap-3">
          <Button onClick={() => void buildPlan()}>{t("organizer.workspace.buildPlan")}</Button>
          <Button variant="secondary" onClick={() => void approvePlan()}>
            {t("organizer.workspace.confirmPlan")}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.workspace.routePlans")}</CardTitle>
            <CardDescription>{t("organizer.workspace.routePlansDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {planList.slice(0, 3).map((plan, index) => (
              <div key={plan.plan_id ?? `${plan.event_id}-${plan.version}`} className="rounded-md border border-slate-200 p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{t("organizer.workspace.planVersion", { version: plan.version ?? "1" })}</span>
                  <Badge variant={plan.status === "approved" ? "success" : "neutral"}>{localizedStatus(plan.status ?? "draft", t)}</Badge>
                </div>
                <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
                  {localizedDemoList(asArray(plan.diff_from_previous).slice(0, 3), t).map((item, itemIndex) => (
                    <li key={`${index}-${itemIndex}-${item}`}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
            {!planList.length ? <p className="text-sm text-slate-500">{t("organizer.workspace.routePlansEmpty")}</p> : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.workspace.evidenceTrail")}</CardTitle>
            <CardDescription>{t("organizer.workspace.evidenceDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {traceList.slice(0, 2).map((trace) => (
              <div key={trace.trace_id} className="rounded-md border border-slate-200 p-3">
                <div className="font-medium">{localizedDemoText(trace.trigger, t)}</div>
                <div className="text-sm text-slate-600">
                  {t("organizer.workspace.reasoningSteps", { count: asArray(trace.steps).length })}
                </div>
              </div>
            ))}
            {!traceList.length ? <p className="text-sm text-slate-500">{t("organizer.workspace.evidenceEmpty")}</p> : null}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("organizer.workspace.merchantTasks")}</CardTitle>
          <CardDescription>{t("organizer.workspace.merchantTasksDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {taskList.slice(0, 4).map((task) => (
            <div key={task.task_id} className="rounded-md border border-slate-200 p-3">
              <div className="font-medium">{localizedDemoText(task.role, t)}</div>
              <div className="text-sm text-slate-600">{task.time_slot}</div>
              <div className="mt-2 text-sm">{localizedDemoText(task.visitor_task, t)}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
