# NEXT

## Recommended Next Step

Configure an active QwenPaw LLM model and rerun the guarded live smoke.

The local QwenPaw service can now be reached on localhost, but it currently returns `No active model configured.` The next meaningful checkpoint is a non-empty advisory response through `apps/api/scripts/live_qwenpaw_smoke.py`; until then the evidence must remain `blocked/provider_error`.

## Do Not Do Yet

- Do not claim QwenPaw `live_success` until a local QwenPaw service returns a non-empty sanitized response through `apps/api/scripts/live_qwenpaw_smoke.py`.
- Do not treat a reachable QwenPaw port as model success; the current blocker is active model configuration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a success claim while the current outcome remains `blocked`.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
