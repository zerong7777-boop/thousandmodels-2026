import { api } from "../../api";
import { NoticeFeed, ProductPageHeader } from "../../components/product";
import { localizedDemoList, useI18n } from "../../i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { asArray, useAsyncData } from "../productUtils";

export function MerchantNotificationsPage({ eventId = "demo-night-tour" }: { eventId?: string }) {
  const { t } = useI18n();
  const { data: publicEvent } = useAsyncData(() => api.getPublicEvent(eventId), null);
  const notices = localizedDemoList(asArray(publicEvent?.public_notices).map((notice) => notice.message), t);

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow={t("merchant.notices.eyebrow")}
        title={t("merchant.notices.title")}
        description={t("merchant.notices.description")}
        meta={[
          t("merchant.notices.recoveryNotice"),
          t("merchant.notices.staffAlignment"),
          t("merchant.notices.visitorSafeWording")
        ]}
        status="current"
        tone="merchant"
      />

      <NoticeFeed
        title={t("merchant.notices.recoveryNotice")}
        notices={notices.length ? notices : [t("merchant.notices.emptyFeed")]}
      />

      <Card>
        <CardHeader>
          <CardTitle>{t("merchant.notices.currentNotices")}</CardTitle>
          <CardDescription>{t("merchant.notices.currentNoticesDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-slate-700">
            {(notices.length ? notices : [t("merchant.notices.emptyNotice")]).map((notice) => (
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
