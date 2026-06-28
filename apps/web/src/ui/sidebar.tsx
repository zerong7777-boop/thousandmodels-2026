import type { MouseEvent, ReactNode } from "react";
import { cn } from "./utils";

export interface SidebarItem {
  label: string;
  href: string;
  icon?: ReactNode;
  badge?: string;
}

function navItemMatches(pathname: string, href: string): boolean {
  return pathname === href || (href !== "/" && pathname.startsWith(`${href}/`));
}

function activeHref(items: SidebarItem[], pathname: string): string | undefined {
  return [...items]
    .sort((left, right) => right.href.length - left.href.length)
    .find((item) => navItemMatches(pathname, item.href))?.href;
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
  const currentHref = activeHref(items, pathname);

  return (
    <nav className="space-y-1">
      {items.map((item) => {
        const active = item.href === currentHref;
        return (
          <a
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            onClick={(event: MouseEvent<HTMLAnchorElement>) => {
              event.preventDefault();
              onNavigate(item.href);
            }}
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
          </a>
        );
      })}
    </nav>
  );
}
