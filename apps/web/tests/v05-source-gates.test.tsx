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
    login: ["Organizer workspace", "Merchant workbench", "Visitor route"],
    dashboard: ["Needs attention", "Merchant readiness", "Activity timeline"],
    exceptions: ["Impact scope", "Public notice preview", "Confirm recovery update"],
    merchantStatus: ["Accept visitors", "Pause visitors", "Report low stock", "Queue busy"],
    publicH5: ["Tonight's route", "Route progress", "Live update"]
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
