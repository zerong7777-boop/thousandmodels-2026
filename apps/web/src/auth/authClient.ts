import type { AuthResponse, AuthUser } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export const authClient = {
  async me(): Promise<AuthUser> {
    const response = await fetch(`${API_BASE}/api/auth/me`, {
      credentials: "include"
    });
    return (await parseJson<AuthResponse>(response)).user;
  },

  async login(username: string, password: string): Promise<AuthUser> {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-Zhiyin-CSRF": "demo" },
      body: JSON.stringify({ username, password })
    });
    return (await parseJson<AuthResponse>(response)).user;
  },

  async logout(): Promise<void> {
    const response = await fetch(`${API_BASE}/api/auth/logout`, {
      method: "POST",
      credentials: "include",
      headers: { "X-Zhiyin-CSRF": "demo" }
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
  }
};
