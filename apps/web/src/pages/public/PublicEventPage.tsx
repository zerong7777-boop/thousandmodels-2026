import { useState } from "react";
import { api } from "../../api";
import { NoticeFeed, ProductPageHeader, RouteProgress, RouteStopCard, StatusPill } from "../../components/product";
import { LanguageSwitcher, localizedDemoList, localizedDemoText, localizedRoutePoint, useI18n } from "../../i18n";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

function recordText(record: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) return value;
  }
  return "";
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function unknownArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function readNumber(value: unknown): number | null {
  if (typeof value === "number") return value;
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function firstString(value: unknown, keys: string[]) {
  const record = asRecord(value);
  if (!record) return "";
  return recordText(record, keys);
}

export function PublicEventPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null, [eventId]);
  const [actionFeedback, setActionFeedback] = useState<{ tone: "success" | "danger"; text: string } | null>(null);
  const [interactionId, setInteractionId] = useState<string>("");
  const [redemptionId, setRedemptionId] = useState<string>("");
  const eventPage = event?.event_page;
  const storySections = asArray(eventPage?.story_sections);
  const merchantHighlights = asArray(eventPage?.merchant_highlights);
  const routeHighlights = asArray(eventPage?.route_highlights);
  const eventRecord = asRecord(event);
  const eventPageRecord = asRecord(eventPage);
  const points = asArray(event?.route_points).map((point) => localizedRoutePoint(point, t));
  const routeNames = localizedDemoList(asArray(event?.route), t);
  const displayPoints =
    points.length > 0
      ? points
      : routeNames.map((name, index) => ({
          point_id: `route-${index + 1}`,
          name,
          story: t("demo.route.genericStory"),
          visitor_task: localizedDemoText(asArray(event?.checkin_tasks)[index] ?? "Follow the story prompt at this stop.", t),
          current_status: "active"
        }));
  const eventPageNotices = localizedDemoList(
    asArray(eventPage?.notices)
      .map((notice) => recordText(notice, ["message", "body", "text", "title"]))
      .filter((notice) => notice.trim()),
    t
  );
  const projectedNotices = localizedDemoList(asArray(event?.public_notices).map((notice) => notice.message), t);
  const notices = projectedNotices.length
    ? projectedNotices.filter((notice) => notice.trim())
    : localizedDemoList(asArray(event?.notices), t).filter((notice) => notice.trim());
  const visibleNotices = eventPageNotices.length ? eventPageNotices : notices;
  const hasEventPage = Boolean(eventPage);
  const planVersion =
    readNumber(eventRecord?.["current" + "_plan" + "_version"]) ??
    readNumber(eventPageRecord?.["plan_version"]) ??
    readNumber(eventPageRecord?.["planVersion"]);
  const packageCandidates = [
    eventRecord?.["interaction_package"],
    ...unknownArray(eventRecord?.["interaction_packages"]),
    eventRecord?.["merchant_edge_packages"],
    ...unknownArray(asRecord(eventRecord?.["merchant_edge_packages"])?.packages),
    eventPageRecord?.["interaction_package"],
    ...merchantHighlights,
    eventPageRecord
  ];
  const touchpointCollections = packageCandidates.flatMap((candidate) => {
    const record = asRecord(candidate);
    return record ? unknownArray(record.touchpoints) : [];
  });
  const couponCollections = packageCandidates.flatMap((candidate) => {
    const record = asRecord(candidate);
    return record ? unknownArray(record.coupon_rules) : [];
  });
  const selectedTouchpointId =
    touchpointCollections.map((item) => firstString(item, ["id", "touchpoint_id"])).find(Boolean) ||
    packageCandidates.map((item) => firstString(item, ["touchpoint_id"])).find(Boolean) ||
    "";
  const selectedCouponRuleId =
    couponCollections.map((item) => firstString(item, ["id", "coupon_rule_id"])).find(Boolean) ||
    packageCandidates.map((item) => firstString(item, ["coupon_rule_id"])).find(Boolean) ||
    "";
  const availableInteractionId =
    interactionId || packageCandidates.map((item) => firstString(item, ["anonymous_interaction_id"])).find(Boolean) || "";
  const availableRedemptionId =
    redemptionId ||
    packageCandidates.map((item) => firstString(item, ["coupon_redemption_id", "redemption_id"])).find(Boolean) ||
    "";
  const actionUnavailable =
    !selectedTouchpointId && !selectedCouponRuleId && !availableInteractionId && !availableRedemptionId;

  const recordScan = async () => {
    if (!selectedTouchpointId) return;
    setActionFeedback(null);
    try {
      const interaction = await api.recordTouchpointInteraction(eventId, selectedTouchpointId, {
        interaction_type: "scan",
        source: "public-event-demo"
      });
      setInteractionId(interaction.anonymous_interaction_id);
      setActionFeedback({ tone: "success", text: t("public.event.scanSuccess") });
    } catch {
      setActionFeedback({ tone: "danger", text: t("public.event.scanError") });
    }
  };

  const claimOffer = async () => {
    if (!selectedCouponRuleId || !availableInteractionId) return;
    setActionFeedback(null);
    try {
      const redemption = await api.claimCoupon(eventId, selectedCouponRuleId, availableInteractionId);
      setRedemptionId(redemption.id);
      setActionFeedback({ tone: "success", text: t("public.event.claimSuccess") });
    } catch {
      setActionFeedback({ tone: "danger", text: t("public.event.claimError") });
    }
  };

  const redeemOffer = async () => {
    if (!availableRedemptionId) return;
    setActionFeedback(null);
    try {
      await api.redeemCoupon(eventId, availableRedemptionId);
      setActionFeedback({ tone: "success", text: t("public.event.redeemSuccess") });
    } catch {
      setActionFeedback({ tone: "danger", text: t("public.event.redeemError") });
    }
  };

  return (
    <main className="min-h-screen bg-violet-50 px-4 py-5 text-ink">
      <div className="mx-auto max-w-xl space-y-4">
        <div className="flex justify-end">
          <LanguageSwitcher />
        </div>
        <ProductPageHeader
          eyebrow={t("public.event.visitorRoute")}
          title={localizedDemoText(eventPage?.title ?? t("public.event.tonightsRoute"), t)}
          description={localizedDemoText(eventPage?.subtitle ?? event?.title ?? event?.theme ?? "Historic District Night Tour", t)}
          meta={[
            localizedDemoText(event?.area ?? "Rua da Felicidade", t),
            t("public.event.storyStops", { count: hasEventPage ? storySections.length || displayPoints.length || 2 : displayPoints.length || 2 }),
            planVersion ? t("public.event.planVersionMeta", { version: planVersion }) : t("public.event.noticesReady")
          ]}
          status={event?.status ?? "active"}
          tone="visitor"
        />

        <Card>
          <CardHeader>
            <CardTitle>{t("public.event.demoActionsTitle")}</CardTitle>
            <CardDescription>
              {planVersion
                ? t("public.event.demoActionsDescriptionWithVersion", { version: planVersion })
                : t("public.event.demoActionsDescription")}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {actionFeedback ? (
              <div
                className={`rounded-md border p-3 text-sm ${
                  actionFeedback.tone === "success"
                    ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                    : "border-rose-200 bg-rose-50 text-rose-900"
                }`}
              >
                {actionFeedback.text}
              </div>
            ) : null}
            <div className="flex flex-wrap gap-3">
              <Button disabled={!selectedTouchpointId} size="sm" onClick={() => void recordScan()}>
                {t("public.event.scanAction")}
              </Button>
              <Button
                disabled={!selectedCouponRuleId || !availableInteractionId}
                size="sm"
                variant="secondary"
                onClick={() => void claimOffer()}
              >
                {t("public.event.claimAction")}
              </Button>
              <Button
                disabled={!availableRedemptionId}
                size="sm"
                variant="secondary"
                onClick={() => void redeemOffer()}
              >
                {t("public.event.redeemAction")}
              </Button>
            </div>
            {actionUnavailable ? <p className="text-sm text-slate-500">{t("public.event.actionUnavailable")}</p> : null}
          </CardContent>
        </Card>

        <NoticeFeed
          notices={visibleNotices.length ? visibleNotices : [t("public.event.defaultNotice")]}
          title={t("public.event.liveUpdate")}
        />

        {hasEventPage ? (
          <div className="space-y-4">
            <section className="space-y-3">
              <h2 className="text-lg font-semibold text-ink">{t("public.event.storySectionsTitle")}</h2>
              {storySections.map((section, index) => {
                const title = recordText(section, ["title", "heading", "name"]);
                const body = recordText(section, ["body", "content", "story", "description"]);
                return (
                  <article key={`${title}-${index}`} className="rounded-lg border border-violet-100 bg-white p-4 shadow-sm">
                    {title ? <h3 className="font-semibold text-ink">{localizedDemoText(title, t)}</h3> : null}
                  {body ? <p className="mt-2 text-sm leading-5 text-slate-700">{localizedDemoText(body, t)}</p> : null}
                </article>
              );
            })}
              {!storySections.length ? <p className="text-sm text-slate-600">{t("public.event.storySectionsEmpty")}</p> : null}
            </section>

            {merchantHighlights.length ? (
              <section className="space-y-3">
                <h2 className="text-lg font-semibold text-ink">{t("public.event.merchantHighlightsTitle")}</h2>
                {merchantHighlights.map((merchant, index) => {
                  const title = recordText(merchant, ["name", "merchant_name", "title"]);
                  const body = recordText(merchant, ["highlight", "body", "description", "offer"]);
                  return (
                    <article key={`${title}-${index}`} className="rounded-lg border border-violet-100 bg-white p-4 shadow-sm">
                      <h3 className="font-semibold text-ink">{localizedDemoText(title || t("public.event.merchantHighlight"), t)}</h3>
                      {body ? <p className="mt-2 text-sm leading-5 text-slate-700">{localizedDemoText(body, t)}</p> : null}
                    </article>
                  );
                })}
              </section>
            ) : null}

            {routeHighlights.length ? (
              <section className="space-y-3">
                <h2 className="text-lg font-semibold text-ink">{t("public.event.routeHighlightsTitle")}</h2>
                {routeHighlights.map((route, index) => {
                  const title = recordText(route, ["name", "title", "stop"]);
                  const body = recordText(route, ["description", "body", "story", "note", "visitor_task"]);
                  return (
                    <article key={`${title}-${index}`} className="rounded-lg border border-violet-100 bg-white p-4 shadow-sm">
                      <h3 className="font-semibold text-ink">{localizedDemoText(title || t("public.event.routeHighlight"), t)}</h3>
                      {body ? <p className="mt-2 text-sm leading-5 text-slate-700">{localizedDemoText(body, t)}</p> : null}
                    </article>
                  );
                })}
              </section>
            ) : null}
          </div>
        ) : (
          <>
            <section aria-label={t("public.event.routeProgress")}>
              <RouteProgress current={1} total={displayPoints.length || 2} />
            </section>

            <div className="space-y-3">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-lg font-semibold text-ink">{t("public.event.storyStopTitle")}</h2>
                <StatusPill tone="visitor">{t("public.event.visitorTask")}</StatusPill>
              </div>
              {displayPoints.map((point, index) => (
                <RouteStopCard
                  index={index + 1}
                  key={point.point_id ?? `${point.name}-${index}`}
                  name={point.name}
                  status={point.current_status ?? "active"}
                  story={point.story}
                  task={point.visitor_task}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
