import type { ReactNode } from "react";
import { cn } from "../../ui/utils";

type ActionTone = "accept" | "pause" | "warning" | "danger" | "neutral";

const toneClasses: Record<ActionTone, string> = {
  accept: "border-emerald-200 bg-emerald-50 text-emerald-900 hover:bg-emerald-100",
  pause: "border-slate-200 bg-white text-slate-900 hover:bg-slate-50",
  warning: "border-amber-200 bg-amber-50 text-amber-900 hover:bg-amber-100",
  danger: "border-red-200 bg-red-50 text-red-900 hover:bg-red-100",
  neutral: "border-slate-200 bg-slate-50 text-slate-900 hover:bg-white"
};

export function MerchantQuickAction({
  label,
  detail,
  icon,
  tone = "neutral",
  onClick,
  disabled
}: {
  label: string;
  detail?: string;
  icon?: ReactNode;
  tone?: ActionTone;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      className={cn(
        "flex min-h-[96px] w-full items-start gap-3 rounded-lg border p-4 text-left shadow-sm transition disabled:pointer-events-none disabled:opacity-60",
        toneClasses[tone]
      )}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {icon ? <span className="mt-1 rounded-md bg-white/75 p-2">{icon}</span> : null}
      <span className="min-w-0">
        <span className="block font-semibold">{label}</span>
        {detail ? <span className="mt-1 block text-sm leading-5 opacity-80">{detail}</span> : null}
      </span>
    </button>
  );
}
