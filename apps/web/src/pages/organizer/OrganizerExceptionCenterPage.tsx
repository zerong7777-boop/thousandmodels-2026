import { useMemo, useState } from "react";
import { api } from "../../api";
import type { Incident, RecoveryProposal } from "../../types";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { ApprovalPanel, ProductPageHeader, RecoveryDiff, StatusPill } from "../../components/product";
import { asArray, useAsyncData } from "../productUtils";

export function OrganizerExceptionCenterPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { data: exceptions } = useAsyncData(() => api.getIncidents(eventId), []);
  const incidents = asArray(exceptions) as Incident[];
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [proposal, setProposal] = useState<RecoveryProposal | null>(null);
  const [confirmationMessage, setConfirmationMessage] = useState<string | null>(null);
  const selectedIncident = useMemo(
    () => incidents.find((item) => item.incident_id === selectedIncidentId) ?? incidents[0],
    [incidents, selectedIncidentId]
  );

  const fallbackChanges = [
    "Pause the sold-out merchant stop.",
    "Move visitors to the next available indoor story point.",
    "Publish a visitor-safe notice once the organizer confirms."
  ];
  const before = [
    "Visitors continue toward the sold-out first snack stop.",
    "Merchant m001 remains assigned as an active arrival point.",
    "Public H5 still shows the original stop order."
  ];
  const after = proposal?.recommended_changes?.length ? proposal.recommended_changes : fallbackChanges;

  const prepareProposal = async (incident: Incident) => {
    const nextProposal = await api.createRecoveryProposal(eventId, incident.incident_id);
    setProposal(nextProposal);
    setSelectedIncidentId(incident.incident_id);
    setConfirmationMessage(null);
  };

  const confirmRecovery = async () => {
    if (!proposal?.proposal_id) {
      setConfirmationMessage("Recovery update prepared. Generate a proposal before approval when running against the live API.");
      return;
    }
    await api.approveRecoveryProposal(eventId, proposal.proposal_id);
    setConfirmationMessage("Recovery update confirmed. Public notice and route v2 are ready.");
  };

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Live exception center"
        title="Recovery suggestions"
        description="Review affected stops, merchant impact, route changes, and visitor release consequences for approval."
        meta={["Decision workflow", "Route update", "Visitor release"]}
        status={selectedIncident?.status ?? "open"}
      />

      <div className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <CardTitle>Exception queue</CardTitle>
            <CardDescription>Items that need an operator decision.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {incidents.map((item) => (
              <button
                className="w-full rounded-lg border border-slate-200 bg-white p-3 text-left transition hover:border-teal-300 hover:bg-teal-50"
                key={item.incident_id ?? item.event_id}
                onClick={() => {
                  setSelectedIncidentId(item.incident_id);
                  setConfirmationMessage(null);
                }}
                type="button"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="font-medium text-ink">{item.trigger_detail ?? "Merchant status changed"}</div>
                    <div className="mt-1 text-sm text-slate-600">
                      Affected merchant: {asArray(item.affected_merchants).join(", ") || "m001"}
                    </div>
                  </div>
                  <StatusPill tone={item.severity === "high" ? "danger" : "warning"}>{item.status ?? "open"}</StatusPill>
                </div>
              </button>
            ))}
            {!incidents.length ? (
              <div className="rounded-md border border-dashed border-slate-200 p-4 text-sm text-slate-500">
                No live exceptions are waiting for review.
              </div>
            ) : null}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Impact scope</CardTitle>
              <CardDescription>Who and which stop are affected by the runtime exception.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">Affected merchant</div>
                <div className="mt-2 text-lg font-semibold text-ink">
                  {asArray(selectedIncident?.affected_merchants).join(", ") || "m001"}
                </div>
                <p className="mt-2 text-sm leading-5 text-slate-600">
                  Inventory status blocks new visitor arrivals until the route is recovered.
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">Affected stop</div>
                <div className="mt-2 text-lg font-semibold text-ink">
                  {asArray(selectedIncident?.affected_route_points).join(", ") || "rp001"}
                </div>
                <p className="mt-2 text-sm leading-5 text-slate-600">
                  The first story stop should stop receiving public traffic once approval is complete.
                </p>
              </div>
            </CardContent>
          </Card>

          <RecoveryDiff before={before} after={after} />
        </div>

        <div className="space-y-4">
          <ApprovalPanel
            actionLabel="Confirm recovery update"
            consequence="Approving this recovery creates route v2, updates merchant execution guidance, and releases the visitor-safe public notice."
            description="The suggestion keeps visitors moving while removing the sold-out merchant from the active arrival path."
            onApprove={() => void confirmRecovery()}
            title="Recovery confirmation"
          >
            {selectedIncident ? (
              <Button size="sm" variant="secondary" onClick={() => void prepareProposal(selectedIncident)}>
                Prepare recovery suggestion
              </Button>
            ) : null}
          </ApprovalPanel>

          <Card>
            <CardHeader>
              <CardTitle>Public notice preview</CardTitle>
              <CardDescription>Copy released to the visitor H5 once the organizer approves.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm leading-5 text-blue-900">
                {proposal?.public_notice_patch ?? "Please continue to the indoor tea stop. Your route has been updated."}
              </div>
              {confirmationMessage ? <StatusPill tone="success">{confirmationMessage}</StatusPill> : null}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
