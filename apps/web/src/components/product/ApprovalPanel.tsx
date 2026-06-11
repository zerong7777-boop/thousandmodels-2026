import type { ReactNode } from "react";
import { Button } from "../../ui/button";

export function ApprovalPanel({
  title,
  description,
  consequence,
  actionLabel,
  onApprove,
  disabled,
  children
}: {
  title: string;
  description?: string;
  consequence?: string;
  actionLabel: string;
  onApprove?: () => void;
  disabled?: boolean;
  children?: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-teal-200 bg-teal-50 p-5 shadow-sm">
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      {description ? <p className="mt-2 text-sm leading-5 text-slate-700">{description}</p> : null}
      {children ? <div className="mt-4">{children}</div> : null}
      {consequence ? (
        <p className="mt-4 rounded-md border border-white bg-white/80 p-3 text-sm leading-5 text-slate-700">
          {consequence}
        </p>
      ) : null}
      <Button className="mt-4 w-full sm:w-auto" disabled={disabled} onClick={onApprove}>
        {actionLabel}
      </Button>
    </section>
  );
}
