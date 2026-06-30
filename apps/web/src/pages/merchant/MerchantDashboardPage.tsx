import { api } from "../../api";
import { MetricTile, ProductPageHeader, StatusPill } from "../../components/product";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

function numberFromSummary(summary: Record<string, unknown> | undefined, keys: string[]) {
  for (const key of keys) {
    const value = summary?.[key];
    if (typeof value === "number") return String(value);
    if (typeof value === "string" && value.trim()) return value;
  }
  return null;
}

function touchpointTypeLabel(value: string | undefined, t: (key: string) => string) {
  const labels: Record<string, string> = {
    event_page: t("merchant.dashboard.touchpointTypeEventPage"),
    in_shop_qr: t("merchant.dashboard.touchpointTypeInShopQr"),
    coupon: t("merchant.dashboard.touchpointTypeCoupon"),
    redemption: t("merchant.dashboard.touchpointTypeRedemption"),
    status_report: t("merchant.dashboard.touchpointTypeStatusReport"),
    display: t("merchant.dashboard.touchpointTypeDisplay")
  };
  return value ? labels[value] ?? t("merchant.dashboard.touchpointTypeOther") : t("common.unavailable");
}

export function MerchantDashboardPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { t } = useI18n();
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] }, [merchantId]);
  const { data: assignedEvents } = useAsyncData(() => api.getMyMerchantEvents(), [], [merchantId]);
  const nextTask = asArray(workbench.tasks)[0];
  const nextAssignedEvent = asArray(assignedEvents)[0];
  const taskCount = asArray(workbench.tasks).length;
  const taskCountKey = taskCount === 1 ? "merchant.dashboard.assignedTask" : "merchant.dashboard.assignedTasks";
  const inventoryStatus = workbench.runtime_state?.inventory_status ?? "normal";
  const queueStatus = workbench.runtime_state?.queue_status ?? "normal";
  const visitorStatus = workbench.runtime_state?.available_for_visitors === false ? "paused" : "open";
  const interactionPackage = workbench.interaction_package;
  const touchpointCount = asArray(interactionPackage?.touchpoints).length;
  const couponCount = asArray(interactionPackage?.coupon_rules).length;
  const currentPackageMetrics = {
    interactions:
      numberFromSummary(workbench.touchpoint_summary, ["interactions", "interaction_count", "total_interactions"]) ??
      t("common.unavailable"),
    claims:
      numberFromSummary(workbench.coupon_summary, ["claims", "claimed", "claim_count", "total_claims"]) ??
      t("common.unavailable"),
    redemptions:
      numberFromSummary(workbench.coupon_summary, ["redemptions", "redeemed", "redemption_count", "total_redemptions"]) ??
      t("common.unavailable")
  };

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

      <Card>
        <CardHeader>
          <CardTitle>{t("merchant.setup.cardTitle")}</CardTitle>
          <CardDescription>{t("merchant.setup.cardDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {asArray(assignedEvents).map((item) => (
            <div key={item.event.event_id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-200 p-3">
              <div>
                <div className="font-medium text-ink">{item.event.title}</div>
                <div className="mt-1 text-sm text-slate-600">
                  {item.event.area} / {item.event.date} / {item.event.time_window}
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <StatusPill tone={item.ready_for_planning ? "success" : "warning"}>
                  {localizedStatus(item.participant.setup_status ?? "not_started", t)}
                </StatusPill>
                <Button asChild variant="secondary" size="sm">
                  <a href={`/merchant/events/${item.event.event_id}/setup`}>{t("merchant.setup.openSetup")}</a>
                </Button>
              </div>
            </div>
          ))}
          {!asArray(assignedEvents).length ? (
            <p className="text-sm text-slate-500">{t("merchant.setup.noAssignedEvents")}</p>
          ) : null}
          {nextAssignedEvent ? (
            <p className="text-xs text-slate-500">{t("merchant.setup.nextEvent", { title: nextAssignedEvent.event.title })}</p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("merchant.dashboard.interactionPackageTitle")}</CardTitle>
          <CardDescription>{t("merchant.dashboard.interactionPackageDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-md border border-slate-200 p-3">
              <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                {t("merchant.dashboard.operatorBrief")}
              </div>
              <p className="mt-2 text-sm leading-5 text-slate-700">
                {interactionPackage?.operator_brief
                  ? localizedDemoText(interactionPackage.operator_brief, t)
                  : t("merchant.dashboard.packageUnavailable")}
              </p>
            </div>
            <div className="rounded-md border border-slate-200 p-3">
              <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                {t("merchant.dashboard.visitorPitch")}
              </div>
              <p className="mt-2 text-sm leading-5 text-slate-700">
                {interactionPackage?.visitor_pitch
                  ? localizedDemoText(interactionPackage.visitor_pitch, t)
                  : t("merchant.dashboard.packageUnavailable")}
              </p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-5">
            <MetricTile label={t("merchant.dashboard.touchpoints")} value={String(touchpointCount)} detail={t("merchant.dashboard.touchpointsDetail")} tone="info" />
            <MetricTile label={t("merchant.dashboard.coupons")} value={String(couponCount)} detail={t("merchant.dashboard.couponsDetail")} tone="warning" />
            <MetricTile label={t("merchant.dashboard.interactions")} value={currentPackageMetrics.interactions} detail={t("merchant.dashboard.interactionsDetail")} tone="success" />
            <MetricTile label={t("merchant.dashboard.claims")} value={currentPackageMetrics.claims} detail={t("merchant.dashboard.claimsDetail")} tone="info" />
            <MetricTile label={t("merchant.dashboard.redemptions")} value={currentPackageMetrics.redemptions} detail={t("merchant.dashboard.redemptionsDetail")} tone="success" />
          </div>
          <div className="space-y-3">
            <div>
              <h3 className="text-sm font-semibold text-ink">{t("merchant.dashboard.touchpointCardsTitle")}</h3>
              <p className="mt-1 text-sm text-slate-600">{t("merchant.dashboard.touchpointCardsDescription")}</p>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {asArray(interactionPackage?.touchpoints).map((touchpoint) => (
                <div key={touchpoint.id} className="rounded-md border border-slate-200 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="font-medium">{localizedDemoText(touchpoint.label, t)}</div>
                    <div className="text-xs text-slate-500">{localizedStatus(touchpoint.status, t)}</div>
                  </div>
                  <p className="mt-2 text-sm text-slate-700">
                    {touchpoint.public_copy
                      ? localizedDemoText(touchpoint.public_copy, t)
                      : t("merchant.dashboard.packageUnavailable")}
                  </p>
                  <div className="mt-3 grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
                    <span>{t("merchant.dashboard.touchpointToken", { value: touchpoint.token || t("common.unavailable") })}</span>
                    <span>{t("merchant.dashboard.touchpointType", { value: touchpointTypeLabel(touchpoint.touchpoint_type, t) })}</span>
                  </div>
                </div>
              ))}
            </div>
            {!asArray(interactionPackage?.touchpoints).length ? (
              <p className="text-sm text-slate-500">{t("merchant.dashboard.touchpointCardsEmpty")}</p>
            ) : null}
          </div>
          <div className="space-y-3">
            <div>
              <h3 className="text-sm font-semibold text-ink">{t("merchant.dashboard.couponRulesTitle")}</h3>
              <p className="mt-1 text-sm text-slate-600">{t("merchant.dashboard.couponRulesDescription")}</p>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {asArray(interactionPackage?.coupon_rules).map((rule) => (
                <div key={rule.id} className="rounded-md border border-slate-200 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="font-medium">{localizedDemoText(rule.title, t)}</div>
                    <div className="text-xs text-slate-500">{localizedStatus(rule.status, t)}</div>
                  </div>
                  <p className="mt-2 text-sm text-slate-700">
                    {rule.description ? localizedDemoText(rule.description, t) : t("merchant.dashboard.packageUnavailable")}
                  </p>
                  <div className="mt-3 grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
                    <span>{t("merchant.dashboard.couponLimit", { count: rule.max_redemptions })}</span>
                    <span>{t("merchant.dashboard.couponPackageVersion", { version: interactionPackage?.plan_version ?? 1 })}</span>
                  </div>
                </div>
              ))}
            </div>
            {!asArray(interactionPackage?.coupon_rules).length ? (
              <p className="text-sm text-slate-500">{t("merchant.dashboard.couponRulesEmpty")}</p>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
