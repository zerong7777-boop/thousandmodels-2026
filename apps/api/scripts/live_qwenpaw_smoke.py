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
MAX_SESSION_ID_CHARS = 96
MAX_AGENT_ID_CHARS = 96
MAX_RESPONSE_BYTES = 65536
CONNECT_TIMEOUT_SECONDS = 3.0
READ_TIMEOUT_SECONDS = 20.0
ADVISORY_CONTRACT_VERSION = "v1.7"
REQUIRED_ADVISORY_FIELDS = (
    "recovery_rationale",
    "visitor_safe_notice_draft",
    "safety_notes",
)
MAX_ADVISORY_EXCERPT_CHARS = 360
AUTHORITY_CLAIM_PATTERNS = [
    re.compile(
        r"\bI\s+(approved|published|applied|mutated|created|redeemed|claimed|changed|updated)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(already|successfully)\s+(approved|published|applied|mutated|created|redeemed|claimed|changed|updated)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(published the notice|approved the plan|applied the suggestion|mutated the state|updated merchant runtime|changed inventory)\b",
        re.IGNORECASE,
    ),
]

SECRET_PATTERNS = [
    re.compile(r"Bearer\s+sk-[A-Za-z0-9._-]{20,}", re.IGNORECASE),
    re.compile(r"Bearer\s+[^\s]+", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9._-]{20,}"),
    re.compile(r"DASHSCOPE_API_KEY\s*=\s*[^\s]+", re.IGNORECASE),
    re.compile(r"QWENPAW_AUTH_PASSWORD\s*=\s*[^\s]+", re.IGNORECASE),
    re.compile(r"Authorization\s*:\s*[^\s]+", re.IGNORECASE),
    re.compile(r"\b(?:DASHSCOPE_API_KEY|QWENPAW_AUTH_PASSWORD|Authorization)\b", re.IGNORECASE),
]
LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Z]:[\\/][^\r\n,;`|\"']+", re.IGNORECASE),
    re.compile(r"\\\\[^\s\\]+\\[^\r\n,;`|]+", re.IGNORECASE),
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


def sanitize_session_id(value: str | None) -> str:
    if not value:
        return DEFAULT_SESSION_ID
    sanitized = bound_preview(value, max_chars=MAX_SESSION_ID_CHARS)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized or DEFAULT_SESSION_ID


def sanitize_agent_id(value: str | None) -> str | None:
    if not value:
        return None
    sanitized = bound_preview(value, max_chars=MAX_AGENT_ID_CHARS)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized or None


def read_bounded_response_text(
    response: httpx.Response,
    max_bytes: int = MAX_RESPONSE_BYTES,
) -> str:
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_bytes():
        if not chunk:
            continue
        remaining = max_bytes - total
        if remaining <= 0:
            break
        chunks.append(chunk[:remaining])
        total += min(len(chunk), remaining)
        if len(chunk) >= remaining:
            break
    return b"".join(chunks).decode("utf-8", errors="replace")


def _extract_json_text(payload: Any) -> str:
    if payload is None:
        return ""
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
        chunk = _extract_json_text(payload)
        if chunk:
            chunks.append(chunk)
    if len(chunks) > 3:
        return "".join(chunks)
    return "\n".join(chunks)


def _iter_sse_payloads(text: str) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def classify_qwenpaw_failure(
    *,
    content_type: str,
    text: str,
) -> tuple[str, str, str] | None:
    lowered = content_type.lower()
    payloads: list[dict[str, Any]] = []
    if "text/event-stream" in lowered:
        payloads = _iter_sse_payloads(text)
    elif "json" in lowered:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            payloads = [payload]
    for payload in payloads:
        error = payload.get("error")
        error_code = ""
        error_message = ""
        if isinstance(error, dict):
            error_code = str(error.get("code") or "")
            error_message = str(error.get("message") or "")
        elif error:
            error_message = str(error)
        status = str(payload.get("status") or "").lower()
        payload_type = str(payload.get("type") or "").lower()
        is_failed_payload = status == "failed"
        is_error_payload = payload_type == "error"
        is_provider_error = error_code.upper() == "PROVIDER_ERROR"
        is_missing_model = "no active model configured" in error_message.lower()
        if not (is_failed_payload or is_error_payload or is_provider_error or is_missing_model):
            continue
        preview = bound_preview(error_message or json.dumps(payload, ensure_ascii=False))
        if is_missing_model:
            return ("QwenPaw model is not configured", "provider_error", preview)
        if is_provider_error:
            return ("QwenPaw returned provider error", "provider_error", preview)
        if is_error_payload or is_failed_payload:
            return ("QwenPaw returned error", "qwenpaw_error", preview)
        return ("QwenPaw returned provider error", "provider_error", preview)
    return None


