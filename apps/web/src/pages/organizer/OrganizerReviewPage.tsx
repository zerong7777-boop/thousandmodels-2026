import { api } from "../../api";
import { MetricTile, ProductPageHeader } from "../../components/product";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function OrganizerReviewPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: report } = useAsyncData(() => api.getReviewReport(eventId), null);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Review center"
        title="Metric-backed review report"
        description={report?.summary ?? "Review report is not generated yet."}
        meta={["H5 visits 428", "Check-ins 136", "Response time 4 min", "Budget used 82%"]}
        status="ready"
      />
      <div className="grid gap-4 md:grid-cols-5">
        <MetricTile label="H5 visits" value="428" detail="H5 visits 428" tone="info" />
        <MetricTile label="Check-ins" value="136" detail="Story stop scans." tone="success" />
        <MetricTile label="Response time" value="4 min" detail="Median recovery acknowledgement." tone="success" />
        <MetricTile label="Queue pressure" value="medium" detail="One merchant reported pressure." tone="warning" />
        <MetricTile label="Budget used" value="82%" detail="Within deterministic demo budget." tone="success" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>What worked</CardTitle>
            <CardDescription>Route and merchant results.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-slate-700">
            <p>{report?.route_result ?? "Route result pending."}</p>
            <p>{report?.merchant_result ?? "Merchant result pending."}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>Next event improvements.</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
              {asArray(report?.next_event_recommendations).map((item) => (
                <li key={item}>{item}</li>
              ))}
              {!asArray(report?.next_event_recommendations).length ? <li>No recommendation yet.</li> : null}
            </ul>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Metrics and lessons</CardTitle>
          <CardDescription>Evidence that should inform the next event.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {asArray(report?.lessons_learned).map((item) => (
              <li key={item}>{item}</li>
            ))}
            {!asArray(report?.lessons_learned).length ? <li>No metric lesson yet.</li> : null}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
