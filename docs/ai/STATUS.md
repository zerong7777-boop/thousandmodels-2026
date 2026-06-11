# STATUS

## Current State

Project root:

`<PROJECT_ROOT>`

As of 2026-06-12, v0.5 UI polish Task 1-12 is complete. The project has a deterministic FastAPI backend loop plus a role-separated React/Vite frontend with backend-backed demo login and screenshot-backed product UI.

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

## Demo Accounts

- organizer: `organizer.demo`
- merchant: `merchant.m001.demo`
- tourist: `tourist.demo`
- password: `demo1234`

## Current Boundary

This is a stronger productized MVP, not a final commercial UI. The organizer pages are credible but conservative; the merchant and tourist mobile flows are functional and role-specific; the public H5 no longer reads as a backend preview.

Do not continue into Qwen/QwenPaw integration, real merchant connections, hardware, real traffic prediction, model training, payment/POS integrations, open registration, real map APIs, or a marketing landing page without a new plan.
