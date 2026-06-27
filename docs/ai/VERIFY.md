# VERIFY

## Environment

- Project root: `<PROJECT_ROOT>`
- Date: 2026-06-12
- Frontend app: `apps/web`
- Backend API: `apps/api`
- Playwright smoke server: configured by the frontend Playwright setup

## v0.5 Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `npm.cmd run test` | `apps/web` | 0 | 14 test files passed, 44 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3196 modules transformed; Vite emitted a large chunk warning for `assets/index-B60lrhhI.js` at 701.64 kB. |
| `npm.cmd exec playwright test tests/e2e/v05-visual.spec.ts` | `apps/web` | 0 | 5 v0.5 visual tests passed and generated 9 screenshots. |
| `npm.cmd exec playwright test` | `apps/web` | 0 | 5 v0.5 visual tests passed; 4 v0.4 historical baseline tests skipped. |
| `python -m pytest -q` | `apps/api` | 0 | 34 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |

### Screenshot Evidence

| Route | Viewport | Screenshot | Manual inspection |
| --- | --- | --- | --- |
| `/login` | 1280x720 desktop | `docs/research/assets/v0.5-verification/01-login.png` | Nonblank; product access and demo accounts are clear. |
| `/organizer/dashboard` | 1440x900 desktop | `docs/research/assets/v0.5-verification/02-organizer-dashboard.png` | Nonblank; event status, attention queue, metrics, and timeline visible. |
| `/organizer/events/demo-night-tour` | 1440x900 desktop | `docs/research/assets/v0.5-verification/03-organizer-workspace.png` | Nonblank; workflow stepper, evidence trail, plan status, merchant readiness visible. |
| `/organizer/events/demo-night-tour/exceptions` | 1440x900 desktop | `docs/research/assets/v0.5-verification/04-organizer-exceptions.png` | Nonblank; impact scope, before/after diff, confirmation, and public notice preview visible. |
| `/organizer/events/demo-night-tour/review` | 1440x900 desktop | `docs/research/assets/v0.5-verification/05-organizer-review.png` | Nonblank; KPI-backed review and recommendations visible. |
| `/merchant/dashboard` | 390x844 mobile | `docs/research/assets/v0.5-verification/06-merchant-dashboard-mobile.png` | Nonblank; today task and next action visible. |
| `/merchant/events/demo-night-tour/status` | 390x844 mobile | `docs/research/assets/v0.5-verification/07-merchant-status-mobile.png` | Nonblank; touch-first quick actions and organizer review feedback visible. |
| `/user/events/demo-night-tour/route` | 390x844 mobile | `docs/research/assets/v0.5-verification/08-tourist-route-mobile.png` | Nonblank; route progress, story stops, and visitor task visible. |
| `/public/events/demo-night-tour` | 390x844 mobile | `docs/research/assets/v0.5-verification/09-public-h5-mobile.png` | Nonblank; public H5 is visitor-facing and does not expose internal backend terms. |

### Template Adoption Evidence

| Document | Result |
| --- | --- |
| `docs/research/v0.5-ui-template-adoption.md` | Completed; compares 18 candidates/references, maps 10 local blocks, lists 8 rejected candidates. |
| `docs/research/v0.5-ui-polish-reference.md` | Completed; records visual references and before/after intent. |
| `docs/research/v0.5-visual-smoke.md` | Completed; indexes 9 v0.5 screenshots with scoring and remaining weaknesses. |

### Boundary Notes

- Public H5 remains unauthenticated.
- Merchant sold-out quick action still calls runtime update API and requests organizer review.
- Tourist and public pages do not expose raw backend object names.
- Product shells do not use Ant Design `Layout`, `Sider`, or `Menu`.
- Qwen/QwenPaw is still not required for the deterministic demo path.
- Known warning: Vite reports the main JS chunk is larger than 500 kB after minification.
- Known warning: backend tests emit existing FastAPI/Starlette deprecation warnings.

## v0.5 Conclusion

v0.5 UI polish Task 1-12 is verified. The deterministic demo remains runnable without `DASHSCOPE_API_KEY`, and the frontend now has role-separated product pages, active v0.5 Playwright visual smoke, and screenshot evidence.

## v0.6 Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `npm.cmd run test` | `apps/web` | 0 | 17 test files passed, 57 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3206 modules transformed; Vite emitted a large chunk warning for `assets/index-DnDdwqZa.js` at 765.53 kB. |
| `npm.cmd exec playwright test tests/e2e/v06-i18n.spec.ts` | `apps/web` | 0 | 9 v0.6 i18n visual tests passed and generated 9 screenshots. |
| `npm.cmd exec playwright test` | `apps/web` | 0 | 14 active visual tests passed; 4 v0.4 historical baseline tests skipped. |
| `python -m pytest -q` | `apps/api` | 0 | 34 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |

### Screenshot Evidence

| Route | Locale | Viewport | Screenshot | Manual inspection |
| --- | --- | --- | --- | --- |
| `/login` | `zh-Hans` | 1280x720 | `docs/research/assets/v0.6-i18n-verification/01-login-zh-Hans.png` | Nonblank; Simplified Chinese product entry and demo accounts visible. |
| `/organizer/dashboard` | `zh-Hans` | 1440x900 | `docs/research/assets/v0.6-i18n-verification/02-organizer-dashboard-zh-Hans.png` | Nonblank; organizer dashboard labels localized. |
| `/merchant/events/demo-night-tour/status` | `zh-Hans` | 390x844 | `docs/research/assets/v0.6-i18n-verification/03-merchant-status-zh-Hans-mobile.png` | Nonblank; quick actions remain usable and sold-out feedback is localized. |
| `/public/events/demo-night-tour` | `zh-Hans` | 390x844 | `docs/research/assets/v0.6-i18n-verification/04-public-h5-zh-Hans-mobile.png` | Nonblank; public H5 is visitor-facing and localized. |
| `/login` | `zh-Hant` | 1280x720 | `docs/research/assets/v0.6-i18n-verification/05-login-zh-Hant.png` | Nonblank; Traditional Chinese product entry visible. |
| `/organizer/dashboard` | `zh-Hant` | 1440x900 | `docs/research/assets/v0.6-i18n-verification/06-organizer-dashboard-zh-Hant.png` | Nonblank; organizer dashboard and navigation localized. |
| `/merchant/events/demo-night-tour/status` | `zh-Hant` | 390x844 | `docs/research/assets/v0.6-i18n-verification/07-merchant-status-zh-Hant-mobile.png` | Nonblank; merchant quick actions fit mobile width. |
| `/public/events/demo-night-tour` | `zh-Hant` | 390x844 | `docs/research/assets/v0.6-i18n-verification/08-public-h5-zh-Hant-mobile.png` | Nonblank; public H5 remains visitor-facing. |
| `/login` | `en` | 1280x720 | `docs/research/assets/v0.6-i18n-verification/09-login-en.png` | Nonblank; English fallback works. |

### Boundary Notes

- Locale preference is stored as `zhiyin.locale`.
- Locale switching does not replace backend-backed demo auth.
- Public H5 language switching works without login.
- Merchant sold-out quick action still sends `inventory_status: "sold_out"` and `available_for_visitors: false`.
- Tourist/public source gates reject raw backend object names.
- Public H5 screenshots do not expose `PlanVersion`, `AgentTrace`, `RecoveryProposal`, `runtime_state`, or `current_plan_version`.
- No model API is required for translation.
- Known warning: mobile full-page screenshots still show the fixed bottom navigation overlaying long captures. This is inherited from v0.5 visual smoke and does not show unresolved translated-text overflow.
- Known warning: Vite reports the main JS chunk is larger than 500 kB after minification.
- Known warning: backend tests emit existing FastAPI/Starlette deprecation warnings.

## Conclusion

v0.6 i18n is verified. The deterministic demo remains runnable without `DASHSCOPE_API_KEY`, and the frontend now defaults to Simplified Chinese, supports Traditional Chinese, keeps English fallback, and preserves backend-backed auth and role routing.

## v0.7 Documentation Verification

| Check | Result |
| --- | --- |
| Required v0.7 proposal documents exist | pass |
| Required v0.7 research documents exist | pass |
| Screenshot walkthrough directory exists | pass |
| Placeholder scan | pass |
| Unsupported Qwen/real-integration claim scan | pass |
| Product runtime source diff check | pass |

### v0.7 Artifacts

| Artifact | Path |
| --- | --- |
| Spec | `docs/proposal/v0.7-demo-narrative-spec.md` |
| Implementation plan | `docs/proposal/v0.7-demo-narrative-implementation-plan.md` |
| Demo narrative | `docs/research/v0.7-demo-narrative.md` |
| Vision-to-MVP gap | `docs/research/v0.7-vision-to-mvp-gap.md` |
| Screenshot walkthrough | `docs/research/v0.7-screenshot-walkthrough.md` |
| Competition brief | `docs/research/v0.7-competition-brief.md` |
| Presentation storyboard | `docs/research/v0.7-presentation-storyboard.md` |
| Screenshot evidence | `docs/research/assets/v0.7-demo-walkthrough/` |

