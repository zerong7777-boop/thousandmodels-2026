import { expect, type Page, test } from "@playwright/test";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../../..");
const resultPath = path.join(
  repoRoot,
  "docs/research/assets/v1.1-live-qwen-smoke/live-qwen-smoke-result.json"
);
const screenshotDir = path.join(repoRoot, "docs/research/assets/v1.1-live-qwen-smoke");

type LiveSmokeResult = {
  outcome: string;
  recovery: {
    run: Record<string, unknown>;
    model_calls: Array<Record<string, unknown>>;
    evaluations: Array<Record<string, unknown>>;
    drafts: Array<Record<string, unknown>>;
  };
  review: {
    run: Record<string, unknown>;
    model_calls: Array<Record<string, unknown>>;
    evaluations: Array<Record<string, unknown>>;
    drafts: Array<Record<string, unknown>>;
  };
};

function loadResult(): LiveSmokeResult | null {
  if (!existsSync(resultPath)) {
    return null;
  }
  return JSON.parse(readFileSync(resultPath, "utf8")) as LiveSmokeResult;
}

const liveResult = loadResult();

const organizerUser = {
  user_id: "usr_org_demo",
  username: "organizer.demo",
  role: "organizer",
  display_name: "Organizer Demo",
  merchant_id: null
};

const routePoints = [
  {
    point_id: "rp001",
    name: "Rua da Felicidade",
    type: "heritage",
    is_indoor: false,
    estimated_stay_minutes: 18,
    story: "A restored street story linking old shops and evening foot traffic.",
    linked_merchants: ["m001"],
    visitor_task: "Collect the red facade stamp.",
    rainy_day_score: 0.62,
    crowd_risk: "medium",
    current_status: "active"
  },
  {
    point_id: "rp002",
    name: "Indoor tea stop",
    type: "merchant",
    is_indoor: true,
    estimated_stay_minutes: 20,
    story: "A sheltered stop used after the live recovery smoke.",
    linked_merchants: ["m002"],
    visitor_task: "Try the heritage tea pairing.",
    rainy_day_score: 0.91,
    crowd_risk: "low",
    current_status: "active"
  }
];

function json(payload: unknown, status = 200) {
  return {
    status,
    contentType: "application/json",
    body: JSON.stringify(payload)
  };
}

function draftFromSmoke(draft: Record<string, unknown>, index: number) {
  return {
    draft_id: String(draft.draft_id ?? `live_draft_${index}`),
    event_id: "demo-night-tour",
    source_run_id: String(draft.source_run_id ?? ""),
    draft_type: String(draft.draft_type ?? "public_notice"),
    locale: String(draft.locale ?? "en"),
    content: String(draft.content_preview ?? "Live smoke controlled draft evidence."),
    structured_payload: { source: "v1.1_live_smoke_sanitized" },
    status: String(draft.status ?? "draft"),
    reviewed_by: null,
    reviewed_at: null,
    created_at: "2026-06-12T10:00:00Z"
  };
}

