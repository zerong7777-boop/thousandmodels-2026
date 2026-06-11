import { AlertTriangle, BarChart3, CalendarDays, Gauge, Route } from "lucide-react";
import type { ReactNode } from "react";
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
  return (
    <ProductShell
      user={user}
      label="Operations workspace"
      subtitle="Plan approvals, event signals, merchant coordination, and review."
      pathname={pathname}
      onNavigate={onNavigate}
      onLogout={onLogout}
      testId="organizer-shell"
      nav={[
        { label: "Dashboard", href: "/organizer/dashboard", icon: <Gauge size={16} /> },
        { label: "Events", href: "/organizer/events", icon: <CalendarDays size={16} /> },
        { label: "Workspace", href: "/organizer/events/demo-night-tour", icon: <Route size={16} /> },
        {
          label: "Exceptions",
          href: "/organizer/events/demo-night-tour/exceptions",
          icon: <AlertTriangle size={16} />,
          badge: "live"
        },
        { label: "Review", href: "/organizer/events/demo-night-tour/review", icon: <BarChart3 size={16} /> }
      ]}
    >
      {children}
    </ProductShell>
  );
}
