import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const src = resolve(__dirname, "..", "src");

const p0Files = {
  login: "pages/login/LoginPage.tsx",
  dashboard: "pages/organizer/OrganizerDashboardPage.tsx",
  exceptions: "pages/organizer/OrganizerExceptionCenterPage.tsx",
  merchantStatus: "pages/merchant/MerchantStatusPage.tsx",
  publicH5: "pages/public/PublicEventPage.tsx"
};

test("P0 pages contain product workflow language, not only shell changes", () => {
  const expectations: Record<string, string[]> = {
    login: ["auth.organizerWorkspace", "auth.merchantWorkbench", "auth.visitorRoute"],
    dashboard: [
      "organizer.dashboard.needsAttention",
      "organizer.dashboard.merchantReadiness",
      "organizer.dashboard.timelineTitle"
    ],
    exceptions: [
      "organizer.exceptions.impactScope",
      "organizer.exceptions.publicNoticePreview",
      "organizer.exceptions.confirmAction"
    ],
    merchantStatus: [
      "merchant.status.acceptVisitors",
      "merchant.status.pauseVisitors",
      "merchant.status.reportLowStock",
      "merchant.status.queueBusy"
    ],
    publicH5: ["public.event.tonightsRoute", "public.event.routeProgress", "public.event.liveUpdate"]
  };

  for (const [key, file] of Object.entries(p0Files)) {
    const source = readFileSync(resolve(src, file), "utf8");
    for (const phrase of expectations[key]) {
      expect(source).toContain(phrase);
    }
  }
});

test("accepted shells still avoid Ant Design layout primitives", () => {
  const shellFiles = [
    "layout/OrganizerProductShell.tsx",
    "layout/MerchantProductShell.tsx",
    "layout/TouristProductShell.tsx"
  ];

  for (const file of shellFiles) {
    const source = readFileSync(resolve(src, file), "utf8");
    expect(source).not.toContain("Layout");
    expect(source).not.toContain("Sider");
    expect(source).not.toContain("Menu");
    expect(source).not.toContain("antd/es/layout");
  }
});
