import { cn } from "../../ui/utils";

export function RecoveryDiff({
  before,
  after,
  className
}: {
  before: string[];
  after: string[];
  className?: string;
}) {
  return (
    <section className={cn("grid gap-3 md:grid-cols-2", className)}>
      <div className="rounded-lg border border-red-100 bg-red-50 p-4">
        <h3 className="text-sm font-semibold text-red-800">Before</h3>
        <ul className="mt-3 space-y-2 text-sm leading-5 text-red-900">
          {before.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
      <div className="rounded-lg border border-emerald-100 bg-emerald-50 p-4">
        <h3 className="text-sm font-semibold text-emerald-800">After</h3>
        <ul className="mt-3 space-y-2 text-sm leading-5 text-emerald-900">
          {after.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
