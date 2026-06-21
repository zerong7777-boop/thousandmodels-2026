import { expect, type Page, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

type Role = "organizer" | "merchant" | null;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotDir = path.resolve(__dirname, "../../../../docs/research/assets/v1.2-event-page-merchant-edge");

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
    display_name: "Merchant Demo",
    merchant_id: "m001"
  }
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
    linked_merchants: ["m001"],
    visitor_task: "Try the heritage tea pairing.",
    rainy_day_score: 0.91,
    crowd_risk: "low",
    current_status: "active"
  }
];

const planVersion = {
  plan_id: "plan-v1",
  event_id: "demo-night-tour",
  version: 1,
  status: "approved",
  created_by: "agent",
  created_reason: "inventory incident recovery",
  route_points: routePoints,
  merchant_assignments: ["m001"],
  budget_plan: {},
  risk_plan: ["Keep indoor backup available"],
  diff_from_previous: ["Initial event page ready"]
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

function json(payload: unknown, status = 200) {
  return {
    status,
    contentType: "application/json",
    body: JSON.stringify(payload)
  };
}

function makeEventPage(status: "draft" | "published") {
  return {
    id: "ep-demo-night-tour-v1",
    event_id: "demo-night-tour",
    plan_version: 1,
    status,
    title: "Moonlit Heritage Walk",
    subtitle: "A live event page for stories, shops, and tonight's offers.",
    story_sections: [
      {
        title: "Lantern opening",
        body: "Start with the red facade story before visiting nearby shops."
      }
    ],
    route_highlights: [
      {
        name: "Old street story path",
        visitor_task: "Follow the story prompt and keep your event card ready."
      }
    ],
    merchant_highlights: [
      {
        name: "Merchant m001",
        highlight: "Show your event card for a tea pairing."
      }
    ],
    notices: [{ message: "Bring your event card." }],
    updated_at: "2026-06-12T10:00:00Z",
    published_at: status === "published" ? "2026-06-12T10:01:00Z" : null
  };
}

function makePackage() {
  return {
    id: "pkg-m001-v1",
    event_id: "demo-night-tour",
    merchant_id: "m001",
    plan_version: 1,
    status: "active",
    operator_brief: "Keep stamps ready at the counter.",
    visitor_pitch: "Show your event card for the tea pairing.",
    task_ids: ["task-m001-v1"],
    touchpoints: [
      {
        id: "tp-m001-qr",
        event_id: "demo-night-tour",
        merchant_id: "m001",
        package_id: "pkg-m001-v1",
        touchpoint_type: "in_shop_qr",
        label: "Counter QR",
        public_copy: "Scan at the counter to record your visit.",
        token: "counter-qr",
        status: "active",
        metrics: {},
        created_at: "2026-06-12T10:00:00Z"
      }
    ],
    coupon_rules: [
      {
        id: "coupon-m001-tea",
        event_id: "demo-night-tour",
        merchant_id: "m001",
        package_id: "pkg-m001-v1",
        title: "Tea pairing",
        description: "A visitor offer for this event page.",
        max_redemptions: 20,
        per_anonymous_interaction_limit: 1,
        status: "active",
        created_at: "2026-06-12T10:00:00Z"
      }
    ],
    evidence_refs: ["plan:demo-night-tour:v1", "task:task-m001-v1"],
    created_at: "2026-06-12T10:00:00Z",
    updated_at: "2026-06-12T10:00:00Z"
  };
}

async function useEnglish(page: Page) {
  await page.addInitScript(() => window.localStorage.setItem("zhiyin.locale", "en"));
}

async function snap(page: Page, fileName: string) {
  mkdirSync(screenshotDir, { recursive: true });
  await page.screenshot({ path: path.join(screenshotDir, fileName), fullPage: true });
}

async function mockApi(page: Page, roleRef: { current: Role }) {
  const state = {
    eventPage: null as ReturnType<typeof makeEventPage> | null,
    packages: [] as Array<ReturnType<typeof makePackage>>,
    runtime: {
      merchant_id: "m001",
      inventory_status: "normal",
      queue_status: "normal",
      available_for_visitors: true,
      temporary_note: "",
      updated_at: "2026-06-12T10:00:00Z"
    },
    incidents: [] as unknown[],
    suggestions: [] as unknown[],
    interactions: 0,
    claims: 0,
    redemptions: 0,
    anonymousInteractionId: "",
    redemptionId: ""
  };

  const workbench = () => ({
    merchant: {
      merchant_id: "m001",
      name: "Merchant m001"
    },
    runtime_state: state.runtime,
    tasks: [
      {
        task_id: "task-m001-v1",
        event_id: "demo-night-tour",
        merchant_id: "m001",
        plan_version: 1,
        role: "Heritage snack stop",
        time_slot: "19:00-20:00",
        visitor_task: "Prepare twenty tasting cards.",
        preparation_items: ["Queue marker", "Stamp card"],
        promo_text: "Tonight only heritage tasting",
        fallback_instruction: "Pause intake and notify organizer.",
        task_status: "active"
      }
    ],
    interaction_package: state.packages[0] ?? null,
    touchpoint_summary: { total_interactions: state.interactions },
    coupon_summary: { claims: state.claims, redemptions: state.redemptions }
  });

  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname;

    if (pathname === "/api/auth/me") {
      const role = roleRef.current;
      if (!role) {
        await route.fulfill(json({ detail: "not authenticated" }, 401));
        return;
      }
      await route.fulfill(json({ user: users[role] }));
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
            current_plan_version: 1,
            public_release_status: state.eventPage?.status === "published" ? "published" : "draft"
          }
        ])
      );
      return;
    }

    if (pathname === "/api/events/demo-night-tour/plans") {
      await route.fulfill(json([planVersion]));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-traces") {
      await route.fulfill(json([]));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-runs") {
      await route.fulfill(json([planningRun]));
      return;
    }

    if (pathname.includes("/api/events/demo-night-tour/agent-runs/")) {
      await route.fulfill(json([]));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/agent-drafts") {
      await route.fulfill(json([]));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/merchant-tasks") {
      await route.fulfill(json(workbench().tasks));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/event-page" && request.method() === "GET") {
      if (!state.eventPage) {
        await route.fulfill(json({ detail: "not found" }, 404));
        return;
      }
      await route.fulfill(json(state.eventPage));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/event-page/draft") {
      state.eventPage = makeEventPage("draft");
      await route.fulfill(json(state.eventPage));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/event-page/publish") {
      state.eventPage = makeEventPage("published");
      await route.fulfill(json(state.eventPage));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/merchant-edge-packages") {
      await route.fulfill(json({ packages: state.packages }));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/merchant-edge-packages/generate") {
      state.packages = [makePackage()];
      await route.fulfill(json({ packages: state.packages }));
      return;
    }

    if (pathname === "/api/merchants/m001/workbench") {
      await route.fulfill(json(workbench()));
      return;
    }

    if (pathname === "/api/merchants/m001/runtime-state") {
      state.runtime = {
        ...state.runtime,
        inventory_status: "sold_out",
        available_for_visitors: false,
        temporary_note: "Merchant reported sold out",
        updated_at: "2026-06-12T10:10:00Z"
      };
      state.incidents = [
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
          created_at: "2026-06-12T10:10:00Z"
        }
      ];
      await route.fulfill(json({ runtime_state: state.runtime, incident: state.incidents[0] }));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/incidents") {
      await route.fulfill(json(state.incidents));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/operation-suggestions") {
      await route.fulfill(json({ suggestions: state.suggestions }));
      return;
    }

    if (pathname === "/api/events/demo-night-tour/operation-suggestions/generate") {
      state.suggestions = [
        {
          id: "os-capacity-m001",
          event_id: "demo-night-tour",
          suggestion_type: "merchant_capacity",
          status: "pending_approval",
          title: "Pause arrivals to Merchant m001",
          rationale: "Merchant m001 reported sold out; keep visitors moving to indoor stops.",
          recommended_actions: [{ action: "pause_arrivals", merchant_id: "m001" }],
          impacted_merchants: ["m001"],
          impacted_route_points: ["rp001"],
          evidence_refs: ["incident:inc-inventory-m001", "metric:touchpoint_total"],
          created_at: "2026-06-12T10:11:00Z"
        }
      ];
      await route.fulfill(json({ suggestions: state.suggestions }));
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
          current_plan_version: 1,
          route: ["Rua da Felicidade", "Indoor tea stop"],
          marketing_content: ["Evening heritage walk"],
          notices: ["Bring your event card."],
          checkin_tasks: ["Collect the red facade stamp."],
          route_points: routePoints,
          event_page: state.eventPage,
          interaction_package: state.packages[0] ?? null,
          public_notices: [{ message: "Bring your event card.", publish_status: "published" }]
        })
      );
      return;
    }

    if (pathname === "/api/public/events/demo-night-tour/touchpoints/tp-m001-qr/interactions") {
      state.interactions += 1;
      state.anonymousInteractionId = "anon-v12";
      await route.fulfill(
        json({
          id: "interaction-v12",
          event_id: "demo-night-tour",
          touchpoint_id: "tp-m001-qr",
          merchant_id: "m001",
          interaction_type: "scan",
          source: "public-event-demo",
          anonymous_interaction_id: state.anonymousInteractionId,
          created_at: "2026-06-12T10:20:00Z",
          metadata: {}
        })
      );
      return;
    }

    if (pathname === "/api/public/events/demo-night-tour/coupons/coupon-m001-tea/claim") {
      state.claims += 1;
      state.redemptionId = "redemption-v12";
      await route.fulfill(
        json({
          id: state.redemptionId,
          event_id: "demo-night-tour",
          coupon_rule_id: "coupon-m001-tea",
          merchant_id: "m001",
          anonymous_interaction_id: state.anonymousInteractionId || "anon-v12",
          status: "claimed",
          claimed_at: "2026-06-12T10:21:00Z"
        })
      );
      return;
    }

    if (pathname === "/api/public/events/demo-night-tour/coupon-redemptions/redemption-v12/redeem") {
      state.redemptions += 1;
      await route.fulfill(
        json({
          id: "redemption-v12",
          event_id: "demo-night-tour",
          coupon_rule_id: "coupon-m001-tea",
          merchant_id: "m001",
          anonymous_interaction_id: state.anonymousInteractionId || "anon-v12",
          status: "redeemed",
          claimed_at: "2026-06-12T10:21:00Z",
          redeemed_at: "2026-06-12T10:22:00Z"
        })
      );
      return;
    }

    if (pathname === "/api/events/demo-night-tour/review-report") {
      await route.fulfill(
        json({
          event_id: "demo-night-tour",
          summary: "Event page interactions and merchant outcomes are ready for review.",
          lessons_learned: ["Event page visits stayed active", "Merchant offer conversion is measurable"],
          next_event_recommendations: ["Prepare backup staffing earlier"],
          touchpoint_summary: {
            total_interactions: state.interactions,
            coupon_claims: state.claims,
            coupon_redemptions: state.redemptions,
            redemption_rate: state.claims ? state.redemptions / state.claims : 0,
            by_type: { in_shop_qr: state.interactions, coupon: state.claims, redemption: state.redemptions },
            by_merchant: { m001: state.interactions }
          },
          merchant_outcomes: [
            {
              merchant_id: "m001",
              total_interactions: state.interactions,
              coupon_claims: state.claims,
              coupon_redemptions: state.redemptions,
              summary: "Merchant m001 produced measurable event-page offer activity."
            }
          ],
          extension_tasks: [
            {
              task_type: "merchant_follow_up",
              title: "Prepare next-night offer staffing",
              metric_refs: ["coupon_claims", "redemption_rate"],
              merchant_ids: ["m001"],
              rationale: "Use event-page offer activity to plan the next event window."
            }
          ]
        })
      );
      return;
    }

    await route.fulfill(json({ detail: `Unhandled mock route: ${pathname}` }, 404));
  });
}

