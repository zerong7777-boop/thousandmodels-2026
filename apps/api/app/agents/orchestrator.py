import os

from app.agents.base import AgentBackend
from app.agents.deterministic import DeterministicAgentBackend
from app.agents.qwen_client import QwenAgentBackend


def choose_agent_backend() -> AgentBackend:
    backend = os.getenv("AGENT_BACKEND", "deterministic").lower()
    if backend == "qwen" and os.getenv("DASHSCOPE_API_KEY"):
        return QwenAgentBackend()
    return DeterministicAgentBackend()
