import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { NoticeFeed, ProductPageHeader, RouteProgress } from "../../components/product";
import { asArray, useAsyncData } from "../productUtils";

export function TouristEventHomePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const points = asArray(event?.route_points);
  const firstPoint = points[0];
  const notices = asArray(event?.public_notices).map((notice) => notice.message);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="My route"
        title={event?.title ?? "Historic District Night Tour"}
        description="Follow stories, visitor tasks, route progress, and live updates for tonight."
        meta={[event?.area ?? "Rua da Felicidade", `${points.length || 1} story stops`, "Live update"]}
        status={event?.status ?? "active"}
        tone="visitor"
      />

      <RouteProgress current={1} total={points.length || 1} />

      <NoticeFeed title="Live update" notices={notices.length ? notices : ["No route update is active."]} />

      <Card>
        <CardHeader>
          <CardTitle>Next stop</CardTitle>
          <CardDescription>Start here and continue through the route.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <div className="text-lg font-semibold">{firstPoint?.name ?? "Rua da Felicidade"}</div>
            <div className="text-sm text-slate-600">{firstPoint?.story ?? "A street story"}</div>
          </div>
          <Badge variant="lotus">Visitor task</Badge>
          <Button asChild>
            <a href={`/user/events/${eventId}/route`}>View route</a>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
