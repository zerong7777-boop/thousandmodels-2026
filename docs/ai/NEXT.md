# NEXT

## Recommended Next Step

Complete v2.6 closeout: commit the browser release evidence branch, push it, open a PR, and observe GitHub Actions before merge. After that, the recommended next implementation phase is `v2.7-real-product-logic-foundation`.

v2.5 and v2.6 now prove the deterministic local beta through API and browser gates. The next useful work should stop adding release wrappers and start improving real product logic:

1. Define a real event/workspace lifecycle beyond the single `demo-night-tour` fixture.
2. Split demo seed data from user-created event data.
3. Add organizer-created events, merchant assignment lifecycle, and package status transitions.
4. Make public interactions idempotent and safer for repeated claims/redeems.
5. Make review metrics derive from stored event activity rather than demo assumptions.
6. Preserve deterministic demo mode as a fixture path for verification.

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
- Do not assume GitHub Actions is green until the pushed workflow run is observed.
