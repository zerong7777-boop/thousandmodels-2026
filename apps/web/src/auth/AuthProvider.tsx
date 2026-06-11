import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { AuthUser } from "../types";
import { authClient } from "./authClient";

type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  user: AuthUser | null;
  status: AuthStatus;
  login: (username: string, password: string) => Promise<AuthUser>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");

  const refresh = async () => {
    try {
      const nextUser = await authClient.me();
      setUser(nextUser);
      setStatus("authenticated");
    } catch {
      setUser(null);
      setStatus("anonymous");
    }
  };

  useEffect(() => {
    let mounted = true;

    authClient
      .me()
      .then((nextUser) => {
        if (!mounted) return;
        setUser(nextUser);
        setStatus("authenticated");
      })
      .catch(() => {
        if (!mounted) return;
        setUser(null);
        setStatus("anonymous");
      });

    return () => {
      mounted = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      status,
      login: async (username: string, password: string) => {
        const nextUser = await authClient.login(username, password);
        setUser(nextUser);
        setStatus("authenticated");
        return nextUser;
      },
      logout: async () => {
        try {
          await authClient.logout();
        } finally {
          setUser(null);
          setStatus("anonymous");
        }
      },
      refresh
    }),
    [status, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
