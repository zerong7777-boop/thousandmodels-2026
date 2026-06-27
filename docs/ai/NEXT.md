# NEXT

## Recommended Next Step

Start `v2.0-ci-repo-hygiene`.

v1.9 completed the commercial-readiness audit pack and classified the project as a CR0 demo-grade MVP with CR1 audit evidence. The next phase should turn the two repository-level P0 findings into enforceable controls:

1. Add GitHub Actions for API pytest, web Vitest, and web production build.
2. Add hygiene scans for secrets, local absolute paths, and accidental generated PNG scope.
3. Document release gates and local reproduction commands.
4. Resolve or quarantine the 14 historical screenshot PNG diffs so future commits stay reviewable.

Do this before production auth/session hardening, migration-backed persistence, deployment configuration, observability, or any new external integration work.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
- Do not stage the historical screenshot PNG diffs unless a separate evidence-refresh task explicitly owns them.
