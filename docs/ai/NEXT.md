# NEXT

## Recommended Next Step

Review `docs/proposal/v0.8-agent-capability-spec.md`, then write the backend-first implementation plan:

```text
docs/proposal/v0.8-agent-capability-implementation-plan.md
```

Recommended order:

```text
review v0.8 agent capability spec
-> write v0.8 backend-first implementation plan
-> implement deterministic Agent runtime and tool-call evidence
-> add optional Qwen draft path only after deterministic Agent tests pass
```

The next implementation phase should focus on real Agent capability rather than additional UI polish:

1. make `AgentRun`, richer `AgentStep`, `AgentToolCall`, and `AgentDraft` contracts concrete
2. build deterministic specialist agents around planning, incident recovery, public notices, and review
3. prove sold-out incident recovery creates auditable Agent evidence before organizer approval
4. keep Qwen/QwenPaw optional and non-blocking

## Do Not Do Yet

- Do not make model APIs required for the demo.
- Do not let model output mutate approval, inventory, route publication, or plan persistence directly.
- Do not add real merchants, hardware, POS, payment, map API, or real traffic prediction.
- Do not claim full QwenPaw orchestration until it is actually implemented and verified.
- Do not start a broad frontend redesign before the Agent runtime exists.
