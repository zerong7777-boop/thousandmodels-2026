# NEXT

## Recommended Next Step

Review `docs/proposal/v0.6-i18n-spec.md` and decide whether to proceed with a v0.6 implementation plan.

Recommended v0.6 direction:

```text
Default locale: zh-Hans
Optional locale: zh-Hant
Fallback locale: en
Implementation: lightweight owned frontend i18n layer
Scope: translate active v0.5 product surfaces without UI redesign or backend workflow changes
```

## Next Candidate Work

- Write `docs/proposal/v0.6-implementation-plan.md` after the spec is approved.
- Implement a local `I18nProvider`, locale dictionaries, and language switcher.
- Translate login, shells, organizer, merchant, tourist, and public H5 surfaces.
- Add v0.6 screenshot evidence for Simplified Chinese, Traditional Chinese, and English fallback.
- Keep deterministic rules as the required local demo path.

## Do Not Do Yet

- Do not start v0.6 source implementation before the implementation plan exists.
- Do not make model APIs required for translation.
- Do not let model output mutate approvals, inventory, publication state, or plan persistence.
- Do not add real merchants, hardware, payment, POS, map, or traffic prediction integrations.
- Do not do another broad visual redesign as part of v0.6.
