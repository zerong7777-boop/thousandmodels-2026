# Frontend Template Scout

Date: 2026-06-10
Spec: docs/proposal/v0.3-product-frontend-redesign.md

## Summary

This document evaluates open-source templates and UI kits for the v0.3 multi-end frontend redesign. The goal is not to find a full application to clone. The goal is to choose a credible UI direction that can support separate organizer, merchant, and user/tourist endpoints without repeating the v0.2 generic admin look.

Evidence sources include official project pages, GitHub repositories, npm registry metadata, and public demos checked on 2026-06-10. Screenshot capture was not available in the current environment, so shortlisted candidates include screenshot descriptions in the screenshot field.

## Candidate Matrix

| # | Name | URL | Repo | License | Last meaningful update | Stack | Role fit | Visual score | Implementation score | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| 1 | Ant Design Pro / ProComponents | https://pro.ant.design/ / https://procomponents.ant.design/ | https://github.com/ant-design/ant-design-pro / https://github.com/ant-design/pro-components | MIT, npm/GitHub | @ant-design/pro-components 2.8.10, npm modified 2025-07-17 | React, Ant Design, ProComponents, Umi patterns | organizer | 3 | 4 | reference only |
| 2 | Arco Design Pro / Arco React | https://pro.arco.design/ | https://github.com/arco-design/arco-design-pro / https://github.com/arco-design/arco-design | MIT, npm/GitHub | @arco-design/web-react 2.66.15, npm modified 2026-05-08 | React, Arco Design | organizer | 3 | 3 | reference only |
| 3 | Semi Design | https://semi.design/ | https://github.com/DouyinFE/semi-design | MIT, npm/GitHub | @douyinfe/semi-ui 2.100.0, npm modified 2026-06-09 | React, Semi UI | organizer, merchant | 4 | 3 | reference only |
| 4 | TDesign React | https://tdesign.tencent.com/react/ | https://github.com/Tencent/tdesign-react | MIT, npm/GitHub | tdesign-react 1.17.1, npm modified 2026-06-05 | React, TDesign | organizer | 3 | 3 | reference only |
| 5 | shadcn/ui dashboard blocks | https://ui.shadcn.com/blocks | https://github.com/shadcn-ui/ui | MIT, GitHub/npm package metadata | @shadcn/ui package 0.0.4, package metadata older than active docs | React, Tailwind CSS, Radix primitives, copy-paste components | organizer, merchant, user | 5 | 4 | adopt primary direction |
| 6 | Tremor | https://www.tremor.so/ | https://github.com/tremorlabs/tremor-npm | Apache-2.0, npm | @tremor/react 3.18.7, npm modified 2025-01-13 | React, Tailwind-oriented dashboard components | organizer, review | 4 | 3 | reference only |
| 7 | Mantine | https://mantine.dev/ | https://github.com/mantinedev/mantine | MIT, npm/GitHub | @mantine/core 9.3.1, npm modified 2026-06-08 | React, Mantine components/hooks | organizer, merchant, user | 4 | 3 | backup candidate |
| 8 | MUI Material UI + Toolpad | https://mui.com/material-ui/ / https://mui.com/toolpad/ | https://github.com/mui/material-ui / https://github.com/mui/toolpad | MIT, npm/GitHub | @mui/material 9.1.0, npm modified 2026-06-08; @toolpad/core 0.16.0, npm modified 2025-06-12 | React, Material UI, Toolpad | organizer | 3 | 3 | reject |
| 9 | Refine | https://refine.dev/ | https://github.com/refinedev/refine | MIT, npm/GitHub | @refinedev/core 5.0.12, npm modified 2026-04-02 | React CRUD/meta-framework, adapters | organizer | 2 | 2 | reject |
| 10 | React-admin | https://marmelab.com/react-admin/ | https://github.com/marmelab/react-admin | MIT, npm | react-admin 5.14.7, npm modified 2026-05-18 | React admin framework, data providers | organizer | 2 | 2 | reject |
| 11 | CoreUI React Admin Template | https://coreui.io/react/ | https://github.com/coreui/coreui-react / https://github.com/coreui/coreui-free-react-admin-template | MIT for core package/free template, npm/GitHub | @coreui/react 5.11.0, npm modified 2026-05-17 | React, CoreUI, Bootstrap-style admin | organizer | 2 | 2 | reject |
| 12 | Flowbite React | https://flowbite-react.com/ | https://github.com/themesberg/flowbite-react | MIT, npm/GitHub | flowbite-react 0.12.17, npm modified 2026-02-09 | React, Tailwind CSS | merchant, user | 3 | 3 | reference only |
| 13 | Radix Themes | https://www.radix-ui.com/themes/docs/overview | https://github.com/radix-ui/themes | MIT, npm/GitHub | @radix-ui/themes 3.3.0, npm modified 2026-01-31 | React, Radix Themes | organizer, merchant, user | 4 | 3 | reference only |
| 14 | Creative Tim Material Dashboard React | https://www.creative-tim.com/product/material-dashboard-react | https://github.com/creativetimofficial/material-dashboard-react | MIT for free repository, GitHub | Public GitHub free template, checked 2026-06-10 | React, Material UI | organizer | 2 | 2 | reject |

