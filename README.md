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

## Run API

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .[dev]
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

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
