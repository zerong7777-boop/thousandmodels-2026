import json

import httpx
import pytest

from scripts import live_qwenpaw_smoke


@pytest.fixture(autouse=True)
def reset_store():
    yield


def test_requires_explicit_live_smoke_flag(monkeypatch, tmp_path):
    monkeypatch.delenv("RUN_LIVE_QWENPAW_SMOKE", raising=False)
    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(env={})

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "RUN_LIVE_QWENPAW_SMOKE is required"
    assert result["request_sent"] is False
    assert (tmp_path / "result.json").exists()


def test_rejects_non_localhost_base_url(monkeypatch, tmp_path):
    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "https://example.com",
        }
    )

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "QWENPAW_BASE_URL must point to localhost"
    assert result["request_sent"] is False


def test_sanitized_prompt_has_no_secret_or_local_path():
    prompt = live_qwenpaw_smoke.build_sanitized_prompt(
        event_id="demo-night-tour",
        merchant_id="m001",
        incident_kind="sold_out",
    )

    assert "demo-night-tour" in prompt
    assert "m001" in prompt
    assert "sold_out" in prompt
    assert "Authorization" not in prompt
    assert "DASHSCOPE_API_KEY" not in prompt
    assert "E:\\" not in prompt
    assert "C:\\Users" not in prompt


def test_redact_sensitive_text_removes_keys_bearers_passwords_and_local_paths():
    fake_key = "sk-" + "a" * 32
    raw = (
        f"Authorization: Bearer {fake_key} "
        f"DASHSCOPE_API_KEY={fake_key} "
        "QWENPAW_AUTH_PASSWORD" + "=secret "
        "path=Z:\\private\\workspace\\project\\apps"
    )

    redacted = live_qwenpaw_smoke.redact_sensitive_text(raw)

    assert fake_key not in redacted
    assert "Bearer" not in redacted
    assert "secret" not in redacted
    assert "Z:\\private" not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert "[REDACTED_LOCAL_PATH]" in redacted


def test_redact_sensitive_text_removes_standalone_sensitive_labels_and_spaced_paths():
    raw = (
        "DASHSCOPE_API_KEY "
        "QWENPAW_AUTH_PASSWORD "
        "Authorization "
        "path=Z:\\Private Users\\Jane Doe\\project\\file.txt "
        "debug=D:\\Program Files\\Qwen Paw\\debug.log"
    )

    redacted = live_qwenpaw_smoke.redact_sensitive_text(raw)

    assert "DASHSCOPE_API_KEY" not in redacted
    assert "QWENPAW_AUTH_PASSWORD" not in redacted
    assert "Authorization" not in redacted
    assert "Z:\\Private Users" not in redacted
    assert "Jane Doe" not in redacted
    assert "Doe\\project" not in redacted
    assert "D:\\Program Files" not in redacted
    assert "Qwen Paw" not in redacted
    assert "debug.log" not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert "[REDACTED_LOCAL_PATH]" in redacted


def test_parse_sse_response_bounds_and_sanitizes_preview():
    fake_key = "sk-" + "a" * 32
    text = (
        "data: {\"content\":\"First chunk\"}\n\n"
        f"data: {{\"content\":\"Second chunk with {fake_key}\"}}\n\n"
    )

    preview = live_qwenpaw_smoke.parse_response_preview(
        content_type="text/event-stream",
        text=text,
        max_chars=80,
    )

    assert "First chunk" in preview
    assert "Second chunk" in preview
    assert fake_key not in preview
    assert len(preview) <= 80


def test_parse_qwenpaw_sse_token_stream_ignores_null_and_compacts_tokens():
    text = (
        'data: {"status":"created","output":null}\n\n'
        'data: {"status":"in_progress","output":null}\n\n'
        'data: {"output":"Ad"}\n\n'
        'data: {"output":"visory"}\n\n'
        'data: {"output":" Response"}\n\n'
        'data: {"output":" with recovery_rationale"}\n\n'
    )

    preview = live_qwenpaw_smoke.parse_response_preview(
        content_type="text/event-stream",
        text=text,
        max_chars=120,
    )

    assert "None" not in preview
    assert "Advisory Response" in preview
    assert "recovery_rationale" in preview


