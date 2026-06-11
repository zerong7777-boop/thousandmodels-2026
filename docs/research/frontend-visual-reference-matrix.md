# Frontend Visual Reference Matrix

Date: 2026-06-10

## Purpose

This document looks beyond code templates. The v0.3 redesign needs product-level patterns for event operations, merchant task execution, tourist route experience, incident handling, and review analytics. The references below are not assets to copy. They are interaction and information-architecture references.

## Reference Matrix

| # | Reference | URL | Category | Organizer lesson | Merchant lesson | User lesson | Screenshot path | Reuse level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Eventbrite Organizer | https://www.eventbrite.com/organizer/ | event operations | Separate event management from public event page; clear organizer-owned workflow | Not primary | Public event and organizer views should be separate | Screenshot unavailable; page checked 2026-06-10, public product page describes organizer tooling | Pattern reference |
| 2 | Luma | https://lu.ma/ | event page / mobile event discovery | Event object has clear owner, time, guests, and updates | Not primary | Strong reference for clean event detail and RSVP-like mobile route entry | Screenshot unavailable; page checked 2026-06-10, visual note: clean mobile-friendly event cards and event pages | Pattern reference |
| 3 | Wanderlog | https://wanderlog.com/ | itinerary / trip planning | Route and plan can be organized around days/stops rather than generic records | Not primary | Strong route timeline and stop-planning mental model | Screenshot unavailable; page checked 2026-06-10, visual note: itinerary plus route/places pattern | Pattern reference |
| 4 | Roadtrippers | https://roadtrippers.com/ | route planning / stops | Route work should highlight stops and sequence, not tables first | Not primary | Route point cards should feel like places in a journey | Screenshot unavailable; page checked 2026-06-10, visual note: map-plus-stops travel planning composition | Pattern reference |
| 5 | Shopify POS | https://www.shopify.com/pos | merchant operations | Organizer should not expose merchant-only controls | Merchant tasks need large direct actions and simple status reporting | Not primary | Screenshot unavailable; page checked 2026-06-10, visual note: touch-first commerce operation modules | Pattern reference |
| 6 | Square POS | https://squareup.com/us/en/point-of-sale | merchant operations | Merchant operational state should be simple and action-oriented | Good reference for tablet/mobile task and status operations | Not primary | Screenshot unavailable; page checked 2026-06-10, visual note: clear operational tiles and transaction/task emphasis | Pattern reference |
| 7 | PagerDuty Incident Management | https://www.pagerduty.com/use-cases/incident-management/ | incident operations | Incident queue needs severity, owner, timeline, and response state | Not primary | Public user copy should be separate from internal incident details | Screenshot unavailable; page checked 2026-06-10, visual note: incident response lifecycle and urgency hierarchy | Pattern reference |
| 8 | Datadog Incident Management | https://www.datadoghq.com/product/incident-management/ | incident / review metrics | Incident and review surfaces should connect events, timeline, status, and metrics | Not primary | Not primary | Screenshot unavailable; page checked 2026-06-10, visual note: timeline, status, and metric-backed incident review | Pattern reference |
| 9 | Linear | https://linear.app/ | operational workspace | Dense product UI can still feel sharp when hierarchy, spacing, and keyboard-like flows are disciplined | Task status language can be concise | Not primary | Screenshot unavailable; page checked 2026-06-10, visual note: clean work queues, compact status, strong typography | Visual rhythm reference |

## Notes

### 1. Eventbrite Organizer

- URL: https://www.eventbrite.com/organizer/
- Category: organizer/event operations.
- What works: It separates organizer workflows from attendee-facing event pages. The organizer surface is about events, tickets, marketing, attendees, and operations rather than a generic app dashboard.
- What does not fit this project: This project is not ticketing, payment, or a full event SaaS.
- Applicable role: organizer.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: The organizer home should be an event operations command surface with event status, pending approvals, exception queue, and review entry. The tourist H5 should stay outside the organizer shell.

### 2. Luma

- URL: https://lu.ma/
- Category: event page / event community.
- What works: Clean event pages, simple event identity, mobile-friendly layout, low clutter, and direct attendee actions.
- What does not fit this project: The product is not a social event platform and should not center RSVP/community growth.
- Applicable role: user/tourist.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: The user H5 should start from event identity, time, route, notices, and action cards, not from backend terms like PlanVersion or Incident.

### 3. Wanderlog

- URL: https://wanderlog.com/
- Category: itinerary / travel planning.
- What works: It frames travel as stops, routes, days, notes, and places. This matches the old-district route story better than a table-first UI.
- What does not fit this project: This MVP does not need collaborative trip planning accounts, booking, or full map integrations.
- Applicable role: user/tourist, organizer route planning.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: User route pages should use a route timeline with place cards, stay time, story, and visitor task.

### 4. Roadtrippers

- URL: https://roadtrippers.com/
- Category: route planning / stops.
- What works: The route itself is the product object. Stops matter more than generic content cards.
- What does not fit this project: The MVP should not add real map APIs or long-distance trip planning.
- Applicable role: user/tourist.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: Use route sequence, stop status, and local story snippets as the core tourist UI. Map-like language can be suggested without integrating a real map API.

### 5. Shopify POS

- URL: https://www.shopify.com/pos
- Category: merchant operations.
- What works: Merchant actions are simple, large, and close to the work being done. The interface does not expose operator analytics or organizer decision internals.
- What does not fit this project: This MVP is not commerce/POS and should not add payments, orders, or inventory systems.
- Applicable role: merchant.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: Merchant pages should emphasize today's tasks, preparation checklist, status report buttons, and organizer notices.

### 6. Square POS

- URL: https://squareup.com/us/en/point-of-sale
- Category: merchant operations.
- What works: Touch-first operational UI, clear status modules, direct actions, and minimal cognitive load.
- What does not fit this project: No sales/payment flows should be added.
- Applicable role: merchant.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: Merchant runtime reporting should use large status controls and short confirmations, not dense admin forms.

### 7. PagerDuty Incident Management

- URL: https://www.pagerduty.com/use-cases/incident-management/
- Category: incident operations.
- What works: Incident surfaces distinguish urgency, response state, ownership, and timeline.
- What does not fit this project: The project should not become an SRE incident tool or add complex escalation policies.
- Applicable role: organizer exception center.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: The exception center should show incident severity, affected route points, affected merchants, proposal state, and approval action in one operational flow.

### 8. Datadog Incident Management

- URL: https://www.datadoghq.com/product/incident-management/
- Category: incident / review metrics.
- What works: Incident timeline and review metrics belong together. A report should be evidence-backed, not a generic text summary.
- What does not fit this project: No observability product, real telemetry, or alerting integrations should be built.
- Applicable role: organizer exception center, review center.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: The review center should present metric-backed outcomes, incident counts, recovery timing, and plan-version impact.

### 9. Linear

- URL: https://linear.app/
- Category: operational workspace.
- What works: Dense operational products can still feel premium through disciplined spacing, compact hierarchy, typography, and restrained color.
- What does not fit this project: Linear is a software issue tracker, not an event, route, or tourism product.
- Applicable role: organizer, merchant.
- Screenshot path: Screenshot unavailable in current environment; public page checked 2026-06-10.
- Extracted pattern: Use compact work queues and clear state transitions for approval and exception workflows, while avoiding generic admin chrome.

## Reference Coverage Check

- Organizer/dashboard references: Eventbrite Organizer, PagerDuty, Datadog, Linear.
- User/tourist mobile route references: Luma, Wanderlog, Roadtrippers.
- Merchant/task workflow references: Shopify POS, Square POS.
- Incident/review references: PagerDuty, Datadog.
