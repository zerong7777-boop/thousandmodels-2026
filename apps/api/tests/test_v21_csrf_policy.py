from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import main
from app.auth import verify_mutation_origin
from app.csrf import CSRF_COOKIE, issue_csrf_token, verify_csrf_token
from app.settings import load_settings


def _request(method="POST", origin=None, csrf=None, cookie_csrf=None):
    headers = {}
    cookies = {}
    if origin is not None:
        headers["origin"] = origin
    if csrf is not None:
        headers["x-zhiyin-csrf"] = csrf
    if cookie_csrf is not None:
        cookies[CSRF_COOKIE] = cookie_csrf
    return SimpleNamespace(method=method, headers=headers, cookies=cookies)


def _non_demo_settings():
    return load_settings(
        {
            "APP_ENV": "production",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://app.example.com",
        }
    )


def _assert_forbidden(request, settings):
    with pytest.raises(HTTPException) as exc:
        verify_mutation_origin(request, settings=settings)
    assert exc.value.status_code == 403


def test_demo_header_is_accepted_in_demo_mode():
    settings = load_settings({"APP_ENV": "local", "DEMO_MODE": "true"})

    verify_mutation_origin(_request(csrf="demo"), settings=settings)


def test_non_demo_rejects_demo_header():
    settings = _non_demo_settings()

    _assert_forbidden(
        _request(
            origin="https://app.example.com",
            csrf="demo",
            cookie_csrf="demo",
        ),
        settings,
    )


def test_local_non_demo_rejects_demo_header_even_when_csrf_mode_is_demo():
    settings = load_settings(
        {
            "APP_ENV": "local",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "demo",
            "ALLOWED_ORIGINS": "http://127.0.0.1:5173",
        }
    )

    _assert_forbidden(
        _request(
            origin="http://127.0.0.1:5173",
            csrf="demo",
            cookie_csrf="demo",
        ),
        settings,
    )


def test_non_demo_accepts_valid_double_submit_token():
    settings = _non_demo_settings()
    token = issue_csrf_token(settings.required_secret())

    verify_mutation_origin(
        _request(
            origin="https://app.example.com",
            csrf=token,
            cookie_csrf=token,
        ),
        settings=settings,
    )


@pytest.mark.parametrize(
    "mutation_request",
    [
        _request(origin="https://app.example.com", csrf="demo"),
        _request(origin="https://app.example.com", csrf="demo", cookie_csrf="other"),
        _request(origin="https://app.example.com", csrf="bad-token", cookie_csrf="bad-token"),
        _request(origin="https://evil.example.com", csrf="demo", cookie_csrf="demo"),
    ],
)
def test_non_demo_rejects_invalid_double_submit_cases(mutation_request):
    _assert_forbidden(mutation_request, _non_demo_settings())


def test_csrf_token_verification_rejects_expired_tokens():
    issued_at = datetime(2026, 1, 1, tzinfo=UTC)
    token = issue_csrf_token("test-secret", now=issued_at)

    assert verify_csrf_token(
        token,
        "test-secret",
        max_age_seconds=7200,
        now=issued_at + timedelta(seconds=7201),
    ) is False


def test_csrf_endpoint_sets_readable_cookie_and_returns_token(monkeypatch):
    settings = load_settings(
        {
            "APP_ENV": "local",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "SESSION_COOKIE_SECURE": "true",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://app.example.com",
        }
    )
    monkeypatch.setattr(main, "load_settings", lambda: settings)

    with TestClient(main.app) as client:
        response = client.get("/api/auth/csrf")

    assert response.status_code == 200
    token = response.json()["csrf_token"]
    assert verify_csrf_token(token, settings.required_secret()) is True
    assert response.cookies[CSRF_COOKIE] == token

    set_cookie = response.headers["set-cookie"].lower()
    assert "zhiyin_csrf=" in set_cookie
    assert "path=/" in set_cookie
    assert "secure" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "httponly" not in set_cookie


def test_csrf_endpoint_omits_secure_cookie_when_setting_is_false(monkeypatch):
    settings = load_settings(
        {
            "APP_ENV": "local",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "SESSION_COOKIE_SECURE": "false",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://app.example.com",
        }
    )
    monkeypatch.setattr(main, "load_settings", lambda: settings)

    with TestClient(main.app) as client:
        response = client.get("/api/auth/csrf")

    assert response.status_code == 200
    set_cookie = response.headers["set-cookie"].lower()
    assert "zhiyin_csrf=" in set_cookie
    assert "secure" not in set_cookie
    assert "httponly" not in set_cookie


def test_default_cors_policy_keeps_local_demo_origins_and_regex():
    middleware = next(
        item for item in main.app.user_middleware if item.cls.__name__ == "CORSMiddleware"
    )

    assert "http://127.0.0.1:5173" in middleware.kwargs["allow_origins"]
    assert "http://localhost:5174" in middleware.kwargs["allow_origins"]
    assert middleware.kwargs["allow_origin_regex"] == main.LOCAL_DEV_ORIGIN_REGEX


def test_non_demo_cors_policy_uses_configured_origins_without_localhost_regex():
    settings = load_settings(
        {
            "APP_ENV": "production",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://app.example.com",
        }
    )

    assert main.cors_allow_origins(settings) == ["https://app.example.com"]
    assert main.cors_allow_origin_regex(settings) is None
