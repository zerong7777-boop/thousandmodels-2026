from datetime import datetime, timedelta

from fastapi import Response

from app.auth import clear_session_cookie, create_login_session
from app.seed import seed_demo_accounts
from app.settings import load_settings
from app.store import MVPStore


def _store_with_demo_users() -> MVPStore:
    store = MVPStore(":memory:")
    seed_demo_accounts(store)
    return store


def _demo_user(store: MVPStore):
    user = store.get_user_by_username("organizer.demo")
    assert user is not None
    return user


def test_local_settings_set_login_cookie_without_secure_flag():
    response = Response()
    store = _store_with_demo_users()

    create_login_session(response, _demo_user(store), store=store, settings=load_settings({}))

    set_cookie = response.headers["set-cookie"]
    assert "zhiyin_session=" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()
    assert "max-age=28800" in set_cookie.lower()
    assert "secure" not in set_cookie.lower()


def test_production_settings_set_secure_login_cookie_with_configured_policy():
    response = Response()
    store = _store_with_demo_users()
    settings = load_settings(
        {
            "APP_ENV": "production",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "SESSION_SAMESITE": "none",
            "SESSION_TTL_HOURS": "2",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    create_login_session(response, _demo_user(store), store=store, settings=settings)

    set_cookie = response.headers["set-cookie"]
    session = store.list_sessions_for_user("usr_org_demo")[0]
    expires_at = datetime.fromisoformat(session.expires_at)
    created_at = datetime.fromisoformat(session.created_at)
    assert "zhiyin_session=" in set_cookie
    assert "secure" in set_cookie.lower()
    assert "httponly" in set_cookie.lower()
    assert "samesite=none" in set_cookie.lower()
    assert "max-age=7200" in set_cookie.lower()
    assert expires_at - created_at == timedelta(hours=settings.session_ttl_hours)


def test_clear_session_cookie_uses_matching_production_cookie_policy():
    response = Response()
    settings = load_settings(
        {
            "APP_ENV": "production",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "SESSION_SAMESITE": "strict",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    clear_session_cookie(response, settings=settings)

    set_cookie = response.headers["set-cookie"]
    assert "zhiyin_session=" in set_cookie
    assert "max-age=0" in set_cookie.lower()
    assert "path=/" in set_cookie.lower()
    assert "secure" in set_cookie.lower()
    assert "samesite=strict" in set_cookie.lower()
