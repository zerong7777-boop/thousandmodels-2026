import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { OrganizerProductShell } from "../src/layout/OrganizerProductShell";
import { OrganizerEventWorkspacePage } from "../src/pages/organizer/OrganizerEventWorkspacePage";
import { OrganizerEventsPage } from "../src/pages/organizer/OrganizerEventsPage";
import type { AuthUser, EventSummary } from "../src/types";

const mockApi = vi.hoisted(() => ({
  getEvents: vi.fn(),
  getEvent: vi.fn(),
  createEvent: vi.fn(),
  seed: vi.fn(),
  generatePlan: vi.fn(),
  approvePlanVersion: vi.fn(),
  getPlanVersions: vi.fn(),
  getAgentTraces: vi.fn(),
  getMerchantTasks: vi.fn(),
  getAgentRuns: vi.fn(),
  getAgentToolCalls: vi.fn(),
  getAgentModelCalls: vi.fn(),
  getAgentEvaluations: vi.fn(),
  getEventPage: vi.fn(),
  draftEventPage: vi.fn(),
  publishEventPage: vi.fn(),
  getMerchantEdgePackages: vi.fn(),
  generateMerchantEdgePackages: vi.fn(),
  generateOperationSuggestions: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

const organizer: AuthUser = {
  user_id: "usr_org_demo",
  username: "organizer.demo",
  role: "organizer",
  display_name: "Organizer Demo",
  merchant_id: null
};

function eventSummary(overrides: Partial<EventSummary> = {}): EventSummary {
  return {
    event_id: "real-harbor-fair",
    title: "Real Harbor Fair",
    area: "Inner Harbor",
    date: "2026-08-12",
    time_window: "15:00-20:00",
    status: "draft",
    current_plan_version: 0,
    public_release_status: "draft",
    ...overrides
  };
}

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  return { promise, resolve, reject };
}

async function fillRequiredCreateFields() {
  fireEvent.change(await screen.findByLabelText(/title/i), { target: { value: "Harbor Community Fair" } });
  fireEvent.change(screen.getByLabelText(/area/i), { target: { value: "Inner Harbor" } });
  fireEvent.change(screen.getByLabelText(/date/i), { target: { value: "2026-08-12" } });
  fireEvent.change(screen.getByLabelText(/time window/i), { target: { value: "15:00-20:00" } });
  fireEvent.change(screen.getByLabelText(/budget/i), { target: { value: "12000" } });
  fireEvent.change(screen.getByLabelText(/target audience/i), { target: { value: "families, students" } });
  fireEvent.change(screen.getByLabelText(/event goal/i), {
    target: { value: "Bring local families into the harbor market." }
  });
  fireEvent.change(screen.getByLabelText(/theme preferences/i), {
    target: { value: "harbor market\ncommunity crafts" }
  });
  fireEvent.change(screen.getByLabelText(/constraints/i), {
    target: { value: "avoid rain exposure, wheelchair friendly" }
  });
  fireEvent.change(screen.getByLabelText(/priority rules/i), {
    target: { value: "minimize walking\ninclude local food" }
  });
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getEvents.mockResolvedValue([]);
  mockApi.getEvent.mockResolvedValue(eventSummary());
  mockApi.createEvent.mockResolvedValue(eventSummary({ event_id: "harbor-community-fair" }));
  mockApi.seed.mockResolvedValue({ status: "ok", event_id: "demo-night-tour" });
  mockApi.generatePlan.mockResolvedValue({ current_plan: { version: 1, status: "draft" } });
  mockApi.approvePlanVersion.mockResolvedValue({ version: 1, status: "approved" });
  mockApi.getPlanVersions.mockResolvedValue([]);
  mockApi.getAgentTraces.mockResolvedValue([]);
  mockApi.getMerchantTasks.mockResolvedValue([]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getAgentToolCalls.mockResolvedValue([]);
  mockApi.getAgentModelCalls.mockResolvedValue([]);
  mockApi.getAgentEvaluations.mockResolvedValue([]);
  mockApi.getEventPage.mockRejectedValue(new Error("event page not drafted"));
  mockApi.draftEventPage.mockResolvedValue(null);
  mockApi.publishEventPage.mockResolvedValue(null);
  mockApi.getMerchantEdgePackages.mockResolvedValue({ packages: [] });
  mockApi.generateMerchantEdgePackages.mockResolvedValue({ packages: [] });
  mockApi.generateOperationSuggestions.mockResolvedValue({ suggestions: [] });
});

afterEach(() => {
  localStorage.clear();
});

test("organizer events page creates a non-demo event and navigates to its workspace", async () => {
  const onNavigate = vi.fn();
  mockApi.getEvents.mockResolvedValue([]);
  mockApi.createEvent.mockResolvedValue(eventSummary({ event_id: "harbor-community-fair" }));

  renderWithI18n(<OrganizerEventsPage onNavigate={onNavigate} />);

  fireEvent.change(await screen.findByLabelText(/title/i), { target: { value: "Harbor Community Fair" } });
  fireEvent.change(screen.getByLabelText(/area/i), { target: { value: "Inner Harbor" } });
  fireEvent.change(screen.getByLabelText(/date/i), { target: { value: "2026-08-12" } });
  fireEvent.change(screen.getByLabelText(/time window/i), { target: { value: "15:00-20:00" } });
  fireEvent.change(screen.getByLabelText(/budget/i), { target: { value: "12000" } });
  fireEvent.change(screen.getByLabelText(/target audience/i), { target: { value: "families, students" } });
  fireEvent.change(screen.getByLabelText(/event goal/i), {
    target: { value: "Bring local families into the harbor market." }
  });
  fireEvent.change(screen.getByLabelText(/theme preferences/i), {
    target: { value: "harbor market\ncommunity crafts" }
  });
  fireEvent.change(screen.getByLabelText(/constraints/i), {
    target: { value: "avoid rain exposure, wheelchair friendly" }
  });
  fireEvent.change(screen.getByLabelText(/priority rules/i), {
    target: { value: "minimize walking\ninclude local food" }
  });

  fireEvent.click(screen.getByRole("button", { name: /create event/i }));

  await waitFor(() =>
    expect(mockApi.createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "Harbor Community Fair",
        area: "Inner Harbor",
        date: "2026-08-12",
        time_window: "15:00-20:00",
        budget_mop: 12000,
        target_audience: ["families", "students"],
        event_goal: "Bring local families into the harbor market.",
        theme_preferences: ["harbor market", "community crafts"],
        constraints: ["avoid rain exposure", "wheelchair friendly"],
        priority_rules: ["minimize walking", "include local food"]
      })
    )
  );
  expect(mockApi.seed).not.toHaveBeenCalled();
  await waitFor(() => expect(onNavigate).toHaveBeenCalledWith("/organizer/events/harbor-community-fair"));
});