## Candidate Notes

### 1. Ant Design Pro and ProComponents

- URL: https://pro.ant.design/ and https://procomponents.ant.design/
- Repository: https://github.com/ant-design/ant-design-pro and https://github.com/ant-design/pro-components
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@ant-design/pro-components` 2.8.10, npm modified 2025-07-17.
- Framework and dependencies: React, Ant Design, ProComponents, Umi-oriented application patterns.
- Reusable pages/components: ProTable-like dense tables, ProLayout patterns, forms, descriptions, approval/detail pages.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: polished enterprise dashboard with dense navigation and card/table modules.
- Visual fit score: 3.
- Implementation fit score: 4.
- Role fit: organizer.
- Risks: It reinforces the current "generic management backend" problem if adopted directly. ProLayout/Umi assumptions also do not match the current Vite codebase cleanly.
- Decision: reference only.
- Reason: Keep as a reference for organizer density, table/detail primitives, and approval workflows, but do not use it as the overall visual direction.

### 2. Arco Design Pro and Arco React

- URL: https://pro.arco.design/
- Repository: https://github.com/arco-design/arco-design-pro and https://github.com/arco-design/arco-design
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@arco-design/web-react` 2.66.15, npm modified 2026-05-08.
- Framework and dependencies: React, Arco Design.
- Reusable pages/components: dashboards, tables, form pages, layout shell, enterprise status modules.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: clean enterprise console style with familiar admin structure.
- Visual fit score: 3.
- Implementation fit score: 3.
- Role fit: organizer.
- Risks: Replacing Ant Design with Arco would introduce component migration cost without solving the role/product identity problem by itself.
- Decision: reference only.
- Reason: Useful for layout density and dashboard hierarchy, but not differentiated enough for this project.

### 3. Semi Design

