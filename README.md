# 智引濠江 MVP Workspace

This workspace implements a deterministic demo loop for the University of Macau Thousand Models AI Developer Student Competition.

## Project

- Task ID: `20260518-thousandmodels-ai-competition`
- Concept: `智引濠江：旧区文旅活动编排 Agent MVP`
- Project root: `<PROJECT_ROOT>`
- Control-plane root: `<CONTROL_PLANE_ROOT>`

## Demo Loop

The MVP demonstrates:

`创建活动 -> 生成方案 -> 主办方确认 -> 商户执行包 -> 游客 H5 -> 库存/天气异常 -> 主办方确认恢复 -> 游客端更新 -> 复盘报告`

The default path does not require `DASHSCOPE_API_KEY`. It uses a deterministic local Agent backend and keeps the Qwen/QwenPaw adapter behind the same interface.

## Auth And Demo Boundary

The local workspace defaults to demo mode:

- `APP_ENV=local`
- `DEMO_MODE=true`
- `CSRF_MODE=demo`
- `VITE_DEMO_MODE=true`

This keeps the seeded demo accounts, visible login quick-fill controls, localhost cookies, and deterministic demo loop usable without external identity infrastructure.

Production-like deployments must disable demo mode and provide explicit security settings:

- `APP_ENV=production`
- `DEMO_MODE=false`
- `APP_SECRET_KEY=<deployment secret>`
- `SESSION_COOKIE_SECURE=true`
- `CSRF_MODE=double-submit`
- `ALLOWED_ORIGINS=https://<allowed-origin>`
- `VITE_DEMO_MODE=false`

Startup validation rejects unsafe production settings such as demo account seeding, demo CSRF, missing secret material, insecure cookies, or non-HTTPS production origins. v2.1 is a beta security baseline; it does not add public registration, OAuth/SSO, password reset, tenant isolation, or a production user administration console.

## Run API

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .[dev]
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

## Store Migrations

The API store is migration-managed. Local/demo mode applies known SQLite migrations automatically when `MVPStore` opens the database.

Run migrations explicitly with:

```powershell
cd apps/api
python scripts\migrate_store.py
```

For production-like environments, set `AUTO_MIGRATE=false` to refuse startup when migrations are pending, then run the migration script as an explicit deployment step. v2.2 keeps SQLite compatibility for beta/demo usage; it does not add PostgreSQL operations, backups, rollback automation, or tenant isolation.

## Deployment Readiness

v2.3 defines the local/demo/staging/production-like environment contract in `docs/research/v2.3-environment-contract.md`.

The API exposes:

- `GET /api/health` for lightweight liveness.
- `GET /api/ready` for environment, store, migration, auth policy, and optional provider readiness summaries.

Run a deployment smoke against a running API with:

```powershell
python apps\api\scripts\deployment_smoke.py --base-url http://127.0.0.1:8000
```

Run the live E2E release gate against a running local/demo API with:

```powershell
python apps\api\scripts\release_gate.py --base-url http://127.0.0.1:8000 --output docs\research\assets\v2.5-live-e2e-release-gate\release-gate-result.json
```

The release gate uses real HTTP sessions and the deterministic demo accounts to verify health, readiness, auth boundary, organizer planning and approval, event-page publish, merchant-edge packages, public scan/claim/redeem, merchant workbench, review report, and process-local metrics. It does not start servers, run browsers, call Qwen/QwenPaw, or prove cloud production readiness.

Staging/production-like startup must use `DEMO_MODE=false`, `CSRF_MODE=double-submit`, explicit HTTPS `ALLOWED_ORIGINS`, secure cookies, and `AUTO_MIGRATE=false`. `RUN_LIVE_QWENPAW_SMOKE=true` and localhost `QWENPAW_BASE_URL` values are rejected outside local/demo mode.

v2.3 intentionally does not add Dockerfiles because the deployment target is still unspecified. Use the existing local commands plus the deployment smoke and v2.5 release gate until a concrete hosting target is selected.

## Observability And Runbooks

v2.4 adds a beta operations baseline:

- every API response includes `X-Request-ID`;
- API request logs are JSON structured and include request ID, route template, status, duration, and authenticated actor when available;
- HTTP errors and unhandled errors return a consistent `error` envelope with the request ID;
- `GET /api/metrics` exposes in-process beta counters for health, auth failures, agent runs, QwenPaw advisory runs, public interactions, recovery approvals, and review reports;
- release and incident response runbooks live in `docs/ops/`.

This is not a vendor monitoring stack. It does not add OpenTelemetry, Prometheus/Grafana hosting, PagerDuty, SLOs, or customer incident operations.

## Run Web

```powershell
cd apps/web
npm install
npm run test
npm run build
npm run dev
```

Open `http://127.0.0.1:5173`.

## Scope Limits

- No hardware.
- No real merchant integration.
- No real traffic prediction.
- No model training or fine-tuning.
- No Qwen/QwenPaw dependency before the deterministic loop works.
