import { useState } from "react";
import { CheckCircle2, PauseCircle, PackageMinus, PackageX, Users } from "lucide-react";
import { api } from "../../api";
import type { MerchantRuntimeState } from "../../types";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { Input } from "../../ui/input";
import { MerchantQuickAction, ProductPageHeader, StatusPill } from "../../components/product";
import { useAsyncData } from "../productUtils";

type Inventory = MerchantRuntimeState["inventory_status"];
type Queue = MerchantRuntimeState["queue_status"];

export function MerchantStatusPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { t } = useI18n();
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] });
  const runtime = workbench.runtime_state;
  const [inventoryStatus, setInventoryStatus] = useState<Inventory>("normal");
  const [queueStatus, setQueueStatus] = useState<Queue>("normal");
  const [availableForVisitors, setAvailableForVisitors] = useState(true);
  const [temporaryNote, setTemporaryNote] = useState("");
  const [lastResult, setLastResult] = useState<string | null>(null);
  const taskCount = workbench.tasks?.length ?? 0;
  const taskCountKey = taskCount === 1 ? "merchant.status.assignedTask" : "merchant.status.assignedTasks";

  const submitStatus = async (override?: Partial<MerchantRuntimeState>) => {
    const payload = {
      inventory_status: override?.inventory_status ?? inventoryStatus,
      queue_status: override?.queue_status ?? queueStatus,
      available_for_visitors: override?.available_for_visitors ?? availableForVisitors,
      temporary_note: override?.temporary_note ?? temporaryNote
    };
    const result = await api.updateRuntimeState(merchantId, payload);
    setLastResult(
      result.incident || payload.inventory_status === "sold_out"
        ? t("merchant.status.organizerReviewRequested")
        : t("merchant.status.statusUpdated")
    );
  };

  const reportSoldOut = async () => {
    setInventoryStatus("sold_out");
    setAvailableForVisitors(false);
    await submitStatus({
      inventory_status: "sold_out",
      available_for_visitors: false,
      temporary_note: t("merchant.status.soldOutNote")
    });
  };

  const quickUpdate = async (override: Partial<MerchantRuntimeState>) => {
    if (override.inventory_status) setInventoryStatus(override.inventory_status);
    if (override.queue_status) setQueueStatus(override.queue_status);
    if (override.available_for_visitors !== undefined) setAvailableForVisitors(override.available_for_visitors);
    if (override.temporary_note !== undefined) setTemporaryNote(override.temporary_note);
    await submitStatus(override);
  };

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("merchant.status.eyebrow")}
        title={t("merchant.status.title")}
        description={t("merchant.status.description")}
        meta={[
          localizedDemoText(workbench.merchant?.name ?? "Merchant m001", t),
          t(taskCountKey, { count: taskCount }),
          t("merchant.status.localDemo")
        ]}
        status={runtime?.available_for_visitors === false ? "paused" : "open"}
        tone="merchant"
      />

      <Card>
        <CardHeader>
          <CardTitle>{t("merchant.status.currentStatus")}</CardTitle>
          <CardDescription>{t("merchant.status.currentStatusDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <StatusItem label={t("merchant.status.inventory")} value={runtime?.inventory_status ?? "normal"} />
          <StatusItem label={t("merchant.status.queue")} value={runtime?.queue_status ?? "normal"} />
          <StatusItem label={t("merchant.status.visitors")} value={runtime?.available_for_visitors === false ? "paused" : "open"} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <CardTitle>{t("merchant.status.quickActions")}</CardTitle>
              <CardDescription>{t("merchant.status.quickActionsDescription")}</CardDescription>
            </div>
            {lastResult ? <StatusPill tone={lastResult.includes("复核") || lastResult.includes("review") ? "warning" : "success"}>{lastResult}</StatusPill> : null}
          </div>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <MerchantQuickAction
            detail={t("merchant.status.acceptVisitorsDetail")}
            icon={<CheckCircle2 size={18} />}
            label={t("merchant.status.acceptVisitors")}
            onClick={() =>
              void quickUpdate({
                inventory_status: "normal",
                queue_status: "normal",
                available_for_visitors: true,
                temporary_note: ""
              })
            }
            tone="accept"
          />
          <MerchantQuickAction
            detail={t("merchant.status.pauseVisitorsDetail")}
            icon={<PauseCircle size={18} />}
            label={t("merchant.status.pauseVisitors")}
            onClick={() =>
              void quickUpdate({ available_for_visitors: false, temporary_note: t("merchant.status.pausedByMerchant") })
            }
            tone="pause"
          />
          <MerchantQuickAction
            detail={t("merchant.status.reportLowStockDetail")}
            icon={<PackageMinus size={18} />}
            label={t("merchant.status.reportLowStock")}
            onClick={() => void quickUpdate({ inventory_status: "low", temporary_note: t("merchant.status.lowStockNote") })}
            tone="warning"
          />
          <MerchantQuickAction
            detail={t("merchant.status.reportSoldOutDetail")}
            icon={<PackageX size={18} />}
            label={t("merchant.status.reportSoldOut")}
            onClick={() => void reportSoldOut()}
            tone="danger"
          />
          <MerchantQuickAction
            detail={t("merchant.status.queueBusyDetail")}
            icon={<Users size={18} />}
            label={t("merchant.status.queueBusy")}
            onClick={() => void quickUpdate({ queue_status: "busy", temporary_note: t("merchant.status.queueBusyNote") })}
            tone="warning"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("merchant.status.advancedReport")}</CardTitle>
          <CardDescription>{t("merchant.status.advancedReportDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <label className="space-y-1 text-sm">
              <span className="font-medium">{t("merchant.status.inventory")}</span>
              <select
                className="h-10 w-full rounded-md border border-slate-200 bg-white px-3"
                value={inventoryStatus}
                onChange={(event) => setInventoryStatus(event.target.value as Inventory)}
              >
                <option value="normal">{t("merchant.status.normal")}</option>
                <option value="low">{t("merchant.status.low")}</option>
                <option value="sold_out">{t("merchant.status.soldOut")}</option>
              </select>
            </label>
            <label className="space-y-1 text-sm">
              <span className="font-medium">{t("merchant.status.queue")}</span>
              <select
                className="h-10 w-full rounded-md border border-slate-200 bg-white px-3"
                value={queueStatus}
                onChange={(event) => setQueueStatus(event.target.value as Queue)}
              >
                <option value="normal">{t("merchant.status.normal")}</option>
                <option value="busy">{t("merchant.status.busy")}</option>
                <option value="overloaded">{t("merchant.status.overloaded")}</option>
              </select>
            </label>
            <label className="flex items-center gap-2 pt-7 text-sm">
              <input
                type="checkbox"
                checked={availableForVisitors}
                onChange={(event) => setAvailableForVisitors(event.target.checked)}
              />
              {t("merchant.status.acceptVisitors")}
            </label>
          </div>
          <label className="space-y-1 text-sm">
            <span className="font-medium">{t("merchant.status.temporaryNote")}</span>
            <Input value={temporaryNote} onChange={(event) => setTemporaryNote(event.target.value)} />
          </label>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => void submitStatus()}>{t("merchant.status.submitStatus")}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  const { t } = useI18n();
  return (
    <div>
      <div className="text-xs text-slate-500">{label}</div>
      <Badge variant={value === "sold_out" || value === "paused" ? "warning" : "success"}>
        {localizedStatus(value, t)}
      </Badge>
    </div>
  );
}
