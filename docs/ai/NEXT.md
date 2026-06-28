# NEXT

## Recommended Next Step

Complete v2.8 closeout: run repository hygiene and whitespace verification, then commit, push, and open a PR for `feat/v28-organizer-event-workspace`.

After v2.8 is merged, the recommended next implementation phase is `v2.9-event-merchant-setup`.

v2.8 makes non-demo event creation and selected-event workspace navigation usable from the organizer UI. The next useful work is to make a created event operationally configurable before route planning:

1. Add a minimal merchant participation setup for a selected event.
2. Let organizers select from the existing local merchant/catalog data without inventing external merchant integrations.
3. Show which merchants are included, missing, or not ready before plan generation.
4. Keep planning, event page, packages, and review scoped to the selected event id.
5. Preserve the deterministic `demo-night-tour` release-gate path.
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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
