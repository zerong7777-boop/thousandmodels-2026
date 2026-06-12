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
