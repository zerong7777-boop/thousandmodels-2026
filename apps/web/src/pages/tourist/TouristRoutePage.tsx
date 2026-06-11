import { api } from "../../api";
import { Card, CardContent } from "../../ui/card";
import { ProductPageHeader, RouteProgress, RouteStopCard } from "../../components/product";
import { asArray, useAsyncData } from "../productUtils";

export function TouristRoutePage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const points = asArray(event?.route_points);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Route"
        title="Story stops"
        description="Move at your own pace, track route progress, and complete each visitor task."
        meta={[`${points.length || 1} stops`, "Next stop available", "Live update"]}
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
            <CardContent className="pt-5 text-sm text-slate-500">Route details are being prepared.</CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