test("organizer events page renders event portfolio rows with event-specific links", async () => {
  mockApi.getEvents.mockResolvedValue([
    eventSummary({
      event_id: "real-harbor-fair",
      status: "active",
      current_plan_version: 2,
      public_release_status: "published"
    })
  ]);

  renderWithI18n(<OrganizerEventsPage />);

  expect(await screen.findByText("Real Harbor Fair")).toBeInTheDocument();
  expect(screen.getByText(/Inner Harbor/)).toBeInTheDocument();
  expect(screen.getByText(/2026-08-12/)).toBeInTheDocument();
  expect(screen.getByText(/15:00-20:00/)).toBeInTheDocument();
  expect(screen.getByText(/active/i)).toBeInTheDocument();
  expect(screen.getByText(/published/i)).toBeInTheDocument();
  expect(screen.getByText(/v2/i)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /open workspace/i })).toHaveAttribute(
    "href",
    "/organizer/events/real-harbor-fair"
  );
  expect(screen.getByRole("link", { name: /exceptions/i })).toHaveAttribute(
    "href",
    "/organizer/events/real-harbor-fair/exceptions"
  );
  expect(screen.getByRole("link", { name: /review/i })).toHaveAttribute(
    "href",
    "/organizer/events/real-harbor-fair/review"
  );
});

test("organizer events page ignores stale event reload responses", async () => {
  const staleEvents = deferred<EventSummary[]>();
  const freshEvents = deferred<EventSummary[]>();
  mockApi.getEvents
    .mockReturnValueOnce(staleEvents.promise)
    .mockReturnValueOnce(freshEvents.promise);
  mockApi.createEvent.mockResolvedValue(eventSummary({ event_id: "fresh-event", title: "Fresh Event" }));

  renderWithI18n(<OrganizerEventsPage onNavigate={vi.fn()} />);

  await fillRequiredCreateFields();
  fireEvent.click(screen.getByRole("button", { name: /create event/i }));

  await waitFor(() => expect(mockApi.getEvents).toHaveBeenCalledTimes(2));

  await act(async () => {
    freshEvents.resolve([eventSummary({ event_id: "fresh-event", title: "Fresh Event" })]);
  });
  expect(await screen.findByText("Fresh Event")).toBeInTheDocument();

  await act(async () => {
    staleEvents.resolve([eventSummary({ event_id: "stale-event", title: "Stale Event" })]);
  });

  expect(screen.getByText("Fresh Event")).toBeInTheDocument();
  expect(screen.queryByText("Stale Event")).not.toBeInTheDocument();
});

test("organizer events page keeps explicit demo seed separate from real create", async () => {
  mockApi.getEvents.mockResolvedValue([]);

  renderWithI18n(<OrganizerEventsPage />);

  fireEvent.click(await screen.findByRole("button", { name: /seed demo event/i }));

  await waitFor(() => expect(mockApi.seed).toHaveBeenCalledTimes(1));
  expect(mockApi.createEvent).not.toHaveBeenCalled();
});

