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

## v1.8 QwenPaw Advisory Optimization Spike State

- v1.8 keeps QwenPaw live execution manual, localhost-only, advisory-only, and optional.
- The smoke script now supports prompt variants for JSON-only, Markdown-section, and few-shot JSON advisory formatting.
- The default v1.8 validator is `json_no_preamble_validator`; `strict_existing_validator` remains available for compatibility with the v1.7 qualification path.
- Repair attempts are bounded and record metadata only: attempt number, response status, advisory status, qualification failure kind, and field presence.
- The v1.8 evidence report now renders a `Repair History` section without raw response content.
- Agent variants can route between the active/default agent and the current QA agent configuration.
- v1.8.1 fixes QwenPaw SSE typed-content parsing: reasoning/thinking streams are excluded, streaming content is grouped by `msg_id`, and only final assistant message text is validated.
- After the parser fix, the real local QwenPaw v1.8 matrix returned 3/3 `advisory_qualified` results with `json_no_preamble_pass=true` and zero repair attempts.
- Matrix evidence is stored under `docs/research/assets/v1.8-qwenpaw-advisory-optimization/` with separate parserfix JSON artifacts for QA JSON-only, QA few-shot JSON, and default JSON-only runs.
- The v1.8.1 live evidence proves local advisory qualification through the guarded smoke adapter, not production orchestration.
- v1.4 fake QwenPaw shadow orchestration remains the accepted product path.
- v1.3 deterministic live demo remains the reliable demo path.

## v1.9 Commercial Readiness Audit State

- v1.9 is a readiness audit and evidence-packaging phase, not a production-hardening implementation phase.
- The v1.9 audit classifies the current product as a CR0 demo-grade MVP with a CR1 evidence-backed audit pack.
- Local verification passed during v1.9: API pytest, web Vitest, and web production build.
- GitHub repository evidence shows no open PRs or issues, PR #1 and PR #2 merged, and origin/main at `562dca89ef20e19e8c2bf9ae244a95517cc86193`.
- No root GitHub Actions workflow directory, commit statuses, or workflow runs were observed for origin/main.
- The local worktree still contains 14 historical screenshot PNG diffs from earlier verification passes; v1.9 keeps them out of scope.
- P0 gaps are CI/release gates, repo hygiene, auth/session/CSRF hardening, migration-backed persistence, deployment/environment policy, and commercial claim boundaries.
- P1 gaps are frontend bundle budget, observability, live E2E release gating, and external integration realism.
- v1.8.1 QwenPaw evidence remains local, optional, localhost-only, advisory-only, and non-authoritative.
- The recommended next phase is `v2.0-ci-repo-hygiene`.

## v2.0 CI And Repository Hygiene State

- v2.0 adds repository-level CI and hygiene gates without changing product runtime behavior.
- `.github/workflows/ci.yml` defines API tests, web tests/build, and repository hygiene jobs for pull requests and pushes to `main` and `v1-qwen-controlled-draft`.
- `scripts/repo_hygiene.py` provides dependency-free checks for high-confidence secrets, local absolute paths, tracked `node_modules`, and generated screenshot artifact changes.
- Local v2.0 verification passed: repo hygiene, API pytest, web Vitest, and web production build.
- Remote GitHub Actions execution has not been observed yet because the v2.0 commit has not been pushed.
- The 14 historical screenshot PNG diffs remain unstaged and unresolved by design; v2.0 does not restore or commit them without an explicit evidence-refresh or restore decision.
- v2.0 locally closes `CR-P0-001` and partially closes `CR-P0-002`; full closure requires a pushed branch with green GitHub Actions.
- The recommended next phase after remote CI is green is `v2.1-auth-security-hardening`.

## v2.1 Auth Security Hardening State

- v2.1 adds typed backend security settings for `APP_ENV`, `DEMO_MODE`, `APP_SECRET_KEY`, session cookie policy, CSRF mode, TTL, and allowed origins.
- Demo account seeding now runs only when demo mode is enabled, and startup validation rejects unsafe production-like configuration before serving requests.
- Session cookies now use settings-driven `secure`, `samesite`, TTL, and path attributes while preserving local localhost demo compatibility.
- CSRF handling now keeps the fixed `X-Zhiyin-CSRF: demo` path demo-only and adds a signed double-submit token baseline for non-demo modes.
- `GET /api/auth/csrf` issues a signed CSRF token and non-HttpOnly `zhiyin_csrf` cookie for frontend double-submit use.
- CORS/local-origin behavior is aligned with the settings boundary: localhost origin regex is demo-only, while non-demo modes use explicit allowed origins.
- The frontend now gates demo quick-fill UI behind `VITE_DEMO_MODE` and uses a shared mutation helper for demo versus double-submit CSRF behavior.
- `.env.example`, README, and docs/ai notes document the beta security baseline and production refusal boundaries without adding secrets.
- v2.1 closes the v1.9 `CR-P0-003` demo-vs-production auth boundary gap at beta baseline level.
- v2.1 does not add public registration, OAuth/SSO, password reset, tenant isolation, real identity administration, or compliance readiness.

