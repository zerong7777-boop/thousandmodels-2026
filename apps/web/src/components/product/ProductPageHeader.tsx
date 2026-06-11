import type { ReactNode } from "react";
import { StatusPill } from "./StatusPill";
import { localizedStatus, useI18n } from "../../i18n";
import { cn } from "../../ui/utils";

export function ProductPageHeader({
  eyebrow,
  title,
  description,
  meta = [],
  status,
  actions,
  tone = "organizer",
  className
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  meta?: Array<string | undefined | null | false>;
  status?: string;
  actions?: ReactNode;
  tone?: "organizer" | "merchant" | "visitor" | "info";
  className?: string;
}) {
  const { t } = useI18n();

  return (
    <section
      className={cn(
        "rounded-lg border border-slate-200 bg-white p-5 shadow-sm",
        tone === "merchant" && "border-amber-200 bg-gradient-to-br from-white to-amber-50",
        tone === "visitor" && "border-violet-200 bg-gradient-to-br from-white to-violet-50",
        tone === "organizer" && "border-teal-200 bg-gradient-to-br from-white to-teal-50",
        className
      )}
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            {eyebrow ? <p className="text-xs font-semibold uppercase tracking-normal text-slate-500">{eyebrow}</p> : null}
            {status ? (
              <StatusPill tone={tone === "info" ? "info" : tone}>{localizedStatus(status, t)}</StatusPill>
            ) : null}
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-ink md:text-3xl">{title}</h1>
            {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p> : null}
          </div>
          {meta.length ? (
            <dl className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2 lg:grid-cols-4">
              {meta.filter(Boolean).map((item) => (
                <div key={String(item)} className="rounded-md border border-white/70 bg-white/75 px-3 py-2">
                  {item}
                </div>
              ))}
            </dl>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 flex-wrap gap-2">{actions}</div> : null}
      </div>
    </section>
  );
}
