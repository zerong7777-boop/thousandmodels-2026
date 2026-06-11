import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { getDemoSession } from "../src/auth/session";
import { authUsers, jsonResponse, mockAppFetch } from "./authTestUtils";

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/login");
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("login page offers credentials and demo account shortcuts", async () => {
  vi.stubGlobal("fetch", mockAppFetch(null));

  render(<App />);

  expect(await screen.findByLabelText("用户名")).toBeInTheDocument();
  expect(screen.getByLabelText("密码")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /主办方演示/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /商户演示/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /游客演示/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /繁體中文/i })).toBeInTheDocument();
});

test("language switcher changes login copy before authentication", async () => {
  vi.stubGlobal("fetch", mockAppFetch(null));

  render(<App />);

  fireEvent.click(await screen.findByRole("button", { name: /English/i }));
  expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /merchant demo/i })).toBeInTheDocument();
  expect(localStorage.getItem("zhiyin.locale")).toBe("en");
});

test("selecting merchant fills credentials and submit creates backend session", async () => {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/auth/me")) {
      return Promise.resolve(jsonResponse({ detail: "not authenticated" }, false, 401));
    }
    if (url.endsWith("/api/auth/login")) {
      expect(init?.body).toBe(JSON.stringify({ username: "merchant.m001.demo", password: "demo1234" }));
      return Promise.resolve(jsonResponse({ user: authUsers.merchant }));
    }
    return Promise.resolve(
      jsonResponse({
        merchant: { merchant_id: "m001", name: "Merchant m001", type: "food" },
        tasks: [],
        runtime_state: {
          merchant_id: "m001",
          inventory_status: "normal",
          queue_status: "normal",
          available_for_visitors: true,
          temporary_note: "",
          updated_at: "2026-06-10T00:00:00Z"
        }
      })
    );
  });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /商户演示/i }));

  expect(screen.getByLabelText("用户名")).toHaveValue("merchant.m001.demo");
  expect(screen.getByLabelText("密码")).toHaveValue("demo1234");
  expect(getDemoSession()).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: /登\s*录/i }));

  await waitFor(() => expect(window.location.pathname).toBe("/merchant/dashboard"));
  expect(await screen.findByTestId("merchant-shell")).toBeInTheDocument();
  expect(getDemoSession()).toBeNull();
});