## v2.2 Persistence And Migrations State

- v2.2 adds a migration-managed SQLite store while keeping the existing `MVPStore` domain API.
- The current migration chain is `0001_initial_records` and `0002_auth_tables`.
- `schema_migrations` records applied schema versions, and migrations are idempotent on fresh or already-current databases.
- `MVPStore` now applies migrations on initialization in local/demo-compatible mode.
- Production/staging-like startup can refuse pending migrations when `AUTO_MIGRATE=false`.
- `/api/health` now reports store kind, schema version, and pending migration count without leaking a local database path in production mode.
- `apps/api/scripts/migrate_store.py` runs the migration chain explicitly and prints JSON status.
- `apps/api/scripts/reset_demo_state.py` now refuses destructive reset outside local/demo mode or when `DEMO_MODE=false`.
- v2.2 improves schema ownership and migration discipline, but does not add production database operations, backups, rollback automation, PostgreSQL, or tenant isolation.

## v2.3 Deployment And Environment Operations State

- v2.3 defines a local/demo/staging/production-like environment contract in `docs/research/v2.3-environment-contract.md`.
- `.env.example` is grouped by app mode, API security, store, agents, manual QwenPaw smoke, and web settings.
- `/api/ready` reports sanitized readiness for settings mode, store connectivity, migration pending count, auth policy, and optional provider status.
- Staging/production-like startup rejects `AUTO_MIGRATE=true`, `RUN_LIVE_QWENPAW_SMOKE=true`, and localhost `QWENPAW_BASE_URL` values.
- `MVPStore` now refuses restricted-environment `AUTO_MIGRATE=true` before creating or migrating the database.
- `apps/api/scripts/deployment_smoke.py` checks `/api/health`, `/api/ready`, and `/api/public/events/demo-night-tour` against a running API.
- v2.3 intentionally does not add Dockerfiles because the deployment target is still unspecified.
- v2.3 partially closes deployment/environment policy readiness, but it does not add real hosting, managed secrets, TLS, DNS, backups, monitoring, or incident operations.

## v2.4 Observability And Release Runbook State

- v2.4 adds request ID middleware. Every normal, HTTPException, and unhandled-error API response includes `X-Request-ID`.
- Safe incoming request IDs are reused; unsafe or too-long request IDs are replaced with generated IDs and stored on `request.state.request_id`.
- API requests emit structured JSON logs with request ID, method, path, route template, status code, duration, and authenticated actor role/user ID when available.
- Structured logging redacts sensitive field names, bearer/cookie-like fields, raw provider payload field names, and embedded local absolute paths.
- HTTP exceptions and unhandled exceptions return a consistent `error` envelope with `code`, `message`, and `request_id`.
- `/api/metrics` exposes process-local beta counters for health checks, auth failures, agent runs, QwenPaw advisory runs, public touchpoint/coupon interactions, recovery approvals, and review reports.
- Release and incident response runbooks are under `docs/ops/`.
- v2.4 is a beta operations baseline. It does not add vendor monitoring, durable metrics, alert routing, formal SLOs, or customer incident management.

## v2.5 Live E2E Release Gate State

- v2.5 adds `apps/api/scripts/release_gate.py`, an API-first release gate for a real running local/demo API.
- The gate checks health, readiness, the unauthenticated protected-route error envelope, organizer login, demo seed, plan generation, plan approval, event-page draft/publish, merchant-edge package generation, public event projection, public scan/claim/redeem, merchant login/workbench, review report generation, and process-local metrics.
- The gate uses real HTTP sessions through `httpx.Client` and writes JSONL step output plus optional JSON evidence.
- The recorded v2.5 evidence is `docs/research/assets/v2.5-live-e2e-release-gate/release-gate-result.json` with `status=passed` for 20 live API steps.
- v2.5 also fixes local-path redaction so ordinary URLs such as `http://127.0.0.1:8025` are not mistaken for Windows absolute paths.
- v2.5 is a deterministic local/demo release gate. It does not start servers, run browser screenshots, call Qwen/QwenPaw, add cloud hosting, or prove production readiness.

