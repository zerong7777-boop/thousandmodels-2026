from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    is_allowed_local_dev_origin,
    public_user,
    record_auth_failure,
    require_merchant,
    require_organizer,
    verify_merchant_owner,
    verify_mutation_origin,
    verify_password,
)
from app.csrf import CSRF_COOKIE, issue_csrf_token
from app.metrics import METRICS
from app.migrations.runner import latest_schema_version, pending_versions
from app.observability import (
    http_exception_handler,
    request_id_middleware,
    unhandled_exception_handler,
)
from app.readiness import build_readiness_payload
from app.schemas import (
    AuthResponse,
    AuthUserRecord,
    EventCreateRequest,
    EventMerchantParticipantUpdateRequest,
    EventMerchantRosterUpdateRequest,
    EventSummary,
    EventUpdateRequest,
    InventoryTriggerRequest,
    LoginRequest,
    MerchantRuntimeState,
    PublicEvent,
    RuntimeStateUpdate,
)
from app.seed import seed_demo, seed_demo_accounts, seed_local_catalog
from app.services.events import (
    create_event,
    mark_public_release_for_plan_approval,
    mark_public_release_published,
    mark_public_release_stale,
    update_draft_event,
)
from app.services.incidents import incident_from_runtime_state
from app.settings import AppSettings, load_settings, load_validated_settings
from app.services.event_page import (
    build_event_page_draft,
    build_event_page_projection,
    publish_event_page as mark_event_page_published,
)
from app.services.event_merchants import (
    merchant_scope_for_plan_ids,
    merchant_scope_for_planning,
    replace_event_merchant_roster,
    summarize_event_merchants,
    update_event_merchant_participant,
)
from app.services.merchant_edge import generate_merchant_interaction_packages
from app.services.operation_suggestions import (
    OperationSuggestionError,
    approve_operation_suggestion,
    generate_operation_suggestions,
    list_current_operation_suggestions,
)
from app.services.planning import (
    generate_event_plan,
    generate_merchant_packs,
    generate_merchant_tasks,
    generate_plan_version,
)
from app.services.publication import build_public_event
from app.services.qwenpaw_shadow import (
    QwenPawShadowRunRequest,
    QwenPawShadowRunResponse,
    run_qwenpaw_shadow,
)
from app.services.recovery import (
    apply_recovery_proposal,
    build_inventory_recovery,
    build_recovery_proposal,
    build_weather_recovery,
)
from app.services.review import generate_review_report
from app.services.touchpoints import (
    claim_coupon,
    record_touchpoint_interaction,
    redeem_coupon,
    summarize_touchpoint_metrics,
)
from app.store import MVPStore, STORE

STRICT_MUTATION_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}
LOCAL_DEV_ORIGIN_REGEX = r"http://(127\.0\.0\.1|localhost):\d+"
APP_SETTINGS = load_settings()


def cors_allow_origins(settings: AppSettings) -> list[str]:
    return list(settings.allowed_origins)


def cors_allow_origin_regex(settings: AppSettings) -> str | None:
    return LOCAL_DEV_ORIGIN_REGEX if settings.demo_mode else None

