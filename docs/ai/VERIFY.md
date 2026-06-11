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
