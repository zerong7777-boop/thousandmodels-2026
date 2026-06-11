import { expect, type Page, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

test.skip(true, "v0.4 visual baseline is historical; v0.5 visual smoke is the active screenshot suite.");

type DemoRole = "organizer" | "merchant" | "tourist" | null;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotDir = path.resolve(__dirname, "../../../../docs/research/assets/v0.4-verification");

const users = {
  organizer: {
    user_id: "usr_org_demo",
    username: "organizer.demo",
    role: "organizer",
    display_name: "Organizer Demo",
    merchant_id: null
  },
  merchant: {
    user_id: "usr_merchant_m001_demo",
    username: "merchant.m001.demo",
    role: "merchant",
    display_name: "Merchant m001",
    merchant_id: "m001"
  },
  tourist: {
    user_id: "usr_tourist_demo",
    username: "tourist.demo",
    role: "tourist",
    display_name: "Tourist Demo",
    merchant_id: null
  }
} as const;

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
      await route.fulfill(json({ user: users[role] }));
      return;
    }

    if (pathname === "/api/auth/login") {
      const body = request.postDataJSON() as { username?: string };
      const nextRole =
        body.username === "merchant.m001.demo"
          ? "merchant"
          : body.username === "tourist.demo"
            ? "tourist"
            : "organizer";
      await route.fulfill(json({ user: users[nextRole] }));
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
            diff_from_previous: ["Pause sold-out stop", "Add indoor tea stop"],
            approved_by: "organizer.demo",
            approved_at: "2026-06-10T12:00:00Z"
          }
        ])
      );
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-traces") {
      await route.fulfill(
        json([
          {
            trace_id: "trace-plan-v2",
            event_id: "demo-night-tour",
            trigger: "Merchant inventory incident",
            steps: Array.from({ length: 5 }, (_, index) => ({
              agent_name: `deterministic-step-${index + 1}`,
              input_refs: ["runtime_state", "plan_v1"],
              tool_calls: [],
              structured_output: { step: index + 1 },
              decision_reason: "Rule-based route recovery evidence.",
              confidence: 0.9,
              requires_human_approval: index === 4
            })),
            final_output_ref: "plan-v2",
            human_decision_ref: "approval-v2"
          }
        ])
      );
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
            incident_id: "inc-inventory-m001",
            event_id: "demo-night-tour",
            type: "inventory",
            severity: "high",
            source: "merchant",
            trigger_detail: "Merchant m001 reported sold out.",
            affected_route_points: ["rp001"],
            affected_merchants: ["m001"],
            status: "proposal_ready",
            created_at: "2026-06-10T12:05:00Z"
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
          merchant_result: "Merchant tasks were updated after the incident.",
          incident_summary: "One inventory incident was approved into Plan v2.",
          agent_actions: ["Generated Plan v1", "Generated recovery proposal"],
          human_approvals: ["Approved Plan v1", "Approved recovery proposal"],
          lessons_learned: ["Inventory telemetry needs earlier merchant prompts."],
          next_event_recommendations: ["Pre-stage an indoor backup stop."]
        })
      );
      return;
    }

    if (pathname === "/api/merchants/m001/workbench") {
      await route.fulfill(
        json({
          merchant: { merchant_id: "m001", name: "Merchant m001", type: "food" },
          runtime_state: {
            merchant_id: "m001",
            inventory_status: "normal",
            queue_status: "normal",
            available_for_visitors: true,
            temporary_note: "",
            updated_at: "2026-06-10T12:00:00Z"
          },
          tasks: [merchantTask]
        })
      );
      return;
    }

    if (pathname === "/api/merchants/m001/runtime-state") {
      await route.fulfill(
        json({
          merchant_id: "m001",
          inventory_status: "sold_out",
          queue_status: "normal",
          available_for_visitors: false,
          temporary_note: "Sold out",
          updated_at: "2026-06-10T12:10:00Z",
          incident: {
            incident_id: "inc-inventory-m001",
            event_id: "demo-night-tour",
            type: "inventory",
            severity: "high",
            source: "merchant",
            trigger_detail: "Merchant m001 reported sold out.",
            affected_route_points: ["rp001"],
            affected_merchants: ["m001"],
            status: "open",
            created_at: "2026-06-10T12:10:00Z"
          }
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
          notices: ["Route v2 is active."],
          checkin_tasks: ["Collect the red facade stamp."],
          route_points: routePoints,
          public_notices: [
            {
              notice_id: "notice-v2",
              event_id: "demo-night-tour",
              plan_version: 2,
              audience: "tourist",
              message: "Plan v2 is active. Please continue to the indoor tea stop.",
              reason: "Inventory recovery",
              publish_status: "published",
              published_at: "2026-06-10T12:15:00Z"
            }
          ]
        })
      );
      return;
    }

    await route.fulfill(json({ detail: `Unhandled mock route: ${pathname}` }, 404));
  });
}

