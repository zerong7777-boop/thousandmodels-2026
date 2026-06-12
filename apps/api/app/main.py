from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.agents.orchestrator import choose_agent_backend
from app.agents.runtime import AgentRuntime
from app.agents.trace_builder import build_trace_from_steps
from app.audit import build_audit_log
from app.auth import (
    SESSION_COOKIE,
    clear_session_cookie,
    create_login_session,
    get_current_user,
    hash_session_token,
    public_user,
    require_merchant,
    require_organizer,
    verify_merchant_owner,
    verify_mutation_origin,
    verify_password,
)
from app.schemas import (
    AuthResponse,
    AuthUserRecord,
    InventoryTriggerRequest,
    LoginRequest,
    MerchantRuntimeState,
    PublicEvent,
    RuntimeStateUpdate,
)
from app.seed import seed_demo, seed_demo_accounts
from app.services.incidents import incident_from_runtime_state
from app.services.planning import (
    generate_event_plan,
    generate_merchant_packs,
    generate_merchant_tasks,
    generate_plan_version,
)
from app.services.publication import build_public_event
from app.services.recovery import (
    apply_recovery_proposal,
    build_inventory_recovery,
    build_recovery_proposal,
    build_weather_recovery,
)
from app.services.review import generate_review_report
from app.store import STORE

