import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { ProductPageHeader, StatusPill } from "../../components/product";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { localizedRoutePoint, localizedStatus, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

export function TouristRoutePointPage({
  eventId = "demo-night-tour",
  pointId = "rp001"
}: {
  eventId?: string;
  pointId?: string;
}) {
  const { t } = useI18n();
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const point =
    asArray(event?.route_points).find((item) => item.point_id === pointId) ?? asArray(event?.route_points)[0];
  const displayPoint = point ? localizedRoutePoint(point, t) : null;
  const displayStatus = displayPoint?.current_status ?? "active";

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("tourist.point.eyebrow")}
        title={displayPoint?.name ?? t("tourist.point.routeStop")}
        description={t("tourist.point.description")}
        meta={[t("tourist.event.visitorTask"), localizedStatus(displayStatus, t)]}
        status={displayStatus}
        tone="visitor"
      />
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-3">
            <div>
              <CardTitle>{displayPoint?.name ?? t("tourist.point.routeStop")}</CardTitle>
              <CardDescription>{t("tourist.point.storyAndTask")}</CardDescription>
            </div>
            <Badge variant="lotus">{localizedStatus(displayStatus, t)}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-700">{displayPoint?.story ?? t("tourist.point.storyPending")}</p>
          <StatusPill tone="visitor">{t("tourist.event.visitorTask")}</StatusPill>
          <div className="rounded-md border border-violet-100 bg-violet-50 p-3 text-sm text-violet-800">
            {displayPoint?.visitor_task ?? t("tourist.point.checkIn")}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
