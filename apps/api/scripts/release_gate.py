from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, TextIO
from urllib.parse import urljoin

import httpx


DEFAULT_EVENT_ID = "demo-night-tour"
DEFAULT_ORIGIN = "http://127.0.0.1:5173"
ORGANIZER_USERNAME = "organizer.demo"
MERCHANT_USERNAME = "merchant.m001.demo"
DEMO_PASSWORD = "demo1234"
ANONYMOUS_INTERACTION_ID = "release-gate-anon"
FORBIDDEN_PUBLIC_TERMS = re.compile(
    r"AgentDraft|AgentRun|PlanVersion|RecoveryProposal|qwen|dashscope|schema_failed|approval_status",
    re.IGNORECASE,
)
SENSITIVE_TEXT = re.compile(
    r"\bBearer\s+[A-Za-z0-9._~+/=-]+|\b(token|password|secret)=([^\s,;]+)",
    re.IGNORECASE,
)
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/][^\s\"'`)]*")
POSIX_LOCAL_PATH = re.compile(r"/(users|home|var|tmp|private|mnt|volumes)/[^\s\"'`)]*", re.IGNORECASE)
REQUIRED_COUNTERS = (
    "health_checks_total",
    "auth_failures_total|reason=missing_session",
    "public_touchpoint_interactions_total",
    "public_coupon_claims_total",
    "public_coupon_redemptions_total",
    "review_reports_total",
)


@dataclass(frozen=True)
class GateResponse:
    status_code: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class GateStep:
    step: str
    ok: bool
    status_code: int | None
    summary: str


