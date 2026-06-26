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
ASSET_DIR = PROJECT_ROOT / "docs" / "research" / "assets" / "v1.8-qwenpaw-advisory-optimization"
RESULT_JSON = ASSET_DIR / "live-qwenpaw-advisory-optimization-result.json"
SMOKE_DOC = PROJECT_ROOT / "docs" / "research" / "v1.8-qwenpaw-advisory-optimization.md"

DEFAULT_BASE_URL = "http://127.0.0.1:8088"
DEFAULT_SESSION_ID = "zhiyin-v15-qwenpaw-smoke"
ENDPOINT = "/api/agent/process"
ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1"}
MAX_PREVIEW_CHARS = 1200
MAX_SESSION_ID_CHARS = 96
MAX_AGENT_ID_CHARS = 96
MAX_RESPONSE_BYTES = 65536
MAX_REPAIR_PREVIOUS_RESPONSE_CHARS = 900
CONNECT_TIMEOUT_SECONDS = 3.0
READ_TIMEOUT_SECONDS = 20.0
ADVISORY_CONTRACT_VERSION = "v1.8"
DEFAULT_PROMPT_VARIANT = "prompt_a_json_only"
DEFAULT_VALIDATOR_VARIANT = "json_no_preamble_validator"
DEFAULT_AGENT_VARIANT = "agent_qa_current"
MAX_REPAIR_ATTEMPTS = 2
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
        r"\bI(?:\s+have|'ve)\s+"
        r"(approved|published|applied|mutated|created|redeemed|claimed|changed|updated)\b",
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
    re.compile(
        r"\b(?:the\s+)?"
        r"(?:notice|plan|suggestion|state|merchant runtime|inventory|coupon|redemption|coupon record|redemption record)\s+"
        r"(?:was|were|has been|have been)\s+"
        r"(?:approved|published|applied|mutated|created|redeemed|claimed|changed|updated)\b",
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


def _case_lines(
    event_id: str,
    merchant_id: str,
    incident_kind: str,
) -> list[str]:
    return [
        f"Event: {event_id}",
        f"Incident: merchant {merchant_id} reported {incident_kind}.",
        "Boundary: advisory only. Do not claim that you approved, published, applied, updated, created, redeemed, or mutated any system state.",
    ]


def _json_contract_lines() -> list[str]:
    return [
        "Return exactly one JSON object and nothing else.",
        "No Markdown. No preamble. No tool inspection. Do not inspect tools, files, workspace, memory, or external context.",
        "Do not describe your reasoning, prompt, schema, agent state, or internal process.",
        "The JSON object must contain exactly these required string fields:",
        '"recovery_rationale"',
        '"visitor_safe_notice_draft"',
        '"safety_notes"',
    ]


def build_sanitized_prompt(
    event_id: str = "demo-night-tour",
    merchant_id: str = "m001",
    incident_kind: str = "sold_out",
    prompt_variant: str = DEFAULT_PROMPT_VARIANT,
) -> str:
    if prompt_variant == "prompt_a_json_only":
        return "\n".join(
            [
                "You are the final advisory formatter for a demo operations system.",
                *_case_lines(event_id, merchant_id, incident_kind),
                *_json_contract_lines(),
                "Use concise visitor-safe wording. State that organizer approval is required before any authoritative action.",
            ]
        )
    if prompt_variant == "prompt_b_markdown_sections":
        return "\n".join(
            [
                "You are the final advisory formatter for a demo operations system.",
                *_case_lines(event_id, merchant_id, incident_kind),
                "Return only these three Markdown sections, with exact headings:",
                "### recovery_rationale",
                "### visitor_safe_notice_draft",
                "### safety_notes",
                "Do not inspect tools, files, workspace, memory, or external context.",
                "Do not describe your reasoning, prompt, schema, agent state, or internal process.",
            ]
        )
    if prompt_variant == "prompt_c_few_shot_json":
        return "\n".join(
            [
                "You are the final advisory formatter for a demo operations system.",
                *_case_lines(event_id, merchant_id, incident_kind),
                *_json_contract_lines(),
                "VALID EXAMPLE:",
                '{"recovery_rationale":"Merchant m001 is sold out, so visitor flow should be reduced until organizer review.","visitor_safe_notice_draft":"Some items at this stop may be unavailable. Please follow on-site guidance.","safety_notes":"Advisory only. Organizer approval is required before publication or runtime changes."}',
                "INVALID EXAMPLE:",
                "I will inspect the workspace before answering.",
                "This is invalid because it has no JSON object.",
                "INVALID EXAMPLE:",
                '{"recovery_rationale":"m001 is sold out","visitor_safe_notice_draft":"Some items may be unavailable."}',
                "This is invalid because it is missing safety_notes.",
            ]
        )
    raise ValueError(f"Unknown QWENPAW_PROMPT_VARIANT: {prompt_variant}")


def sanitize_max_repair_attempts(value: str | None) -> int:
    try:
        attempts = int((value or "").strip())
    except ValueError:
        return 0
    return max(0, min(attempts, MAX_REPAIR_ATTEMPTS))


def build_repair_prompt(
    original_text: str,
    qualification: dict[str, Any],
    prompt_variant: str,
) -> str:
    missing_fields = [
        field
        for field in REQUIRED_ADVISORY_FIELDS
        if not (qualification.get("advisory_fields_present") or {}).get(field)
    ]
    validation_errors = {
        "qualification_failure_kind": qualification.get("qualification_failure_kind"),
        "missing_fields": missing_fields,
        "unexpected_fields": qualification.get("unexpected_fields") or [],
        "advisory_fields_present": qualification.get("advisory_fields_present") or {},
        "parsed_output_format": qualification.get("parsed_output_format"),
        "json_no_preamble_pass": qualification.get("json_no_preamble_pass"),
    }
    return "\n".join(
        [
            "Repair the previous QwenPaw advisory response so it passes the v1.8 advisory contract.",
            "Return only the corrected advisory response for the same incident.",
            "Exact validation errors:",
            json.dumps(validation_errors, ensure_ascii=False, sort_keys=True),
            "Required fields:",
            *REQUIRED_ADVISORY_FIELDS,
            "Previous response excerpt:",
            bound_preview(original_text, max_chars=MAX_REPAIR_PREVIOUS_RESPONSE_CHARS),
            "Boundary: advisory only. Do not claim that you approved, published, applied, updated, created, redeemed, or mutated any system state.",
            "Use the same output style requested by this prompt variant:",
            prompt_variant,
            *_json_contract_lines(),
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


def select_prompt_variant(env: dict[str, str]) -> str:
    return (env.get("QWENPAW_PROMPT_VARIANT") or DEFAULT_PROMPT_VARIANT).strip()


def select_validator_variant(env: dict[str, str], prompt_variant: str) -> str:
    raw = (env.get("QWENPAW_VALIDATOR_VARIANT") or "").strip()
    if raw:
        return raw
    if prompt_variant == "prompt_b_markdown_sections":
        return "strict_existing_validator"
    return DEFAULT_VALIDATOR_VARIANT


def select_agent_variant(env: dict[str, str]) -> str:
    return (env.get("QWENPAW_AGENT_VARIANT") or DEFAULT_AGENT_VARIANT).strip()


def resolve_agent_id_for_variant(env: dict[str, str], agent_variant: str) -> str | None:
    if agent_variant == "agent_default":
        return None
    if agent_variant in {"agent_qa_current", "agent_formatter_candidate"}:
        return sanitize_agent_id(env.get("QWENPAW_AGENT_ID"))
    return sanitize_agent_id(env.get("QWENPAW_AGENT_ID"))


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


def call_qwenpaw(
    client: httpx.Client,
    *,
    base_url: str,
    request_body: dict[str, Any],
    headers: dict[str, str],
) -> tuple[int, str, str, int]:
    started = time.perf_counter()
    with client.stream(
        "POST",
        f"{base_url}{ENDPOINT}",
        json=request_body,
        headers=headers,
    ) as response:
        response_status_code = response.status_code
        content_type = response.headers.get("content-type", "")
        response_text = read_bounded_response_text(response)
    latency_ms = int((time.perf_counter() - started) * 1000)
    return response_status_code, content_type, response_text, latency_ms


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


def _extract_typed_content_text(payload: Any) -> str:
    if isinstance(payload, list):
        return "\n".join(
            item for item in (_extract_typed_content_text(item) for item in payload) if item
        )
    if not isinstance(payload, dict):
        return ""
    if (
        str(payload.get("object") or "").lower() == "message"
        and str(payload.get("type") or "").lower() == "reasoning"
    ):
        return ""

    chunks: list[str] = []
    content = payload.get("content")
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") not in {"text", "output_text"}:
                continue
            text = _extract_json_text(block.get("text"))
            if text:
                chunks.append(text)
    elif isinstance(content, str) and payload.get("type") in {"text", "output_text"}:
        chunks.append(content)

    for key in ("output", "message", "response", "data"):
        nested = payload.get(key)
        nested_text = _extract_typed_content_text(nested)
        if nested_text:
            chunks.append(nested_text)

    return "\n".join(chunks)


def _is_completed_qwenpaw_payload(payload: dict[str, Any]) -> bool:
    status = str(payload.get("status") or "").lower()
    obj = str(payload.get("object") or "").lower()
    return status in {"completed", "succeeded"} and obj in {"message", "response", ""}


def _extract_qwenpaw_message_delta_text(payloads: list[dict[str, Any]]) -> str:
    message_types: dict[str, str] = {}
    message_buffers: dict[str, list[str]] = {}

    for payload in payloads:
        obj = str(payload.get("object") or "").lower()
        if obj == "message":
            message_id = str(payload.get("id") or "")
            message_type = str(payload.get("type") or "").lower()
            if message_id and message_type:
                message_types[message_id] = message_type
            continue

        if obj != "content":
            continue
        if str(payload.get("type") or "").lower() not in {"text", "output_text"}:
            continue
        if payload.get("delta") is False:
            continue
        msg_id = str(payload.get("msg_id") or "")
        if not msg_id:
            continue
        text = _extract_json_text(payload.get("text"))
        if not text:
            continue
        message_buffers.setdefault(msg_id, []).append(text)

    message_chunks = [
        "".join(chunks)
        for msg_id, chunks in message_buffers.items()
        if message_types.get(msg_id) == "message"
    ]
    return "\n".join(chunk for chunk in message_chunks if chunk)


def _extract_sse_text(text: str) -> str:
    chunks: list[str] = []
    typed_chunks: list[str] = []
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
            chunks.append(data)
            continue
        if isinstance(payload, dict):
            payloads.append(payload)
        if isinstance(payload, dict) and _is_completed_qwenpaw_payload(payload):
            typed_text = _extract_typed_content_text(payload)
            if typed_text and typed_text not in typed_chunks:
                typed_chunks.append(typed_text)
            continue
        chunk = _extract_json_text(payload)
        if chunk:
            chunks.append(chunk)
    message_delta_text = _extract_qwenpaw_message_delta_text(payloads)
    if message_delta_text:
        return message_delta_text
    if typed_chunks:
        return "\n".join(typed_chunks)
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


def _parse_exact_advisory_json(text: str) -> tuple[dict[str, str], bool, list[str]]:
    stripped = text.strip()
    if not stripped.startswith("{") or not stripped.endswith("}"):
        return {}, False, []
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return {}, False, []
    if not isinstance(payload, dict):
        return {}, False, []
    unexpected_fields = sorted(set(payload) - set(REQUIRED_ADVISORY_FIELDS))
    fields = {
        field: _extract_json_text(payload.get(field)).strip()
        for field in REQUIRED_ADVISORY_FIELDS
        if field in payload
    }
    return fields, True, unexpected_fields


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
        "i have not approved",
        "i have not published",
        "i have not applied",
        "i have not mutated",
        "i have not created",
        "i have not redeemed",
        "i have not claimed",
        "i have not changed",
        "i have not updated",
        "i did not approve",
        "i did not publish",
        "i did not apply",
        "i did not mutate",
        "i did not create",
        "i did not redeem",
        "i did not claim",
        "i did not change",
        "i did not update",
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


def qualify_advisory_text(
    text: str,
    validator_variant: str = DEFAULT_VALIDATOR_VARIANT,
) -> dict[str, Any]:
    parsed_output_format: str | None = None
    json_no_preamble_pass: bool | None = None
    preamble_stripped = False
    unexpected_fields: list[str] = []

    if validator_variant == "json_no_preamble_validator":
        json_fields, exact_json, unexpected_fields = _parse_exact_advisory_json(text)
        json_no_preamble_pass = exact_json
        fields = json_fields
        parsed_output_format = "json" if json_fields else None
    elif validator_variant == "strict_existing_validator":
        json_fields = _parse_advisory_json(text)
        markdown_fields, preamble_stripped = _parse_advisory_markdown(text)
        fields = {**markdown_fields, **json_fields}
        if json_fields:
            parsed_output_format = "json"
        elif markdown_fields:
            parsed_output_format = "markdown"
    else:
        return {
            "advisory_contract_version": ADVISORY_CONTRACT_VERSION,
            "advisory_status": "unqualified",
            "qualification_failure_kind": "invalid_validator_variant",
            "advisory_fields_present": {
                field: False for field in REQUIRED_ADVISORY_FIELDS
            },
            "sanitized_advisory_excerpt": {},
            "preamble_stripped": False,
            "parsed_output_format": None,
            "json_no_preamble_pass": None,
            "unexpected_fields": [],
        }
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
    unsafe = _contains_unsafe_authority_claim(text)
    if validator_variant == "json_no_preamble_validator" and json_no_preamble_pass is False:
        status = "unqualified"
        failure_kind = "json_preamble_detected"
    elif validator_variant == "json_no_preamble_validator" and unexpected_fields:
        status = "unqualified"
        failure_kind = "unexpected_fields"
    elif missing:
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
        "parsed_output_format": parsed_output_format,
        "json_no_preamble_pass": json_no_preamble_pass,
        "unexpected_fields": unexpected_fields,
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
    repair_history = result.get("repair_history") or []
    if repair_history:
        repair_lines = [
            (
                f"- Attempt `{entry.get('attempt')}`: "
                f"response_status_code=`{entry.get('response_status_code')}`, "
                f"advisory_status=`{entry.get('advisory_status')}`, "
                f"qualification_failure_kind=`{entry.get('qualification_failure_kind') or entry.get('failure_kind')}`"
            )
            for entry in repair_history
        ]
    else:
        repair_lines = ["- No repair attempts were used."]
    return "\n".join(
        [
            "# v1.8 QwenPaw Advisory Optimization Smoke",
            "",
            "## Result",
            "",
            f"- Outcome: `{result['outcome']}`",
            f"- Endpoint: `{result['endpoint']}`",
            f"- Host: `{result['base_url_host']}`",
            f"- Agent ID: `{result.get('agent_id') or 'active/default'}`",
            f"- Prompt variant: `{result.get('prompt_variant')}`",
            f"- Validator variant: `{result.get('validator_variant')}`",
            f"- Agent variant: `{result.get('agent_variant')}`",
            f"- Repair attempts: `{result.get('repair_attempt_count')}`",
            f"- Parsed output format: `{result.get('parsed_output_format')}`",
            f"- JSON no-preamble pass: `{result.get('json_no_preamble_pass')}`",
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
            "- It tests prompt, agent, validator, and bounded repair variants for advisory qualification.",
            "- It does not approve plans, publish notices, mutate merchant runtime, or create coupon/redemption records.",
            "- `advisory_qualified` means the response passed the v1.8 required-field, validator, and authority-claim checks; it still does not prove production orchestration.",
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
            "## Repair History",
            "",
            *repair_lines,
            "",
            "## Evidence",
            "",
            "- JSON artifact: `docs/research/assets/v1.8-qwenpaw-advisory-optimization/live-qwenpaw-advisory-optimization-result.json`",
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
    prompt_variant = select_prompt_variant(env)
    agent_variant = select_agent_variant(env)
    agent_id = resolve_agent_id_for_variant(env, agent_variant)
    validator_variant = select_validator_variant(env, prompt_variant)
    try:
        prompt_preview = bound_preview(
            build_sanitized_prompt(prompt_variant=prompt_variant),
            max_chars=500,
        )
    except ValueError:
        prompt_preview = ""
    return {
        "outcome": "blocked",
        "base_url_host": parsed.hostname or "",
        "endpoint": ENDPOINT,
        "agent_id": agent_id,
        "prompt_variant": prompt_variant,
        "validator_variant": validator_variant,
        "agent_variant": agent_variant,
        "repair_attempt_count": 0,
        "repair_history": [],
        "parsed_output_format": None,
        "json_no_preamble_pass": None,
        "unexpected_fields": [],
        "session_id": session_id,
        "request_sent": request_sent,
        "response_status_code": None,
        "response_content_type": None,
        "latency_ms": None,
        "sanitized_prompt_preview": prompt_preview,
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


def reset_advisory_qualification_for_blocked_failure(result: dict[str, Any]) -> None:
    result.update(
        {
            "provider_reachable": False,
            "advisory_status": "not_applicable",
            "qualification_failure_kind": None,
            "advisory_fields_present": {
                field: False for field in REQUIRED_ADVISORY_FIELDS
            },
            "sanitized_advisory_excerpt": {},
            "preamble_stripped": False,
            "parsed_output_format": None,
            "json_no_preamble_pass": None,
            "unexpected_fields": [],
        }
    )


def append_repair_history_entry(
    result: dict[str, Any],
    *,
    attempt: int,
    response_status_code: int | None = None,
    failure_kind: str | None = None,
) -> None:
    result["repair_history"].append(
        {
            "attempt": attempt,
            "response_status_code": response_status_code,
            "failure_kind": failure_kind,
            "advisory_status": result["advisory_status"],
            "qualification_failure_kind": result["qualification_failure_kind"],
            "advisory_fields_present": dict(result["advisory_fields_present"]),
            "unexpected_fields": list(result.get("unexpected_fields") or []),
        }
    )


def append_pending_repair_failure_history(
    result: dict[str, Any],
    *,
    failure_kind: str,
) -> None:
    attempt = result.get("repair_attempt_count") or 0
    if attempt and len(result["repair_history"]) < attempt:
        append_repair_history_entry(
            result,
            attempt=attempt,
            failure_kind=failure_kind,
        )


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

    prompt_variant = select_prompt_variant(source)
    try:
        prompt = build_sanitized_prompt(prompt_variant=prompt_variant)
    except ValueError as exc:
        result = base_result(env=source, base_url=base_url, request_sent=False)
        result["prompt_variant"] = prompt_variant
        result["blocked_reason"] = str(exc)
        result["failure_kind"] = "invalid_prompt_variant"
        write_evidence(result)
        return result

    session_id = sanitize_session_id(source.get("QWENPAW_SMOKE_SESSION_ID"))
    agent_variant = select_agent_variant(source)
    agent_id = resolve_agent_id_for_variant(source, agent_variant)
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
    result = base_result(env=source, base_url=base_url, request_sent=True)
    result["sanitized_prompt_preview"] = bound_preview(prompt, max_chars=500)
    max_repair_attempts = sanitize_max_repair_attempts(
        source.get("QWENPAW_MAX_REPAIR_ATTEMPTS")
    )

    def apply_qwenpaw_response(
        *,
        response_status_code: int,
        content_type: str,
        response_text: str,
        latency_ms: int,
    ) -> tuple[dict[str, Any] | None, str]:
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
                "latency_ms": latency_ms,
                "sanitized_response_preview": preview,
                "response_preview_sha256": (
                    hashlib.sha256(preview.encode("utf-8")).hexdigest()
                    if preview
                    else ""
                ),
            }
        )
        if failure:
            blocked_reason, failure_kind, failure_preview = failure
            result["outcome"] = "blocked"
            result["blocked_reason"] = blocked_reason
            result["failure_kind"] = failure_kind
            reset_advisory_qualification_for_blocked_failure(result)
            result["sanitized_response_preview"] = failure_preview
            result["response_preview_sha256"] = (
                hashlib.sha256(failure_preview.encode("utf-8")).hexdigest()
                if failure_preview
                else ""
            )
            return None, ""
        if response_status_code == 200 and preview:
            advisory_text = extract_response_text(
                content_type=content_type,
                text=response_text,
            )
            qualification = qualify_advisory_text(
                advisory_text,
                validator_variant=result["validator_variant"],
            )
            result.update(qualification)
            result["provider_reachable"] = True
            result["outcome"] = (
                "advisory_qualified"
                if qualification["advisory_status"] == "qualified"
                else "advisory_unqualified"
            )
            return qualification, advisory_text
        if response_status_code in {401, 403}:
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
        reset_advisory_qualification_for_blocked_failure(result)
        return None, ""

    try:
        with httpx.Client(timeout=timeout, transport=transport, trust_env=False) as client:
            response_status_code, content_type, response_text, latency_ms = call_qwenpaw(
                client,
                base_url=base_url,
                request_body=request_body,
                headers=headers,
            )
            qualification, advisory_text = apply_qwenpaw_response(
                response_status_code=response_status_code,
                content_type=content_type,
                response_text=response_text,
                latency_ms=latency_ms,
            )
            repair_attempt = 0
            while (
                result["outcome"] == "advisory_unqualified"
                and qualification is not None
                and result["qualification_failure_kind"] != "invalid_validator_variant"
                and repair_attempt < max_repair_attempts
            ):
                repair_attempt += 1
                result["repair_attempt_count"] = repair_attempt
                repair_prompt = build_repair_prompt(
                    advisory_text,
                    qualification,
                    prompt_variant,
                )
                repair_body = {
                    "input": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": repair_prompt}],
                        }
                    ],
                    "session_id": session_id,
                }
                (
                    response_status_code,
                    content_type,
                    response_text,
                    latency_ms,
                ) = call_qwenpaw(
                    client,
                    base_url=base_url,
                    request_body=repair_body,
                    headers=headers,
                )
                qualification, advisory_text = apply_qwenpaw_response(
                    response_status_code=response_status_code,
                    content_type=content_type,
                    response_text=response_text,
                    latency_ms=latency_ms,
                )
                append_repair_history_entry(
                    result,
                    attempt=repair_attempt,
                    response_status_code=response_status_code,
                    failure_kind=result.get("failure_kind"),
                )
    except httpx.ConnectError:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw service is not reachable"
        result["failure_kind"] = "connect_error"
        reset_advisory_qualification_for_blocked_failure(result)
        append_pending_repair_failure_history(result, failure_kind="connect_error")
        write_evidence(result)
        return result
    except httpx.TimeoutException:
        result["outcome"] = "blocked"
        result["blocked_reason"] = "QwenPaw service timed out"
        result["failure_kind"] = "timeout"
        reset_advisory_qualification_for_blocked_failure(result)
        append_pending_repair_failure_history(result, failure_kind="timeout")
        write_evidence(result)
        return result
    except httpx.HTTPError as exc:
        result["outcome"] = "failed"
        result["failure_kind"] = exc.__class__.__name__
        result["sanitized_response_preview"] = bound_preview(str(exc))
        reset_advisory_qualification_for_blocked_failure(result)
        append_pending_repair_failure_history(
            result,
            failure_kind=exc.__class__.__name__,
        )
        write_evidence(result)
        return result
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
