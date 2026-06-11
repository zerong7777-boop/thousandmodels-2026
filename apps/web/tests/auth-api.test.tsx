import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { zhHans as zh } from "../src/i18n/dictionaries/zh-Hans";
import { authUsers, mockAppFetch } from "./authTestUtils";

const organizer = {
  user: {
    user_id: "usr_org_demo",
    username: "organizer.demo",
    role: "organizer",
    display_name: "Organizer Demo",
    merchant_id: null
  }
};

beforeEach(() => {
  localStorage.clear();
  window.history.pushState({}, "", "/login");
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("demo quick fill does not authenticate until submit", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: false,
    status: 401,
    json: async () => ({ detail: "not authenticated" }),
    text: async () => "not authenticated"
  });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  fireEvent.click(await screen.findByRole("button", { name: new RegExp(zh["auth.organizerDemo"]) }));

  expect(screen.getByLabelText(zh["auth.username"])).toHaveValue("organizer.demo");
  expect(screen.getByLabelText(zh["auth.password"])).toHaveValue("demo1234");
  expect(window.location.pathname).toBe("/login");
  expect(localStorage.getItem("zhiyin.demo.session")).toBeNull();
});

test("login submits credentials to backend and redirects by returned role", async () => {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/auth/me")) {
      return Promise.resolve({
        ok: false,
        status: 401,
        text: async () => "not authenticated",
        json: async () => ({ detail: "not authenticated" })
      } as Response);
    }
    if (url.endsWith("/api/auth/login")) {
      expect(init?.method).toBe("POST");
      expect(init?.credentials).toBe("include");
      expect(init?.headers).toMatchObject({ "Content-Type": "application/json", "X-Zhiyin-CSRF": "demo" });
      expect(init?.body).toBe(JSON.stringify({ username: "organizer.demo", password: "demo1234" }));
      return Promise.resolve({
        ok: true,
        json: async () => organizer,
        text: async () => JSON.stringify(organizer)
      } as Response);
    }
    return Promise.resolve({ ok: true, json: async () => [], text: async () => "[]" } as Response);
  });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  fireEvent.change(await screen.findByLabelText(zh["auth.username"]), { target: { value: "organizer.demo" } });
  fireEvent.change(screen.getByLabelText(zh["auth.password"]), { target: { value: "demo1234" } });
  fireEvent.click(screen.getByRole("button", { name: /登\s*录/ }));

  await waitFor(() => expect(window.location.pathname).toBe("/organizer/dashboard"));
  expect(localStorage.getItem("zhiyin.demo.session")).toBeNull();
});

test("language choice persists after login without changing returned role", async () => {
  vi.stubGlobal(
    "fetch",
    mockAppFetch(null, (url) => {
      if (url.endsWith("/api/auth/login")) {
        return { user: authUsers.organizer };
      }
      return [];
    })
  );

  render(<App />);

  fireEvent.click(await screen.findByRole("button", { name: /English/i }));
  expect(localStorage.getItem("zhiyin.locale")).toBe("en");

  fireEvent.click(screen.getByRole("button", { name: /Organizer demo/i }));
  fireEvent.click(screen.getByRole("button", { name: /Sign in/i }));

  await waitFor(() => expect(window.location.pathname).toBe("/organizer/dashboard"));
  expect(localStorage.getItem("zhiyin.locale")).toBe("en");
  expect(await screen.findByTestId("organizer-shell")).toBeInTheDocument();
  expect(localStorage.getItem("zhiyin.demo.session")).toBeNull();
});

test("app startup calls me before treating protected route as authenticated", async () => {
  window.history.pushState({}, "", "/organizer/dashboard");
  const fetchMock = vi.fn().mockResolvedValue({
    ok: false,
    status: 401,
    text: async () => "not authenticated",
    json: async () => ({ detail: "not authenticated" })
  });
  vi.stubGlobal("fetch", fetchMock);

  render(<App />);

  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/auth/me"),
      expect.objectContaining({ credentials: "include" })
    )
  );
  await waitFor(() => expect(window.location.pathname).toBe("/login"));
});
