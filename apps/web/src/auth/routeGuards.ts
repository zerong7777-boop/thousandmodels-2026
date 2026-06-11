import type { DemoRole, DemoSession } from "./session";

export function defaultPathForRole(role: DemoRole): string {
  if (role === "organizer") return "/organizer/dashboard";
  if (role === "merchant") return "/merchant/dashboard";
  return "/user/events/demo-night-tour";
}

export function requiredRoleForPath(pathname: string): DemoRole | "public" | null {
  if (pathname === "/" || pathname === "/login") return "public";
  if (pathname.startsWith("/public/events/")) return "public";
  if (pathname === "/organizer" || pathname.startsWith("/organizer/")) return "organizer";
  if (pathname === "/review" || pathname.startsWith("/review/")) return "organizer";
  if (pathname === "/merchant" || pathname.startsWith("/merchant/")) return "merchant";
  if (pathname === "/user" || pathname.startsWith("/user/")) return "tourist";
  return null;
}

export function canAccessPath(pathname: string, session: DemoSession | null): boolean {
  const requiredRole = requiredRoleForPath(pathname);
  if (requiredRole === "public") return true;
  if (!requiredRole) return Boolean(session);
  return session?.role === requiredRole;
}
