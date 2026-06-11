from collections.abc import Callable
from time import perf_counter
from typing import Any

from app.schemas import AgentToolCall


class ToolRecorder:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.calls: list[AgentToolCall] = []
        self._counter = 0

    def call(
        self,
        step_id: str,
        tool_name: str,
        input_payload: dict,
        fn: Callable[[], Any],
    ) -> Any:
        self._counter += 1
        started = perf_counter()
        call_id = f"tool_{self.run_id}_{self._counter:03d}"
        try:
            result = fn()
        except Exception as exc:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self.calls.append(
                AgentToolCall(
                    tool_call_id=call_id,
                    run_id=self.run_id,
                    step_id=step_id,
                    tool_name=tool_name,
                    input_payload=input_payload,
                    output_payload={},
                    status="failed",
                    latency_ms=elapsed_ms,
                    error_summary=str(exc),
                )
            )
            raise
        elapsed_ms = int((perf_counter() - started) * 1000)
        self.calls.append(
            AgentToolCall(
                tool_call_id=call_id,
                run_id=self.run_id,
                step_id=step_id,
                tool_name=tool_name,
                input_payload=input_payload,
                output_payload={"result": result},
                status="success",
                latency_ms=elapsed_ms,
                error_summary=None,
            )
        )
        return result
