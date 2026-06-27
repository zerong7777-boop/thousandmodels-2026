from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable, TextIO
from urllib.parse import urljoin

import httpx


DEFAULT_ENDPOINTS = (
    ("health", "/api/health"),
    ("ready", "/api/ready"),
    ("public_event", "/api/public/events/demo-night-tour"),
)


@dataclass(frozen=True)
class SmokeResponse:
    status_code: int
    payload: dict[str, Any]


RequestJson = Callable[[str, str], SmokeResponse]


def request_json(base_url: str, path: str) -> SmokeResponse:
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    with httpx.Client(timeout=10, trust_env=False) as client:
        response = client.get(url)
    try:
        payload = response.json()
    except ValueError:
        payload = {"detail": "non-json response"}
    return SmokeResponse(status_code=response.status_code, payload=payload)


def run_smoke(
    base_url: str,
    *,
    request: RequestJson = request_json,
    output: TextIO = sys.stdout,
) -> int:
    all_ok = True
    for name, path in DEFAULT_ENDPOINTS:
        try:
            response = request(base_url, path)
        except Exception as exc:
            all_ok = False
            _write_result(
                output,
                name=name,
                path=path,
                ok=False,
                status_code=None,
                summary=f"request_error:{exc.__class__.__name__}",
            )
            continue
        ok = _endpoint_ok(name, response)
        all_ok = all_ok and ok
        _write_result(
            output,
            name=name,
            path=path,
            ok=ok,
            status_code=response.status_code,
            summary=_safe_summary(response.payload),
        )
    return 0 if all_ok else 1


def _safe_summary(payload: dict[str, Any]) -> str:
    status = payload.get("status")
    if isinstance(status, str):
        return status
    detail = payload.get("detail")
    if isinstance(detail, str):
        return detail[:80]
    return "json"


def _endpoint_ok(name: str, response: SmokeResponse) -> bool:
    if response.status_code != 200:
        return False
    if name == "health":
        return response.payload.get("status") == "ok"
    if name == "ready":
        return response.payload.get("status") == "ready"
    if name == "public_event":
        return response.payload.get("event_id") == "demo-night-tour"
    return True


def _write_result(
    output: TextIO,
    *,
    name: str,
    path: str,
    ok: bool,
    status_code: int | None,
    summary: str,
) -> None:
    output.write(
        json.dumps(
            {
                "endpoint": name,
                "path": path,
                "ok": ok,
                "status_code": status_code,
                "summary": summary,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deployment readiness smoke checks.")
    parser.add_argument("--base-url", required=True, help="API base URL, for example http://127.0.0.1:8000")
    args = parser.parse_args(argv)
    return run_smoke(args.base_url)


if __name__ == "__main__":
    raise SystemExit(main())