app = FastAPI(title="智引濠江 MVP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins(APP_SETTINGS),
    allow_origin_regex=cors_allow_origin_regex(APP_SETTINGS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.on_event("startup")
def seed_auth_on_startup() -> None:
    settings = load_validated_settings()
    validate_and_seed_auth(STORE, settings)


def validate_and_seed_auth(store: MVPStore, settings: AppSettings) -> None:
    settings.validate_startup()
    if settings.demo_mode:
        seed_demo_accounts(store)


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


def has_ascii_slug_component(value: str) -> bool:
    return any(char.isascii() and char.isalnum() for char in value.strip())


def verify_strict_mutation_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin in STRICT_MUTATION_ORIGINS or is_allowed_local_dev_origin(origin):
        return
    record_auth_failure("invalid_mutation_origin")
    raise HTTPException(status_code=403, detail="invalid mutation origin")


def persist_agent_runtime_result(result) -> None:
    STORE.save_agent_run(result.run)
    METRICS.increment(
        "agent_runs_total",
        {
            "mode": result.run.mode,
            "status": result.run.status,
            "trigger": result.run.trigger,
        },
    )
    for call in result.tool_calls:
        STORE.save_agent_tool_call(call)
    for draft in result.drafts:
        STORE.save_agent_draft(draft)
    for model_call in result.model_calls:
        STORE.save_agent_model_call(model_call)
    for evaluation in result.evaluations:
        STORE.save_agent_evaluation(evaluation)


def current_event_and_plan(event_id: str):
    event = STORE.get_event_summary(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    plan = STORE.get_plan_version(event_id, event.current_plan_version)
    if not plan:
        raise HTTPException(status_code=404, detail="current plan not found")
    return event, plan


def require_event_summary(event_id: str):
    event = STORE.get_event_summary(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return event


def latest_published_event_page(event_id: str, plan_version: int | None = None):
    pages = [page for page in STORE.list_event_pages(event_id) if page.status == "published"]
    if plan_version is not None:
        pages = [page for page in pages if page.plan_version == plan_version]
    if not pages:
        return None
    return max(
        pages,
        key=lambda page: (
            page.plan_version,
            page.published_at or "",
            page.updated_at or "",
            page.id,
        ),
    )


@app.get("/api/health")
def health():
    METRICS.increment("health_checks_total")
    settings = load_settings()
    store = {
        "kind": "sqlite",
        "schema_version": latest_schema_version(STORE.conn),
        "pending_migrations": len(pending_versions(STORE.conn)),
    }
    if settings.app_env in {"local", "demo"}:
        store["database_path"] = str(STORE.db_path)
    return {
        "status": "ok",
        "agent_backend": choose_agent_backend().__class__.__name__,
        "store": store,
    }


@app.get("/api/ready")
def ready():
    return build_readiness_payload(settings=load_settings(), store=STORE)


@app.get("/api/metrics")
def metrics():
    return {"scope": "process", "counters": METRICS.snapshot()}


@app.post("/api/auth/login", response_model=AuthResponse)
def login(request: Request, response: Response, payload: LoginRequest):
    verify_mutation_origin(request)
    user = STORE.get_user_by_username(payload.username)
    if not user or user.status != "active" or not verify_password(payload.password, user.password_hash):
        record_auth_failure("invalid_credentials")
        raise HTTPException(status_code=401, detail="invalid credentials")
    return create_login_session(response, user)


@app.get("/api/auth/me", response_model=AuthResponse)
def me(user: AuthUserRecord = Depends(get_current_user)):
    return AuthResponse(user=public_user(user))


@app.get("/api/auth/csrf")
def csrf(response: Response):
    settings = load_settings()
    token = issue_csrf_token(settings.required_secret())
    response.set_cookie(
        CSRF_COOKIE,
        token,
        httponly=False,
        secure=settings.session_cookie_secure,
        samesite=settings.session_samesite,
        path="/",
    )
    return {"csrf_token": token}


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


@app.post("/api/events", response_model=EventSummary)
def create_event_endpoint(
    request: Request,
    payload: EventCreateRequest,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    try:
        event = create_event(STORE, payload)
    except ValueError as exc:
        detail = str(exc)
        status_code = 400 if detail == "event_id is invalid" else 409
        raise HTTPException(status_code=status_code, detail=detail) from exc
    audit_user(event.event_id, user, "create_event", event.title)
    return event


@app.patch("/api/events/{event_id}", response_model=EventSummary)
def update_event_endpoint(
    request: Request,
    event_id: str,
    payload: EventUpdateRequest,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    if not has_ascii_slug_component(event_id):
        raise HTTPException(status_code=400, detail="event_id is invalid")
    try:
        event = update_draft_event(STORE, event_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    audit_user(event_id, user, "update_event", event.title)
    return event


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


@app.get("/api/events/{event_id}/merchant-roster")
def get_event_merchant_roster(
    event_id: str, user: AuthUserRecord = Depends(require_organizer)
):
    require_event_summary(event_id)
    return summarize_event_merchants(STORE, event_id)


@app.put("/api/events/{event_id}/merchant-roster")
def replace_event_merchant_roster_endpoint(
    request: Request,
    event_id: str,
    payload: EventMerchantRosterUpdateRequest,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    require_event_summary(event_id)
    if not STORE.list_merchants():
        seed_local_catalog(STORE)
    try:
        summary = replace_event_merchant_roster(STORE, event_id, payload.merchant_ids)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    audit_user(event_id, user, "replace_event_merchant_roster", f"{summary.total_count} merchants")
    return summary


@app.patch("/api/events/{event_id}/merchant-roster/{merchant_id}")
def update_event_merchant_participant_endpoint(
    request: Request,
    event_id: str,
    merchant_id: str,
    payload: EventMerchantParticipantUpdateRequest,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    require_event_summary(event_id)
    if not STORE.get_merchant(merchant_id):
        raise HTTPException(status_code=404, detail="merchant not found")
    try:
        summary = update_event_merchant_participant(STORE, event_id, merchant_id, payload)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    audit_user(event_id, user, "update_event_merchant_roster", merchant_id)
    return summary


@app.post("/api/events/{event_id}/generate-plan")
def generate_plan(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    brief = STORE.get_event_brief(event_id)
    event = STORE.get_event_summary(event_id)
    if not brief or not event:
        raise HTTPException(status_code=404, detail="event brief not found")
    route_points = STORE.list_route_points()
    if not STORE.list_merchants() or not route_points:
        seed_local_catalog(STORE)
        route_points = STORE.list_route_points()
    try:
        merchants = merchant_scope_for_planning(STORE, event_id)
    except RuntimeError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    plan = generate_event_plan(brief, merchants, choose_agent_backend())
    packs = generate_merchant_packs(plan, merchants)
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
    event.status = "pending_approval"
    event.public_release_status = "draft"
    STORE.save_event_summary(event)
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
        event = mark_public_release_for_plan_approval(STORE, event, 1)
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
    event = mark_public_release_for_plan_approval(STORE, event, version)
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
    run = STORE.get_agent_run(run_id, event_id=event_id)
    if not run or run.event_id != event_id:
        raise HTTPException(status_code=404, detail="agent run not found")
    return STORE.list_agent_tool_calls(run_id)


@app.get("/api/events/{event_id}/agent-runs/{run_id}/model-calls")
def agent_model_calls(
    event_id: str,
    run_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    run = STORE.get_agent_run(run_id, event_id=event_id)
    if not run or run.event_id != event_id:
        raise HTTPException(status_code=404, detail="agent run not found")
    return STORE.list_agent_model_calls(run_id)


@app.get("/api/events/{event_id}/agent-runs/{run_id}/evaluations")
def agent_evaluations(
    event_id: str,
    run_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    run = STORE.get_agent_run(run_id, event_id=event_id)
    if not run or run.event_id != event_id:
        raise HTTPException(status_code=404, detail="agent run not found")
    return STORE.list_agent_evaluations(run_id)


@app.get("/api/events/{event_id}/merchant-tasks")
def merchant_tasks(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_merchant_tasks(event_id)


@app.get("/api/events/{event_id}/merchant-packs")
def merchant_packs(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return STORE.list_packs(event_id)


@app.post("/api/events/{event_id}/merchant-edge-packages/generate")
def generate_merchant_edge_packages(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    _, plan_version = current_event_and_plan(event_id)
    if plan_version.status != "approved":
        raise HTTPException(status_code=400, detail="current plan is not approved")
    run_id = f"run_{event_id}_merchant_edge_v{plan_version.version}"
    merchants = merchant_scope_for_plan_ids(STORE, event_id, plan_version.merchant_assignments)
    packages = generate_merchant_interaction_packages(
        event_id=event_id,
        plan_version=plan_version,
        merchants=merchants,
        tasks=STORE.list_merchant_tasks(event_id),
        run_id=run_id,
    )
    runtime_result = AgentRuntime(mode="deterministic").run_merchant_edge_package_generation(
        event_id=event_id,
        plan=plan_version,
        merchants=merchants,
        tasks=STORE.list_merchant_tasks(event_id),
        packages=packages,
    )
    persist_agent_runtime_result(runtime_result)
    trace = build_trace_from_steps(
        event_id=event_id,
        trigger="merchant_edge_package_generation",
        steps=runtime_result.steps,
        final_output_ref=runtime_result.run.final_output_ref
        or f"merchant_interaction_packages:{event_id}:v{plan_version.version}",
        trace_id=f"trace_{event_id}_merchant_edge_v{plan_version.version}",
    )
    STORE.save_agent_trace(trace)
    for package in packages:
        for touchpoint in package.touchpoints:
            STORE.save_touchpoint(touchpoint)
        for coupon_rule in package.coupon_rules:
            STORE.save_coupon_rule(coupon_rule)
        STORE.save_merchant_interaction_package(package)
    audit_user(event_id, user, "generate_merchant_edge_packages", f"generated {len(packages)} packages")
    return {"packages": packages, "agent_run": runtime_result.run, "agent_trace": trace}


@app.get("/api/events/{event_id}/merchant-edge-packages")
def list_merchant_edge_packages(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    return {"packages": STORE.list_merchant_interaction_packages(event_id)}


@app.post("/api/events/{event_id}/operation-suggestions/generate")
def generate_operation_suggestions_endpoint(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    if not STORE.get_event_summary(event_id):
        raise HTTPException(status_code=404, detail="event not found")
    try:
        suggestions = generate_operation_suggestions(event_id)
    except OperationSuggestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    audit_user(event_id, user, "generate_operation_suggestions", f"generated {len(suggestions)} suggestions")
    return {"suggestions": suggestions}


@app.get("/api/events/{event_id}/operation-suggestions")
def list_operation_suggestions(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    if not STORE.get_event_summary(event_id):
        raise HTTPException(status_code=404, detail="event not found")
    try:
        suggestions = list_current_operation_suggestions(event_id)
    except OperationSuggestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return {"suggestions": suggestions}


@app.post("/api/events/{event_id}/operation-suggestions/{suggestion_id}/approve")
def approve_operation_suggestion_endpoint(
    request: Request,
    event_id: str,
    suggestion_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    if not STORE.get_event_summary(event_id):
        raise HTTPException(status_code=404, detail="event not found")
    try:
        suggestion = approve_operation_suggestion(event_id, suggestion_id)
    except OperationSuggestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    audit_user(event_id, user, "approve_operation_suggestion", suggestion_id)
    return suggestion


@app.post(
    "/api/events/{event_id}/qwenpaw-shadow-orchestration/run",
    response_model=QwenPawShadowRunResponse,
)
def run_qwenpaw_shadow_orchestration_endpoint(
    request: Request,
    event_id: str,
    payload: QwenPawShadowRunRequest,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    verify_strict_mutation_origin(request)
    try:
        runtime_result, advisory_bundle = run_qwenpaw_shadow(
            event_id=event_id,
            incident_id=payload.incident_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    persist_agent_runtime_result(runtime_result)
    trace = build_trace_from_steps(
        event_id=event_id,
        trigger="qwenpaw_shadow_orchestration",
        steps=runtime_result.steps,
        final_output_ref=runtime_result.run.final_output_ref or "",
        trace_id=f"trace_{runtime_result.run.run_id}",
    )
    STORE.save_agent_trace(trace)
    METRICS.increment(
        "qwenpaw_advisory_total",
        {"status": runtime_result.run.status},
    )
    permission_decisions = [
        call.output_payload["permission_decision"]
        for call in runtime_result.tool_calls
        if "permission_decision" in call.output_payload
    ]
    audit_user(event_id, user, "run_qwenpaw_shadow_orchestration", runtime_result.run.run_id)
    return QwenPawShadowRunResponse(
        agent_run=runtime_result.run,
        advisory_bundle=advisory_bundle,
        steps=runtime_result.steps,
        permission_decisions=permission_decisions,
    )


@app.get("/api/merchants")
def merchants(user: AuthUserRecord = Depends(require_organizer)):
    if not STORE.list_merchants():
        seed_local_catalog(STORE)
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
    merchant_payload = merchant.model_dump()
    merchant_payload["id"] = merchant.merchant_id
    interaction_package = STORE.get_merchant_interaction_package(event_id, merchant_id)
    if interaction_package:
        touchpoints = [
            touchpoint
            for touchpoint in STORE.list_touchpoints(event_id, merchant_id=merchant_id)
            if touchpoint.package_id == interaction_package.id
        ]
        coupon_rules = [
            rule
            for rule in STORE.list_coupon_rules(event_id, merchant_id=merchant_id)
            if rule.package_id == interaction_package.id
        ]
    else:
        touchpoints = []
        coupon_rules = []
    touchpoint_metrics = summarize_touchpoint_metrics(event_id, merchant_id=merchant_id)
    current_touchpoint_ids = {touchpoint.id for touchpoint in touchpoints}
    current_coupon_rule_ids = {rule.id for rule in coupon_rules}
    current_interactions = [
        interaction
        for interaction in STORE.list_touchpoint_interactions(event_id, merchant_id=merchant_id)
        if interaction.touchpoint_id in current_touchpoint_ids
    ]
    current_redemptions = [
        redemption
        for redemption in STORE.list_coupon_redemptions(event_id, merchant_id=merchant_id)
        if redemption.coupon_rule_id in current_coupon_rule_ids
    ]
    return {
        "merchant": merchant_payload,
        "runtime_state": state,
        "tasks": STORE.list_merchant_tasks(event_id, merchant_id=merchant_id),
        "interaction_package": interaction_package,
        "touchpoint_summary": {
            "total": len(touchpoints),
            "active": len([touchpoint for touchpoint in touchpoints if touchpoint.status == "active"]),
            "types": sorted({touchpoint.touchpoint_type for touchpoint in touchpoints}),
            "total_interactions": touchpoint_metrics["total_interactions"],
            "interaction_types": touchpoint_metrics["interaction_types"],
            "current_package_interactions": len(current_interactions),
            "event_merchant_interactions": touchpoint_metrics["total_interactions"],
        },
        "coupon_summary": {
            "total": len(coupon_rules),
            "active": len([rule for rule in coupon_rules if rule.status == "active"]),
            "max_redemptions": sum(rule.max_redemptions for rule in coupon_rules),
            "current_package_claims": len(
                [redemption for redemption in current_redemptions if redemption.status in {"claimed", "redeemed"}]
            ),
            "current_package_redemptions": len(
                [redemption for redemption in current_redemptions if redemption.status == "redeemed"]
            ),
            "event_merchant_claims": touchpoint_metrics["coupon_claims"],
            "event_merchant_redemptions": touchpoint_metrics["coupon_redemptions"],
        },
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
    incident = STORE.get_incident(incident_id, event_id=event_id)
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
    proposal = STORE.get_recovery_proposal(proposal_id, event_id=event_id)
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
    event = mark_public_release_stale(event)
    STORE.save_plan_version(current_plan)
    STORE.save_plan_version(next_plan)
    STORE.save_merchant_tasks(event_id, next_tasks)
    STORE.save_public_notice(notice)
    STORE.save_recovery_proposal(proposal)
    incident = STORE.get_incident(proposal.incident_id, event_id=event_id)
    if incident:
        incident.status = "approved"
        STORE.save_incident(incident)
    STORE.save_event_summary(event)
    METRICS.increment("recovery_approvals_total", {"kind": "proposal"})
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
    METRICS.increment("recovery_approvals_total", {"kind": "action"})
    audit_user(action.event_id, user, "approve_recovery", action.action_id)
    return action


@app.post("/api/events/{event_id}/event-page/draft")
def draft_event_page(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    event, plan_version = current_event_and_plan(event_id)
    if plan_version.status != "approved":
        raise HTTPException(status_code=400, detail="current plan is not approved")
    merchants = merchant_scope_for_plan_ids(STORE, event_id, plan_version.merchant_assignments)
    page = build_event_page_draft(
        event=event,
        plan_version=plan_version,
        route_points=plan_version.route_points,
        merchants=merchants,
        notices=STORE.list_public_notices(event_id),
    )
    STORE.save_event_page(page)
    audit_user(event_id, user, "draft_event_page", page.id)
    return page


@app.post("/api/events/{event_id}/event-page/publish")
def publish_event_page_endpoint(
    request: Request,
    event_id: str,
    user: AuthUserRecord = Depends(require_organizer),
):
    verify_mutation_origin(request)
    event, plan_version = current_event_and_plan(event_id)
    if plan_version.status != "approved":
        raise HTTPException(status_code=400, detail="current plan is not approved")
    page = STORE.get_latest_event_page(event_id)
    if not page:
        raise HTTPException(status_code=404, detail="event page not found")
    if page.plan_version != plan_version.version:
        page = build_event_page_draft(
            event=event,
            plan_version=plan_version,
            route_points=plan_version.route_points,
            merchants=merchant_scope_for_plan_ids(STORE, event_id, plan_version.merchant_assignments),
            notices=STORE.list_public_notices(event_id),
        )
    published = mark_event_page_published(page)
    STORE.save_event_page(published)
    event = mark_public_release_published(event)
    STORE.save_event_summary(event)
    audit_user(event_id, user, "publish_event_page", published.id)
    return published


@app.get("/api/events/{event_id}/event-page")
def get_event_page(event_id: str, user: AuthUserRecord = Depends(require_organizer)):
    page = STORE.get_latest_event_page(event_id)
    if not page:
        raise HTTPException(status_code=404, detail="event page not found")
    return page


@app.get("/api/public/events/{event_id}")
def public_event(event_id: str):
    event = STORE.get_event_summary(event_id)
    if event:
        if event.current_plan_version:
            plan_version = STORE.get_plan_version(event_id, event.current_plan_version)
            if plan_version:
                page = latest_published_event_page(event_id, plan_version=plan_version.version)
                public_payload = build_public_event(
                    event=event,
                    plan=plan_version,
                    notices=STORE.list_public_notices(event_id),
                    legacy_notices=STORE.list_notices(event_id),
                )
                if page:
                    event_page = build_event_page_projection(
                        event=event,
                        page=page,
                        plan_version=plan_version,
                        notices=STORE.list_public_notices(event_id),
                        packages=STORE.list_merchant_interaction_packages(event_id),
                    )
                    public_payload["event_page"] = event_page
                    public_payload["merchant_highlights"] = event_page["merchant_highlights"]
                    return public_payload
                if event_id == "demo-night-tour":
                    return public_payload
        if event_id != "demo-night-tour":
            raise HTTPException(status_code=404, detail="event page not found")
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


def require_public_event_ready(event_id: str) -> None:
    if event_id == "demo-night-tour":
        return
    event = STORE.get_event_summary(event_id)
    if not event or event.public_release_status != "published":
        raise HTTPException(status_code=404, detail="event page not found")
    plan_version = STORE.get_plan_version(event_id, event.current_plan_version)
    if not plan_version:
        raise HTTPException(status_code=404, detail="event page not found")
    page = latest_published_event_page(event_id, plan_version=plan_version.version)
    if not page:
        raise HTTPException(status_code=404, detail="event page not found")


@app.post("/api/public/events/{event_id}/touchpoints/{touchpoint_id}/interactions")
def public_touchpoint_interaction(
    request: Request,
    event_id: str,
    touchpoint_id: str,
    payload: dict | None = None,
):
    verify_mutation_origin(request)
    require_public_event_ready(event_id)
    body = payload or {}
    interaction_type = body.get("interaction_type", "scan")
    anonymous_interaction_id = body.get("anonymous_interaction_id")
    existing_interaction = None
    if anonymous_interaction_id:
        existing_interaction = STORE.find_touchpoint_interaction(
            event_id=event_id,
            touchpoint_id=touchpoint_id,
            anonymous_interaction_id=anonymous_interaction_id,
            interaction_type=interaction_type,
        )
    try:
        interaction = record_touchpoint_interaction(
            event_id=event_id,
            touchpoint_id=touchpoint_id,
            interaction_type=interaction_type,
            source=body.get("source", "demo"),
            anonymous_interaction_id=anonymous_interaction_id,
            metadata=body.get("metadata") or {},
        )
        if existing_interaction is None:
            METRICS.increment("public_touchpoint_interactions_total")
        return interaction
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/public/events/{event_id}/coupons/{coupon_rule_id}/claim")
def public_coupon_claim(
    request: Request,
    event_id: str,
    coupon_rule_id: str,
    payload: dict | None = None,
):
    verify_mutation_origin(request)
    require_public_event_ready(event_id)
    body = payload or {}
    anonymous_interaction_id = body.get("anonymous_interaction_id", "")
    existing_redemption = None
    if anonymous_interaction_id:
        existing_redemption = STORE.find_coupon_redemption_for_anonymous(
            event_id=event_id,
            coupon_rule_id=coupon_rule_id,
            anonymous_interaction_id=anonymous_interaction_id,
        )
    try:
        redemption = claim_coupon(
            event_id=event_id,
            coupon_rule_id=coupon_rule_id,
            anonymous_interaction_id=anonymous_interaction_id,
        )
        if existing_redemption is None:
            METRICS.increment("public_coupon_claims_total")
        return redemption
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/public/events/{event_id}/coupon-redemptions/{redemption_id}/redeem")
def public_coupon_redeem(
    request: Request,
    event_id: str,
    redemption_id: str,
):
    verify_mutation_origin(request)
    require_public_event_ready(event_id)
    existing_redemption = STORE.get_coupon_redemption(event_id, redemption_id)
    already_redeemed = bool(existing_redemption and existing_redemption.status == "redeemed")
    try:
        redemption = redeem_coupon(event_id=event_id, redemption_id=redemption_id)
        if not already_redeemed:
            METRICS.increment("public_coupon_redemptions_total")
        return redemption
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    touchpoint_summary = summarize_touchpoint_metrics(event_id)
    report = generate_review_report(
        plan=plan,
        recovery_actions=STORE.list_recovery_actions(event_id),
        audit_logs=STORE.list_audit_logs(event_id),
        metrics=STORE.list_operational_metrics(event_id),
        touchpoint_summary=touchpoint_summary,
        merchant_outcomes=touchpoint_summary["merchant_outcomes"],
        extension_tasks=touchpoint_summary["extension_tasks"],
    )
    runtime_result = AgentRuntime().run_review_generation(
        event_id=event_id,
        metrics=STORE.list_operational_metrics(event_id),
        incidents=STORE.list_incidents(event_id),
        notices=STORE.list_public_notices(event_id),
        proposals=STORE.list_recovery_proposals(event_id),
    )
    persist_agent_runtime_result(runtime_result)
    STORE.save_report(report)
    METRICS.increment("review_reports_total")
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
