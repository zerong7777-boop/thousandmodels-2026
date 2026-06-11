import { api } from "../../api";
import { MetricTile, ProductPageHeader } from "../../components/product";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function MerchantDashboardPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { t } = useI18n();
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] });
  const nextTask = asArray(workbench.tasks)[0];
  const taskCount = asArray(workbench.tasks).length;
  const taskCountKey = taskCount === 1 ? "merchant.dashboard.assignedTask" : "merchant.dashboard.assignedTasks";
  const inventoryStatus = workbench.runtime_state?.inventory_status ?? "normal";
  const queueStatus = workbench.runtime_state?.queue_status ?? "normal";
  const visitorStatus = workbench.runtime_state?.available_for_visitors === false ? "paused" : "open";

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("merchant.dashboard.eyebrow")}
        title={localizedDemoText(workbench.merchant?.name ?? "Merchant m001", t)}
        description={t("merchant.dashboard.description")}
        meta={[t("merchant.dashboard.beforeVisitors"), t(taskCountKey, { count: taskCount }), t("merchant.dashboard.noticesActive")]}
        status={visitorStatus}
        tone="merchant"
      />

      <div className="grid gap-4 md:grid-cols-3">
        <MetricTile
          label={t("merchant.dashboard.inventory")}
          value={localizedStatus(inventoryStatus, t)}
          detail={t("merchant.dashboard.inventoryDetail")}
          tone={inventoryStatus === "sold_out" ? "danger" : "success"}
        />
        <MetricTile
          label={t("merchant.dashboard.queue")}
          value={localizedStatus(queueStatus, t)}
          detail={t("merchant.dashboard.queueDetail")}
          tone={queueStatus === "overloaded" ? "warning" : "neutral"}
        />
        <MetricTile
          label={t("merchant.dashboard.visitorIntake")}
          value={localizedStatus(visitorStatus, t)}
          detail={t("merchant.dashboard.visitorIntakeDetail")}
          tone={visitorStatus === "paused" ? "warning" : "success"}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("merchant.dashboard.nextAction")}</CardTitle>
          <CardDescription>{t("merchant.dashboard.nextActionDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="font-medium">
              {nextTask?.role ? localizedDemoText(nextTask.role, t) : t("merchant.dashboard.reviewTask")}
            </div>
            <div className="text-sm text-slate-600">{t("merchant.dashboard.beforeVisitors")}</div>
            {nextTask?.time_slot ? <div className="text-xs text-slate-500">{nextTask.time_slot}</div> : null}
          </div>
          <Button asChild>
            <a href="/merchant/events/demo-night-tour/status">{t("merchant.dashboard.reportStatus")}</a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
