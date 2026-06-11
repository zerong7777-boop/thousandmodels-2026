# NEXT

## Recommended Next Step

Review `docs/proposal/v0.6-implementation-plan.md` and decide whether to execute v0.6 i18n.

Recommended execution target:

```text
Build a lightweight owned frontend i18n layer.
Default locale: zh-Hans.
Additional locale: zh-Hant.
Fallback locale: en.
Translate active v0.5 product surfaces.
Keep backend deterministic workflow unchanged.
```

## Next Candidate Work

- Execute `docs/proposal/v0.6-implementation-plan.md` Task 1-11.
- Start with i18n red tests before source implementation.
- Translate login and shells before page-by-page translation.
- Generate v0.6 screenshot evidence after translations are complete.
- Update docs/ai and commit the verified v0.6 result.

## Do Not Do Yet

- Do not start Qwen/QwenPaw integration.
- Do not make model APIs required for translation.
- Do not change backend core workflow, approval state, inventory state, publication state, or plan persistence.
- Do not add real merchants, hardware, payment, POS, map, or traffic prediction integrations.
- Do not do another broad UI redesign as part of v0.6.
