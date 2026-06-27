from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime

CSRF_COOKIE = "zhiyin_csrf"


def issue_csrf_token(secret: str, now: datetime | None = None) -> str:
    issued_at = int((now or datetime.now(UTC)).timestamp())
    payload = {
        "ts": issued_at,
        "nonce": secrets.token_urlsafe(24),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_part = _base64url_encode(payload_bytes)
    signature_part = _sign(payload_part, secret)
    return f"{payload_part}.{signature_part}"


def verify_csrf_token(
    token: str,
    secret: str,
    max_age_seconds: int = 7200,
    now: datetime | None = None,
) -> bool:
    try:
        payload_part, signature_part = token.split(".", 1)
        if not payload_part or not signature_part:
            return False

        expected_signature = _sign(payload_part, secret)
        if not hmac.compare_digest(signature_part, expected_signature):
            return False

        payload = json.loads(_base64url_decode(payload_part))
        issued_at = int(payload["ts"])
        nonce = payload["nonce"]
        if not isinstance(nonce, str) or not nonce:
            return False

        current_ts = int((now or datetime.now(UTC)).timestamp())
        age_seconds = current_ts - issued_at
        return 0 <= age_seconds <= max_age_seconds
    except Exception:
        return False


def _sign(payload_part: str, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        payload_part.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return _base64url_encode(digest)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))
