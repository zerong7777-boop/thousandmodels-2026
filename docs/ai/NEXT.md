# NEXT

## Recommended Next Step

v3.4 is implemented and full local release verification has passed. The immediate closeout step is to commit, push, and open a PR for `feat/v34-event-operations-command-center-pack`.

After v3.4 is merged, the recommended next implementation phase is `v3.5-integration-readiness-pack`.

v3.4 makes the organizer side operationally clearer by consolidating launch readiness, blockers, warnings, action items, and audit evidence. The next product gap is not more demo UI; it is preparing the codebase to connect real external information without corrupting the deterministic demo path or letting provider output mutate authority directly:

1. Define connector contracts for weather, map/walking distance, merchant/POS inventory, and notification channels.
2. Add provider configuration and capability checks that are disabled by default in local/demo mode.
3. Add read-only adapter interfaces with sanitized evidence capture and explicit failure classification.
4. Add a deterministic fake-provider baseline so tests remain stable without external credentials.
5. Add one narrow end-to-end connector spike target for a later phase, likely weather or walking-distance enrichment.
6. Keep human approval boundaries intact: no automatic plan approval, public publication, recovery approval, or provider-driven authoritative mutation.
7. Preserve v2.9-v3.4 gates, command-center checks, and the deterministic release path.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, DashScope, map, weather, POS, payment, or notification providers required for the deterministic demo.
- Do not allow model, QwenPaw, or external-provider output to approve, publish, recover, or mutate authoritative state.
- Do not expose raw model/backend/provider terms on merchant, tourist, or public H5 pages.
- Do not add public merchant onboarding, open registration, real identity administration, settlement, payment, POS, hardware, real traffic prediction, or customer incident operations before a new plan.
- Do not use optional Qwen or QwenPaw live evidence as a business-success claim; it is only provider reachability/advisory evidence.
- Do not run backend pytest in parallel against the default SQLite database; use serial runs or isolated database paths.
- Do not stage historical screenshot PNG diffs unless a separate evidence-refresh task explicitly owns them.
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
- Do not treat v3.3 as real merchant onboarding or identity administration; it is selected-event setup evidence for already-known local merchants.
- Do not treat v3.4 as real external operations intelligence; it is a read-only command center over existing local state.
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
