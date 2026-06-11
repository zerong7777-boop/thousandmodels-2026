import { render, screen } from "@testing-library/react";
import { MerchantProductShell } from "../src/layout/MerchantProductShell";
import { OrganizerProductShell } from "../src/layout/OrganizerProductShell";
import { TouristProductShell } from "../src/layout/TouristProductShell";

const organizer = {
  user_id: "usr_org_demo",
  username: "organizer.demo",
  role: "organizer" as const,
  display_name: "Organizer Demo",
  merchant_id: null
};

const merchant = {
  user_id: "usr_merchant_m001_demo",
  username: "merchant.m001.demo",
  role: "merchant" as const,
  display_name: "Merchant m001 Demo",
  merchant_id: "m001"
};

const tourist = {
  user_id: "usr_tourist_demo",
  username: "tourist.demo",
  role: "tourist" as const,
  display_name: "Tourist Demo",
  merchant_id: null
};

test("organizer shell is operations focused and has no cross-role shortcuts", () => {
  render(
    <OrganizerProductShell user={organizer} pathname="/organizer/dashboard" onNavigate={vi.fn()} onLogout={vi.fn()}>
      <div>Workspace</div>
    </OrganizerProductShell>
  );

  expect(screen.getByText(/operations/i)).toBeInTheDocument();
  expect(screen.queryByText(/open merchant workbench/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/open tourist/i)).not.toBeInTheDocument();
});

test("merchant shell has task status notice navigation and no organizer approvals", () => {
  render(
    <MerchantProductShell user={merchant} pathname="/merchant/dashboard" onNavigate={vi.fn()} onLogout={vi.fn()}>
      <div>Workbench</div>
    </MerchantProductShell>
  );

  expect(screen.getAllByText(/tasks/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/status/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/notices/i).length).toBeGreaterThan(0);
  expect(screen.queryByText(/approvals/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/agent trace/i)).not.toBeInTheDocument();
});

test("tourist shell is route focused and has no backend terms", () => {
  render(
    <TouristProductShell user={tourist} pathname="/user/events/demo-night-tour" onNavigate={vi.fn()} onLogout={vi.fn()}>
      <div>Route</div>
    </TouristProductShell>
  );

  expect(screen.getAllByText(/route/i).length).toBeGreaterThan(0);
  expect(screen.queryByText(/PlanVersion/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/Incident/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/RecoveryProposal/i)).not.toBeInTheDocument();
});
