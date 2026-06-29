# NEXT

## Recommended Next Step

v3.2 is implemented and locally verified. The immediate closeout step is to commit, push, and open a PR for `feat/v32-route-assembly-quality-pack`.

After v3.2 is merged, the recommended next implementation phase is `v3.3-merchant-portal-setup-pack`.

v3.2 makes merchant-linked route assembly scored and explainable, but the merchant side is still mostly a demo workbench. The next useful product package is to make merchant participation setup more product-real:

1. Let merchants complete required setup fields for a selected event instead of relying only on organizer-side mark-ready.
2. Add merchant-facing event participation context: assigned event, requested role, readiness checklist, capacity notes, and constraints.
3. Keep organizer roster authority intact while allowing merchant setup evidence to inform readiness.
4. Surface setup gaps and merchant-submitted notes back in organizer workspace before planning.
5. Preserve v2.9 roster gates, v3.0 eligibility checks, v3.1 merchant-fit evidence, and v3.2 route-fit evidence.
6. Avoid real merchant onboarding, identity administration, POS/payment, hardware, or production integrations until a separate plan exists.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
- Do not stage the historical screenshot PNG diffs unless a separate evidence-refresh task explicitly owns them.
- Do not treat v2.1 as complete production identity; it is a beta auth/session/CSRF baseline.
- Do not treat v2.2 as production database operations; it is schema ownership and migration discipline for the current SQLite store.
- Do not treat v2.3 as a real cloud launch; it is an environment/readiness operations baseline without hosting, TLS, managed secrets, backups, or monitoring.
- Do not treat v2.4 as full observability maturity; it is a beta operations baseline without vendor monitoring, alert routing, SLOs, or customer incident operations.
- Do not treat v2.5 as browser or cloud release proof; it is a live API release gate for local/demo beta readiness.
- Do not treat v2.6 as cloud release proof; it is a live browser release gate for local/demo beta readiness.
- Do not treat v2.7 as production readiness; it is a beta product-logic foundation without real external integrations or a full organizer creation UI.
- Do not treat v2.8 as production readiness; it is a frontend organizer workflow layer without merchant assignment setup or external integrations.
- Do not treat v2.9 as real merchant onboarding or external merchant integration; it scopes planning to an event roster backed by the local catalog.
- Do not treat v3.0 as real merchant onboarding or external merchant integration; it is an organizer-managed local merchant network baseline.
- Do not treat v3.1 as route optimization or real external planning intelligence; it is deterministic local merchant-fit ranking and evidence.
- Do not treat v3.2 as route optimization or real map/weather/traffic intelligence; it is deterministic local route assembly and evidence.
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
