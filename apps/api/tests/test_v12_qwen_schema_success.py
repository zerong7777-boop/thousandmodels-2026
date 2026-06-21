from app.agents import draft_generation


def test_qwen_candidate_parser_accepts_nested_agent_draft_wrapper():
    result = draft_generation.parse_qwen_candidate(
        '{"agent_draft":{"content":"Use the backup route.","locale":"en",'
        '"structured_payload":{"reason":"inventory pressure"},'
        '"evidence_refs":["incident:i001"],'
        '"safety_notes":["operator approval required"]}}'
    )

    assert result.response_status == "success", result.error_summary
    assert result.candidate is not None
    assert result.candidate.content == "Use the backup route."
    assert result.candidate.structured_payload["reason"] == "inventory pressure"
    assert result.candidate.evidence_refs == ["incident:i001"]


def test_qwen_prompt_payload_sanitizer_removes_mutation_fields_recursively():
    assert hasattr(
        draft_generation, "sanitize_qwen_prompt_payload"
    ), "sanitize_qwen_prompt_payload must be implemented for Qwen prompt payloads"

    sanitized = draft_generation.sanitize_qwen_prompt_payload(
        {
            "proposal_id": "rp1",
            "approval_status": "pending",
            "plan_patch": {"route": ["a", "b"]},
            "public_copy": "Route adjusted.",
            "nested": {
                "publish_status": "draft",
                "approved_at": "2026-06-12T10:00:00Z",
                "safe": "kept",
                "items": [
                    {"status_transition": "publish", "safe_child": "kept"},
                    {"published_at": "2026-06-12T10:05:00Z", "count": 2},
                ],
            },
        }
    )

    sanitized_text = str(sanitized)
    assert "approval_status" not in sanitized_text
    assert "plan_patch" not in sanitized_text
    assert "publish_status" not in sanitized_text
    assert "approved_at" not in sanitized_text
    assert "status_transition" not in sanitized_text
    assert "published_at" not in sanitized_text
    assert sanitized["proposal_id"] == "rp1"
    assert sanitized["public_copy"] == "Route adjusted."
    assert sanitized["nested"]["safe"] == "kept"
    assert sanitized["nested"]["items"][0]["safe_child"] == "kept"
    assert sanitized["nested"]["items"][1]["count"] == 2


def test_qwen_prompt_payload_sanitizer_removes_merchant_task_patch_without_mutation():
    payload = {
        "proposal_id": "rp1",
        "approved_by": "organizer.demo",
        "inventory_status": "sold_out",
        "queue_status": "busy",
        "available_for_visitors": False,
        "nested": [
            {
                "merchant_task_patch": {"merchant_id": "m001", "task": "pause"},
                "public_copy": "Please use the backup stop.",
            }
        ],
    }

    sanitized = draft_generation.sanitize_qwen_prompt_payload(payload)

    assert "approved_by" not in sanitized
    assert "merchant_task_patch" not in sanitized["nested"][0]
    assert sanitized["inventory_status"] == "sold_out"
    assert sanitized["queue_status"] == "busy"
    assert sanitized["available_for_visitors"] is False
    assert payload["approved_by"] == "organizer.demo"
    assert payload["nested"][0]["merchant_task_patch"] == {
        "merchant_id": "m001",
        "task": "pause",
    }


def test_qwen_candidate_parser_rejects_unsafe_fields_inside_agent_draft_wrapper():
    result = draft_generation.parse_qwen_candidate(
        '{"agent_draft":{"content":"Use the backup route.","locale":"en",'
        '"structured_payload":{"merchant_task_patch":{"merchant_id":"m001"}},'
        '"evidence_refs":["incident:i001"],'
        '"safety_notes":[]}}'
    )

    assert result.candidate is None
    assert result.response_status == "schema_failed"
    assert "unsafe mutation fields" in result.error_summary
