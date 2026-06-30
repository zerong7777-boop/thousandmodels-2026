import { useEffect, useMemo, useState } from "react";
import { localizedStatus, useI18n } from "../../i18n";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import type { EventMerchantSetupSummary, MerchantProfile } from "../../types";

type EventMerchantSetupPanelProps = {
  eventId: string;
  merchants: MerchantProfile[];
  setup: EventMerchantSetupSummary | null;
  onSave: (merchantIds: string[]) => Promise<void>;
  onMarkReady: (merchantId: string) => Promise<void>;
};

function operatingWindowSummary(merchant: MerchantProfile): string {
  const windows = merchant.operating_windows ?? [];
  if (windows.length) {
    return windows.map((window) => `${window.start_time}-${window.end_time}`).join(", ");
  }
  return merchant.opening_hours ?? "";
}

function eligibilityLabel(status: string | undefined, t: ReturnType<typeof useI18n>["t"]): string {
  if (status === "eligible") return t("organizer.workspace.eligibilityEligible");
  if (status === "needs_review") return t("organizer.workspace.eligibilityNeedsReview");
  if (status === "ineligible") return t("organizer.workspace.eligibilityIneligible");
  return t("organizer.workspace.eligibilityNeedsReview");
}

function readinessLabel(value: boolean | undefined, t: ReturnType<typeof useI18n>["t"]): string {
  return value ? t("organizer.workspace.setupReady") : t("organizer.workspace.setupMissing");
}

