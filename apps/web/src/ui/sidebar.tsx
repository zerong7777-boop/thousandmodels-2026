import type { ReactNode } from "react";
import { cn } from "./utils";

export interface SidebarItem {
  label: string;
  href: string;
  icon?: ReactNode;
  badge?: string;
}

export function Sidebar({
  items,
  pathname,
  onNavigate
}: {
  items: SidebarItem[];
  pathname: string;
  onNavigate: (path: string) => void;
}) {
  return (
    <nav className="space-y-1">
      {items.map((item) => {
        const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
        return (
          <button
            key={item.href}
            type="button"
            onClick={() => onNavigate(item.href)}
            className={cn(
              "flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm",
              active ? "bg-teal-50 text-harbor" : "text-slate-700 hover:bg-slate-50"
            )}
          >
            <span className="flex items-center gap-2">
              {item.icon}
              {item.label}
            </span>
            {item.badge ? (
              <span className="rounded-sm bg-amber-100 px-2 py-0.5 text-xs text-amber-800">{item.badge}</span>
            ) : null}
          </button>
        );
      })}
    </nav>
  );
}
