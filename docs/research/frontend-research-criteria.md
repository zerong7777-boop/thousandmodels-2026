# Frontend Research Criteria

Date: 2026-06-10
Project: Zhiyin Haojiang v0.3 frontend redesign

## Purpose

This research checkpoint selects the visual and UI implementation direction before any v0.3 frontend redesign starts. The project must stop looking like a generic admin dashboard while keeping the existing FastAPI + React/Vite deterministic demo path stable.

## Scope

This phase is research only.

- No source code changes.
- No login implementation.
- No page redesign.
- No new UI dependencies.
- No Qwen/QwenPaw integration.
- No backend core-loop changes.

## Evaluation Dimensions

| Dimension | Score 1 | Score 3 | Score 5 |
| --- | --- | --- | --- |
| Visual maturity | Generic demo or default admin | Polished but common | Distinctive, credible, product-grade |
| Non-admin feel | Looks like CRUD backend | Some custom product framing | Clearly not a generic admin template |
| Macau old-district fit | No sense of place or cultural route | Can be adapted with content | Naturally supports cultural route and local event storytelling |
| Organizer fit | Poor dashboard/workflow support | Usable dashboard primitives | Strong operations, approval, exception, timeline patterns |
| Merchant fit | Desktop-only or too complex | Can be simplified | Lightweight task/status workflow works well on mobile/tablet |
| User H5 fit | Not mobile-first | Mobile responsive but generic | Mobile-first event/route experience feels natural |
| React/Vite fit | Hard to integrate | Integrates with moderate effort | Directly usable in current React/Vite stack |
| License risk | Unclear or restrictive | Permissive but needs verification | Clear MIT/Apache/BSD or compatible license |
| Maintenance health | Stale or abandoned | Occasional updates | Active repo or stable mature package |
| Migration cost | Requires rewrite | Requires component adaptation | Can be adopted incrementally |

## Candidate Record Template

| Field | Required Content |
| --- | --- |
| Name | Project/template/product name |
| URL | Official or demo URL |
| Repository URL | GitHub/GitLab/source URL |
| License | License name and source |
| Last meaningful update | Date or release evidence |
| Framework and dependencies | React/Vite/Next/Tailwind/AntD/etc. |
| Reusable pages/components | Concrete pages or components |
| Visual fit score | 1-5 |
| Implementation fit score | 1-5 |
| Role fit | organizer / merchant / user |
| Screenshot path | Local path under docs/research/assets, or a screenshot note if capture is unavailable |
| Risks | Concrete risks |
| Decision | adopt / reference only / reject |
| Reason | One short paragraph |

## Research Evidence Rules

- Prefer official docs, demo pages, GitHub repositories, license files, and npm registry metadata.
- Record exact URLs so the next implementer can re-check facts.
- Do not treat a template as reusable only because it is visually attractive.
- Do not recommend any candidate with unclear license terms.
- Do not copy proprietary product layouts, screenshots, brand assets, or commercial visual systems.
- Screenshot capture is optional in this environment; a screenshot description is acceptable when capture tooling is unavailable.

## Decision Rule

The final recommendation must choose one primary direction and at most one backup direction. A candidate cannot be recommended if its license is unclear. The selected direction must support all three role surfaces:

- Organizer: operations workspace, approval queue, exception center, review metrics.
- Merchant: lightweight task/status workflow for mobile or tablet.
- User/tourist: mobile-first route, story, task, and notice experience.

The primary direction must also preserve compatibility with the current React/Vite codebase and avoid turning the project into a generic SaaS/admin template.
