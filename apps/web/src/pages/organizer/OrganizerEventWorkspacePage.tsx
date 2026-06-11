import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { MetricTile, ProductPageHeader, WorkflowStepper } from "../../components/product";
import { asArray, useAsyncData } from "../productUtils";

export function OrganizerEventWorkspacePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: plans } = useAsyncData(() => api.getPlanVersions(eventId), []);
  const { data: traces } = useAsyncData(() => api.getAgentTraces(eventId), []);
  const { data: tasks } = useAsyncData(() => api.getMerchantTasks(eventId), []);
  const planList = asArray(plans);
  const traceList = asArray(traces);
  const taskList = asArray(tasks);
  const currentPlan = planList.find((plan) => plan.status === "approved") ?? planList[0];
  const readinessCount = taskList.filter((task) => task.task_status === "active").length;

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Event workspace"
        title="Route plan and execution readiness"
        description="Build the route plan, inspect the evidence trail, review merchant readiness, and confirm the operating plan."
        meta={[
          `Route plan status ${currentPlan?.status ?? "draft"}`,
          `Merchant readiness ${readinessCount}/${taskList.length || 1}`,
          `Approval state ${currentPlan?.status === "approved" ? "confirmed" : "needs confirmation"}`
        ]}
        status={currentPlan?.status ?? "draft"}
        actions={
          <>
            <Button onClick={() => void api.generatePlan(eventId)}>Build route plan</Button>
            <Button variant="secondary" onClick={() => void api.approvePlanVersion(eventId, currentPlan?.version ?? 1)}>
              Confirm plan
            </Button>
          </>
        }
      />

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-ink">Workflow stepper</h2>
            <p className="mt-1 text-sm text-slate-600">Operator-visible flow from route building to public release.</p>
          </div>
        </div>
        <WorkflowStepper
          className="mt-4"
          steps={[
            { label: "Build route plan", detail: "Create the first operating route.", state: currentPlan ? "done" : "current" },
            { label: "Review evidence trail", detail: `${traceList[0]?.steps?.length ?? 0} evidence steps available.`, state: traceList.length ? "done" : "pending" },
            { label: "Approval state", detail: currentPlan?.status === "approved" ? "Confirmed for operations." : "Awaiting organizer confirmation.", state: currentPlan?.status === "approved" ? "done" : "current" }
          ]}
        />
      </section>

      <div className="grid gap-4 md:grid-cols-3">
        <MetricTile label="Route plan status" value={currentPlan ? `v${currentPlan.version}` : "draft"} detail={currentPlan?.created_reason ?? "No route plan has been created yet."} tone={currentPlan?.status === "approved" ? "success" : "warning"} />
        <MetricTile label="Merchant readiness" value={`${readinessCount}/${taskList.length || 1}`} detail="Active merchant tasks ready for tonight." tone="info" />
        <MetricTile label="Approval state" value={currentPlan?.status === "approved" ? "confirmed" : "pending"} detail="Human confirmation remains the release gate." tone={currentPlan?.status === "approved" ? "success" : "warning"} />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap gap-3">
          <Button onClick={() => void api.generatePlan(eventId)}>Build route plan</Button>
          <Button variant="secondary" onClick={() => void api.approvePlanVersion(eventId, currentPlan?.version ?? 1)}>
            Confirm plan
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Route plans</CardTitle>
            <CardDescription>Versioned operating plans with visible differences.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {planList.slice(0, 3).map((plan, index) => (
              <div key={plan.plan_id ?? `${plan.event_id}-${plan.version}`} className="rounded-md border border-slate-200 p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">Plan v{plan.version ?? "1"}</span>
                  <Badge variant={plan.status === "approved" ? "success" : "neutral"}>{plan.status ?? "draft"}</Badge>
                </div>
                <ul className="mt-2 list-disc pl-5 text-sm text-slate-600">
                  {asArray(plan.diff_from_previous).slice(0, 3).map((item, itemIndex) => (
                    <li key={`${index}-${itemIndex}-${item}`}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
            {!planList.length ? <p className="text-sm text-slate-500">No route plan has been created yet.</p> : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Evidence trail</CardTitle>
            <CardDescription>Why the route and recovery choices were recommended.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {traceList.slice(0, 2).map((trace) => (
              <div key={trace.trace_id} className="rounded-md border border-slate-200 p-3">
                <div className="font-medium">{trace.trigger}</div>
                <div className="text-sm text-slate-600">{asArray(trace.steps).length} reasoning steps recorded.</div>
              </div>
            ))}
            {!traceList.length ? <p className="text-sm text-slate-500">Evidence will appear after route planning.</p> : null}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Merchant tasks</CardTitle>
          <CardDescription>Execution packs sent to participating stores.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {taskList.slice(0, 4).map((task) => (
            <div key={task.task_id} className="rounded-md border border-slate-200 p-3">
              <div className="font-medium">{task.role}</div>
              <div className="text-sm text-slate-600">{task.time_slot}</div>
              <div className="mt-2 text-sm">{task.visitor_task}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
