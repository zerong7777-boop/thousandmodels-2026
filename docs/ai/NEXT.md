# NEXT

## Recommended Next Step

Finish publishing the v1.8.1 QwenPaw SSE parser fix and live matrix evidence.

The optional local live QwenPaw v1.8 matrix has now been run after the parser fix. All three cells returned `advisory_qualified` with `json_no_preamble_pass=true` and zero repair attempts:

1. QA agent + JSON-only prompt.
2. QA agent + few-shot JSON prompt with bounded repair enabled.
3. Default agent + JSON-only prompt.

After this commit is pushed, the recommended next spike is v1.9 Direct Structured Output Baseline: a clean provider-level JSON-schema baseline that does not go through QwenPaw agent SSE. That baseline should be treated as an ablation, not a product requirement.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
