from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

REQUIRED_ENV_KEYS = {
    "APP_ENV",
    "DEMO_MODE",
    "APP_SECRET_KEY",
    "ALLOWED_ORIGINS",
    "CSRF_MODE",
    "SESSION_COOKIE_SECURE",
    "SESSION_SAMESITE",
    "SESSION_TTL_HOURS",
    "DATABASE_URL",
    "AUTO_MIGRATE",
    "AGENT_BACKEND",
    "AGENT_DRAFT_BACKEND",
    "DASHSCOPE_API_KEY",
    "QWEN_MODEL",
    "RUN_LIVE_QWENPAW_SMOKE",
    "QWENPAW_BASE_URL",
    "QWENPAW_AGENT_ID",
    "VITE_API_BASE_URL",
    "VITE_DEMO_MODE",
}


def _env_example_keys() -> set[str]:
    keys: set[str] = set()
    for line in (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, _, _ = stripped.partition("=")
        keys.add(key)
    return keys


def test_env_example_documents_required_v23_keys():
    assert REQUIRED_ENV_KEYS.issubset(_env_example_keys())
