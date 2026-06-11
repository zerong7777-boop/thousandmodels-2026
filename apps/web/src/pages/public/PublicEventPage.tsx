import { api } from "../../api";
import { NoticeFeed, ProductPageHeader, RouteProgress, RouteStopCard, StatusPill } from "../../components/product";
import { LanguageSwitcher, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

export function PublicEventPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const points = asArray(event?.route_points);
  const routeNames = asArray(event?.route);
  const displayPoints =
    points.length > 0
      ? points
      : routeNames.map((name, index) => ({
          point_id: `route-${index + 1}`,
          name,
          story: "A cultural stop on tonight's walking route.",
          visitor_task: asArray(event?.checkin_tasks)[index] ?? "Follow the story prompt at this stop.",
          current_status: "active"
        }));
  const projectedNotices = asArray(event?.public_notices).map((notice) => notice.message);
  const notices = projectedNotices.length ? projectedNotices : asArray(event?.notices);

  return (
    <main className="min-h-screen bg-violet-50 px-4 py-5 text-ink">
      <div className="mx-auto max-w-xl space-y-4">
        <div className="flex justify-end">
          <LanguageSwitcher />
        </div>
        <ProductPageHeader
          eyebrow={t("public.event.visitorRoute")}
          title={t("public.event.tonightsRoute")}
          description={event?.title ?? event?.theme ?? "Historic District Night Tour"}
          meta={[
            event?.area ?? t("demo.event.area"),
            t("public.event.storyStops", { count: displayPoints.length || 2 }),
            t("public.event.noticesReady")
          ]}
          status={event?.status ?? "active"}
          tone="visitor"
        />

        <NoticeFeed
          notices={notices.length ? notices : ["Enjoy the heritage route. Any route changes will appear here."]}
          title="Live update"
        />

        <section aria-label="Route progress">
          <RouteProgress current={1} total={displayPoints.length || 2} />
        </section>

        <div className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-ink">Story stops</h2>
            <StatusPill tone="visitor">Visitor task</StatusPill>
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
      </div>
    </main>
  );
}
