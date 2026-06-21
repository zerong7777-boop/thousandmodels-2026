import { afterEach, describe, expect, test, vi } from "vitest";
import { api } from "../src/api";
import type {
  CouponRedemption,
  EventPage,
  MerchantEdgePackagesResponse,
  OperationSuggestionsResponse,
  TouchpointInteraction
} from "../src/types";
import { jsonResponse } from "./authTestUtils";

const mutationOptions = (body?: unknown) => ({
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json", "X-Zhiyin-CSRF": "demo" },
  ...(body === undefined ? {} : { body: JSON.stringify(body) })
});

describe("v1.2 event interaction API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("event page draft publish and read use v1.2 routes", async () => {
    const page: EventPage = {
      id: "ep-demo-night-tour-v1",
      event_id: "demo-night-tour",
      plan_version: 1,
      status: "draft",
      title: "Historic District Night Tour",
      subtitle: "Story route",
      story_sections: [],
      route_highlights: [],
      merchant_highlights: [],
      notices: [],
      generated_from_run_id: null,
      published_at: null,
      updated_at: "2026-06-17T10:00:00Z"
    };
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(page)));
    vi.stubGlobal("fetch", fetchSpy);

    await api.draftEventPage("demo-night-tour");
    await api.publishEventPage("demo-night-tour");
    await api.getEventPage("demo-night-tour");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "/api/events/demo-night-tour/event-page/draft",
      mutationOptions()
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "/api/events/demo-night-tour/event-page/publish",
      mutationOptions()
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      3,
      "/api/events/demo-night-tour/event-page",
      { credentials: "include" }
    );
  });

  test("merchant edge package routes use organizer credentials", async () => {
    const payload: MerchantEdgePackagesResponse = { packages: [] };
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    await api.generateMerchantEdgePackages("demo-night-tour");
    await api.getMerchantEdgePackages("demo-night-tour");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "/api/events/demo-night-tour/merchant-edge-packages/generate",
      mutationOptions()
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "/api/events/demo-night-tour/merchant-edge-packages",
      { credentials: "include" }
    );
  });

  test("operation suggestion routes support generate list and approve", async () => {
    const payload: OperationSuggestionsResponse = { suggestions: [] };
    const fetchSpy = vi.fn(() => Promise.resolve(jsonResponse(payload)));
    vi.stubGlobal("fetch", fetchSpy);

    await api.generateOperationSuggestions("demo-night-tour");
    await api.getOperationSuggestions("demo-night-tour");
    await api.approveOperationSuggestion("demo-night-tour", "os-001");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "/api/events/demo-night-tour/operation-suggestions/generate",
      mutationOptions()
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "/api/events/demo-night-tour/operation-suggestions",
      { credentials: "include" }
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      3,
      "/api/events/demo-night-tour/operation-suggestions/os-001/approve",
      mutationOptions()
    );
  });

  test("public touchpoint and coupon mutations use CSRF mutation options", async () => {
    const interaction: TouchpointInteraction = {
      id: "tpi-001",
      event_id: "demo-night-tour",
      touchpoint_id: "tp-001",
      merchant_id: "m001",
      interaction_type: "scan",
      source: "qr",
      anonymous_interaction_id: "anon-001",
      created_at: "2026-06-17T10:00:00Z",
      metadata: {}
    };
    const redemption: CouponRedemption = {
      id: "redemption-001",
      event_id: "demo-night-tour",
      coupon_rule_id: "cr-001",
      merchant_id: "m001",
      anonymous_interaction_id: "anon-001",
      status: "claimed",
      claimed_at: "2026-06-17T10:00:00Z",
      redeemed_at: null
    };
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(interaction))
      .mockResolvedValueOnce(jsonResponse(redemption))
      .mockResolvedValueOnce(jsonResponse({ ...redemption, status: "redeemed" }));
    vi.stubGlobal("fetch", fetchSpy);

    await api.recordTouchpointInteraction("demo-night-tour", "tp-001", {
      interaction_type: "scan",
      source: "qr"
    });
    await api.claimCoupon("demo-night-tour", "cr-001", "anon-001");
    await api.redeemCoupon("demo-night-tour", "redemption-001");

    expect(fetchSpy).toHaveBeenNthCalledWith(
      1,
      "/api/public/events/demo-night-tour/touchpoints/tp-001/interactions",
      mutationOptions({ interaction_type: "scan", source: "qr" })
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      2,
      "/api/public/events/demo-night-tour/coupons/cr-001/claim",
      mutationOptions({ anonymous_interaction_id: "anon-001" })
    );
    expect(fetchSpy).toHaveBeenNthCalledWith(
      3,
      "/api/public/events/demo-night-tour/coupon-redemptions/redemption-001/redeem",
      mutationOptions()
    );
  });
});
