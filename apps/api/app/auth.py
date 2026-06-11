import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request, Response

from app.schemas import AuthResponse, AuthSessionRecord, AuthUserRecord, AuthUserResponse
from app.store import MVPStore, STORE

SESSION_COOKIE = "zhiyin_session"
SESSION_TTL_HOURS = 8
PBKDF2_ITERATIONS = 260000
ALLOWED_MUTATION_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}
LOCAL_DEV_ORIGIN_HOSTS = {"127.0.0.1", "localhost"}


def hash_password(password: str, salt: bytes | None = None) -> str:
    actual_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        actual_salt,
        PBKDF2_ITERATIONS,
    )
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(actual_salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def public_user(user: AuthUserRecord) -> AuthUserResponse:
    return AuthUserResponse(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        display_name=user.display_name,
        merchant_id=user.merchant_id,
    )


def create_login_session(
    response: Response, user: AuthUserRecord, store: MVPStore = STORE
) -> AuthResponse:
    token = secrets.token_urlsafe(48)
    now = datetime.now(UTC)
    store.create_session(
        AuthSessionRecord(
            session_id=f"sess_{secrets.token_urlsafe(18)}",
            token_hash=hash_session_token(token),
            user_id=user.user_id,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=SESSION_TTL_HOURS)).isoformat(),
        )
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_TTL_HOURS * 60 * 60,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return AuthResponse(user=public_user(user))


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", samesite="lax")


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


def verify_mutation_origin(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    origin = request.headers.get("origin")
    csrf = request.headers.get("x-zhiyin-csrf")
    if origin in ALLOWED_MUTATION_ORIGINS or is_allowed_local_dev_origin(origin):
        return
    if csrf == "demo":
        return
    raise HTTPException(status_code=403, detail="invalid mutation origin")