export function EventMerchantSetupPanel({
  merchants,
  setup,
  onSave,
  onMarkReady
}: EventMerchantSetupPanelProps) {
  const { t } = useI18n();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [readyingMerchantId, setReadyingMerchantId] = useState<string | null>(null);

  useEffect(() => {
    setSelectedIds(setup?.participants.map((participant) => participant.merchant_id) ?? []);
  }, [setup?.participants]);

  const participantsByMerchantId = useMemo(
    () => new Map((setup?.participants ?? []).map((participant) => [participant.merchant_id, participant])),
    [setup?.participants]
  );

  const selectedMerchants = useMemo(
    () => merchants.filter((merchant) => selectedIds.includes(merchant.merchant_id)),
    [merchants, selectedIds]
  );

  const toggleMerchant = (merchantId: string) => {
    setSelectedIds((current) =>
      current.includes(merchantId)
        ? current.filter((item) => item !== merchantId)
        : [...current, merchantId]
    );
  };

  const save = async () => {
    setSaving(true);
    try {
      await onSave(selectedIds);
    } finally {
      setSaving(false);
    }
  };

  const markReady = async (merchantId: string) => {
    setReadyingMerchantId(merchantId);
    try {
      await onMarkReady(merchantId);
    } finally {
      setReadyingMerchantId(null);
    }
  };

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-ink">{t("organizer.workspace.merchantSetupTitle")}</h2>
          <p className="mt-1 text-sm text-slate-600">{t("organizer.workspace.merchantSetupDescription")}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={setup?.ready_for_planning ? "success" : "warning"}>
            {setup?.ready_for_planning
              ? t("organizer.workspace.readyForPlanning")
              : t("organizer.workspace.notReadyForPlanning")}
          </Badge>
          <span className="text-sm font-medium text-slate-700">
            {t("organizer.workspace.merchantSetupReadySummary", {
              ready: setup?.ready_count ?? 0,
              total: setup?.total_count ?? 0
            })}
          </span>
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)]">
        <div className="grid gap-2 sm:grid-cols-2">
          {merchants.map((merchant) => {
            const selected = selectedIds.includes(merchant.merchant_id);
            const eligibility = setup?.eligibility?.[merchant.merchant_id];
            return (
              <label
                key={merchant.merchant_id}
                className={`flex min-h-[72px] cursor-pointer items-start gap-3 rounded-md border p-3 text-sm transition-colors ${
                  selected ? "border-teal-300 bg-teal-50" : "border-slate-200 bg-white hover:bg-slate-50"
                }`}
              >
                <input
                  type="checkbox"
                  aria-label={merchant.name}
                  className="mt-1 h-4 w-4 rounded border-slate-300 text-harbor"
                  checked={selected}
                  onChange={() => toggleMerchant(merchant.merchant_id)}
                />
                <span className="min-w-0">
                  <span className="block font-medium text-ink">{merchant.name}</span>
                  <span className="mt-1 block text-xs text-slate-500">
                    {merchant.type} / {localizedStatus(merchant.capacity_level, t)}
                  </span>
                  <span className="mt-1 block text-xs text-slate-500">
                    {merchant.area || merchant.location?.label || "-"} / {operatingWindowSummary(merchant)}
                  </span>
                  {eligibility ? (
                    <span className="mt-2 block">
                      <Badge variant={eligibility.status === "ineligible" ? "danger" : eligibility.status === "eligible" ? "success" : "warning"}>
                        {eligibilityLabel(eligibility.status, t)}
                      </Badge>
                    </span>
                  ) : null}
                </span>
              </label>
            );
          })}
          {!merchants.length ? (
            <p className="rounded-md border border-dashed border-slate-200 p-3 text-sm text-slate-500">
              {t("organizer.workspace.noMerchantsAvailable")}
            </p>
          ) : null}
        </div>

        <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold text-ink">{t("organizer.workspace.selectedMerchants")}</h3>
            <Button size="sm" onClick={() => void save()} disabled={saving}>
              {t("organizer.workspace.saveMerchantSetup")}
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {selectedMerchants.map((merchant) => {
              const participant = participantsByMerchantId.get(merchant.merchant_id);
              const isReady = participant?.readiness_status === "ready";
              const eligibility = setup?.eligibility?.[merchant.merchant_id];
              const isIneligible = eligibility?.status === "ineligible";
              const setupGaps = participant?.setup_gaps ?? [];
              const hasSetupGaps = setupGaps.length > 0;
              return (
                <div key={merchant.merchant_id} className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-medium text-ink">{merchant.name}</span>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant={isReady ? "success" : "warning"}>
                        {localizedStatus(participant?.readiness_status ?? "needs_setup", t)}
                      </Badge>
                      {eligibility ? (
                        <Badge variant={isIneligible ? "danger" : eligibility.status === "eligible" ? "success" : "warning"}>
                          {eligibilityLabel(eligibility.status, t)}
                        </Badge>
                      ) : null}
                      <Badge variant={participant?.setup_status === "submitted" || participant?.setup_status === "approved" ? "success" : "warning"}>
                        {localizedStatus(participant?.setup_status ?? "not_started", t)}
                      </Badge>
                    </div>
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    {merchant.area || merchant.location?.label || "-"} / {operatingWindowSummary(merchant)}
                  </p>
                  {merchant.participation_constraints?.length ? (
                    <p className="mt-1 text-xs text-slate-500">
                      {merchant.participation_constraints.join(", ")}
                    </p>
                  ) : null}
                  {eligibility?.reasons.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-slate-600">
                      {eligibility.reasons.map((reason) => (
                        <li key={reason}>{reason}</li>
                      ))}
                    </ul>
                  ) : null}
                  {participant ? (
                    <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-2 text-xs text-slate-600">
                      <div className="grid gap-2 sm:grid-cols-2">
                        <span>{t("organizer.workspace.setupContact", { name: participant.merchant_contact_name || "-", phone: participant.merchant_contact_phone || "-" })}</span>
                        <span>{t("organizer.workspace.setupCapacity", { value: participant.capacity_commitment || "-" })}</span>
                        <span>{t("organizer.workspace.setupStaffing", { value: readinessLabel(participant.staffing_ready, t) })}</span>
                        <span>{t("organizer.workspace.setupStock", { value: readinessLabel(participant.stock_ready, t) })}</span>
                        <span>{t("organizer.workspace.setupIndoor", { value: readinessLabel(participant.indoor_backup_ready, t) })}</span>
                        <span>{t("organizer.workspace.setupWindow", { value: readinessLabel(participant.operating_window_confirmed, t) })}</span>
                      </div>
                      {participant.merchant_notes ? (
                        <p className="mt-2 text-slate-700">{participant.merchant_notes}</p>
                      ) : null}
                      {setupGaps.length ? (
                        <ul className="mt-2 space-y-1 text-amber-800">
                          {setupGaps.map((gap) => (
                            <li key={gap}>{gap}</li>
                          ))}
                        </ul>
                      ) : null}
                    </div>
                  ) : null}
                  {!isReady && participant && !isIneligible ? (
                    <Button
                      className="mt-3"
                      size="sm"
                      variant="secondary"
                      disabled={readyingMerchantId === merchant.merchant_id || hasSetupGaps}
                      onClick={() => void markReady(merchant.merchant_id)}
                    >
                      {t("organizer.workspace.markMerchantReady")}
                    </Button>
                  ) : null}
                </div>
              );
            })}
            {!selectedMerchants.length ? (
              <p className="text-sm text-slate-500">{t("organizer.workspace.noSelectedMerchants")}</p>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  );
}
