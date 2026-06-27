import io
import json

from scripts import release_gate
from scripts.release_gate import GateResponse


EVENT_ID = "demo-night-tour"


class FakeGateApi:
    def __init__(
        self,
        *,
        ready_status: str = "ready",
        public_leak: bool = False,
        include_metrics: bool = True,
        request_error: bool = False,
    ) -> None:
        self.ready_status = ready_status
        self.public_leak = public_leak
        self.include_metrics = include_metrics
        self.request_error = request_error
        self.role: str | None = None
        self.touchpoint_id = "tp_gate_m001"
        self.coupon_rule_id = "coupon_gate_m001"
        self.redemption_id = "red_gate_m001"

    def request(self, _base_url: str, method: str, path: str, payload=None, headers=None) -> GateResponse:
        if self.request_error and path == "/api/ready":
            raise RuntimeError("boom with Bearer secret-token")
        if method == "GET" and path == "/api/health":
            return GateResponse(200, {"status": "ok"})
        if method == "GET" and path == "/api/ready":
            return GateResponse(200, {"status": self.ready_status})
        if method == "GET" and path == "/api/events":
            if self.role != "organizer":
                return GateResponse(401, {"error": {"code": "http_401", "message": "not authenticated", "request_id": "req_gate"}})
            return GateResponse(200, [{"event_id": EVENT_ID}])
        if method == "POST" and path == "/api/auth/login":
            username = (payload or {}).get("username")
            if username == "organizer.demo":
                self.role = "organizer"
                return GateResponse(200, {"user": {"role": "organizer", "username": username}})
            if username == "merchant.m001.demo":
                self.role = "merchant"
                return GateResponse(200, {"user": {"role": "merchant", "username": username, "merchant_id": "m001"}})
            return GateResponse(401, {"error": {"message": "invalid credentials"}})
        if method == "GET" and path == "/api/auth/me":
            return GateResponse(200, {"user": {"role": self.role, "username": f"{self.role}.demo"}})
        if method == "POST" and path == "/api/events/demo/seed":
            return GateResponse(200, {"status": "seeded", "event_id": EVENT_ID})
        if method == "POST" and path == f"/api/events/{EVENT_ID}/generate-plan":
            return GateResponse(200, {"approval_status": "draft", "current_plan": {"version": 1, "status": "draft"}})
        if method == "POST" and path == f"/api/events/{EVENT_ID}/plans/1/approve":
            return GateResponse(200, {"version": 1, "status": "approved"})
        if method == "POST" and path == f"/api/events/{EVENT_ID}/event-page/draft":
            return GateResponse(200, {"id": "page_gate", "publication_status": "draft"})
        if method == "POST" and path == f"/api/events/{EVENT_ID}/event-page/publish":
            return GateResponse(200, {"id": "page_gate", "publication_status": "published"})
        if method == "POST" and path == f"/api/events/{EVENT_ID}/merchant-edge-packages/generate":
            return GateResponse(200, {"packages": [_package_payload(self.touchpoint_id, self.coupon_rule_id)]})
        if method == "GET" and path == f"/api/public/events/{EVENT_ID}":
            if self.public_leak:
                return GateResponse(200, {"event_id": EVENT_ID, "event_page": {}, "copy": "AgentRun leaked"})
            return GateResponse(
                200,
                {
                    "event_id": EVENT_ID,
                    "current_plan_version": 1,
                    "event_page": {"title": "Visitor event page"},
                    "merchant_highlights": [{"merchant_id": "m001"}],
                },
            )
        if method == "POST" and path == f"/api/public/events/{EVENT_ID}/touchpoints/{self.touchpoint_id}/interactions":
            return GateResponse(200, {"id": "int_gate", "anonymous_interaction_id": "anon_gate"})
        if method == "POST" and path == f"/api/public/events/{EVENT_ID}/coupons/{self.coupon_rule_id}/claim":
            return GateResponse(200, {"id": self.redemption_id, "status": "claimed"})
        if method == "POST" and path == f"/api/public/events/{EVENT_ID}/coupon-redemptions/{self.redemption_id}/redeem":
            return GateResponse(200, {"redemption_id": self.redemption_id, "status": "redeemed"})
        if method == "GET" and path == f"/api/merchants/m001/workbench?event_id={EVENT_ID}":
            return GateResponse(200, {"merchant_id": "m001", "interaction_package": _package_payload(self.touchpoint_id, self.coupon_rule_id)})
        if method == "POST" and path == f"/api/events/{EVENT_ID}/review-report":
            return GateResponse(200, {"lessons_learned": ["Touchpoints worked"], "agent_run": {"status": "completed"}})
        if method == "GET" and path == "/api/metrics":
            counters = {"health_checks_total": 1}
            if self.include_metrics:
                counters.update(
                    {
                        "auth_failures_total|reason=missing_session": 1,
                        "public_touchpoint_interactions_total": 1,
                        "public_coupon_claims_total": 1,
                        "public_coupon_redemptions_total": 1,
                        "review_reports_total": 1,
                    }
                )
            return GateResponse(200, {"scope": "process", "counters": counters})
        return GateResponse(404, {"error": {"message": f"unexpected {method} {path}"}})


