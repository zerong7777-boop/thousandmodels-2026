import type { ReactNode } from "react";
import type { DemoSession } from "../auth/session";
import { LoginPage } from "../pages/login/LoginPage";
import { MerchantDashboardPage } from "../pages/merchant/MerchantDashboardPage";
import { MerchantNotificationsPage } from "../pages/merchant/MerchantNotificationsPage";
import { MerchantStatusPage } from "../pages/merchant/MerchantStatusPage";
import { MerchantTasksPage } from "../pages/merchant/MerchantTasksPage";
import { OrganizerDashboardPage } from "../pages/organizer/OrganizerDashboardPage";
import { OrganizerEventWorkspacePage } from "../pages/organizer/OrganizerEventWorkspacePage";
import { OrganizerEventsPage } from "../pages/organizer/OrganizerEventsPage";
import { OrganizerExceptionCenterPage } from "../pages/organizer/OrganizerExceptionCenterPage";
import { OrganizerReviewPage } from "../pages/organizer/OrganizerReviewPage";
import { PublicEventPage } from "../pages/public/PublicEventPage";
import { TouristEventHomePage } from "../pages/tourist/TouristEventHomePage";
import { TouristNoticesPage } from "../pages/tourist/TouristNoticesPage";
import { TouristRoutePage } from "../pages/tourist/TouristRoutePage";
import { TouristRoutePointPage } from "../pages/tourist/TouristRoutePointPage";

export type RouteShell = "login" | "organizer" | "merchant" | "user" | "public";

export interface ResolvedRoute {
  shell: RouteShell;
  activeKey: string;
  title: string;
  content: ReactNode;
}

function segment(pathname: string, index: number): string | undefined {
  return pathname.split("/").filter(Boolean)[index];
}

export function resolveRoute(
  pathname: string,
  session: DemoSession | null,
  onNavigate: (path: string) => void
): ResolvedRoute {
  if (pathname === "/" || pathname === "/login") {
    return {
      shell: "login",
      activeKey: "login",
      title: "Sign in",
      content: <LoginPage onNavigate={onNavigate} />
    };
  }

  if (pathname.startsWith("/public/events/")) {
    return {
      shell: "public",
      activeKey: "public",
      title: "Visitor route",
      content: <PublicEventPage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  if (pathname.startsWith("/review/")) {
    return {
      shell: "organizer",
      activeKey: "review",
      title: "Review center",
      content: <OrganizerReviewPage eventId={segment(pathname, 1) || "demo-night-tour"} />
    };
  }

  if (pathname.startsWith("/organizer/events/") && pathname.endsWith("/exceptions")) {
    return {
      shell: "organizer",
      activeKey: "exceptions",
      title: "Exception center",
      content: <OrganizerExceptionCenterPage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  if (pathname.startsWith("/organizer/events/") && pathname.endsWith("/review")) {
    return {
      shell: "organizer",
      activeKey: "review",
      title: "Review center",
      content: <OrganizerReviewPage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  if (pathname.startsWith("/organizer/events/")) {
    return {
      shell: "organizer",
      activeKey: "workspace",
      title: "Event workspace",
      content: <OrganizerEventWorkspacePage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  if (pathname === "/organizer/events") {
    return {
      shell: "organizer",
      activeKey: "events",
      title: "Events",
      content: <OrganizerEventsPage onNavigate={onNavigate} />
    };
  }

  if (pathname === "/organizer" || pathname === "/organizer/dashboard") {
    return {
      shell: "organizer",
      activeKey: "dashboard",
      title: "Operations dashboard",
      content: <OrganizerDashboardPage />
    };
  }

  if (pathname.startsWith("/merchant/events/") && pathname.endsWith("/tasks")) {
    return {
      shell: "merchant",
      activeKey: "tasks",
      title: "Assigned tasks",
      content: <MerchantTasksPage merchantId={session?.merchant_id || "m001"} />
    };
  }

  if (pathname.startsWith("/merchant/events/") && pathname.endsWith("/status")) {
    return {
      shell: "merchant",
      activeKey: "status",
      title: "Report live status",
      content: <MerchantStatusPage merchantId={session?.merchant_id || "m001"} />
    };
  }

  if (pathname === "/merchant/notifications") {
    return {
      shell: "merchant",
      activeKey: "notices",
      title: "Organizer notices",
      content: <MerchantNotificationsPage />
    };
  }

  if (pathname.startsWith("/merchant/")) {
    const merchantId =
      pathname === "/merchant/dashboard" || pathname.startsWith("/merchant/events/")
        ? session?.merchant_id || "m001"
        : segment(pathname, 1) || session?.merchant_id || "m001";

    return {
      shell: "merchant",
      activeKey: "dashboard",
      title: "Merchant dashboard",
      content: <MerchantDashboardPage merchantId={merchantId} />
    };
  }

  if (pathname.startsWith("/user/events/") && pathname.includes("/points/")) {
    return {
      shell: "user",
      activeKey: "route",
      title: "Route stop",
      content: (
        <TouristRoutePointPage
          eventId={segment(pathname, 2) || "demo-night-tour"}
          pointId={segment(pathname, 4) || "rp001"}
        />
      )
    };
  }

  if (pathname.startsWith("/user/events/") && pathname.endsWith("/route")) {
    return {
      shell: "user",
      activeKey: "route",
      title: "Route",
      content: <TouristRoutePage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  if (pathname.startsWith("/user/events/") && pathname.endsWith("/notices")) {
    return {
      shell: "user",
      activeKey: "notices",
      title: "Notices",
      content: <TouristNoticesPage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  if (pathname.startsWith("/user/events/")) {
    return {
      shell: "user",
      activeKey: "event",
      title: "My route",
      content: <TouristEventHomePage eventId={segment(pathname, 2) || "demo-night-tour"} />
    };
  }

  return {
    shell: "login",
    activeKey: "login",
    title: "Sign in",
    content: <LoginPage onNavigate={onNavigate} />
  };
}
