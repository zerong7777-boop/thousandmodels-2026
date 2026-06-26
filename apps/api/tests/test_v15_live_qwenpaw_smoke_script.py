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


def test_prompt_a_json_only_is_contract_first():
    prompt = live_qwenpaw_smoke.build_sanitized_prompt(
        prompt_variant="prompt_a_json_only"
    )

    assert "Return exactly one JSON object" in prompt
    assert '"recovery_rationale"' in prompt
    assert '"visitor_safe_notice_draft"' in prompt
    assert '"safety_notes"' in prompt
    assert "Do not inspect tools" in prompt
    assert "Do not describe your reasoning" in prompt
    assert "No Markdown" in prompt


def test_prompt_b_markdown_sections_keeps_exact_headings():
    prompt = live_qwenpaw_smoke.build_sanitized_prompt(
        prompt_variant="prompt_b_markdown_sections"
    )

    assert "### recovery_rationale" in prompt
    assert "### visitor_safe_notice_draft" in prompt
    assert "### safety_notes" in prompt
    assert "Do not inspect tools" in prompt


def test_prompt_c_few_shot_json_labels_invalid_examples():
    prompt = live_qwenpaw_smoke.build_sanitized_prompt(
        prompt_variant="prompt_c_few_shot_json"
    )

    assert "VALID EXAMPLE" in prompt
    assert "INVALID EXAMPLE" in prompt
    assert "invalid because it has no JSON object" in prompt
    assert "invalid because it is missing safety_notes" in prompt


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


def _assert_versioned_evidence(tmp_path, result):
    evidence = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert result["advisory_contract_version"] == "v1.8"
    assert evidence["advisory_contract_version"] == result["advisory_contract_version"]
    assert evidence["outcome"] == result["outcome"]
    assert evidence["advisory_status"] == result["advisory_status"]
    assert (
        evidence["qualification_failure_kind"]
        == result["qualification_failure_kind"]
    )
    assert evidence["advisory_fields_present"] == result["advisory_fields_present"]
    assert (
        evidence["sanitized_advisory_excerpt"]
        == result["sanitized_advisory_excerpt"]
    )
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


def _assert_blocked_advisory_fields_reset(result, *, failure_kind):
    assert result["outcome"] == "blocked"
    assert result["failure_kind"] == failure_kind
    assert result["provider_reachable"] is False
    assert result["advisory_status"] == "not_applicable"
    assert result["qualification_failure_kind"] is None
    _assert_advisory_field_presence(
        result,
        recovery_rationale=False,
        visitor_safe_notice_draft=False,
        safety_notes=False,
    )
    assert result["sanitized_advisory_excerpt"] == {}
    assert result["preamble_stripped"] is False
    assert result["parsed_output_format"] is None
    assert result["json_no_preamble_pass"] is None


def _assert_repair_failure_history(result, *, failure_kind):
    assert len(result["repair_history"]) == 1
    entry = result["repair_history"][0]
    assert entry["attempt"] == 1
    assert entry.get("failure_kind") == failure_kind
    assert entry.get("qualification_failure_kind") is None
    assert not any((entry.get("advisory_fields_present") or {}).values())


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
    _assert_versioned_evidence(tmp_path, result)


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
        env=_live_smoke_env(QWENPAW_VALIDATOR_VARIANT="strict_existing_validator"),
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
    _assert_versioned_evidence(tmp_path, result)


def test_missing_fields_response_can_be_repaired_to_qualified(monkeypatch, tmp_path):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
    }
    repaired_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer the nearest safe alternative.",
        "safety_notes": "Advisory only. Do not publish or mutate merchant runtime state.",
    }
    request_texts = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        request_texts.append(payload["input"][0]["content"][0]["text"])
        advisory = initial_advisory if len(request_texts) == 1 else repaired_advisory
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["repair_attempt_count"] == 1
    assert len(result["repair_history"]) == 1
    assert len(request_texts) == 2
    repair_prompt = request_texts[1]
    assert "missing_fields" in repair_prompt
    assert "visitor_safe_notice_draft" in repair_prompt
    assert "safety_notes" in repair_prompt


