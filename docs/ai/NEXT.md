# NEXT

## Recommended Next Step

Improve prompt and agent selection until the guarded real-QwenPaw smoke returns `advisory_qualified`, while keeping the v1.4 fake adapter as the accepted product path.

The current v1.7 smoke proves that the local QwenPaw provider is reachable and that the guarded adapter no longer accepts a non-empty response as success. The latest recorded outcome is `advisory_unqualified` because the response stayed in preamble/tool-introspection text and did not provide `recovery_rationale`, `visitor_safe_notice_draft`, or `safety_notes`.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
