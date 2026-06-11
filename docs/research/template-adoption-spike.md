# v0.4 Template Adoption Spike

Date: 2026-06-10
Project: Zhiyin Haojiang
Plan: `docs/proposal/v0.4-implementation-plan.md`

## Decision

Primary: `satnaing/shadcn-admin` plus official `shadcn/ui` blocks and owned local primitives.

Backup: `TailAdmin React`, reference only.

Adoption mode: copy and adapt selected shell, sidebar, login, card, badge, and command/menu patterns into this project. Do not import either template as a whole app. Do not copy routing, Clerk auth, TanStack Router setup, charts, map widgets, or sample admin pages.

## Candidate Evidence

| Candidate | Repo | Commit Or Version | License File | Build Command | Build Result | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| satnaing/shadcn-admin | https://github.com/satnaing/shadcn-admin | `a6352e7df0de652e4349f6bf53ca246de6ff013f` | `LICENSE`, MIT, copyright Sat Naing 2024 | `corepack pnpm install --frozen-lockfile`, `corepack pnpm approve-builds --all`, `corepack pnpm run build` | Passed. Vite 8.0.8 transformed 3973 modules and reported `built in 1.14s`. Install required pnpm build-script approval for `esbuild` and `@clerk/shared`. | Adopt as primary structure reference and code pattern source. |
| official shadcn/ui blocks | https://ui.shadcn.com/blocks and https://github.com/shadcn-ui/ui | GitHub page checked 2026-06-10; repo page reported latest release `shadcn@4.11.0` on 2026-06-08 | GitHub repository reports MIT license | Web documentation verification only; blocks are copied by command or source pattern, not built as a standalone app | Blocks page exposes dashboard, sidebar, login, and signup building blocks with copy/add commands such as `npx shadcn add dashboard-01` and `npx shadcn add sidebar-07`. | Adopt selected primitive and block patterns into local owned files. |
| TailAdmin React | https://github.com/TailAdmin/free-react-tailwind-admin-dashboard | `21dc917cb6cb22b5f1d12e5af57359a849d19aa8` | `LICENSE.md`, MIT, copyright TailAdmin 2023 | `npm.cmd install`, `npm.cmd run build` | Passed. Vite 6.1.0 transformed 242 modules and reported `built in 6.53s`. Install reported 18 vulnerabilities; build warned about `eval` in `@react-jvectormap/core` and a 1.94 MB JS chunk. | Keep as backup visual reference only. |

## Dependency Delta

| Package | Type | Reason |
| --- | --- | --- |
| tailwindcss | dev | local utility styling and shadcn-style primitives |
| postcss | dev | Tailwind build pipeline |
| autoprefixer | dev | CSS browser compatibility |
| class-variance-authority | prod | button and badge variants |
| clsx | prod | conditional class names |
| tailwind-merge | prod | class conflict merge |
| @radix-ui/react-slot | prod | composable primitive slots |
| @playwright/test | dev | screenshot and browser smoke evidence |

Do not add `@clerk/react`, TanStack Router, TanStack Query, Recharts, ApexCharts, FullCalendar, jvectormap, or template auth dependencies in v0.4. They are template implementation details, not required for this product foundation.

## Source To Project Mapping

| Source candidate area | Project target | Use | Copy Level |
| --- | --- | --- | --- |
| satnaing/shadcn-admin authenticated layout and sidebar pattern | `apps/web/src/layout/OrganizerProductShell.tsx` | organizer operations navigation, header, account area, and content frame | adapt structure and spacing only |
| satnaing/shadcn-admin responsive navigation density | `apps/web/src/layout/MerchantProductShell.tsx` | compact merchant task/status/notice workbench shell | adapt pattern, not route config |
| official shadcn/ui login block pattern | `apps/web/src/pages/login/LoginPage.tsx` | API-backed login form with demo quick-fill controls | adapt structure and local primitives |
| official shadcn/ui sidebar block pattern | `apps/web/src/ui/sidebar.tsx` and `apps/web/src/layout/ProductShell.tsx` | role-aware navigation primitive | copy small primitive pattern into owned implementation |
| shadcn/admin card, badge, and command/menu visual grammar | `apps/web/src/ui/card.tsx`, `apps/web/src/ui/badge.tsx`, organizer dashboard components | consistent dashboard panels and workload summaries | adapt visual grammar |
| TailAdmin dashboard cards | no direct source copy in primary path | backup visual density reference if primary path fails later | reference only |

## Screenshot Evidence

