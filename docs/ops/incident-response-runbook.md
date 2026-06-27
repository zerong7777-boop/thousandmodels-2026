# Incident Response Runbook

Date: 2026-06-27

## Purpose

This runbook gives first checks and escalation paths for beta operations failures. It is not a customer support SLA or vendor monitoring process.

## CI Red

First checks:

- Open the failed GitHub Actions job.
- Identify whether the failure is API tests, web tests, web build, or repository hygiene.
- Reproduce the failing command locally before changing code.

Escalation:

- If the failure is deterministic, fix on a branch and rerun the focused command.
- If the failure depends on a missing external service or secret, mark the PR blocked and document the missing dependency.
- Do not merge with red CI unless the failure is explicitly documented as unrelated infrastructure outage.

## API Startup Failure

First checks:

- Confirm `APP_ENV`, `DEMO_MODE`, `APP_SECRET_KEY`, `ALLOWED_ORIGINS`, `CSRF_MODE`, `SESSION_COOKIE_SECURE`, and `AUTO_MIGRATE`.
- Run `python apps\api\scripts\migrate_store.py`.
- Call `/api/health` and `/api/ready` after startup.

Escalation:

- If startup fails on restricted environment guards, fix configuration first.
- If startup fails on schema state, run migrations or restore the previous database backup.
- If startup fails after a code change, roll back to the previous passing commit and rerun deployment smoke.

## Auth Failure

First checks:

- Confirm browser requests include an allowed origin.
- In non-demo mode, call `/api/auth/csrf` and confirm double-submit CSRF cookies and headers are present.
- Check whether demo accounts are expected for the current `DEMO_MODE`.

Escalation:

- If all login attempts fail, stop release and run `python -m pytest apps/api/tests/test_v21_security_settings.py apps/api/tests/test_v21_csrf_policy.py -q`.
- If only one role fails, inspect that user's seeded status and session cookie policy.

## Migration Failure

First checks:

- Run `python apps\api\scripts\migrate_store.py`.
- Inspect current and pending migration versions in the JSON output.
- Confirm the database path is writable by the API process.

Escalation:

- If a migration fails before data changes, fix the migration and rerun against a copied database.
- If a migration partially changed state, restore from the previous database backup before retrying.
- Do not start staging or production-like services with `AUTO_MIGRATE=true`.

## QwenPaw Failure

First checks:

- Confirm `RUN_LIVE_QWENPAW_SMOKE` is false outside local/demo.
- For local smoke, confirm `QWENPAW_BASE_URL` is reachable and `QWENPAW_AGENT_ID` is configured when required.
- Rerun the guarded QwenPaw smoke only from a local environment.

Escalation:

- If QwenPaw is unreachable, keep the deterministic product path active and record the smoke as blocked.
- Do not let QwenPaw output approve, publish, mutate state, or create coupon/redemption records.

## Public H5 Failure

First checks:

- Run deployment smoke against the API base URL.
- Confirm `/api/public/events/demo-night-tour` returns HTTP 200 and `event_id=demo-night-tour`.
- Confirm a plan has been generated and approved for the demo event.

Escalation:

- If the public event is missing, seed the demo event and approve plan v1 in a local/demo environment.
- If public H5 exposes internal errors or stack traces, stop release and fix the API error envelope before retrying.

## Repo Hygiene Failure

First checks:

- Run `python scripts\repo_hygiene.py --base origin/main`.
- Identify whether the failure is secrets, local paths, tracked `node_modules`, or generated artifacts.

Escalation:

- Remove generated artifacts from the release commit unless they are explicitly scoped evidence.
- Rotate any real secret that was committed or printed in logs.
- Do not bypass repository hygiene for release branches.

## Evidence

Record incident evidence in `docs/ai/VERIFY.md` when it affects a release, and summarize the current state in `docs/ai/STATUS.md`.
