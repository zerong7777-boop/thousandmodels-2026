import { expect, type Page, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

type DemoRole = "organizer" | null;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotDir = path.resolve(__dirname, "../../../../docs/research/assets/v0.9-agent-evidence");

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
    story: "A sheltered stop used after the recovery plan.",
    linked_merchants: ["m002"],
    visitor_task: "Try the heritage tea pairing.",
    rainy_day_score: 0.91,
    crowd_risk: "low",
    current_status: "active"
  }
];

const merchantTask = {
  task_id: "task-m001-v2",
  event_id: "demo-night-tour",
  merchant_id: "m001",
  plan_version: 2,
  role: "Heritage snack stop",
  time_slot: "19:00-20:00",
  visitor_task: "Prepare twenty tasting cards.",
  preparation_items: ["Queue marker", "Stamp card"],
  promo_text: "Tonight only heritage tasting",
  fallback_instruction: "Pause intake and notify organizer.",
  task_status: "active"
};

const planningRun = {
  run_id: "run_demo-night-tour_planning",
  event_id: "demo-night-tour",
  trigger: "planning_generation",
  mode: "deterministic",
  status: "completed",
  started_at: "2026-06-12T10:00:00Z",
  completed_at: "2026-06-12T10:00:01Z",
  fallback_used: false,
  fallback_reason: null,
  final_output_ref: "plan:demo-night-tour:v1",
  error_summary: null
};

const recoveryRun = {
  ...planningRun,
  run_id: "run_demo-night-tour_recovery",
  trigger: "incident_recovery",
  final_output_ref: "draft:draft_notice_001"
};

const reviewRun = {
  ...planningRun,
  run_id: "run_demo-night-tour_review",
  trigger: "review_generation",
  final_output_ref: "draft:draft_review_001"
};

const planningTrace = {
  trace_id: "trace-v1",
  event_id: "demo-night-tour",
  trigger: "planning_generation",
  steps: [
    "CoordinatorAgent",
    "CulturalNarrativeAgent",
    "RoutePlanningAgent",
    "MerchantMatchingAgent",
    "RiskRecoveryAgent",
    "PublicNoticeAgent"
  ].map((agentName, index) => ({
    step_id: `step_${index + 1}`,
    run_id: planningRun.run_id,
    agent_name: agentName,
    objective: `${agentName} objective`,
    input_refs: ["event_brief:demo-night-tour"],
    tool_calls: [],
    tool_call_refs: index === 2 ? ["tool_route_001"] : [],
    structured_output: { step: index + 1 },
    decision_reason: `${agentName} produced deterministic evidence.`,
    confidence: 0.88,
    requires_human_approval: agentName === "PublicNoticeAgent",
    schema_name: "AgentStep",
    validation_status: "passed"
  })),
  final_output_ref: "plan:demo-night-tour:v1",
  human_decision_ref: null
};

const toolCalls = {
  [planningRun.run_id]: [
    {
      tool_call_id: "tool_route_001",
      run_id: planningRun.run_id,
      step_id: "step_3",
      tool_name: "route.build_static_route",
      input_payload: { rainy: false },
      output_payload: { route_count: 6 },
      status: "success",
      latency_ms: 0,
      error_summary: null
    },
    {
      tool_call_id: "tool_merchant_001",
      run_id: planningRun.run_id,
      step_id: "step_4",
      tool_name: "merchant.select_night_merchants",
      input_payload: { event_id: "demo-night-tour" },
      output_payload: { selected: ["m001"] },
      status: "success",
      latency_ms: 0,
      error_summary: null
    }
  ],
  [recoveryRun.run_id]: [
    {
      tool_call_id: "tool_recovery_001",
      run_id: recoveryRun.run_id,
      step_id: "step_recovery",
      tool_name: "recovery.build_recovery_proposal",
      input_payload: { incident_id: "inc_inventory_m001" },
      output_payload: { recommended_changes: ["Pause sold-out stop"] },
      status: "success",
      latency_ms: 0,
      error_summary: null
    }
  ],
  [reviewRun.run_id]: []
} as const;

const drafts = [
  {
    draft_id: "draft_recovery_001",
    event_id: "demo-night-tour",
    source_run_id: recoveryRun.run_id,
    draft_type: "recovery_explanation",
    locale: "zh-Hans",
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
    locale: "zh-Hans",
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
    content: "Evidence: metrics=h5_visits, incidents=inc_inventory_m001. Recommendation: add backup stop.",
    structured_payload: {
      metrics: ["h5_visits", "checkins"],
      incidents: ["inc_inventory_m001"],
      public_notices: ["notice-v2"],
      recovery_proposals: ["proposal-inc_inventory_m001"]
    },
    status: "draft",
    reviewed_by: null,
    reviewed_at: null,
    created_at: "2026-06-12T10:00:01Z"
  }
];

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

    if (pathname === "/api/events/demo-night-tour/plans") {
      await route.fulfill(
        json([
          {
            plan_id: "plan-v2",
            event_id: "demo-night-tour",
            version: 2,
            status: "approved",
            created_by: "agent",
            created_reason: "inventory incident recovery",
            route_points: routePoints,
            merchant_assignments: ["m001", "m002"],
            budget_plan: {},
            risk_plan: ["Avoid overloaded merchant"],
            diff_from_previous: ["Pause sold-out stop", "Add indoor tea stop"]
          }
        ])
      );
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-traces") {
      await route.fulfill(json([planningTrace]));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-runs") {
      await route.fulfill(json([planningRun, recoveryRun, reviewRun]));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/") && pathname.endsWith("/tool-calls")) {
      const runId = pathname.split("/").at(-2) ?? "";
      await route.fulfill(json(toolCalls[runId as keyof typeof toolCalls] ?? []));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-drafts") {
      const draftType = url.searchParams.get("draft_type");
      await route.fulfill(json(draftType ? drafts.filter((draft) => draft.draft_type === draftType) : drafts));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/merchant-tasks") {
      await route.fulfill(json([merchantTask]));
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

test("v0.9 organizer workspace Agent evidence screenshot", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, "organizer");
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour");
  await expect(page.getByText("Planning Agent evidence")).toBeVisible();
  await expect(page.getByText("RoutePlanningAgent", { exact: true })).toBeVisible();
  await expect(page.getByText("route.build_static_route")).toBeVisible();
  await snap(page, "01-organizer-workspace-agent-evidence.png");
});

test("v0.9 organizer exception Agent drafts screenshot", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, "organizer");
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour/exceptions");
  await expect(page.getByText("Recovery Agent evidence")).toBeVisible();
  await expect(page.getByText("Recovery explanation draft")).toBeVisible();
  await expect(page.getByText("Public notice draft")).toBeVisible();
  await snap(page, "02-organizer-exception-agent-drafts.png");
});

test("v0.9 organizer review Agent evidence screenshot", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await mockApi(page, "organizer");
  await useEnglish(page);
  await page.goto("/organizer/events/demo-night-tour/review");
  await expect(page.getByText("Review Agent evidence")).toBeVisible();
  await expect(page.getByText("Review summary draft")).toBeVisible();
  await snap(page, "03-organizer-review-agent-evidence.png");
});

test("v0.9 public H5 does not expose Agent internals", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockApi(page, null);
  await useEnglish(page);
  await page.goto("/public/events/demo-night-tour");
  await expect(page.getByText("Tonight's route")).toBeVisible();
  await expect(page.getByText(/AgentRun|AgentDraft|Qwen|fallback|schema|backend/i)).toHaveCount(0);
  await snap(page, "04-public-h5-no-agent-leakage-mobile.png");
});
