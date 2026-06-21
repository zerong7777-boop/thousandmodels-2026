import json
import os
from typing import Protocol

import httpx


class QwenProviderError(RuntimeError):
    pass


class QwenDraftProvider(Protocol):
    def complete_json(self, prompt_template_id: str, payload: dict) -> str:
        ...


class DashScopeQwenDraftProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model or os.getenv("QWEN_MODEL", "qwen-plus")
        self.timeout_seconds = timeout_seconds or float(os.getenv("QWEN_TIMEOUT_SECONDS", "30"))

    def complete_json(self, prompt_template_id: str, payload: dict) -> str:
        if not self.api_key:
            raise QwenProviderError("missing_provider_key")
        prompt_payload = json.dumps(
            {"template": prompt_template_id, "payload": payload},
            ensure_ascii=False,
            sort_keys=True,
        )
        response = httpx.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Return one JSON object only, with exactly these top-level keys: "
                            "content, locale, structured_payload, evidence_refs, safety_notes. "
                            "Do not wrap the object in agent_draft or any other key. "
                            "Do not include approval_status, publish_status, approved_at, "
                            "published_at, status_transition, plan_patch, approval actions, "
                            "publish actions, plan-version creation, inventory mutation, or "
                            "backend schema names in public copy."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt_payload,
                    },
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise QwenProviderError("malformed_provider_response") from exc