async function mockApi(page: Page, result: LiveSmokeResult) {
  const runs = [result.recovery.run, result.review.run].filter((run) => run.run_id);
  const drafts = [...result.recovery.drafts, ...result.review.drafts].map(draftFromSmoke);
  const modelCallsByRun = new Map<string, Array<Record<string, unknown>>>([
    [String(result.recovery.run.run_id ?? ""), result.recovery.model_calls],
    [String(result.review.run.run_id ?? ""), result.review.model_calls]
  ]);
  const evaluationsByRun = new Map<string, Array<Record<string, unknown>>>([
    [String(result.recovery.run.run_id ?? ""), result.recovery.evaluations],
    [String(result.review.run.run_id ?? ""), result.review.evaluations]
  ]);

  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    const pathname = url.pathname;

    if (pathname === "/api/auth/me") {
      await route.fulfill(json({ user: organizerUser }));
      return;
    }

    if (pathname === "/api/events") {
      await route.fulfill(
        json([
          {
            event_id: "demo-night-tour",
            title: "Historic District Night Tour",
            area: "Rua da Felicidade",
            date: "2026-07-18",
            time_window: "18:00-21:30",
            status: "active",
            current_plan_version: 2,
            public_release_status: "published"
          }
        ])
      );
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-runs") {
      await route.fulfill(json(runs));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-drafts") {
      const draftType = url.searchParams.get("draft_type");
      await route.fulfill(
        json(draftType ? drafts.filter((draft) => draft.draft_type === draftType) : drafts)
      );
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/tool-calls")) {
      await route.fulfill(json([]));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/model-calls")) {
      const pathParts = pathname.split("/");
      const runId = pathParts[pathParts.length - 2] ?? "";
      await route.fulfill(json(modelCallsByRun.get(runId) ?? []));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/evaluations")) {
      const pathParts = pathname.split("/");
      const runId = pathParts[pathParts.length - 2] ?? "";
      await route.fulfill(json(evaluationsByRun.get(runId) ?? []));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/incidents") {
      await route.fulfill(
        json([
          {
            incident_id: "inc_inventory_m001",
            event_id: "demo-night-tour",
            type: "inventory",
            severity: "high",
            source: "merchant",
            trigger_detail: "Live smoke merchant sold-out signal.",
            affected_route_points: ["rp001"],
            affected_merchants: ["m001"],
            status: "proposal_ready",
            created_at: "2026-06-12T10:00:01Z"
          }
        ])
      );
      return;
    }

    if (pathname === "/api/events/demo-night-tour/review-report") {
      await route.fulfill(
        json({
          event_id: "demo-night-tour",
          summary: "Live smoke review evidence generated from the v1.1 sanitized result.",
          route_result: "Route v2 kept the visitor flow active.",
          merchant_result: "Merchant tasks were updated after the exception.",
          incident_summary: "One inventory exception was approved into a recovered route.",
          agent_actions: ["Generated controlled draft evidence"],
          human_approvals: ["Organizer approval remains required"],
          lessons_learned: ["H5 visits 428", "Check-ins 136", "Response time 4 min"],
          next_event_recommendations: ["Keep backup stop readiness visible"]
        })
      );
      return;
    }

    if (pathname === "/api/public/events/demo-night-tour") {
      await route.fulfill(
        json({
          event_id: "demo-night-tour",
          theme: "Historic District Night Tour",
          title: "Historic District Night Tour",
          area: "Rua da Felicidade",
          status: "active",
          current_plan_version: 2,
          route: ["Rua da Felicidade", "Indoor tea stop"],
          marketing_content: ["Evening heritage walk"],
          notices: ["Please continue to the indoor tea stop."],
          checkin_tasks: ["Collect the red facade stamp."],
          route_points: routePoints,
          public_notices: [
            {
              notice_id: "notice-v2",
              event_id: "demo-night-tour",
              plan_version: 2,
              audience: "tourist",
              message: "Please continue to the indoor tea stop.",
              publish_status: "published"
            }
          ]
        })
      );
      return;
    }

    await route.fulfill(json({ detail: `Unhandled mock route: ${pathname}` }, 404));
  });
}

async function useEnglish(page: Page) {
  await page.addInitScript(() => window.localStorage.setItem("zhiyin.locale", "en"));
}

async function snap(page: Page, fileName: string) {
  mkdirSync(screenshotDir, { recursive: true });
  await page.screenshot({ path: path.join(screenshotDir, fileName), fullPage: true });
}

test("v1.1 live smoke exception model evidence screenshot", async ({ page }) => {
  test.skip(!liveResult || liveResult.outcome !== "live_success", "No live success evidence to screenshot.");
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, liveResult);
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour/exceptions");
  await expect(page.getByText("Model draft evidence")).toBeVisible();
  await expect(page.getByText("dashscope")).toBeVisible();
  await snap(page, "01-live-exception-model-evidence.png");
});

test("v1.1 live smoke review model evidence screenshot", async ({ page }) => {
  test.skip(!liveResult || liveResult.outcome !== "live_success", "No live success evidence to screenshot.");
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, liveResult);
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour/review");
  await expect(page.getByText("Model draft evidence")).toBeVisible();
  await expect(page.getByText("dashscope")).toBeVisible();
  await snap(page, "02-live-review-model-evidence.png");
});
