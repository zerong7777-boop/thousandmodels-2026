from app.agents.deterministic import DeterministicAgentBackend
from app.agents.orchestrator import choose_agent_backend


def test_default_agent_backend_is_deterministic(monkeypatch):
    monkeypatch.delenv("AGENT_BACKEND", raising=False)
    backend = choose_agent_backend()
    assert isinstance(backend, DeterministicAgentBackend)


def test_unknown_agent_backend_falls_back_to_deterministic(monkeypatch):
    monkeypatch.setenv("AGENT_BACKEND", "unknown")
    backend = choose_agent_backend()
    assert isinstance(backend, DeterministicAgentBackend)
