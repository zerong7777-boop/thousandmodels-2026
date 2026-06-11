import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { ProductPageHeader, StatusPill } from "../../components/product";
import { merchantContingencyInstruction } from "../../design/merchantTaskPresentation";
import { localizedDemoList, localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

export function MerchantTasksPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { t } = useI18n();
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] });

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("merchant.tasks.eyebrow")}
        title={t("merchant.tasks.title")}
        description={t("merchant.tasks.description")}
        meta={[t("merchant.dashboard.beforeVisitors"), t("merchant.tasks.recoveryNoticeIncluded"), t("merchant.tasks.staffChecklist")]}
        status="active"
        tone="merchant"
      />

      <div className="grid gap-4">
        {asArray(workbench.tasks).map((task) => (
          <Card key={task.task_id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <CardTitle>{localizedDemoText(task.role, t)}</CardTitle>
                  <CardDescription>{task.time_slot}</CardDescription>
                </div>
                <Badge variant={task.task_status === "active" ? "success" : "neutral"}>{localizedStatus(task.task_status, t)}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <StatusPill tone="merchant">{t("merchant.dashboard.beforeVisitors")}</StatusPill>
                <StatusPill tone="warning">{t("merchant.tasks.recoveryNotice")}</StatusPill>
              </div>
              <div>
                <div className="text-xs text-slate-500">{t("merchant.tasks.visitorTask")}</div>
                <div className="text-sm">{localizedDemoText(task.visitor_task, t)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">{t("merchant.tasks.preparation")}</div>
                <ul className="list-disc pl-5 text-sm text-slate-700">
                  {localizedDemoList(asArray(task.preparation_items), t).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="text-xs text-slate-500">{t("merchant.tasks.contingencyInstruction")}</div>
                <div className="text-sm text-slate-700">{localizedDemoText(merchantContingencyInstruction(task), t)}</div>
              </div>
            </CardContent>
          </Card>
        ))}
        {!asArray(workbench.tasks).length ? (
          <Card>
            <CardContent className="pt-5 text-sm text-slate-500">{t("merchant.tasks.empty")}</CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
