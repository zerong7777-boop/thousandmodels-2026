from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = PROJECT_ROOT / "docs" / "research" / "assets" / "v1.5-real-qwenpaw-guarded-smoke"
RESULT_JSON = ASSET_DIR / "live-qwenpaw-smoke-result.json"
SMOKE_DOC = PROJECT_ROOT / "docs" / "research" / "v1.5-real-qwenpaw-guarded-smoke.md"

DEFAULT_BASE_URL = "http://127.0.0.1:8088"
DEFAULT_SESSION_ID = "zhiyin-v15-qwenpaw-smoke"
ENDPOINT = "/api/agent/process"
ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1"}
MAX_PREVIEW_CHARS = 1200
CONNECT_TIMEOUT_SECONDS = 3.0
READ_TIMEOUT_SECONDS = 20.0

SECRET_PATTERNS = [
    re.compile(r"Bearer\s+sk-[A-Za-z0-9._-]{20,}", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9._-]{20,}"),
    re.compile(r"DASHSCOPE_API_KEY\s*=\s*[^\s]+", re.IGNORECASE),
    re.compile(r"QWENPAW_AUTH_PASSWORD\s*=\s*[^\s]+", re.IGNORECASE),
    re.compile(r"Authorization\s*:\s*[^\s]+", re.IGNORECASE),
]
LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Z]:[\\/][^\s]+", re.IGNORECASE),
    re.compile(r"\\\\[^\s\\]+\\[^\s]+", re.IGNORECASE),
]


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_sanitized_prompt(
    event_id: str = "demo-night-tour",
    merchant_id: str = "m001",
    incident_kind: str = "sold_out",
) -> str:
    return "\n".join(
        [
            "You are helping verify a local QwenPaw integration for a demo operations system.",
            f"Event: {event_id}",
            f"Incident: merchant {merchant_id} reported {incident_kind}.",
            "Boundary: advisory only. Do not claim that you approved, published, applied, or mutated any system state.",
            "Return a concise advisory response with recovery_rationale, visitor_safe_notice_draft, and safety_notes.",
        ]
    )


def normalize_base_url(raw: str | None) -> str:
    value = (raw or DEFAULT_BASE_URL).strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("QWENPAW_BASE_URL must use http or https")
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("QWENPAW_BASE_URL must point to localhost")
    return value


def redact_sensitive_text(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    for pattern in LOCAL_PATH_PATTERNS:
        redacted = pattern.sub("[REDACTED_LOCAL_PATH]", redacted)
    return redacted.replace("Bearer", "[REDACTED_SECRET]")


def bound_preview(value: str, max_chars: int = MAX_PREVIEW_CHARS) -> str:
    cleaned = redact_sensitive_text(value).replace("\r", "\n")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    if max_chars <= len("\n[TRUNCATED]"):
        return cleaned[:max_chars]
    return cleaned[: max_chars - len("\n[TRUNCATED]")].rstrip() + "\n[TRUNCATED]"


def _extract_json_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, list):
        return "\n".join(_extract_json_text(item) for item in payload)
    if not isinstance(payload, dict):
        return str(payload)
    for key in ("content", "text", "message", "response", "output", "data"):
        if key in payload:
            return _extract_json_text(payload[key])
    nested = [
        _extract_json_text(item)
        for item in payload.values()
        if isinstance(item, (dict, list))
    ]
    if nested:
        return "\n".join(item for item in nested if item)
    return json.dumps(payload, ensure_ascii=False)


def _extract_sse_text(text: str) -> str:
    chunks: list[str] = []
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            chunks.append(data)
            continue
        chunks.append(_extract_json_text(payload))
    return "\n".join(chunk for chunk in chunks if chunk)


def parse_response_preview(
    content_type: str,
    text: str,
    max_chars: int = MAX_PREVIEW_CHARS,
) -> str:
    lowered = content_type.lower()
    if "text/event-stream" in lowered:
        extracted = _extract_sse_text(text) or text
    elif "json" in lowered:
        try:
            extracted = _extract_json_text(json.loads(text))
        except json.JSONDecodeError:
            extracted = text
    else:
        extracted = text
    return bound_preview(extracted, max_chars=max_chars)


def render_smoke_doc(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# v1.5 Real QwenPaw Guarded Smoke",
            "",
            "## Result",
            "",
            f"- Outcome: `{result['outcome']}`",
            f"- Endpoint: `{result['endpoint']}`",
            f"- Host: `{result['base_url_host']}`",
            f"- Request sent: `{result['request_sent']}`",
            f"- HTTP status: `{result.get('response_status_code')}`",
            f"- Latency ms: `{result.get('latency_ms')}`",
            f"- Blocked reason: `{result.get('blocked_reason')}`",
            f"- Failure kind: `{result.get('failure_kind')}`",
            "",
            "## Boundary",
            "",
            "- This smoke is manual and guarded by `RUN_LIVE_QWENPAW_SMOKE=1`.",
            "- It calls only a localhost QwenPaw service.",
            "- It does not approve plans, publish notices, mutate merchant runtime, or create coupon/redemption records.",
            "- The v1.4 fake adapter remains the accepted product path.",
            "- The v1.3 deterministic live demo remains the reliable demo path.",
            "",
            "## Sanitized Response Preview",
            "",
            "```text",
            result.get("sanitized_response_preview") or "",
            "```",
            "",
            "## Evidence",
            "",
            "- JSON artifact: `docs/research/assets/v1.5-real-qwenpaw-guarded-smoke/live-qwenpaw-smoke-result.json`",
            "- The artifact stores bounded sanitized previews only, not raw streams or secrets.",
            "",
        ]
    )


