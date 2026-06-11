import { Bell, MapPinned, Route } from "lucide-react";
import type { ReactNode } from "react";
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
  return (
    <ProductShell
      user={user}
      label="Route guide"
      subtitle="Stories, tasks, and live visitor notices."
      pathname={pathname}
      onNavigate={onNavigate}
      onLogout={onLogout}
      compact
      accent="lotus"
      testId="user-shell"
      nav={[
        { label: "Event", href: "/user/events/demo-night-tour", icon: <MapPinned size={16} /> },
        { label: "Route", href: "/user/events/demo-night-tour/route", icon: <Route size={16} /> },
        { label: "Notices", href: "/user/events/demo-night-tour/notices", icon: <Bell size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
