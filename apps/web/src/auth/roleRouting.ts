import type { AuthUser, UserRole } from "../types";

export function defaultPathForRole(role: UserRole): string {
  if (role === "organizer") return "/organizer/dashboard";
  if (role === "merchant") return "/merchant/dashboard";
  return "/user/events/demo-night-tour";
}

export function requiredRoleForPath(pathname: string): UserRole | "public" | null {
  if (pathname === "/" || pathname === "/login") return "public";
  if (pathname.startsWith("/public/events/")) return "public";
  if (pathname === "/organizer" || pathname.startsWith("/organizer/")) return "organizer";
  if (pathname === "/review" || pathname.startsWith("/review/")) return "organizer";
  if (pathname === "/merchant" || pathname.startsWith("/merchant/")) return "merchant";
  if (pathname === "/user" || pathname.startsWith("/user/")) return "tourist";
  return null;
}

export function canAccessPath(pathname: string, user: AuthUser | null): boolean {
  const requiredRole = requiredRoleForPath(pathname);
  if (requiredRole === "public") return true;
  if (!requiredRole) return Boolean(user);
  if (!user || user.role !== requiredRole) return false;

  if (requiredRole === "merchant") {
    const merchantId = pathname.match(/^\/merchant\/([^/]+)/)?.[1];
    const reserved = merchantId === "dashboard" || merchantId === "events" || merchantId === "notifications";
    if (merchantId && !reserved && merchantId !== user.merchant_id) {
      return false;
    }
  }

  return true;
}

export function redirectedPathFor(pathname: string, user: AuthUser | null): string {
  if (pathname === "/") {
    return user ? defaultPathForRole(user.role) : "/login";
  }
  if (pathname === "/login" && user) {
    return defaultPathForRole(user.role);
  }
  if (canAccessPath(pathname, user)) {
    return pathname;
  }
  return user ? defaultPathForRole(user.role) : "/login";
}
