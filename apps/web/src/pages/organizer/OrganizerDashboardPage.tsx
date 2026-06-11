import { AlertTriangle, CheckCircle2, Route, Store } from "lucide-react";
import { api } from "../../api";
import { Button } from "../../ui/button";
import { ActivityTimeline, AttentionQueue, MetricTile, ProductPageHeader } from "../../components/product";
import { useAsyncData } from "../productUtils";

export function OrganizerDashboardPage() {
  const { data: events } = useAsyncData(() => api.getEvents(), []);
  const current = events[0];
  const eventTitle = current?.title ?? "Historic District Night Tour";
  const eventArea = current?.area ?? "Rua da Felicidade";
  const eventWindow = current?.time_window ?? "18:00-21:30";
  const eventDate = current?.date ?? "2026-07-18";
  const planVersion = current?.current_plan_version ?? 2;
  const releaseState = current?.public_release_status ?? "published";

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Operations overview"
        title={eventTitle}
        description="Monitor approvals, live exception workload, public release state, and review evidence from one operations home."
        meta={[eventArea, eventDate, eventWindow, `Current route plan v${planVersion}`]}
        status={releaseState}
        actions={
          <>
            <Button asChild>
              <a href="/organizer/events/demo-night-tour">Enter event workspace</a>
            </Button>
            <Button asChild variant="secondary">
              <a href="/organizer/events/demo-night-tour/exceptions">Open exception center</a>
            </Button>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-4">
        <MetricTile icon={<Route size={18} />} label="Current plan" value={`v${planVersion}`} detail="Approved route visible to operations." tone="success" />
        <MetricTile icon={<AlertTriangle size={18} />} label="Live exceptions" value="1" detail="Inventory exception needs recovery review." tone="warning" />
        <MetricTile icon={<Store size={18} />} label="Merchant readiness" value="7/8" detail="One merchant is waiting for a route update." tone="info" />
        <MetricTile icon={<CheckCircle2 size={18} />} label="Public notice state" value={releaseState} detail="Visitor H5 has the latest route update." tone="success" />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
        <AttentionQueue
          title="Needs attention"
          items={[
            {
              title: "Recovery suggestion ready",
              detail: "Merchant m001 inventory exception has a deterministic recovery suggestion waiting for confirmation.",
              badge: "decision",
              tone: "warning",
              action: (
                <Button asChild size="sm" variant="secondary">
                  <a href="/organizer/events/demo-night-tour/exceptions">Review</a>
                </Button>
              )
            },
            {
              title: "Merchant m001 inventory exception",
              detail: "Sold-out status affects the first story stop and visitor arrival guidance.",
              badge: "high",
              tone: "danger"
            },
            {
              title: "Public notice published after confirmation",
              detail: "Visitor-facing copy is ready once the organizer approves the recovery update.",
              badge: "release"
            }
          ]}
        />

        <ActivityTimeline
          title="Activity timeline"
          items={[
            {
              time: "18:02",
              title: "Route plan approved",
              detail: "Initial route plan moved into event operations.",
              tone: "success"
            },
            {
              time: "18:44",
              title: "Merchant reported status",
              detail: "Merchant m001 reported inventory pressure from the workbench.",
              tone: "warning"
            },
            {
              time: "18:46",
              title: "Recovery suggestion prepared",
              detail: "Rule-based evidence created a safer indoor stop sequence.",
              tone: "info"
            },
            {
              time: "18:51",
              title: "Visitor route updated",
              detail: "Public notice and route order are ready for the H5 surface.",
              tone: "success"
            }
          ]}
        />
      </div>
    </div>
  );
}