def write_evidence(result: dict[str, Any]) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    SMOKE_DOC.parent.mkdir(parents=True, exist_ok=True)
    RESULT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SMOKE_DOC.write_text(render_smoke_doc(result), encoding="utf-8")


def base_result(*, env: dict[str, str], base_url: str | None, request_sent: bool) -> dict[str, Any]:
    parsed = urlparse(base_url or DEFAULT_BASE_URL)
    session_id = env.get("QWENPAW_SMOKE_SESSION_ID") or DEFAULT_SESSION_ID
    return {
        "outcome": "blocked",
        "base_url_host": parsed.hostname or "",
        "endpoint": ENDPOINT,
        "session_id": session_id,
        "request_sent": request_sent,
        "response_status_code": None,
        "response_content_type": None,
        "latency_ms": None,
        "sanitized_prompt_preview": bound_preview(build_sanitized_prompt(), max_chars=500),
        "sanitized_response_preview": "",
        "response_preview_sha256": "",
        "blocked_reason": None,
        "failure_kind": None,
        "evidence_generated_at": utc_now_iso(),
    }


def blocked_result(
    *,
    env: dict[str, str],
    base_url: str | None,
    reason: str,
    failure_kind: str | None = None,
) -> dict[str, Any]:
    result = base_result(env=env, base_url=base_url, request_sent=False)
    result["blocked_reason"] = reason
    result["failure_kind"] = failure_kind
    write_evidence(result)
    return result


def run_smoke(
    env: dict[str, str] | None = None,
    transport: httpx.BaseTransport | None = None,
) -> dict[str, Any]:
    source = dict(os.environ if env is None else env)
    raw_base_url = source.get("QWENPAW_BASE_URL") or DEFAULT_BASE_URL
    if source.get("RUN_LIVE_QWENPAW_SMOKE") != "1":
        return blocked_result(
            env=source,
            base_url=raw_base_url,
            reason="RUN_LIVE_QWENPAW_SMOKE is required",
            failure_kind="missing_live_flag",
        )

    try:
        base_url = normalize_base_url(raw_base_url)
    except ValueError as exc:
        return blocked_result(
            env=source,
            base_url=raw_base_url,
            reason=str(exc),
            failure_kind="invalid_base_url",
        )

    session_id = source.get("QWENPAW_SMOKE_SESSION_ID") or DEFAULT_SESSION_ID
    prompt = build_sanitized_prompt()
    request_body = {
        "input": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
        "session_id": session_id,
    }

    timeout = httpx.Timeout(
        timeout=READ_TIMEOUT_SECONDS,
        connect=CONNECT_TIMEOUT_SECONDS,
        read=READ_TIMEOUT_SECONDS,
    )
    started = time.perf_counter()
    result = base_result(env=source, base_url=base_url, request_sent=True)
    result["sanitized_prompt_preview"] = bound_preview(prompt, max_chars=500)
    try:
        with httpx.Client(timeout=timeout, transport=transport) as client:
            response = client.post(
                f"{base_url}{ENDPOINT}",
                json=request_body,
                headers={"Content-Type": "application/json"},
            )
    except httpx.ConnectError:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw service is not reachable"
        result["failure_kind"] = "connect_error"
        result["latency_ms"] = int((time.perf_counter() - started) * 1000)
        write_evidence(result)
        return result
    except httpx.TimeoutException:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw service timed out"
        result["failure_kind"] = "timeout"
        result["latency_ms"] = int((time.perf_counter() - started) * 1000)
        write_evidence(result)
        return result
    except httpx.HTTPError as exc:
        result["outcome"] = "failed"
        result["failure_kind"] = exc.__class__.__name__
        result["sanitized_response_preview"] = bound_preview(str(exc))
        result["latency_ms"] = int((time.perf_counter() - started) * 1000)
        write_evidence(result)
        return result

    content_type = response.headers.get("content-type", "")
    preview = parse_response_preview(content_type=content_type, text=response.text)
    result.update(
        {
            "response_status_code": response.status_code,
            "response_content_type": content_type,
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "sanitized_response_preview": preview,
            "response_preview_sha256": (
                hashlib.sha256(preview.encode("utf-8")).hexdigest() if preview else ""
            ),
        }
    )
    if response.status_code == 200 and preview:
        result["outcome"] = "live_success"
    elif response.status_code in {401, 403}:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw authentication is required"
        result["failure_kind"] = "auth_required"
    elif response.status_code in {404, 405}:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw agent process endpoint is unavailable"
        result["failure_kind"] = "endpoint_unavailable"
    else:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw returned no usable response"
        result["failure_kind"] = f"http_{response.status_code}"
    write_evidence(result)
    return result


def main() -> int:
    result = run_smoke()
    print(
        json.dumps(
            {
                "outcome": result["outcome"],
                "path": str(RESULT_JSON.relative_to(PROJECT_ROOT)),
            },
            indent=2,
        )
    )
    return 0 if result["outcome"] == "live_success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
