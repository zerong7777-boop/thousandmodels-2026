import hmac
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request, Response

from app.csrf import CSRF_COOKIE, verify_csrf_token
from app.schemas import AuthResponse, AuthSessionRecord, AuthUserRecord, AuthUserResponse
from app.security import hash_password, hash_session_token, verify_password
from app.settings import AppSettings, load_settings
from app.store import MVPStore, STORE

SESSION_COOKIE = "zhiyin_session"
SETTINGS = load_settings()
ALLOWED_MUTATION_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}
LOCAL_DEV_ORIGIN_HOSTS = {"127.0.0.1", "localhost"}


def public_user(user: AuthUserRecord) -> AuthUserResponse:
    return AuthUserResponse(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        display_name=user.display_name,
        merchant_id=user.merchant_id,
    )


def create_login_session(
    response: Response,
    user: AuthUserRecord,
    store: MVPStore = STORE,
    settings: AppSettings = SETTINGS,
) -> AuthResponse:
    token = secrets.token_urlsafe(48)
    now = datetime.now(UTC)
    max_age = settings.session_ttl_hours * 60 * 60
    store.create_session(
        AuthSessionRecord(
            session_id=f"sess_{secrets.token_urlsafe(18)}",
            token_hash=hash_session_token(token),
            user_id=user.user_id,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=settings.session_ttl_hours)).isoformat(),
        )
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=max_age,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_samesite,
        path="/",
    )
    return AuthResponse(user=public_user(user))


def clear_session_cookie(response: Response, settings: AppSettings = SETTINGS) -> None:
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        secure=settings.session_cookie_secure,
        samesite=settings.session_samesite,
    )


def get_current_user(request: Request) -> AuthUserRecord:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="not authenticated")
    session = STORE.get_session_by_token_hash(hash_session_token(token))
    if not session:
        raise HTTPException(status_code=401, detail="not authenticated")
    if session.revoked_at:
        raise HTTPException(status_code=401, detail="not authenticated")
    if datetime.fromisoformat(session.expires_at) <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail="not authenticated")
    user = STORE.get_user(session.user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="not authenticated")
    return user


def require_organizer(user: AuthUserRecord = Depends(get_current_user)) -> AuthUserRecord:
    if user.role != "organizer":
        raise HTTPException(status_code=403, detail="forbidden")
    return user


def require_merchant(user: AuthUserRecord = Depends(get_current_user)) -> AuthUserRecord:
    if user.role != "merchant":
        raise HTTPException(status_code=403, detail="forbidden")
    return user


def verify_merchant_owner(merchant_id: str, user: AuthUserRecord) -> None:
    if user.role == "merchant" and user.merchant_id != merchant_id:
        raise HTTPException(status_code=403, detail="forbidden")


def is_allowed_local_dev_origin(origin: str | None) -> bool:
    if not origin:
        return False
    parsed = urlparse(origin)
    return parsed.scheme == "http" and parsed.hostname in LOCAL_DEV_ORIGIN_HOSTS and parsed.port is not None


def verify_mutation_origin(request: Request, settings: AppSettings = SETTINGS) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    origin = request.headers.get("origin")
    csrf = request.headers.get("x-zhiyin-csrf")
    if settings.demo_mode:
        if (
            origin in settings.allowed_origins
            or origin in ALLOWED_MUTATION_ORIGINS
            or is_allowed_local_dev_origin(origin)
        ):
            return
        if csrf == "demo":
            return
        raise HTTPException(status_code=403, detail="invalid mutation origin")

    if origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="invalid mutation origin")

    cookie_csrf = request.cookies.get(CSRF_COOKIE)
    if not csrf or not cookie_csrf or not hmac.compare_digest(csrf, cookie_csrf):
        raise HTTPException(status_code=403, detail="invalid csrf token")

    if not verify_csrf_token(csrf, settings.required_secret()):
        raise HTTPException(status_code=403, detail="invalid csrf token")
