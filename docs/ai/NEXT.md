# NEXT

## Recommended Next Step

Complete v2.3 full verification, commit the deployment environment operations branch, then push it and observe GitHub Actions before merge. After that, the recommended next implementation phase is `v2.4-observability-release-runbook`.

v2.3 adds an explicit environment contract, `/api/ready`, deployment smoke checks, and restricted-environment startup guards. Before moving on, keep the release discipline:

1. Run full backend pytest serially.
2. Run full frontend Vitest and production build.
3. Run repository hygiene and whitespace checks.
4. Run the deployment smoke against a local API when a server is running.
5. Commit and push the v2.3 branch.
6. Merge only after remote CI is green.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
