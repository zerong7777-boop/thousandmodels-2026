# STATUS

## Current State

Project root:

`<PROJECT_ROOT>`

As of 2026-06-12, v0.6 i18n is complete. The project has a deterministic FastAPI backend loop plus a role-separated React/Vite frontend with backend-backed demo login, screenshot-backed product UI, and a lightweight owned multilingual frontend layer.

Current product direction:

```text
shadcn/ui-inspired local component layer
+ Tailwind product shells
+ owned product components under apps/web/src/components/product
+ existing Ant Design as migration bridge for legacy/login pieces
```

## v0.5 UI Polish State

- v0.5 template adoption gate completed in `docs/research/v0.5-ui-template-adoption.md`.
- Primary page-level visual direction selected and mapped to local files.
- P0 pages polished: login, organizer dashboard, organizer exception center, merchant status, public H5.
- P1 pages aligned: organizer workspace/review, merchant dashboard/tasks/notices, tourist route/notices.
- Added reusable product components: page header, status pill, metric tile, attention queue, activity timeline, workflow stepper, approval panel, recovery diff, merchant quick action, route progress, route stop card, notice feed, and empty state.
- Added v0.5 screenshot evidence in `docs/research/assets/v0.5-verification/`.
- Added visual review index in `docs/research/v0.5-visual-smoke.md`.
- Marked the old v0.4 Playwright visual spec as a historical baseline; v0.5 visual smoke is now the active screenshot suite.
- No backend core orchestration changes were required.
- Deterministic local demo remains runnable without `DASHSCOPE_API_KEY`.

## v0.6 i18n State

- Added a lightweight owned frontend i18n layer under `apps/web/src/i18n/`.
- Supported locales are exactly `zh-Hans`, `zh-Hant`, and `en`.
- Default locale is `zh-Hans`; English is the fallback.
- Locale preference persists under `zhiyin.locale`.
- Login, organizer shell, merchant shell, tourist shell, and public H5 expose language switching.
- Active v0.5 product surfaces use dictionary-backed product copy without a broad UI redesign.
- Known demo event route content needed for screenshots is localized on the frontend without backend schema changes.
- Public H5 remains unauthenticated.
- Locale switching does not replace backend-backed demo auth or role routing.
- Merchant sold-out quick action still sends the runtime update and requests organizer review.
- Added v0.6 screenshot evidence in `docs/research/assets/v0.6-i18n-verification/`.
- Added visual smoke index in `docs/research/v0.6-i18n-smoke.md`.
- No backend core workflow changes were required.
- Qwen/QwenPaw remains outside the required deterministic demo path.

## v0.7 Demo Narrative State

- v0.7 is a documentation and evidence-packaging phase, not a product feature phase.
- The v0.7 spec and implementation plan are under `docs/proposal/`.
- Demo narrative, vision-to-MVP gap review, screenshot walkthrough, competition brief, and presentation storyboard are under `docs/research/`.
- The recommended competition story is: planning -> merchant runtime signal -> incident -> organizer recovery approval -> public H5 update -> metric-backed review.
- Screenshot evidence is collected under `docs/research/assets/v0.7-demo-walkthrough/`.
- Two walkthrough screenshots are documented replacements for exact sold-out and approved-v2 moments; regenerate those before final slide production if stronger evidence is needed.
- Qwen/QwenPaw remains a future advisory layer and is not required for the current deterministic demo.

## Demo Accounts

- organizer: `organizer.demo`
- merchant: `merchant.m001.demo`
- tourist: `tourist.demo`
- password: `demo1234`

## Current Boundary

This is a stronger productized multilingual MVP, not a final commercial UI. The organizer pages are credible but conservative; the merchant and tourist mobile flows are functional and role-specific; the public H5 no longer reads as a backend preview.

Do not continue into Qwen/QwenPaw integration, real merchant connections, hardware, real traffic prediction, model training, payment/POS integrations, open registration, real map APIs, or a marketing landing page without a new plan.
