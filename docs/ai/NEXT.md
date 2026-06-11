# NEXT

## Recommended Next Step

Review the v0.8 backend Agent evidence, then choose one next track:

1. Build a focused organizer Agent evidence panel that reads the new `AgentRun`, `AgentToolCall`, and `AgentDraft` endpoints.
2. Execute the optional Qwen draft backend task if model-assisted draft generation is now desired.
3. Convert v0.7/v0.8 evidence into final competition slides.

Recommended order:

```text
verify v0.8 backend Agent evidence
-> decide whether organizer UI should expose Agent runs/drafts
-> only then run optional Qwen draft enrichment or final deck work
```

## Do Not Do Yet

- Do not make model APIs required for the demo.
- Do not let model output mutate approval, inventory, route publication, or plan persistence directly.
- Do not claim full QwenPaw orchestration until it is actually implemented and verified.
- Do not expose raw Agent internals on merchant, tourist, or public H5 pages.
- Do not start real merchant, hardware, POS, payment, real map, or real traffic integrations.