### v0.7 Verification Commands

| Command | Working directory | Result |
| --- | --- | --- |
| `Test-Path ...` required v0.7 docs and screenshot directory | project root | pass; all returned `True` |
| `Get-ChildItem docs\research\assets\v0.7-demo-walkthrough` | project root | pass; 9 PNG screenshots listed |
| `rg -n "T[O]DO\|T[B]D\|待[补]\|占[位]" ...` | project root | pass; no matches |
| `rg -n "already uses Qwen[P]aw\|..." docs\research -g "v0.7-*.md"` | project root | pass; no unsupported implementation claims |
| `git diff --name-only -- apps\api apps\web\src data` | project root | pass; no runtime product source changes |

### v0.7 Boundary Notes

- No backend workflow, frontend runtime, database schema, auth, or demo data changes were made.
- No v0.7 Playwright screenshot spec was created; the walkthrough reuses verified v0.5/v0.6 screenshot evidence.
- The v0.7 screenshot walkthrough marks exact sold-out and approved-v2 moments as documented replacements.
- Qwen/QwenPaw is positioned only as a future advisory layer.

## v0.8 Agent Capability Verification

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest tests/test_v08_agent_contracts.py tests/test_v08_agent_runtime.py tests/test_v08_planning_agent.py tests/test_v08_recovery_agent.py tests/test_v08_review_agent.py -q` | `apps/api` | 0 | 8 v0.8 P0 tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 42 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `rg -n "DASHSCOPE_API_KEY|required|must provide" apps\api docs\ai docs\proposal\v0.8-agent-capability-implementation-plan.md` | project root | 0 | Matches describe optional/non-required model API behavior or existing optional adapter paths; no route requires the key. |
| `git diff --name-only -- apps\web\src apps\web\tests package.json apps\web\package.json` | project root | 0 | No frontend source, test, or package files changed in v0.8 P0. |

### v0.8 Boundary Checks

| Check | Result |
| --- | --- |
| Deterministic Agent runtime runs without `DASHSCOPE_API_KEY` | pass |
| Planning run records `AgentRun`, enriched `AgentStep`, and `AgentToolCall` evidence | pass |
| Merchant sold-out creates `Incident` plus Agent drafts | pass |
| Agent drafts do not create `PlanVersion` v2 before organizer approval | pass |
| Recovery approval remains the v2/public-notice publication gate | pass |
| Public notice draft avoids backend/model terms checked by v0.8 recovery tests | pass |
| Review draft references metrics/incidents/proposals/notices | pass |
| Qwen/QwenPaw remains optional | pass |
| Frontend regression not rerun | not run; no frontend files changed |

## v0.9 Agent Evidence UI Verification

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `npm.cmd run test -- v09-agent-api.test.ts v09-agent-components.test.tsx v09-agent-evidence-pages.test.tsx v09-agent-boundaries.test.ts` | `apps/web` | 0 | 4 v0.9 test files passed, 13 tests passed. |
| `npm.cmd run test` | `apps/web` | 0 | 21 frontend test files passed, 70 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3215 modules transformed; Vite emitted the existing >500 kB chunk warning. Initial build attempt exposed test-source TS target issues (`Array.at`, `replaceAll`), which were fixed before the passing run. |
| `npm.cmd exec playwright test` | `apps/web` | 0 | 18 active Playwright tests passed, 4 historical v0.4 tests skipped; v0.9 screenshots regenerated. |
| `python -m pytest -q` | `apps/api` | 0 | 42 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |

### Screenshot Evidence

| Route | Screenshot |
| --- | --- |
| `/organizer/events/demo-night-tour` | `docs/research/assets/v0.9-agent-evidence/01-organizer-workspace-agent-evidence.png` |
| `/organizer/events/demo-night-tour/exceptions` | `docs/research/assets/v0.9-agent-evidence/02-organizer-exception-agent-drafts.png` |
| `/organizer/events/demo-night-tour/review` | `docs/research/assets/v0.9-agent-evidence/03-organizer-review-agent-evidence.png` |
| `/public/events/demo-night-tour` | `docs/research/assets/v0.9-agent-evidence/04-public-h5-no-agent-leakage-mobile.png` |

### Boundary Checks

| Check | Result |
| --- | --- |
| Agent evidence visible on organizer workspace | pass |
| Agent evidence visible on organizer exception center | pass |
| Agent evidence visible on organizer review center | pass |
| Merchant pages do not expose raw Agent internals | pass |
| Tourist/public pages do not expose raw Agent/backend/model terms | pass |
| Public H5 remains unauthenticated | pass |
| Merchant sold-out quick action still triggers organizer review | pass |
| Qwen/QwenPaw remains optional and non-required | pass |

### Boundary Scan Commands

| Command | Working directory | Exit code | Result |
| --- | --- | --- | --- |
| `rg -n "DASHSCOPE_API_KEY|required Qwen|required QwenPaw|must provide" apps docs` | project root | 0 | Matches are optional/non-required behavior, tests, specs, or historical verification notes; no required model API path was introduced. |
| `rg -n "AgentRun|AgentDraft|AgentToolCall|AgentModelCall|AgentEvaluation|Qwen|QwenPaw|fallback|schema|backend" apps\web\src\pages\merchant apps\web\src\pages\tourist apps\web\src\pages\public` | project root | 1 | No matches; `rg` exit 1 is expected for no matches. |

## v1.0 Qwen Controlled Draft Verification

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest tests/test_v10_draft_generation.py tests/test_v10_qwen_draft_runtime.py tests/test_v10_agent_evidence_api.py -q` | `apps/api` | 0 | 15 v1.0 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 57 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test -- v10-agent-model-api.test.ts v10-agent-model-components.test.tsx v10-agent-model-pages.test.tsx v09-agent-boundaries.test.ts` | `apps/web` | 0 | 4 focused frontend test files passed, 10 tests passed. |
| `npm.cmd run test` | `apps/web` | 0 | 24 frontend test files passed, 78 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3216 modules transformed; existing >500 kB chunk warning remains for `assets/index-CQMjPpfb.js` at 786.59 kB. |
| `npm.cmd exec playwright test tests/e2e/v10-qwen-draft-evidence.spec.ts` | `apps/web` | 0 | 3 v1.0 Playwright smoke tests passed and generated 3 screenshots. |
| `npm.cmd exec playwright test` | `apps/web` | 0 | 21 active Playwright tests passed, 4 historical v0.4 tests skipped. |

### v1.0 Screenshot Evidence

| Route | Screenshot |
| --- | --- |
| `/organizer/events/demo-night-tour/exceptions` | `docs/research/assets/v1.0-qwen-controlled-draft/01-exception-model-evidence.png` |
| `/organizer/events/demo-night-tour/review` | `docs/research/assets/v1.0-qwen-controlled-draft/02-review-model-evidence.png` |
| `/public/events/demo-night-tour` | `docs/research/assets/v1.0-qwen-controlled-draft/03-public-h5-no-model-terms.png` |

### v1.0 Boundary Checks

| Check | Result |
| --- | --- |
| Demo runs without `DASHSCOPE_API_KEY` | pass |
| Qwen path is optional behind `AGENT_DRAFT_BACKEND=qwen` | pass |
| Missing provider key records skipped model calls and deterministic fallback | pass |
| Invalid JSON/schema/provider errors fall back deterministically | pass |
| Public notice blocks raw model/backend terms | pass |
| Model output cannot create plan versions or publish notices | pass |
| Merchant/tourist/public pages do not expose raw model evidence | pass |
| QwenPaw is not claimed as implemented workflow orchestration | pass |

### v1.0 Boundary Scan Commands

| Command | Working directory | Exit code | Result |
| --- | --- | --- | --- |
| `rg -n "DASHSCOPE_API_KEY|required Qwen|required QwenPaw|must provide" apps docs` | project root | 0 | Matches are optional/non-required behavior, tests, specs, implementation plan examples, or adapter code; no required model API path was introduced. |
| `rg -n "AgentModelCall|Qwen|QwenPaw|fallback|schema|backend|deterministic" apps\web\src\pages\merchant apps\web\src\pages\tourist apps\web\src\pages\public` | project root | 1 | No matches; `rg` exit 1 is expected for no matches. |

### v1.0 Verification Notes

- Initial Playwright/build attempts in the managed sandbox hit Windows `EPERM` when writing `test-results` or `tsconfig.tsbuildinfo`; the same commands passed when rerun with approved project write access.
- The v1.0 focused smoke screenshots were manually inspected after generation. The organizer exception/review pages show model draft evidence, and the public H5 screenshot remains visitor-facing.

## v1.1 Live Qwen Smoke And Demo Material Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python scripts\live_qwen_smoke.py` with `RUN_LIVE_QWEN_SMOKE=1`, `AGENT_DRAFT_BACKEND=qwen`, `QWEN_MODEL=qwen-plus`, `QWEN_TIMEOUT_SECONDS=30` | `apps/api` | 2 | Wrote sanitized blocked evidence because `DASHSCOPE_API_KEY` was not present in the process environment; deterministic fallback probe completed. Initial sandboxed attempt hit SQLite `readonly database`, then the same non-secret command wrote evidence with approved project write access. |
| `python -m pytest tests/test_v11_live_qwen_smoke_script.py tests/test_v10_qwen_draft_runtime.py -q` | `apps/api` | 0 | 17 selected backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 69 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 24 frontend test files passed, 78 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed after fixing v1.1 Playwright result typing; 3216 modules transformed; existing >500 kB chunk warning remains. Initial sandboxed build attempt also hit Windows `EPERM` on `tsconfig.tsbuildinfo`. |
| `npm.cmd exec playwright test tests/e2e/v11-live-qwen-smoke-evidence.spec.ts` | `apps/web` | 0 | 2 tests skipped because the recorded v1.1 smoke outcome is `blocked`, not `live_success`. |
| `npm.cmd exec playwright test` | `apps/web` | 0 | 21 active Playwright tests passed, 6 tests skipped. The skips include 4 historical v0.4 tests and 2 v1.1 live-success-only screenshot tests. |
| `rg -n "sk-[A-Za-z0-9]{16,}\|Authorization: Bearer [A-Za-z0-9]" apps docs` | project root | 1 | No real API key or Authorization bearer pattern found; `rg` exit 1 is expected for no matches. |
| `rg -n "AgentModelCall\|Qwen\|QwenPaw\|fallback\|schema\|backend\|deterministic" apps\web\src\pages\merchant apps\web\src\pages\tourist apps\web\src\pages\public` | project root | 1 | No raw model/backend terms in merchant, tourist, or public page source; `rg` exit 1 is expected for no matches. |