test("organizer events page surfaces backend create validation errors", async () => {
  const onNavigate = vi.fn();
  mockApi.getEvents.mockResolvedValue([]);
  mockApi.createEvent.mockRejectedValue(new Error("Event ID already exists"));

  renderWithI18n(<OrganizerEventsPage onNavigate={onNavigate} />);

  await fillRequiredCreateFields();
  fireEvent.click(screen.getByRole("button", { name: /create event/i }));

  expect(await screen.findByRole("alert")).toHaveTextContent(/Event ID already exists/i);
  expect(onNavigate).not.toHaveBeenCalled();
});

test("organizer shell links follow the selected event id", () => {
  const onNavigate = vi.fn();

  renderWithI18n(
    <OrganizerProductShell
      user={organizer}
      pathname="/organizer/events/real-harbor-fair"
      onNavigate={onNavigate}
      onLogout={vi.fn()}
    >
      <div>Workspace</div>
    </OrganizerProductShell>
  );

  expect(screen.getByRole("link", { name: /workspace/i })).toHaveAttribute("aria-current", "page");
  expect(screen.getByRole("link", { name: /events/i })).not.toHaveAttribute("aria-current");
  fireEvent.click(screen.getByRole("link", { name: /workspace/i }));
  fireEvent.click(screen.getByRole("link", { name: /exceptions/i }));
  fireEvent.click(screen.getByRole("link", { name: /review/i }));

  expect(onNavigate).toHaveBeenNthCalledWith(1, "/organizer/events/real-harbor-fair");
  expect(onNavigate).toHaveBeenNthCalledWith(2, "/organizer/events/real-harbor-fair/exceptions");
  expect(onNavigate).toHaveBeenNthCalledWith(3, "/organizer/events/real-harbor-fair/review");
});

test("organizer workspace shows selected draft event context and builds that event plan", async () => {
  mockApi.getEvent.mockResolvedValue(eventSummary());
  mockApi.getPlanVersions.mockResolvedValue([]);
  mockApi.getAgentTraces.mockResolvedValue([]);
  mockApi.getMerchantTasks.mockResolvedValue([]);
  mockApi.getAgentRuns.mockResolvedValue([]);
  mockApi.getEventPage.mockRejectedValue(new Error("event page not drafted"));
  mockApi.getMerchantEdgePackages.mockResolvedValue({ packages: [] });

  renderWithI18n(<OrganizerEventWorkspacePage eventId="real-harbor-fair" />);

  expect(await screen.findByText("Real Harbor Fair")).toBeInTheDocument();
  expect(screen.getByText(/Inner Harbor/)).toBeInTheDocument();
  expect(screen.getByText(/2026-08-12/)).toBeInTheDocument();
  expect(screen.getByText(/15:00-20:00/)).toBeInTheDocument();
  expect(screen.getByText(/Event status: draft/i)).toBeInTheDocument();
  expect(screen.getByText(/Public release: draft/i)).toBeInTheDocument();
  expect(screen.getByText(/No route plan has been created yet/i)).toBeInTheDocument();

  const workspaceActions = screen.getByRole("region", { name: /Event workspace actions/i });
  fireEvent.click(within(workspaceActions).getByRole("button", { name: /Build route plan/i }));

  await waitFor(() => expect(mockApi.generatePlan).toHaveBeenCalledWith("real-harbor-fair"));
});

test("organizer workspace shows a visible selected event context load failure", async () => {
  mockApi.getEvent.mockRejectedValue(new Error("event not found"));

  renderWithI18n(<OrganizerEventWorkspacePage eventId="missing-event" />);

  expect(await screen.findByText(/Event context is not available yet/i)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Back to events/i })).toHaveAttribute("href", "/organizer/events");
});

test("organizer workspace surfaces event page and package action errors", async () => {
  mockApi.draftEventPage.mockRejectedValueOnce(new Error("Draft failed"));
  mockApi.publishEventPage.mockRejectedValueOnce(new Error("Publish failed"));
  mockApi.generateMerchantEdgePackages.mockRejectedValueOnce(new Error("Package failed"));

  renderWithI18n(<OrganizerEventWorkspacePage eventId="real-harbor-fair" />);

  fireEvent.click(await screen.findByRole("button", { name: /Draft event page/i }));
  expect(await screen.findByRole("alert")).toHaveTextContent(/Draft failed/i);

  fireEvent.click(screen.getByRole("button", { name: /Publish event page/i }));
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/Publish failed/i));

  fireEvent.click(screen.getByRole("button", { name: /Generate packs/i }));
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/Package failed/i));
});

test("organizer workspace exposes operation suggestion feedback as a live status", async () => {
  mockApi.generateOperationSuggestions.mockResolvedValueOnce({ suggestions: [{ id: "s1" }] });

  renderWithI18n(<OrganizerEventWorkspacePage eventId="real-harbor-fair" />);

  fireEvent.click(await screen.findByRole("button", { name: /Generate operation suggestions/i }));

  expect(await screen.findByRole("status")).toHaveTextContent(/1 operation suggestions are ready for review/i);
});
