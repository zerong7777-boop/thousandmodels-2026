from typing import Protocol

from app.schemas import EventBrief, MerchantProfile


class AgentBackend(Protocol):
    def plan_event(self, brief: EventBrief, merchants: list[MerchantProfile]) -> dict:
        """Return data compatible with EventPlan."""
