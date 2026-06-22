import json

import httpx

from scripts import live_qwenpaw_smoke


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
