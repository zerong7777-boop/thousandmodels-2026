from __future__ import annotations

import re
from collections import Counter
from threading import Lock


LABEL_SAFE_PATTERN = re.compile(r"[^A-Za-z0-9_.:-]+")


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._lock = Lock()

    def increment(self, name: str, labels: dict[str, str] | None = None) -> None:
        key = _counter_key(name, labels)
        with self._lock:
            self._counters[key] += 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(sorted(self._counters.items()))


def _counter_key(name: str, labels: dict[str, str] | None = None) -> str:
    safe_name = _safe_label(name)
    if not labels:
        return safe_name
    label_text = ",".join(
        f"{_safe_label(key)}={_safe_label(value)}"
        for key, value in sorted(labels.items())
    )
    return f"{safe_name}|{label_text}"


def _safe_label(value: str) -> str:
    normalized = LABEL_SAFE_PATTERN.sub("_", str(value).strip())
    return normalized[:64] or "unknown"


METRICS = MetricsRegistry()
