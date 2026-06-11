import { render, screen } from "@testing-library/react";
import App from "../src/App";
import { zhHans as zh } from "../src/i18n/dictionaries/zh-Hans";
import { mockAppFetch } from "./authTestUtils";

const eventSummary = {
  event_id: "demo-night-tour",
  title: "Demo night tour",
  area: "Rua da Felicidade",
  date: "2026-07-18",
  time_window: "18:00-21:30",
  status: "active",
  current_plan_version: 1,
  public_release_status: "published"
};

const routePayload = (url: string) =>
  url.includes("/api/events") && !url.includes("/plans")
    ? [eventSummary]
    : {
        merchant: { merchant_id: "m001", name: "Merchant m001", type: "food" },
        tasks: []
      };

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("organizer compatibility route renders organizer shell", async () => {
  vi.stubGlobal("fetch", mockAppFetch("organizer", routePayload));
  window.history.pushState({}, "", "/organizer");
  render(<App />);
  expect(await screen.findByTestId("organizer-shell")).toBeInTheDocument();
});

test("merchant compatibility route renders merchant shell", async () => {
  vi.stubGlobal("fetch", mockAppFetch("merchant", routePayload));
  window.history.pushState({}, "", "/merchant/m001");
  render(<App />);
  expect(await screen.findByTestId("merchant-shell")).toBeInTheDocument();
});

test("public route renders visitor route without login", async () => {
  vi.stubGlobal("fetch", mockAppFetch(null, routePayload));
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);
  expect(await screen.findByText(zh["public.event.visitorRoute"])).toBeInTheDocument();
});

test("review compatibility route is organizer owned", async () => {
  vi.stubGlobal("fetch", mockAppFetch("organizer", routePayload));
  window.history.pushState({}, "", "/review/demo-night-tour");
  render(<App />);
  expect(await screen.findByTestId("organizer-shell")).toBeInTheDocument();
});
