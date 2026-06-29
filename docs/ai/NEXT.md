# NEXT

## Recommended Next Step

v3.1 is implemented and locally verified. The immediate closeout step is to commit, push, and open a PR for `feat/v31-event-planning-eligibility-pack`.

After v3.1 is merged, the recommended next implementation phase is `v3.2-route-assembly-quality-pack`.

v3.1 makes selected merchants fit-ranked and explainable, but route generation is still a simple first-six route-point assembly. The next useful product package is to make route assembly itself more product-real:

1. Score route points against the selected event brief, time window, indoor/outdoor constraints, rainy-day needs, and linked selected merchants.
2. Build a deterministic route sequence with explainable stop roles instead of slicing the first six route points.
3. Warn organizers when selected merchants have no suitable route point linkage or when route coverage is thin.
4. Keep route-point `linked_merchants` scoped to selected plan merchants.
5. Preserve the deterministic `demo-night-tour` release-gate path, v2.9 roster gate, v3.0 eligibility gate, and v3.1 merchant-fit evidence.
6. Avoid live map/weather/traffic integrations until a separate integration plan exists.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