The local Vite builds passed for both candidates. Browser route screenshot capture for the temporary template dev servers was not stable in the current Windows shell environment because hidden background server startup did not bind to the expected port. To keep Task 1 moving without faking browser evidence, the image files below are copied from each candidate repository's own preview assets. Task 11 still requires Playwright screenshots of this project's actual product routes.

| Screenshot | Path | Viewport Label | Source | Observation |
| --- | --- | --- | --- | --- |
| satnaing dashboard preview | `docs/research/assets/v0.4-template-spike/satnaing-shadcn-admin-dashboard-1440x900.png` | 1440x900 | `public/images/shadcn-admin.png` | Shows the overall app shell, sidebar, command/search density, and dashboard frame. |
| satnaing login/dashboard light preview | `docs/research/assets/v0.4-template-spike/satnaing-shadcn-admin-login-1440x900.png` | 1440x900 | `src/features/auth/sign-in/assets/dashboard-light.png` | Useful for login-page background/product preview treatment, but Clerk auth must not be copied. |
| satnaing dark preview | `docs/research/assets/v0.4-template-spike/satnaing-shadcn-admin-mobile-390x844.png` | 390x844 | `src/features/auth/sign-in/assets/dashboard-dark.png` | Visual reference only; not a verified mobile route screenshot. |
| TailAdmin dashboard preview | `docs/research/assets/v0.4-template-spike/tailadmin-dashboard-1440x900.png` | 1440x900 | `banner.png` | Polished dashboard density but reads more like a generic admin. |
| TailAdmin image-grid preview | `docs/research/assets/v0.4-template-spike/tailadmin-mobile-390x844.png` | 390x844 | `public/images/grid-image/image-01.png` | Asset evidence only; not a route screenshot. |

## Rejected Candidates

| Candidate | Reason |
| --- | --- |
| Ant Design Pro / ProComponents app shell | Reject for v0.4 accepted surfaces because the current product already looks too much like a generic Ant Design management backend. Ant Design can remain only as a migration bridge for complex tables and legacy widgets. |
| Arco Design Pro dashboard | Reject because it would repeat the generic admin-shell problem and add another complete design system without solving backend auth, merchant tablet flow, or tourist mobile route needs. |
| Tremor dashboard components | Reject as primary template because it is metric/dashboard focused and does not provide login, role shell, merchant workbench, or tourist mobile route patterns. It remains a reference for review metrics only. |
| TailAdmin React as primary | Reject as primary despite passing build because install reports 18 vulnerabilities, the build includes `eval` warnings from jvectormap, and the default visual language is broad admin/dashboard rather than role-specific product. |

## License Notes

`satnaing/shadcn-admin` is MIT licensed in the repository `LICENSE` file. If code is copied, preserve the MIT copyright notice where required.

`TailAdmin React` is MIT licensed in `LICENSE.md`. The project should not copy TailAdmin source in the primary path.

`shadcn/ui` repository and documentation identify the project as MIT licensed and describe blocks as open-source building blocks that can be copied into apps. Any copied block code must become owned local code under `apps/web/src/ui` or `apps/web/src/layout`, with project-specific role language and no upstream app routing/auth assumptions.

## Risks

| Risk | Evidence | Mitigation |
| --- | --- | --- |
| Template auth leakage | satnaing includes `@clerk/react` and Clerk examples | Do not install or copy Clerk; v0.4 uses FastAPI cookie sessions only. |
| Router mismatch | satnaing uses TanStack Router; current app uses a simple Vite route resolver | Copy layout and primitives only; keep local routing. |
| Tailwind version mismatch | satnaing and TailAdmin both use Tailwind 4 while the plan currently lists PostCSS/Tailwind setup generically | During Task 8, choose a minimal Tailwind setup compatible with the current Vite app and lock it in package.json. |
| Generic admin feel | both candidates are admin/dashboard templates | Map every copied pattern to organizer, merchant, tourist, or public role contracts. |
| Backup security risk | TailAdmin install reported 18 vulnerabilities and jvectormap `eval` warnings | Keep TailAdmin as reference only; do not copy jvectormap, chart stack, or calendar stack. |
| Screenshot limitation | temporary dev server launch was unstable in this shell | Use repository preview assets for Task 1 only; Task 11 must produce real Playwright screenshots of this product. |

## Adoption Summary

Proceed with `satnaing/shadcn-admin + official shadcn/ui blocks` as the primary direction. Use the source mapping above to build local primitives and role-specific product shells. Keep TailAdmin only as a backup visual reference. The next implementation task should start backend auth red tests before frontend product shell code changes.
