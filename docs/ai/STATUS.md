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

## v0.8 Agent Capability State

- v0.8 P0 shifts the project from demo packaging toward concrete backend Agent capability.
- Backend Agent contracts now cover `AgentRun`, enriched `AgentStep`, `AgentToolCall`, `AgentDraft`, `AgentModelCall`, and `AgentEvaluation`.
- The deterministic Agent runtime records specialist Agent steps and tool-call evidence for planning, incident recovery, and review.
- Planning generation now persists an `AgentRun`, a backward-compatible `AgentTrace`, and deterministic tool calls for route, merchant selection, and budget split.
- Merchant sold-out updates create `Incident` plus recovery/public-notice Agent drafts without approving recovery or publishing public notices.
- Organizer recovery approval remains the only path that creates `PlanVersion` v2 and a published `PublicNotice`.
- Review generation creates an evidence-backed review summary draft tied to metrics, incidents, notices, and proposals.
- Optional Qwen draft backend was not executed in v0.8 P0.
- Qwen/QwenPaw remains optional and non-required for the deterministic demo.

## v0.9 Agent Evidence UI State

- v0.9 exposes the v0.8 backend Agent evidence inside organizer-facing product pages.
- Organizer workspace shows planning Agent run status, specialist steps, deterministic tool calls, and the human approval boundary.
- Organizer exception center shows incident recovery Agent evidence plus controlled recovery/public-notice drafts before approval.
- Organizer review center shows review Agent evidence and review summary draft beside the metric-backed report.
- Merchant, tourist, and public H5 pages do not import Agent evidence components or expose raw Agent/backend/model terms.
- Public H5 remains unauthenticated and visitor-facing.
- Screenshot evidence is under `docs/research/assets/v0.9-agent-evidence/`.
- Smoke documentation is in `docs/research/v0.9-agent-evidence-smoke.md`.
- Qwen/QwenPaw remains outside the required deterministic demo path.

## v1.0 Qwen Controlled Draft State

- v1.0 adds optional Qwen-assisted controlled drafts behind `AGENT_DRAFT_BACKEND=qwen`.
- Default local demo remains deterministic and does not require `DASHSCOPE_API_KEY`.
- Incident recovery can record Qwen/skipped/fallback model evidence for recovery explanation and public notice drafts.
- Review generation can record Qwen/skipped/fallback model evidence for review summary drafts.
- Model output is schema-checked, public-copy checked, unsafe-mutation checked, and never directly mutates authoritative state.
- Organizer pages can inspect model draft evidence; merchant, tourist, and public H5 pages do not expose raw model/backend terms.
- Screenshot evidence is under `docs/research/assets/v1.0-qwen-controlled-draft/`.
- Smoke documentation is in `docs/research/v1.0-qwen-controlled-draft-smoke.md`.
- QwenPaw remains unimplemented and must not be claimed as active workflow orchestration.

## v1.1 Live Qwen Smoke And Demo Material State

- v1.1 adds a guarded manual live Qwen smoke procedure under `apps/api/scripts/live_qwen_smoke.py`.
- The live smoke is not part of default backend pytest and requires `RUN_LIVE_QWEN_SMOKE=1` plus local process environment credentials.
- The live smoke writes sanitized evidence to `docs/research/v1.1-live-qwen-smoke.md` and `docs/research/assets/v1.1-live-qwen-smoke/live-qwen-smoke-result.json`.
- The current recorded smoke outcome is `blocked` because `DASHSCOPE_API_KEY` was not present in the local process environment.
- The blocked smoke evidence records a completed deterministic fallback probe; no API key, Authorization header, or raw provider payload is stored.
- Added `apps/web/tests/e2e/v11-live-qwen-smoke-evidence.spec.ts`; it skips live screenshots unless the smoke outcome is `live_success`.
- Demo material documents now cover the demo script, architecture brief, slide outline, and screenshot index.
- Qwen remains optional and constrained to controlled drafts.
- QwenPaw remains unimplemented and must not be claimed as active workflow orchestration.

## v1.2 Backend P0 State

