import type { ReactNode } from "react";
import { cn } from "../../ui/utils";

type StatusTone = "neutral" | "success" | "warning" | "danger" | "info" | "organizer" | "merchant" | "visitor";

const toneClasses: Record<StatusTone, string> = {
  neutral: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-red-200 bg-red-50 text-red-700",
  info: "border-blue-200 bg-blue-50 text-blue-700",
  organizer: "border-teal-200 bg-teal-50 text-teal-800",
  merchant: "border-amber-200 bg-amber-50 text-amber-800",
  visitor: "border-violet-200 bg-violet-50 text-violet-800"
};

export function StatusPill({
  children,
  tone = "neutral",
  className
}: {
  children: ReactNode;
  tone?: StatusTone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-semibold leading-none",
        toneClasses[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
