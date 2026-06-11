import { api } from "../../api";
import { Card, CardContent } from "../../ui/card";
import { ProductPageHeader, RouteProgress, RouteStopCard } from "../../components/product";
import { localizedRoutePoint, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

export function TouristRoutePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const points = asArray(event?.route_points).map((point) => localizedRoutePoint(point, t));

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("tourist.route.eyebrow")}
        title={t("tourist.route.title")}
        description={t("tourist.route.description")}
        meta={[t("tourist.route.stops", { count: points.length || 1 }), t("tourist.route.nextStopAvailable"), t("tourist.route.liveUpdate")]}
        status={event?.status ?? "active"}
        tone="visitor"
      />

      <RouteProgress current={1} total={points.length || 1} />

      <div className="grid gap-3">
        {points.map((point, index) => (
          <RouteStopCard
            index={index + 1}
            key={point.point_id}
            name={point.name}
            status={point.current_status}
            story={point.story}
            task={point.visitor_task}
          />
        ))}
        {!points.length ? (
          <Card>
            <CardContent className="pt-5 text-sm text-slate-500">{t("tourist.route.routePrepared")}</CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
