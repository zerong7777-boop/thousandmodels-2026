import pytest

from scripts.live_qwen_smoke import (
    ACCEPTED_MODEL_STATUSES,
    LiveSmokeConfigError,
    has_live_success,
    render_markdown,
    require_live_qwen_env,
    sanitize_model_call,
)


def test_live_smoke_env_requires_manual_guard(monkeypatch):
    monkeypatch.delenv("RUN_LIVE_QWEN_SMOKE", raising=False)
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")

    with pytest.raises(LiveSmokeConfigError, match="RUN_LIVE_QWEN_SMOKE"):
        require_live_qwen_env()


@pytest.mark.parametrize("guard_value", ["true", "0"])
def test_live_smoke_env_requires_exact_manual_guard_value(monkeypatch, guard_value):
    monkeypatch.setenv("RUN_LIVE_QWEN_SMOKE", guard_value)
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")

    with pytest.raises(LiveSmokeConfigError, match="RUN_LIVE_QWEN_SMOKE"):
        require_live_qwen_env()


def test_live_smoke_env_requires_qwen_backend(monkeypatch):
    monkeypatch.setenv("RUN_LIVE_QWEN_SMOKE", "1")
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "deterministic")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")

    with pytest.raises(LiveSmokeConfigError, match="AGENT_DRAFT_BACKEND=qwen"):
        require_live_qwen_env()


def test_live_smoke_env_requires_provider_key(monkeypatch):
    monkeypatch.setenv("RUN_LIVE_QWEN_SMOKE", "1")
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

    with pytest.raises(LiveSmokeConfigError, match="DASHSCOPE_API_KEY"):
        require_live_qwen_env()


def test_live_smoke_env_returns_non_secret_config(monkeypatch):
    monkeypatch.setenv("RUN_LIVE_QWEN_SMOKE", "1")
    monkeypatch.setenv("AGENT_DRAFT_BACKEND", "qwen")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setenv("QWEN_MODEL", "qwen-plus")

    config = require_live_qwen_env()

    assert config == {
        "agent_draft_backend": "qwen",
        "qwen_model": "qwen-plus",
        "qwen_timeout_seconds": "30",
    }


def test_sanitize_model_call_removes_raw_payload_and_headers():
    raw_call = {
        "model_call_id": "model_001",
        "run_id": "run_001",
        "provider": "dashscope",
        "model": "qwen-plus",
        "prompt_template_id": "qwen_public_notice_v1",
        "input_refs": ["incident:inc_inventory_m001"],
        "response_status": "success",
        "parsed_output": {"content": "full model content should not be copied here"},
        "fallback_used": False,
        "error_summary": None,
        "created_at": "2026-06-12T10:00:00Z",
        "Authorization": "Bearer sk-secret",
    }

    sanitized = sanitize_model_call(raw_call)

    assert sanitized["response_status"] == "success"
    assert sanitized["provider"] == "dashscope"
    assert "parsed_output" not in sanitized
    assert "Authorization" not in sanitized
    assert "sk-secret" not in str(sanitized)


def test_accepted_model_statuses_match_v10_contract():
    assert ACCEPTED_MODEL_STATUSES == {
        "skipped",
        "success",
        "invalid_json",
        "schema_failed",
        "provider_error",
    }


def test_has_live_success_only_counts_non_fallback_success():
    result = {
        "recovery": {"model_calls": [{"response_status": "schema_failed", "fallback_used": True}]},
        "review": {"model_calls": [{"response_status": "success", "fallback_used": False}]},
    }

    assert has_live_success(result) is True


def test_has_live_success_ignores_fallback_successes():
    result = {
        "recovery": {"model_calls": [{"response_status": "success", "fallback_used": True}]},
        "review": {"model_calls": [{"response_status": "success", "fallback_used": True}]},
    }

    assert has_live_success(result) is False


def test_render_markdown_does_not_include_secret_values():
    result = {
        "date": "2026-06-12",
        "config": {
            "agent_draft_backend": "qwen",
            "qwen_model": "qwen-plus",
            "qwen_timeout_seconds": "30",
        },
        "outcome": "live_success",
        "recovery": {
            "run": {
                "run_id": "run_recovery",
                "mode": "qwen_draft",
                "status": "completed",
                "fallback_used": False,
            },
            "model_calls": [
                {
                    "model_call_id": "model_recovery",
                    "run_id": "run_recovery",
                    "provider": "dashscope",
                    "model": "qwen-plus",
                    "prompt_template_id": "qwen_public_notice_v1",
                    "input_refs": ["incident:inc_inventory_m001"],
                    "response_status": "success",
                    "fallback_used": False,
                    "error_summary": None,
                    "created_at": "2026-06-12T10:00:00Z",
                    "Authorization": "Bearer sk-secret",
                    "parsed_output": {"content": "raw provider payload includes sk-secret"},
                }
            ],
            "evaluations": [
                {
                    "evaluation_id": "eval_recovery",
                    "schema_pass": True,
                    "fallback_used": False,
                    "unsafe_mutation_attempted": False,
                    "human_approval_required": True,
                    "forbidden_public_terms_present": False,
                    "public_copy_ready": True,
                    "notes": ["public copy ready"],
                }
            ],
            "drafts": [
                {
                    "draft_type": "public_notice",
                    "locale": "en",
                    "content_preview": "Please continue.",
                }
            ],
        },
        "review": {
            "run": {
                "run_id": "run_review",
                "mode": "qwen_draft",
                "status": "completed",
                "fallback_used": False,
            },
            "model_calls": [],
            "evaluations": [],
            "drafts": [],
        },
        "public_projection": {"current_plan_version": 2, "notice_count": 1},
        "deterministic_fallback_probe": {
            "agent_run_mode": "deterministic",
            "agent_run_status": "completed",
            "fallback_used": False,
        },
        "secret_policy": "No API key, Authorization header, or raw provider payload is stored.",
    }

    markdown = render_markdown(result)

    assert "# v1.1 Live Qwen Smoke" in markdown
    assert "qwen_public_notice_v1" in markdown
    assert "No API key" in markdown
    assert "sk-secret" not in markdown
    assert "Authorization: Bearer" not in markdown
    assert "raw provider payload" not in markdown
