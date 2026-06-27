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
