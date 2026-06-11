import type { ReactNode } from "react";
import { cn } from "../../ui/utils";

export function EmptyState({
  title,
  description,
  action,
  className
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center", className)}>
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      {description ? <p className="mx-auto mt-2 max-w-md text-sm leading-5 text-slate-600">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
