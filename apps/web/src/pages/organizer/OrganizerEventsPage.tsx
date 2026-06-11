import { api } from "../../api";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { useAsyncData } from "../productUtils";

export function OrganizerEventsPage() {
  const { t } = useI18n();
  const { data: events } = useAsyncData(() => api.getEvents(), []);

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-harbor">{t("organizer.events.eyebrow")}</p>
        <h1 className="text-2xl font-semibold">{t("organizer.events.title")}</h1>
      </div>
      {events.map((event) => (
        <Card key={event.event_id}>
          <CardHeader>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <CardTitle>{localizedDemoText(event.title, t)}</CardTitle>
                <CardDescription>
                  {localizedDemoText(event.area, t)} / {event.date} / {event.time_window}
                </CardDescription>
              </div>
              <Badge variant={event.status === "active" ? "success" : "neutral"}>
                {localizedStatus(event.status, t)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-sm text-slate-600">
              {t("organizer.events.publicRelease", { status: localizedStatus(event.public_release_status, t) })}
            </span>
            <Button asChild variant="secondary">
              <a href={`/organizer/events/${event.event_id}`}>{t("organizer.events.openWorkspace")}</a>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
