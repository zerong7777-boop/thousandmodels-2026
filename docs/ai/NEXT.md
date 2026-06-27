# NEXT

## Recommended Next Step

Complete v2.1 full verification and commit the auth/security hardening branch. After that, the recommended next implementation phase is `v2.2-persistence-migration-hardening`.

v2.1 now adds a beta auth/session/CSRF boundary between local demo behavior and production-like behavior. Before moving on, keep the release discipline:

1. Run full backend pytest serially.
2. Run full frontend Vitest and production build.
3. Run repository hygiene and whitespace checks.
4. Commit the v2.1 branch.
5. Push the branch and observe GitHub Actions before merging.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
