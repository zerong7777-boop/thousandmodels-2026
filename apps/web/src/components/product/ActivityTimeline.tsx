import { cn } from "../../ui/utils";

type TimelineItem = {
  time?: string;
  title: string;
  detail?: string;
  tone?: "neutral" | "success" | "warning" | "danger" | "info";
};

const dotClasses: Record<NonNullable<TimelineItem["tone"]>, string> = {
  neutral: "bg-slate-400",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-red-500",
  info: "bg-blue-500"
};

export function ActivityTimeline({
  title = "Activity timeline",
  items,
  className
}: {
  title?: string;
  items: TimelineItem[];
  className?: string;
}) {
  return (
    <section className={cn("rounded-lg border border-slate-200 bg-white p-5 shadow-sm", className)}>
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <ol className="mt-4 space-y-4">
        {items.map((item, index) => (
          <li key={`${item.title}-${index}`} className="grid grid-cols-[16px_minmax(0,1fr)] gap-3">
            <div className="relative flex justify-center">
              <span className={cn("mt-1 h-2.5 w-2.5 rounded-full", dotClasses[item.tone ?? "neutral"])} />
              {index < items.length - 1 ? <span className="absolute top-4 h-full w-px bg-slate-200" /> : null}
            </div>
            <div>
              <div className="flex flex-wrap items-baseline gap-2">
                <p className="font-medium text-ink">{item.title}</p>
                {item.time ? <span className="text-xs text-slate-500">{item.time}</span> : null}
              </div>
              {item.detail ? <p className="mt-1 text-sm leading-5 text-slate-600">{item.detail}</p> : null}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