async function snap(page: Page, fileName: string) {
  mkdirSync(screenshotDir, { recursive: true });
  await page.screenshot({ path: path.join(screenshotDir, fileName), fullPage: true });
}

test("login can authenticate a demo organizer account", async ({ page }) => {
  await mockApi(page, null);
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Zhiyin Haojiang Sign In" })).toBeVisible();
  await snap(page, "01-login.png");

  await page.getByRole("button", { name: /Organizer demo/i }).first().click();
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/organizer\/dashboard$/);
  await expect(page.getByTestId("organizer-shell")).toBeVisible();
});

test("organizer product routes render dashboard workspace exceptions and review", async ({ page }) => {
  await mockApi(page, "organizer");
  await page.goto("/organizer/dashboard");
  await expect(page.getByTestId("organizer-shell")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Historic district night tour" })).toBeVisible();
  await snap(page, "02-organizer-dashboard.png");

  await page.goto("/organizer/events/demo-night-tour");
  await expect(page.getByRole("heading", { name: "Route plan and execution readiness" })).toBeVisible();
  await expect(page.getByText("Plan v2")).toBeVisible();
  await snap(page, "03-organizer-workspace.png");

  await page.goto("/organizer/events/demo-night-tour/exceptions");
  await expect(page.getByRole("heading", { name: "Recovery suggestions" })).toBeVisible();
  await expect(page.getByText("Merchant m001 reported sold out.")).toBeVisible();
  await snap(page, "04-organizer-exceptions.png");

  await page.goto("/organizer/events/demo-night-tour/review");
  await expect(page.getByRole("heading", { name: "Metric-backed review report" })).toBeVisible();
  await expect(page.getByText(/H5 visits 428/i)).toBeVisible();
  await snap(page, "05-organizer-review.png");
});

test("merchant status route is a standalone mobile workbench", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockApi(page, "merchant");
  await page.goto("/merchant/events/demo-night-tour/status");
  await expect(page.getByTestId("merchant-shell")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Visitor readiness" })).toBeVisible();
  await page.getByRole("button", { name: "Report sold out" }).click();
  await expect(page.getByText("Organizer review was requested.")).toBeVisible();
  await snap(page, "06-merchant-status-mobile.png");
});

test("tourist route and public projection render as mobile experiences", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await mockApi(page, "tourist");
  await page.goto("/user/events/demo-night-tour/route");
  await expect(page.getByTestId("user-shell")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Story stops" })).toBeVisible();
  await expect(page.getByText("Collect the red facade stamp.")).toBeVisible();
  await snap(page, "07-tourist-route-mobile.png");

  await mockApi(page, null);
  await page.goto("/public/events/demo-night-tour");
  await expect(page.getByRole("heading", { name: "Historic District Night Tour" })).toBeVisible();
  await expect(page.getByText("Plan v2 is active. Please continue to the indoor tea stop.")).toBeVisible();
  await snap(page, "08-public-h5-mobile.png");
});
