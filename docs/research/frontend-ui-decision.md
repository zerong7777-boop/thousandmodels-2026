# Frontend UI Decision

Date: 2026-06-10

Inputs:

- docs/research/frontend-research-criteria.md
- docs/research/frontend-template-scout.md
- docs/research/frontend-visual-reference-matrix.md
- docs/research/role-ia-matrix.md

Approval status:

- User approved the primary direction, option A, on 2026-06-10.
- The next implementation phase may proceed with Task 6-9 from `docs/proposal/v0.3-implementation-plan.md`.
- Mantine remains a backup reference only.

## Recommendation

Primary direction: adopt a shadcn/ui-inspired product interface direction using Tailwind/Radix-style layout patterns, copied/owned components, and role-specific shells. Use it as the visual and structural direction for v0.3 after user approval.

Backup direction: Mantine as the only backup direction if the user rejects Tailwind/shadcn-style adoption. Mantine provides a cohesive React UI kit with lower admin-template smell than Ant Design Pro, but migration cost is higher.

This recommendation does not require implementing shadcn/ui or Mantine during Phase 0. It only selects the direction for the next implementation phase.

## Why

The current product problem is not only component quality. It is product identity. The v0.2 frontend already has routes, but it still reads like one shared admin shell. shadcn/ui-style blocks are better suited to composing different role surfaces without inheriting a heavy admin framework:

- Organizer can become a dense but polished operations workspace with queues, version diff, incident cards, trace timeline, and metrics.
- Merchant can become a light task/status workbench with large touch-friendly controls.
- User/tourist can become a mobile route/event H5 with route point stories, notices, and tasks.

Ant Design Pro, Refine, React-admin, CoreUI, and similar admin frameworks are credible engineering tools but repeat the exact maturity problem the user identified: the app feels like a backend dashboard rather than a product.

## What To Reuse

| Source | Reuse | Role | Notes |
| --- | --- | --- | --- |
| shadcn/ui dashboard blocks | Shell composition, cards, status strips, tables, responsive dashboard patterns | organizer, merchant, user | Primary visual direction; copy/adapt patterns rather than importing a full admin app. |
| Radix primitives | Accessible dialog/menu/form behavior | organizer, merchant, user | Already aligned with shadcn ecosystem. Use only if the next phase approves dependencies. |
| lucide icons | Product actions and navigation icons | organizer, merchant, user | Existing frontend already uses lucide-react. |
| Ant Design existing components | Keep where already stable for forms, tables, messages, and compatibility during migration | organizer | Do not use Ant Design Pro layout as the main visual shell. |
| Tremor | Metric hierarchy and review dashboard inspiration | organizer review | Reference only; no dependency required yet. |
| Luma | Clean mobile event page hierarchy | user/tourist | Pattern reference for public route H5. |
| Wanderlog / Roadtrippers | Route stop sequence and journey mental model | user/tourist | Pattern reference; no real map API in v0.3. |
| Shopify POS / Square POS | Direct task/status controls | merchant | Pattern reference for mobile/tablet merchant actions. |
| PagerDuty / Datadog | Incident queue, severity, timeline, and review metrics | organizer | Pattern reference for exception center and review. |

## What To Avoid

| Avoid | Reason |
| --- | --- |
| Generic admin dashboard look | It repeats the v0.2 maturity problem. |
| Marketing landing hero | The product starts from work and route execution, not promotion. |
| Full admin frameworks such as Refine or React-admin | They optimize CRUD/admin apps, not role-specific event collaboration. |
| Direct Ant Design Pro shell adoption | It would make the project look like another enterprise backend. |
| Proprietary product visual copying | Product references are for interaction patterns only. |
| New UI dependency before user approval | Phase 0 is a decision gate, not implementation. |

## Component Strategy

Recommended strategy for the next phase:

1. Keep the current React/Vite app and preserve existing API contracts.
2. Keep Ant Design initially for existing stable forms, messages, tables, and tests.
3. Introduce a small owned design layer: tokens, status colors, role layout primitives, and shared typography/spacing rules.
4. After user approval, evaluate adding Tailwind and shadcn/Radix-style components incrementally, starting with shells and high-impact role components.
5. Do not import a full admin template. Build role-specific shells and components inside the project.

This is a hybrid direction: shadcn/ui-inspired visual/product architecture, Ant Design retained only where it reduces migration risk.

## Migration Impact

| Area | Impact | Mitigation |
| --- | --- | --- |
| Existing tests | Route and flow tests should stay conceptually stable, but selectors may change once pages are rebuilt. | Keep assertions around role separation, flow state, and visible business outcomes rather than Ant Design-specific DOM. |
| Existing v0.2 routes | Compatibility aliases must remain. | Keep `/organizer`, `/merchant/m001`, `/review/demo-night-tour`, and `/public/events/demo-night-tour`. |
| Bundle size | Tailwind/Radix/shadcn-style adoption may add tooling and components; Mantine would add a larger component package. | Re-check after build in the implementation phase. Add dependencies only after approval. |
| Visual consistency | Hybrid AntD + shadcn can look inconsistent if tokens are not controlled. | Establish tokens and role shells before replacing individual components. |
| Implementation complexity | New role shells plus login/session require test coverage. | Implement Task 6 onward with tests first, as planned. |

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Hybrid UI becomes inconsistent | High | Define tokens and shell-level layout rules before page work. |
| Tailwind setup takes time | Medium | Keep Ant Design for existing complex controls during first pass. |
| shadcn blocks are copied without product adaptation | High | Map every component to role IA before using it. |
| User H5 still looks like a backend preview | High | Build user shell separately and ban backend terms in user views. |
| Organizer dashboard becomes too decorative | Medium | Keep density and workflow-first layout; no marketing hero. |

## Acceptance Criteria For User Approval

The next implementation phase can start only if the user accepts this direction:

- Primary direction: shadcn/ui-inspired role-specific product UI.
- Backup: Mantine only if Tailwind/shadcn direction is rejected.
- Ant Design remains allowed as a migration bridge, not as the main visual identity.
- No full admin framework adoption.
- No source changes have been made in Phase 0.

## Stop Gate

Status: resolved. The user confirmed option A.

Proceed to the next checkpoint:

```text
Task 6-9: demo login/session, route guards, and separate Organizer/Merchant/User shells.
```