- URL: https://semi.design/
- Repository: https://github.com/DouyinFE/semi-design
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@douyinfe/semi-ui` 2.100.0, npm modified 2026-06-09.
- Framework and dependencies: React, Semi UI.
- Reusable pages/components: navigation, tables, forms, status tags, data display, empty/loading states.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: modern, crisp component language with stronger product polish than default admin kits.
- Visual fit score: 4.
- Implementation fit score: 3.
- Role fit: organizer, merchant.
- Risks: The project already uses Ant Design 6. A full Semi migration would be expensive and would not automatically create a mobile tourist H5.
- Decision: reference only.
- Reason: Good visual benchmark for cleaner component rhythm and status presentation, but not the chosen implementation base.

### 4. TDesign React

- URL: https://tdesign.tencent.com/react/
- Repository: https://github.com/Tencent/tdesign-react
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `tdesign-react` 1.17.1, npm modified 2026-06-05.
- Framework and dependencies: React, TDesign.
- Reusable pages/components: enterprise layout, forms, status components, tables, mobile-adjacent component patterns.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: stable enterprise product style with broad component coverage.
- Visual fit score: 3.
- Implementation fit score: 3.
- Role fit: organizer.
- Risks: Switching the component foundation would be a major migration for modest visual benefit.
- Decision: reference only.
- Reason: Good for enterprise consistency examples, not for the main v0.3 redesign.

### 5. shadcn/ui Dashboard Blocks

- URL: https://ui.shadcn.com/blocks
- Repository: https://github.com/shadcn-ui/ui
- License: MIT, verified through project/repository metadata.
- Last meaningful update: Official docs and blocks checked 2026-06-10; npm package metadata is not the main distribution mechanism because shadcn/ui is primarily copied into the app.
- Framework and dependencies: React, Tailwind CSS, Radix primitives, lucide icons, copy-paste component source.
- Reusable pages/components: dashboard shell, sidebar/topbar patterns, cards, metrics, tables, command-style navigation, mobile-friendly blocks, form controls.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: modern product-grade dashboard blocks with less default admin feel and stronger compositional flexibility.
- Visual fit score: 5.
- Implementation fit score: 4.
- Role fit: organizer, merchant, user.
- Risks: Tailwind/Radix adoption must be deliberate. Copy-paste components can fragment styling if design tokens are not centralized. It may require replacing some Ant Design layout/form usage over time.
- Decision: adopt primary direction.
- Reason: It is the best fit for escaping the default Ant Design admin look while still allowing incremental adoption. Its block model can support a dense organizer product, a lighter merchant workbench, and a mobile-first tourist route surface.

### 6. Tremor

- URL: https://www.tremor.so/
- Repository: https://github.com/tremorlabs/tremor-npm
- License: Apache-2.0, verified through npm metadata.
- Last meaningful update: `@tremor/react` 3.18.7, npm modified 2025-01-13.
- Framework and dependencies: React, Tailwind-oriented dashboard/chart components.
- Reusable pages/components: metric cards, charts, KPI panels, dashboards, review center primitives.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: strong analytical dashboard style with clean metric hierarchy.
- Visual fit score: 4.
- Implementation fit score: 3.
- Role fit: organizer, review.
- Risks: Not a full product shell. It is strongest for analytics/review, not merchant or tourist flows.
- Decision: reference only.
- Reason: Use as a reference for metric-backed review panels, not as the main UI framework.

### 7. Mantine

- URL: https://mantine.dev/
- Repository: https://github.com/mantinedev/mantine
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@mantine/core` 9.3.1, npm modified 2026-06-08.
- Framework and dependencies: React, Mantine components and hooks.
- Reusable pages/components: app shell, cards, forms, notifications, modals, segmented controls, responsive layout primitives.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: modern neutral product UI with good documentation and broad component coverage.
- Visual fit score: 4.
- Implementation fit score: 3.
- Role fit: organizer, merchant, user.
- Risks: Replacing Ant Design with Mantine is a larger library migration than shadcn-style selective adoption. It may still need custom role-specific visual design.
- Decision: backup candidate.
- Reason: Strong all-round React UI kit if the user rejects Tailwind/shadcn. It is less admin-like than Ant Design Pro but comes with higher component replacement cost.

### 8. MUI Material UI and Toolpad

- URL: https://mui.com/material-ui/ and https://mui.com/toolpad/
- Repository: https://github.com/mui/material-ui and https://github.com/mui/toolpad
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@mui/material` 9.1.0, npm modified 2026-06-08; `@toolpad/core` 0.16.0, npm modified 2025-06-12.
- Framework and dependencies: React, Material UI, Toolpad.
- Reusable pages/components: app shell, data tables, forms, dashboards, auth/admin patterns.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: mature Material-style application framework.
- Visual fit score: 3.
- Implementation fit score: 3.
- Role fit: organizer.
- Risks: Material styling is very recognizable and may feel generic. It would require a broad replacement of existing Ant Design components.
- Decision: reject.
- Reason: It does not solve the key aesthetic problem enough to justify migration cost.

### 9. Refine

- URL: https://refine.dev/
- Repository: https://github.com/refinedev/refine
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@refinedev/core` 5.0.12, npm modified 2026-04-02.
- Framework and dependencies: React framework for CRUD/business apps, data providers, optional UI adapters.
- Reusable pages/components: resource routing, CRUD scaffolding, auth/provider architecture.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: powerful admin/business application framework.
- Visual fit score: 2.
- Implementation fit score: 2.
- Role fit: organizer.
- Risks: It shifts the project toward CRUD/admin architecture and would be a major rewrite around providers/resources.
- Decision: reject.
- Reason: The project needs role-specific product surfaces, not an admin framework migration.

### 10. React-admin

- URL: https://marmelab.com/react-admin/
- Repository: https://github.com/marmelab/react-admin
- License: MIT, verified by npm metadata.
- Last meaningful update: `react-admin` 5.14.7, npm modified 2026-05-18.
- Framework and dependencies: React admin framework with data providers.
- Reusable pages/components: CRUD resources, list/edit/show views, auth/provider abstractions.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: mature generic admin interface.
- Visual fit score: 2.
- Implementation fit score: 2.
- Role fit: organizer.
- Risks: Strongly reinforces the "admin backend" look and requires reshaping the app around react-admin concepts.
- Decision: reject.
- Reason: Good product for admin apps, wrong direction for an event collaboration product with tourist and merchant endpoints.

