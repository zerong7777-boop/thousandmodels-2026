# NEXT

## Recommended Next Step

Push the v2.0 CI/repo-hygiene commit and observe GitHub Actions.

v2.0 has added local CI and repository hygiene gates. The next decision is whether to push the branch so GitHub can execute the new workflow:

1. Push `v1-qwen-controlled-draft`.
2. Check the new `CI` workflow on GitHub.
3. If GitHub Actions is green, start `v2.1-auth-security-hardening`.
4. If GitHub Actions fails, fix CI before product hardening.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
