import { useEffect, useState } from "react";
import { api } from "../../api";
import { ProductPageHeader, StatusPill } from "../../components/product";
import { localizedStatus, useI18n } from "../../i18n";
import type { MerchantAssignedEvent, MerchantSetupSubmitRequest } from "../../types";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray } from "../productUtils";

const defaultForm: MerchantSetupSubmitRequest = {
  capacity_commitment: "medium",
  staffing_ready: false,
  stock_ready: false,
  indoor_backup_ready: false,
  operating_window_confirmed: false,
  merchant_contact_name: "",
  merchant_contact_phone: "",
  merchant_notes: ""
};

type ReadinessField =
  | "staffing_ready"
  | "stock_ready"
  | "indoor_backup_ready"
  | "operating_window_confirmed";

function setupTone(status: string | undefined): "success" | "warning" | "danger" | "neutral" {
  if (status === "submitted" || status === "approved") return "success";
  if (status === "not_started") return "warning";
  return "neutral";
}

function boolLabel(value: boolean | undefined, yes: string, no: string) {
  return value ? yes : no;
}

export function MerchantEventSetupPage({ eventId }: { eventId: string }) {
  const { t } = useI18n();
  const [context, setContext] = useState<MerchantAssignedEvent | null>(null);
  const [form, setForm] = useState<MerchantSetupSubmitRequest>(defaultForm);
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    api
      .getMyMerchantEventSetup(eventId)
      .then((nextContext) => {
        if (!active) return;
        setContext(nextContext);
        setForm({
          capacity_commitment: nextContext.participant.capacity_commitment ?? "medium",
          staffing_ready: Boolean(nextContext.participant.staffing_ready),
          stock_ready: Boolean(nextContext.participant.stock_ready),
          indoor_backup_ready: Boolean(nextContext.participant.indoor_backup_ready),
          operating_window_confirmed: Boolean(nextContext.participant.operating_window_confirmed),
          merchant_contact_name: nextContext.participant.merchant_contact_name ?? "",
          merchant_contact_phone: nextContext.participant.merchant_contact_phone ?? "",
          merchant_notes: nextContext.participant.merchant_notes ?? ""
        });
      })
      .catch(() => {
        if (active) setStatus(t("merchant.setup.loadError"));
      });
    return () => {
      active = false;
    };
  }, [eventId, t]);

  const updateField = <K extends keyof MerchantSetupSubmitRequest>(
    field: K,
    value: MerchantSetupSubmitRequest[K]
  ) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const updateReadinessField = (field: ReadinessField, value: boolean) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submit = async () => {
    setSaving(true);
    setStatus("");
    try {
      const nextContext = await api.submitMyMerchantEventSetup(eventId, form);
      setContext(nextContext);
      setStatus(t("merchant.setup.submitSuccess"));
    } catch {
      setStatus(t("merchant.setup.submitError"));
    } finally {
      setSaving(false);
    }
  };

  const participant = context?.participant;
  const gaps = asArray(context?.setup_gaps);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("merchant.setup.eyebrow")}
        title={context?.event.title ?? t("merchant.setup.titleFallback")}
        description={t("merchant.setup.description")}
        meta={
          context
            ? [context.event.area, context.event.date, context.event.time_window]
            : [t("common.unavailable")]
        }
        status={participant?.setup_status ?? "not_started"}
        tone="merchant"
      />

      {status ? (
        <div role="status" className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          {status}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[minmax(280px,0.8fr)_minmax(0,1.2fr)]">
        <Card>
          <CardHeader>
            <CardTitle>{t("merchant.setup.contextTitle")}</CardTitle>
            <CardDescription>{t("merchant.setup.contextDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex flex-wrap gap-2">
              <Badge variant={setupTone(participant?.setup_status)}>
                {localizedStatus(participant?.setup_status ?? "not_started", t)}
              </Badge>
              <Badge variant={context?.ready_for_planning ? "success" : "warning"}>
                {context?.ready_for_planning ? t("merchant.setup.readyForPlanning") : t("merchant.setup.needsSetup")}
              </Badge>
              {context?.eligibility ? (
                <Badge
                  variant={
                    context.eligibility.status === "eligible"
                      ? "success"
                      : context.eligibility.status === "ineligible"
                        ? "danger"
                        : "warning"
                  }
                >
                  {localizedStatus(context.eligibility.status, t)}
                </Badge>
              ) : null}
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                {t("merchant.setup.roleHint")}
              </div>
              <p className="mt-1 text-slate-700">{participant?.role_hint || t("common.unavailable")}</p>
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
                {t("merchant.setup.organizerNotes")}
              </div>
              <p className="mt-1 text-slate-700">{participant?.notes || t("common.unavailable")}</p>
            </div>
            {gaps.length ? (
              <div>
                <div className="text-xs font-semibold uppercase tracking-normal text-amber-700">
                  {t("merchant.setup.gaps")}
                </div>
                <ul className="mt-2 space-y-1 text-amber-800">
                  {gaps.map((gap) => (
                    <li key={gap}>{gap}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("merchant.setup.formTitle")}</CardTitle>
            <CardDescription>{t("merchant.setup.formDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 md:grid-cols-3">
              <label className="text-sm font-medium text-slate-700">
                {t("merchant.setup.capacityCommitment")}
                <select
                  aria-label={t("merchant.setup.capacityCommitment")}
                  className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                  value={form.capacity_commitment}
                  onChange={(event) =>
                    updateField("capacity_commitment", event.target.value as MerchantSetupSubmitRequest["capacity_commitment"])
                  }
                >
                  <option value="low">{localizedStatus("low", t)}</option>
                  <option value="medium">{localizedStatus("medium", t)}</option>
                  <option value="high">{localizedStatus("high", t)}</option>
                </select>
              </label>
              <label className="text-sm font-medium text-slate-700">
                {t("merchant.setup.contactName")}
                <input
                  aria-label={t("merchant.setup.contactName")}
                  className="mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  value={form.merchant_contact_name}
                  onChange={(event) => updateField("merchant_contact_name", event.target.value)}
                />
              </label>
              <label className="text-sm font-medium text-slate-700">
                {t("merchant.setup.contactPhone")}
                <input
                  aria-label={t("merchant.setup.contactPhone")}
                  className="mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  value={form.merchant_contact_phone}
                  onChange={(event) => updateField("merchant_contact_phone", event.target.value)}
                />
              </label>
            </div>

            <div className="grid gap-2 sm:grid-cols-2">
              {([
                ["staffing_ready", t("merchant.setup.staffingReady")],
                ["stock_ready", t("merchant.setup.stockReady")],
                ["indoor_backup_ready", t("merchant.setup.indoorBackupReady")],
                ["operating_window_confirmed", t("merchant.setup.operatingWindowConfirmed")]
              ] satisfies Array<[ReadinessField, string]>).map(([field, label]) => (
                <label
                  key={field}
                  className="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm text-slate-700"
                >
                  <input
                    type="checkbox"
                    aria-label={label}
                    checked={form[field]}
                    onChange={(event) => updateReadinessField(field, event.target.checked)}
                  />
                  {label}
                </label>
              ))}
            </div>

            <label className="block text-sm font-medium text-slate-700">
              {t("merchant.setup.merchantNotes")}
              <textarea
                aria-label={t("merchant.setup.merchantNotes")}
                className="mt-1 min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={form.merchant_notes}
                onChange={(event) => updateField("merchant_notes", event.target.value)}
              />
            </label>

            <div className="grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
              <span>{t("merchant.setup.staffingState", { value: boolLabel(form.staffing_ready, "ready", "not ready") })}</span>
              <span>{t("merchant.setup.stockState", { value: boolLabel(form.stock_ready, "ready", "not ready") })}</span>
            </div>

            <Button onClick={() => void submit()} disabled={saving}>
              {t("merchant.setup.submit")}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
