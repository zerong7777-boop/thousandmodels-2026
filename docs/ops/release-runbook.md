# Release Runbook

Date: 2026-06-27

## Purpose

This runbook defines the repeatable beta release path for the current app. It is a lightweight operations baseline, not a managed deployment or formal SLO process.

## Pre-Release Checks

Run from the project root unless a command changes directory.

```powershell
Push-Location apps\api
python -m pytest -q
Pop-Location

Push-Location apps\web
npm.cmd run test
npm.cmd run build
Pop-Location

python scripts\repo_hygiene.py --base origin/main
git diff --check
```

The API suite must pass before release. The web test suite and production build must pass before release. Repository hygiene must pass before any branch is pushed for review.

## CI Checks

Before merge, confirm GitHub Actions completes the repository workflow for:

- API tests;
- web tests;
- web production build;
- repository hygiene.

If CI is red, stop the release and use the incident response runbook section "CI red".

## Migration

Before staging or production-like startup, run the explicit migration command:

```powershell
python apps\api\scripts\migrate_store.py
```

For staging or production-like environments, set `AUTO_MIGRATE=false` after migrations have been applied.

## Deployment Smoke

After starting the API, prepare or confirm the public demo event exists, then run:

```powershell
python apps\api\scripts\deployment_smoke.py --base-url http://127.0.0.1:8000
```

The smoke must pass for:

- `/api/health`;
- `/api/ready`;
- `/api/public/events/demo-night-tour`.

## Live E2E Release Gate

After the deployment smoke passes, run the release gate against the same local/demo API:

```powershell
python apps\api\scripts\release_gate.py --base-url http://127.0.0.1:8000 --output docs\research\assets\v2.5-live-e2e-release-gate\release-gate-result.json
```

The gate must pass these API-level checks:

- health and readiness;
- unauthenticated protected-route error envelope;
- organizer login, demo seed, plan generation, and plan approval;
- event-page draft and publish;
- merchant-edge package generation;
- public event projection without internal terms;
- public scan, coupon claim, and redemption;
- merchant login and workbench package visibility;
- review report generation;
- metrics counters touched by the gate.

The release gate is deterministic and local/demo-scoped. It does not start servers, run Playwright, call Qwen/QwenPaw, or prove cloud deployment readiness.

## Rollback

Use the hosting platform's previous deployment or the previous Git commit as the rollback target. After rollback, rerun the deployment smoke command against the restored service and record the commit SHA, smoke result, and operator initials in release evidence.

## Acceptable Warnings

The current accepted warnings are:

- existing FastAPI and Starlette deprecation warnings in backend tests;
- existing Vite large chunk warning for the web production build.

New warnings that include secrets, local absolute paths, stack traces in public responses, or failed checks are not acceptable.

## Evidence Paths

Record release evidence in:

- `docs/ai/VERIFY.md` for command results;
- `docs/ai/STATUS.md` for current state;
- `docs/ai/NEXT.md` for the next recommended phase;
- GitHub PR checks for CI status.

## Boundary

This runbook does not add managed secrets, TLS, backups, alert routing, or customer incident operations. It is the release discipline expected for an operable beta candidate.
