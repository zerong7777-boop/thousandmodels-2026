import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { localizedDemoList, localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { AgentEvidencePanel, latestRunForTrigger, stepsForRun, toolCallsForRun } from "../../components/agent";
import { MetricTile, ProductPageHeader, WorkflowStepper } from "../../components/product";
import type { AgentToolCall } from "../../types";
import { asArray, useAsyncData } from "../productUtils";

export function OrganizerEventWorkspacePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: plans } = useAsyncData(() => api.getPlanVersions(eventId), []);
  const { data: traces } = useAsyncData(() => api.getAgentTraces(eventId), []);
  const { data: tasks } = useAsyncData(() => api.getMerchantTasks(eventId), []);
  const { data: agentRuns } = useAsyncData(() => api.getAgentRuns(eventId), [], [eventId]);
  const planList = asArray(plans);
  const traceList = asArray(traces);
  const taskList = asArray(tasks);
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
  const approvalState =
    currentPlan?.status === "approved" ? t("common.status.confirmed") : t("organizer.workspace.needsConfirmation");

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("organizer.workspace.eyebrow")}
        title={t("organizer.workspace.title")}
        description={t("organizer.workspace.description")}
        meta={[
          t("organizer.workspace.planStatusMeta", { status: localizedStatus(currentStatus, t) }),
          t("organizer.workspace.readinessMeta", { ready: readinessCount, total: taskList.length || 1 }),
          t("organizer.workspace.approvalMeta", { state: approvalState })
        ]}
        status={currentStatus}
        actions={
          <>
            <Button onClick={() => void api.generatePlan(eventId)}>{t("organizer.workspace.buildPlan")}</Button>
            <Button variant="secondary" onClick={() => void api.approvePlanVersion(eventId, currentPlan?.version ?? 1)}>
              {t("organizer.workspace.confirmPlan")}
            </Button>
          </>
        }
      />

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
          detail={currentPlan?.created_reason ? localizedDemoText(currentPlan.created_reason, t) : t("organizer.workspace.noPlan")}
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

      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap gap-3">
          <Button onClick={() => void api.generatePlan(eventId)}>{t("organizer.workspace.buildPlan")}</Button>
          <Button variant="secondary" onClick={() => void api.approvePlanVersion(eventId, currentPlan?.version ?? 1)}>
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
            {!planList.length ? <p className="text-sm text-slate-500">{t("organizer.workspace.noPlan")}</p> : null}
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
