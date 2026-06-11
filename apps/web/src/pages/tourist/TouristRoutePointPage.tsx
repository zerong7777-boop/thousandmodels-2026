import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { ProductPageHeader, StatusPill } from "../../components/product";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function TouristRoutePointPage({
  eventId = "demo-night-tour",
  pointId = "rp001"
}: {
  eventId?: string;
  pointId?: string;
}) {
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const point = asArray(event?.route_points).find((item) => item.point_id === pointId) ?? asArray(event?.route_points)[0];

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Next stop"
        title={point?.name ?? "Route stop"}
        description="Story, arrival cue, and visitor task for this stop."
        meta={["Visitor task", point?.current_status ?? "active"]}
        status={point?.current_status ?? "active"}
        tone="visitor"
      />
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-3">
            <div>
              <CardTitle>{point?.name ?? "Route stop"}</CardTitle>
              <CardDescription>Story and visitor task</CardDescription>
            </div>
            <Badge variant="lotus">{point?.current_status ?? "active"}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-700">{point?.story ?? "Story details will appear here."}</p>
          <StatusPill tone="visitor">Visitor task</StatusPill>
          <div className="rounded-md border border-violet-100 bg-violet-50 p-3 text-sm text-violet-800">
            {point?.visitor_task ?? "Check in when you arrive."}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
