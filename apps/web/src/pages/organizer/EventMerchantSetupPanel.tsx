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
              return (
                <div key={merchant.merchant_id} className="rounded-md border border-slate-200 bg-white p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-medium text-ink">{merchant.name}</span>
                    <Badge variant={isReady ? "success" : "warning"}>
                      {localizedStatus(participant?.readiness_status ?? "needs_setup", t)}
                    </Badge>
                  </div>
                  {!isReady && participant ? (
                    <Button
                      className="mt-3"
                      size="sm"
                      variant="secondary"
                      disabled={readyingMerchantId === merchant.merchant_id}
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