### v1.1 Artifacts

| Artifact | Path |
| --- | --- |
| Guarded smoke script | `apps/api/scripts/live_qwen_smoke.py` |
| Smoke contract tests | `apps/api/tests/test_v11_live_qwen_smoke_script.py` |
| Smoke result document | `docs/research/v1.1-live-qwen-smoke.md` |
| Sanitized smoke JSON | `docs/research/assets/v1.1-live-qwen-smoke/live-qwen-smoke-result.json` |
| Live evidence Playwright spec | `apps/web/tests/e2e/v11-live-qwen-smoke-evidence.spec.ts` |
| Demo script | `docs/research/v1.1-demo-script.md` |
| Architecture brief | `docs/research/v1.1-architecture-brief.md` |
| Slide outline | `docs/research/v1.1-slide-outline.md` |
| Screenshot index | `docs/research/v1.1-screenshot-index.md` |

### v1.1 Boundary Checks

| Check | Result |
| --- | --- |
| Live smoke requires `RUN_LIVE_QWEN_SMOKE=1` | pass |
| Live smoke requires `AGENT_DRAFT_BACKEND=qwen` | pass |
| Live smoke requires `DASHSCOPE_API_KEY` from process env and does not store it | pass |
| Live smoke is not part of default automated tests | pass |
| Current live smoke artifact honestly records `blocked`, not `live_success` | pass |
| Deterministic fallback remains verified after blocked smoke | pass |
| No real API key or Authorization header appears in repo evidence | pass |
| Merchant/tourist/public pages do not expose raw model evidence | pass |
| v1.1 live screenshots are skipped unless outcome is `live_success` | pass |
| Demo materials do not claim QwenPaw implementation | pass |

### v1.1 Verification Notes

- The current v1.1 evidence does not prove live Qwen provider success. It proves the guarded live path exists, safely blocks without a process key, writes sanitized blocked evidence, and verifies deterministic fallback.
- Do not use v1.1 live screenshot paths in slides while the outcome remains `blocked`.
- Full Playwright regenerated several historical screenshots during verification; those generated diffs were cleaned because they were not v1.1 plan outputs.

## v1.2 Backend P0 Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest apps/api/tests/test_v12_event_page_merchant_edge.py -q` | project root | 0 | 12 v1.2 event page, merchant edge, touchpoint, coupon, review, and operation suggestion tests passed. |
| `python -m pytest apps/api/tests/test_v12_qwen_schema_success.py apps/api/tests/test_v10_draft_generation.py apps/api/tests/test_v10_qwen_draft_runtime.py -q` | project root | 0 | 16 Qwen parser/sanitizer and existing controlled-draft runtime tests passed. |
| `python -m pytest apps/api/tests/test_v12_store_models.py apps/api/tests/test_v12_event_page_merchant_edge.py apps/api/tests/test_v12_qwen_schema_success.py apps/api/tests/test_v08_planning_agent.py apps/api/tests/test_v08_recovery_agent.py apps/api/tests/test_v10_draft_generation.py apps/api/tests/test_v10_qwen_draft_runtime.py -q` | project root | 0 | 47 Task 1-7 backend core tests passed. |
| `python -m pytest tests/test_review.py::test_review_report_mentions_approved_actions -q` | `apps/api` | 0 | Existing review responsibility-boundary regression passed after restoring the Chinese lesson text. |
| `python -m pytest -q` | `apps/api` | 0 | 101 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |

### Boundary Checks

| Check | Result |
| --- | --- |
| Default deterministic demo still does not require `DASHSCOPE_API_KEY` | pass |
| Event page draft/publish requires approved current plan | pass |
| Stale event page is not attached after recovery creates current v2 | pass |
| Merchant workbench exposes only the merchant's current package children | pass |
| Touchpoint interactions strip visitor identity metadata | pass |
| Coupon claim/redeem metrics appear in review report | pass |
| Operation suggestions use current approved plan merchant/route scope | pass |
| Stale operation suggestions disappear after runtime condition resolves | pass |
| Stale operation suggestion approval is rejected | pass |
| Queue notice suggestion payload refreshes when runtime queue state changes | pass |
| Qwen prompt sanitizer removes control fields without mutating input | pass |
| Unsafe Qwen output inside `agent_draft` wrapper is still rejected | pass |
| No real Qwen live call was run for v1.2 Task 1-7 | pass |

### v1.2 Verification Notes

- Backend pytest must be run serially against the default SQLite store. A parallel pytest attempt created a `database is locked` failure; after stopping the stale Python process and rerunning serially, the full backend suite passed.
- Task 8-10 frontend exposure and smoke were completed after this backend P0 checkpoint; see the full v1.2 verification section below.
- The existing FastAPI/Starlette deprecation warnings remain unchanged.

## v1.2 Event Page And Merchant Edge Full Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `npm.cmd run test -- tests/v09-agent-boundaries.test.ts tests/public-review.test.tsx tests/v05-ui-contracts.test.tsx --reporter=verbose` | `apps/web` | 0 | Focused regression rerun passed: 3 files, 10 tests. This verified the public source gate, public Event Page language switching, and Ant Design test cleanup fix. |
| `npm.cmd run test` | `apps/web` | 0 | 26 frontend test files passed, 90 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3216 modules transformed. Existing >500 kB chunk warning remains. |
| `npm.cmd exec playwright test tests/e2e/v12-event-page-merchant-edge.spec.ts` | `apps/web` | 0 | 1 v1.2 Playwright visual smoke passed and generated five v1.2 screenshots. |
| `npm.cmd exec playwright test` | `apps/web` | 0 | 22 active Playwright tests passed, 6 tests skipped. Skips were historical v0.4 and v1.1 live-success-only evidence tests. Initial sandboxed attempt hit Windows `EPERM` writing `test-results/.last-run.json`; rerun with approved project write access passed. |
| `python -m pytest -q` | `apps/api` | 0 | 101 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |
| `rg -n "sk-[A-Za-z0-9]{16,}\|Authorization[: ]+Bearer\|DASHSCOPE_API_KEY\\s*=" apps docs .gitignore README.md` | project root | 0 | Broad scan matched documentation examples and test assertions only; no real key or bearer token was found. |
| `rg -n "sk-[A-Za-z0-9._-]{20,}\|Bearer\\s+sk-[A-Za-z0-9._-]{20,}\|DASHSCOPE_API_KEY\\s*=\\s*sk-" apps docs README.md .gitignore` | project root | 1 | Strict real-key scan found no matches; `rg` exit 1 is expected for no matches. |
| `rg -n "([A-Z]:\\\\Users\\\\[^\\\\]+\|[A-Z]:\\\\rz\\\\\|[A-Z]:/rz/)" docs apps README.md` | project root | 1 | No local absolute path matches; `rg` exit 1 is expected for no matches. |
| `rg -n "AgentDraft\|AgentRun\|PlanVersion\|RecoveryProposal\|qwen\|dashscope\|schema_failed\|approval_status" apps\\web\\src\\pages\\public apps\\web\\src\\pages\\merchant apps\\web\\src\\i18n\\dictionaries` | project root | 1 | Public/merchant pages and dictionaries do not expose the listed internal terms; `rg` exit 1 is expected for no matches. |

