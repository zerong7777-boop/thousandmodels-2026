import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { I18nProvider } from "../src/i18n";
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

function renderWithI18n(ui: ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

test("organizer shell is operations focused and has no cross-role shortcuts", () => {
  renderWithI18n(
    <OrganizerProductShell user={organizer} pathname="/organizer/dashboard" onNavigate={vi.fn()} onLogout={vi.fn()}>
      <div>Workspace</div>
    </OrganizerProductShell>
  );

  expect(screen.getByText(/运营工作台/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /English/i })).toBeInTheDocument();
  expect(screen.queryByText(/open merchant workbench/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/open tourist/i)).not.toBeInTheDocument();
});

test("merchant shell has task status notice navigation and no organizer approvals", () => {
  renderWithI18n(
    <MerchantProductShell user={merchant} pathname="/merchant/dashboard" onNavigate={vi.fn()} onLogout={vi.fn()}>
      <div>Workbench</div>
    </MerchantProductShell>
  );

  expect(screen.getAllByText(/任务/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/状态/i).length).toBeGreaterThan(0);
  expect(screen.getAllByText(/通知/i).length).toBeGreaterThan(0);
  expect(screen.queryByText(/approvals/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/agent trace/i)).not.toBeInTheDocument();
});

test("tourist shell is route focused and has no backend terms", () => {
  renderWithI18n(
    <TouristProductShell user={tourist} pathname="/user/events/demo-night-tour" onNavigate={vi.fn()} onLogout={vi.fn()}>
      <div>Route</div>
    </TouristProductShell>
  );

  expect(screen.getAllByText(/路线/i).length).toBeGreaterThan(0);
  expect(screen.queryByText(/PlanVersion/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/Incident/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/RecoveryProposal/i)).not.toBeInTheDocument();
});
