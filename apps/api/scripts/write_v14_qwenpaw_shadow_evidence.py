from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_PATH = (
    PROJECT_ROOT
    / "docs"
    / "research"
    / "assets"
    / "v1.4-qwenpaw-orchestration-spike"
    / "shadow-run-evidence.json"
)
MUTATION_HEADERS = {"origin": "http://127.0.0.1:5173"}
_TEMP_DB_DIR = tempfile.TemporaryDirectory(prefix="zhiyin-v14-qwenpaw-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEMP_DB_DIR.name) / 'shadow.sqlite3'}"

from fastapi.testclient import TestClient

from app.main import app
from app.store import STORE
from scripts.reset_demo_state import reset_demo_state


def login_as(client: TestClient, username: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "demo1234"},
        headers=MUTATION_HEADERS,
    )
    response.raise_for_status()


def prepare_shadow_scenario(client: TestClient) -> str:
    reset_demo_state(event_id="demo-night-tour")
    login_as(client, "organizer.demo")
    client.post("/api/events/demo-night-tour/generate-plan", headers=MUTATION_HEADERS).raise_for_status()
    client.post("/api/events/demo-night-tour/plans/1/approve", headers=MUTATION_HEADERS).raise_for_status()
    client.post("/api/events/demo-night-tour/event-page/draft", headers=MUTATION_HEADERS).raise_for_status()
    client.post("/api/events/demo-night-tour/event-page/publish", headers=MUTATION_HEADERS).raise_for_status()
    client.post(
        "/api/events/demo-night-tour/merchant-edge-packages/generate",
        headers=MUTATION_HEADERS,
    ).raise_for_status()
    login_as(client, "merchant.m001.demo")
    client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "normal",
            "available_for_visitors": False,
            "temporary_note": "Sold out during v1.4 evidence generation.",
        },
        headers=MUTATION_HEADERS,
    ).raise_for_status()
    return STORE.list_incidents("demo-night-tour")[-1].incident_id


def build_evidence() -> dict:
    with TestClient(app) as client:
        incident_id = prepare_shadow_scenario(client)
        login_as(client, "organizer.demo")
        response = client.post(
            "/api/events/demo-night-tour/qwenpaw-shadow-orchestration/run",
            json={"incident_id": incident_id},
            headers=MUTATION_HEADERS,
        )
        response.raise_for_status()
        payload = response.json()

    denied = [
        decision
        for decision in payload["permission_decisions"]
        if not decision.get("allowed")
    ]
    return {
        "outcome": "shadow_success",
        "event_id": "demo-night-tour",
        "backend": "qwenpaw_fake",
        "agent_run_mode": payload["agent_run"]["mode"],
        "authoritative_mutation": payload["advisory_bundle"].get("authoritative_mutation"),
        "human_approval_required": payload["advisory_bundle"].get("human_approval_required"),
        "permission_decision_count": len(payload["permission_decisions"]),
        "denied_permission_count": len(denied),
        "agent_run": payload["agent_run"],
        "advisory_bundle": payload["advisory_bundle"],
        "permission_decisions": payload["permission_decisions"],
    }


def main() -> int:
    try:
        evidence = build_evidence()
        EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE_PATH.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "written", "path": str(EVIDENCE_PATH.relative_to(PROJECT_ROOT))}, indent=2))
        return 0
    finally:
        STORE.conn.close()
        _TEMP_DB_DIR.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