## v2.6 Browser Release Evidence Gate State

- v2.6 adds `apps/web/tests/e2e/v26-browser-release-evidence.spec.ts`, a Playwright browser release gate for a real local FastAPI API and Vite app.
- `apps/web/playwright.live.config.ts` now supports env-driven API/web ports and uses an isolated SQLite database by default when `DATABASE_URL` is not supplied.
- Ordinary Playwright runs keep live specs out of scope; `apps/web/playwright.config.ts` excludes both v1.3 and v2.6 live browser specs.
- `apps/web/package.json` adds `npm.cmd run test:e2e:live:v26` for the focused browser gate.
- The gate verifies organizer workspace, merchant package surface, merchant sold-out reporting, organizer exception suggestions, public mobile scan/claim/redeem, organizer review page, and process-local metrics.
- The recorded v2.6 evidence is `docs/research/assets/v2.6-browser-release-evidence-gate/browser-release-gate-result.json` with `status=passed`, 8 passed steps, and 5 screenshot hashes.
- Screenshot PNG files are generated as local inspection artifacts and are not committed by default.
- v2.6 is still deterministic local/demo browser release evidence. It does not add cloud browser testing, real external integrations, Qwen/QwenPaw production orchestration, or real commercial business logic.

## v2.7 Real Product Logic Foundation State

- v2.7 adds the first non-demo event lifecycle foundation while preserving the deterministic demo release gates.
- Organizers can create and update draft events through `POST /api/events` and `PATCH /api/events/{event_id}` before planning.
- Non-demo plan generation now requires an explicit event brief and summary; it no longer silently seeds `demo-night-tour`.
- Demo event seeding remains explicit through `/api/events/demo/seed`, while shared local merchant/route catalog seeding is separated from demo event and mock metric records.
- Event lifecycle state now separates plan approval from public publication: generated plans move events to `pending_approval`, approved plans move events to `active`, and only event-page publish marks `public_release_status=published`.
- Non-demo public event projection and public scan/claim/redeem mutations require a published current event page.
- Public touchpoint scans, coupon claims, and coupon redeems are idempotent for repeated anonymous interactions and do not double-count stored review metrics or exposed process counters.
- Public scan, claim, and redeem mutations reject stale touchpoint/coupon children after a merchant's current package changes.
- Review reports continue deriving touchpoint summaries, merchant outcomes, and extension tasks from stored interaction and coupon redemption records.
- Frontend API/types now expose `createEvent` and `updateEvent` contracts, but v2.7 does not add a full organizer event-creation UI.
- v2.7 is a product-logic beta foundation, not pilot readiness or production commercial readiness.

## v2.8 Organizer Event Workspace State

- v2.8 turns the v2.7 event API into an organizer-facing event workflow layer.
- `/organizer/events` now acts as the event portfolio and loads events from `api.getEvents()`.
- Organizers can create a non-demo draft event from a compact form backed by `api.createEvent()`.
- The create form parses comma/newline list fields, validates required payload fields locally, keeps entered values on backend validation/conflict errors, and does not call demo seed.
- Empty event lists remain empty by default; the demo event is only created through the explicit demo seed action.
- Event portfolio rows show event title, area, date, time window, lifecycle status, public release status, current plan version, and event-specific workspace/exceptions/review links.
- Organizer shell workspace, exceptions, and review navigation follows the selected event id when the route contains one, with `demo-night-tour` as the fallback.
- `OrganizerEventWorkspacePage` loads selected event context through `api.getEvent(eventId)` and shows title, area, date, time window, event status, and public release state.
- Draft events with no route plan show a clear no-plan state while keeping the build-plan action available.
- Workspace action errors for plan/event-page/package/suggestion actions surface as visible feedback with alert/status semantics.
- Event list reloads ignore stale responses so older `getEvents()` calls cannot overwrite newer create/seed refresh state.
- New v2.8 visible copy has explicit `en`, `zh-Hans`, and `zh-Hant` dictionary entries.
- v2.8 is a frontend product workflow layer. It does not add merchant assignment setup, event archive/delete/clone, external integrations, QwenPaw production orchestration, or production readiness.

## v2.9 Event Operations Setup Pack State

