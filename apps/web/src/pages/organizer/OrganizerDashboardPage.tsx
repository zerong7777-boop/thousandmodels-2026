import { AlertTriangle, CheckCircle2, Route, Store } from "lucide-react";
import { api } from "../../api";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { Button } from "../../ui/button";
import { ActivityTimeline, AttentionQueue, MetricTile, ProductPageHeader } from "../../components/product";
import { useAsyncData } from "../productUtils";

export function OrganizerDashboardPage() {
  const { t } = useI18n();
  const { data: events } = useAsyncData(() => api.getEvents(), []);
  const current = events[0];
  const eventTitle = localizedDemoText(current?.title ?? "Historic District Night Tour", t);
  const eventArea = localizedDemoText(current?.area ?? "Rua da Felicidade", t);
  const eventWindow = current?.time_window ?? "18:00-21:30";
  const eventDate = current?.date ?? "2026-07-18";
  const planVersion = current?.current_plan_version ?? 2;
  const releaseState = current?.public_release_status ?? "published";
  const displayReleaseState = localizedStatus(releaseState, t);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("organizer.dashboard.eyebrow")}
        title={eventTitle}
        description={t("organizer.dashboard.description")}
        meta={[eventArea, eventDate, eventWindow, t("organizer.dashboard.currentPlanMeta", { version: planVersion })]}
        status={releaseState}
        actions={
          <>
            <Button asChild>
              <a href="/organizer/events/demo-night-tour">{t("organizer.dashboard.enterWorkspace")}</a>
            </Button>
            <Button asChild variant="secondary">
              <a href="/organizer/events/demo-night-tour/exceptions">{t("organizer.dashboard.openExceptions")}</a>
            </Button>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-4">
        <MetricTile icon={<Route size={18} />} label={t("organizer.dashboard.currentPlan")} value={`v${planVersion}`} detail={t("organizer.dashboard.currentPlanDetail")} tone="success" />
        <MetricTile icon={<AlertTriangle size={18} />} label={t("organizer.dashboard.liveExceptions")} value="1" detail={t("organizer.dashboard.liveExceptionsDetail")} tone="warning" />
        <MetricTile icon={<Store size={18} />} label={t("organizer.dashboard.merchantReadiness")} value="7/8" detail={t("organizer.dashboard.merchantReadinessDetail")} tone="info" />
        <MetricTile icon={<CheckCircle2 size={18} />} label={t("organizer.dashboard.publicNoticeState")} value={displayReleaseState} detail={t("organizer.dashboard.publicNoticeDetail")} tone="success" />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
        <AttentionQueue
          title={t("organizer.dashboard.needsAttention")}
          items={[
            {
              title: t("organizer.dashboard.recoveryReady"),
              detail: t("organizer.dashboard.recoveryReadyDetail"),
              badge: t("organizer.dashboard.badgeDecision"),
              tone: "warning",
              action: (
                <Button asChild size="sm" variant="secondary">
                  <a href="/organizer/events/demo-night-tour/exceptions">{t("organizer.dashboard.review")}</a>
                </Button>
              )
            },
            {
              title: t("organizer.dashboard.inventoryException"),
              detail: t("organizer.dashboard.inventoryExceptionDetail"),
              badge: t("organizer.dashboard.badgeHigh"),
              tone: "danger"
            },
            {
              title: t("organizer.dashboard.publicNoticePublished"),
              detail: t("organizer.dashboard.publicNoticePublishedDetail"),
              badge: t("organizer.dashboard.badgeRelease")
            }
          ]}
        />

        <ActivityTimeline
          title={t("organizer.dashboard.timelineTitle")}
          items={[
            {
              time: "18:02",
              title: t("organizer.dashboard.timelinePlanApproved"),
              detail: t("organizer.dashboard.timelinePlanApprovedDetail"),
              tone: "success"
            },
            {
              time: "18:44",
              title: t("organizer.dashboard.timelineMerchantStatus"),
              detail: t("organizer.dashboard.timelineMerchantStatusDetail"),
              tone: "warning"
            },
            {
              time: "18:46",
              title: t("organizer.dashboard.timelineRecoveryPrepared"),
              detail: t("organizer.dashboard.timelineRecoveryPreparedDetail"),
              tone: "info"
            },
            {
              time: "18:51",
              title: t("organizer.dashboard.timelineVisitorUpdated"),
              detail: t("organizer.dashboard.timelineVisitorUpdatedDetail"),
              tone: "success"
            }
          ]}
        />
      </div>
    </div>
  );
}