### v1.2 Screenshot Evidence

| Surface | Path |
| --- | --- |
| Organizer event page status | `docs/research/assets/v1.2-event-page-merchant-edge/01-organizer-event-page-status.png` |
| Merchant edge package | `docs/research/assets/v1.2-event-page-merchant-edge/02-merchant-edge-package.png` |
| Public Event Page mobile | `docs/research/assets/v1.2-event-page-merchant-edge/03-public-event-page-mobile.png` |
| Exception center operation suggestion | `docs/research/assets/v1.2-event-page-merchant-edge/04-exception-operation-suggestion.png` |
| Review touchpoint summary | `docs/research/assets/v1.2-event-page-merchant-edge/05-review-touchpoint-summary.png` |

### v1.2 Boundary Checks

| Check | Result |
| --- | --- |
| Public H5 remains unauthenticated | pass |
| Public H5 is framed as Event Page rather than backend preview | pass |
| Merchant package is merchant-scoped in backend and UI | pass |
| Scan, claim, and redeem interactions remain anonymous demo interactions | pass |
| Merchant sold-out quick action still triggers runtime/incident path | pass |
| Operation suggestions cite evidence and do not bypass recovery plan approval semantics | pass |
| Review report includes touchpoint summary, merchant outcomes, and extension tasks | pass |
| Optional Qwen parser accepts a single `agent_draft` wrapper | pass |
| Unsafe Qwen output fields remain rejected | pass |
| No Qwen/DashScope key is required for deterministic demo | pass |
| No QwenPaw workflow orchestration is claimed | pass |
| Public/merchant source does not expose raw model/backend terms | pass |
| No real key or local absolute path was found by final scans | pass |

### v1.2 Verification Notes

- The v1.2 Playwright spec is a deterministic mocked-API visual/product-flow smoke. It verifies route-level UI, screenshots, and public-copy boundaries without needing a running backend.
- Backend integration and authority are verified by the FastAPI pytest suite. A future live E2E can add real demo login plus running FastAPI/Vite if needed.
- Full Playwright regenerated several historical screenshot artifacts in addition to the new v1.2 screenshots.
- The existing frontend bundle-size warning remains unchanged and is not a v1.2 regression.

## v1.3 Live Demo Hardening Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python scripts\reset_demo_state.py` | `apps/api` | 0 | Reset `demo-night-tour` and printed demo accounts `organizer.demo`, `merchant.m001.demo`, and `tourist.demo`. |
| `python -m pytest -q` | `apps/api` | 0 | 105 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 26 frontend test files passed, 90 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3216 modules transformed; existing >500 kB chunk warning remains for `assets/index-D2XlfyTl.js` at 837.35 kB. |
| `npm.cmd exec -- playwright test --list` | `apps/web` | 0 | Listed 28 default Playwright tests in 7 files; the live-only `v13-live-demo-smoke.spec.ts` is excluded from the mocked suite. |
| `npm.cmd exec -- playwright test` | `apps/web` | 0 | Default mocked Playwright suite passed: 22 passed, 6 skipped. |
| `npm.cmd exec -- playwright test tests/e2e/v13-live-demo-smoke.spec.ts --config playwright.live.config.ts` | `apps/web` | 0 | v1.3 live smoke passed: 1 test passed and 5 screenshots generated. |
| `python scripts\live_qwen_smoke.py` with guarded Qwen env and no `DASHSCOPE_API_KEY` | `apps/api` | 1 | Wrote sanitized `blocked` optional Qwen evidence; blocked reason is missing process environment key. Initial sandboxed attempt hit SQLite readonly access, then the same non-secret command wrote evidence with approved project write access. |
| `rg -n "sk-[A-Za-z0-9._-]{20,}\|Bearer\s+sk-[A-Za-z0-9._-]{20,}\|DASHSCOPE_API_KEY\s*=\s*sk-" apps docs README.md .gitignore` | project root | 1 | Strict secret scan found no real key or bearer-token matches; `rg` exit 1 is expected for no matches. |
| `rg -n "([A-Z]:\\Users\\[^\\]+\|[A-Z]:\\rz\\\|[A-Z]:/rz/)" docs apps README.md` | project root | 1 | Local absolute path scan found no matches; `rg` exit 1 is expected for no matches. |
| `rg -n "AgentDraft\|AgentRun\|PlanVersion\|RecoveryProposal\|qwen\|dashscope\|schema_failed\|approval_status" apps\web\src\pages\public apps\web\src\pages\merchant apps\web\src\i18n\dictionaries` | project root | 1 | Public/merchant pages and dictionaries do not expose the listed internal terms; `rg` exit 1 is expected for no matches. |

### v1.3 Screenshot Evidence

| Surface | Path |
| --- | --- |
| Organizer workspace | `docs/research/assets/v1.3-live-demo-smoke/01-live-organizer-workspace.png` |
| Merchant package | `docs/research/assets/v1.3-live-demo-smoke/02-live-merchant-package.png` |
| Exception suggestion | `docs/research/assets/v1.3-live-demo-smoke/03-live-exception-suggestion.png` |
| Public event page | `docs/research/assets/v1.3-live-demo-smoke/04-live-public-event-page.png` |
| Review metrics | `docs/research/assets/v1.3-live-demo-smoke/05-live-review-metrics.png` |

### v1.3 Boundary Checks

| Check | Result |
| --- | --- |
| Reset command seeds deterministic demo accounts and event | pass |
| Live Playwright config starts real FastAPI and Vite | pass |
| Default mocked Playwright suite remains separate from live-only smoke | pass |
| Live smoke uses real backend API and no Playwright route mocks | pass |
| Public H5 remains unauthenticated | pass |
| Public scan, claim, and redeem use actual H5 UI controls | pass |
| Public interaction controls expose only visitor-safe current-plan fields | pass |
| Review report reflects public touchpoint metrics and merchant outcomes | pass |
| Qwen live smoke remains optional and is honestly classified as `blocked` without a process key | pass |
| No real key or local absolute path was found by final scans | pass |
| Public/merchant source does not expose raw model/backend terms | pass |
| QwenPaw workflow orchestration remains unimplemented | pass |

### v1.3 Verification Notes

- The first Task 7 default Playwright run failed because the default mocked config picked up the live-only v1.3 spec without starting FastAPI. This was fixed by excluding `v13-live-demo-smoke.spec.ts` from `apps/web/playwright.config.ts`; the live spec remains covered by `apps/web/playwright.live.config.ts`.
- Full Playwright verification regenerated several historical screenshot artifacts. Only v1.3 evidence screenshots are part of v1.3 outputs.
- The current optional Qwen evidence does not prove live provider success. It proves the guarded path blocks safely without a process key, writes sanitized evidence, and leaves the deterministic live demo valid.

## v1.4 QwenPaw Multi-Agent Orchestration Spike Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest tests/test_v14_workflow_contract.py tests/test_v14_tool_registry.py tests/test_v14_qwenpaw_shadow_runtime.py tests/test_v14_qwenpaw_shadow_api.py -q` | `apps/api` | 0 | 14 focused v1.4 workflow, permissioned-tool, shadow-runtime, and API tests passed; 3 existing FastAPI/Starlette deprecation warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 119 backend tests passed; 3 existing FastAPI/Starlette deprecation warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 28 frontend test files passed, 94 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3216 modules transformed; existing >500 kB chunk warning remains for `assets/index-DwOVRZL_.js` at 841.37 kB. |
| `npm.cmd exec -- playwright test` | `apps/web` | 0 | Default mocked Playwright suite passed: 22 passed, 6 skipped. |
| `npm.cmd exec -- playwright test tests/e2e/v13-live-demo-smoke.spec.ts --config playwright.live.config.ts` | `apps/web` | 0 | v1.3 live smoke passed after clearing a stale local Vite process on port 5179: 1 test passed. |
| `rg -n 'sk-[A-Za-z0-9._-]{20,}\|Bearer\\s+sk-[A-Za-z0-9._-]{20,}\|DASHSCOPE_API_KEY\\s*=\\s*sk-' apps docs README.md .gitignore` | project root | 1 | Strict secret scan found no real key or bearer-token matches; `rg` exit 1 is expected for no matches. |
| `rg -n '([A-Z]:\\\\Users\\\\[^\\\\]+\|[A-Z]:\\\\rz\\\\\|[A-Z]:/rz/)' docs apps README.md` | project root | 1 | Local absolute path scan found no matches; `rg` exit 1 is expected for no matches. |
| `rg -n 'QwenPaw\|AgentRun\|AgentDraft\|AgentModelCall\|AgentEvaluation\|schema\|fallback\|backend\|deterministic\|PlanVersion\|RecoveryProposal' apps\\web\\src\\pages\\public apps\\web\\src\\pages\\merchant apps\\web\\src\\pages\\tourist` | project root | 1 | Public, merchant, and tourist page sources do not expose the listed internal QwenPaw/model/backend terms; `rg` exit 1 is expected for no matches. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `docs/research/v1.4-qwenpaw-orchestration-spike-smoke.md` | Documents the shadow run, advisory-only boundary, no required provider credentials, and optional live-provider status. |
| `docs/research/assets/v1.4-qwenpaw-orchestration-spike/shadow-run-evidence.json` | Sanitized evidence with `outcome=shadow_success`, `backend=qwenpaw_fake`, `agent_run_mode=qwenpaw_workflow`, `authoritative_mutation=false`, `human_approval_required=true`, 3 permission decisions, and 1 denied permission. |

