import { cn } from "../../ui/utils";
import { useI18n } from "../../i18n";
import { StatusPill } from "./StatusPill";

type WorkflowStep = {
  label: string;
  detail?: string;
  state?: "done" | "current" | "pending";
};

export function WorkflowStepper({ steps, className }: { steps: WorkflowStep[]; className?: string }) {
  const { t } = useI18n();
  const stateLabel = (state: WorkflowStep["state"]) => {
    if (state === "done") return t("common.status.completed");
    if (state === "current") return t("common.status.current");
    return t("common.status.pending");
  };

  return (
    <div className={cn("grid gap-3 md:grid-cols-3", className)}>
      {steps.map((step, index) => (
        <div key={step.label} className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between gap-3">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
              {index + 1}
            </span>
            <StatusPill tone={step.state === "done" ? "success" : step.state === "current" ? "info" : "neutral"}>
              {stateLabel(step.state)}
            </StatusPill>
          </div>
          <p className="mt-3 font-semibold text-ink">{step.label}</p>
          {step.detail ? <p className="mt-1 text-sm leading-5 text-slate-600">{step.detail}</p> : null}
        </div>
      ))}
    </div>
  );
}