def test_repair_http_failure_resets_previous_advisory_state(monkeypatch, tmp_path):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
    }
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(
                200,
                headers={"content-type": "application/json"},
                json={"message": {"content": json.dumps(initial_advisory)}},
            )
        return httpx.Response(
            500,
            headers={"content-type": "application/json"},
            json={"error": "provider unavailable"},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    _assert_blocked_advisory_fields_reset(result, failure_kind="http_500")
    assert result["repair_attempt_count"] == 1
    assert call_count == 2
    assert all(
        not any(entry.get("advisory_fields_present", {}).values())
        for entry in result["repair_history"]
    )


def test_repair_provider_error_sse_blocks_and_resets_previous_advisory_state(
    monkeypatch,
    tmp_path,
):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
    }
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(
                200,
                headers={"content-type": "application/json"},
                json={"message": {"content": json.dumps(initial_advisory)}},
            )
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=(
                'data: {"status":"failed",'
                '"error":{"code":"PROVIDER_ERROR","message":"No active model configured."},'
                '"output":null}\n\n'
            ),
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    _assert_blocked_advisory_fields_reset(result, failure_kind="provider_error")
    assert result["repair_attempt_count"] == 1
    assert call_count == 2


def test_repair_generic_http_error_fails_and_resets_previous_advisory_state(
    monkeypatch,
    tmp_path,
):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
    }
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise httpx.HTTPError("repair failed")
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(initial_advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "failed"
    assert result["failure_kind"] == "HTTPError"
    assert result["repair_attempt_count"] == 1
    assert call_count == 2
    assert result["provider_reachable"] is False
    assert result["advisory_status"] == "not_applicable"
    assert result["qualification_failure_kind"] is None
    _assert_advisory_field_presence(
        result,
        recovery_rationale=False,
        visitor_safe_notice_draft=False,
        safety_notes=False,
    )
    assert result["sanitized_advisory_excerpt"] == {}
    assert result["preamble_stripped"] is False
    assert result["parsed_output_format"] is None
    assert result["json_no_preamble_pass"] is None
    _assert_repair_failure_history(result, failure_kind="HTTPError")


@pytest.mark.parametrize(
    ("raised", "failure_kind"),
    [
        (httpx.TimeoutException("repair timed out"), "timeout"),
        (httpx.ConnectError("repair connect failed"), "connect_error"),
    ],
)
def test_repair_network_exception_counts_attempt_and_resets_state(
    monkeypatch,
    tmp_path,
    raised,
    failure_kind,
):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
    }
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise raised
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(initial_advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    _assert_blocked_advisory_fields_reset(result, failure_kind=failure_kind)
    assert result["repair_attempt_count"] == 1
    assert call_count == 2
    _assert_repair_failure_history(result, failure_kind=failure_kind)


def test_repair_loop_stops_after_bounded_missing_fields_failure(monkeypatch, tmp_path):
    advisory = {"recovery_rationale": "Route affected visitors to another hosted slot."}
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="2",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert result["repair_attempt_count"] == 2
    assert len(result["repair_history"]) == 2
    assert call_count == 3


def test_unsafe_authority_claim_repair_remains_unqualified(monkeypatch, tmp_path):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
    }
    unsafe_repaired_advisory = {
        "recovery_rationale": "Route affected visitors to another hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer the nearest safe alternative.",
        "safety_notes": "I published the notice and updated merchant runtime.",
    }
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        advisory = initial_advisory if call_count == 1 else unsafe_repaired_advisory
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="unsafe_authority_claim")
    assert result["repair_attempt_count"] == 1
    assert len(result["repair_history"]) == 1
    assert call_count == 2


def test_preamble_only_response_is_unqualified_missing_fields(monkeypatch, tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"I will inspect context before answering."}\n\n',
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(QWENPAW_VALIDATOR_VARIANT="strict_existing_validator"),
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


