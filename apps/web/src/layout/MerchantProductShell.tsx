import { Bell, ClipboardList, Store, ToggleLeft } from "lucide-react";
import type { ReactNode } from "react";
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
  return (
    <ProductShell
      user={user}
      label="Merchant workbench"
      subtitle="Today's tasks, live status, and organizer notices."
      pathname={pathname}
      onNavigate={onNavigate}
      onLogout={onLogout}
      compact
      accent="amber"
      testId="merchant-shell"
      nav={[
        { label: "Tasks", href: "/merchant/events/demo-night-tour/tasks", icon: <ClipboardList size={16} /> },
        { label: "Status", href: "/merchant/events/demo-night-tour/status", icon: <ToggleLeft size={16} /> },
        { label: "Notices", href: "/merchant/notifications", icon: <Bell size={16} /> },
        { label: "Today", href: "/merchant/dashboard", icon: <Store size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
