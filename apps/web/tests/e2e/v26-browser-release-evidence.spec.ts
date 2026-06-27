import { expect, type APIRequestContext, type APIResponse, type Page, test } from "@playwright/test";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const apiPort = process.env.PLAYWRIGHT_API_PORT ?? "8000";
const webPort = process.env.PLAYWRIGHT_WEB_PORT ?? "5179";
const API_BASE = process.env.VITE_API_BASE_URL ?? `http://127.0.0.1:${apiPort}`;
const WEB_BASE = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${webPort}`;
const EVENT_ID = "demo-night-tour";
const evidenceDir = path.resolve(
  __dirname,
  "../../../../docs/research/assets/v2.6-browser-release-evidence-gate"
);
const evidenceFile =
  process.env.V26_BROWSER_EVIDENCE_OUTPUT ??
  path.join(evidenceDir, "browser-release-gate-result.json");
const screenshotDir =
  process.env.V26_BROWSER_SCREENSHOT_DIR ??
  path.join(os.tmpdir(), "thousandmodels-v26-browser-release-evidence-gate");
const maxScreenshots = 5;
const forbiddenSurfaceTerms =
  /AgentDraft|AgentRun|PlanVersion|RecoveryProposal|qwen|dashscope|schema_failed|approval_status/i;
const mutationHeaders = {
  "Content-Type": "application/json",
  "X-Zhiyin-CSRF": "demo",
  origin: new URL(WEB_BASE).origin
};

type EvidenceStatus = "passed" | "failed";

interface EvidenceStep {
  step: string;
  ok: boolean;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  summary: string;
}

interface ScreenshotMetadata {
  file_name: string;
  step: string;
  viewport: {
    width: number;
    height: number;
  };
  bytes: number;
  sha256: string;
}

interface Evidence {
  status: EvidenceStatus;
  event_id: string;
  api_base_url: string;
  web_base_url: string;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  steps: EvidenceStep[];
  screenshots: ScreenshotMetadata[];
  metrics_observed: Record<string, number>;
  artifact_policy: {
    evidence_file: string;
    screenshot_storage: "temp_dir" | "V26_BROWSER_SCREENSHOT_DIR";
    screenshot_count_limit: number;
    path_policy: string;
    secret_policy: string;
  };
  failure?: {
    step?: string;
    summary: string;
  };
}

function sanitizeError(error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  return message
    .replace(/demo1234/g, "[redacted]")
    .replace(/[A-Za-z]:\\[^\s"'<>)]*/g, "[local-path]")
    .replace(/\/(?:Users|home|tmp|var|private|mnt)\/[^\s"'<>)]*/g, "[local-path]")
    .replace(/(password|token|cookie)=([^&\s]+)/gi, "$1=[redacted]");
}

function createEvidence(): Evidence {
  const startedAt = new Date().toISOString();
  return {
    status: "failed",
    event_id: EVENT_ID,
    api_base_url: API_BASE,
    web_base_url: WEB_BASE,
    started_at: startedAt,
    finished_at: startedAt,
    duration_ms: 0,
    steps: [],
    screenshots: [],
    metrics_observed: {},
    artifact_policy: {
      evidence_file:
        "docs/research/assets/v2.6-browser-release-evidence-gate/browser-release-gate-result.json",
      screenshot_storage: process.env.V26_BROWSER_SCREENSHOT_DIR ? "V26_BROWSER_SCREENSHOT_DIR" : "temp_dir",
      screenshot_count_limit: maxScreenshots,
      path_policy: "Evidence records relative artifact names only, never local absolute paths.",
      secret_policy: "Evidence omits passwords, cookies, tokens, and request headers."
    }
  };
}

async function recordStep<T>(
  evidence: Evidence,
  name: string,
  action: () => Promise<T>,
  summary = "passed"
): Promise<T> {
  const startedAt = new Date().toISOString();
  const started = Date.now();
  try {
    const result = await test.step(name, action);
    evidence.steps.push({
      step: name,
      ok: true,
      started_at: startedAt,
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - started,
      summary
    });
    return result;
  } catch (error) {
    const sanitized = sanitizeError(error);
    evidence.steps.push({
      step: name,
      ok: false,
      started_at: startedAt,
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - started,
      summary: sanitized
    });
    throw error;
  }
}

function writeEvidence(evidence: Evidence, started: number) {
  evidence.finished_at = new Date().toISOString();
  evidence.duration_ms = Date.now() - started;
  mkdirSync(path.dirname(evidenceFile), { recursive: true });
  writeFileSync(evidenceFile, `${JSON.stringify(evidence, null, 2)}\n`, "utf8");
}

async function expectOk(response: APIResponse, pathName: string) {
  if (!response.ok()) {
    throw new Error(`${pathName}: ${response.status()} ${await response.text()}`);
  }
}

async function apiGet<T>(request: APIRequestContext, pathName: string): Promise<T> {
  const response = await request.get(`${API_BASE}${pathName}`);
  await expectOk(response, pathName);
  return response.json() as Promise<T>;
}

async function apiPost<T>(
  request: APIRequestContext,
  pathName: string,
  data?: Record<string, unknown>
): Promise<T> {
  const response = await request.post(`${API_BASE}${pathName}`, {
    data,
    headers: mutationHeaders
  });
  await expectOk(response, pathName);
  return response.json() as Promise<T>;
}

async function setupDemo(request: APIRequestContext) {
  const health = await apiGet<{ status?: string }>(request, "/api/health");
  expect(health.status).toBe("ok");

  const ready = await apiGet<{ status?: string }>(request, "/api/ready");
  expect(ready.status).toBe("ready");

  await apiPost(request, "/api/auth/login", {
    username: "organizer.demo",
    password: "demo1234"
  });
  const seed = await apiPost<{ event_id: string }>(request, "/api/events/demo/seed");
  expect(seed.event_id).toBe(EVENT_ID);

  await apiPost(request, `/api/events/${EVENT_ID}/generate-plan`);
  await apiPost(request, `/api/events/${EVENT_ID}/plans/1/approve`);
  await apiPost(request, `/api/events/${EVENT_ID}/event-page/draft`);
  await apiPost(request, `/api/events/${EVENT_ID}/event-page/publish`);
  await apiPost(request, `/api/events/${EVENT_ID}/merchant-edge-packages/generate`);
}

async function readTouchedMetrics(request: APIRequestContext) {
  const payload = await apiGet<{ counters?: Record<string, number> }>(request, "/api/metrics");
  const counters = payload.counters ?? {};
  const required = [
    "health_checks_total",
    "public_touchpoint_interactions_total",
    "public_coupon_claims_total",
    "public_coupon_redemptions_total",
    "review_reports_total"
  ];
  const missing = required.filter((key) => !counters[key]);
  expect(missing, `missing browser gate metrics: ${missing.join(",")}`).toEqual([]);
  return counters;
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

async function expectForbiddenTermsAbsent(page: Page) {
  await expect(page.locator("body")).not.toContainText(forbiddenSurfaceTerms);
}

async function capture(page: Page, evidence: Evidence, step: string, fileName: string) {
  if (evidence.screenshots.length >= maxScreenshots) return;
  mkdirSync(screenshotDir, { recursive: true });
  const screenshotPath = path.join(screenshotDir, fileName);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  const bytes = statSync(screenshotPath).size;
  const sha256 = createHash("sha256").update(readFileSync(screenshotPath)).digest("hex");
  const viewport = page.viewportSize() ?? { width: 0, height: 0 };
  evidence.screenshots.push({
    file_name: fileName,
    step,
    viewport,
    bytes,
    sha256
  });
}

async function runPublicInteractions(page: Page) {
  const scanButton = page.getByRole("button", { name: "Scan spot" });
  const claimButton = page.getByRole("button", { name: "Claim offer" });
  const redeemButton = page.getByRole("button", { name: "Redeem offer" });

  await expect(scanButton).toBeEnabled();
  await scanButton.click();
  await expect(page.getByText("Spot scan recorded.")).toBeVisible();
  await expect(claimButton).toBeEnabled();
  await claimButton.click();
  await expect(page.getByText("Offer claimed.")).toBeVisible();
  await expect(redeemButton).toBeEnabled();
  await redeemButton.click();
  await expect(page.getByText("Offer redeemed.")).toBeVisible();
}

test("v2.6 browser release evidence gate runs against live FastAPI and Vite", async ({ page, request }) => {
  const evidence = createEvidence();
  const started = Date.now();

  try {
    await recordStep(evidence, "api health ready and demo setup", async () => {
      await setupDemo(request);
    }, "health_ready_seeded");

    await page.addInitScript(() => window.localStorage.setItem("zhiyin.locale", "en"));
    await page.setViewportSize({ width: 1440, height: 940 });

    await recordStep(evidence, "organizer event workspace", async () => {
      await loginThroughUi(page, "organizer.demo");
      await page.goto(`/organizer/events/${EVENT_ID}`);
      await expect(page.getByText("Visitor event page")).toBeVisible();
      await expect(page.getByText("Generate packs")).toBeVisible();
      await expect(page.getByText("Package for Merchant m001")).toBeVisible();
      await capture(page, evidence, "organizer event workspace", "01-organizer-workspace.png");
    }, "workspace_visible");

    await recordStep(evidence, "merchant package surface", async () => {
      await loginThroughUi(page, "merchant.m001.demo");
      await expect(page).toHaveURL(/\/merchant\/dashboard/);
      await expect(page.getByText("In-store touchpoints")).toBeVisible();
      await expect(page.getByText("Interaction pack")).toBeVisible();
      await expectForbiddenTermsAbsent(page);
      await capture(page, evidence, "merchant package surface", "02-merchant-package.png");
    }, "merchant_package_visible");

    await recordStep(evidence, "merchant sold-out status", async () => {
      await page.goto(`/merchant/events/${EVENT_ID}/status`);
      await page.getByRole("button", { name: "Report sold out" }).click();
      await expect(page.getByText("Organizer review requested.")).toBeVisible();
      await expectForbiddenTermsAbsent(page);
    }, "sold_out_reported");

    await recordStep(evidence, "organizer exception suggestions", async () => {
      await loginThroughUi(page, "organizer.demo");
      await page.goto(`/organizer/events/${EVENT_ID}/exceptions`);
      await expect(page.getByText(/sold out|inventory/i)).toBeVisible();
      await page.getByRole("button", { name: "Generate suggestions" }).click();
      await expect(page.getByText(/Pause visitor flow|Pause arrivals|visitor flow|merchant capacity/i).first()).toBeVisible();
      await capture(page, evidence, "organizer exception suggestions", "03-exception-suggestions.png");
    }, "exception_suggestion_visible");

    await recordStep(evidence, "public mobile scan claim redeem", async () => {
      await page.context().clearCookies();
      await page.setViewportSize({ width: 390, height: 844 });
      await page.goto(`/public/events/${EVENT_ID}`);
      await expect(page.getByText("Visitor event page")).toBeVisible();
      await runPublicInteractions(page);
      await expectForbiddenTermsAbsent(page);
      await capture(page, evidence, "public mobile scan claim redeem", "04-public-mobile.png");
    }, "scan_claim_redeem_visible");

    await recordStep(evidence, "organizer review page", async () => {
      await apiPost(request, `/api/events/${EVENT_ID}/review-report`);
      await page.setViewportSize({ width: 1440, height: 940 });
      await loginThroughUi(page, "organizer.demo");
      await page.goto(`/review/${EVENT_ID}`);
      await expect(page.getByText("Touchpoint summary")).toBeVisible();
      await expect(page.getByRole("heading", { name: "Merchant outcomes" })).toBeVisible();
      await expect(page.getByText("Total interactions", { exact: true })).toBeVisible();
      await capture(page, evidence, "organizer review page", "05-review-page.png");
    }, "review_visible");

    await recordStep(evidence, "metrics touched", async () => {
      evidence.metrics_observed = await readTouchedMetrics(request);
    }, "metrics_ready");

    evidence.status = "passed";
  } catch (error) {
    evidence.status = "failed";
    const failedStep = evidence.steps.find((step) => !step.ok);
    evidence.failure = {
      step: failedStep?.step,
      summary: sanitizeError(error)
    };
    throw error;
  } finally {
    writeEvidence(evidence, started);
  }
});
