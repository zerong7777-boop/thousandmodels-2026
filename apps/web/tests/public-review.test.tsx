import { fireEvent, render, screen } from "@testing-library/react";
import App from "../src/App";
import { zhHans as zh } from "../src/i18n/dictionaries/zh-Hans";
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
  expect(await screen.findByText(zh["public.event.tonightsRoute"])).toBeInTheDocument();
  expect(screen.getByText(zh["demo.route.rp001.story"])).toBeInTheDocument();
  expect(screen.getByText(zh["demo.notice.routeUpdated"])).toBeInTheDocument();
  expect(screen.queryByText(/PlanVersion/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/Incident/i)).not.toBeInTheDocument();
});

test("review center renders metric-backed recommendations for organizer session", async () => {
  vi.stubGlobal("fetch", mockAppFetch("organizer", reviewPayload));
  window.history.pushState({}, "", "/review/demo-night-tour");
  render(<App />);
  expect(await screen.findByTestId("organizer-shell")).toBeInTheDocument();
  expect((await screen.findAllByText(zh["organizer.review.metaVisits"])).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["organizer.review.checkIns"]).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["organizer.review.responseTime"]).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["organizer.review.queuePressure"]).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["organizer.review.budgetUsed"]).length).toBeGreaterThan(0);
  expect(screen.getAllByText(zh["organizer.review.recommendations"]).length).toBeGreaterThan(0);
});

test("public H5 switches language without login", async () => {
  vi.stubGlobal("fetch", mockAppFetch(null, reviewPayload));
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);

  expect(await screen.findByText(zh["public.event.tonightsRoute"])).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /English/i }));

  expect(await screen.findByText(/Tonight's route/i)).toBeInTheDocument();
  expect(window.location.pathname).toBe("/public/events/demo-night-tour");
  expect(screen.queryByText(/logout/i)).not.toBeInTheDocument();
});
