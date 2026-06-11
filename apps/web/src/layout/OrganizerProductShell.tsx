import { AlertTriangle, BarChart3, CalendarDays, Gauge, Route } from "lucide-react";
import type { ReactNode } from "react";
import { useI18n } from "../i18n";
import type { AuthUser } from "../types";
import { ProductShell } from "./ProductShell";

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
        { label: t("shell.nav.workspace"), href: "/organizer/events/demo-night-tour", icon: <Route size={16} /> },
        {
          label: t("shell.nav.exceptions"),
          href: "/organizer/events/demo-night-tour/exceptions",
          icon: <AlertTriangle size={16} />,
          badge: "live"
        },
        { label: t("shell.nav.review"), href: "/organizer/events/demo-night-tour/review", icon: <BarChart3 size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
