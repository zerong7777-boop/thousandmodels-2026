import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../../api";
import { EmptyState } from "../../components/product";
import { localizedDemoText, localizedStatus, useI18n } from "../../i18n";
import type { EventSummary } from "../../types";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { EventCreatePanel } from "./EventCreatePanel";

function navigateTo(path: string, onNavigate?: (path: string) => void) {
  if (onNavigate) {
    onNavigate(path);
    return;
  }
  window.location.assign(path);
}

export function OrganizerEventsPage({ onNavigate }: { onNavigate?: (path: string) => void } = {}) {
  const { t } = useI18n();
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [seedFeedback, setSeedFeedback] = useState<"error" | null>(null);
  const loadRequestRef = useRef(0);
  const mountedRef = useRef(true);

  const loadEvents = useCallback(async () => {
    const requestId = ++loadRequestRef.current;
    setLoading(true);
    setLoadError(false);
    try {
      const nextEvents = await api.getEvents();
      if (!mountedRef.current || requestId !== loadRequestRef.current) return;
      setEvents(nextEvents);
    } catch {
      if (!mountedRef.current || requestId !== loadRequestRef.current) return;
      setEvents([]);
      setLoadError(true);
    } finally {
      if (mountedRef.current && requestId === loadRequestRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadEvents();
    return () => {
      mountedRef.current = false;
    };
  }, [loadEvents]);

  const handleCreated = async (event: EventSummary) => {
    await loadEvents();
    navigateTo(`/organizer/events/${event.event_id}`, onNavigate);
  };

  const seedDemoEvent = async () => {
    setSeedFeedback(null);
    try {
      await api.seed();
      await loadEvents();
    } catch {
      setSeedFeedback("error");
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-harbor">{t("organizer.events.eyebrow")}</p>
        <h1 className="text-2xl font-semibold">{t("organizer.events.title")}</h1>
      </div>

      <EventCreatePanel onCreated={(event) => void handleCreated(event)} />

      {loadError ? (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
          {t("organizer.events.loadError")}
        </div>
      ) : null}

      {seedFeedback ? (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
          {t("organizer.events.seedError")}
        </div>
      ) : null}

      {!loading && !events.length ? (
        <EmptyState
          title={t("organizer.events.emptyTitle")}
          description={t("organizer.events.emptyDescription")}
          action={
            <Button variant="secondary" onClick={() => void seedDemoEvent()}>
              {t("organizer.events.seedDemo")}
            </Button>
          }
        />
      ) : null}

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
            <span className="text-sm text-slate-600">
              {t("organizer.events.planVersion", { version: event.current_plan_version })}
            </span>
            <div className="flex flex-wrap gap-2">
              <Button asChild variant="secondary">
                <a href={`/organizer/events/${event.event_id}`}>{t("organizer.events.openWorkspace")}</a>
              </Button>
              <Button asChild variant="secondary">
                <a href={`/organizer/events/${event.event_id}/exceptions`}>{t("shell.nav.exceptions")}</a>
              </Button>
              <Button asChild variant="secondary">
                <a href={`/organizer/events/${event.event_id}/review`}>{t("shell.nav.review")}</a>
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