- v1.2 Task 1-7 backend P0 is complete.
- Added event-page, merchant-edge package, in-shop touchpoint, coupon/redemption, and operation-suggestion backend contracts.
- Event pages can be drafted/published from an approved current `PlanVersion`, and public projection attaches only a published page for the current plan version.
- Merchant edge package generation creates merchant-scoped interaction packages, in-shop touchpoints, coupon rules, and deterministic Agent evidence.
- Public scan, coupon claim, and redemption simulation is anonymous and feeds merchant workbench plus review metrics.
- Merchant sold-out/runtime updates still create incidents and can now generate current-state operation suggestions.
- Operation suggestions are scoped to the current approved plan, filter stale task/package data, refresh pending payloads, and reject stale approvals.
- Review reports include touchpoint summary, merchant outcomes, extension tasks, and the existing responsibility-boundary lesson.
- Optional Qwen draft parsing now accepts a single `agent_draft` wrapper, sanitizes outbound prompt payload control fields, serializes provider prompts as JSON, and keeps unsafe output rejection intact.
- No real Qwen live call was run in this phase; Qwen remains optional and non-authoritative.
- Frontend exposure for v1.2 event page / merchant edge / operation suggestion surfaces is now implemented; see the Task 8-10 state below.
- QwenPaw remains unimplemented and must not be claimed as active workflow orchestration.

## v1.2 Event Page And Merchant Edge Frontend State

- v1.2 Task 8-10 is complete.
- Organizer workspace exposes Event Page draft/publish actions, merchant package generation, package readiness, evidence refs, and operation-suggestion generation.
- Organizer exception center exposes operation suggestions beside incidents/recovery proposals and guards stale proposal/suggestion responses.
- Merchant dashboard exposes the merchant-scoped interaction package, QR/touchpoint cards, coupon rules, claimed/redeemed counts, operator brief, and runtime update flow.
- Public H5 is framed as a visitor Event Page, remains unauthenticated, and supports simulated scan, coupon claim, and redemption actions without exposing backend/model terms.
- Review center shows touchpoint summary, merchant outcomes, extension tasks, and business-facing metric labels.
- Added v1.2 frontend API/types, UI tests, Playwright visual smoke, screenshots, and smoke documentation.
- Screenshot evidence is under `docs/research/assets/v1.2-event-page-merchant-edge/`.
- Smoke documentation is in `docs/research/v1.2-event-page-merchant-edge-smoke.md`.
- v1.2 Playwright smoke uses deterministic mocked API data for visual/product-flow evidence; backend authority is covered by pytest, not by a live backend E2E in this phase.
- Full verification passed on 2026-06-17: frontend tests/build, Playwright suite, backend pytest, public-boundary scan, local-path scan, and strict secret scan.
- Broad secret-pattern scanning only matched documentation examples and test assertions, not a real key or bearer token.
- QwenPaw remains unimplemented and must not be claimed as active workflow orchestration.

## v1.3 Live Demo Hardening State

- v1.3 adds a deterministic local demo reset command under `apps/api/scripts/reset_demo_state.py`.
- v1.3 adds a separate live Playwright config under `apps/web/playwright.live.config.ts`.
- v1.3 keeps the default mocked Playwright suite separate from the live-only smoke; `v13-live-demo-smoke.spec.ts` is excluded from `apps/web/playwright.config.ts` and runs through the live config.
- v1.3 live smoke starts FastAPI and Vite together and exercises real backend state.
- The live smoke covers organizer login, merchant login, public H5, merchant sold-out reporting, organizer operation suggestions, public UI scan/claim/redeem, and review metrics.
- Public interaction controls expose only visitor-safe touchpoint/coupon fields for the current plan version.
- Screenshot evidence is under `docs/research/assets/v1.3-live-demo-smoke/`.
- Smoke documentation is in `docs/research/v1.3-live-demo-smoke.md`.
- Operator demo script is in `docs/research/v1.3-operator-demo-script.md`.
- Optional Qwen live smoke is currently classified as `blocked` because `DASHSCOPE_API_KEY` was not present in the process environment.
- Qwen remains optional and non-authoritative.
- QwenPaw remains unimplemented and must not be claimed as active workflow orchestration.

## v1.4 QwenPaw Multi-Agent Orchestration Spike State

