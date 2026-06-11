import { api } from "../../api";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { useAsyncData } from "../productUtils";

export function OrganizerEventsPage() {
  const { data: events } = useAsyncData(() => api.getEvents(), []);

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-harbor">Event portfolio</p>
        <h1 className="text-2xl font-semibold">Events</h1>
      </div>
      {events.map((event) => (
        <Card key={event.event_id}>
          <CardHeader>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <CardTitle>{event.title}</CardTitle>
                <CardDescription>
                  {event.area} · {event.date} · {event.time_window}
                </CardDescription>
              </div>
              <Badge variant={event.status === "active" ? "success" : "neutral"}>{event.status}</Badge>
            </div>
          </CardHeader>
          <CardContent className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-sm text-slate-600">Public release: {event.public_release_status}</span>
            <Button asChild variant="secondary">
              <a href={`/organizer/events/${event.event_id}`}>Open workspace</a>
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
