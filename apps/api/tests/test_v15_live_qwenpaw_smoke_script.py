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
        "path=E:\\rz\\competitions\\thousandmodels-2026\\apps"
    )

    redacted = live_qwenpaw_smoke.redact_sensitive_text(raw)

    assert fake_key not in redacted
    assert "Bearer" not in redacted
    assert "secret" not in redacted
    assert "E:\\rz" not in redacted
    assert "[REDACTED_SECRET]" in redacted
    assert "[REDACTED_LOCAL_PATH]" in redacted


def test_redact_sensitive_text_removes_standalone_sensitive_labels_and_spaced_paths():
    raw = (
        "DASHSCOPE_API_KEY "
        "QWENPAW_AUTH_PASSWORD "
        "Authorization "
        "path=C:\\Users\\Jane Doe\\project\\file.txt "
        "debug=D:\\Program Files\\Qwen Paw\\debug.log"
    )

    redacted = live_qwenpaw_smoke.redact_sensitive_text(raw)

    assert "DASHSCOPE_API_KEY" not in redacted
    assert "QWENPAW_AUTH_PASSWORD" not in redacted
    assert "Authorization" not in redacted
    assert "C:\\Users" not in redacted
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


def test_live_success_with_fake_http_transport(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/agent/process"
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

    assert result["outcome"] == "live_success"
    assert result["request_sent"] is True
    assert result["response_status_code"] == 200
    assert result["endpoint"] == "/api/agent/process"
    assert result["base_url_host"] == "127.0.0.1"
    assert "Advisory only response" in result["sanitized_response_preview"]
    assert result["response_preview_sha256"]
    assert (tmp_path / "result.json").exists()
    assert (tmp_path / "smoke.md").exists()


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

    assert result["outcome"] == "live_success"
    assert captured_client_kwargs.get("trust_env") is False


def test_session_id_is_sanitized_and_bounded_in_request_and_evidence(monkeypatch, tmp_path):
    fake_key = "sk-" + "a" * 32
    raw_session_id = (
        "session "
        "Bearer "
        + fake_key
        + " debug=D:\\Program Files\\Qwen Paw\\debug.log "
        + " path=E:\\rz\\competitions\\thousandmodels-2026\\apps\\api "
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

    assert result["outcome"] == "live_success"
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
        assert "E:\\rz" not in session_id
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

    assert result["outcome"] == "live_success"
    assert expected_preview in result["sanitized_response_preview"]
    assert len(result["sanitized_response_preview"]) <= 1200
    assert sentinel.decode("utf-8") not in evidence_text
    assert sentinel.decode("utf-8") not in result["sanitized_response_preview"]


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