- v1.4 adds an optional QwenPaw-style shadow orchestration path for a merchant incident.
- The accepted path uses a deterministic fake QwenPaw adapter and does not require `DASHSCOPE_API_KEY`.
- No real QwenPaw or DashScope provider API is executed in v1.4.
- Shadow orchestration records `AgentRun(mode="qwenpaw_workflow")`, Leader/Worker step evidence through `AgentTrace.steps`, permissioned tool decisions, advisory drafts, and safety evaluations.
- The shadow run is advisory only. It does not approve plans, publish notices, mutate merchant runtime state, or create coupon/redemption records.
- Organizer pages may inspect shadow orchestration evidence.
- Merchant, tourist, and public H5 pages do not expose raw QwenPaw/model/backend terms.
- v1.3 deterministic live demo remains the required reliable demo path.

## v1.5 Real QwenPaw Guarded Smoke State

- v1.5 adds a manual guarded smoke script for a real locally running QwenPaw service under `apps/api/scripts/live_qwenpaw_smoke.py`.
- The smoke script is gated by `RUN_LIVE_QWENPAW_SMOKE=1` and defaults to `http://127.0.0.1:8088`.
- The script calls only `POST /api/agent/process`, rejects non-localhost hosts, disables environment/proxy trust with `trust_env=False`, and records bounded sanitized evidence.
- The original v1.5 recorded smoke outcome was `blocked`: localhost `127.0.0.1:8088` was reachable, but QwenPaw returned `No active model configured.` (`failure_kind=provider_error`).
- The current recorded smoke outcome has since been updated by v1.6 to `live_success` after an active LLM model was configured.
- Missing QwenPaw service, missing model configuration, or auth/configuration issues are classified as `blocked`, not deterministic-demo failures.
- v1.4 fake QwenPaw shadow orchestration remains the accepted organizer product path.
- v1.3 deterministic live demo remains the required reliable demo path.
- Live smoke success still does not mean production QwenPaw orchestration.

## v1.6 Local QwenPaw Reachability State

- A local QwenPaw service was installed in an isolated temp venv and initialized outside the repo.
- Local CLI version observed: `qwenpaw 1.1.12.post1`.
- The service started on `http://127.0.0.1:8088` and `POST /api/agent/process` returned an SSE response.
- Before model configuration, the SSE response ended with `status=failed`, `error.code=PROVIDER_ERROR`, and `message=No active model configured.`
- The global active LLM was then configured as `opencode/deepseek-v4-flash-free`, which does not require a process API key in this local QwenPaw setup.
- The smoke script now supports optional `QWENPAW_AGENT_ID`; the latest evidence uses `QwenPaw_QA_Agent_0.2` through the `X-Agent-Id` header.
- A fresh guarded smoke session returned `outcome=live_success`, HTTP 200, and a bounded non-empty model response preview.
- The smoke script treats failed QwenPaw SSE/provider responses and 200-level QwenPaw error payloads as `blocked`, not `live_success`.
- The recorded evidence remains sanitized and bounded at `docs/research/assets/v1.5-real-qwenpaw-guarded-smoke/live-qwenpaw-smoke-result.json`.
- This proves manual local QwenPaw model reachability, not production QwenPaw orchestration or authoritative state mutation.

## v1.7 Real QwenPaw Guarded Adapter State

- v1.7 adds advisory qualification on top of the v1.6 local QwenPaw reachability smoke.
- The smoke script now distinguishes provider reachability from advisory qualification.
- `advisory_qualified` requires `recovery_rationale`, `visitor_safe_notice_draft`, and `safety_notes`.
- `advisory_unqualified` means QwenPaw responded but the response did not pass adapter qualification.
- Provider/runtime failures remain `blocked`, not deterministic-demo failures.
- The current recorded v1.7 smoke outcome is `advisory_unqualified`: provider reachable, HTTP 200, but required advisory fields were missing.
- v1.4 fake QwenPaw shadow orchestration remains the accepted product path.
- v1.3 deterministic live demo remains the reliable demo path.

## Demo Accounts

- organizer: `organizer.demo`
- merchant: `merchant.m001.demo`
- tourist: `tourist.demo`
- password: `demo1234`

## Current Boundary

This is a stronger productized multilingual MVP, not a final commercial UI. The organizer pages are credible but conservative; the merchant and tourist mobile flows are functional and role-specific; the public H5 no longer reads as a backend preview. v1.4 adds optional organizer-only QwenPaw shadow evidence, and v1.7 adds strict guarded local QwenPaw advisory qualification evidence, while the reliable demo path remains deterministic.

Do not continue into production QwenPaw orchestration, real merchant connections, hardware, real traffic prediction, model training, payment/POS integrations, open registration, real map APIs, or a marketing landing page without a new plan.
