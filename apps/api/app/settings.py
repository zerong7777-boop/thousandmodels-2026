from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse


APP_ENV_VALUES = {"local", "demo", "staging", "production"}
CSRF_MODE_VALUES = {"demo", "double-submit"}
SESSION_SAMESITE_VALUES = {"lax", "strict", "none"}
LOCAL_ALLOWED_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
)
DEV_ONLY_SECRET = "local-dev-only-secret"


@dataclass(frozen=True)
class AppSettings:
    app_env: str
    demo_mode: bool
    app_secret_key: str | None
    session_cookie_secure: bool
    session_samesite: str
    session_ttl_hours: int
    csrf_mode: str
    allowed_origins: tuple[str, ...]
    auto_migrate: bool = True
    run_live_qwenpaw_smoke: bool = False
    qwenpaw_base_url: str | None = None
    qwenpaw_agent_id: str | None = None

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def validate_startup(self) -> None:
        if self.app_env in {"staging", "production"}:
            if self.demo_mode:
                raise RuntimeError("DEMO_MODE must be false for staging/production")
            if not self.app_secret_key:
                raise RuntimeError("APP_SECRET_KEY is required for staging/production")
            if not self.session_cookie_secure:
                raise RuntimeError("SESSION_COOKIE_SECURE must be true for staging/production")
            if self.csrf_mode != "double-submit":
                raise RuntimeError("CSRF_MODE must be double-submit for staging/production")
            if not self.allowed_origins:
                raise RuntimeError("ALLOWED_ORIGINS must be set for staging/production")
            malformed_origins = [
                origin for origin in self.allowed_origins if not _is_https_origin(origin)
            ]
            if malformed_origins:
                raise RuntimeError("ALLOWED_ORIGINS must contain only valid HTTPS origins")
            if self.auto_migrate:
                raise RuntimeError("AUTO_MIGRATE must be false for staging/production")
            if self.run_live_qwenpaw_smoke:
                raise RuntimeError(
                    "RUN_LIVE_QWENPAW_SMOKE must be false for staging/production"
                )
            if self.qwenpaw_base_url and _is_local_url(self.qwenpaw_base_url):
                raise RuntimeError(
                    "QWENPAW_BASE_URL must not point to localhost for staging/production"
                )

        if self.session_samesite == "none" and not self.session_cookie_secure:
            raise RuntimeError("SESSION_SAMESITE=none requires secure cookies")

    def required_secret(self) -> str:
        if self.app_secret_key:
            return self.app_secret_key
        if self.app_env in {"local", "demo"}:
            return DEV_ONLY_SECRET
        raise RuntimeError("APP_SECRET_KEY is required for staging/production")


def load_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    source = os.environ if environ is None else environ
    app_env = _parse_choice(source.get("APP_ENV", "local"), "APP_ENV", APP_ENV_VALUES)
    demo_mode = _parse_bool(
        source.get("DEMO_MODE"),
        "DEMO_MODE",
        default=app_env in {"local", "demo"},
    )
    session_cookie_secure = _parse_session_cookie_secure(
        source.get("SESSION_COOKIE_SECURE"), app_env
    )
    session_samesite = _parse_choice(
        source.get("SESSION_SAMESITE", "lax"),
        "SESSION_SAMESITE",
        SESSION_SAMESITE_VALUES,
    )
    session_ttl_hours = _parse_positive_int(
        source.get("SESSION_TTL_HOURS", "8"),
        "SESSION_TTL_HOURS",
    )
    csrf_mode = _parse_choice(
        source.get("CSRF_MODE", "demo" if demo_mode else "double-submit"),
        "CSRF_MODE",
        CSRF_MODE_VALUES,
    )
    allowed_origins = _parse_allowed_origins(source.get("ALLOWED_ORIGINS"), app_env)
    auto_migrate = _parse_bool(source.get("AUTO_MIGRATE"), "AUTO_MIGRATE", default=True)
    run_live_qwenpaw_smoke = _parse_bool(
        source.get("RUN_LIVE_QWENPAW_SMOKE"),
        "RUN_LIVE_QWENPAW_SMOKE",
        default=False,
    )

    return AppSettings(
        app_env=app_env,
        demo_mode=demo_mode,
        app_secret_key=_optional_secret(source.get("APP_SECRET_KEY")),
        session_cookie_secure=session_cookie_secure,
        session_samesite=session_samesite,
        session_ttl_hours=session_ttl_hours,
        csrf_mode=csrf_mode,
        allowed_origins=allowed_origins,
        auto_migrate=auto_migrate,
        run_live_qwenpaw_smoke=run_live_qwenpaw_smoke,
        qwenpaw_base_url=_optional_secret(source.get("QWENPAW_BASE_URL")),
        qwenpaw_agent_id=_optional_secret(source.get("QWENPAW_AGENT_ID")),
    )


def load_validated_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    settings = load_settings(environ)
    settings.validate_startup()
    return settings


def _parse_choice(value: str, name: str, allowed: set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {choices}")
    return normalized


def _parse_bool(value: str | None, name: str, *, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false")


def _parse_session_cookie_secure(value: str | None, app_env: str) -> bool:
    if value is None:
        value = "auto"
    normalized = value.strip().lower()
    if normalized == "auto":
        return app_env in {"staging", "production"}
    return _parse_bool(normalized, "SESSION_COOKIE_SECURE", default=False)


def _parse_positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed


def _parse_allowed_origins(value: str | None, app_env: str) -> tuple[str, ...]:
    if value is None:
        return LOCAL_ALLOWED_ORIGINS if app_env in {"local", "demo"} else ()
    return tuple(origin.strip() for origin in value.split(",") if origin.strip())


def _optional_secret(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _is_https_origin(origin: str) -> bool:
    if any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in origin
    ):
        return False

    parsed = urlparse(origin)
    if parsed.netloc.endswith(":"):
        return False

    try:
        parsed.port
    except ValueError:
        return False

    hostname = parsed.hostname
    if hostname is None or any(character.isspace() for character in hostname):
        return False

    return (
        parsed.scheme == "https"
        and hostname
        and parsed.username is None
        and parsed.password is None
        and parsed.path == ""
        and not parsed.params
        and not parsed.query
        and not parsed.fragment
    )


def _is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname in {"localhost", "127.0.0.1", "::1"}
