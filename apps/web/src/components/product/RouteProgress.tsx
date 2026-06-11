import { cn } from "../../ui/utils";
import { useI18n } from "../../i18n";

export function RouteProgress({
  current = 1,
  total,
  label,
  className
}: {
  current?: number;
  total: number;
  label?: string;
  className?: string;
}) {
  const { t } = useI18n();
  const safeTotal = Math.max(total, 1);
  const safeCurrent = Math.min(Math.max(current, 1), safeTotal);

  return (
    <section className={cn("rounded-lg border border-violet-200 bg-white p-4 shadow-sm", className)}>
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-semibold text-ink">{label ?? t("routeProgress.title")}</h2>
        <span className="text-sm font-medium text-violet-800">
          {safeCurrent}/{safeTotal}
        </span>
      </div>
      <div className="mt-4 grid gap-2" style={{ gridTemplateColumns: `repeat(${safeTotal}, minmax(0, 1fr))` }}>
        {Array.from({ length: safeTotal }).map((_, index) => (
          <span
            aria-hidden="true"
            className={cn("h-2 rounded-full", index < safeCurrent ? "bg-violet-600" : "bg-violet-100")}
            key={index}
          />
        ))}
      </div>
    </section>
  );
}
