# Frontend Visual Board

Date: 2026-06-10
Purpose: help select the v0.3 frontend visual direction before implementation.

This board uses screenshots only as internal visual references. Do not copy proprietary page layouts, images, brand colors, or commercial assets into the product. Extract interaction patterns, density, spacing, and role-specific information architecture only.

## Quick Choice

### A. Recommended: shadcn/ui-inspired product UI + keep Ant Design as migration bridge

Choose this if you want the project to stop looking like a generic management backend.

- Best for: organizer operations shell, merchant workbench, user/tourist H5 after customization.
- Reuse: layout rhythm, dashboard blocks, card/table composition, command/sidebar patterns.
- Keep: existing Ant Design forms/tables/messages where they are stable.
- Risk: needs careful design tokens, Tailwind/Radix-style setup, and owned components.

<img src="assets/template-screenshots/01-shadcn-blocks-desktop.png" width="900" alt="shadcn/ui dashboard blocks screenshot">

### B. Backup: Mantine full React UI kit

Choose this if you prefer a cohesive maintained component library and want less copy-paste component ownership.

- Best for: broad component coverage, forms, app shell, responsive layouts.
- Reuse: component API, hooks, neutral product look.
- Risk: larger component migration from current Ant Design stack; still needs custom role design.

<img src="assets/template-screenshots/03-mantine-desktop.png" width="900" alt="Mantine homepage screenshot">

### C. Fast but not recommended: Ant Design Pro-style organizer backend

Choose this only if speed matters more than visual maturity.

- Best for: dense organizer tables, approval/detail pages, familiar enterprise admin modules.
- Reuse: data density, table/detail structure.
- Risk: repeats the current problem: the product still looks like a generic admin dashboard.

<img src="assets/template-screenshots/02-ant-design-pro-desktop.png" width="900" alt="Ant Design Pro screenshot">

## Template/UI Kit References

### shadcn/ui

Decision: primary direction.

Why it matters: strongest option for a modern product surface that can be adapted into different role shells without adopting a full admin framework.

<img src="assets/template-screenshots/01-shadcn-blocks-desktop.png" width="900" alt="shadcn/ui screenshot">

### Mantine

Decision: backup direction.

Why it matters: cohesive library, clean defaults, good docs. Better if we want one library instead of copied shadcn-style components.

<img src="assets/template-screenshots/03-mantine-desktop.png" width="900" alt="Mantine screenshot">

### Semi Design

Decision: visual reference only.

Why it matters: crisp component style and professional visual rhythm, but migrating away from Ant Design to Semi is not necessary for this MVP.

<img src="assets/template-screenshots/05-semi-design-desktop.png" width="900" alt="Semi Design screenshot">

### Tremor

Decision: review/metrics reference only.

Why it matters: useful for metric-backed review center, KPI panels, and operational analytics.

<img src="assets/template-screenshots/04-tremor-desktop.png" width="900" alt="Tremor screenshot">

### Flowbite React

Decision: mobile/tablet component reference only.

Why it matters: simple Tailwind components can help merchant/user surfaces, but it is less distinctive than shadcn.

<img src="assets/template-screenshots/06-flowbite-react-desktop.png" width="900" alt="Flowbite React screenshot">

### Radix Themes

Decision: primitive/theme reference only.

Why it matters: accessible primitives and controlled theme language. It is a foundation, not a full product template.

<img src="assets/template-screenshots/07-radix-themes-desktop.png" width="900" alt="Radix Themes screenshot">

## Product Visual References By Role

### User/Tourist H5: Luma

Borrow: event identity, mobile-first event page hierarchy, direct action, strong visual memory.

Avoid: playful party style and oversized promotional hero if it weakens the old-district route product.

<img src="assets/visual-reference-screenshots/01-luma-mobile.png" width="320" alt="Luma mobile screenshot">

### User/Tourist Route: Wanderlog

Borrow: route/itinerary mental model, stops as the main object, travel planning structure.

Avoid: full trip planner complexity, collaborative travel planning, booking/map-heavy features.

<img src="assets/visual-reference-screenshots/02-wanderlog-desktop.png" width="900" alt="Wanderlog screenshot">

### User/Tourist Route: Roadtrippers

Borrow: route sequence, stop-first storytelling, journey framing.

Avoid: real map API and long-distance road-trip assumptions.

<img src="assets/visual-reference-screenshots/03-roadtrippers-desktop.png" width="900" alt="Roadtrippers screenshot">

### Merchant Workbench: Clover POS

Borrow: merchant context, direct operational framing, touch-first business workflow.

Avoid: hardware/POS/payment scope. This project only needs task/status reporting, not commerce.

<img src="assets/visual-reference-screenshots/04-clover-pos-desktop.png" width="900" alt="Clover POS screenshot">

### Organizer Exception Center: Datadog Incident Response

Borrow: incident list, severity tags, timeline, detail panel, evidence-backed recovery/review language.

Avoid: SRE observability product complexity and real alerting integrations.

<img src="assets/visual-reference-screenshots/07-datadog-incident-desktop.png" width="900" alt="Datadog Incident Response screenshot">

### Organizer Event Operations: Eventbrite Organizer

Borrow: event object ownership, organizer workflow separate from attendee view, clear operation entry.

Avoid: ticketing/payment/marketing SaaS scope.

<img src="assets/visual-reference-screenshots/08-eventbrite-organizer-desktop.png" width="900" alt="Eventbrite Organizer screenshot">

### Dense Product Polish: Linear

Borrow: compact operational layout, restrained color, sharp typography, work queue feel.

Avoid: dark-only issue-tracker aesthetic and software-project terminology.

<img src="assets/visual-reference-screenshots/09-linear-desktop.png" width="900" alt="Linear screenshot">

## Decision Matrix

| Option | Visual maturity | Non-admin feel | Three-role fit | Migration cost | Recommendation |
| --- | ---: | ---: | ---: | ---: | --- |
| A. shadcn/ui-inspired hybrid | 5 | 5 | 5 | 3 | Choose this by default |
| B. Mantine full UI kit | 4 | 4 | 4 | 4 | Backup if you reject Tailwind/shadcn |
| C. Ant Design Pro-style | 3 | 2 | 3 | 2 | Fast but likely too admin-like |
| D. Semi Design migration | 4 | 4 | 3 | 4 | Nice visual reference, not worth migration now |
| E. Tremor-only metrics style | 4 | 3 | 2 | 3 | Use only for review center inspiration |

## My Recommendation

Pick option A:

```text
shadcn/ui-inspired role-specific product UI
+ existing Ant Design as migration bridge
+ Luma/Wanderlog for tourist H5
+ Clover for merchant task/status framing
+ Datadog/Linear/Eventbrite for organizer operations
```

This gives the best chance of escaping the current "generic backend demo" feel without rewriting the entire frontend stack at once.

## What I Need You To Decide

Reply with one of these:

1. `Choose A` - proceed with shadcn/ui-inspired hybrid direction.
2. `Choose B` - use Mantine as the main UI kit direction.
3. `More research` - collect more screenshots before deciding.