### v1.4 Boundary Checks

| Check | Result |
| --- | --- |
| QwenPaw shadow path is organizer-only | pass |
| Shadow run is advisory and cannot approve, publish, or mutate authoritative runtime/business state | pass |
| Permissioned tool calls record allowed and denied decisions | pass |
| Unsafe adapter output falls back to safe deterministic advisory output | pass |
| Missing Origin plus demo CSRF is rejected for the QwenPaw shadow endpoint | pass |
| Frontend ignores stale shadow orchestration responses when the selected incident changes | pass |
| Merchant, tourist, and public pages do not expose raw QwenPaw/model/backend terms | pass |
| v1.3 deterministic live demo remains verified after v1.4 | pass |
| No real provider API key, bearer token, or local absolute path was found by final scans | pass |

### v1.4 Verification Notes

- Backend pytest must be run serially against the default SQLite store. An initial verification attempt ran focused and full pytest concurrently, which reproduced the known SQLite lock/seed-state failure. After stopping stale local Python services and rerunning serially, both focused and full backend suites passed.
- The first v1.3 live smoke attempt found a stale local Vite process on port 5179 from an earlier run. After stopping that process and the failed-run Python residue, the live smoke passed.
- Full Playwright and live smoke regenerated several historical screenshot artifacts. They are verification byproducts and are not part of the v1.4 documentation commit.
- v1.4 does not prove live QwenPaw provider execution. It proves a guarded QwenPaw-style shadow orchestration contract, fake-adapter evidence path, organizer UI exposure, and non-authoritative safety boundary.

## v1.5 Real QwenPaw Guarded Smoke Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest tests/test_v15_live_qwenpaw_smoke_script.py -q` | `apps/api` | 0 | 21 v1.5 script tests passed; tests cover live flag guard, localhost guard, redaction, bounded response/session handling, optional `QWENPAW_AGENT_ID` header routing, `trust_env=False`, fake success, blocked connection failure, failed QwenPaw SSE/provider responses, token-stream compaction, 200-level QwenPaw error payloads, Markdown evidence whitespace hygiene, and provider-error classification boundaries. |
| `python -m pytest tests/test_v14_workflow_contract.py tests/test_v14_tool_registry.py tests/test_v14_qwenpaw_shadow_runtime.py tests/test_v14_qwenpaw_shadow_api.py tests/test_v15_live_qwenpaw_smoke_script.py -q` | `apps/api` | 0 | 35 focused v1.4/v1.5 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 140 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 28 frontend test files passed, 94 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; 3216 modules transformed; existing >500 kB chunk warning remains for `assets/index-DwOVRZL_.js` at 841.37 kB. |
| `npm.cmd exec -- playwright test` | `apps/web` | 0 | Default mocked Playwright suite passed: 22 passed, 6 skipped. |
| `npm.cmd exec -- playwright test tests/e2e/v13-live-demo-smoke.spec.ts --config playwright.live.config.ts` | `apps/web` | 0 | v1.3 live smoke passed: 1 test passed. |
| `where.exe qwenpaw` | project root | 1 | No local `qwenpaw` executable was found. |
| `Test-NetConnection -ComputerName 127.0.0.1 -Port 8088` | project root | 0 | Command completed with `TcpTestSucceeded=False`; no local QwenPaw service was listening on port 8088. |
| `python scripts\live_qwenpaw_smoke.py` without `RUN_LIVE_QWENPAW_SMOKE` | `apps/api` | 1 | Wrote sanitized `blocked` evidence with `blocked_reason=RUN_LIVE_QWENPAW_SMOKE is required` and `request_sent=false`. Initial sandboxed attempt could not write `docs/research`; rerun with approved project write access succeeded. |
| `python scripts\live_qwenpaw_smoke.py` with `RUN_LIVE_QWENPAW_SMOKE=1`, `QWENPAW_BASE_URL=http://127.0.0.1:8088` against the local QwenPaw service | `apps/api` | 1 | Wrote sanitized `blocked` evidence with `request_sent=true`, `response_status_code=200`, `blocked_reason=QwenPaw model is not configured`, and `failure_kind=provider_error`. |
| strict secret/password scan | project root | 1 | `rg` found no real key, bearer-token, provider key assignment, or QwenPaw password matches in `apps`, `docs`, `README.md`, or `.gitignore`; exit 1 is expected for no matches. |
| local-path scan | project root | 1 | `rg` found no local absolute path matches in `docs`, `apps`, or `README.md`; exit 1 is expected for no matches. |
| public/merchant/tourist boundary scan | project root | 1 | `rg` found no raw QwenPaw/model/backend/internal terms in public, merchant, or tourist page source; exit 1 is expected for no matches. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `apps/api/scripts/live_qwenpaw_smoke.py` | Manual localhost-only smoke script guarded by `RUN_LIVE_QWENPAW_SMOKE=1`, with `trust_env=False`, optional `QWENPAW_AGENT_ID` routing via `X-Agent-Id`, bounded response reads, bounded session/agent IDs, and redaction for secrets and local paths. |
| `apps/api/tests/test_v15_live_qwenpaw_smoke_script.py` | Contract tests for guard rails, prompt sanitization, response parsing, redaction, bounded evidence, fake live success, connection blocking, and proxy/environment isolation. |
| `docs/research/v1.5-real-qwenpaw-guarded-smoke.md` | Sanitized smoke report. The original v1.5 outcome was `blocked`; the current artifact has since been updated by v1.6 to `live_success`. |
| `docs/research/assets/v1.5-real-qwenpaw-guarded-smoke/live-qwenpaw-smoke-result.json` | Sanitized JSON evidence. The original v1.5 provider-error evidence was superseded by v1.6 live-success evidence after active model configuration. |

### v1.5 Boundary Checks

| Check | Result |
| --- | --- |
| Smoke refuses to send a request unless `RUN_LIVE_QWENPAW_SMOKE=1` | pass |
| Smoke rejects non-localhost `QWENPAW_BASE_URL` values | pass |
| Smoke disables environment/proxy routing with `trust_env=False` | pass |
| Optional `QWENPAW_AGENT_ID` is sent only as an explicit `X-Agent-Id` header and is recorded in sanitized evidence | pass |
| Fake transport can prove `live_success` without real network access | pass |
| QwenPaw 200-level error payloads are classified as `blocked`, not `live_success` | pass |
| Missing local QwenPaw service or missing active model configuration is classified as `blocked`, not a product failure | pass |
| Original v1.5 recorded evidence was honest `blocked/provider_error`, not live success | pass |
| Evidence stores bounded sanitized previews only | pass |
| v1.4 fake QwenPaw adapter remains the accepted product path | pass |
| v1.3 deterministic live demo remains verified | pass |
| No real key, password, bearer token, or local absolute path was found by final scans | pass |
| Public, merchant, and tourist pages do not expose raw QwenPaw/model/backend terms | pass |

### v1.5 Verification Notes

- The original v1.5 live-flag smoke reached a local QwenPaw service on `127.0.0.1:8088`, but it returned `No active model configured.` That evidence proved localhost service reachability plus safe provider-error classification, not real QwenPaw model success.
- During the first live-flag smoke attempt, the authorized process recorded an HTTP 502 while port 8088 was not listening. Root-cause probing showed `httpx` with default environment trust could be influenced by the execution environment, while `trust_env=False` produced direct localhost connection failure. The script was patched and tested to always use `trust_env=False`.
- Full Playwright and v1.3 live smoke regenerated several historical screenshot PNGs. Those PNG diffs are verification byproducts and are not part of the v1.5 documentation commits.
- Backend pytest was run serially against the default SQLite store.

