import { ConfigProvider } from "antd";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AuthProvider, useAuth } from "./auth/AuthProvider";
import { redirectedPathFor, requiredRoleForPath } from "./auth/roleRouting";
import type { DemoSession } from "./auth/session";
import { MerchantProductShell } from "./layout/MerchantProductShell";
import { OrganizerProductShell } from "./layout/OrganizerProductShell";
import { TouristProductShell } from "./layout/TouristProductShell";
import { I18nProvider, useI18n } from "./i18n";
import { resolveRoute } from "./routes/routeConfig";
import { appTheme } from "./theme";
import type { AuthUser } from "./types";

export default function App() {
  return (
    <ConfigProvider theme={appTheme}>
      <I18nProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </I18nProvider>
    </ConfigProvider>
  );
}

function sessionFromUser(user: AuthUser): DemoSession {
  return {
    role: user.role,
    actor_id: user.user_id,
    display_name: user.display_name,
    merchant_id: user.merchant_id ?? undefined
  };
}

function AppContent() {
  const { status, user, logout } = useAuth();
  const { t } = useI18n();
  const [pathname, setPathname] = useState(window.location.pathname);

  const navigate = useCallback((path: string) => {
    window.history.pushState({}, "", path);
    setPathname(path);
  }, []);

  const logoutAndNavigate = useCallback(async () => {
    await logout();
    navigate("/login");
  }, [logout, navigate]);

  const session = user ? sessionFromUser(user) : null;
  const waitingForProtectedSession =
    status === "loading" && requiredRoleForPath(pathname) !== "public" && pathname !== "/login";

  const effectivePath = useMemo(() => {
    if (waitingForProtectedSession) {
      return pathname;
    }
    return redirectedPathFor(pathname, user);
  }, [pathname, user, waitingForProtectedSession]);

  const route = resolveRoute(effectivePath, session, navigate);

  useEffect(() => {
    const onPopState = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    if (effectivePath !== pathname) {
      window.history.replaceState({}, "", effectivePath);
      setPathname(effectivePath);
    }
  }, [effectivePath, pathname]);

  if (waitingForProtectedSession) {
    return <main className="auth-loading">{t("common.loadingSession")}</main>;
  }

  return route.shell === "login" || !session || !user ? (
    route.content
  ) : route.shell === "organizer" ? (
    <OrganizerProductShell user={user} pathname={effectivePath} onNavigate={navigate} onLogout={logoutAndNavigate}>
      {route.content}
    </OrganizerProductShell>
  ) : route.shell === "merchant" ? (
    <MerchantProductShell user={user} pathname={effectivePath} onNavigate={navigate} onLogout={logoutAndNavigate}>
      {route.content}
    </MerchantProductShell>
  ) : route.shell === "user" ? (
    <TouristProductShell user={user} pathname={effectivePath} onNavigate={navigate} onLogout={logoutAndNavigate}>
      {route.content}
    </TouristProductShell>
  ) : (
    route.content
  );
}
