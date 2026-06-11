import os

import httpx

from app.agents.deterministic import DeterministicAgentBackend
from app.schemas import EventBrief, MerchantProfile


class QwenAgentBackend(DeterministicAgentBackend):
    """Qwen adapter. Falls back to deterministic output if API use is unavailable."""

    def plan_event(self, brief: EventBrief, merchants: list[MerchantProfile]) -> dict:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        model = os.getenv("QWEN_MODEL", "qwen-plus")
        if not api_key:
            return super().plan_event(brief, merchants)

        prompt = {
            "event_brief": brief.model_dump(),
            "merchants": [merchant.model_dump() for merchant in merchants],
            "instruction": "Return one JSON object matching the EventPlan schema. Do not include markdown.",
        }
        try:
            response = httpx.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an event orchestration planner for Macau old districts.",
                        },
                        {"role": "user", "content": str(prompt)},
                    ],
                    "response_format": {"type": "json_object"},
                },
                timeout=30,
            )
            response.raise_for_status()
        except Exception:
            return super().plan_event(brief, merchants)

        # Keep deterministic output until strict schema parsing is separately verified.
        return super().plan_event(brief, merchants)
