import { vi } from "vitest";

export const authUsers = {
  organizer: {
    user_id: "usr_org_demo",
    username: "organizer.demo",
    role: "organizer",
    display_name: "Organizer Demo",
    merchant_id: null
  },
  merchant: {
    user_id: "usr_merchant_m001_demo",
    username: "merchant.m001.demo",
    role: "merchant",
    display_name: "Merchant m001",
    merchant_id: "m001"
  },
  tourist: {
    user_id: "usr_tourist_demo",
    username: "tourist.demo",
    role: "tourist",
    display_name: "Tourist Demo",
    merchant_id: null
  }
} as const;

export type AuthTestRole = keyof typeof authUsers;

export function jsonResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
    text: async () => (typeof payload === "string" ? payload : JSON.stringify(payload))
  } as Response;
}

export function mockAppFetch(
  role: AuthTestRole | null,
  resolvePayload: (url: string, init?: RequestInit) => unknown = () => ({})
) {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/auth/me")) {
      return Promise.resolve(
        role
          ? jsonResponse({ user: authUsers[role] })
          : jsonResponse({ detail: "not authenticated" }, false, 401)
      );
    }
    if (url.endsWith("/api/auth/logout")) {
      return Promise.resolve(jsonResponse({ status: "ok" }));
    }
    return Promise.resolve(jsonResponse(resolvePayload(url, init)));
  });
}
