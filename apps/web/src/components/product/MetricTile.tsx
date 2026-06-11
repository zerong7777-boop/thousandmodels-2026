import type { ReactNode } from "react";
import { cn } from "../../ui/utils";

type MetricTone = "neutral" | "success" | "warning" | "danger" | "info";

const toneClasses: Record<MetricTone, string> = {
  neutral: "border-slate-200 bg-white",
  success: "border-emerald-200 bg-emerald-50",
  warning: "border-amber-200 bg-amber-50",
  danger: "border-red-200 bg-red-50",
  info: "border-blue-200 bg-blue-50"
};

export function MetricTile({
  label,
  value,
  detail,
  icon,
  tone = "neutral"
}: {
  label: string;
  value: ReactNode;
  detail?: string;
  icon?: ReactNode;
  tone?: MetricTone;
}) {
  return (
    <div className={cn("rounded-lg border p-4 shadow-sm", toneClasses[tone])}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-normal text-slate-500">{label}</p>
          <div className="mt-2 text-2xl font-semibold text-ink">{value}</div>
        </div>
        {icon ? <div className="rounded-md bg-white/70 p-2 text-slate-600">{icon}</div> : null}
      </div>
      {detail ? <p className="mt-2 text-sm leading-5 text-slate-600">{detail}</p> : null}
    </div>
  );
}
