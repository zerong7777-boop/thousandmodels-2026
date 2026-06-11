import { Bell, MapPinned, Route } from "lucide-react";
import type { ReactNode } from "react";
import { useI18n } from "../i18n";
import type { AuthUser } from "../types";
import { ProductShell } from "./ProductShell";

export function TouristProductShell({
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
      label={t("shell.touristLabel")}
      subtitle={t("shell.touristSubtitle")}
      pathname={pathname}
      onNavigate={onNavigate}
      onLogout={onLogout}
      compact
      accent="lotus"
      testId="user-shell"
      nav={[
        { label: t("shell.nav.event"), href: "/user/events/demo-night-tour", icon: <MapPinned size={16} /> },
        { label: t("shell.nav.route"), href: "/user/events/demo-night-tour/route", icon: <Route size={16} /> },
        { label: t("shell.nav.notices"), href: "/user/events/demo-night-tour/notices", icon: <Bell size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
