import { cn } from "../../ui/utils";
import { useI18n } from "../../i18n";

export function NoticeFeed({
  title,
  notices,
  className
}: {
  title?: string;
  notices: string[];
  className?: string;
}) {
  const { t } = useI18n();

  return (
    <section className={cn("rounded-lg border border-blue-100 bg-blue-50 p-4 shadow-sm", className)}>
      <h2 className="text-base font-semibold text-ink">{title ?? t("noticeFeed.defaultTitle")}</h2>
      <div className="mt-3 space-y-2">
        {notices.length ? (
          notices.map((notice) => (
            <p key={notice} className="rounded-md border border-white bg-white/80 p-3 text-sm leading-5 text-slate-700">
              {notice}
            </p>
          ))
        ) : (
          <p className="text-sm leading-5 text-slate-600">{t("noticeFeed.empty")}</p>
        )}
      </div>
    </section>
  );
}