## v1.6 Local QwenPaw Reachability Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `<TEMP_QWENPAW_VENV>\Scripts\qwenpaw.exe --version` | project root | 0 | Local isolated QwenPaw CLI reported `1.1.12.post1`. |
| `qwenpaw init --defaults --accept-security --force` with isolated `QWENPAW_WORKING_DIR` and `QWENPAW_SECRET_DIR` | temp workspace | 0 | Initialized QwenPaw outside the repo and reported no default model configured. |
| `Test-NetConnection -ComputerName 127.0.0.1 -Port 8088` while QwenPaw app was running | project root | 0 | Command completed with `TcpTestSucceeded=True`. |
| `python scripts\live_qwenpaw_smoke.py` with `RUN_LIVE_QWENPAW_SMOKE=1`, `QWENPAW_BASE_URL=http://127.0.0.1:8088` | `apps/api` | 1 | Wrote sanitized blocked evidence for reachable QwenPaw SSE response: `failure_kind=provider_error`, `blocked_reason=QwenPaw model is not configured`. |
| Configure active model as `opencode/deepseek-v4-flash-free` through QwenPaw `ProviderManager.activate_model()` | temp workspace | 0 | Wrote the global active model into the isolated QwenPaw secret/config directory; no process API key was present or stored. |
| `qwenpaw models list` with isolated QwenPaw dirs | temp workspace | 0 | Active model slot reported `opencode / deepseek-v4-flash-free`. |
| `python scripts\live_qwenpaw_smoke.py` with `RUN_LIVE_QWENPAW_SMOKE=1`, `QWENPAW_BASE_URL=http://127.0.0.1:8088`, `QWENPAW_AGENT_ID=QwenPaw_QA_Agent_0.2`, `QWENPAW_SMOKE_SESSION_ID=zhiyin-v15-qwenpaw-smoke-qa-agent-v1` | `apps/api` | 0 | Wrote sanitized `live_success` evidence with HTTP 200, explicit QA-agent routing, bounded response preview, and no `blocked_reason` or `failure_kind`. |
| `python -m pytest tests/test_v14_workflow_contract.py tests/test_v14_tool_registry.py tests/test_v14_qwenpaw_shadow_runtime.py tests/test_v14_qwenpaw_shadow_api.py tests/test_v15_live_qwenpaw_smoke_script.py -q` | `apps/api` | 0 | 35 focused QwenPaw backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 140 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| strict changed-file secret/password scan | project root | 1 | No real key, bearer token, provider key assignment, or QwenPaw password matches; exit 1 is expected for no matches. |
| changed evidence/docs local-path scan | project root | 1 | No local absolute path matches in changed evidence/docs/script files; exit 1 is expected for no matches. |
| `git diff --check` | project root | 0 | No whitespace errors; Git reported expected Windows line-ending warnings for touched text files. |

### v1.6 Boundary Checks

| Check | Result |
| --- | --- |
| Local QwenPaw service was reachable on localhost | pass |
| QwenPaw provider/model failure was not misclassified as `live_success` | pass |
| Active QwenPaw LLM model was configured without adding a process API key | pass |
| Guarded live smoke returned `live_success` after active model configuration and explicit QA-agent routing | pass |
| Missing/invalid agent-style QwenPaw error payloads are blocked instead of misclassified as success | pass |
| Evidence remains bounded and sanitized | pass |
| Live success remains advisory-only and non-authoritative | pass |
| v1.4 fake QwenPaw shadow path remains the accepted product path | pass |
| v1.3 deterministic live demo remains the reliable demo path | pass |

## v1.7 Real QwenPaw Guarded Adapter Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest tests/test_v15_live_qwenpaw_smoke_script.py -q` | `apps/api` | 0 | 32 v1.5/v1.7 smoke script tests passed; tests cover strict advisory qualification, unqualified missing fields, unsafe authority claims, safe authority negation, coupon/redemption authority claims, provider-error blocking, evidence persistence, localhost guard, and `trust_env=False`. |
| `python -m pytest tests/test_v14_workflow_contract.py tests/test_v14_tool_registry.py tests/test_v14_qwenpaw_shadow_runtime.py tests/test_v14_qwenpaw_shadow_api.py tests/test_v15_live_qwenpaw_smoke_script.py -q` | `apps/api` | 0 | 46 focused v1.4/v1.5/v1.7 QwenPaw backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 151 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python scripts\live_qwenpaw_smoke.py` with `RUN_LIVE_QWENPAW_SMOKE=1`, localhost QwenPaw, `QWENPAW_AGENT_ID=QwenPaw_QA_Agent_0.2`, and session `zhiyin-v17-qwenpaw-qualified-advisory-v1` | `apps/api` | 1 | Strict live smoke wrote sanitized evidence with `outcome=advisory_unqualified`, `provider_reachable=true`, `advisory_status=unqualified`, and `qualification_failure_kind=missing_fields`; QwenPaw returned HTTP 200 but did not provide the required advisory fields. |
| strict secret/password scan | project root | 1 | `rg` found no real key, bearer-token, provider key assignment, OpenAI key assignment, or QwenPaw password matches in `apps`, `docs`, `README.md`, or `.gitignore`; exit 1 is expected for no matches. |
| local-path scan | project root | 1 | `rg` found no local absolute path matches in `docs`, `apps`, or `README.md`; exit 1 is expected for no matches. |
| public/merchant/tourist boundary scan | project root | 1 | `rg` found no raw QwenPaw/model/backend/internal terms in public, merchant, or tourist page source; exit 1 is expected for no matches. |
| `git diff --check` | project root | 0 | No whitespace errors. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `apps/api/scripts/live_qwenpaw_smoke.py` | Manual localhost-only smoke script now records `provider_reachable`, `advisory_status`, field presence, sanitized advisory excerpts, and strict `advisory_qualified`/`advisory_unqualified` outcomes. |
| `apps/api/tests/test_v15_live_qwenpaw_smoke_script.py` | Contract tests for guarded live flag, localhost guard, strict advisory fields, authority-claim rejection, safe negations, bounded evidence, and blocked provider/runtime failures. |
| `docs/research/v1.5-real-qwenpaw-guarded-smoke.md` | Sanitized smoke report for the v1.7 contract. The current outcome is `advisory_unqualified`, not product orchestration. |
| `docs/research/assets/v1.5-real-qwenpaw-guarded-smoke/live-qwenpaw-smoke-result.json` | Sanitized JSON evidence with `advisory_contract_version=v1.7`, `provider_reachable=true`, `advisory_status=unqualified`, and missing-field diagnostics. |

### v1.7 Boundary Checks

| Check | Result |
| --- | --- |
| Smoke refuses to send a request unless `RUN_LIVE_QWENPAW_SMOKE=1` | pass |
| Smoke rejects non-localhost `QWENPAW_BASE_URL` values | pass |
| Smoke disables environment/proxy routing with `trust_env=False` | pass |
| Provider/runtime/QwenPaw error payloads remain `blocked` | pass |
| A non-empty response alone no longer passes the smoke | pass |
| `advisory_qualified` requires all three required advisory fields | pass |
| Unsafe authority claims produce `advisory_unqualified` | pass |
| Evidence contains only bounded sanitized previews and excerpts | pass |
| `main()` exits 0 only for `advisory_qualified` | pass |
| v1.4 fake adapter remains the accepted product path | pass |
| Merchant, tourist, and public source files remain untouched by v1.7 product behavior | pass |

### v1.7 Verification Notes

- The strict live smoke used an isolated temporary QwenPaw workspace and stopped the local QwenPaw process after the run; port 8088 was confirmed closed afterward.
- The live provider was reachable and returned HTTP 200, but the model output stayed in preamble/tool-introspection text and did not include the required advisory fields.
- The correct next step is prompt and agent-selection hardening, not product wiring.

## v1.8 QwenPaw Advisory Optimization Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest apps\api\tests\test_v15_live_qwenpaw_smoke_script.py -q` | project root | 0 | 57 smoke script tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest apps\api\tests\test_v14_qwenpaw_shadow_runtime.py apps\api\tests\test_v14_qwenpaw_shadow_api.py apps\api\tests\test_v15_live_qwenpaw_smoke_script.py -q` | project root | 0 | 64 focused QwenPaw tests passed; 3 existing FastAPI/Starlette warnings. |
| v1.8.1 QA JSON-only live matrix cell | `apps/api` | 0 | Real local QwenPaw returned `advisory_qualified`, `json_no_preamble_pass=true`, `parsed_output_format=json`, and zero repair attempts. |
| v1.8.1 QA few-shot JSON live matrix cell | `apps/api` | 0 | Real local QwenPaw returned `advisory_qualified`, `json_no_preamble_pass=true`, `parsed_output_format=json`, and zero repair attempts. |
| v1.8.1 default JSON-only live matrix cell | `apps/api` | 0 | Real local QwenPaw returned `advisory_qualified`, `json_no_preamble_pass=true`, `parsed_output_format=json`, and zero repair attempts. |
| `Test-NetConnection -ComputerName 127.0.0.1 -Port 8088` after stopping QwenPaw | project root | 0 | Command completed with `TcpTestSucceeded=False`; local QwenPaw service was stopped after the live matrix. |
| v1.8 evidence secret scan | project root | 1 | No secret, bearer-token, provider key assignment, OpenAI key assignment, or QwenPaw password matches in v1.8 evidence/docs paths; `rg` exit 1 is expected for no matches. |
| v1.8 evidence local-path scan | project root | 1 | No local absolute path matches in v1.8 evidence/docs paths; `rg` exit 1 is expected for no matches. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `apps/api/scripts/live_qwenpaw_smoke.py` | v1.8.1 parser fix: QwenPaw SSE reasoning streams are excluded, content deltas are grouped by `msg_id`, and only final assistant message text is validated. |
| `apps/api/tests/test_v15_live_qwenpaw_smoke_script.py` | Adds regression coverage for typed `thinking + text`, streamed reasoning/message deltas, and completed response envelopes that contain reasoning plus message output. |
| `docs/research/v1.8-qwenpaw-advisory-optimization.md` | Sanitized v1.8.1 smoke report with parser-fix root cause and 3-cell live matrix summary. |
| `docs/research/assets/v1.8-qwenpaw-advisory-optimization/live-qwenpaw-advisory-optimization-result-json-qa-parserfix.json` | QA agent, JSON-only prompt, `advisory_qualified`, zero repair attempts. |
| `docs/research/assets/v1.8-qwenpaw-advisory-optimization/live-qwenpaw-advisory-optimization-result-fewshot-repair-parserfix.json` | QA agent, few-shot JSON prompt, `advisory_qualified`, zero repair attempts. |
| `docs/research/assets/v1.8-qwenpaw-advisory-optimization/live-qwenpaw-advisory-optimization-result-json-default-parserfix.json` | Default agent, JSON-only prompt, `advisory_qualified`, zero repair attempts. |
| `docs/research/assets/v1.8-qwenpaw-advisory-optimization/live-qwenpaw-advisory-optimization-result.json` | Latest matrix cell, default agent JSON-only, `advisory_qualified`. |

### v1.8 Boundary Checks

| Check | Result |
| --- | --- |
| Smoke refuses to send a request unless `RUN_LIVE_QWENPAW_SMOKE=1` | pass |
| QwenPaw SSE reasoning/thinking is not validated as final advisory output | pass |
| Real local QwenPaw matrix returned 3/3 `advisory_qualified` after parser fix | pass |
| Repair history is rendered in the Markdown report | pass |
| Empty repair history records `No repair attempts were used.` | pass |
| Repair metadata does not render raw response content | pass |
| Evidence remains bounded and sanitized | pass |
| Optional live QwenPaw remains localhost-only and advisory-only | pass |
| v1.4 fake adapter remains the accepted product path | pass |
| v1.3 deterministic live demo remains the reliable demo path | pass |

### v1.8 Verification Notes

- The v1.8.1 live matrix used local QwenPaw `1.1.12.post1` through `http://127.0.0.1:8088/api/agent/process`.
- The initial live matrix failure was a parser false negative: QwenPaw returned final JSON in assistant `text`, but the previous parser flattened reasoning/thinking into the same preview.
- v1.8.1 does not make QwenPaw a product requirement and does not authorize QwenPaw output to approve, publish, mutate runtime state, or create coupon/redemption records.
- No frontend suite, build, or Playwright suite was run in this pass because v1.8.1 touched only the guarded backend smoke script, tests, and research/status docs.

