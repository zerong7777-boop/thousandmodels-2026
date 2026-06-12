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
        response = httpx.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Return JSON only. Produce a controlled AgentDraft candidate. "
                            "Do not approve, publish, mutate inventory, create plan versions, "
                            "or include backend schema names in public copy."
                        ),
                    },
                    {
                        "role": "user",
                        "content": str({"template": prompt_template_id, "payload": payload}),
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
