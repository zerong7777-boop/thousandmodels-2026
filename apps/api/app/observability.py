import json
import logging
import re
import time
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Request
from starlette.responses import JSONResponse
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")
LOGGER = logging.getLogger("app.observability")
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
SENSITIVE_FIELD_MARKERS = (
    "authorization",
    "cookie",
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "provider_payload",
    "raw_payload",
    "raw_response",
)
PATH_TRAILING_WORDS = "with|and|for|from|to|via|because|while|using|when|error|failed"
WINDOWS_ABSOLUTE_PATH = re.compile(
    rf"[A-Za-z]:[\\/](?:(?!\s+(?:{PATH_TRAILING_WORDS})\b)[^\"'\r\n,;])+",
    re.IGNORECASE,
)
POSIX_LOCAL_PATH = re.compile(
    rf"/(?:users|home|var|tmp|private|mnt|volumes)/(?:(?!\s+(?:{PATH_TRAILING_WORDS})\b)[^\"'\r\n,;])+",
    re.IGNORECASE,
)
BEARER_TOKEN = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
INLINE_SECRET = re.compile(
    r"\b(api[_-]?key|token|password|secret)=([^\s,;]+)",
    re.IGNORECASE,
)


def is_safe_request_id(value: str | None) -> bool:
    if not value or len(value) > MAX_REQUEST_ID_LENGTH:
        return False
    return REQUEST_ID_PATTERN.fullmatch(value) is not None


def select_request_id(request: Request) -> str:
    request_id = request.headers.get(REQUEST_ID_HEADER)
    if is_safe_request_id(request_id):
        return request_id
    return uuid4().hex


async def request_id_middleware(request: Request, call_next) -> Response:
    request_id = select_request_id(request)
    request.state.request_id = request_id
    started_at = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
    finally:
        log_event(
            "info",
            "api_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            path_template=_path_template(request),
            status_code=status_code,
            duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
            actor_role=getattr(request.state, "actor_role", None),
            actor_user_id=getattr(request.state, "actor_user_id", None),
        )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    message = str(exc.detail) if isinstance(exc.detail, str) else "request failed"
    return error_response(
        request=request,
        status_code=exc.status_code,
        code=f"http_{exc.status_code}",
        message=message,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request_id_from_state(request)
    log_event(
        "error",
        "unhandled_exception",
        request_id=request_id,
        error_type=exc.__class__.__name__,
    )
    return error_response(
        request=request,
        status_code=500,
        code="internal_server_error",
        message="internal server error",
    )


def error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    request_id = request_id_from_state(request)
    body = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={REQUEST_ID_HEADER: request_id},
    )


def request_id_from_state(request: Request) -> str:
    value = getattr(request.state, "request_id", None)
    if is_safe_request_id(value):
        return value
    return uuid4().hex


def log_event(level: str, event: str, **fields: object) -> None:
    normalized_level = level.lower()
    payload = {
        "event": event,
        "level": normalized_level,
        "timestamp": datetime.now(UTC).isoformat(),
        **{key: _sanitize_value(key, value) for key, value in fields.items()},
    }
    LOGGER.log(
        LOG_LEVELS.get(normalized_level, logging.INFO),
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
    )


def _path_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if isinstance(path, str) and path:
        return path
    return request.url.path


def _sanitize_value(key: str, value: object) -> object:
    normalized_key = key.lower()
    if any(marker in normalized_key for marker in SENSITIVE_FIELD_MARKERS):
        return "[redacted]"
    if isinstance(value, str):
        return _sanitize_string(value)
    if isinstance(value, dict):
        return {str(item_key): _sanitize_value(str(item_key), item_value) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(key, item) for item in value]
    return value


def _sanitize_string(value: str) -> str:
    sanitized = BEARER_TOKEN.sub("Bearer [redacted]", value)
    sanitized = INLINE_SECRET.sub(lambda match: f"{match.group(1)}=[redacted]", sanitized)
    sanitized = WINDOWS_ABSOLUTE_PATH.sub("[redacted]", sanitized)
    sanitized = POSIX_LOCAL_PATH.sub("[redacted]", sanitized)
    return sanitized
