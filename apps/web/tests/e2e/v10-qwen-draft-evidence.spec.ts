import { expect, type Page, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

type DemoRole = "organizer" | null;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotDir = path.resolve(__dirname, "../../../../docs/research/assets/v1.0-qwen-controlled-draft");

const organizerUser = {
  user_id: "usr_org_demo",
  username: "organizer.demo",
  role: "organizer",
  display_name: "Organizer Demo",
  merchant_id: null
};

const recoveryRun = {
  run_id: "run_demo-night-tour_recovery",
  event_id: "demo-night-tour",
  trigger: "incident_recovery",
  mode: "qwen_draft",
  status: "fallback_completed",
  started_at: "2026-06-12T10:00:00Z",
  completed_at: "2026-06-12T10:00:01Z",
  fallback_used: true,
  fallback_reason: "schema_failed",
  final_output_ref: "draft:draft_notice_001",
  error_summary: null
};

const reviewRun = {
  run_id: "run_demo-night-tour_review",
  event_id: "demo-night-tour",
  trigger: "review_generation",
  mode: "qwen_draft",
  status: "completed",
  started_at: "2026-06-12T10:05:00Z",
  completed_at: "2026-06-12T10:05:01Z",
  fallback_used: false,
  fallback_reason: null,
  final_output_ref: "draft:draft_review_001",
  error_summary: null
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
    story: "A sheltered stop used after the route update.",
    linked_merchants: ["m002"],
    visitor_task: "Try the heritage tea pairing.",
    rainy_day_score: 0.91,
    crowd_risk: "low",
    current_status: "active"
  }
];

const drafts = [
  {
    draft_id: "draft_recovery_001",
    event_id: "demo-night-tour",
    source_run_id: recoveryRun.run_id,
    draft_type: "recovery_explanation",
    locale: "en",
    content: "Pause the sold-out merchant stop and guide visitors to the indoor tea stop.",
    structured_payload: { affected_merchants: ["m001"], requires_organizer_approval: true },
    status: "draft",
    reviewed_by: null,
    reviewed_at: null,
    created_at: "2026-06-12T10:00:01Z"
  },
  {
    draft_id: "draft_notice_001",
    event_id: "demo-night-tour",
    source_run_id: recoveryRun.run_id,
    draft_type: "public_notice",
    locale: "en",
    content: "Please continue to the indoor tea stop. Your route has been updated.",
    structured_payload: { public_copy_ready: true, requires_organizer_approval: true },
    status: "draft",
    reviewed_by: null,
    reviewed_at: null,
    created_at: "2026-06-12T10:00:01Z"
  },
  {
    draft_id: "draft_review_001",
    event_id: "demo-night-tour",
    source_run_id: reviewRun.run_id,
    draft_type: "review_summary",
    locale: "mixed",
    content: "Evidence: H5 visits 428, check-ins 136, one recovery approval. Recommendation: add a backup stop.",
    structured_payload: {
      metrics: ["h5_visits", "checkins"],
      incidents: ["inc_inventory_m001"],
      public_notices: ["notice-v2"],
      recovery_proposals: ["proposal-inc_inventory_m001"]
    },
    status: "draft",
    reviewed_by: null,
    reviewed_at: null,
    created_at: "2026-06-12T10:05:01Z"
  }
];

const modelCallsByRun = {
  [recoveryRun.run_id]: [
    {
      model_call_id: "model_recovery_notice_001",
      run_id: recoveryRun.run_id,
      provider: "dashscope",
      model: "qwen-plus",
      prompt_template_id: "qwen_public_notice_v1",
      input_refs: ["incident:inc_inventory_m001", "proposal:proposal-inc_inventory_m001"],
      response_status: "schema_failed",
      parsed_output: null,
      fallback_used: true,
      error_summary: "Candidate included fields outside the controlled draft schema.",
      created_at: "2026-06-12T10:00:01Z"
    }
  ],
  [reviewRun.run_id]: [
    {
      model_call_id: "model_review_001",
      run_id: reviewRun.run_id,
      provider: "dashscope",
      model: "qwen-plus",
      prompt_template_id: "qwen_review_summary_v1",
      input_refs: ["metrics", "incidents", "public_notices", "recovery_proposals"],
      response_status: "success",
      parsed_output: { evidence_refs: ["metric:h5_visits", "incident:inc_inventory_m001"] },
      fallback_used: false,
      error_summary: null,
      created_at: "2026-06-12T10:05:01Z"
    }
  ]
} as const;

