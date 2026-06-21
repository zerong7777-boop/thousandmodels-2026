import { api } from "../../api";
import { AgentEvidencePanel, latestRunForTrigger } from "../../components/agent";
import { MetricTile, ProductPageHeader } from "../../components/product";
import { localizedDemoList, localizedDemoText, useI18n } from "../../i18n";
import type { Locale, Translator } from "../../i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

function displayValue(value: unknown) {
  if (typeof value === "number") return String(value);
  if (typeof value === "string" && value.trim()) return value;
  if (typeof value === "boolean") return value ? "yes" : "no";
  return "";
}

function unknownArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function localizedCopy(locale: Locale, en: string, zhHans: string, zhHant: string) {
  if (locale === "zh-Hans") return zhHans;
  if (locale === "zh-Hant") return zhHant;
  return en;
}

function translationOrFallback(
  locale: Locale,
  t: Translator,
  key: string,
  en: string,
  zhHans: string,
  zhHant: string
) {
  const translated = t(key);
  return translated === key ? localizedCopy(locale, en, zhHans, zhHant) : translated;
}

function formatStructuredItems(
  value: unknown,
  labelForKey: (key: string) => string
) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return "";
  return Object.entries(value as Record<string, unknown>)
    .map(([key, itemValue]) => {
      const renderedValue = displayValue(itemValue);
      return renderedValue ? `${labelForKey(key)} ${renderedValue}` : "";
    })
    .filter(Boolean)
    .join(" | ");
}

function merchantLabel(value: string, t: Translator) {
  if (value === "m001") return localizedDemoText("Merchant m001", t);
  return localizedDemoText(value, t) || value;
}

