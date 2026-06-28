import { AlertTriangle, BarChart3, CalendarDays, Gauge, Route, Store } from "lucide-react";
import type { ReactNode } from "react";
import { useI18n } from "../i18n";
import type { AuthUser } from "../types";
import { ProductShell } from "./ProductShell";

function eventIdFromPath(pathname: string): string {
  const parts = pathname.split("/").filter(Boolean);
  if (parts[0] === "organizer" && parts[1] === "events" && parts[2]) {
    return parts[2];
  }
  if (parts[0] === "review" && parts[1]) {
    return parts[1];
  }
  return "demo-night-tour";
}

export function OrganizerProductShell({
  user,
  pathname,
  onNavigate,
  onLogout,
  children
}: {
  user: AuthUser;
  pathname: string;
  onNavigate: (path: string) => void;
  onLogout: () => void;
  children: ReactNode;
}) {
  const { t } = useI18n();
  const selectedEventId = eventIdFromPath(pathname);

  return (
    <ProductShell
      user={user}
      label={t("shell.organizerLabel")}
      subtitle={t("shell.organizerSubtitle")}
      pathname={pathname}
      onNavigate={onNavigate}
      onLogout={onLogout}
      testId="organizer-shell"
      nav={[
        { label: t("shell.nav.dashboard"), href: "/organizer/dashboard", icon: <Gauge size={16} /> },
        { label: t("shell.nav.events"), href: "/organizer/events", icon: <CalendarDays size={16} /> },
        { label: t("shell.nav.merchants"), href: "/organizer/merchants", icon: <Store size={16} /> },
        { label: t("shell.nav.workspace"), href: `/organizer/events/${selectedEventId}`, icon: <Route size={16} /> },
        {
          label: t("shell.nav.exceptions"),
          href: `/organizer/events/${selectedEventId}/exceptions`,
          icon: <AlertTriangle size={16} />,
          badge: "live"
        },
        { label: t("shell.nav.review"), href: `/organizer/events/${selectedEventId}/review`, icon: <BarChart3 size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