RequestJson = Callable[[str, str, str, dict[str, Any] | None, dict[str, str] | None], GateResponse]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the live API E2E release gate.")
    parser.add_argument("--base-url", required=True, help="API base URL, for example http://127.0.0.1:8000")
    parser.add_argument("--event-id", default=DEFAULT_EVENT_ID)
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def run_gate(
    base_url: str,
    *,
    event_id: str = DEFAULT_EVENT_ID,
    origin: str = DEFAULT_ORIGIN,
    request: RequestJson | None = None,
    output: TextIO = sys.stdout,
    evidence_path: Path | None = None,
) -> int:
    started = time.perf_counter()
    started_at = _now()
    steps: list[GateStep] = []
    failure: dict[str, Any] | None = None
    metrics_observed: dict[str, int] = {}
    client: httpx.Client | None = None
    if request is None:
        client = httpx.Client(timeout=10, trust_env=False)
        request = _http_request(client)

    def record(step: str, ok: bool, status_code: int | None, summary: str) -> bool:
        gate_step = GateStep(step=step, ok=bool(ok), status_code=status_code, summary=_redact(summary))
        steps.append(gate_step)
        _write_step(output, gate_step)
        return ok

    try:
        try:
            response = request(base_url, "GET", "/api/health", None, None)
        except Exception as exc:
            failure = _failure("health", f"request_error:{exc.__class__.__name__}")
            record("health", False, None, failure["summary"])
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)
        if not record("health", response.status_code == 200 and response.payload.get("status") == "ok", response.status_code, _safe_status(response)):
            failure = _failure("health", "expected status=ok")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        try:
            response = request(base_url, "GET", "/api/ready", None, None)
        except Exception as exc:
            failure = _failure("ready", f"request_error:{exc.__class__.__name__}")
            record("ready", False, None, failure["summary"])
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)
        if not record("ready", response.status_code == 200 and response.payload.get("status") == "ready", response.status_code, _safe_status(response)):
            failure = _failure("ready", "expected status=ready")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "GET", "/api/events", None, None)
        boundary_ok = response.status_code == 401 and _has_error_envelope(response.payload)
        if not record("unauthenticated_boundary", boundary_ok, response.status_code, _safe_error_summary(response)):
            failure = _failure("unauthenticated_boundary", "expected 401 error envelope")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        if not _login(base_url, request, origin, ORGANIZER_USERNAME, "organizer", record, "organizer_login"):
            failure = _failure("organizer_login", "organizer login failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "GET", "/api/auth/me", None, None)
        if not record("organizer_me", response.status_code == 200 and _role(response.payload) == "organizer", response.status_code, _safe_role_summary(response)):
            failure = _failure("organizer_me", "expected organizer role")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        if not _expect_event_id(base_url, request, origin, "seed_demo", "POST", "/api/events/demo/seed", event_id, record):
            failure = _failure("seed_demo", "seed failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/events/{event_id}/generate-plan", None, _mutation_headers(origin))
        if not record("generate_plan", response.status_code == 200 and response.payload.get("current_plan"), response.status_code, "plan_generated"):
            failure = _failure("generate_plan", "missing current_plan")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/events/{event_id}/plans/1/approve", None, _mutation_headers(origin))
        if not record("approve_plan", response.status_code == 200 and response.payload.get("status") == "approved", response.status_code, _safe_status(response)):
            failure = _failure("approve_plan", "plan v1 was not approved")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/events/{event_id}/event-page/draft", None, _mutation_headers(origin))
        if not record("draft_event_page", response.status_code == 200 and bool(response.payload.get("id")), response.status_code, "drafted"):
            failure = _failure("draft_event_page", "draft missing id")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/events/{event_id}/event-page/publish", None, _mutation_headers(origin))
        if not record("publish_event_page", response.status_code == 200 and bool(response.payload.get("id")), response.status_code, "published"):
            failure = _failure("publish_event_page", "publish missing id")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/events/{event_id}/merchant-edge-packages/generate", None, _mutation_headers(origin))
        package = _first_package(response.payload)
        ids = _package_ids(package)
        if not record("generate_merchant_edge_packages", response.status_code == 200 and ids is not None, response.status_code, "packages_generated"):
            failure = _failure("generate_merchant_edge_packages", "missing touchpoint or coupon ids")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)
        assert ids is not None
        touchpoint_id, coupon_rule_id = ids

        response = request(base_url, "GET", f"/api/public/events/{event_id}", None, None)
        public_ok = response.status_code == 200 and response.payload.get("event_page") and not _contains_forbidden_public_terms(response.payload)
        if not record("public_event_projection", bool(public_ok), response.status_code, "public_projection"):
            failure = _failure("public_event_projection", "missing event_page or leaked internal terms")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(
            base_url,
            "POST",
            f"/api/public/events/{event_id}/touchpoints/{touchpoint_id}/interactions",
            {"interaction_type": "scan", "source": "release_gate", "anonymous_interaction_id": ANONYMOUS_INTERACTION_ID},
            _mutation_headers(origin),
        )
        interaction_id = response.payload.get("interaction_id") or response.payload.get("id")
        if not record("public_touchpoint_interaction", response.status_code == 200 and isinstance(interaction_id, str), response.status_code, "scan_recorded"):
            failure = _failure("public_touchpoint_interaction", "scan failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(
            base_url,
            "POST",
            f"/api/public/events/{event_id}/coupons/{coupon_rule_id}/claim",
            {"anonymous_interaction_id": ANONYMOUS_INTERACTION_ID},
            _mutation_headers(origin),
        )
        redemption_id = response.payload.get("redemption_id") or response.payload.get("id")
        if not record("public_coupon_claim", response.status_code == 200 and isinstance(redemption_id, str), response.status_code, "coupon_claimed"):
            failure = _failure("public_coupon_claim", "claim failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/public/events/{event_id}/coupon-redemptions/{redemption_id}/redeem", None, _mutation_headers(origin))
        if not record("public_coupon_redeem", response.status_code == 200 and response.payload.get("status") == "redeemed", response.status_code, _safe_status(response)):
            failure = _failure("public_coupon_redeem", "redeem failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        if not _login(base_url, request, origin, MERCHANT_USERNAME, "merchant", record, "merchant_login"):
            failure = _failure("merchant_login", "merchant login failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "GET", f"/api/merchants/m001/workbench?event_id={event_id}", None, None)
        workbench_ok = response.status_code == 200 and bool(response.payload.get("interaction_package"))
        if not record("merchant_workbench", workbench_ok, response.status_code, "workbench_ready"):
            failure = _failure("merchant_workbench", "missing interaction package")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        if not _login(base_url, request, origin, ORGANIZER_USERNAME, "organizer", record, "organizer_relogin"):
            failure = _failure("organizer_relogin", "organizer relogin failed")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "POST", f"/api/events/{event_id}/review-report", None, _mutation_headers(origin))
        if not record("review_report", response.status_code == 200 and bool(response.payload.get("lessons_learned")), response.status_code, "review_ready"):
            failure = _failure("review_report", "missing lessons_learned")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        response = request(base_url, "GET", "/api/metrics", None, None)
        counters = response.payload.get("counters") if isinstance(response.payload, dict) else None
        metrics_observed = counters if isinstance(counters, dict) else {}
        missing = [name for name in REQUIRED_COUNTERS if not metrics_observed.get(name)]
        if not record("metrics", response.status_code == 200 and not missing, response.status_code, "metrics_ready" if not missing else f"missing:{','.join(missing)}"):
            failure = _failure("metrics", f"missing counters:{','.join(missing)}")
            return _finish(1, base_url, event_id, started, started_at, steps, metrics_observed, failure, evidence_path)

        return _finish(0, base_url, event_id, started, started_at, steps, metrics_observed, None, evidence_path)
    finally:
        if client is not None:
            client.close()


def _http_request(client: httpx.Client) -> RequestJson:
    def request(base_url: str, method: str, path: str, payload=None, headers=None) -> GateResponse:
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        if method == "GET":
            response = client.get(url, headers=headers)
        elif method == "POST":
            response = client.post(url, json=payload or {}, headers=headers)
        else:
            raise ValueError(f"unsupported method: {method}")
        try:
            response_payload = response.json()
        except ValueError:
            response_payload = {"error": {"message": "non-json response"}}
        if not isinstance(response_payload, dict):
            response_payload = {"value": response_payload}
        return GateResponse(status_code=response.status_code, payload=response_payload)

    return request


def _login(
    base_url: str,
    request: RequestJson,
    origin: str,
    username: str,
    role: str,
    record: Callable[[str, bool, int | None, str], bool],
    step: str,
) -> bool:
    response = request(
        base_url,
        "POST",
        "/api/auth/login",
        {"username": username, "password": DEMO_PASSWORD},
        _mutation_headers(origin),
    )
    return record(step, response.status_code == 200 and _role(response.payload) == role, response.status_code, _safe_role_summary(response))


def _expect_event_id(
    base_url: str,
    request: RequestJson,
    origin: str,
    step: str,
    method: str,
    path: str,
    event_id: str,
    record: Callable[[str, bool, int | None, str], bool],
) -> bool:
    response = request(base_url, method, path, None, _mutation_headers(origin))
    return record(step, response.status_code == 200 and response.payload.get("event_id") == event_id, response.status_code, _safe_status(response))


def _mutation_headers(origin: str) -> dict[str, str]:
    return {"origin": origin}


def _has_error_envelope(payload: dict[str, Any]) -> bool:
    error = payload.get("error")
    return isinstance(error, dict) and all(isinstance(error.get(key), str) for key in ("code", "message", "request_id"))


def _role(payload: dict[str, Any]) -> str | None:
    user = payload.get("user")
    if isinstance(user, dict):
        role = user.get("role")
        if isinstance(role, str):
            return role
    return None


def _first_package(payload: dict[str, Any]) -> dict[str, Any] | None:
    packages = payload.get("packages")
    if isinstance(packages, list) and packages and isinstance(packages[0], dict):
        return packages[0]
    return None


def _package_ids(package: dict[str, Any] | None) -> tuple[str, str] | None:
    if not package:
        return None
    touchpoints = package.get("touchpoints")
    coupon_rules = package.get("coupon_rules")
    if not isinstance(touchpoints, list) or not touchpoints or not isinstance(touchpoints[0], dict):
        return None
    if not isinstance(coupon_rules, list) or not coupon_rules or not isinstance(coupon_rules[0], dict):
        return None
    touchpoint_id = touchpoints[0].get("touchpoint_id") or touchpoints[0].get("id")
    coupon_rule_id = coupon_rules[0].get("coupon_rule_id") or coupon_rules[0].get("id")
    if isinstance(touchpoint_id, str) and isinstance(coupon_rule_id, str):
        return touchpoint_id, coupon_rule_id
    return None


def _contains_forbidden_public_terms(payload: dict[str, Any]) -> bool:
    return FORBIDDEN_PUBLIC_TERMS.search(json.dumps(payload, ensure_ascii=False)) is not None


def _safe_status(response: GateResponse) -> str:
    status = response.payload.get("status")
    if isinstance(status, str):
        return status
    error = response.payload.get("error")
    if isinstance(error, dict) and isinstance(error.get("message"), str):
        return str(error["message"])[:80]
    return "json"


def _safe_error_summary(response: GateResponse) -> str:
    error = response.payload.get("error")
    if isinstance(error, dict):
        code = error.get("code")
        if isinstance(code, str):
            return code
    return _safe_status(response)


def _safe_role_summary(response: GateResponse) -> str:
    role = _role(response.payload)
    return role or _safe_status(response)


def _failure(step: str, summary: str) -> dict[str, str]:
    return {"step": step, "summary": _redact(summary)}


def _finish(
    exit_code: int,
    base_url: str,
    event_id: str,
    started: float,
    started_at: str,
    steps: list[GateStep],
    metrics_observed: dict[str, int],
    failure: dict[str, str] | None,
    evidence_path: Path | None,
) -> int:
    if evidence_path:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        finished_at = _now()
        evidence = {
            "status": "passed" if exit_code == 0 else "failed",
            "base_url": base_url,
            "event_id": event_id,
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "steps": [step.__dict__ for step in steps],
            "metrics_observed": metrics_observed,
        }
        if failure:
            evidence["failure"] = failure
        evidence_path.write_text(json.dumps(_sanitize_value(evidence), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return exit_code


def _write_step(output: TextIO, step: GateStep) -> None:
    output.write(json.dumps(_sanitize_value(step.__dict__), ensure_ascii=False, sort_keys=True) + "\n")


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _redact(value)
    if isinstance(value, dict):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


def _redact(value: str) -> str:
    sanitized = value.replace(DEMO_PASSWORD, "[redacted]")
    sanitized = SENSITIVE_TEXT.sub(lambda match: f"{match.group(1)}=[redacted]" if match.group(1) else "Bearer [redacted]", sanitized)
    sanitized = WINDOWS_ABSOLUTE_PATH.sub("[redacted]", sanitized)
    sanitized = POSIX_LOCAL_PATH.sub("[redacted]", sanitized)
    return sanitized


def _now() -> str:
    return datetime.now(UTC).isoformat()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run_gate(args.base_url, event_id=args.event_id, origin=args.origin, evidence_path=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
