import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.schemas import (
    AgentDraft,
    AgentEvaluation,
    AgentModelCall,
    AgentRun,
    AgentToolCall,
    AgentTrace,
    AuthSessionRecord,
    AuthUserRecord,
    AuditLog,
    EventBrief,
    EventPlan,
    EventSummary,
    Incident,
    MerchantExecutionPack,
    MerchantProfile,
    MerchantRuntimeState,
    MerchantTask,
    OperationalMetric,
    PlanVersion,
    PublicNotice,
    RecoveryAction,
    RecoveryProposal,
    ReviewReport,
    RoutePoint,
)

T = TypeVar("T", bound=BaseModel)


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def database_path_from_env() -> Path:
    raw = os.getenv("DATABASE_URL", "sqlite:///./data/runtime/zhiyin.sqlite3")
    if raw.startswith("sqlite:///"):
        raw = raw.removeprefix("sqlite:///")
    path = Path(raw)
    if not path.is_absolute():
        path = project_root() / path
    return path


class MVPStore:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else database_path_from_env()
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
              collection TEXT NOT NULL,
              item_key TEXT NOT NULL,
              payload TEXT NOT NULL,
              PRIMARY KEY (collection, item_key)
            )
            """
        )
        self.ensure_auth_schema()
        self.conn.commit()

    def ensure_auth_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id TEXT PRIMARY KEY,
              username TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL,
              display_name TEXT NOT NULL,
              merchant_id TEXT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              session_id TEXT PRIMARY KEY,
              token_hash TEXT UNIQUE NOT NULL,
              user_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              expires_at TEXT NOT NULL,
              revoked_at TEXT NULL,
              FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        self.conn.commit()

    def clear_auth_for_tests(self) -> None:
        self.conn.execute("DELETE FROM sessions")
        self.conn.execute("DELETE FROM users")
        self.conn.commit()

    def upsert_user(self, user: AuthUserRecord) -> None:
        self.conn.execute(
            """
            INSERT INTO users(user_id, username, password_hash, role, display_name, merchant_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              username = excluded.username,
              password_hash = excluded.password_hash,
              role = excluded.role,
              display_name = excluded.display_name,
              merchant_id = excluded.merchant_id,
              status = excluded.status
            """,
            (
                user.user_id,
                user.username,
                user.password_hash,
                user.role,
                user.display_name,
                user.merchant_id,
                user.status,
                user.created_at,
            ),
        )
        self.conn.commit()

    def list_users(self) -> list[AuthUserRecord]:
        rows = self.conn.execute("SELECT * FROM users ORDER BY username").fetchall()
        return [AuthUserRecord.model_validate(dict(row)) for row in rows]

    def get_user(self, user_id: str) -> AuthUserRecord | None:
        row = self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return AuthUserRecord.model_validate(dict(row)) if row else None

    def get_user_by_username(self, username: str) -> AuthUserRecord | None:
        row = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return AuthUserRecord.model_validate(dict(row)) if row else None

    def update_user_status(self, user_id: str, status: str) -> None:
        self.conn.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        self.conn.commit()

    def create_session(self, session: AuthSessionRecord) -> None:
        self.conn.execute(
            """
            INSERT INTO sessions(session_id, token_hash, user_id, created_at, expires_at, revoked_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.session_id,
                session.token_hash,
                session.user_id,
                session.created_at,
                session.expires_at,
                session.revoked_at,
            ),
        )
        self.conn.commit()

    def get_session_by_token_hash(self, token_hash: str) -> AuthSessionRecord | None:
        row = self.conn.execute("SELECT * FROM sessions WHERE token_hash = ?", (token_hash,)).fetchone()
        return AuthSessionRecord.model_validate(dict(row)) if row else None

    def list_sessions_for_user(self, user_id: str) -> list[AuthSessionRecord]:
        rows = self.conn.execute(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [AuthSessionRecord.model_validate(dict(row)) for row in rows]

    def revoke_session(self, session_id: str, revoked_at: datetime | None = None) -> None:
        value = (revoked_at or datetime.now(UTC)).isoformat()
        self.conn.execute("UPDATE sessions SET revoked_at = ? WHERE session_id = ?", (value, session_id))
        self.conn.commit()

    def set_session_expiry(self, session_id: str, expires_at: datetime) -> None:
        self.conn.execute(
            "UPDATE sessions SET expires_at = ? WHERE session_id = ?",
            (expires_at.isoformat(), session_id),
        )
        self.conn.commit()

    def clear_demo(self, event_id: str = "demo-night-tour") -> None:
        collections = [
            "event_briefs",
            "events",
            "merchants",
            "runtime_states",
            "plans",
            "plan_versions",
            "route_points",
            "merchant_packs",
            "merchant_tasks",
            "recovery_actions",
            "incidents",
            "recovery_proposals",
            "public_notices",
            "agent_runs",
            "agent_tool_calls",
            "agent_drafts",
            "agent_model_calls",
            "agent_evaluations",
            "agent_traces",
            "operational_metrics",
            "reports",
            "notices",
            "audit_logs",
        ]
        for collection in collections:
            if collection in {"merchants", "runtime_states"}:
                self.conn.execute("DELETE FROM records WHERE collection = ?", (collection,))
            elif collection in {"agent_tool_calls", "agent_model_calls", "agent_evaluations"}:
                self.conn.execute(
                    "DELETE FROM records WHERE collection = ? AND item_key LIKE ?",
                    (collection, f"%{event_id}%"),
                )
            else:
                self.conn.execute(
                    "DELETE FROM records WHERE collection = ? AND item_key LIKE ?",
                    (collection, f"{event_id}%"),
                )
        self.conn.commit()

    def upsert_model(self, collection: str, key: str, model: BaseModel) -> None:
        self.upsert_payload(collection, key, model.model_dump())

    def upsert_payload(self, collection: str, key: str, payload: dict | list | str) -> None:
        self.conn.execute(
            """
            INSERT INTO records(collection, item_key, payload)
            VALUES (?, ?, ?)
            ON CONFLICT(collection, item_key) DO UPDATE SET payload = excluded.payload
            """,
            (collection, key, json.dumps(payload, ensure_ascii=False)),
        )
        self.conn.commit()

    def get_payload(self, collection: str, key: str) -> dict | list | str | None:
        row = self.conn.execute(
            "SELECT payload FROM records WHERE collection = ? AND item_key = ?",
            (collection, key),
        ).fetchone()
        if not row:
            return None
        return json.loads(row["payload"])

    def get_model(self, collection: str, key: str, model_class: type[T]) -> T | None:
        payload = self.get_payload(collection, key)
        if payload is None:
            return None
        return model_class.model_validate(payload)

    def list_models(self, collection: str, model_class: type[T], prefix: str = "") -> list[T]:
        if prefix:
            rows = self.conn.execute(
                "SELECT payload FROM records WHERE collection = ? AND item_key LIKE ? ORDER BY item_key",
                (collection, f"{prefix}%"),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT payload FROM records WHERE collection = ? ORDER BY item_key",
                (collection,),
            ).fetchall()
        return [model_class.model_validate(json.loads(row["payload"])) for row in rows]

    def save_event_brief(self, brief: EventBrief) -> None:
        self.upsert_model("event_briefs", brief.event_id, brief)

    def get_event_brief(self, event_id: str) -> EventBrief | None:
        return self.get_model("event_briefs", event_id, EventBrief)

    def save_merchant(self, merchant: MerchantProfile) -> None:
        self.upsert_model("merchants", merchant.merchant_id, merchant)

    def list_merchants(self) -> list[MerchantProfile]:
        return self.list_models("merchants", MerchantProfile)

    def get_merchant(self, merchant_id: str) -> MerchantProfile | None:
        return self.get_model("merchants", merchant_id, MerchantProfile)

    def save_runtime_state(self, state: MerchantRuntimeState) -> None:
        self.upsert_model("runtime_states", state.merchant_id, state)

    def get_runtime_state(self, merchant_id: str) -> MerchantRuntimeState | None:
        return self.get_model("runtime_states", merchant_id, MerchantRuntimeState)

    def list_runtime_states(self) -> list[MerchantRuntimeState]:
        return self.list_models("runtime_states", MerchantRuntimeState)

    def save_plan(self, plan: EventPlan) -> None:
        self.upsert_model("plans", plan.event_id, plan)

    def get_plan(self, event_id: str) -> EventPlan | None:
        return self.get_model("plans", event_id, EventPlan)

    def save_packs(self, event_id: str, packs: list[MerchantExecutionPack]) -> None:
        self.conn.execute(
            "DELETE FROM records WHERE collection = ? AND item_key LIKE ?",
            ("merchant_packs", f"{event_id}:"),
        )
        for pack in packs:
            self.upsert_model("merchant_packs", f"{event_id}:{pack.merchant_id}", pack)
        self.conn.commit()

    def list_packs(self, event_id: str) -> list[MerchantExecutionPack]:
        return self.list_models("merchant_packs", MerchantExecutionPack, prefix=f"{event_id}:")

    def save_recovery_action(self, action: RecoveryAction) -> None:
        self.upsert_model("recovery_actions", f"{action.event_id}:{action.action_id}", action)

    def get_recovery_action(self, action_id: str) -> RecoveryAction | None:
        rows = self.conn.execute(
            "SELECT payload FROM records WHERE collection = ? AND item_key LIKE ?",
            ("recovery_actions", f"%:{action_id}"),
        ).fetchall()
        if not rows:
            return None
        return RecoveryAction.model_validate(json.loads(rows[0]["payload"]))

    def list_recovery_actions(self, event_id: str) -> list[RecoveryAction]:
        return self.list_models("recovery_actions", RecoveryAction, prefix=f"{event_id}:")

    def append_notice(self, event_id: str, notice: str) -> None:
        notices = self.list_notices(event_id)
        if notice not in notices:
            notices.append(notice)
        self.upsert_payload("notices", event_id, notices)

    def list_notices(self, event_id: str) -> list[str]:
        payload = self.get_payload("notices", event_id)
        return list(payload or [])

    def save_report(self, report: ReviewReport) -> None:
        self.upsert_model("reports", report.event_id, report)

    def get_report(self, event_id: str) -> ReviewReport | None:
        return self.get_model("reports", event_id, ReviewReport)

    def save_audit_log(self, log: AuditLog) -> None:
        self.upsert_model("audit_logs", f"{log.event_id}:{log.log_id}", log)

    def list_audit_logs(self, event_id: str) -> list[AuditLog]:
        return self.list_models("audit_logs", AuditLog, prefix=f"{event_id}:")

    def save_event_summary(self, event: EventSummary) -> None:
        self.upsert_model("events", event.event_id, event)

    def get_event_summary(self, event_id: str) -> EventSummary | None:
        return self.get_model("events", event_id, EventSummary)

    def list_event_summaries(self) -> list[EventSummary]:
        return self.list_models("events", EventSummary)

    def save_route_point(self, point: RoutePoint) -> None:
        self.upsert_model("route_points", point.point_id, point)

    def list_route_points(self) -> list[RoutePoint]:
        return self.list_models("route_points", RoutePoint)

    def save_plan_version(self, plan: PlanVersion) -> None:
        self.upsert_model("plan_versions", f"{plan.event_id}:v{plan.version}", plan)

    def get_plan_version(self, event_id: str, version: int) -> PlanVersion | None:
        return self.get_model("plan_versions", f"{event_id}:v{version}", PlanVersion)

    def list_plan_versions(self, event_id: str) -> list[PlanVersion]:
        return self.list_models("plan_versions", PlanVersion, prefix=f"{event_id}:")

    def save_merchant_tasks(self, event_id: str, tasks: list[MerchantTask]) -> None:
        self.conn.execute(
            "DELETE FROM records WHERE collection = ? AND item_key LIKE ?",
            ("merchant_tasks", f"{event_id}:"),
        )
        for task in tasks:
            self.upsert_model("merchant_tasks", f"{event_id}:{task.task_id}", task)
        self.conn.commit()

    def list_merchant_tasks(
        self, event_id: str, merchant_id: str | None = None
    ) -> list[MerchantTask]:
        tasks = self.list_models("merchant_tasks", MerchantTask, prefix=f"{event_id}:")
        if merchant_id:
            return [task for task in tasks if task.merchant_id == merchant_id]
        return tasks

    def save_incident(self, incident: Incident) -> None:
        self.upsert_model("incidents", f"{incident.event_id}:{incident.incident_id}", incident)

    def get_incident(self, incident_id: str) -> Incident | None:
        rows = self.conn.execute(
            "SELECT payload FROM records WHERE collection = ? AND item_key LIKE ?",
            ("incidents", f"%:{incident_id}"),
        ).fetchall()
        if not rows:
            return None
        return Incident.model_validate(json.loads(rows[0]["payload"]))

    def list_incidents(self, event_id: str) -> list[Incident]:
        return self.list_models("incidents", Incident, prefix=f"{event_id}:")

    def save_recovery_proposal(self, proposal: RecoveryProposal) -> None:
        self.upsert_model(
            "recovery_proposals", f"{proposal.event_id}:{proposal.proposal_id}", proposal
        )

    def get_recovery_proposal(self, proposal_id: str) -> RecoveryProposal | None:
        rows = self.conn.execute(
            "SELECT payload FROM records WHERE collection = ? AND item_key LIKE ?",
            ("recovery_proposals", f"%:{proposal_id}"),
        ).fetchall()
        if not rows:
            return None
        return RecoveryProposal.model_validate(json.loads(rows[0]["payload"]))

    def list_recovery_proposals(self, event_id: str) -> list[RecoveryProposal]:
        return self.list_models("recovery_proposals", RecoveryProposal, prefix=f"{event_id}:")

    def save_public_notice(self, notice: PublicNotice) -> None:
        self.upsert_model("public_notices", f"{notice.event_id}:{notice.notice_id}", notice)

    def list_public_notices(self, event_id: str) -> list[PublicNotice]:
        return self.list_models("public_notices", PublicNotice, prefix=f"{event_id}:")

    def save_agent_trace(self, trace: AgentTrace) -> None:
        self.upsert_model("agent_traces", f"{trace.event_id}:{trace.trace_id}", trace)

    def list_agent_traces(self, event_id: str) -> list[AgentTrace]:
        return self.list_models("agent_traces", AgentTrace, prefix=f"{event_id}:")

    def save_agent_run(self, run: AgentRun) -> None:
        self.upsert_model("agent_runs", f"{run.event_id}:{run.run_id}", run)

    def get_agent_run(self, run_id: str) -> AgentRun | None:
        rows = self.conn.execute(
            "SELECT payload FROM records WHERE collection = ? AND item_key LIKE ?",
            ("agent_runs", f"%:{run_id}"),
        ).fetchall()
        if not rows:
            return None
        return AgentRun.model_validate(json.loads(rows[0]["payload"]))

    def list_agent_runs(self, event_id: str) -> list[AgentRun]:
        return self.list_models("agent_runs", AgentRun, prefix=f"{event_id}:")

    def save_agent_tool_call(self, call: AgentToolCall) -> None:
        self.upsert_model("agent_tool_calls", f"{call.run_id}:{call.tool_call_id}", call)

    def list_agent_tool_calls(self, run_id: str | None = None) -> list[AgentToolCall]:
        prefix = f"{run_id}:" if run_id else ""
        return self.list_models("agent_tool_calls", AgentToolCall, prefix=prefix)

    def save_agent_draft(self, draft: AgentDraft) -> None:
        self.upsert_model("agent_drafts", f"{draft.event_id}:{draft.draft_id}", draft)

    def list_agent_drafts(
        self, event_id: str, draft_type: str | None = None
    ) -> list[AgentDraft]:
        drafts = self.list_models("agent_drafts", AgentDraft, prefix=f"{event_id}:")
        if draft_type:
            return [draft for draft in drafts if draft.draft_type == draft_type]
        return drafts

    def save_agent_model_call(self, call: AgentModelCall) -> None:
        self.upsert_model("agent_model_calls", f"{call.run_id}:{call.model_call_id}", call)

    def list_agent_model_calls(self, run_id: str | None = None) -> list[AgentModelCall]:
        prefix = f"{run_id}:" if run_id else ""
        return self.list_models("agent_model_calls", AgentModelCall, prefix=prefix)

    def save_agent_evaluation(self, evaluation: AgentEvaluation) -> None:
        self.upsert_model(
            "agent_evaluations",
            f"{evaluation.run_id}:{evaluation.evaluation_id}",
            evaluation,
        )

    def list_agent_evaluations(
        self, run_id: str | None = None
    ) -> list[AgentEvaluation]:
        prefix = f"{run_id}:" if run_id else ""
        return self.list_models("agent_evaluations", AgentEvaluation, prefix=prefix)

    def save_operational_metric(self, metric: OperationalMetric) -> None:
        self.upsert_model(
            "operational_metrics", f"{metric.event_id}:{metric.metric_id}", metric
        )

    def list_operational_metrics(self, event_id: str) -> list[OperationalMetric]:
        return self.list_models("operational_metrics", OperationalMetric, prefix=f"{event_id}:")


STORE = MVPStore()
