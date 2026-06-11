import type { ReactNode } from "react";
import { cn } from "../../ui/utils";
import { StatusPill } from "./StatusPill";

type QueueItem = {
  title: string;
  detail?: string;
  tone?: "neutral" | "success" | "warning" | "danger" | "info" | "organizer" | "merchant" | "visitor";
  badge?: string;
  action?: ReactNode;
};

export function AttentionQueue({
  title = "Needs attention",
  items,
  className
}: {
  title?: string;
  items: QueueItem[];
  className?: string;
}) {
  return (
    <section className={cn("rounded-lg border border-slate-200 bg-white shadow-sm", className)}>
      <div className="border-b border-slate-100 px-5 py-4">
        <h2 className="text-base font-semibold text-ink">{title}</h2>
      </div>
      <div className="divide-y divide-slate-100">
        {items.map((item) => (
          <div key={item.title} className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0 space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-medium text-ink">{item.title}</p>
                {item.badge ? <StatusPill tone={item.tone ?? "neutral"}>{item.badge}</StatusPill> : null}
              </div>
              {item.detail ? <p className="text-sm leading-5 text-slate-600">{item.detail}</p> : null}
            </div>
            {item.action ? <div className="shrink-0">{item.action}</div> : null}
          </div>
        ))}
      </div>
    </section>
  );
}