def test_parse_json_response_bounds_and_sanitizes_preview():
    fake_key = "sk-" + "a" * 32
    text = json.dumps(
        {
            "message": {
                "content": f"QwenPaw says advisory only with Bearer {fake_key}"
            }
        }
    )

    preview = live_qwenpaw_smoke.parse_response_preview(
        content_type="application/json",
        text=text,
        max_chars=96,
    )

    assert "QwenPaw says advisory only" in preview
    assert "Bearer" not in preview
    assert len(preview) <= 96


def _set_temp_evidence_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")


def _live_smoke_env(**overrides):
    env = {
        "RUN_LIVE_QWENPAW_SMOKE": "1",
        "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
    }
    env.update(overrides)
    return env


def _assert_v17_evidence(tmp_path, result):
    evidence = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert result["advisory_contract_version"] == "v1.7"
    assert evidence["advisory_contract_version"] == "v1.7"
    return evidence


def _assert_advisory_field_presence(result, **expected):
    assert result["advisory_fields_present"] == {
        "recovery_rationale": expected["recovery_rationale"],
        "visitor_safe_notice_draft": expected["visitor_safe_notice_draft"],
        "safety_notes": expected["safety_notes"],
    }


def _assert_unqualified_reachable(result, *, failure_kind):
    assert result["outcome"] == "advisory_unqualified"
    assert result["provider_reachable"] is True
    assert result["advisory_status"] == "unqualified"
    assert result["qualification_failure_kind"] == failure_kind