## v1.9 Commercial Readiness Audit Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest -q` | `apps/api` | 0 | 176 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 28 frontend test files passed; 94 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; Vite still emitted the known large chunk warning for `assets/index-DwOVRZL_.js` at 841.37 kB. |
| `Test-Path .github` | project root | 0 | Returned `False`; no root GitHub Actions workflow directory was present. |
| `git ls-files apps\web\node_modules` | project root | 0 | Returned 0 tracked files. |
| GitHub connector repository check | GitHub | 0 | Repository is public, default branch is `main`, and archived is false. |
| GitHub connector open PR search | GitHub | 0 | No open pull requests. |
| GitHub connector open issue search | GitHub | 0 | No open issues. |
| GitHub connector PR checks | GitHub | 0 | PR #1 and PR #2 are merged. |
| GitHub connector status/workflow checks | GitHub | 0 | No commit statuses or workflow runs were observed for origin/main. |
| `ConvertFrom-Json` for v1.9 JSON artifacts | project root | 0 | Both v1.9 JSON evidence files parse successfully. |
| v1.9 placeholder scan | project root | 1 | No unresolved placeholder markers in v1.9 proposal/report/evidence files; `rg` exit 1 is expected for no matches. |
| v1.9 strict secret scan | project root | 1 | No key, bearer-token, provider-key assignment, or auth-header matches in v1.9 proposal/report/evidence files; `rg` exit 1 is expected for no matches. |
| v1.9 local-path scan | project root | 1 | No local absolute workspace paths in v1.9 proposal/report/evidence files; `rg` exit 1 is expected for no matches. |
| `git diff --check` for v1.9/docs-ai scope | project root | 0 | No whitespace errors; Git reported expected Windows line-ending warnings for touched docs/ai markdown files. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `docs/proposal/v1.9-commercial-readiness-audit-pack-spec.md` | Formal v1.9 spec for commercial-readiness classification, P0/P1 gap mapping, and acceptance criteria. |
| `docs/proposal/v1.9-commercial-readiness-audit-pack-implementation-plan.md` | Stepwise execution plan with scoped files, verification gates, and commit boundaries. |
| `docs/research/v1.9-commercial-readiness-audit.md` | Human-readable audit report and next-phase recommendation. |
| `docs/research/assets/v1.9-commercial-readiness-audit/github-repo-state.json` | Repository, branch, GitHub, dirty-worktree, and local verification snapshot. |
| `docs/research/assets/v1.9-commercial-readiness-audit/commercial-readiness-matrix.json` | Machine-readable P0/P1 readiness matrix and `v2.0-ci-repo-hygiene` recommendation. |

### v1.9 Boundary Checks

| Check | Result |
| --- | --- |
| Current implementation is classified as commercial-ready | fail by design; the correct classification is CR0 product/demo readiness plus CR1 audit-pack readiness. |
| Local product suites pass | pass. |
| GitHub release gates exist | fail; no Actions workflow/status evidence was observed. |
| Historical screenshot PNG diffs are included in v1.9 scope | no; they remain explicitly out of scope. |
| QwenPaw is claimed as production orchestration | no; it remains optional, localhost-only, advisory-only evidence. |

### v1.9 Verification Notes

- v1.9 did not modify runtime product code.
- v1.9 did not run the v1.3 live Playwright smoke; the phase reran API tests, web tests, and web build to support the audit pack.
- The next implementation phase should create enforceable CI/repository controls before auth, persistence, deployment, or external integrations are expanded.

## v2.0 CI And Repository Hygiene Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python scripts\repo_hygiene.py --check secrets` | project root | 0 | Secret scanner passed after allowing historical fake-key fixtures while retaining high-confidence token patterns. |
| `python scripts\repo_hygiene.py --check local-paths` | project root | 0 | No local absolute workspace paths found in tracked text files. |
| `python scripts\repo_hygiene.py --check node-modules` | project root | 0 | No tracked `node_modules` paths. |
| `python scripts\repo_hygiene.py --check generated-artifacts --base origin/main` | project root | 0 | No committed generated screenshot artifact changes relative to `origin/main`. |
| `python scripts\repo_hygiene.py --base origin/main` | project root | 0 | All repository hygiene checks passed. |
| `python -m pytest -q` | `apps/api` | 0 | 176 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 28 frontend test files passed; 94 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; Vite still emitted the known large chunk warning for `assets/index-DwOVRZL_.js` at 841.37 kB. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `.github/workflows/ci.yml` | GitHub Actions workflow for API tests, web tests/build, and repository hygiene. |
| `scripts/repo_hygiene.py` | Dependency-free local/CI hygiene scanner. |
| `docs/proposal/v2.0-ci-repo-hygiene-spec.md` | v2.0 scope, required behavior, and acceptance criteria. |
| `docs/proposal/v2.0-ci-repo-hygiene-implementation-plan.md` | v2.0 task plan and verification gates. |
| `docs/research/v2.0-ci-repo-hygiene.md` | Local evidence report and remaining PNG decision boundary. |

### v2.0 Boundary Checks

| Check | Result |
| --- | --- |
| Product runtime behavior changed | no. |
| CI workflow exists locally | pass. |
| Remote GitHub Actions observed green | not yet; requires push. |
| Historical PNG files included in v2.0 scope | no; they remain unstaged. |
| v2.0 makes the app commercial-ready | no; it only adds repository gates needed before security and deployment hardening. |