def test_passive_authority_claim_is_unqualified(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors to the next available hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer an alternative.",
        "safety_notes": "The notice was published and merchant runtime was updated.",
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


def test_preamble_authority_claim_is_unqualified(monkeypatch, tmp_path):
    markdown = """I approved the plan before drafting the advisory.

### recovery_rationale
Route affected visitors to the next available hosted slot.

### visitor_safe_notice_draft
Some items sold out; staff will offer the nearest safe alternative.

### safety_notes
Advisory only. No plan, notice, merchant runtime, coupon, or redemption state has changed.
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=f"data: {json.dumps({'output': markdown})}\n\n",
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(QWENPAW_VALIDATOR_VARIANT="strict_existing_validator"),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="unsafe_authority_claim")
    assert result["preamble_stripped"] is True


def test_safe_authority_negation_remains_qualified(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors to the next available hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer an alternative.",
        "safety_notes": "I have not approved the plan. Advisory only; organizer approval is still required.",
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
    assert result["advisory_status"] == "qualified"
    assert result["qualification_failure_kind"] is None


@pytest.mark.parametrize(
    "safety_notes",
    [
        "I have created a coupon for affected visitors.",
        "The redemption was claimed for affected visitors.",
    ],
)
def test_coupon_redemption_authority_claim_is_unqualified(
    monkeypatch,
    tmp_path,
    safety_notes,
):
    advisory = {
        "recovery_rationale": "Route affected visitors to the next available hosted slot.",
        "visitor_safe_notice_draft": "Some items sold out; staff will offer an alternative.",
        "safety_notes": safety_notes,
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
        lambda: {"outcome": "live_success"},
    )

    assert live_qwenpaw_smoke.main() == 1

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
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
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
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
        },
        transport=httpx.MockTransport(handler),
    )
    evidence = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert captured_headers["x-agent-id"] == "QwenPaw_QA_Agent_0.2"
    assert result["agent_id"] == "QwenPaw_QA_Agent_0.2"
    assert evidence["agent_id"] == "QwenPaw_QA_Agent_0.2"


@pytest.mark.parametrize(
    "env_overrides",
    [
        {"QWENPAW_AGENT_VARIANT": "agent_default"},
        {
            "QWENPAW_AGENT_VARIANT": "agent_default",
            "QWENPAW_AGENT_ID": "QwenPaw_QA_Agent_0.2",
        },
    ],
)
def test_agent_default_variant_omits_agent_id_header(
    monkeypatch,
    tmp_path,
    env_overrides,
):
    captured_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"Default agent advisory response"}\n\n',
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
            **env_overrides,
        ),
        transport=httpx.MockTransport(handler),
    )
    evidence = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert "x-agent-id" not in captured_headers
    assert result["agent_variant"] == "agent_default"
    assert result["agent_id"] is None
    assert evidence["agent_id"] is None


def test_agent_qa_current_variant_uses_explicit_agent_id(monkeypatch, tmp_path):
    captured_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text='data: {"content":"QA agent advisory response"}\n\n',
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_AGENT_VARIANT="agent_qa_current",
            QWENPAW_AGENT_ID="QwenPaw_QA_Agent_0.2",
            QWENPAW_VALIDATOR_VARIANT="strict_existing_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    _assert_unqualified_reachable(result, failure_kind="missing_fields")
    assert captured_headers["x-agent-id"] == "QwenPaw_QA_Agent_0.2"
    assert result["agent_id"] == "QwenPaw_QA_Agent_0.2"


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


def test_render_smoke_doc_includes_empty_repair_history_state():
    doc = live_qwenpaw_smoke.render_smoke_doc(
        {
            "outcome": "blocked",
            "endpoint": "/api/agent/process",
            "base_url_host": "127.0.0.1",
            "request_sent": False,
            "response_status_code": None,
            "latency_ms": None,
            "blocked_reason": "RUN_LIVE_QWENPAW_SMOKE is required",
            "failure_kind": "missing_live_flag",
            "sanitized_response_preview": "",
            "repair_history": [],
        }
    )

    assert doc.index("## Advisory Field Check") < doc.index("## Repair History")
    assert doc.index("## Repair History") < doc.index("## Evidence")
    assert "- No repair attempts were used." in doc
    assert "## Repair History\n\n- No repair attempts were used.\n\n## Evidence" in doc


def test_render_smoke_doc_includes_bounded_repair_history_metadata():
    doc = live_qwenpaw_smoke.render_smoke_doc(
        {
            "outcome": "advisory_unqualified",
            "endpoint": "/api/agent/process",
            "base_url_host": "127.0.0.1",
            "request_sent": True,
            "response_status_code": 200,
            "latency_ms": 1234,
            "blocked_reason": None,
            "failure_kind": None,
            "sanitized_response_preview": "bounded preview",
            "repair_history": [
                {
                    "attempt": 1,
                    "response_status_code": 200,
                    "advisory_status": "unqualified",
                    "qualification_failure_kind": "missing_fields",
                    "raw_response": "must not be rendered",
                }
            ],
        }
    )

    assert "## Repair History" in doc
    assert "- Attempt `1`: response_status_code=`200`" in doc
    assert "advisory_status=`unqualified`" in doc
    assert "qualification_failure_kind=`missing_fields`" in doc
    assert "must not be rendered" not in doc


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
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
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
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
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
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
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
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
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


def test_invalid_prompt_variant_blocks_before_request(monkeypatch, tmp_path):
    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_PROMPT_VARIANT": "missing_variant",
        },
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    )

    assert result["outcome"] == "blocked"
    assert result["request_sent"] is False
    assert result["failure_kind"] == "invalid_prompt_variant"
    assert result["prompt_variant"] == "missing_variant"


def test_json_no_preamble_validator_accepts_exact_json(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=f"data: {json.dumps({'output': json.dumps(advisory)})}\n\n",
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_PROMPT_VARIANT": "prompt_a_json_only",
            "QWENPAW_VALIDATOR_VARIANT": "json_no_preamble_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["validator_variant"] == "json_no_preamble_validator"
    assert result["json_no_preamble_pass"] is True
    assert result["parsed_output_format"] == "json"


def test_json_no_preamble_validator_uses_qwenpaw_typed_text_not_thinking(
    monkeypatch, tmp_path
):
    advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
    }
    typed_message = {
        "object": "message",
        "status": "completed",
        "output": [
            {
                "content": [
                    {
                        "type": "thinking",
                        "thinking": "The user wants a JSON object, so I will construct it.",
                    },
                    {"type": "text", "text": json.dumps(advisory)},
                ]
            }
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=f"data: {json.dumps(typed_message)}\n\n",
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_PROMPT_VARIANT": "prompt_a_json_only",
            "QWENPAW_VALIDATOR_VARIANT": "json_no_preamble_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["json_no_preamble_pass"] is True
    assert result["parsed_output_format"] == "json"
    assert "The user wants" not in result["sanitized_response_preview"]


def test_json_no_preamble_validator_uses_qwenpaw_message_delta_not_reasoning(
    monkeypatch, tmp_path
):
    advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
    }
    advisory_json = json.dumps(advisory)
    events = [
        {"object": "response", "status": "created", "output": None},
        {
            "object": "message",
            "status": "in_progress",
            "type": "reasoning",
            "id": "msg_reasoning",
            "role": "assistant",
        },
        {
            "object": "content",
            "status": "in_progress",
            "type": "text",
            "msg_id": "msg_reasoning",
            "text": "The user wants JSON.",
        },
        {
            "object": "content",
            "status": "completed",
            "type": "text",
            "msg_id": "msg_reasoning",
            "text": "The user wants JSON.",
        },
        {
            "object": "content",
            "status": "in_progress",
            "type": "text",
            "msg_id": "msg_answer",
            "text": advisory_json[:80],
        },
        {
            "object": "content",
            "status": "in_progress",
            "type": "text",
            "msg_id": "msg_answer",
            "text": advisory_json[80:],
        },
        {
            "object": "message",
            "status": "completed",
            "type": "message",
            "id": "msg_answer",
            "role": "assistant",
        },
        {"object": "response", "status": "completed", "output": None},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text="".join(f"data: {json.dumps(event)}\n\n" for event in events),
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_PROMPT_VARIANT": "prompt_a_json_only",
            "QWENPAW_VALIDATOR_VARIANT": "json_no_preamble_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["json_no_preamble_pass"] is True
    assert result["parsed_output_format"] == "json"
    assert "The user wants" not in result["sanitized_response_preview"]


def test_json_no_preamble_validator_skips_reasoning_in_completed_response_output(
    monkeypatch, tmp_path
):
    advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
    }
    advisory_json = json.dumps(advisory)
    events = [
        {
            "object": "content",
            "status": "in_progress",
            "type": "text",
            "msg_id": "msg_answer",
            "text": advisory_json,
        },
        {
            "object": "message",
            "status": "completed",
            "type": "message",
            "id": "msg_answer",
            "role": "assistant",
        },
        {
            "object": "response",
            "status": "completed",
            "output": [
                {
                    "object": "message",
                    "type": "reasoning",
                    "content": [
                        {
                            "type": "text",
                            "text": "The user wants JSON, so I will construct it.",
                        }
                    ],
                },
                {
                    "object": "message",
                    "type": "message",
                    "content": [{"type": "text", "text": advisory_json}],
                },
            ],
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text="".join(f"data: {json.dumps(event)}\n\n" for event in events),
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_PROMPT_VARIANT": "prompt_a_json_only",
            "QWENPAW_VALIDATOR_VARIANT": "json_no_preamble_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["json_no_preamble_pass"] is True
    assert result["parsed_output_format"] == "json"
    assert "The user wants" not in result["sanitized_response_preview"]


def test_json_no_preamble_validator_rejects_extra_top_level_fields(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
        "debug_notes": "Internal diagnostics should not be returned.",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_VALIDATOR_VARIANT": "json_no_preamble_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_unqualified"
    assert result["qualification_failure_kind"] == "unexpected_fields"
    assert result["unexpected_fields"] == ["debug_notes"]
    assert result["json_no_preamble_pass"] is True
    assert result["parsed_output_format"] == "json"


def test_extra_top_level_fields_are_included_in_repair_prompt(monkeypatch, tmp_path):
    initial_advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
        "debug_notes": "Internal diagnostics should not be returned.",
    }
    repaired_advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop. Please follow staff guidance.",
        "safety_notes": "Advisory only. Organizer approval is required before any publication.",
    }
    request_texts = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        request_texts.append(payload["input"][0]["content"][0]["text"])
        advisory = initial_advisory if len(request_texts) == 1 else repaired_advisory
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": json.dumps(advisory)}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env=_live_smoke_env(
            QWENPAW_MAX_REPAIR_ATTEMPTS="1",
            QWENPAW_VALIDATOR_VARIANT="json_no_preamble_validator",
        ),
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["repair_attempt_count"] == 1
    assert len(request_texts) == 2
    repair_prompt = request_texts[1]
    assert '"unexpected_fields": ["debug_notes"]' in repair_prompt


def test_json_no_preamble_validator_rejects_preamble_wrapped_json(monkeypatch, tmp_path):
    advisory = {
        "recovery_rationale": "Route affected visitors away from the sold-out merchant.",
        "visitor_safe_notice_draft": "Some items may be unavailable at this stop.",
        "safety_notes": "Advisory only. Organizer approval is required.",
    }
    response_text = "Here is the advisory:\n" + json.dumps(advisory)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"message": {"content": response_text}},
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_VALIDATOR_VARIANT": "json_no_preamble_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_unqualified"
    assert result["qualification_failure_kind"] == "json_preamble_detected"
    assert result["json_no_preamble_pass"] is False


def test_strict_existing_validator_still_accepts_markdown_sections(monkeypatch, tmp_path):
    markdown = """### recovery_rationale
Route affected visitors away from the sold-out merchant.

### visitor_safe_notice_draft
Some items may be unavailable at this stop.

### safety_notes
Advisory only. Organizer approval is required.
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=f"data: {json.dumps({'output': markdown})}\n\n",
        )

    _set_temp_evidence_paths(monkeypatch, tmp_path)

    result = live_qwenpaw_smoke.run_smoke(
        env={
            "RUN_LIVE_QWENPAW_SMOKE": "1",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
            "QWENPAW_VALIDATOR_VARIANT": "strict_existing_validator",
        },
        transport=httpx.MockTransport(handler),
    )

    assert result["outcome"] == "advisory_qualified"
    assert result["validator_variant"] == "strict_existing_validator"
    assert result["parsed_output_format"] == "markdown"
