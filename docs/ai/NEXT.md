# NEXT

## Recommended Next Step

Complete v2.5 full verification, commit the release-gate branch, push it, open a PR, and observe GitHub Actions before merge. After that, the recommended next implementation phase is `v2.6-browser-release-evidence-gate`.

v2.5 adds a deterministic live API release gate. The next gap is browser-level release evidence: a controlled Playwright run against a real local API and Vite app that records a small, intentional evidence set without reintroducing broad screenshot churn.

For v2.5 closeout:

1. Run the focused release-gate tests.
2. Run full backend pytest serially.
3. Run full frontend Vitest and production build.
4. Run the live API release gate against an isolated local SQLite database.
5. Run repository hygiene and whitespace checks.
6. Commit and push the v2.5 branch.
7. Merge only after remote CI is green.

The 14 historical screenshot PNG diffs still need a separate explicit decision: restore them, commit them as a named evidence refresh, or regenerate them through a dedicated visual evidence task.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
- Do not stage the historical screenshot PNG diffs unless a separate evidence-refresh task explicitly owns them.
- Do not treat v2.1 as complete production identity; it is a beta auth/session/CSRF baseline.
- Do not treat v2.2 as production database operations; it is schema ownership and migration discipline for the current SQLite store.
- Do not treat v2.3 as a real cloud launch; it is an environment/readiness operations baseline without hosting, TLS, managed secrets, backups, or monitoring.
- Do not treat v2.4 as full observability maturity; it is a beta operations baseline without vendor monitoring, alert routing, SLOs, or customer incident operations.
- Do not treat v2.5 as browser or cloud release proof; it is a live API release gate for local/demo beta readiness.
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
