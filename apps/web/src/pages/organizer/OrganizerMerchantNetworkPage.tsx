import { useEffect, useMemo, useState } from "react";
import { api } from "../../api";
import { localizedStatus, useI18n } from "../../i18n";
import type { MerchantCreateRequest, MerchantDetail, MerchantProfile, MerchantUpdateRequest } from "../../types";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";

function operatingWindowSummary(merchant: MerchantProfile): string {
  const windows = merchant.operating_windows ?? [];
  if (windows.length) {
    return windows.map((window) => `${window.start_time}-${window.end_time}`).join(", ");
  }
  return merchant.opening_hours ?? "";
}

function listText(values: string[] | undefined): string {
  return values?.length ? values.join(", ") : "-";
}

function createPayload(merchantId: string, name: string): MerchantCreateRequest {
  return {
    merchant_id: merchantId.trim(),
    name: name.trim(),
    type: "local merchant",
    location: { lat: 22.192, lng: 113.538, label: "Inner Harbor" },
    opening_hours: "10:00-22:00",
    capacity_level: "medium",
    signature_products: [],
    story: "",
    suitable_activity_types: [],
    rainy_day_score: 3,
    night_score: 3,
    constraints: [],
    contact_name: "",
    contact_phone: "",
    address_label: "",
    area: "Inner Harbor",
    operating_windows: [{ label: "daily", start_time: "10:00", end_time: "22:00" }],
    capacity_notes: "",
    category_tags: [],
    participation_constraints: [],
    status: "active"
  };
}

