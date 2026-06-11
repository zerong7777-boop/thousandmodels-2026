import { api } from "../../api";
import { NoticeFeed, ProductPageHeader } from "../../components/product";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function TouristNoticesPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const notices = asArray(event?.public_notices).map((notice) => notice.message);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Notices"
        title="Visitor updates"
        description="Live update messages that help you follow tonight's route."
        meta={["Live update", "Visitor-safe messages"]}
        status="current"
        tone="visitor"
      />
      <NoticeFeed title="Live update" notices={notices.length ? notices : ["No visitor update is active."]} />
      <Card>
        <CardHeader>
          <CardTitle>Latest updates</CardTitle>
          <CardDescription>Only visitor-safe messages are shown here.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-slate-700">
            {(notices.length ? notices : ["No visitor update is active."]).map((notice) => (
              <li key={notice} className="rounded-md border border-slate-200 p-3">
                {notice}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
