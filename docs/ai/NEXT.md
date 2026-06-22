# NEXT

## Recommended Next Step

Turn the manual real-QwenPaw smoke into a stricter guarded adapter checkpoint before wiring it into product flow.

The local QwenPaw service is reachable, the active LLM is configured as `opencode/deepseek-v4-flash-free`, and the guarded smoke now records `live_success` through optional `QWENPAW_AGENT_ID=QwenPaw_QA_Agent_0.2`. The next meaningful checkpoint is to make success criteria stricter: require advisory fields, normalize/suppress bootstrap or preamble noise from evidence, and keep real QwenPaw output behind the existing advisory-only safety boundary.

## Do Not Do Yet

- Do not treat QwenPaw `live_success` as production orchestration.
- Do not treat a reachable QwenPaw port alone as model success; require the guarded smoke evidence.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