def _package_payload(touchpoint_id: str, coupon_rule_id: str) -> dict:
    return {
        "merchant_id": "m001",
        "touchpoints": [{"id": touchpoint_id}],
        "coupon_rules": [{"id": coupon_rule_id}],
    }


def _json_lines(output: io.StringIO) -> list[dict]:
    return [json.loads(line) for line in output.getvalue().splitlines()]


def test_release_gate_success_outputs_jsonl_and_evidence(tmp_path):
    output = io.StringIO()
    evidence_path = tmp_path / "release-gate-result.json"

    exit_code = release_gate.run_gate(
        "http://api.example",
        request=FakeGateApi().request,
        output=output,
        evidence_path=evidence_path,
    )

    assert exit_code == 0
    lines = _json_lines(output)
    assert [line["step"] for line in lines] == [
        "health",
        "ready",
        "unauthenticated_boundary",
        "organizer_login",
        "organizer_me",
        "seed_demo",
        "generate_plan",
        "approve_plan",
        "draft_event_page",
        "publish_event_page",
        "generate_merchant_edge_packages",
        "public_event_projection",
        "public_touchpoint_interaction",
        "public_coupon_claim",
        "public_coupon_redeem",
        "merchant_login",
        "merchant_workbench",
        "organizer_relogin",
        "review_report",
        "metrics",
    ]
    assert all(line["ok"] for line in lines)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["status"] == "passed"
    assert evidence["base_url"] == "http://api.example"
    assert evidence["event_id"] == EVENT_ID
    serialized = output.getvalue() + json.dumps(evidence)
    assert "demo1234" not in serialized
    assert "zhiyin_session" not in serialized
    assert "Bearer" not in serialized


def test_release_gate_ready_not_ready_fails(tmp_path):
    output = io.StringIO()
    evidence_path = tmp_path / "failed.json"

    exit_code = release_gate.run_gate(
        "http://api.example",
        request=FakeGateApi(ready_status="not_ready").request,
        output=output,
        evidence_path=evidence_path,
    )

    assert exit_code == 1
    lines = _json_lines(output)
    assert lines[-1]["step"] == "ready"
    assert lines[-1]["ok"] is False
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["status"] == "failed"
    assert evidence["failure"]["step"] == "ready"


def test_release_gate_public_internal_term_leak_fails():
    output = io.StringIO()

    exit_code = release_gate.run_gate(
        "http://api.example",
        request=FakeGateApi(public_leak=True).request,
        output=output,
    )

    assert exit_code == 1
    assert _json_lines(output)[-1]["step"] == "public_event_projection"


def test_release_gate_missing_metrics_fail():
    output = io.StringIO()

    exit_code = release_gate.run_gate(
        "http://api.example",
        request=FakeGateApi(include_metrics=False).request,
        output=output,
    )

    assert exit_code == 1
    assert _json_lines(output)[-1]["step"] == "metrics"


def test_release_gate_request_error_redacts_summary():
    output = io.StringIO()

    exit_code = release_gate.run_gate(
        "http://api.example",
        request=FakeGateApi(request_error=True).request,
        output=output,
    )

    assert exit_code == 1
    assert "RuntimeError" in output.getvalue()
    assert "secret-token" not in output.getvalue()


def test_parse_args_defaults():
    args = release_gate.parse_args(["--base-url", "http://127.0.0.1:8000"])

    assert args.base_url == "http://127.0.0.1:8000"
    assert args.event_id == EVENT_ID
    assert args.origin == "http://127.0.0.1:5173"
    assert args.output is None
