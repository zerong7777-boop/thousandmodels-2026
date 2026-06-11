import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(__dirname, "..", "src");
const productFiles = [
  "pages/login/LoginPage.tsx",
  "pages/organizer/OrganizerDashboardPage.tsx",
  "pages/organizer/OrganizerEventsPage.tsx",
  "pages/organizer/OrganizerEventWorkspacePage.tsx",
  "pages/organizer/OrganizerExceptionCenterPage.tsx",
  "pages/merchant/MerchantDashboardPage.tsx",
  "pages/merchant/MerchantTasksPage.tsx",
  "pages/merchant/MerchantStatusPage.tsx",
  "pages/merchant/MerchantNotificationsPage.tsx",
  "pages/tourist/TouristEventHomePage.tsx",
  "pages/tourist/TouristRoutePage.tsx",
  "pages/tourist/TouristRoutePointPage.tsx",
  "pages/tourist/TouristNoticesPage.tsx",
  "pages/public/PublicEventPage.tsx"
];

const forbiddenEverywhere = [
  "Choose demo identity",
  "Demo-only local session",
  "Switch identity",
  "simulate merchant",
  "Seed demo event",
  "Open merchant workbench",
  "Open tourist H5"
];

const forbiddenVisitorTerms = [
  "Tourist H5",
  "Route version",
  "PlanVersion",
  "RecoveryProposal",
  "AgentTrace",
  "Incident",
  "runtime_state",
  "merchant_task_patch",
  "plan_patch"
];

test("product files do not expose demo operator controls", () => {
  for (const file of productFiles) {
    const source = readFileSync(resolve(root, file), "utf8");
    for (const term of forbiddenEverywhere) {
      expect(source).not.toContain(term);
    }
  }
});

test("tourist and public files do not leak backend terms", () => {
  for (const file of productFiles.filter((item) => item.includes("/tourist/") || item.includes("/public/"))) {
    const source = readFileSync(resolve(root, file), "utf8");
    for (const term of forbiddenVisitorTerms) {
      expect(source).not.toContain(term);
    }
  }
});
