# NEXT

## Recommended Next Step

Commit the verified v2.2 persistence migrations branch, then push it and observe GitHub Actions before merge. After that, the recommended next implementation phase is `v2.3-deployment-environment-policy`.

v2.2 now adds migration-managed SQLite persistence and explicit demo reset boundaries. The local verification gate has passed; before moving on, keep the release discipline:

1. Commit the v2.2 branch.
2. Push the branch.
3. Observe GitHub Actions before merging.
4. Merge only after remote CI is green.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
