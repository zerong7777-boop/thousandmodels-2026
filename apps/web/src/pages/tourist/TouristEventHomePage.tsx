import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { NoticeFeed, ProductPageHeader, RouteProgress } from "../../components/product";
import { localizedDemoList, localizedDemoText, localizedRoutePoint, useI18n } from "../../i18n";
import { asArray, useAsyncData } from "../productUtils";

export function TouristEventHomePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const points = asArray(event?.route_points).map((point) => localizedRoutePoint(point, t));
  const firstPoint = points[0];
  const notices = localizedDemoList(asArray(event?.public_notices).map((notice) => notice.message), t);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("tourist.event.eyebrow")}
        title={localizedDemoText(event?.title ?? "Historic District Night Tour", t)}
        description={t("tourist.event.description")}
        meta={[
          localizedDemoText(event?.area ?? "Rua da Felicidade", t),
          t("tourist.event.storyStops", { count: points.length || 1 }),
          t("tourist.event.liveUpdate")
        ]}
        status={event?.status ?? "active"}
        tone="visitor"
      />

      <RouteProgress current={1} total={points.length || 1} />

      <NoticeFeed title={t("tourist.event.liveUpdate")} notices={notices.length ? notices : [t("tourist.event.noUpdate")]} />

      <Card>
        <CardHeader>
          <CardTitle>{t("tourist.event.nextStop")}</CardTitle>
          <CardDescription>{t("tourist.event.nextStopDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <div className="text-lg font-semibold">{firstPoint?.name ?? t("demo.event.area")}</div>
            <div className="text-sm text-slate-600">{firstPoint?.story ?? t("tourist.event.streetStory")}</div>
          </div>
          <Badge variant="lotus">{t("tourist.event.visitorTask")}</Badge>
          <Button asChild>
            <a href={`/user/events/${eventId}/route`}>{t("tourist.event.viewRoute")}</a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