export function OrganizerMerchantNetworkPage() {
  const { t } = useI18n();
  const [merchants, setMerchants] = useState<MerchantProfile[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<MerchantDetail | null>(null);
  const [loadingError, setLoadingError] = useState(false);
  const [saveError, setSaveError] = useState(false);
  const [merchantId, setMerchantId] = useState("");
  const [merchantName, setMerchantName] = useState("");
  const [editing, setEditing] = useState(false);
  const [contactOwner, setContactOwner] = useState("");
  const [area, setArea] = useState("");
  const [capacityNotes, setCapacityNotes] = useState("");

  const selectedMerchant = useMemo(
    () => merchants.find((merchant) => merchant.merchant_id === selectedId) ?? detail?.merchant ?? null,
    [detail, merchants, selectedId]
  );

  const loadMerchants = async (nextSelectedId?: string) => {
    setLoadingError(false);
    try {
      const nextMerchants = await api.getMerchants();
      setMerchants(nextMerchants);
      const resolvedId = nextSelectedId ?? selectedId ?? nextMerchants[0]?.merchant_id ?? null;
      setSelectedId(resolvedId);
      if (resolvedId) {
        const nextDetail = await api.getMerchant(resolvedId);
        setDetail(nextDetail);
        setContactOwner(nextDetail.merchant.contact_name ?? "");
        setArea(nextDetail.merchant.area ?? "");
        setCapacityNotes(nextDetail.merchant.capacity_notes ?? "");
      }
    } catch {
      setLoadingError(true);
    }
  };

  useEffect(() => {
    void loadMerchants();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectMerchant = async (merchant: MerchantProfile) => {
    setSelectedId(merchant.merchant_id);
    setEditing(false);
    setSaveError(false);
    try {
      const nextDetail = await api.getMerchant(merchant.merchant_id);
      setDetail(nextDetail);
      setContactOwner(nextDetail.merchant.contact_name ?? "");
      setArea(nextDetail.merchant.area ?? "");
      setCapacityNotes(nextDetail.merchant.capacity_notes ?? "");
    } catch {
      setLoadingError(true);
    }
  };

  const createMerchant = async () => {
    setSaveError(false);
    try {
      const created = await api.createMerchant(createPayload(merchantId, merchantName));
      setMerchantId("");
      setMerchantName("");
      await loadMerchants(created.merchant.merchant_id);
    } catch {
      setSaveError(true);
    }
  };

  const saveMerchant = async () => {
    if (!selectedId) return;
    setSaveError(false);
    const payload: MerchantUpdateRequest = {
      contact_name: contactOwner,
      area,
      capacity_notes: capacityNotes
    };
    try {
      const updated = await api.updateMerchant(selectedId, payload);
      setDetail(updated);
      setMerchants((current) =>
        current.map((merchant) => (merchant.merchant_id === selectedId ? updated.merchant : merchant))
      );
      setEditing(false);
    } catch {
      setSaveError(true);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-harbor">{t("organizer.merchants.eyebrow")}</p>
        <h1 className="text-2xl font-semibold">{t("organizer.merchants.title")}</h1>
      </div>

      {loadingError ? (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
          {t("organizer.merchants.loadError")}
        </div>
      ) : null}
      {saveError ? (
        <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
          {t("organizer.merchants.saveError")}
        </div>
      ) : null}

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.merchants.title")}</CardTitle>
            <CardDescription>{t("organizer.merchants.listDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {merchants.map((merchant) => (
              <div
                key={merchant.merchant_id}
                className="rounded-md border border-slate-200 bg-white p-3"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-base font-semibold text-ink">{merchant.name}</h2>
                      <Badge variant={merchant.status === "active" || !merchant.status ? "success" : "warning"}>
                        {localizedStatus(merchant.status ?? "active", t)}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">
                      {merchant.area || merchant.location?.label || "-"} / {operatingWindowSummary(merchant)}
                    </p>
                    <p className="mt-1 text-sm text-slate-600">
                      {t("organizer.merchants.contactOwner")}: {merchant.contact_name || "-"}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">{listText(merchant.category_tags)}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="secondary"
                    aria-label={`Edit ${merchant.name}`}
                    onClick={() => {
                      void selectMerchant(merchant);
                      setEditing(true);
                    }}
                  >
                    {t("common.edit")}
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("organizer.merchants.createTitle")}</CardTitle>
            <CardDescription>{t("organizer.merchants.createDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <label className="block text-sm font-medium text-slate-700" htmlFor="merchant-id">
              {t("organizer.merchants.merchantId")}
            </label>
            <input
              id="merchant-id"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={merchantId}
              onChange={(event) => setMerchantId(event.target.value)}
            />
            <label className="block text-sm font-medium text-slate-700" htmlFor="merchant-name">
              {t("organizer.merchants.merchantName")}
            </label>
            <input
              id="merchant-name"
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              value={merchantName}
              onChange={(event) => setMerchantName(event.target.value)}
            />
            <Button onClick={() => void createMerchant()} disabled={!merchantId.trim() || !merchantName.trim()}>
              {t("organizer.merchants.createMerchant")}
            </Button>
          </CardContent>
        </Card>
      </section>

      {selectedMerchant ? (
        <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
          <Card>
            <CardHeader>
              <CardTitle>{t("organizer.merchants.detailTitle")}</CardTitle>
              <CardDescription>
                {selectedMerchant.name} / {selectedMerchant.type}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-3 md:grid-cols-3">
                <div className="rounded-md border border-slate-200 p-3 text-sm">
                  {t("organizer.merchants.area")}: {selectedMerchant.area || "-"}
                </div>
                <div className="rounded-md border border-slate-200 p-3 text-sm">
                  {t("organizer.merchants.openingHours")}: {operatingWindowSummary(selectedMerchant)}
                </div>
                <div className="rounded-md border border-slate-200 p-3 text-sm">
                  {t("organizer.merchants.capacity")}: {localizedStatus(selectedMerchant.capacity_level, t)}
                </div>
              </div>
              <div className="rounded-md border border-slate-200 p-3 text-sm">
                {t("organizer.merchants.constraints")}: {listText(selectedMerchant.participation_constraints)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("organizer.merchants.detailTitle")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {!editing ? (
                <Button variant="secondary" onClick={() => setEditing(true)}>
                  {t("common.edit")}
                </Button>
              ) : null}
              <label className="block text-sm font-medium text-slate-700" htmlFor="contact-owner">
                {t("organizer.merchants.contactOwner")}
              </label>
              <input
                id="contact-owner"
                className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={contactOwner}
                onChange={(event) => setContactOwner(event.target.value)}
              />
              <label className="block text-sm font-medium text-slate-700" htmlFor="merchant-area">
                {t("organizer.merchants.area")}
              </label>
              <input
                id="merchant-area"
                className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={area}
                onChange={(event) => setArea(event.target.value)}
              />
              <label className="block text-sm font-medium text-slate-700" htmlFor="capacity-notes">
                {t("organizer.merchants.capacityNotes")}
              </label>
              <textarea
                id="capacity-notes"
                className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                value={capacityNotes}
                onChange={(event) => setCapacityNotes(event.target.value)}
              />
              <Button onClick={() => void saveMerchant()}>{t("organizer.merchants.saveMerchant")}</Button>
            </CardContent>
          </Card>
        </section>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>{t("organizer.merchants.historyTitle")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(detail?.participation_history ?? []).map((item) => (
            <div key={`${item.event_id}:${item.event_date}`} className="rounded-md border border-slate-200 p-3 text-sm">
              <div className="font-medium text-ink">{item.event_title}</div>
              <div className="mt-1 text-slate-600">
                {item.event_date} / {localizedStatus(item.participation_status, t)} /{" "}
                {localizedStatus(item.readiness_status, t)}
              </div>
              <div className="mt-1 text-xs text-slate-500">
                v{item.latest_plan_version} / {item.has_interaction_package ? "package ready" : "no package"}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
