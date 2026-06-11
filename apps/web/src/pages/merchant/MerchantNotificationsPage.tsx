import { api } from "../../api";
import { NoticeFeed, ProductPageHeader } from "../../components/product";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function MerchantNotificationsPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: publicEvent } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const notices = asArray(publicEvent?.public_notices).map((notice) => notice.message);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Organizer notices"
        title="Event messages"
        description="Operational messages that affect your store during the event."
        meta={["Recovery notice", "Staff alignment", "Visitor-safe wording"]}
        status="current"
        tone="merchant"
      />

      <NoticeFeed
        title="Recovery notice"
        notices={notices.length ? notices : ["No recovery notice is active. Keep staff ready for organizer updates."]}
      />

      <Card>
        <CardHeader>
          <CardTitle>Current notices</CardTitle>
          <CardDescription>Keep staff aligned with these messages.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-slate-700">
            {(notices.length ? notices : ["No organizer notice is active."]).map((notice) => (
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
