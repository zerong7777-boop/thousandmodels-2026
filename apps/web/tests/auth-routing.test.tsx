import { beforeEach, describe, expect, test } from "vitest";
import {
  clearDemoSession,
  getDemoSession,
  setDemoSession,
  type DemoSession
} from "../src/auth/session";
import { canAccessPath, defaultPathForRole, requiredRoleForPath } from "../src/auth/routeGuards";

const organizer: DemoSession = {
  role: "organizer",
  actor_id: "org-demo",
  display_name: "Organizer demo"
};

const merchant: DemoSession = {
  role: "merchant",
  actor_id: "merchant-m001",
  display_name: "Merchant m001",
  merchant_id: "m001"
};

const tourist: DemoSession = {
  role: "tourist",
  actor_id: "tourist-demo",
  display_name: "Tourist demo"
};

beforeEach(() => {
  localStorage.clear();
});

describe("demo session", () => {
  test("stores and clears the selected demo role", () => {
    setDemoSession(merchant);
    expect(getDemoSession()).toEqual(merchant);
    clearDemoSession();
    expect(getDemoSession()).toBeNull();
  });

  test("ignores malformed session payloads", () => {
    localStorage.setItem("zhiyin.demo.session", "{bad json");
    expect(getDemoSession()).toBeNull();
  });
});

describe("route guards", () => {
  test("allows login and public event routes without login", () => {
    expect(canAccessPath("/login", null)).toBe(true);
    expect(canAccessPath("/public/events/demo-night-tour", null)).toBe(true);
  });

  test("blocks protected role routes without login", () => {
    expect(canAccessPath("/organizer/dashboard", null)).toBe(false);
    expect(canAccessPath("/merchant/dashboard", null)).toBe(false);
    expect(canAccessPath("/user/events/demo-night-tour", null)).toBe(false);
  });

  test("allows organizer only on organizer-owned routes", () => {
    expect(canAccessPath("/organizer/dashboard", organizer)).toBe(true);
    expect(canAccessPath("/organizer/events/demo-night-tour/exceptions", organizer)).toBe(true);
    expect(canAccessPath("/review/demo-night-tour", organizer)).toBe(true);
    expect(canAccessPath("/merchant/dashboard", organizer)).toBe(false);
  });

  test("allows merchant only on merchant-owned routes", () => {
    expect(canAccessPath("/merchant/dashboard", merchant)).toBe(true);
    expect(canAccessPath("/merchant/m001", merchant)).toBe(true);
    expect(canAccessPath("/organizer/dashboard", merchant)).toBe(false);
  });

  test("allows tourist only on user-owned routes", () => {
    expect(canAccessPath("/user/events/demo-night-tour", tourist)).toBe(true);
    expect(canAccessPath("/organizer/dashboard", tourist)).toBe(false);
    expect(canAccessPath("/merchant/dashboard", tourist)).toBe(false);
  });

  test("maps each role to a default landing page", () => {
    expect(defaultPathForRole("organizer")).toBe("/organizer/dashboard");
    expect(defaultPathForRole("merchant")).toBe("/merchant/dashboard");
    expect(defaultPathForRole("tourist")).toBe("/user/events/demo-night-tour");
  });

  test("resolves route ownership for compatibility routes", () => {
    expect(requiredRoleForPath("/organizer")).toBe("organizer");
    expect(requiredRoleForPath("/merchant/m001")).toBe("merchant");
    expect(requiredRoleForPath("/review/demo-night-tour")).toBe("organizer");
    expect(requiredRoleForPath("/public/events/demo-night-tour")).toBe("public");
  });
});
