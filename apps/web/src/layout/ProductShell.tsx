import { Bell, LogOut } from "lucide-react";
import type { ReactNode } from "react";
import { LanguageSwitcher, useI18n } from "../i18n";
import type { AuthUser } from "../types";
import { Avatar } from "../ui/avatar";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Separator } from "../ui/separator";
import { Sidebar, type SidebarItem } from "../ui/sidebar";
import { cn } from "../ui/utils";

interface ProductShellProps {
  user: AuthUser;
  label: string;
  subtitle: string;
  pathname: string;
  nav: SidebarItem[];
  onNavigate: (path: string) => void;
  onLogout: () => void;
  children: ReactNode;
  compact?: boolean;
  testId: string;
  accent?: "harbor" | "lotus" | "amber";
}

export function ProductShell({
  user,
  label,
  subtitle,
  pathname,
  nav,
  onNavigate,
  onLogout,
  children,
  compact = false,
  testId,
  accent = "harbor"
}: ProductShellProps) {
  const { t } = useI18n();
  const accentClass =
    accent === "lotus" ? "text-lotus" : accent === "amber" ? "text-amberline" : "text-harbor";
  const activeNav = nav.find((item) => pathname === item.href || pathname.startsWith(item.href));

  return (
    <div className={cn("min-h-screen bg-mist text-ink", compact ? "pb-20" : "")} data-testid={testId}>
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
          <div className="min-w-0">
            <div className={cn("text-xs font-semibold uppercase", accentClass)}>{label}</div>
            <div className="truncate text-lg font-semibold">Zhiyin Haojiang</div>
            <div className="truncate text-sm text-slate-500">{subtitle}</div>
          </div>
          <div className="flex flex-wrap items-center justify-end gap-2 sm:gap-3">
            <LanguageSwitcher compact={compact} />
            <Button variant="ghost" size="sm" aria-label={t("common.notifications")}>
              <Bell size={16} />
            </Button>
            <div className="hidden items-center gap-2 sm:flex">
              <Avatar name={user.display_name} />
              <div className="text-right">
                <div className="text-sm font-medium">{user.display_name}</div>
                <div className="text-xs text-slate-500">{user.username}</div>
              </div>
            </div>
            <Button variant="secondary" size="sm" onClick={onLogout}>
              <LogOut size={14} className="mr-2" />
              {t("common.logout")}
            </Button>
          </div>
        </div>
      </header>

      <div
        className={cn(
          "mx-auto grid max-w-7xl gap-4 px-4 py-4",
          compact ? "grid-cols-1" : "lg:grid-cols-[240px_minmax(0,1fr)]"
        )}
      >
        {!compact ? (
          <Card className="h-fit p-2">
            <Sidebar items={nav} pathname={pathname} onNavigate={onNavigate} />
            <Separator className="my-3" />
            <div className="px-2 pb-2 text-xs text-slate-500">
              {t("common.currentArea")}
              <div className="mt-1">
                <Badge variant={accent === "lotus" ? "lotus" : accent === "amber" ? "warning" : "success"}>
                  {activeNav?.label ?? t("shell.nav.workspace")}
                </Badge>
              </div>
            </div>
          </Card>
        ) : null}
        <main className="min-w-0">{children}</main>
      </div>

      {compact ? (
        <nav className="fixed inset-x-0 bottom-0 z-20 grid grid-cols-3 border-t border-slate-200 bg-white">
          {nav.slice(0, 3).map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href);
            return (
              <button
                key={item.href}
                type="button"
                onClick={() => onNavigate(item.href)}
                className={cn("px-2 py-3 text-sm", active ? accentClass : "text-slate-600")}
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      ) : null}
    </div>
  );
}
