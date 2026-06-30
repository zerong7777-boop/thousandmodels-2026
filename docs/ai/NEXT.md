# NEXT

## Recommended Next Step

v3.3 is implemented and locally verified. The immediate closeout step is to commit, push, and open a PR for `feat/v33-merchant-portal-setup-pack`.

After v3.3 is merged, the recommended next implementation phase is `v3.4-event-operations-command-center-pack`.

v3.3 makes merchant setup evidence real enough to gate planning, but the organizer still has to mentally connect roster readiness, plan state, event page publication, merchant-edge packages, public notices, and incident suggestions across several surfaces. The next useful product package is to make the organizer day-of command center more commercial-grade:

1. Add one event operations command center that summarizes readiness across plan approval, event page publication, merchant setup, package generation, public notices, and active incidents.
2. Add explicit pre-launch checks so organizers can see which operational steps are blocking launch or package readiness.
3. Add event-scoped action history and operator-facing audit evidence for setup submission, mark-ready, plan generation, approval, page publish, package generation, and public notices.
4. Add better day-of exception triage states: open, suggested, approved, resolved, and stale.
5. Keep human approval boundaries intact: no automatic plan approval, public publication, or Qwen/QwenPaw authoritative mutation.
6. Preserve the deterministic demo path, v2.9-v3.3 gates, and local-catalog constraints.

## Do Not Do Yet

- Do not treat QwenPaw advisory qualification as production orchestration.
- Do not make QwenPaw, Qwen, or DashScope required for the deterministic demo.
- Do not allow model or QwenPaw output to approve, publish, or mutate authoritative state.
- Do not expose raw model/backend terms on merchant, tourist, or public H5 pages.
- Do not add real merchant, POS, payment, hardware, map, weather, traffic, or visitor identity integrations before a new plan.
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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
