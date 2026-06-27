from __future__ import annotations

import os
from typing import TYPE_CHECKING
from typing import Any

from app.agents.orchestrator import choose_agent_backend
from app.migrations.runner import latest_schema_version, pending_versions
from app.settings import AppSettings

if TYPE_CHECKING:
    from app.store import MVPStore


def build_readiness_payload(settings: AppSettings, store: "MVPStore") -> dict[str, Any]:
    connectivity = _store_connectivity(store)
    pending = pending_versions(store.conn) if connectivity == "ok" else []
    return {
        "status": "ready" if connectivity == "ok" else "not_ready",
        "settings": {
            "app_env": settings.app_env,
            "demo_mode": settings.demo_mode,
        },
        "store": {
            "kind": "sqlite",
            "connectivity": connectivity,
            "schema_version": latest_schema_version(store.conn) if connectivity == "ok" else None,
            "pending_migrations": len(pending),
        },
        "auth_policy": {
            "csrf_mode": settings.csrf_mode,
            "session_cookie_secure": settings.session_cookie_secure,
            "session_samesite": settings.session_samesite,
        },
        "providers": {
            "agent_backend": choose_agent_backend().__class__.__name__,
            "agent_draft_backend": os.getenv("AGENT_DRAFT_BACKEND", "deterministic").strip().lower(),
            "qwen": {
                "enabled": _is_qwen_enabled(),
                "model_configured": bool(os.getenv("QWEN_MODEL", "").strip()),
            },
            "qwenpaw_smoke": {
                "enabled": settings.run_live_qwenpaw_smoke,
                "base_url_configured": bool(settings.qwenpaw_base_url),
                "agent_id_configured": bool(settings.qwenpaw_agent_id),
            },
        },
    }


def _store_connectivity(store: MVPStore) -> str:
    try:
        store.conn.execute("SELECT 1").fetchone()
    except Exception:
        return "error"
    return "ok"


def _is_qwen_enabled() -> bool:
    return (
        os.getenv("AGENT_DRAFT_BACKEND", "deterministic").strip().lower() == "qwen"
        and bool(os.getenv("DASHSCOPE_API_KEY", "").strip())
    )