def parse_response_preview(
    content_type: str,
    text: str,
    max_chars: int = MAX_PREVIEW_CHARS,
) -> str:
    return bound_preview(
        extract_response_text(content_type=content_type, text=text),
        max_chars=max_chars,
    )


def extract_response_text(content_type: str, text: str) -> str:
    lowered = content_type.lower()
    if "text/event-stream" in lowered:
        return _extract_sse_text(text) or text
    if "json" in lowered:
        try:
            return _extract_json_text(json.loads(text))
        except json.JSONDecodeError:
            return text
    return text


def _parse_advisory_json(text: str) -> dict[str, str]:
    candidates = [text.strip()]
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        fields = {
            field: _extract_json_text(payload.get(field)).strip()
            for field in REQUIRED_ADVISORY_FIELDS
            if field in payload
        }
        if fields:
            return fields
    return {}


def _parse_advisory_markdown(text: str) -> tuple[dict[str, str], bool]:
    fields: dict[str, str] = {}
    pattern = re.compile(
        r"(?im)^\s{0,3}#{1,6}\s*(recovery_rationale|visitor_safe_notice_draft|safety_notes)\s*$"
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return fields, False
    preamble_stripped = matches[0].start() > 0 and bool(text[: matches[0].start()].strip())
    for index, match in enumerate(matches):
        field = match.group(1).lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = text[start:end].strip()
        if value:
            fields[field] = value
    return fields, preamble_stripped


def _contains_unsafe_authority_claim(text: str) -> bool:
    scrubbed = text.lower()
    safe_negations = (
        "do not approve",
        "do not publish",
        "do not mutate",
        "do not apply",
        "do not update",
        "do not change",
        "no state was changed",
        "no system state mutated",
        "no system state was mutated",
        "no plan, notice, merchant runtime, coupon, or redemption state has changed",
    )
    for phrase in safe_negations:
        scrubbed = scrubbed.replace(phrase, "")
    return any(pattern.search(scrubbed) for pattern in AUTHORITY_CLAIM_PATTERNS)


def qualify_advisory_text(text: str) -> dict[str, Any]:
    json_fields = _parse_advisory_json(text)
    markdown_fields, preamble_stripped = _parse_advisory_markdown(text)
    fields = {**markdown_fields, **json_fields}
    sanitized_fields = {
        field: bound_preview(fields.get(field, ""), max_chars=MAX_ADVISORY_EXCERPT_CHARS)
        for field in REQUIRED_ADVISORY_FIELDS
        if fields.get(field, "").strip()
    }
    fields_present = {
        field: bool(sanitized_fields.get(field))
        for field in REQUIRED_ADVISORY_FIELDS
    }
    missing = [field for field, present in fields_present.items() if not present]
    unsafe = _contains_unsafe_authority_claim("\n".join(sanitized_fields.values()))
    if missing:
        status = "unqualified"
        failure_kind = "missing_fields"
    elif unsafe:
        status = "unqualified"
        failure_kind = "unsafe_authority_claim"
    else:
        status = "qualified"
        failure_kind = None
    return {
        "advisory_contract_version": ADVISORY_CONTRACT_VERSION,
        "advisory_status": status,
        "qualification_failure_kind": failure_kind,
        "advisory_fields_present": fields_present,
        "sanitized_advisory_excerpt": sanitized_fields,
        "preamble_stripped": preamble_stripped,
    }


def render_smoke_doc(result: dict[str, Any]) -> str:
    response_preview = "\n".join(
        line.rstrip()
        for line in (result.get("sanitized_response_preview") or "").splitlines()
    )
    field_lines = [
        f"- {field}: `{present}`"
        for field, present in (result.get("advisory_fields_present") or {}).items()
    ]
    return "\n".join(
        [
            "# v1.5 Real QwenPaw Guarded Smoke",
            "",
            "## Result",
            "",
            f"- Outcome: `{result['outcome']}`",
            f"- Endpoint: `{result['endpoint']}`",
            f"- Host: `{result['base_url_host']}`",
            f"- Agent ID: `{result.get('agent_id') or 'active/default'}`",
            f"- Request sent: `{result['request_sent']}`",
            f"- HTTP status: `{result.get('response_status_code')}`",
            f"- Latency ms: `{result.get('latency_ms')}`",
            f"- Blocked reason: `{result.get('blocked_reason')}`",
            f"- Failure kind: `{result.get('failure_kind')}`",
            f"- Advisory contract: `{result.get('advisory_contract_version')}`",
            f"- Provider reachable: `{result.get('provider_reachable')}`",
            f"- Advisory status: `{result.get('advisory_status')}`",
            f"- Qualification failure kind: `{result.get('qualification_failure_kind')}`",
            "",
            "## Boundary",
            "",
            "- This smoke is manual and guarded by `RUN_LIVE_QWENPAW_SMOKE=1`.",
            "- It calls only a localhost QwenPaw service.",
            "- It does not approve plans, publish notices, mutate merchant runtime, or create coupon/redemption records.",
            "- `advisory_qualified` means the response passed the v1.7 required-field and authority-claim checks; it still does not prove production orchestration.",
            "- `advisory_unqualified` means the local provider responded, but the response did not pass adapter qualification.",
            "- The v1.4 fake adapter remains the accepted product path.",
            "- The v1.3 deterministic live demo remains the reliable demo path.",
            "",
            "## Sanitized Response Preview",
            "",
            "```text",
            response_preview,
            "```",
            "",
            "## Advisory Field Check",
            "",
            *field_lines,
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
    session_id = sanitize_session_id(env.get("QWENPAW_SMOKE_SESSION_ID"))
    agent_id = sanitize_agent_id(env.get("QWENPAW_AGENT_ID"))
    return {
        "outcome": "blocked",
        "base_url_host": parsed.hostname or "",
        "endpoint": ENDPOINT,
        "agent_id": agent_id,
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
        "advisory_contract_version": ADVISORY_CONTRACT_VERSION,
        "provider_reachable": False,
        "advisory_status": "not_applicable",
        "qualification_failure_kind": None,
        "advisory_fields_present": {
            field: False for field in REQUIRED_ADVISORY_FIELDS
        },
        "sanitized_advisory_excerpt": {},
        "preamble_stripped": False,
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

    session_id = sanitize_session_id(source.get("QWENPAW_SMOKE_SESSION_ID"))
    agent_id = sanitize_agent_id(source.get("QWENPAW_AGENT_ID"))
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
    headers = {"Content-Type": "application/json"}
    if agent_id:
        headers["X-Agent-Id"] = agent_id

    timeout = httpx.Timeout(
        timeout=READ_TIMEOUT_SECONDS,
        connect=CONNECT_TIMEOUT_SECONDS,
        read=READ_TIMEOUT_SECONDS,
    )
    started = time.perf_counter()
    result = base_result(env=source, base_url=base_url, request_sent=True)
    result["sanitized_prompt_preview"] = bound_preview(prompt, max_chars=500)
    try:
        with httpx.Client(timeout=timeout, transport=transport, trust_env=False) as client:
            with client.stream(
                "POST",
                f"{base_url}{ENDPOINT}",
                json=request_body,
                headers=headers,
            ) as response:
                response_status_code = response.status_code
                content_type = response.headers.get("content-type", "")
                response_text = read_bounded_response_text(response)
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

    failure = (
        classify_qwenpaw_failure(content_type=content_type, text=response_text)
        if response_status_code == 200
        else None
    )
    preview = parse_response_preview(content_type=content_type, text=response_text)
    result.update(
        {
            "response_status_code": response_status_code,
            "response_content_type": content_type,
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "sanitized_response_preview": preview,
            "response_preview_sha256": (
                hashlib.sha256(preview.encode("utf-8")).hexdigest() if preview else ""
            ),
        }
    )
    if failure:
        blocked_reason, failure_kind, failure_preview = failure
        result["outcome"] = "blocked"
        result["blocked_reason"] = blocked_reason
        result["failure_kind"] = failure_kind
        result["provider_reachable"] = False
        result["advisory_status"] = "not_applicable"
        result["sanitized_response_preview"] = failure_preview
        result["response_preview_sha256"] = (
            hashlib.sha256(failure_preview.encode("utf-8")).hexdigest()
            if failure_preview
            else ""
        )
    elif response_status_code == 200 and preview:
        qualification = qualify_advisory_text(
            extract_response_text(content_type=content_type, text=response_text)
        )
        result.update(qualification)
        result["provider_reachable"] = True
        result["outcome"] = (
            "advisory_qualified"
            if qualification["advisory_status"] == "qualified"
            else "advisory_unqualified"
        )
    elif response_status_code in {401, 403}:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw authentication is required"
        result["failure_kind"] = "auth_required"
    elif response_status_code in {404, 405}:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw agent process endpoint is unavailable"
        result["failure_kind"] = "endpoint_unavailable"
    else:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw returned no usable response"
        result["failure_kind"] = f"http_{response_status_code}"
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
    return 0 if result["outcome"] == "advisory_qualified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
