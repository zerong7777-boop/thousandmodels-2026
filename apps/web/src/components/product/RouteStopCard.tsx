import { StatusPill } from "./StatusPill";
import { localizedStatus, useI18n } from "../../i18n";

export function RouteStopCard({
  index,
  name,
  story,
  task,
  status
}: {
  index: number;
  name: string;
  story?: string;
  task?: string;
  status?: string;
}) {
  const { t } = useI18n();

  return (
    <article className="rounded-lg border border-violet-100 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-violet-800">{t("routeStop.stop", { index })}</p>
          <h3 className="mt-1 text-lg font-semibold text-ink">{name}</h3>
        </div>
        {status ? <StatusPill tone="visitor">{localizedStatus(status, t)}</StatusPill> : null}
      </div>
      {story ? <p className="mt-3 text-sm leading-6 text-slate-600">{story}</p> : null}
      {task ? (
        <div className="mt-4 rounded-md border border-violet-100 bg-violet-50 p-3 text-sm leading-5 text-violet-900">
          <span className="font-semibold">{t("routeStop.visitorTask")}</span>
          <p className="mt-1">{task}</p>
        </div>
      ) : null}
    </article>
  );
}
