import { cn } from "../../ui/utils";

export function NoticeFeed({
  title = "Live update",
  notices,
  className
}: {
  title?: string;
  notices: string[];
  className?: string;
}) {
  return (
    <section className={cn("rounded-lg border border-blue-100 bg-blue-50 p-4 shadow-sm", className)}>
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <div className="mt-3 space-y-2">
        {notices.length ? (
          notices.map((notice) => (
            <p key={notice} className="rounded-md border border-white bg-white/80 p-3 text-sm leading-5 text-slate-700">
              {notice}
            </p>
          ))
        ) : (
          <p className="text-sm leading-5 text-slate-600">No updates right now.</p>
        )}
      </div>
    </section>
  );
}