const evaluationsByRun = {
  [recoveryRun.run_id]: [
    {
      evaluation_id: "eval_recovery_notice_001",
      run_id: recoveryRun.run_id,
      schema_pass: false,
      fallback_used: true,
      unsafe_mutation_attempted: false,
      human_approval_required: true,
      forbidden_public_terms_present: false,
      public_copy_ready: true,
      notes: ["Schema validation failed; deterministic fallback draft was used before organizer review."]
    }
  ],
  [reviewRun.run_id]: [
    {
      evaluation_id: "eval_review_001",
      run_id: reviewRun.run_id,
      schema_pass: true,
      fallback_used: false,
      unsafe_mutation_attempted: false,
      human_approval_required: true,
      forbidden_public_terms_present: false,
      public_copy_ready: true,
      notes: ["Review summary references existing metrics and incident evidence."]
    }
  ]
} as const;

function json(payload: unknown, status = 200) {
  return {
    status,
    contentType: "application/json",
    body: JSON.stringify(payload)
  };
}

async function mockApi(page: Page, role: DemoRole) {
  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname;

    if (pathname === "/api/auth/me") {
      if (!role) {
        await route.fulfill(json({ detail: "not authenticated" }, 401));
        return;
      }
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
      await route.fulfill(json([recoveryRun, reviewRun]));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-drafts") {
      const draftType = url.searchParams.get("draft_type");
      await route.fulfill(json(draftType ? drafts.filter((draft) => draft.draft_type === draftType) : drafts));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/tool-calls")) {
      await route.fulfill(json([]));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/model-calls")) {
      const pathParts = pathname.split("/");
      const runId = pathParts[pathParts.length - 2] ?? "";
      await route.fulfill(json(modelCallsByRun[runId as keyof typeof modelCallsByRun] ?? []));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/evaluations")) {
      const pathParts = pathname.split("/");
      const runId = pathParts[pathParts.length - 2] ?? "";
      await route.fulfill(json(evaluationsByRun[runId as keyof typeof evaluationsByRun] ?? []));
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
            trigger_detail: "Merchant m001 reported sold out.",
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
          summary: "H5 visits 428; recovery confirmation reduced confused arrivals.",
          route_result: "Route v2 kept the visitor flow active.",
          merchant_result: "Merchant tasks were updated after the exception.",
          incident_summary: "One inventory exception was approved into a recovered route.",
          agent_actions: ["Generated initial route", "Generated recovery suggestion"],
          human_approvals: ["Approved route v1", "Approved recovery route v2"],
          lessons_learned: ["H5 visits 428", "Check-ins 136", "Response time 4 min"],
          next_event_recommendations: ["Reduce sold-out merchant routing weight", "Add one more sheltered stop"]
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

test("v1.0 exception center shows organizer-only Qwen draft evidence", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, "organizer");
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour/exceptions");
  await expect(page.getByText("Model draft evidence")).toBeVisible();
  await expect(page.getByText("qwen-plus")).toBeVisible();
  await expect(page.getByText(/schema_failed|success|skipped/)).toBeVisible();
  await snap(page, "01-exception-model-evidence.png");
});

test("v1.0 review center shows model draft evidence beside metric-backed review", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, "organizer");
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour/review");
  await expect(page.getByText("Model draft evidence")).toBeVisible();
  await expect(page.getByText("qwen-plus")).toBeVisible();
  await expect(page.getByText(/schema_failed|success|skipped/)).toBeVisible();
  await snap(page, "02-review-model-evidence.png");
});

test("v1.0 public H5 remains visitor-safe without model evidence terms", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockApi(page, null);
  await useEnglish(page);
  await page.goto("/public/events/demo-night-tour");
  await expect(page.getByText("Tonight's route")).toBeVisible();
  await expect(page.getByText(/Qwen|AgentModelCall|fallback|schema|backend/i)).toHaveCount(0);
  await snap(page, "03-public-h5-no-model-terms.png");
});