- v2.9 adds event-level merchant roster setup for organizer-managed non-demo events.
- Organizers can read, replace, and update a selected event's merchant roster through organizer-only backend APIs.
- Non-demo plan generation now requires at least one selected merchant and all selected participants to be confirmed and ready.
- Planning merchant assignments, merchant tasks, route point linked merchants, event-page drafts, stale page rebuilds, and merchant-edge packages are scoped to selected ready merchants.
- The organizer workspace shows merchant setup, selected merchant readiness, save actions, and mark-ready actions for the selected event.
- The workspace disables Build route plan for non-demo events until merchant setup is ready, while the deterministic `demo-night-tour` path remains backward compatible.
- v2.9 uses the existing local merchant catalog only. It does not add merchant onboarding, external merchant integrations, POS/payment/hardware/map/weather/traffic/identity, production QwenPaw orchestration, or production readiness.

## v3.0 Merchant Network Pack State

- v3.0 turns the thin local merchant catalog into an organizer-managed merchant network baseline.
- Merchant profiles now include contact owner/phone, address label, area, structured operating windows, capacity notes, category tags, participation constraints, and active/inactive/suspended status.
- Organizers can create merchants, read merchant detail, update merchant profile fields, and inspect event participation history through organizer-only backend APIs.
- The organizer frontend adds `/organizer/merchants` and a Merchant Network navigation item for catalog operations.
- The merchant network page supports create, select, edit, profile inspection, and local participation-history review.
- Event merchant setup now evaluates selected merchant eligibility using merchant status, event time-window overlap, missing contact/area/windows, and participation constraints.
- Ineligible merchants cannot be marked ready and keep non-demo planning blocked; needs-review merchants remain visible for organizer judgment.
- Sidebar navigation now exposes semantic links with hrefs while preserving client-side navigation behavior.
- v3.0 remains local-catalog based. It does not add public merchant onboarding, POS/payment/hardware/map/weather/traffic/identity integrations, production QwenPaw orchestration, or production readiness.

## v3.1 Event Planning Eligibility Pack State

- v3.1 makes non-demo route planning use merchant-network data as deterministic planning intelligence instead of only as a readiness gate.
- Backend `PlanVersion` now exposes `merchant_fit` and `planner_warnings` with backward-compatible defaults for existing stored plans.
- A focused `merchant_fit` service scores eligible merchants by event brief signals, merchant category/activity tags, operating-window overlap, capacity, night/rain scores, missing profile data, and participation constraints.
- Ineligible merchants remain excluded through the existing v3.0 eligibility rules; weak but eligible merchants can still be planned with organizer-visible warnings.
- `generate_plan_version()` now orders selected merchant assignments by fit score and records fit evidence on the generated plan.
- The legacy `demo-night-tour` path still preserves catalog-order merchant assignment when no explicit roster exists, so existing demo and merchant-edge contracts remain stable while fit evidence is still recorded.
- Planning Agent evidence now records deterministic merchant-fit output in the merchant matching step rather than a generic night-score selection output.
- Organizer workspace now renders planner warnings, fit levels, scores, matched signals, warnings, and rationales from the current plan.
- v3.1 remains deterministic and local-catalog based. It does not add live Qwen/QwenPaw scoring, route geometry optimization, map/weather/traffic/POS/payment integrations, or automatic approval/publication.

## v3.2 Route Assembly Quality Pack State

- v3.2 makes selected route points deterministic, scored, and explainable instead of relying on first-six route-point slicing.
- Backend `PlanVersion` now exposes `route_fit` and `route_warnings` with backward-compatible defaults for existing stored plans.
- A focused `route_assembly` service scores route points by selected merchant linkage, event-brief token match, rainy-day/indoor backup fit, guided-route stay duration, status, and crowd risk.
- `generate_plan_version()` now covers selected merchants with linked route points where possible, fills remaining route slots by route fit, preserves local catalog order for selected points, and keeps route-point `linked_merchants` scoped to selected plan merchants.
- Generated plans warn when selected merchants have no linked route point, when selected route points carry weak fit/rain/crowd/status concerns, or when route coverage is thinner than selected merchant coverage.
- Planning Agent evidence now records the `route.assemble_route_points` tool call plus route fit and route warnings in the route step structured output.
- Organizer workspace now renders route warnings, fit levels, scores, roles, matched signals, warnings, and rationales from the current plan.
- Explicit demo seeding now clears stale global route points before reseeding the deterministic local catalog, preventing historical test/catalog entries from polluting the legacy demo route scope.
- v3.2 remains deterministic and local-catalog based. It does not add route geometry optimization, live map/weather/traffic APIs, Qwen/QwenPaw production orchestration, POS/payment integrations, or automatic approval/publication.

## v3.3 Merchant Portal Setup Pack State

