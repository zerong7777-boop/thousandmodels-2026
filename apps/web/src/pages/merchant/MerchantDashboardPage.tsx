import { api } from "../../api";
import { MetricTile, ProductPageHeader } from "../../components/product";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function MerchantDashboardPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] });
  const nextTask = asArray(workbench.tasks)[0];

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Today"
        title={workbench.merchant?.name ?? "Merchant m001"}
        description="Check assigned tasks, prepare before visitors arrive, and keep live availability current."
        meta={["Before visitors arrive", `${asArray(workbench.tasks).length} assigned task`, "Organizer notices active"]}
        status={workbench.runtime_state?.available_for_visitors === false ? "paused" : "open"}
        tone="merchant"
      />

      <div className="grid gap-4 md:grid-cols-3">
        <MetricTile label="Inventory" value={workbench.runtime_state?.inventory_status ?? "normal"} detail="Update this before stock runs low." tone={workbench.runtime_state?.inventory_status === "sold_out" ? "danger" : "success"} />
        <MetricTile label="Queue" value={workbench.runtime_state?.queue_status ?? "normal"} detail="Keep the organizer aware of pressure." tone={workbench.runtime_state?.queue_status === "overloaded" ? "warning" : "neutral"} />
        <MetricTile label="Visitor intake" value={workbench.runtime_state?.available_for_visitors === false ? "paused" : "open"} detail="Controls whether visitors should keep arriving." tone={workbench.runtime_state?.available_for_visitors === false ? "warning" : "success"} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Next required action</CardTitle>
          <CardDescription>Keep this focused on the merchant job for tonight.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="font-medium">{nextTask?.role ?? "Review assigned task"}</div>
            <div className="text-sm text-slate-600">Before visitors arrive</div>
            {nextTask?.time_slot ? <div className="text-xs text-slate-500">{nextTask.time_slot}</div> : null}
          </div>
          <Button asChild>
            <a href="/merchant/events/demo-night-tour/status">Report live status</a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
