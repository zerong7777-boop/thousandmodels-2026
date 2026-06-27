import { afterEach, describe, expect, test, vi } from "vitest";
import { api } from "../src/api";
import { authClient } from "../src/auth/authClient";
import { authUsers, jsonResponse } from "./authTestUtils";

describe("v2.1 CSRF client boundary", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  test("demo mode sends the demo CSRF token without fetching a token first", async () => {
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse({ status: "ok", event_id: "demo-night-tour" })));
    vi.stubGlobal("fetch", fetchSpy);

    await api.seed();

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/events/demo/seed",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.objectContaining({ "X-Zhiyin-CSRF": "demo" })
      })
    );
    expect(fetchSpy).not.toHaveBeenCalledWith("/api/auth/csrf", expect.anything());
  });

  test("non-demo mode fetches a CSRF token before sending mutations", async () => {
    vi.stubEnv("VITE_DEMO_MODE", "false");
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "csrf-real-token" }))
      .mockResolvedValueOnce(jsonResponse({ status: "ok", event_id: "demo-night-tour" }));
    vi.stubGlobal("fetch", fetchSpy);

    await api.seed();

    expect(fetchSpy).toHaveBeenNthCalledWith(1, "/api/auth/csrf", { credentials: "include" });
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "/api/events/demo/seed",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.objectContaining({ "X-Zhiyin-CSRF": "csrf-real-token" })
      })
    );
  });

  test("auth login and logout use the shared CSRF mutation path", async () => {
    vi.stubEnv("VITE_DEMO_MODE", "false");
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "login-token" }))
      .mockResolvedValueOnce(jsonResponse({ user: authUsers.organizer }))
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "logout-token" }))
      .mockResolvedValueOnce(jsonResponse({ status: "ok" }));
    vi.stubGlobal("fetch", fetchSpy);

    await authClient.login("organizer.demo", "demo1234");
    await authClient.logout();

    expect(fetchSpy).toHaveBeenNthCalledWith(1, "/api/auth/csrf", { credentials: "include" });
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "/api/auth/login",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.objectContaining({ "X-Zhiyin-CSRF": "login-token" }),
        body: JSON.stringify({ username: "organizer.demo", password: "demo1234" })
      })
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(3, "/api/auth/csrf", { credentials: "include" });
    expect(fetchSpy).toHaveBeenNthCalledWith(
      4,
      "/api/auth/logout",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.objectContaining({ "X-Zhiyin-CSRF": "logout-token" })
      })
    );
  });
});
