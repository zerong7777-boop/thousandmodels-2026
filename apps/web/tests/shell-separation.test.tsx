import { render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { mockAppFetch } from "./authTestUtils";

const emptyPayload = (url: string) => {
  if (url.includes("/public/events")) {
    return {
      event_id: "demo-night-tour",
      title: "Demo night tour",
      route_points: [],
      notices: [],
      public_notices: []
    };
  }
  if (url.includes("/api/merchants/")) {
    return {
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
    };
  }
  return [];
};

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("organizer shell does not render merchant status controls or tourist H5", async () => {
  vi.stubGlobal("fetch", mockAppFetch("organizer", emptyPayload));
  window.history.pushState({}, "", "/organizer/dashboard");
  render(<App />);
  expect(await screen.findByTestId("organizer-shell")).toBeInTheDocument();
  expect(screen.queryByText(/report sold out/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/^Tourist H5$/i)).not.toBeInTheDocument();
});

test("merchant shell does not render organizer exception navigation or AgentTrace", async () => {
  vi.stubGlobal("fetch", mockAppFetch("merchant", emptyPayload));
  window.history.pushState({}, "", "/merchant/dashboard");
  render(<App />);
  expect(await screen.findByTestId("merchant-shell")).toBeInTheDocument();
  expect(screen.queryByText(/exception center/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/agenttrace/i)).not.toBeInTheDocument();
});

test("user shell does not render organizer navigation or internal object names", async () => {
  vi.stubGlobal("fetch", mockAppFetch("tourist", emptyPayload));
  window.history.pushState({}, "", "/user/events/demo-night-tour");
  render(<App />);
  expect(await screen.findByTestId("user-shell")).toBeInTheDocument();
  expect(screen.queryByText(/activity workspace/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/incident/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/recoveryproposal/i)).not.toBeInTheDocument();
});

test("protected organizer route without backend session redirects to login", async () => {
  vi.stubGlobal("fetch", mockAppFetch(null, emptyPayload));
  window.history.pushState({}, "", "/organizer/dashboard");
  render(<App />);
  await waitFor(() => expect(window.location.pathname).toBe("/login"));
  expect(screen.getByRole("heading", { name: /zhiyin haojiang/i })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: /product access/i })).toBeInTheDocument();
});
