import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { EventMerchantSetupPanel } from "../src/pages/organizer/EventMerchantSetupPanel";
import { MerchantEventSetupPage } from "../src/pages/merchant/MerchantEventSetupPage";
import type { EventMerchantSetupSummary, MerchantAssignedEvent, MerchantProfile } from "../src/types";

const mockApi = vi.hoisted(() => ({
  getMyMerchantEvents: vi.fn(),
  getMyMerchantEventSetup: vi.fn(),
  submitMyMerchantEventSetup: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

const assignedEvent: MerchantAssignedEvent = {
  event: {
    event_id: "v33-merchant-setup",
    title: "V33 Merchant Setup",
    area: "Inner Harbor",
    date: "2026-09-20",
    time_window: "16:00-21:00",
    status: "draft",
    current_plan_version: 0,
    public_release_status: "draft"
  },
  participant: {
    event_id: "v33-merchant-setup",
    merchant_id: "m001",
    participation_status: "confirmed",
    readiness_status: "needs_setup",
    role_hint: "tea stop",
    notes: "Organizer wants a covered queue.",
    setup_status: "not_started",
    capacity_commitment: null,
    staffing_ready: false,
    stock_ready: false,
    indoor_backup_ready: false,
    operating_window_confirmed: false,
    merchant_contact_name: "",
    merchant_contact_phone: "",
    merchant_notes: "",
    submitted_at: null,
    submitted_by: null,
    setup_gaps: ["merchant setup not submitted"],
    created_at: "2026-06-29T00:00:00Z",
    updated_at: "2026-06-29T00:00:00Z"
  },
  eligibility: {
    merchant_id: "m001",
    status: "eligible",
    reasons: []
  },
  setup_gaps: ["merchant setup not submitted"],
  ready_for_planning: false
};

const merchant: MerchantProfile = {
  merchant_id: "m001",
  name: "Harbor Tea Lab",
  type: "tea",
  capacity_level: "medium",
  signature_products: ["Cold brew tea"],
  suitable_activity_types: ["rainy-day"],
  rainy_day_score: 5,
  night_score: 5,
  constraints: [],
  area: "Inner Harbor",
  operating_windows: [{ label: "daily", start_time: "10:00", end_time: "22:00" }]
};

function roster(): EventMerchantSetupSummary {
  return {
    event_id: "v33-merchant-setup",
    participants: [
      {
        ...assignedEvent.participant,
        setup_status: "submitted",
        capacity_commitment: "medium",
        staffing_ready: true,
        stock_ready: true,
        indoor_backup_ready: false,
        operating_window_confirmed: true,
        merchant_contact_name: "Ada Chan",
        merchant_contact_phone: "+853-6000-0101",
        merchant_notes: "Two staff confirmed.",
        setup_gaps: ["indoor backup readiness not confirmed"]
      }
    ],
    total_count: 1,
    ready_count: 0,
    needs_setup_count: 1,
    missing_count: 0,
    declined_count: 0,
    ready_for_planning: false,
    eligibility: {
      m001: {
        merchant_id: "m001",
        status: "eligible",
        reasons: []
      }
    }
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getMyMerchantEvents.mockResolvedValue([assignedEvent]);
  mockApi.getMyMerchantEventSetup.mockResolvedValue(assignedEvent);
  mockApi.submitMyMerchantEventSetup.mockResolvedValue({
    ...assignedEvent,
    participant: {
      ...assignedEvent.participant,
      setup_status: "submitted",
      capacity_commitment: "high",
      staffing_ready: true,
      stock_ready: true,
      indoor_backup_ready: true,
      operating_window_confirmed: true,
      merchant_contact_name: "Ada Chan",
      merchant_contact_phone: "+853-6000-0101",
      merchant_notes: "Full setup submitted."
    },
    setup_gaps: []
  });
});

test("merchant setup page submits event-specific preparation evidence", async () => {
  renderWithI18n(<MerchantEventSetupPage eventId="v33-merchant-setup" />);

  expect(await screen.findByRole("heading", { name: /V33 Merchant Setup/i })).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText(/Capacity commitment/i), { target: { value: "high" } });
  fireEvent.change(screen.getByLabelText(/Contact name/i), { target: { value: "Ada Chan" } });
  fireEvent.change(screen.getByLabelText(/Contact phone/i), { target: { value: "+853-6000-0101" } });
  fireEvent.click(screen.getByLabelText(/Staffing ready/i));
  fireEvent.click(screen.getByLabelText(/Stock ready/i));
  fireEvent.click(screen.getByLabelText(/Indoor backup ready/i));
  fireEvent.click(screen.getByLabelText(/Operating window confirmed/i));
  fireEvent.change(screen.getByLabelText(/Merchant notes/i), { target: { value: "Full setup submitted." } });
  fireEvent.click(screen.getByRole("button", { name: /Submit setup/i }));

  await waitFor(() =>
    expect(mockApi.submitMyMerchantEventSetup).toHaveBeenCalledWith(
      "v33-merchant-setup",
      expect.objectContaining({
        capacity_commitment: "high",
        staffing_ready: true,
        stock_ready: true,
        indoor_backup_ready: true,
        operating_window_confirmed: true,
        merchant_contact_name: "Ada Chan",
        merchant_contact_phone: "+853-6000-0101",
        merchant_notes: "Full setup submitted."
      })
    )
  );
  expect(await screen.findByRole("status")).toHaveTextContent("Setup submitted.");
});

test("organizer merchant setup panel renders submitted setup evidence and gaps", async () => {
  renderWithI18n(
    <EventMerchantSetupPanel
      eventId="v33-merchant-setup"
      merchants={[merchant]}
      setup={roster()}
      onSave={vi.fn()}
      onMarkReady={vi.fn()}
    />
  );

  expect(screen.getByText(/Ada Chan/i)).toBeInTheDocument();
  expect(screen.getByText(/\+853-6000-0101/i)).toBeInTheDocument();
  expect(screen.getByText(/Capacity medium/i)).toBeInTheDocument();
  expect(screen.getByText(/Two staff confirmed/i)).toBeInTheDocument();
  expect(screen.getByText(/indoor backup readiness not confirmed/i)).toBeInTheDocument();
});
