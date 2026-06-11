import { render, screen } from "@testing-library/react";
import App from "../src/App";
import { mockAppFetch } from "./authTestUtils";

const reviewPayload = (url: string) =>
  url.includes("/public/events")
    ? {
        event_id: "demo-night-tour",
        title: "Demo night tour",
        status: "active",
        current_plan_version: 2,
        route_points: [
          {
            point_id: "rp001",
            name: "Rua da Felicidade",
            story: "Old street story",
            visitor_task: "Answer a question",
            linked_merchants: ["m001"],
            is_indoor: false,
            current_status: "active"
          }
        ],
        notices: ["Route updated"],
        public_notices: [{ message: "Route updated", publish_status: "published" }]
      }
    : {
        event_id: "demo-night-tour",
        summary: "Event completed",
        route_result: "Route completed",
        merchant_result: "Merchants completed",
        incident_summary: "Inventory exception recovered",
        agent_actions: ["ReviewAgent summarized metrics"],
        human_approvals: ["Organizer approved recovery"],
        lessons_learned: ["H5 visits 428"],
        next_event_recommendations: ["Reduce sold-out merchant routing weight"]
      };

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("public visitor route renders story and notice without login", async () => {
  vi.stubGlobal("fetch", mockAppFetch(null, reviewPayload));
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);
  expect(await screen.findByText(/Demo night tour/)).toBeInTheDocument();
  expect(screen.getByText(/Old street story/)).toBeInTheDocument();
  expect(screen.getByText(/Route updated/)).toBeInTheDocument();
});

test("review center renders metric-backed recommendations for organizer session", async () => {
  vi.stubGlobal("fetch", mockAppFetch("organizer", reviewPayload));
  window.history.pushState({}, "", "/review/demo-night-tour");
  render(<App />);
  expect(await screen.findByTestId("organizer-shell")).toBeInTheDocument();
  expect((await screen.findAllByText(/H5 visits 428/)).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/Check-ins/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/Response time/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/Queue pressure/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/Budget used/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/Recommendations/i).length).toBeGreaterThan(0);
});
