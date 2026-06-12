from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed_demo_accounts
from app.store import STORE


ACCEPTED_MODEL_STATUSES = {
    "skipped",
    "success",
    "invalid_json",
    "schema_failed",
    "provider_error",
}
MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
REPO_ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = REPO_ROOT / "docs" / "research" / "assets" / "v1.1-live-qwen-smoke"
RESULT_JSON = ASSET_DIR / "live-qwen-smoke-result.json"
SMOKE_DOC = REPO_ROOT / "docs" / "research" / "v1.1-live-qwen-smoke.md"
EVENT_ID = "demo-night-tour"


class LiveSmokeConfigError(RuntimeError):
    pass


def _redact_secret_like(value: Any) -> Any:
    if isinstance(value, str):
        redacted = re.sub(r"Authorization:\s*Bearer\s+\S+", "[redacted]", value, flags=re.IGNORECASE)
        redacted = re.sub(r"Bearer\s+sk-[A-Za-z0-9._-]+", "Bearer [redacted]", redacted)
        redacted = re.sub(r"sk-[A-Za-z0-9._-]+", "[redacted]", redacted)
        return redacted
    if isinstance(value, list):
        return [_redact_secret_like(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact_secret_like(item) for key, item in value.items()}
    return value


def require_live_qwen_env(env: dict[str, str] | None = None) -> dict[str, str]:
    source = os.environ if env is None else env
    if source.get("RUN_LIVE_QWEN_SMOKE") != "1":
        raise LiveSmokeConfigError("RUN_LIVE_QWEN_SMOKE must be exactly 1")
    if source.get("AGENT_DRAFT_BACKEND") != "qwen":
        raise LiveSmokeConfigError("AGENT_DRAFT_BACKEND=qwen is required")
    if not source.get("DASHSCOPE_API_KEY"):
        raise LiveSmokeConfigError("DASHSCOPE_API_KEY is required")
    return {
        "agent_draft_backend": "qwen",
        "qwen_model": source.get("QWEN_MODEL", "qwen-plus"),
        "qwen_timeout_seconds": source.get("QWEN_TIMEOUT_SECONDS", "30"),
    }


def sanitize_model_call(call: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "model_call_id",
        "run_id",
        "provider",
        "model",
        "prompt_template_id",
        "input_refs",
        "response_status",
        "fallback_used",
        "error_summary",
        "created_at",
    }
    return {key: _redact_secret_like(call[key]) for key in allowed if key in call}


def has_live_success(result: dict[str, Any]) -> bool:
    for section_name in ("recovery", "review"):
        for call in result.get(section_name, {}).get("model_calls", []):
            if call.get("response_status") == "success" and call.get("fallback_used") is False:
                return True
    return False


def reset_demo_state() -> None:
    STORE.clear_demo()
    if hasattr(STORE, "clear_auth_for_tests"):
        STORE.clear_auth_for_tests()
    if hasattr(STORE, "ensure_auth_schema"):
        STORE.ensure_auth_schema()
    seed_demo_accounts(STORE)


def login_as(client: TestClient, username: str, password: str = "demo1234") -> dict[str, Any]:
    return post_json(
        client,
        "/api/auth/login",
        {"username": username, "password": password},
    )


def post_json(client: TestClient, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = client.post(path, json=payload, headers=MUTATION_HEADERS)
    response.raise_for_status()
    return response.json()


def get_json(client: TestClient, path: str) -> dict[str, Any] | list[dict[str, Any]]:
    response = client.get(path)
    response.raise_for_status()
    return response.json()


def prepare_active_event(client: TestClient) -> dict[str, Any]:
    login_as(client, "organizer.demo")
    post_json(client, "/api/events/demo/seed")
    plan = post_json(client, f"/api/events/{EVENT_ID}/generate-plan")
    approved_plan = post_json(client, f"/api/events/{EVENT_ID}/plans/1/approve")
    return {"plan": plan, "approved_plan": approved_plan}


def report_sold_out(client: TestClient) -> dict[str, Any]:
    login_as(client, "merchant.m001.demo")
    return post_json(
        client,
        "/api/merchants/m001/runtime-state",
        {
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "sold out during guarded live qwen smoke",
        },
    )


def approve_first_recovery(client: TestClient) -> dict[str, Any]:
    login_as(client, "organizer.demo")
    incidents = get_json(client, f"/api/events/{EVENT_ID}/incidents")
    if not incidents:
        raise RuntimeError("no incidents available for recovery approval")
    proposal = post_json(
        client,
        f"/api/events/{EVENT_ID}/incidents/{incidents[0]['incident_id']}/recovery-proposals",
    )
    approved = post_json(
        client,
        f"/api/events/{EVENT_ID}/recovery-proposals/{proposal['proposal_id']}/approve",
    )
    return {"incident": incidents[0], "proposal": proposal, "approval": approved}


def sanitize_evaluation(evaluation: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "evaluation_id",
        "run_id",
        "schema_pass",
        "fallback_used",
        "unsafe_mutation_attempted",
        "human_approval_required",
        "forbidden_public_terms_present",
        "public_copy_ready",
        "notes",
    }
    return {key: evaluation[key] for key in allowed if key in evaluation}


def sanitize_draft(draft: dict[str, Any]) -> dict[str, Any]:
    content = draft.get("content") or ""
    return {
        "draft_id": draft.get("draft_id"),
        "source_run_id": draft.get("source_run_id"),
        "draft_type": draft.get("draft_type"),
        "locale": draft.get("locale"),
        "status": draft.get("status"),
        "content_preview": content[:160],
        "structured_payload_keys": sorted((draft.get("structured_payload") or {}).keys()),
        "created_at": draft.get("created_at"),
    }


def sanitize_run(run: dict[str, Any] | None) -> dict[str, Any]:
    if not run:
        return {}
    allowed = {
        "run_id",
        "event_id",
        "trigger",
        "mode",
        "status",
        "started_at",
        "completed_at",
        "fallback_used",
        "fallback_reason",
        "final_output_ref",
        "error_summary",
    }
    return {key: run[key] for key in allowed if key in run}


def collect_run_evidence(
    client: TestClient,
    run: dict[str, Any] | None,
    draft_type: str,
) -> dict[str, Any]:
    if not run:
        return {"run": {}, "model_calls": [], "evaluations": [], "drafts": []}
    login_as(client, "organizer.demo")
    run_id = run["run_id"]
    model_calls = get_json(client, f"/api/events/{EVENT_ID}/agent-runs/{run_id}/model-calls")
    evaluations = get_json(client, f"/api/events/{EVENT_ID}/agent-runs/{run_id}/evaluations")
    drafts = get_json(client, f"/api/events/{EVENT_ID}/agent-drafts?draft_type={draft_type}")
    run_drafts = [draft for draft in drafts if draft.get("source_run_id") == run_id]
    return {
        "run": sanitize_run(run),
        "model_calls": [sanitize_model_call(call) for call in model_calls],
        "evaluations": [sanitize_evaluation(evaluation) for evaluation in evaluations],
        "drafts": [sanitize_draft(draft) for draft in run_drafts],
    }


def summarize_public_projection(public_event: dict[str, Any]) -> dict[str, Any]:
    notices = public_event.get("public_notices", public_event.get("notices", []))
    return {
        "event_id": public_event.get("event_id"),
        "current_plan_version": public_event.get("current_plan_version"),
        "notice_count": len(notices),
    }


def run_deterministic_fallback_probe() -> dict[str, Any]:
    previous_key = os.environ.pop("DASHSCOPE_API_KEY", None)
    previous_backend = os.environ.get("AGENT_DRAFT_BACKEND")
    os.environ["AGENT_DRAFT_BACKEND"] = "deterministic"
    try:
        reset_demo_state()
        with TestClient(app) as client:
            prepare_active_event(client)
            sold_out = report_sold_out(client)
        run = sold_out.get("agent_run") or {}
        return {
            "agent_run_mode": run.get("mode"),
            "agent_run_status": run.get("status"),
            "fallback_used": run.get("fallback_used"),
        }
    finally:
        if previous_key is None:
            os.environ.pop("DASHSCOPE_API_KEY", None)
        else:
            os.environ["DASHSCOPE_API_KEY"] = previous_key
        if previous_backend is None:
            os.environ.pop("AGENT_DRAFT_BACKEND", None)
        else:
            os.environ["AGENT_DRAFT_BACKEND"] = previous_backend


def validate_model_statuses(result: dict[str, Any]) -> None:
    statuses = {
        call.get("response_status")
        for section_name in ("recovery", "review")
        for call in result.get(section_name, {}).get("model_calls", [])
    }
    unexpected = statuses - ACCEPTED_MODEL_STATUSES
    if unexpected:
        raise RuntimeError(f"unexpected model call statuses: {sorted(unexpected)}")


def run_live_smoke() -> dict[str, Any]:
    config = require_live_qwen_env()
    reset_demo_state()
    with TestClient(app) as client:
        prepare_active_event(client)
        sold_out = report_sold_out(client)
        recovery = collect_run_evidence(client, sold_out.get("agent_run"), "public_notice")
        approval = approve_first_recovery(client)
        login_as(client, "organizer.demo")
        review_report = post_json(client, f"/api/events/{EVENT_ID}/review-report")
        review = collect_run_evidence(client, review_report.get("agent_run"), "review_summary")
        public_projection = summarize_public_projection(
            get_json(client, f"/api/public/events/{EVENT_ID}")
        )

    result = {
        "date": datetime.now(UTC).date().isoformat(),
        "config": config,
        "outcome": "pending",
        "recovery": recovery,
        "recovery_approval": {
            "proposal_id": approval["proposal"].get("proposal_id"),
            "current_plan_version": approval["approval"].get("current_plan", {}).get("version"),
            "notice_id": approval["approval"].get("notice", {}).get("notice_id"),
        },
        "review": review,
        "public_projection": public_projection,
        "deterministic_fallback_probe": run_deterministic_fallback_probe(),
        "secret_policy": "No API key, Authorization header, or raw provider payload is stored.",
    }
    result["outcome"] = (
        "live_success" if has_live_success(result) else "live_completed_without_success_model_call"
    )
    validate_model_statuses(result)
    return result


def blocked_result(reason: str) -> dict[str, Any]:
    return {
        "date": datetime.now(UTC).date().isoformat(),
        "config": {
            "agent_draft_backend": os.environ.get("AGENT_DRAFT_BACKEND"),
            "qwen_model": os.environ.get("QWEN_MODEL", "qwen-plus"),
            "qwen_timeout_seconds": os.environ.get("QWEN_TIMEOUT_SECONDS", "30"),
        },
        "outcome": "blocked",
        "blocked_reason": reason,
        "recovery": {"run": {}, "model_calls": [], "evaluations": [], "drafts": []},
        "review": {"run": {}, "model_calls": [], "evaluations": [], "drafts": []},
        "public_projection": {},
        "deterministic_fallback_probe": run_deterministic_fallback_probe(),
        "secret_policy": "No API key, Authorization header, or raw provider payload is stored.",
    }


def render_markdown(result: dict[str, Any]) -> str:
    safe_recovery_calls = [
        sanitize_model_call(call) for call in result.get("recovery", {}).get("model_calls", [])
    ]
    safe_review_calls = [
        sanitize_model_call(call) for call in result.get("review", {}).get("model_calls", [])
    ]
    lines = [
        "# v1.1 Live Qwen Smoke",
        "",
        "## Evaluation Summary",
        "",
        f"- Date: {result.get('date', '')}",
        f"- Outcome: {result.get('outcome', '')}",
        f"- Agent draft backend: {result.get('config', {}).get('agent_draft_backend', '')}",
        f"- Qwen model: {result.get('config', {}).get('qwen_model', '')}",
        f"- Timeout seconds: {result.get('config', {}).get('qwen_timeout_seconds', '')}",
        f"- Secret policy: {result.get('secret_policy', 'No API key, Authorization header, or raw provider payload is stored.')}",
        "",
        "## Model Calls",
        "",
        "| Phase | Call ID | Run ID | Provider | Model | Prompt | Status | Fallback | Error |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for phase, calls in (("recovery", safe_recovery_calls), ("review", safe_review_calls)):
        if not calls:
            lines.append(f"| {phase} | none |  |  |  |  |  |  |  |")
            continue
        for call in calls:
            lines.append(
                "| {phase} | {call_id} | {run_id} | {provider} | {model} | {prompt} | {status} | {fallback} | {error} |".format(
                    phase=phase,
                    call_id=call.get("model_call_id", ""),
                    run_id=call.get("run_id", ""),
                    provider=call.get("provider", ""),
                    model=call.get("model", ""),
                    prompt=call.get("prompt_template_id", ""),
                    status=call.get("response_status", ""),
                    fallback=call.get("fallback_used", ""),
                    error=call.get("error_summary") or "",
                )
            )
    recovery_drafts = result.get("recovery", {}).get("drafts", [])
    review_drafts = result.get("review", {}).get("drafts", [])
    projection = result.get("public_projection", {})
    fallback_probe = result.get("deterministic_fallback_probe", {})
    lines.extend(
        [
            "",
            "## Draft Counts",
            "",
            f"- Recovery public notice drafts: {len(recovery_drafts)}",
            f"- Review summary drafts: {len(review_drafts)}",
            "",
            "## Public Projection",
            "",
            f"- Current plan version: {projection.get('current_plan_version', '')}",
            f"- Notice count: {projection.get('notice_count', '')}",
            "",
            "## Deterministic Fallback Probe",
            "",
            f"- Agent run mode: {fallback_probe.get('agent_run_mode', '')}",
            f"- Agent run status: {fallback_probe.get('agent_run_status', '')}",
            f"- Fallback used: {fallback_probe.get('fallback_used', '')}",
            "",
            "## Non-Claims",
            "",
            "- This smoke result is manual evidence, not an automated unit test.",
            "- It does not claim live DashScope availability unless a non-fallback success model call is present.",
            "- No API key, Authorization header, or raw provider payload is stored.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts(result: dict[str, Any]) -> dict[str, str]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    SMOKE_DOC.parent.mkdir(parents=True, exist_ok=True)
    SMOKE_DOC.write_text(render_markdown(result), encoding="utf-8")
    return {"json": str(RESULT_JSON), "markdown": str(SMOKE_DOC)}


def main() -> int:
    try:
        result = run_live_smoke()
        exit_code = 0
    except LiveSmokeConfigError as exc:
        result = blocked_result(str(exc))
        exit_code = 2
    paths = write_artifacts(result)
    print(f"status={result.get('outcome')}")
    print(f"json={paths['json']}")
    print(f"markdown={paths['markdown']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
