import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type React from "react";
import { beforeEach, expect, test, vi } from "vitest";
import { I18nProvider } from "../src/i18n";
import { OrganizerProductShell } from "../src/layout/OrganizerProductShell";
import { resolveRoute } from "../src/routes/routeConfig";
import type { AuthUser, MerchantDetail, MerchantProfile } from "../src/types";

const mockApi = vi.hoisted(() => ({
  getMerchants: vi.fn(),
  getMerchant: vi.fn(),
  createMerchant: vi.fn(),
  updateMerchant: vi.fn()
}));

vi.mock("../src/api", () => ({ api: mockApi }));

const user: AuthUser = {
  user_id: "usr_org_demo",
  username: "organizer.demo",
  role: "organizer",
  display_name: "Organizer Demo",
  merchant_id: null
};

function merchant(overrides: Partial<MerchantProfile> = {}): MerchantProfile {
  return {
    merchant_id: "m900",
    name: "Harbor Tea Lab",
    type: "tea",
    location: { lat: 22.192, lng: 113.538, label: "Inner Harbor" },
    opening_hours: "10:00-22:00",
    capacity_level: "medium",
    signature_products: ["Cold brew tea"],
    story: "A local tea stop.",
    suitable_activity_types: ["rest stop"],
    rainy_day_score: 4,
    night_score: 5,
    constraints: ["needs crowd notice"],
    contact_name: "Ada Wong",
    contact_phone: "+853-6000-9000",
    address_label: "Inner Harbor Shop 9",
    area: "Inner Harbor",
    operating_windows: [{ label: "daily", start_time: "10:00", end_time: "22:00" }],
    capacity_notes: "Two guided groups per hour.",
    category_tags: ["tea", "rainy-day"],
    participation_constraints: ["needs 24h notice"],
    status: "active",
    ...overrides
  };
}

function detail(overrides: Partial<MerchantDetail> = {}): MerchantDetail {
  return {
    merchant: merchant(),
    participation_history: [
      {
        event_id: "v30-merchant-network",
        event_title: "V30 Harbor Night",
        event_date: "2026-09-09",
        participation_status: "confirmed",
        readiness_status: "ready",
        latest_plan_version: 1,
        has_interaction_package: true
      }
    ],
    ...overrides
  };
}

function renderWithI18n(content: React.ReactNode) {
  localStorage.setItem("zhiyin.locale", "en");
  return render(<I18nProvider>{content}</I18nProvider>);
}

function renderRoute(pathname = "/organizer/merchants") {
  const route = resolveRoute(
    pathname,
    { role: "organizer", actor_id: "usr_org_demo", display_name: "Organizer Demo" },
    vi.fn()
  );
  return renderWithI18n(
    <OrganizerProductShell user={user} pathname={pathname} onNavigate={vi.fn()} onLogout={vi.fn()}>
      {route.content}
    </OrganizerProductShell>
  );
}

beforeEach(() => {
  vi.resetAllMocks();
  mockApi.getMerchants.mockResolvedValue([merchant()]);
  mockApi.getMerchant.mockResolvedValue(detail());
  mockApi.createMerchant.mockResolvedValue(
    detail({ merchant: merchant({ merchant_id: "m901", name: "New Dessert Shop" }) })
  );
  mockApi.updateMerchant.mockResolvedValue(detail({ merchant: merchant({ contact_name: "Ben Lei" }) }));
});

test("organizer merchant network route lists merchant operations fields", async () => {
  renderRoute();

  expect(await screen.findByText("Harbor Tea Lab")).toBeInTheDocument();
  expect(screen.getAllByText(/Inner Harbor/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/10:00-22:00/i).length).toBeGreaterThan(0);
  expect(screen.getByText(/Ada Wong/i)).toBeInTheDocument();
});

test("organizer can create a merchant from the network page", async () => {
  renderRoute();

  fireEvent.change(await screen.findByLabelText(/Merchant name/i), { target: { value: "New Dessert Shop" } });
  fireEvent.change(screen.getByLabelText(/Merchant id/i), { target: { value: "m901" } });
  fireEvent.click(screen.getByRole("button", { name: /Create merchant/i }));

  await waitFor(() => expect(mockApi.createMerchant).toHaveBeenCalled());
});

test("organizer can edit selected merchant contact owner", async () => {
  renderRoute();

  fireEvent.click(await screen.findByRole("button", { name: /Edit Harbor Tea Lab/i }));
  fireEvent.change(screen.getByLabelText(/Contact owner/i), { target: { value: "Ben Lei" } });
  fireEvent.click(screen.getByRole("button", { name: /Save merchant/i }));

  await waitFor(() =>
    expect(mockApi.updateMerchant).toHaveBeenCalledWith("m900", expect.objectContaining({ contact_name: "Ben Lei" }))
  );
});

test("merchant network appears in organizer navigation", async () => {
  renderRoute();

  expect(await screen.findByRole("link", { name: /Merchant Network/i })).toHaveAttribute(
    "href",
    "/organizer/merchants"
  );
});
