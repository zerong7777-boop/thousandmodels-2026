import { Bell, ClipboardCheck, ClipboardList, Store, ToggleLeft } from "lucide-react";
import type { ReactNode } from "react";
import { useI18n } from "../i18n";
import type { AuthUser } from "../types";
import { ProductShell } from "./ProductShell";

export function MerchantProductShell({
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
      label={t("shell.merchantLabel")}
      subtitle={t("shell.merchantSubtitle")}
      pathname={pathname}
      onNavigate={onNavigate}
      onLogout={onLogout}
      compact
      accent="amber"
      testId="merchant-shell"
      nav={[
        { label: t("shell.nav.setup"), href: "/merchant/events/demo-night-tour/setup", icon: <ClipboardCheck size={16} /> },
        { label: t("shell.nav.tasks"), href: "/merchant/events/demo-night-tour/tasks", icon: <ClipboardList size={16} /> },
        { label: t("shell.nav.status"), href: "/merchant/events/demo-night-tour/status", icon: <ToggleLeft size={16} /> },
        { label: t("shell.nav.notices"), href: "/merchant/notifications", icon: <Bell size={16} /> },
        { label: t("shell.nav.today"), href: "/merchant/dashboard", icon: <Store size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
