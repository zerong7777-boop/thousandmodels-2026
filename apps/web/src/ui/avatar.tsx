import { cn } from "./utils";

export function Avatar({ name, className }: { name: string; className?: string }) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <div
      className={cn(
        "flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white",
        className
      )}
      aria-hidden="true"
    >
      {initials || "ZH"}
    </div>
  );
}
