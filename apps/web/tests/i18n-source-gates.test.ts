import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { describe, expect, test } from "vitest";

const root = path.resolve(__dirname, "../src");

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((entry) => {
    const full = path.join(dir, entry);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

describe("i18n source gates", () => {
  test("does not add a major i18n dependency", () => {
    const pkg = JSON.parse(readFileSync(path.resolve(__dirname, "../package.json"), "utf8")) as {
      dependencies?: Record<string, string>;
    };
    expect(Object.keys(pkg.dependencies ?? {})).not.toContain("i18next");
    expect(Object.keys(pkg.dependencies ?? {})).not.toContain("react-i18next");
    expect(Object.keys(pkg.dependencies ?? {})).not.toContain("@formatjs/intl");
  });

  test("active page files import useI18n after translation pass", () => {
    const translatedPages = [
      "pages/login/LoginPage.tsx",
      "pages/organizer/OrganizerDashboardPage.tsx",
      "pages/organizer/OrganizerEventWorkspacePage.tsx",
      "pages/organizer/OrganizerExceptionCenterPage.tsx",
      "pages/organizer/OrganizerReviewPage.tsx",
      "pages/merchant/MerchantDashboardPage.tsx",
      "pages/merchant/MerchantStatusPage.tsx",
      "pages/tourist/TouristRoutePage.tsx",
      "pages/public/PublicEventPage.tsx"
    ];

    for (const relativePath of translatedPages) {
      const source = readFileSync(path.join(root, relativePath), "utf8");
      expect(source).toMatch(/useI18n|t\(/);
    }
  });

  test("language switcher is wired into login and product shell surfaces", () => {
    const files = ["pages/login/LoginPage.tsx", "layout/ProductShell.tsx", "pages/public/PublicEventPage.tsx"];

    for (const relativePath of files) {
      const source = readFileSync(path.join(root, relativePath), "utf8");
      expect(source).toContain("LanguageSwitcher");
    }
  });

  test("tourist and public source avoids raw backend object names", () => {
    const forbidden = [
      "PlanVersion",
      "AgentTrace",
      "RecoveryProposal",
      "runtime_state",
      "merchant_task_patch",
      "plan_patch",
      "current_plan_version",
      "PublicProjection"
    ];
    const files = walk(path.join(root, "pages")).filter(
      (file) => file.includes(`${path.sep}public${path.sep}`) || file.includes(`${path.sep}tourist${path.sep}`)
    );

    for (const file of files) {
      const source = readFileSync(file, "utf8");
      for (const term of forbidden) {
        expect(source).not.toContain(term);
      }
    }
  });

  test("task 8 Chinese dictionaries do not keep obvious English labels", () => {
    const chineseDictionaries = [
      path.resolve(__dirname, "../src/i18n/dictionaries/zh-Hans.ts"),
      path.resolve(__dirname, "../src/i18n/dictionaries/zh-Hant.ts")
    ];
    const forbiddenPhrases = [
      "Visitor event page",
      "Merchant interaction packs",
      "Operation suggestions",
      "Touchpoint summary",
      "Merchant outcomes",
      "Follow-up tasks",
      "Tonight's story",
      "Merchant highlights",
      "Route highlights"
    ];

    for (const file of chineseDictionaries) {
      const source = readFileSync(file, "utf8");
      for (const phrase of forbiddenPhrases) {
        expect(source).not.toContain(phrase);
      }
    }
  });
});
