import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { ProductPageHeader, StatusPill } from "../../components/product";
import { asArray, useAsyncData } from "../productUtils";

export function MerchantTasksPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] });

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Assigned tasks"
        title="Tonight's work pack"
        description="Preparation items, visitor task, and fallback instruction for staff before visitors arrive."
        meta={["Before visitors arrive", "Recovery notice included", "Staff checklist"]}
        status="active"
        tone="merchant"
      />

      <div className="grid gap-4">
        {asArray(workbench.tasks).map((task) => (
          <Card key={task.task_id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <CardTitle>{task.role}</CardTitle>
                  <CardDescription>{task.time_slot}</CardDescription>
                </div>
                <Badge variant={task.task_status === "active" ? "success" : "neutral"}>{task.task_status}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <StatusPill tone="merchant">Before visitors arrive</StatusPill>
                <StatusPill tone="warning">Recovery notice</StatusPill>
              </div>
              <div>
                <div className="text-xs text-slate-500">Visitor task</div>
                <div className="text-sm">{task.visitor_task}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Preparation</div>
                <ul className="list-disc pl-5 text-sm text-slate-700">
                  {asArray(task.preparation_items).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="text-xs text-slate-500">Fallback instruction</div>
                <div className="text-sm text-slate-700">{task.fallback_instruction}</div>
              </div>
            </CardContent>
          </Card>
        ))}
        {!asArray(workbench.tasks).length ? (
          <Card>
            <CardContent className="pt-5 text-sm text-slate-500">No assigned tasks are available yet.</CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