def test_json_advisory_with_required_fields_is_qualified(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors to the next available hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer the nearest safe alternative.",
        "safety_notes": "Advisory only. Do not publish or mutate merchant runtime state.",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(),
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["provider_reachable"] is True
    assert result["advisory_status"] == "qualified"
    assert result["qualification_failure_kind"] is None
    _assert_advisory_field_presence(
        result,
        recovery_rationale=True,
        visitor_safe_notice_draft=True,
        safety_notes=True,
    )
    excerpts = result["sanitized_advisory_excerpt"]
    assert excerpts["recovery_rationale"].startswith("Route affected visitors")
    assert excerpts["visitor_safe_notice_draft"].startswith("Some items sold out")
    assert excerpts["safety_notes"].startswith("Advisory only")
    _assert_v17_evidence(tmp_path, result)


def test_markdown_advisory_with_preamble_is_qualified(monkeypatch, tmp_path):
    markdown = """I will inspect context before answering.

### recovery_rationale
Route affected visitors to the next available hosted slot.

### visitor_safe_notice_draft
Some items sold out; staff will offer the nearest safe alternative.

### safety_notes
Advisory only. Do not publish or mutate merchant runtime state.
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=f"data: {json.dumps({'output': markdown})}\n\n",
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(),
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["provider_reachable"] is True
    assert result["advisory_status"] == "qualified"
    assert result["qualification_failure_kind"] is None
    assert result["preamble_stripped"] is True
    assert result["sanitized_advisory_excerpt"]["visitor_safe_notice_draft"].startswith("Some items")


def test_advisory_missing_required_fields_is_unqualified(monkeypatch, tmp_path):
    advisory = {"recovery_rationale": "Route affected visitors to another hosted slot."}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    _assert_advisory_field_presence(
        result,
        recovery_rationale=True,
        visitor_safe_notice_draft=False,
        safety_notes=False,
    )


def test_preamble_only_response_is_unqualified_missing_fields(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"I will inspect context before answering."}\n\n',
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    _assert_advisory_field_presence(
        result,
        recovery_rationale=False,
        visitor_safe_notice_draft=False,
        safety_notes=False,
    )


def test_authority_claim_in_safety_notes_is_unqualified(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors to the next available hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer an alternative.",
        "safety_notes": "I published the notice and updated merchant runtime state.",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="unsafe_authority_claim")
    _assert_advisory_field_presence(
        result,
        recovery_rationale=True,
        visitor_safe_notice_draft=True,
        safety_notes=True,
    )


def test_main_returns_zero_only_for_advisory_qualified(monkeypatch, tmp_path):
    monkeypatch.setattr(live_qwenpaw_smoke, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(
        live_qwenpaw_smoke,
        "run_smoke",
        lambda: {"outcome": "advisory_qualified"},
    )

    assert live_qwenpaw_smoke.main() == 0

    monkeypatch.setattr(
        live_qwenpaw_smoke,
        "run_smoke",
        lambda: {"outcome": "advisory_unqualified"},
    )

    assert live_qwenpaw_smoke.main() == 1


def test_unstructured_fake_http_response_is_unqualified(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/agent/process"
        assert "x-agent-id" not in request.headers
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["session_id"] == "zhiyin-v15-qwenpaw-smoke"
        assert "demo-night-tour" in payload["input"][0]["content"][0]["text"]
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"Advisory only response from QwenPaw"}\n\n',
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert result["request_sent"] is True
    assert result["response_status_code"] == 200
    assert result["endpoint"] == "/api/agent/process"
    assert result["base_url_host"] == "127.0.0.1"
    assert "Advisory only response" in result["sanitized_response_preview"]
    assert result["response_preview_sha256"]
    assert (tmp_path / "result.json").exists()
    assert (tmp_path / "smoke.md").exists()


def test_optional_agent_id_is_sent_as_header_and_written_to_evidence(monkeypatch, tmp_path):
    captured_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"QA agent advisory response"}\n\n',
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_AGENT_ID": "QwenPaw_QA_Agent_0.2",
        },
        transport=httpx.MockTransport(handler),
    )
    evidence = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert captured_headers["x-agent-id"] == "QwenPaw_QA_Agent_0.2"
    assert result["agent_id"] == "QwenPaw_QA_Agent_0.2"
    assert evidence["agent_id"] == "QwenPaw_QA_Agent_0.2"


def test_render_smoke_doc_strips_response_preview_trailing_whitespace():
    doc = live_qwenpaw_smoke.render_smoke_doc(
        {
            "outcome": "advisory_unqualified",
            "endpoint": "/api/agent/process",
            "base_url_host": "127.0.0.1",
            "agent_id": "QwenPaw_QA_Agent_0.2",
            "request_sent": True,
            "response_status_code": 200,
            "latency_ms": 1234,
            "blocked_reason": None,
            "failure_kind": None,
            "sanitized_response_preview": "first line  \nsecond line  ",
        }
    )

    assert "  \n" not in doc
    assert all(line == line.rstrip() for line in doc.splitlines())


def test_run_smoke_disables_httpx_proxy_environment(monkeypatch, tmp_path):
    original_client = httpx.Client
    captured_client_kwargs = {}

    def recording_client(*args, **kwargs):
        captured_client_kwargs.update(kwargs)
        return original_client(*args, **kwargs)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"Direct localhost response"}\n\n',
        )

    monkeypatch.setattr(live_qwenpaw_smoke.httpx, "Client", recording_client)
    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert captured_client_kwargs.get("trust_env") is False


def test_session_id_is_sanitized_and_bounded_in_request_and_evidence(monkeypatch, tmp_path):
    fake_key = "sk-" + "a" * 32
    raw_session_id = (
        "session "
        "Bearer "
        + fake_key
        + " debug=D:\\Program Files\\Qwen Paw\\debug.log "
        + " path=Z:\\private\\workspace\\project\\apps\\api "
        + ("x" * 160)
    )
    captured_payload = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": "Advisory only response from QwenPaw"}},
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_SMOKE_SESSION_ID": raw_session_id,
        },
        transport=httpx.MockTransport(handler),
    )
    evidence = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    for session_id in (
        result["session_id"],
        evidence["session_id"],
        captured_payload["session_id"],
    ):
        assert fake_key not in session_id
        assert "Bearer" not in session_id
        assert "D:\\Program Files" not in session_id
        assert "Qwen Paw" not in session_id
        assert "debug.log" not in session_id
        assert "Z:\\private" not in session_id
        assert len(session_id) <= 96


class _ExplodingAfterFirstChunkStream(httpx.SyncByteStream):
    def __init__(self, first_chunk: bytes, sentinel: bytes):
        self.first_chunk = first_chunk
        self.sentinel = sentinel

    def __iter__(self):
        yield self.first_chunk
        raise AssertionError(
            f"response read exceeded cap and reached {self.sentinel.decode('utf-8')}"
        )


@pytest.mark.parametrize(
    ("content_type", "first_chunk", "expected_preview"),
    [
        (
            "text/event-stream",
            b'data: {"content":"bounded sse response"}\n\n',
            "bounded sse response",
        ),
        (
            "application/json",
            json.dumps({"message": {"content": "bounded json response"}}).encode("utf-8"),
            "bounded json response",
        ),
    ],
)
def test_run_smoke_reads_bounded_response_stream_without_sentinel(
    monkeypatch,
    tmp_path,
    content_type,
    first_chunk,
    expected_preview,
):
    sentinel = b"SHOULD_NOT_BE_READ_AFTER_RESPONSE_CAP"
    padded_first_chunk = first_chunk + (
        b" " * (65536 - len(first_chunk))
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": content_type},
            stream=_ExplodingAfterFirstChunkStream(padded_first_chunk, sentinel),
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )
    evidence_text = (tmp_path / "result.json").read_text(encoding="utf-8")

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert expected_preview in result["sanitized_response_preview"]
    assert len(result["sanitized_response_preview"]) <= 1200
    assert sentinel.decode("utf-8") not in evidence_text
    assert sentinel.decode("utf-8") not in result["sanitized_response_preview"]


def test_failed_qwenpaw_sse_response_records_blocked_provider_error(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=(
                'data: {"sequence_number":0,"status":"created","output":null}\n\n'
                'data: {"sequence_number":1,"status":"in_progress","output":null}\n\n'
                'data: {"sequence_number":2,"status":"failed",'
                '"error":{"code":"PROVIDER_ERROR","message":"No active model configured."},'
                '"output":null}\n\n'
            ),
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "QwenPaw model is not configured"
    assert result["failure_kind"] == "provider_error"
    assert "No active model configured" in result["sanitized_response_preview"]


def test_auth_error_json_keeps_auth_required_classification(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            headers={"content-type": "application/json"},
            json={"error": "unauthorized"},
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "QwenPaw authentication is required"
    assert result["failure_kind"] == "auth_required"
    assert result["response_status_code"] == 401


def test_non_failed_sse_error_field_does_not_override_unqualified_reachable(
    monkeypatch,
    tmp_path,
):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=(
                'data: {"status":"completed","error":"nonfatal warning",'
                '"output":{"content":"Advisory only response from QwenPaw"}}\n\n'
            ),
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert result["failure_kind"] is None
    assert "Advisory only response" in result["sanitized_response_preview"]


def test_qwenpaw_error_payload_records_blocked_instead_of_live_success(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"type":"error","error":"Agent not found: missing-agent"}\n\n',
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "QwenPaw returned error"
    assert result["failure_kind"] == "qwenpaw_error"
    assert "Agent not found" in result["sanitized_response_preview"]


def test_provider_error_with_model_word_is_not_assumed_unconfigured(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=(
                'data: {"status":"failed",'
                '"error":{"code":"PROVIDER_ERROR","message":"Selected model timed out."},'
                '"output":null}\n\n'
            ),
        )

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "QwenPaw returned provider error"
    assert result["failure_kind"] == "provider_error"
    assert "Selected model timed out." in result["sanitized_response_preview"]


def test_connection_failure_records_blocked(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    monkeypatch.setattr(live_qwenpaw_smoke, "ASSET_DIR", tmp_path)
    monkeypatch.setattr(live_qwenpaw_smoke, "RESULT_JSON", tmp_path / "result.json")
    monkeypatch.setattr(live_qwenpaw_smoke, "SMOKE_DOC", tmp_path / "smoke.md")

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "blocked"
    assert result["blocked_reason"] == "QwenPaw service is not reachable"
    assert result["request_sent"] is True
    assert result["failure_kind"] == "connect_error"