## v2.1 Auth Security Hardening Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest apps/api/tests/test_v21_security_settings.py apps/api/tests/test_v21_demo_boundary.py apps/api/tests/test_v21_session_cookie_policy.py apps/api/tests/test_v21_csrf_policy.py -q` | project root | 0 | 91 focused v2.1 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test -- tests/v21-csrf-client.test.ts tests/login-page.test.tsx tests/auth-api.test.tsx tests/v12-event-interaction-api.test.ts` | `apps/web` | 0 | 4 focused frontend test files passed, 15 tests passed. |
| `python -m pytest -q` | `apps/api` | 0 | 267 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 29 frontend test files passed, 98 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; Vite emitted the existing large chunk warning for `assets/index-BZnjRTU3.js` at 840.94 kB. |
| `python scripts\repo_hygiene.py --base origin/main` | project root | 0 | Secret, local-path, node-modules, and generated-artifact checks passed. |
| `git diff --check` | project root | 0 | No whitespace errors; Git reported expected Windows line-ending warnings for touched text files. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `apps/api/app/settings.py` | Typed security settings and startup validation for app env, demo mode, session cookies, CSRF mode, TTL, secret material, and allowed origins. |
| `apps/api/app/csrf.py` | Signed double-submit CSRF token issuance and validation. |
| `apps/api/app/auth.py` | Settings-driven session cookie policy and demo-only versus double-submit mutation-origin enforcement. |
| `apps/api/app/main.py` | Validated startup seeding, settings-aligned CORS policy, and `/api/auth/csrf` endpoint. |
| `apps/web/src/api.ts` | Shared frontend mutation helper that uses the demo CSRF header only in demo mode and fetches signed CSRF tokens otherwise. |
| `apps/web/src/auth/authClient.ts` | Login/logout now use the shared mutation helper instead of hard-coded demo CSRF. |
| `apps/web/src/pages/login/LoginPage.tsx` | Demo account shortcut UI is gated by `VITE_DEMO_MODE`. |
| `.env.example` and `README.md` | Local demo defaults and production-like refusal boundaries are documented without secrets. |

### v2.1 Boundary Checks

| Check | Result |
| --- | --- |
| Local demo mode remains usable by default | pass. |
| Demo users are seeded only when demo mode is enabled | pass. |
| Production/staging-like unsafe startup config is rejected | pass. |
| Session cookie attributes resolve from settings | pass. |
| Fixed `X-Zhiyin-CSRF: demo` is demo-only | pass. |
| Non-demo CSRF uses signed double-submit token/cookie matching | pass. |
| Localhost origin regex is demo-only; non-demo modes use explicit allowed origins | pass. |
| Frontend demo quick-fill is hidden when `VITE_DEMO_MODE=false` | pass. |
| v2.1 provides complete production identity | no; it remains a beta auth/session/CSRF baseline without registration, SSO, tenant isolation, password reset, or user administration. |

### v2.1 Verification Notes

- Backend pytest must be run serially against the default SQLite store; parallel backend pytest is still unsafe for this repo's shared test database.
- A sandboxed `python -X utf8 -m pytest ...` attempt failed with `sqlite3.OperationalError: attempt to write a readonly database` because that command prefix did not use the approved non-sandbox execution path. The same focused v2.1 backend tests passed with the approved `python -m pytest ...` prefix.

## v2.2 Persistence And Migrations Verification

### Commands

| Command | Working directory | Exit code | Summary |
| --- | --- | --- | --- |
| `python -m pytest apps/api/tests/test_v22_migrations.py -q` | project root | 0 | 4 initial migration-runner tests passed before quality review hardening. |
| `python -m pytest apps/api/tests/test_v02_seed_store.py apps/api/tests/test_v12_store_models.py apps/api/tests/test_v22_store_migration_integration.py -q` | project root | 0 | 21 store-focused tests passed before `AUTO_MIGRATE=false` hardening. |
| `python apps\api\scripts\migrate_store.py` | project root | 0 | Migration script returned JSON with `current_version=0002_auth_tables` and no pending migrations for the current local store. |
| `python -m pytest apps/api/tests/test_v22_health_schema_status.py -q` | project root | 0 | 3 initial health schema metadata tests passed before staging path-leak hardening. |
| `python -m pytest apps/api/tests/test_v22_demo_reset_boundary.py apps/api/tests/test_v13_demo_reset_script.py -q` | project root | 0 | 7 reset-boundary and existing reset tests passed. |
| `python -m pytest apps/api/tests/test_v22_migrations.py apps/api/tests/test_v22_health_schema_status.py apps/api/tests/test_v22_demo_reset_boundary.py -q` | project root | 0 | 17 focused tests passed after fixing import-time store side effects and staging path omission. |
| `python -m pytest apps/api/tests/test_v22_migrations.py apps/api/tests/test_v22_store_migration_integration.py apps/api/tests/test_v22_health_schema_status.py apps/api/tests/test_v22_demo_reset_boundary.py apps/api/tests/test_v02_seed_store.py apps/api/tests/test_v12_store_models.py apps/api/tests/test_v13_demo_reset_script.py -q` | project root | 0 | 42 v2.2 focused backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest apps/api/tests/test_v22_demo_reset_boundary.py apps/api/tests/test_v04_auth.py -q` | project root | 0 | 16 reset/import-boundary and auth regression tests passed after moving password helpers into `app.security`. |
| `python -m pytest apps/api/tests/test_v22_migrations.py apps/api/tests/test_v22_store_migration_integration.py apps/api/tests/test_v22_health_schema_status.py apps/api/tests/test_v22_demo_reset_boundary.py apps/api/tests/test_v02_seed_store.py apps/api/tests/test_v04_auth.py apps/api/tests/test_v12_store_models.py apps/api/tests/test_v13_demo_reset_script.py -q` | project root | 0 | 53 v2.2 focused backend tests passed after adding the non-mutating path-read regression; 3 existing FastAPI/Starlette warnings. |
| `python -m pytest -q` | `apps/api` | 0 | 292 backend tests passed; 3 existing FastAPI/Starlette warnings. |
| `npm.cmd run test` | `apps/web` | 0 | 29 frontend test files passed, 98 tests passed. |
| `npm.cmd run build` | `apps/web` | 0 | `tsc -b && vite build` passed; Vite emitted the existing large chunk warning for `assets/index-BZnjRTU3.js` at 840.94 kB. |
| `python apps\api\scripts\migrate_store.py` | project root | 0 | Fresh final migration check returned `current_version=0002_auth_tables`, `applied_versions=[]`, and `pending_versions=[]`. |
| `python scripts\repo_hygiene.py --base origin/main` | project root | 0 | Secret, local-path, node-modules, and generated-artifact checks passed. |
| `git diff --check` | project root | 0 | No whitespace errors; Git reported expected Windows line-ending warnings for touched text files. |

### Evidence Artifacts

| Artifact | Summary |
| --- | --- |
| `apps/api/app/migrations/versions.py` | Defines `0001_initial_records` and `0002_auth_tables` with the current records/users/sessions/index schema. |
| `apps/api/app/migrations/runner.py` | Runs idempotent SQLite migrations, reports current and pending versions, uses savepoints for migration atomicity, and keeps read helpers non-mutating. |
| `apps/api/app/store.py` | `MVPStore` initializes through migrations and can refuse pending production/staging migrations when `AUTO_MIGRATE=false`. |
| `apps/api/app/store_paths.py` | Provides database path resolution without importing `app.store` or constructing global `STORE`. |
| `apps/api/app/security.py` | Holds password/session-token helpers without importing `app.store`, so seed/reset imports avoid global `STORE` side effects. |
| `apps/api/scripts/migrate_store.py` | Explicit migration command that avoids import-time `STORE` side effects. |
| `apps/api/scripts/reset_demo_state.py` | Demo reset now checks local/demo and `DEMO_MODE=true` before lazy-loading default `STORE`. |
| `apps/api/app/main.py` | `/api/health` reports store kind, schema version, and pending migrations; database path is only shown in local/demo. |

### v2.2 Boundary Checks

| Check | Result |
| --- | --- |
| Fresh database migrates to latest schema | pass. |
| Repeated migrations are idempotent | pass. |
| Pending migrations are detected | pass. |
| Failed migration rolls back DDL side effects | pass. |
| Migration read helpers do not commit caller-owned transactions | pass. |
| Path-based migration read helpers do not create missing database files or parent directories | pass. |
| Existing `records`, auth, seed, and v1.2 store operations still work | pass. |
| Migration script runs without constructing global `STORE` first | pass. |
| Health metadata omits database path in staging/production | pass. |
| Demo reset refuses outside local/demo or when `DEMO_MODE=false` before default store creation | pass. |
| v2.2 provides production database operations/backups/tenant isolation | no; it remains migration-managed SQLite beta readiness. |
