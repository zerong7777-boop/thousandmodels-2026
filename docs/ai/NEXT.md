# NEXT

## Recommended Next Step

Review `docs/proposal/v0.8-agent-capability-implementation-plan.md`, then execute v0.8 P0 backend Agent capability tasks:

```text
Tasks 1-7 + Task 9
```

Recommended order:

```text
review v0.8 implementation plan
-> implement Agent contracts and store persistence
-> implement deterministic Agent runtime and tool-call evidence
-> connect planning, incident recovery, and review Agent flows
-> verify backend pytest and update handoff docs
```

The next implementation phase should focus on real Agent capability rather than additional UI polish:

1. make `AgentRun`, richer `AgentStep`, `AgentToolCall`, and `AgentDraft` contracts concrete
2. build deterministic specialist agents around planning, incident recovery, public notices, and review
3. prove sold-out incident recovery creates auditable Agent evidence before organizer approval
4. keep Qwen/QwenPaw optional and non-blocking
5. do not execute the optional Qwen draft backend task until P0 passes and the user explicitly approves it

## Do Not Do Yet

- Do not make model APIs required for the demo.
- Do not let model output mutate approval, inventory, route publication, or plan persistence directly.
- Do not add real merchants, hardware, POS, payment, map API, or real traffic prediction.
- Do not claim full QwenPaw orchestration until it is actually implemented and verified.
- Do not start a broad frontend redesign before the Agent runtime exists.