test("v1.2 event page and merchant edge agent loop screenshots", async ({ page }) => {
  const roleRef: { current: Role } = { current: "organizer" };
  await page.setViewportSize({ width: 1440, height: 940 });
  await mockApi(page, roleRef);
  await useEnglish(page);

  await page.goto("/organizer/events/demo-night-tour");
  await page.getByRole("button", { name: "Draft event page" }).click();
  await expect(page.getByText("Moonlit Heritage Walk")).toBeVisible();
  await page.getByRole("button", { name: "Publish event page" }).click();
  await expect(page.getByText("published")).toBeVisible();
  await page.getByRole("button", { name: "Generate packs" }).click();
  await expect(page.getByText("Package for Merchant m001")).toBeVisible();
  await expect(page.getByText("plan:demo-night-tour:v1", { exact: true })).toBeVisible();
  await snap(page, "01-organizer-event-page-status.png");

  roleRef.current = "merchant";
  await page.goto("/merchant/dashboard");
  await expect(page.getByText("In-store touchpoints")).toBeVisible();
  await expect(page.getByText("Counter QR")).toBeVisible();
  await expect(page.getByText("Tea pairing", { exact: true })).toBeVisible();
  await snap(page, "02-merchant-edge-package.png");

  await page.goto("/merchant/events/demo-night-tour/status");
  await page.getByRole("button", { name: "Report sold out" }).click();
  await expect(page.getByText("Organizer review requested.")).toBeVisible();

  roleRef.current = "organizer";
  await page.goto("/organizer/events/demo-night-tour/exceptions");
  await expect(page.getByText("Merchant m001 reported sold out.")).toBeVisible();
  await page.getByRole("button", { name: "Generate suggestions" }).click();
  await expect(page.getByText("Pause arrivals to Merchant m001")).toBeVisible();
  await expect(page.getByText("2 evidence items")).toBeVisible();
  await snap(page, "04-exception-operation-suggestion.png");

  roleRef.current = null;
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/public/events/demo-night-tour");
  await expect(page.getByText("Visitor event page")).toBeVisible();
  await expect(page.getByText("Moonlit Heritage Walk")).toBeVisible();
  await page.getByRole("button", { name: "Scan spot" }).click();
  await expect(page.getByText("Spot scan recorded.")).toBeVisible();
  await page.getByRole("button", { name: "Claim offer" }).click();
  await expect(page.getByText("Offer claimed.")).toBeVisible();
  await page.getByRole("button", { name: "Redeem offer" }).click();
  await expect(page.getByText("Offer redeemed.")).toBeVisible();
  await expect(page.getByText(/AgentDraft|AgentRun|PlanVersion|RecoveryProposal|qwen|dashscope|schema_failed|approval_status/i)).toHaveCount(0);
  await snap(page, "03-public-event-page-mobile.png");

  roleRef.current = "organizer";
  await page.setViewportSize({ width: 1440, height: 940 });
  await page.goto("/review/demo-night-tour");
  await expect(page.getByText("Touchpoint summary")).toBeVisible();
  await expect(page.getByText("Total interactions", { exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Merchant outcomes" })).toBeVisible();
  await expect(page.getByText("Prepare next-night offer staffing")).toBeVisible();
  await snap(page, "05-review-touchpoint-summary.png");
});
