import { api } from "../../api";
import { NoticeFeed, ProductPageHeader } from "../../components/product";
import { localizedDemoList, useI18n } from "../../i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function TouristNoticesPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: event } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const notices = localizedDemoList(asArray(event?.public_notices).map((notice) => notice.message), t);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("tourist.notices.eyebrow")}
        title={t("tourist.notices.title")}
        description={t("tourist.notices.description")}
        meta={[t("tourist.event.liveUpdate"), t("tourist.notices.visitorSafe")]}
        status="current"
        tone="visitor"
      />
      <NoticeFeed title={t("tourist.event.liveUpdate")} notices={notices.length ? notices : [t("tourist.notices.empty")]} />
      <Card>
        <CardHeader>
          <CardTitle>{t("tourist.notices.latest")}</CardTitle>
          <CardDescription>{t("tourist.notices.latestDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-slate-700">
            {(notices.length ? notices : [t("tourist.notices.empty")]).map((notice) => (
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
