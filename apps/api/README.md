# 智引濠江 API

FastAPI backend for the deterministic old-district event orchestration demo.

## Commands

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .[dev]
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

The API defaults to `AGENT_BACKEND=deterministic` and does not require `DASHSCOPE_API_KEY`.