### 11. CoreUI React Admin Template

- URL: https://coreui.io/react/
- Repository: https://github.com/coreui/coreui-react and https://github.com/coreui/coreui-free-react-admin-template
- License: MIT for the core/free open-source packages, verified through npm/GitHub metadata.
- Last meaningful update: `@coreui/react` 5.11.0, npm modified 2026-05-17.
- Framework and dependencies: React, CoreUI, Bootstrap-style admin template.
- Reusable pages/components: admin sidebar, dashboard cards, charts, forms, tables.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: conventional admin dashboard template.
- Visual fit score: 2.
- Implementation fit score: 2.
- Role fit: organizer.
- Risks: Very likely to make the site look like a generic template. Visual identity would be weak.
- Decision: reject.
- Reason: It directly conflicts with the v0.3 requirement to stop looking like a standard admin backend.

### 12. Flowbite React

- URL: https://flowbite-react.com/
- Repository: https://github.com/themesberg/flowbite-react
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `flowbite-react` 0.12.17, npm modified 2026-02-09.
- Framework and dependencies: React, Tailwind CSS.
- Reusable pages/components: cards, navbars, forms, alerts, timeline-like layouts, mobile-friendly UI blocks.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: Tailwind component library with straightforward responsive components.
- Visual fit score: 3.
- Implementation fit score: 3.
- Role fit: merchant, user.
- Risks: Less distinctive than shadcn/ui and can feel like a component catalog unless heavily curated.
- Decision: reference only.
- Reason: Useful for mobile/tablet component patterns, but not the main direction.

### 13. Radix Themes

- URL: https://www.radix-ui.com/themes/docs/overview
- Repository: https://github.com/radix-ui/themes
- License: MIT, verified through npm/GitHub metadata.
- Last meaningful update: `@radix-ui/themes` 3.3.0, npm modified 2026-01-31.
- Framework and dependencies: React, Radix Themes.
- Reusable pages/components: accessible primitives, dialogs, buttons, forms, layout components, theme tokens.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: polished accessible component foundation rather than a full template.
- Visual fit score: 4.
- Implementation fit score: 3.
- Role fit: organizer, merchant, user.
- Risks: It is not a complete app shell or template. More custom layout work would be needed.
- Decision: reference only.
- Reason: Good lower-level component reference, especially because shadcn uses Radix primitives.

### 14. Creative Tim Material Dashboard React

- URL: https://www.creative-tim.com/product/material-dashboard-react
- Repository: https://github.com/creativetimofficial/material-dashboard-react
- License: MIT for the free public repository, checked through GitHub/project metadata.
- Last meaningful update: Public free repository checked 2026-06-10.
- Framework and dependencies: React, Material UI.
- Reusable pages/components: dashboard shell, cards, charts, form pages, table pages.
- Screenshot path: Screenshot unavailable in current environment; visual inspection note: recognizable commercial/free admin dashboard template style.
- Visual fit score: 2.
- Implementation fit score: 2.
- Role fit: organizer.
- Risks: Template look is too obvious and would weaken competition product credibility.
- Decision: reject.
- Reason: It is a polished admin starter, but the project explicitly needs to move away from that category.

## Rejected Candidates

| Name | Rejection Reason |
| --- | --- |
| MUI Material UI + Toolpad | Mature, but the Material/admin look does not solve the v0.2 aesthetic issue and migration cost is high. |
| Refine | Excellent CRUD framework, but it pushes the app toward resource-admin architecture instead of role-specific event collaboration. |
| React-admin | Strong admin framework, wrong product category for organizer/merchant/tourist separation. |
| CoreUI React Admin Template | Too close to a generic admin template, which is the main problem to avoid. |
| Creative Tim Material Dashboard React | Visually polished but obviously template-like and not suited to a distinctive Macau event product. |

## Shortlist

| Rank | Candidate | Use | Reason |
| --- | --- | --- | --- |
| 1 | shadcn/ui dashboard blocks | Primary direction | Best balance of modern product feel, role-shell flexibility, React/Vite compatibility, and incremental adoption. |
| 2 | Mantine | Backup direction | Good full React UI kit if Tailwind/shadcn is rejected, but migration cost is higher. |
| 3 | Ant Design Pro / ProComponents | Reference only | Keep as an organizer-density reference because the project already uses Ant Design, but do not adopt its visual shell. |
| 4 | Tremor | Reference only | Useful for review metrics and operational dashboards, not a full product shell. |
