# NEXT

## Recommended Next Step

Complete v3.0 closeout: review the merchant network diff, then commit, push, and open a PR for `feat/v30-merchant-network-pack`.

After v3.0 is merged, the recommended next implementation phase is `v3.1-event-planning-eligibility-pack`.

v3.0 makes the merchant network credible enough for organizer setup, but route generation still mostly treats eligibility as a gate instead of using merchant fit as planning intelligence. The next useful product package is to make planner output use merchant-network data more directly:

1. Feed merchant category tags, capacity notes, operating windows, and participation constraints into non-demo route candidate selection.
2. Explain why each selected merchant fits the event brief, target audience, weather/time context, and route role.
3. Surface planner warnings when ready roster merchants are eligible but weak fits for the event.
4. Keep planner output deterministic and evidence-backed before introducing any live model scoring.
5. Preserve the deterministic `demo-night-tour` release-gate path and existing v2.9 roster gate.
6. Avoid POS/payment/hardware/map/weather/traffic integrations until a separate integration plan exists.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