app = FastAPI(title="智引濠江 MVP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_origin_regex=r"http://(127\.0\.0\.1|localhost):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def seed_auth_on_startup() -> None:
    seed_demo_accounts(STORE)


def audit(event_id: str, actor_type: str, actor_id: str, action_type: str, note: str) -> None:
    STORE.save_audit_log(
        build_audit_log(
            event_id=event_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action_type=action_type,
            note=note,
        )
    )


def audit_user(event_id: str, user: AuthUserRecord, action_type: str, note: str) -> None:
    audit(event_id, user.role, user.user_id, action_type, note)


def persist_agent_runtime_result(result) -> None:
    STORE.save_agent_run(result.run)
    for call in result.tool_calls:
        STORE.save_agent_tool_call(call)
    for draft in result.drafts:
        STORE.save_agent_draft(draft)
    for model_call in result.model_calls:
        STORE.save_agent_model_call(model_call)
    for evaluation in result.evaluations:
        STORE.save_agent_evaluation(evaluation)


@app.get("/api/health")
def health():
    return {"status": "ok", "agent_backend": choose_agent_backend().__class__.__name__}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(request: Request, response: Response, payload: LoginRequest):
    verify_mutation_origin(request)
    user = STORE.get_user_by_username(payload.username)
    if not user or user.status != "active" or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return create_login_session(response, user)


@app.get("/api/auth/me", response_model=AuthResponse)
def me(user: AuthUserRecord = Depends(get_current_user)):
    return AuthResponse(user=public_user(user))


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    verify_mutation_origin(request)
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = STORE.get_session_by_token_hash(hash_session_token(token))
        if session:
            STORE.revoke_session(session.session_id)
    clear_session_cookie(response)
    return {"status": "logged_out"}


@app.get("/api/events")
def list_events(user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_event_summaries()


@app.get("/api/events/{event_id}")
def get_event(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    event = STORE.get_event_summary(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return event


@app.post("/api/events/demo/seed")
def seed_demo_event(request: Request, user: AuthUserRecord = Depends(require_organizer)):
    verify_mutation_origin(request)
    brief = seed_demo(STORE)
    audit(brief.event_id, "system", "seed", "seed_demo", "初始化演示活动和商户状态")
    return {"status": "seeded", "event_id": brief.event_id}


@app.get("/api/events/{event_id}/brief")
def get_event_brief(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    brief = STORE.get_event_brief(event_id)
    if not brief:
        raise HTTPException(status_code=404, detail="event brief not found")
    return brief


@app.post("/api/events/{event_id}/generate-plan")
def generate_plan(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    brief = STORE.get_event_brief(event_id)
    if not brief:
        brief = seed_demo(STORE, event_id=event_id)
    merchants = STORE.list_merchants()
    plan = generate_event_plan(brief, merchants, choose_agent_backend())
    packs = generate_merchant_packs(plan, merchants)
    route_points = STORE.list_route_points()
    if not route_points:
        seed_demo(STORE, event_id=event_id)
        brief = STORE.get_event_brief(event_id) or brief
        merchants = STORE.list_merchants()
        route_points = STORE.list_route_points()
    plan_v1 = generate_plan_version(
        brief=brief,
        merchants=merchants,
        route_points=route_points,
        version=1,
        reason="initial_plan",
    )
    runtime_result = AgentRuntime(mode="deterministic").run_planning(
        event_id=event_id,
        brief=brief,
        merchants=merchants,
        plan=plan_v1,
    )
    trace = build_trace_from_steps(
        event_id=event_id,
        trigger="planning_generation",
        steps=runtime_result.steps,
        final_output_ref=runtime_result.run.final_output_ref or f"plan:{event_id}:v{plan_v1.version}",
        trace_id=f"trace_{event_id}_v{plan_v1.version}",
    )
    tasks = generate_merchant_tasks(plan_v1, merchants)
    STORE.save_plan(plan)
    STORE.save_packs(event_id, packs)
    STORE.save_plan_version(plan_v1)
    persist_agent_runtime_result(runtime_result)
    STORE.save_agent_trace(trace)
    STORE.save_merchant_tasks(event_id, tasks)
    audit(event_id, "agent", "planner", "generate_plan", "生成 EventPlan 和商户执行包")
    return {
        **plan.model_dump(),
        "current_plan": plan_v1,
        "agent_trace": trace,
        "agent_run": runtime_result.run,
        "merchant_tasks": tasks,
    }


@app.get("/api/events/{event_id}/plan")
def get_plan(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    plan = STORE.get_plan(event_id)
    if not plan:
        raise HTTPException(status_code=404, detail="plan not found")
    return plan


@app.post("/api/events/{event_id}/approve-plan")
def approve_plan(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    plan = STORE.get_plan(event_id)
    if not plan:
        raise HTTPException(status_code=404, detail="plan not found")
    plan.approval_status = "approved"
    STORE.save_plan(plan)
    event = STORE.get_event_summary(event_id)
    plan_v1 = STORE.get_plan_version(event_id, 1)
    if event and plan_v1:
        plan_v1.status = "approved"
        plan_v1.approved_by = user.user_id
        plan_v1.approved_at = datetime.now(UTC).isoformat()
        event.status = "active"
        event.current_plan_version = 1
        event.public_release_status = "published"
        STORE.save_plan_version(plan_v1)
        STORE.save_event_summary(event)
    audit_user(event_id, user, "approve_plan", "organizer approved event plan")
    return plan


@app.get("/api/events/{event_id}/plans")
def list_plan_versions(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_plan_versions(event_id)


@app.get("/api/events/{event_id}/plans/current")
def current_plan_version(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    event = STORE.get_event_summary(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    plan = STORE.get_plan_version(event_id, event.current_plan_version)
    if not plan:
        raise HTTPException(status_code=404, detail="current plan not found")
    return plan


@app.post("/api/events/{event_id}/plans/{version}/approve")
def approve_plan_version(
    request: Request,
    event_id: str,
    version: int,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    plan = STORE.get_plan_version(event_id, version)
    event = STORE.get_event_summary(event_id)
    if not plan or not event:
        raise HTTPException(status_code=404, detail="plan or event not found")
    plan.status = "approved"
    plan.approved_by = user.user_id
    plan.approved_at = datetime.now(UTC).isoformat()
    event.status = "active"
    event.current_plan_version = version
    event.public_release_status = "published"
    STORE.save_plan_version(plan)
    STORE.save_event_summary(event)
    audit_user(event_id, user, "approve_plan_version", f"approved v{version}")
    return plan


@app.get("/api/events/{event_id}/agent-traces")
def agent_traces(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_agent_traces(event_id)


@app.get("/api/events/{event_id}/agent-runs")
def agent_runs(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_agent_runs(event_id)


@app.get("/api/events/{event_id}/agent-drafts")
def agent_drafts(
    event_id: str,
    draft_type: str | None = None,
    user: AuthUserRecord = Depends(require_organizer),
):
    return STORE.list_agent_drafts(event_id, draft_type=draft_type)


@app.get("/api/events/{event_id}/agent-runs/{run_id}/tool-calls")
def agent_tool_calls(
    event_id: str,
    run_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    run = STORE.get_agent_run(run_id)
    if not run or run.event_id != event_id:
        raise HTTPException(status_code=404, detail="agent run not found")
    return STORE.list_agent_tool_calls(run_id)


@app.get("/api/events/{event_id}/agent-runs/{run_id}/model-calls")
def agent_model_calls(
    event_id: str,
    run_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    run = STORE.get_agent_run(run_id)
    if not run or run.event_id != event_id:
        raise HTTPException(status_code=404, detail="agent run not found")
    return STORE.list_agent_model_calls(run_id)


@app.get("/api/events/{event_id}/merchant-tasks")
def merchant_tasks(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_merchant_tasks(event_id)


@app.get("/api/events/{event_id}/merchant-packs")
def merchant_packs(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_packs(event_id)


@app.get("/api/merchants")
def merchants(user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_merchants()


@app.get("/api/merchants/runtime-states")
def runtime_states(user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_runtime_states()


@app.post("/api/merchants/{merchant_id}/runtime-state")
def update_runtime_state(
    request: Request,
    merchant_id: str,
    payload: RuntimeStateUpdate,
    user: AuthUserRecord = Depends(require_merchant),
):
    verify_mutation_origin(request)
    verify_merchant_owner(merchant_id, user)
    state = STORE.get_runtime_state(merchant_id)
    if not state:
        raise HTTPException(status_code=404, detail="merchant state not found")
    next_payload = state.model_dump()
    for key, value in payload.model_dump(exclude_none=True).items():
        next_payload[key] = value
    next_payload["updated_at"] = datetime.now(UTC).isoformat()
    next_state = MerchantRuntimeState.model_validate(next_payload)
    STORE.save_runtime_state(next_state)
    incident = incident_from_runtime_state("demo-night-tour", next_state)
    runtime_result = None
    if incident:
        STORE.save_incident(incident)
        runtime_result = AgentRuntime().run_incident_recovery_preview(
            event_id="demo-night-tour",
            incident=incident,
            state=next_state,
        )
        persist_agent_runtime_result(runtime_result)
        audit("demo-night-tour", "system", "incident-detector", "create_incident", incident.trigger_detail)
    audit_user("demo-night-tour", user, "update_runtime_state", "merchant runtime state updated")
    return {
        **next_state.model_dump(),
        "runtime_state": next_state,
        "incident": incident,
        "agent_run": runtime_result.run if runtime_result else None,
        "agent_drafts": runtime_result.drafts if runtime_result else [],
    }


@app.get("/api/merchants/{merchant_id}/workbench")
def merchant_workbench(
    merchant_id: str,
    event_id: str = "demo-night-tour",
    user: AuthUserRecord = Depends(get_current_user),
):
    if user.role == "merchant":
        verify_merchant_owner(merchant_id, user)
    elif user.role != "organizer":
        raise HTTPException(status_code=403, detail="forbidden")
    merchant = STORE.get_merchant(merchant_id)
    state = STORE.get_runtime_state(merchant_id)
    if not merchant or not state:
        raise HTTPException(status_code=404, detail="merchant not found")
    return {
        "merchant": merchant,
        "runtime_state": state,
        "tasks": STORE.list_merchant_tasks(event_id, merchant_id=merchant_id),
    }


@app.post("/api/events/{event_id}/trigger/inventory")
def trigger_inventory(
    request: Request,
    event_id: str,
    payload: InventoryTriggerRequest,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    state = STORE.get_runtime_state(payload.merchant_id)
    if not state:
        raise HTTPException(status_code=404, detail="merchant state not found")
    state.inventory_status = "sold_out"
    state.queue_status = "busy"
    state.available_for_visitors = False
    state.temporary_note = "演示触发：库存不足"
    state.updated_at = datetime.now(UTC).isoformat()
    STORE.save_runtime_state(state)
    action = build_inventory_recovery(event_id, state, fallback_merchant_id="m007")
    STORE.save_recovery_action(action)
    audit(event_id, "tool", "inventory", "trigger_inventory", action.trigger_detail)
    return action


@app.post("/api/events/{event_id}/trigger/weather")
def trigger_weather(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    action = build_weather_recovery(event_id, weather_status="heavy_rain")
    STORE.save_recovery_action(action)
    incident = incident_from_runtime_state(
        event_id,
        MerchantRuntimeState(
            merchant_id="weather",
            inventory_status="normal",
            queue_status="normal",
            available_for_visitors=True,
            temporary_note="heavy_rain",
            updated_at=datetime.now(UTC).isoformat(),
        ),
    )
    if incident is None:
        from app.schemas import Incident

        incident = Incident(
            incident_id=f"inc_{event_id}_weather_heavy_rain",
            event_id=event_id,
            type="weather",
            severity="high",
            source="weather_tool",
            trigger_detail="weather_status=heavy_rain",
            affected_route_points=["rp001", "rp003"],
            affected_merchants=["m002", "m005", "m008"],
            status="open",
            created_at=datetime.now(UTC).isoformat(),
        )
    STORE.save_incident(incident)
    audit(event_id, "tool", "weather", "trigger_weather", action.trigger_detail)
    return action


@app.get("/api/events/{event_id}/recovery-actions")
def recovery_actions(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_recovery_actions(event_id)


@app.get("/api/events/{event_id}/incidents")
def list_incidents(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_incidents(event_id)


@app.post("/api/events/{event_id}/incidents/{incident_id}/recovery-proposals")
def create_recovery_proposal(
    request: Request,
    event_id: str,
    incident_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    incident = STORE.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")
    proposal = build_recovery_proposal(incident)
    incident.status = "proposal_ready"
    STORE.save_incident(incident)
    STORE.save_recovery_proposal(proposal)
    audit(event_id, "agent", "RecoveryAgent", "create_recovery_proposal", proposal.impact_summary)
    return proposal


@app.post("/api/events/{event_id}/recovery-proposals/{proposal_id}/approve")
def approve_recovery_proposal(
    request: Request,
    event_id: str,
    proposal_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    proposal = STORE.get_recovery_proposal(proposal_id)
    event = STORE.get_event_summary(event_id)
    if not proposal or not event:
        raise HTTPException(status_code=404, detail="proposal or event not found")
    current_version = event.current_plan_version or 1
    current_plan = STORE.get_plan_version(event_id, current_version)
    if not current_plan:
        raise HTTPException(status_code=404, detail="current plan not found")
    proposal.approval_status = "approved"
    next_plan, next_tasks, notice = apply_recovery_proposal(
        current_plan=current_plan,
        proposal=proposal,
        route_points=STORE.list_route_points(),
        current_tasks=STORE.list_merchant_tasks(event_id),
    )
    current_plan.status = "superseded"
    event.current_plan_version = next_plan.version
    event.public_release_status = "published"
    STORE.save_plan_version(current_plan)
    STORE.save_plan_version(next_plan)
    STORE.save_merchant_tasks(event_id, next_tasks)
    STORE.save_public_notice(notice)
    STORE.save_recovery_proposal(proposal)
    incident = STORE.get_incident(proposal.incident_id)
    if incident:
        incident.status = "approved"
        STORE.save_incident(incident)
    STORE.save_event_summary(event)
    audit_user(event_id, user, "approve_recovery_proposal", proposal_id)
    return {"proposal": proposal, "current_plan": next_plan, "notice": notice}


@app.post("/api/recovery-actions/{action_id}/approve")
def approve_recovery_action(
    request: Request,
    action_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    action = STORE.get_recovery_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="recovery action not found")
    action.approval_status = "approved"
    STORE.save_recovery_action(action)
    STORE.append_notice(action.event_id, action.tourist_notification)
    audit_user(action.event_id, user, "approve_recovery", action.action_id)
    return action


@app.get("/api/public/events/{event_id}")
def public_event(event_id: str):
    event = STORE.get_event_summary(event_id)
    if event and event.current_plan_version:
        plan_version = STORE.get_plan_version(event_id, event.current_plan_version)
        if plan_version:
            return build_public_event(
                event=event,
                plan=plan_version,
                notices=STORE.list_public_notices(event_id),
                legacy_notices=STORE.list_notices(event_id),
            )
    plan = STORE.get_plan(event_id)
    if not plan:
        raise HTTPException(status_code=404, detail="plan not found")
    return PublicEvent(
        event_id=event_id,
        theme=plan.theme,
        route=plan.route,
        marketing_content=plan.marketing_content,
        notices=STORE.list_notices(event_id),
        checkin_tasks=[
            "完成福隆新街老字号问答",
            "在新马路文创铺领取街区线索",
            "在内港故事点完成一次打卡",
        ],
    )


@app.post("/api/events/{event_id}/review-report")
def review_report(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    plan = STORE.get_plan(event_id)
    if not plan:
        raise HTTPException(status_code=404, detail="plan not found")
    report = generate_review_report(
        plan=plan,
        recovery_actions=STORE.list_recovery_actions(event_id),
        audit_logs=STORE.list_audit_logs(event_id),
        metrics=STORE.list_operational_metrics(event_id),
    )
    runtime_result = AgentRuntime(mode="deterministic").run_review_generation(
        event_id=event_id,
        metrics=STORE.list_operational_metrics(event_id),
        incidents=STORE.list_incidents(event_id),
        notices=STORE.list_public_notices(event_id),
        proposals=STORE.list_recovery_proposals(event_id),
    )
    persist_agent_runtime_result(runtime_result)
    STORE.save_report(report)
    audit(event_id, "agent", "review", "generate_review_report", "生成活动复盘报告")
    return {**report.model_dump(), "agent_run": runtime_result.run, "agent_drafts": runtime_result.drafts}


@app.get("/api/events/{event_id}/review-report")
def get_review_report(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    report = STORE.get_report(event_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return report


@app.get("/api/events/{event_id}/audit-logs")
def audit_logs(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_audit_logs(event_id)