export function OrganizerReviewPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { locale, t } = useI18n();
  const { data: report } = useAsyncData(() => api.getReviewReport(eventId), null, [eventId]);
  const { data: agentRuns } = useAsyncData(() => api.getAgentRuns(eventId), [], [eventId]);
  const reviewRun = latestRunForTrigger(asArray(agentRuns), "review_generation");
  const { data: reviewDrafts } = useAsyncData(() => api.getAgentDrafts(eventId, "review_summary"), [], [eventId]);
  const { data: reviewModelCalls } = useAsyncData(
    () => (reviewRun ? api.getAgentModelCalls(eventId, reviewRun.run_id) : Promise.resolve([])),
    [],
    [eventId, reviewRun?.run_id]
  );
  const { data: reviewEvaluations } = useAsyncData(
    () => (reviewRun ? api.getAgentEvaluations(eventId, reviewRun.run_id) : Promise.resolve([])),
    [],
    [eventId, reviewRun?.run_id]
  );
  const recommendations = localizedDemoList(asArray(report?.next_event_recommendations), t);
  const lessons = localizedDemoList(asArray(report?.lessons_learned), t);
  const touchpointSummary = report?.touchpoint_summary ?? {};
  const merchantOutcomes = asArray(report?.merchant_outcomes);
  const extensionTasks = asArray(report?.extension_tasks);

  const touchpointTypeLabel = (value: string) => {
    const labels: Record<string, string> = {
      event_page: translationOrFallback(locale, t, "organizer.review.touchpointType.eventPage", "Event page", "活动页", "活動頁"),
      in_shop_qr: translationOrFallback(locale, t, "organizer.review.touchpointType.inShopQr", "In-store QR", "店内扫码", "店內掃碼"),
      coupon: translationOrFallback(locale, t, "organizer.review.touchpointType.coupon", "Coupon claim", "领券", "領券"),
      redemption: translationOrFallback(locale, t, "organizer.review.touchpointType.redemption", "Coupon redemption", "核销", "核銷"),
      status_report: translationOrFallback(locale, t, "organizer.review.touchpointType.statusReport", "Status report", "状态上报", "狀態回報"),
      display: translationOrFallback(locale, t, "organizer.review.touchpointType.display", "Store display", "店内展示", "店內展示")
    };
    return labels[value] ?? t("organizer.review.touchpointType.other");
  };

  const totalInteractionsLabel = translationOrFallback(
    locale,
    t,
    "organizer.review.touchpointMetric.totalInteractions",
    "Total interactions",
    "总互动次数",
    "總互動次數"
  );
  const couponClaimsLabel = translationOrFallback(
    locale,
    t,
    "organizer.review.touchpointMetric.couponClaims",
    "Coupon claims",
    "领券次数",
    "領券次數"
  );
  const couponRedemptionsLabel = translationOrFallback(
    locale,
    t,
    "organizer.review.touchpointMetric.couponRedemptions",
    "Coupon redemptions",
    "核销次数",
    "核銷次數"
  );
  const redemptionRateLabel = translationOrFallback(
    locale,
    t,
    "organizer.review.touchpointMetric.redemptionRate",
    "Redemption rate",
    "核销率",
    "核銷率"
  );
  const byTouchpointLabel = translationOrFallback(locale, t, "organizer.review.touchpointMetric.byType", "By touchpoint", "按触点", "按觸點");
  const byMerchantLabel = translationOrFallback(locale, t, "organizer.review.touchpointMetric.byMerchant", "By merchant", "按商户", "按商戶");
  const metricLabel = (value: string) => {
    const labels: Record<string, string> = {
      total_interactions: totalInteractionsLabel,
      interactions: totalInteractionsLabel,
      coupon_claims: couponClaimsLabel,
      claims: couponClaimsLabel,
      coupon_redemptions: couponRedemptionsLabel,
      redemptions: couponRedemptionsLabel,
      redemption_rate: redemptionRateLabel
    };
    return labels[value] ?? t("organizer.review.touchpointMetric.other");
  };

  const touchpointEntries = [
    {
      key: "total_interactions",
      label: totalInteractionsLabel,
      value: displayValue(touchpointSummary.total_interactions)
    },
    {
      key: "coupon_claims",
      label: couponClaimsLabel,
      value: displayValue(touchpointSummary.coupon_claims)
    },
    {
      key: "coupon_redemptions",
      label: couponRedemptionsLabel,
      value: displayValue(touchpointSummary.coupon_redemptions)
    },
    {
      key: "redemption_rate",
      label: redemptionRateLabel,
      value: displayValue(touchpointSummary.redemption_rate)
    },
    {
      key: "by_type",
      label: byTouchpointLabel,
      value: formatStructuredItems(touchpointSummary.by_type, touchpointTypeLabel)
    },
    {
      key: "by_merchant",
      label: byMerchantLabel,
      value: formatStructuredItems(touchpointSummary.by_merchant, (merchantId) => merchantLabel(merchantId, t))
    }
  ].filter((entry) => entry.value);

  const extensionTaskTypeLabel = (value: string) => {
    const labels: Record<string, string> = {
      merchant_follow_up: translationOrFallback(
        locale,
        t,
        "organizer.review.extensionTaskType.merchantFollowUp",
        "Merchant follow-up",
        "商户跟进",
        "商戶跟進"
      ),
      route_update: translationOrFallback(locale, t, "organizer.review.extensionTaskType.routeUpdate", "Route update", "路线更新", "路線更新"),
      coupon_rebalance: translationOrFallback(
        locale,
        t,
        "organizer.review.extensionTaskType.couponRebalance",
        "Coupon rebalance",
        "优惠重配",
        "優惠重配"
      ),
      public_notice: translationOrFallback(locale, t, "organizer.review.extensionTaskType.publicNotice", "Public notice", "游客通知", "遊客通知")
    };
    return labels[value] ?? t("organizer.review.extensionTaskType.other");
  };

  const metricRefsLabel = translationOrFallback(locale, t, "organizer.review.metricRefs", "Linked metrics", "关联指标", "關聯指標");
  const merchantRefsLabel = translationOrFallback(locale, t, "organizer.review.merchantRefs", "Related merchants", "相关商户", "相關商戶");

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("organizer.review.eyebrow")}
        title={t("organizer.review.title")}
        description={report?.summary ? localizedDemoText(report.summary, t) : t("organizer.review.descriptionFallback")}
        meta={[
          t("organizer.review.metaVisits"),
          t("organizer.review.metaCheckins"),
          t("organizer.review.metaResponse"),
          t("organizer.review.metaBudget")
        ]}
        status="ready"
      />
      <div className="grid gap-4 md:grid-cols-5">
        <MetricTile label={t("organizer.review.h5Visits")} value="428" detail={t("organizer.review.metaVisits")} tone="info" />
        <MetricTile label={t("organizer.review.checkIns")} value="136" detail={t("organizer.review.checkInsDetail")} tone="success" />
        <MetricTile label={t("organizer.review.responseTime")} value="4 min" detail={t("organizer.review.responseTimeDetail")} tone="success" />
        <MetricTile label={t("organizer.review.queuePressure")} value={t("organizer.review.queuePressureValue")} detail={t("organizer.review.queuePressureDetail")} tone="warning" />
        <MetricTile label={t("organizer.review.budgetUsed")} value="82%" detail={t("organizer.review.budgetUsedDetail")} tone="success" />
      </div>
      <AgentEvidencePanel
        title={t("organizer.agentEvidence.reviewTitle")}
        description={t("organizer.agentEvidence.reviewDescription")}
        runs={reviewRun ? [reviewRun] : []}
        steps={[]}
        toolCalls={[]}
        drafts={asArray(reviewDrafts).filter((draft) => draft.source_run_id === reviewRun?.run_id)}
        modelCalls={asArray(reviewModelCalls)}
        evaluations={asArray(reviewEvaluations)}
        emptyMessage={t("organizer.agentEvidence.emptyReview")}
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.review.touchpointSummary")}</CardTitle>
            <CardDescription>{t("organizer.review.touchpointSummaryDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            {touchpointEntries.map((entry) => (
              <div key={entry.key} className="rounded-md border border-slate-200 p-3">
                <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">{entry.label}</div>
                <div className="mt-2 text-lg font-semibold text-ink">{entry.value}</div>
              </div>
            ))}
            {!touchpointEntries.length ? <p className="text-sm text-slate-500">{t("organizer.review.touchpointSummaryEmpty")}</p> : null}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.review.merchantOutcomes")}</CardTitle>
            <CardDescription>{t("organizer.review.merchantOutcomesDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {merchantOutcomes.map((outcome, index) => (
              <div key={`${displayValue(outcome.merchant_id)}-${index}`} className="rounded-md border border-slate-200 p-3">
                <div className="font-medium">
                  {displayValue(outcome.merchant_name)
                    ? localizedDemoText(displayValue(outcome.merchant_name), t)
                    : displayValue(outcome.merchant_id)
                      ? merchantLabel(displayValue(outcome.merchant_id), t)
                      : t("organizer.review.merchantOutcome")}
                </div>
                <div className="mt-2 text-sm text-slate-700">
                  {localizedDemoText(
                    displayValue(outcome.outcome) || displayValue(outcome.summary) || displayValue(outcome.result),
                    t
                  )}
                </div>
                <div className="mt-2 text-xs text-slate-500">
                  {[
                    displayValue(outcome.total_interactions) ? `${totalInteractionsLabel} ${displayValue(outcome.total_interactions)}` : "",
                    displayValue(outcome.coupon_claims) ? `${couponClaimsLabel} ${displayValue(outcome.coupon_claims)}` : "",
                    displayValue(outcome.coupon_redemptions) ? `${couponRedemptionsLabel} ${displayValue(outcome.coupon_redemptions)}` : ""
                  ]
                    .filter(Boolean)
                    .join(" | ")}
                </div>
              </div>
            ))}
            {!merchantOutcomes.length ? <p className="text-sm text-slate-500">{t("organizer.review.merchantOutcomesEmpty")}</p> : null}
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{t("organizer.review.extensionTasks")}</CardTitle>
          <CardDescription>{t("organizer.review.extensionTasksDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-slate-700">
            {extensionTasks.map((task, index) => (
              <li key={`${displayValue(task.title)}-${index}`} className="rounded-md border border-slate-200 p-3">
                <div className="font-medium">
                  {localizedDemoText(
                    displayValue(task.title) || extensionTaskTypeLabel(displayValue(task.task_type)) || t("organizer.review.extensionTask"),
                    t
                  )}
                </div>
                <div className="mt-1 text-slate-600">{localizedDemoText(displayValue(task.rationale), t)}</div>
                <div className="mt-2 space-y-1 text-xs text-slate-500">
                  {unknownArray(task.metric_refs).length ? (
                    <div>
                      {metricRefsLabel}: {unknownArray(task.metric_refs).map((item) => metricLabel(displayValue(item))).join(", ")}
                    </div>
                  ) : null}
                  {unknownArray(task.merchant_ids).length ? (
                    <div>
                      {merchantRefsLabel}: {unknownArray(task.merchant_ids).map((merchantId) => merchantLabel(displayValue(merchantId), t)).join(", ")}
                    </div>
                  ) : null}
                </div>
              </li>
            ))}
            {!extensionTasks.length ? <li>{t("organizer.review.extensionTasksEmpty")}</li> : null}
          </ul>
        </CardContent>
      </Card>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.review.recommendations")}</CardTitle>
            <CardDescription>{t("organizer.review.recommendationsDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
              {recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
              {!recommendations.length ? <li>{t("organizer.review.noRecommendation")}</li> : null}
            </ul>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{t("organizer.review.metricsLessons")}</CardTitle>
          <CardDescription>{t("organizer.review.metricsLessonsDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {lessons.map((item) => (
              <li key={item}>{item}</li>
            ))}
            {!lessons.length ? <li>{t("organizer.review.noMetricLesson")}</li> : null}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