- v3.3 turns selected-event merchant readiness from an organizer-only toggle into a merchant-submitted setup workflow.
- `EventMerchantParticipant` now carries event-specific setup status, capacity commitment, staffing/stock/indoor-backup/window confirmations, merchant contact details, merchant notes, submission metadata, and computed setup gaps.
- A focused merchant setup service builds assigned-event contexts, computes setup gaps, detects rainy/indoor-backup requirements from event briefs, and updates only merchant-owned setup evidence fields.
- Merchant users can list assigned events, read one setup context, and submit setup evidence through `/api/merchants/me/events...` endpoints using the existing session and mutation-origin boundary.
- Merchant setup submission does not mark organizer readiness, approve a plan, publish an event page, generate packages, or mutate runtime state.
- Organizer roster summaries now expose merchant setup evidence and setup gaps, and non-demo plan generation remains blocked until selected merchants are confirmed, organizer-ready, eligible, and setup-complete.
- The merchant dashboard now surfaces assigned-event setup entry points, and `/merchant/events/:eventId/setup` provides an event-specific merchant setup form.
- The organizer workspace merchant setup panel now renders setup status, merchant contact, capacity, readiness confirmations, merchant notes, and gap reasons before planning.
- Existing v2.9 roster gates, v3.0 eligibility checks, v3.1 merchant-fit evidence, v3.2 route-fit evidence, and the legacy deterministic demo path remain compatible.
- v3.3 remains local-catalog and beta-auth based. It does not add public merchant onboarding, identity administration, contracts, settlement, POS/payment/hardware/map/weather/traffic integrations, Qwen/QwenPaw production orchestration, or automatic approval/publication.

## v3.4 Event Operations Command Center Pack State

- v3.4 adds a read-only event operations summary for organizer users through `GET /api/events/{event_id}/operations-summary`.
- The summary consolidates event state, merchant setup readiness, current plan approval, visitor event page publication, merchant interaction packages, incidents, public notices, and audit logs.
- Overall readiness is classified as `ready`, `warning`, or `blocked`, with blocker and warning counts plus evidence-linked launch checks.
- Launch checks block incomplete merchant setup, missing approved plan, missing published event page, missing active merchant packages, and unresolved high-severity incidents.
- Lower-severity active incidents, missing notice evidence, and missing audit evidence surface as warnings without mutating event state.
- Action items are advisory and do not approve plans, publish pages, generate packages, publish notices, or recover incidents.
- The organizer workspace now renders an operations command center near the top of the selected event workspace with readiness metrics, launch checks, action items, and recent audit timeline.
- Existing v2.9-v3.3 roster/setup/planning gates and the deterministic demo path remain compatible.
- v3.4 remains local-catalog and beta-operations based. It does not add external integrations, real provider data, production QwenPaw orchestration, automatic approval/publication, or customer incident operations.

## Demo Accounts

- organizer: `organizer.demo`
- merchant: `merchant.m001.demo`
- tourist: `tourist.demo`
- password: `demo1234`

## Current Boundary

This is a stronger productized multilingual MVP, not a final commercial UI or commercial application. The organizer pages are credible but conservative; the merchant and tourist mobile flows are functional and role-specific; the public H5 no longer reads as a backend preview. v1.4 adds optional organizer-only QwenPaw shadow evidence, v1.8 adds guarded local QwenPaw advisory optimization evidence, v1.9 maps the P0/P1 commercial-readiness gaps, v2.0 adds local CI/repository hygiene gates, v2.1 adds beta auth/session/CSRF demo-boundary hardening, v2.2 adds migration-managed SQLite persistence, v2.3 adds deployment environment/readiness operations, v2.4 adds beta observability/runbook operations, v2.5 adds a deterministic live API release gate, v2.6 adds deterministic live browser release evidence, v2.7 adds the first real non-demo event lifecycle foundation, v2.8 exposes that foundation through organizer event portfolio/create/workspace navigation, v2.9 adds event-level merchant setup gating before non-demo planning, v3.0 adds organizer-managed merchant network profiles plus eligibility checks, v3.1 makes non-demo plan merchant selection fit-ranked and explainable, v3.2 makes local route assembly scored, merchant-linked, and organizer-visible, v3.3 adds merchant-submitted event setup evidence before organizer readiness and planning, and v3.4 adds an organizer operations command center that consolidates launch readiness and audit evidence. The reliable demo path remains deterministic.

Do not continue into production QwenPaw orchestration, real merchant connections, hardware, real traffic prediction, model training, payment/POS integrations, open registration, real map APIs, or a marketing landing page without a new plan.
