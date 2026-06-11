import type { ReactNode } from "react";
import { useAuth } from "./AuthProvider";
import { canAccessPath } from "./roleRouting";

export function ProtectedRoute({ pathname, children }: { pathname: string; children: ReactNode }) {
  const { status, user } = useAuth();

  if (status === "loading") {
    return <div className="auth-loading">Loading session...</div>;
  }

  if (!canAccessPath(pathname, user)) {
    return null;
  }

  return <>{children}</>;
}
