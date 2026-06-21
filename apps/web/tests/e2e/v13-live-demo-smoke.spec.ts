import { expect, type APIRequestContext, type Page, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotDir = path.resolve(__dirname, "../../../../docs/research/assets/v1.3-live-demo-smoke");
const API_BASE = process.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const EVENT_ID = "demo-night-tour";
const MUTATION_HEADERS = {
  "Content-Type": "application/json",
  "X-Zhiyin-CSRF": "demo",
  origin: "http://127.0.0.1:5179"
};
const FORBIDDEN_SURFACE_TERMS =
  /AgentDraft|AgentRun|PlanVersion|RecoveryProposal|qwen|dashscope|schema_failed|approval_status/i;

type MerchantEdgePackage = {
  id: string;
  merchant_id: string;
  touchpoints: Array<{ id: string }>;
  coupon_rules: Array<{ id: string }>;
};

type MerchantEdgePackageResponse = {
  packages: MerchantEdgePackage[];
};

type DemoSetup = {
  touchpointId: string;
  couponRuleId: string;
};

async function expectOk(response: Awaited<ReturnType<APIRequestContext["post"]>>, pathName: string) {
  if (!response.ok()) {
    throw new Error(`${pathName}: ${response.status()} ${await response.text()}`);
  }
}

async function apiPost<T>(
  request: APIRequestContext,
  pathName: string,
  data?: Record<string, unknown>
): Promise<T> {
  const response = await request.post(`${API_BASE}${pathName}`, {
    data,
    headers: MUTATION_HEADERS
  });
  await expectOk(response, pathName);
  return response.json() as Promise<T>;
}

async function apiGet<T>(request: APIRequestContext, pathName: string): Promise<T> {
  const response = await request.get(`${API_BASE}${pathName}`);
  await expectOk(response, pathName);
  return response.json() as Promise<T>;
}

async function setupDemo(request: APIRequestContext): Promise<DemoSetup> {
  await apiPost(request, "/api/auth/login", {
    username: "organizer.demo",
    password: "demo1234"
  });
  await apiPost(request, "/api/events/demo/seed");
  await apiPost(request, `/api/events/${EVENT_ID}/generate-plan`);
  await apiPost(request, `/api/events/${EVENT_ID}/plans/1/approve`);
  await apiPost(request, `/api/events/${EVENT_ID}/event-page/draft`);
  await apiPost(request, `/api/events/${EVENT_ID}/event-page/publish`);
  const generated = await apiPost<MerchantEdgePackageResponse>(
    request,
    `/api/events/${EVENT_ID}/merchant-edge-packages/generate`
  );
  const firstPackage = generated.packages.find(
    (item) => item.touchpoints.length > 0 && item.coupon_rules.length > 0
  );
  expect(firstPackage, "merchant package with touchpoint and coupon rule").toBeTruthy();
  return {
    touchpointId: firstPackage?.touchpoints[0]?.id ?? "",
    couponRuleId: firstPackage?.coupon_rules[0]?.id ?? ""
  };
}

async function loginThroughUi(page: Page, username: string) {
  await page.context().clearCookies();
  await page.goto("/login");
  await page.getByRole("button", { name: /English/i }).click();
  await page.getByLabel(/username/i).fill(username);
  await page.getByLabel(/password/i).fill("demo1234");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(username.startsWith("merchant.") ? /\/merchant\/dashboard/ : /\/organizer\/dashboard/);
}

async function snap(page: Page, fileName: string) {
  mkdirSync(screenshotDir, { recursive: true });
  await page.screenshot({ path: path.join(screenshotDir, fileName), fullPage: true });
}

async function expectForbiddenTermsHidden(page: Page) {
  await expect(page.getByText(FORBIDDEN_SURFACE_TERMS)).toHaveCount(0);
}

async function publicPostFromBrowser<T>(
  page: Page,
  pathName: string,
  data?: Record<string, unknown>
): Promise<T> {
  return page.evaluate(
    async ({ apiBase, pathName: browserPathName, data: browserData }) => {
      const response = await fetch(`${apiBase}${browserPathName}`, {
        method: "POST",
        credentials: "omit",
        headers: {
          "Content-Type": "application/json",
          "X-Zhiyin-CSRF": "demo"
        },
        body: browserData === undefined ? undefined : JSON.stringify(browserData)
      });
      const text = await response.text();
      if (!response.ok) {
        throw new Error(`${browserPathName}: ${response.status} ${text}`);
      }
      return text ? JSON.parse(text) : null;
    },
    { apiBase: API_BASE, pathName, data }
  ) as Promise<T>;
}

async function runPublicInteractions(page: Page, setup: DemoSetup) {
  const scanButton = page.getByRole("button", { name: "Scan spot" });
  const claimButton = page.getByRole("button", { name: "Claim offer" });
  const redeemButton = page.getByRole("button", { name: "Redeem offer" });

  if (await scanButton.isEnabled()) {
    await scanButton.click();
    await expect(page.getByText("Spot scan recorded.")).toBeVisible();
    await claimButton.click();
    await expect(page.getByText("Offer claimed.")).toBeVisible();
    await redeemButton.click();
    await expect(page.getByText("Offer redeemed.")).toBeVisible();
    return;
  }

  const interaction = await publicPostFromBrowser<{ anonymous_interaction_id: string }>(
    page,
    `/api/public/events/${EVENT_ID}/touchpoints/${setup.touchpointId}/interactions`,
    { interaction_type: "scan", source: "public-event-demo", metadata: { display_mode: "h5" } }
  );
  const claim = await publicPostFromBrowser<{ id: string; status: string }>(
    page,
    `/api/public/events/${EVENT_ID}/coupons/${setup.couponRuleId}/claim`,
    { anonymous_interaction_id: interaction.anonymous_interaction_id }
  );
  expect(claim.status).toBe("claimed");
  const redeemed = await publicPostFromBrowser<{ status: string }>(
    page,
    `/api/public/events/${EVENT_ID}/coupon-redemptions/${claim.id}/redeem`
  );
  expect(redeemed.status).toBe("redeemed");
}

test("v1.3 live local demo runs through FastAPI and Vite", async ({ page, request }) => {
  const setup = await setupDemo(request);

  await page.addInitScript(() => window.localStorage.setItem("zhiyin.locale", "en"));
  await page.setViewportSize({ width: 1440, height: 940 });

  await loginThroughUi(page, "organizer.demo");
  await expect(page).toHaveURL(/\/organizer\/dashboard/);
  await page.goto(`/organizer/events/${EVENT_ID}`);
  await expect(page.getByText("Visitor event page")).toBeVisible();
  await expect(page.getByText("Generate packs")).toBeVisible();
  await snap(page, "01-live-organizer-workspace.png");

  await loginThroughUi(page, "merchant.m001.demo");
  await expect(page).toHaveURL(/\/merchant\/dashboard/);
  await expect(page.getByText("In-store touchpoints")).toBeVisible();
  await expect(page.getByText("Interaction pack")).toBeVisible();
  await expectForbiddenTermsHidden(page);
  await snap(page, "02-live-merchant-package.png");

  await page.goto(`/merchant/events/${EVENT_ID}/status`);
  await page.getByRole("button", { name: "Report sold out" }).click();
  await expect(page.getByText("Organizer review requested.")).toBeVisible();

  await loginThroughUi(page, "organizer.demo");
  await page.goto(`/organizer/events/${EVENT_ID}/exceptions`);
  await expect(page.getByText(/sold out|inventory/i)).toBeVisible();
  await page.getByRole("button", { name: "Generate suggestions" }).click();
  await expect(page.getByText("Pause visitor flow for m001")).toBeVisible();
  await snap(page, "03-live-exception-suggestion.png");

  await page.context().clearCookies();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`/public/events/${EVENT_ID}`);
  await expect(page.getByText("Visitor event page")).toBeVisible();
  await runPublicInteractions(page, setup);
  await expectForbiddenTermsHidden(page);
  await snap(page, "04-live-public-event-page.png");

  await apiPost(request, `/api/events/${EVENT_ID}/review-report`);

  await page.setViewportSize({ width: 1440, height: 940 });
  await loginThroughUi(page, "organizer.demo");
  await page.goto(`/review/${EVENT_ID}`);
  await expect(page.getByText("Touchpoint summary")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Merchant outcomes" })).toBeVisible();
  await expect(page.getByText("Total interactions", { exact: true })).toBeVisible();
  await snap(page, "05-live-review-metrics.png");

  const publicEvent = await apiGet<Record<string, unknown>>(request, `/api/public/events/${EVENT_ID}`);
  expect(publicEvent.current_plan_version).toBeTruthy();
});
