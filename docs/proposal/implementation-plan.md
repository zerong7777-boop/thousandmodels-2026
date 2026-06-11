# 智引濠江 v0.2 Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the current v0.1 clickable demo into a v0.2 product-shaped old-district event operations Agent MVP with separate organizer, merchant, tourist H5, and review entry points.

**Architecture:** Keep the existing FastAPI + Pydantic + SQLite key-value store and React/Vite/Ant Design foundation, but refactor the domain around `PlanVersion`, `Incident`, `RecoveryProposal`, `MerchantTask`, `PublicNotice`, `AgentTrace`, and `OperationalMetric`. The deterministic demo path remains mandatory; multi-Agent behavior is represented through structured deterministic trace first, with Qwen/QwenPaw remaining optional behind adapters.

**Tech Stack:** FastAPI, Pydantic, SQLite, pytest, React 19, Vite, TypeScript, Ant Design, Vitest, Testing Library.

---

## 0. Scope Lock

This plan implements `docs/proposal/v0.2-redesign.md`. It supersedes the previous v0.1 implementation plan in this file.

Hard constraints:

- Do not connect real merchants.
- Do not add hardware, AI glasses, IoT, or robotics.
- Do not add real traffic prediction.
- Do not train or fine-tune models.
- Do not make Qwen/QwenPaw required for the local demo.
- Do not put organizer, merchant, tourist, and review experiences into one single demo page.
- Do not treat merchant and tourist screens as static preview cards inside the organizer screen.

The v0.2 demo must run without `DASHSCOPE_API_KEY`.

## 1. Current Baseline

Current useful foundation:

- Backend exists under `apps/api/app`.
- Frontend exists under `apps/web/src`.
- Existing tests exist under `apps/api/tests` and `apps/web/tests`.
- Existing deterministic loop already covers seed -> generate plan -> approve plan -> merchant packs -> public event -> inventory/weather trigger -> approve recovery -> report.

Current maturity gap:

- `apps/web/src/App.tsx` switches views in one in-memory shell instead of using role-specific entry points.
- `EventPlan` is still the main plan object; there is no explicit `PlanVersion`.
- Recovery approval appends a tourist notice, but does not create a new plan version or structured diff.
- Agent behavior is not visible as a structured `AgentTrace`.
- Merchant state update records state but does not automatically create an `Incident`.
- Tourist H5 uses route strings, not route point objects with story/task/status.
- Review report does not cite operational metrics.

## 2. Target File Structure

Keep existing files where possible. Add focused files only where they create clearer boundaries.

```text
apps/api/app/
  schemas.py                         # extend with v0.2 domain contracts
  store.py                           # add v0.2 collections and accessors
  main.py                            # add v0.2 endpoints and preserve existing compatibility endpoints
  seed.py                            # seed route points, event summary, metrics, and runtime state
  agents/
    deterministic.py                 # keep existing backend, add deterministic trace builders
    trace_builder.py                 # new: structured AgentTrace factory
  services/
    planning.py                      # add PlanVersion + MerchantTask generation
    incidents.py                     # new: merchant/weather state -> Incident
    recovery.py                      # change recovery into proposal + patch + version update
    publication.py                   # new: public H5 projection from current approved plan
    review.py                        # cite OperationalMetric and incident timeline

apps/api/tests/
  test_v02_contracts.py
  test_v02_agent_trace.py
  test_v02_plan_versioning.py
  test_v02_incident_recovery.py
  test_v02_public_projection.py
  test_v02_review_metrics.py

apps/web/src/
  App.tsx                            # replace in-memory view switch with route resolver
  api.ts                             # add event_id and merchant_id aware methods
  types.ts                           # mirror v0.2 schemas
  components/
    AgentTracePanel.tsx              # new: visible Agent evidence panel
    PlanVersionDiff.tsx              # new: v1 -> v2 diff
    IncidentQueue.tsx                # new: exception center panel
    RoutePointTimeline.tsx           # new: route point cards/timeline
    MetricSummary.tsx                # new: review metric cards
  pages/
    OrganizerHomePage.tsx            # new: /organizer
    ActivityWorkspacePage.tsx        # new: /organizer/events/:eventId
    ExceptionCenterPage.tsx          # new: /organizer/events/:eventId/exceptions
    MerchantWorkbenchPage.tsx        # new: /merchant/:merchantId
    TouristH5Page.tsx                # new: /public/events/:eventId
    ReviewCenterPage.tsx             # new: /review/:eventId
```

Deprecated after migration:

- `apps/web/src/pages/OrganizerPage.tsx`
- `apps/web/src/pages/MerchantPage.tsx`
- `apps/web/src/pages/TouristPage.tsx`

Do not delete deprecated pages until the new route tests pass.

## 3. API Contract Targets

Add or update these endpoints:

```text
POST /api/events/demo/seed
GET  /api/events
GET  /api/events/{event_id}
POST /api/events/{event_id}/generate-plan
GET  /api/events/{event_id}/plans
GET  /api/events/{event_id}/plans/current
POST /api/events/{event_id}/plans/{version}/approve
GET  /api/events/{event_id}/agent-traces
GET  /api/events/{event_id}/merchant-tasks
GET  /api/merchants/{merchant_id}/workbench?event_id=demo-night-tour
POST /api/merchants/{merchant_id}/runtime-state
GET  /api/events/{event_id}/incidents
POST /api/events/{event_id}/trigger/weather
POST /api/events/{event_id}/incidents/{incident_id}/recovery-proposals
POST /api/events/{event_id}/recovery-proposals/{proposal_id}/approve
GET  /api/public/events/{event_id}
POST /api/events/{event_id}/review-report
GET  /api/events/{event_id}/review-report
```

Keep these compatibility endpoints until frontend migration is complete:

```text
GET  /api/events/{event_id}/plan
POST /api/events/{event_id}/approve-plan
GET  /api/events/{event_id}/merchant-packs
GET  /api/events/{event_id}/recovery-actions
POST /api/recovery-actions/{action_id}/approve
```

## 4. Task List

### Task 1: Baseline Guard Tests

**Purpose:** Lock current working behavior before refactoring.

**Files:**

- Modify: `apps/api/tests/test_api_flow.py`
- Modify: `apps/web/tests/app.test.tsx`

- [ ] **Step 1: Add current-loop smoke assertions to backend test**

In `apps/api/tests/test_api_flow.py`, keep the existing `test_complete_demo_loop` and add two assertions after recovery approval:

```python
    logs = client.get("/api/events/demo-night-tour/audit-logs")
    assert logs.status_code == 200
    assert any(item["action_type"] == "approve_recovery" for item in logs.json())

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
```

- [ ] **Step 2: Run backend baseline**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest -q
```

Expected: all existing backend tests pass.

- [ ] **Step 3: Add frontend baseline wording guard**

In `apps/web/tests/app.test.tsx`, keep the existing test and add:

```tsx
expect(screen.getByText(/福隆新街/)).toBeInTheDocument();
expect(screen.getByText(/旧区/)).toBeInTheDocument();
```

- [ ] **Step 4: Run frontend baseline**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test
```

Expected: current frontend smoke test passes before v0.2 changes begin.

### Task 2: Add v0.2 Domain Contracts

**Purpose:** Make product maturity visible in the backend model before changing UI.

**Files:**

- Modify: `apps/api/app/schemas.py`
- Create: `apps/api/tests/test_v02_contracts.py`
- Modify: `apps/web/src/types.ts`

- [ ] **Step 1: Write backend contract tests**

Create `apps/api/tests/test_v02_contracts.py`:

```python
from app.schemas import (
    AgentStep,
    AgentTrace,
    Incident,
    MerchantTask,
    OperationalMetric,
    PlanVersion,
    PublicNotice,
    RecoveryProposal,
    RoutePoint,
)


def test_plan_version_contract_contains_diff_and_route_points():
    route_point = RoutePoint(
        point_id="rp001",
        name="福隆新街开场点",
        type="street",
        is_indoor=False,
        estimated_stay_minutes=20,
        story="以老字号街景作为夜游起点。",
        linked_merchants=["m001"],
        visitor_task="完成老字号问答",
        rainy_day_score=2,
        crowd_risk="medium",
        current_status="active",
    )
    plan = PlanVersion(
        plan_id="demo-night-tour:v1",
        event_id="demo-night-tour",
        version=1,
        status="draft",
        created_by="OrchestratorAgent",
        created_reason="initial_plan",
        route_points=[route_point],
        merchant_assignments=["m001"],
        budget_plan={"total_mop": 50000, "contingency_mop": 5000},
        risk_plan=["inventory", "weather"],
        diff_from_previous=[],
    )
    assert plan.route_points[0].point_id == "rp001"
    assert plan.diff_from_previous == []


def test_incident_recovery_notice_and_trace_contracts():
    incident = Incident(
        incident_id="inc_inventory_m001",
        event_id="demo-night-tour",
        type="inventory",
        severity="high",
        source="merchant",
        trigger_detail="m001 sold_out",
        affected_route_points=["rp001"],
        affected_merchants=["m001"],
        status="open",
        created_at="2026-06-09T12:00:00Z",
    )
    proposal = RecoveryProposal(
        proposal_id="rec_inc_inventory_m001",
        incident_id=incident.incident_id,
        event_id="demo-night-tour",
        recommended_changes=["replace route point rp001 with rp007"],
        plan_patch={"replace_route_points": [{"from": "rp001", "to": "rp007"}]},
        merchant_task_patch={"m001": "pause_visitors", "m007": "activate_backup"},
        public_notice_patch="福隆老饼家库存售罄，路线调整至新街手信铺。",
        impact_summary="影响 1 个路线点和 2 个商户任务。",
        requires_approval=True,
        approval_status="pending",
    )
    notice = PublicNotice(
        notice_id="notice_rec_inc_inventory_m001",
        event_id="demo-night-tour",
        plan_version=2,
        audience="tourist",
        message=proposal.public_notice_patch,
        reason="inventory_recovery",
        publish_status="draft",
    )
    trace = AgentTrace(
        trace_id="trace_plan_v1",
        event_id="demo-night-tour",
        trigger="generate_plan",
        steps=[
            AgentStep(
                agent_name="RoutePlannerAgent",
                input_refs=["event_brief:demo-night-tour"],
                tool_calls=[{"tool": "route.check", "result": "rain backup available"}],
                structured_output={"route_points": ["rp001", "rp002"]},
                decision_reason="route fits night-tour timing",
                confidence=0.88,
                requires_human_approval=False,
            )
        ],
        final_output_ref="plan:demo-night-tour:v1",
        human_decision_ref=None,
    )
    assert proposal.requires_approval is True
    assert notice.publish_status == "draft"
    assert trace.steps[0].agent_name == "RoutePlannerAgent"


def test_merchant_task_and_metric_contracts():
    task = MerchantTask(
        task_id="task_demo_m001_v1",
        event_id="demo-night-tour",
        merchant_id="m001",
        plan_version=1,
        role="集合与开场试吃",
        time_slot="18:10-18:35",
        visitor_task="完成老字号问答",
        preparation_items=["准备 80 份试吃", "张贴活动二维码"],
        promo_text="凭 H5 打卡领取限定优惠。",
        fallback_instruction="库存不足时暂停导流并提示主办方。",
        task_status="active",
    )
    metric = OperationalMetric(
        metric_id="metric_h5_visits",
        event_id="demo-night-tour",
        name="h5_visits",
        value=428,
        unit="visits",
        source="mock",
        captured_at="2026-06-09T12:00:00Z",
    )
    assert task.plan_version == 1
    assert metric.value == 428
```

- [ ] **Step 2: Run contract tests and confirm failure**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_contracts.py -q
```

Expected: fails because the v0.2 schema classes are not defined.

- [ ] **Step 3: Extend `apps/api/app/schemas.py`**

Add these classes below existing models. Use the same field names as the test:

```python
class EventSummary(BaseModel):
    event_id: str
    title: str
    area: str
    date: str
    time_window: str
    status: Literal["draft", "pending_approval", "active", "ended"]
    current_plan_version: int
    public_release_status: Literal["draft", "published", "stale"]


class RoutePoint(BaseModel):
    point_id: str
    name: str
    type: str
    is_indoor: bool
    estimated_stay_minutes: int = Field(gt=0)
    story: str
    linked_merchants: list[str]
    visitor_task: str
    rainy_day_score: int = Field(ge=1, le=5)
    crowd_risk: Literal["low", "medium", "high"]
    current_status: Literal["active", "paused", "replaced"]


class PlanVersion(BaseModel):
    plan_id: str
    event_id: str
    version: int = Field(ge=1)
    status: Literal["draft", "approved", "superseded"]
    created_by: str
    created_reason: str
    route_points: list[RoutePoint]
    merchant_assignments: list[str]
    budget_plan: dict
    risk_plan: list[str]
    diff_from_previous: list[str]
    approved_by: str | None = None
    approved_at: str | None = None


class MerchantTask(BaseModel):
    task_id: str
    event_id: str
    merchant_id: str
    plan_version: int
    role: str
    time_slot: str
    visitor_task: str
    preparation_items: list[str]
    promo_text: str
    fallback_instruction: str
    task_status: Literal["draft", "active", "paused", "replaced", "completed"]


class Incident(BaseModel):
    incident_id: str
    event_id: str
    type: Literal["inventory", "queue", "weather", "merchant_unavailable"]
    severity: Literal["low", "medium", "high"]
    source: Literal["merchant", "weather_tool", "organizer", "system"]
    trigger_detail: str
    affected_route_points: list[str]
    affected_merchants: list[str]
    status: Literal["open", "proposal_ready", "approved", "closed"]
    created_at: str


class RecoveryProposal(BaseModel):
    proposal_id: str
    incident_id: str
    event_id: str
    recommended_changes: list[str]
    plan_patch: dict
    merchant_task_patch: dict
    public_notice_patch: str
    impact_summary: str
    requires_approval: bool = True
    approval_status: Literal["pending", "approved", "rejected"] = "pending"


class PublicNotice(BaseModel):
    notice_id: str
    event_id: str
    plan_version: int
    audience: Literal["tourist", "merchant", "organizer"]
    message: str
    reason: str
    publish_status: Literal["draft", "published"]
    published_at: str | None = None


class AgentStep(BaseModel):
    agent_name: str
    input_refs: list[str]
    tool_calls: list[dict]
    structured_output: dict
    decision_reason: str
    confidence: float = Field(ge=0, le=1)
    requires_human_approval: bool


class AgentTrace(BaseModel):
    trace_id: str
    event_id: str
    trigger: str
    steps: list[AgentStep]
    final_output_ref: str
    human_decision_ref: str | None = None


class OperationalMetric(BaseModel):
    metric_id: str
    event_id: str
    name: str
    value: float
    unit: str
    source: Literal["mock", "system", "merchant", "public_h5"]
    captured_at: str
```

- [ ] **Step 4: Mirror types in `apps/web/src/types.ts`**

Add TypeScript interfaces with identical field names:

```ts
export interface RoutePoint {
  point_id: string;
  name: string;
  type: string;
  is_indoor: boolean;
  estimated_stay_minutes: number;
  story: string;
  linked_merchants: string[];
  visitor_task: string;
  rainy_day_score: number;
  crowd_risk: "low" | "medium" | "high";
  current_status: "active" | "paused" | "replaced";
}

export interface PlanVersion {
  plan_id: string;
  event_id: string;
  version: number;
  status: "draft" | "approved" | "superseded";
  created_by: string;
  created_reason: string;
  route_points: RoutePoint[];
  merchant_assignments: string[];
  budget_plan: Record<string, unknown>;
  risk_plan: string[];
  diff_from_previous: string[];
  approved_by?: string | null;
  approved_at?: string | null;
}

export interface AgentStep {
  agent_name: string;
  input_refs: string[];
  tool_calls: Array<Record<string, unknown>>;
  structured_output: Record<string, unknown>;
  decision_reason: string;
  confidence: number;
  requires_human_approval: boolean;
}

export interface AgentTrace {
  trace_id: string;
  event_id: string;
  trigger: string;
  steps: AgentStep[];
  final_output_ref: string;
  human_decision_ref?: string | null;
}
```

Also add `MerchantTask`, `Incident`, `RecoveryProposal`, `PublicNotice`, and `OperationalMetric` interfaces using the backend field names.

- [ ] **Step 5: Run contract tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_contracts.py -q
```

Expected: `3 passed`.

### Task 3: Extend Store and Seed Data for v0.2 Objects

**Purpose:** Store v0.2 state as first-class records.

**Files:**

- Modify: `apps/api/app/store.py`
- Modify: `apps/api/app/seed.py`
- Create: `apps/api/tests/test_v02_seed_store.py`

- [ ] **Step 1: Write seed/store test**

Create `apps/api/tests/test_v02_seed_store.py`:

```python
from app.seed import seed_demo
from app.store import MVPStore


def test_seed_demo_creates_v02_collections(tmp_path):
    store = MVPStore(tmp_path / "demo.sqlite3")
    brief = seed_demo(store)

    assert brief.event_id == "demo-night-tour"
    assert store.get_event_summary("demo-night-tour").title == "福隆新街周末旧区夜游"
    assert len(store.list_route_points()) >= 6
    assert len(store.list_runtime_states()) >= 8
    assert len(store.list_operational_metrics("demo-night-tour")) >= 5
```

- [ ] **Step 2: Add store collections**

In `apps/api/app/store.py`, import the new schema classes and add methods:

```python
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


def list_merchant_tasks(self, event_id: str, merchant_id: str | None = None) -> list[MerchantTask]:
    tasks = self.list_models("merchant_tasks", MerchantTask, prefix=f"{event_id}:")
    if merchant_id:
        return [task for task in tasks if task.merchant_id == merchant_id]
    return tasks
```

Add equivalent `save_incident`, `get_incident`, `list_incidents`, `save_recovery_proposal`, `get_recovery_proposal`, `list_recovery_proposals`, `save_public_notice`, `list_public_notices`, `save_agent_trace`, `list_agent_traces`, `save_operational_metric`, and `list_operational_metrics` methods using collection names matching the method names.

- [ ] **Step 3: Update `clear_demo` collections**

Add these collection names to `clear_demo`:

```python
"events",
"route_points",
"plan_versions",
"merchant_tasks",
"incidents",
"recovery_proposals",
"public_notices",
"agent_traces",
"operational_metrics",
```

- [ ] **Step 4: Seed v0.2 objects**

In `apps/api/app/seed.py`, after existing merchants/runtime states are saved:

```python
store.save_event_summary(
    EventSummary(
        event_id=brief.event_id,
        title="福隆新街周末旧区夜游",
        area=brief.area,
        date=brief.date,
        time_window=brief.time_window,
        status="draft",
        current_plan_version=0,
        public_release_status="draft",
    )
)
```

Create at least 6 `RoutePoint` records:

```python
RoutePoint(
    point_id="rp001",
    name="福隆新街开场点",
    type="street",
    is_indoor=False,
    estimated_stay_minutes=20,
    story="以老字号街景作为夜游起点。",
    linked_merchants=["m001"],
    visitor_task="完成老字号问答",
    rainy_day_score=2,
    crowd_risk="medium",
    current_status="active",
)
```

Add 5 mock `OperationalMetric` records for `h5_visits`, `checkins_completed`, `avg_queue_minutes`, `incident_response_minutes`, and `budget_spent_mop`.

- [ ] **Step 5: Run seed/store tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_seed_store.py -q
```

Expected: `1 passed`.

### Task 4: Deterministic Multi-Agent Trace and PlanVersion v1

**Purpose:** Show visible Agent evidence without requiring a model API.

**Files:**

- Create: `apps/api/app/agents/trace_builder.py`
- Modify: `apps/api/app/services/planning.py`
- Create: `apps/api/tests/test_v02_agent_trace.py`

- [ ] **Step 1: Write trace test**

Create `apps/api/tests/test_v02_agent_trace.py`:

```python
from app.agents.trace_builder import build_planning_trace
from app.seed import seed_demo
from app.services.planning import generate_plan_version, generate_merchant_tasks
from app.store import MVPStore


def test_deterministic_plan_version_has_agent_trace(tmp_path):
    store = MVPStore(tmp_path / "demo.sqlite3")
    brief = seed_demo(store)

    plan = generate_plan_version(
        brief=brief,
        merchants=store.list_merchants(),
        route_points=store.list_route_points(),
        version=1,
        reason="initial_plan",
    )
    trace = build_planning_trace(brief.event_id, plan)
    tasks = generate_merchant_tasks(plan, store.list_merchants())

    assert plan.version == 1
    assert plan.status == "draft"
    assert len(trace.steps) >= 5
    assert {"OrchestratorAgent", "RoutePlannerAgent", "MerchantMatcherAgent"}.issubset(
        {step.agent_name for step in trace.steps}
    )
    assert len(tasks) >= 5
    assert all(task.plan_version == 1 for task in tasks)
```

- [ ] **Step 2: Implement `trace_builder.py`**

Create `apps/api/app/agents/trace_builder.py`:

```python
from app.schemas import AgentStep, AgentTrace, PlanVersion


def build_planning_trace(event_id: str, plan: PlanVersion) -> AgentTrace:
    steps = [
        AgentStep(
            agent_name="OrchestratorAgent",
            input_refs=[f"event_brief:{event_id}"],
            tool_calls=[{"tool": "task.decompose", "result": "6 planning tasks"}],
            structured_output={"tasks": ["narrative", "route", "merchant", "risk", "budget", "publication"]},
            decision_reason="活动目标需要同时协调文化叙事、路线、商户和风险。",
            confidence=0.9,
            requires_human_approval=False,
        ),
        AgentStep(
            agent_name="CulturalNarrativeAgent",
            input_refs=["knowledge:fulong-new-street", "route_points"],
            tool_calls=[{"tool": "knowledge.lookup", "result": "old district story snippets"}],
            structured_output={"theme": "旧城夜光", "story_points": [p.name for p in plan.route_points[:3]]},
            decision_reason="使用旧区故事强化活动辨识度。",
            confidence=0.86,
            requires_human_approval=False,
        ),
        AgentStep(
            agent_name="RoutePlannerAgent",
            input_refs=["route_points", "weather:mock"],
            tool_calls=[{"tool": "route.check", "result": "primary and rainy route available"}],
            structured_output={"route_points": [p.point_id for p in plan.route_points]},
            decision_reason="路线控制在活动时间窗内，并保留室内备用点。",
            confidence=0.88,
            requires_human_approval=False,
        ),
        AgentStep(
            agent_name="MerchantMatcherAgent",
            input_refs=["merchants", "event_brief"],
            tool_calls=[{"tool": "merchant.select", "result": plan.merchant_assignments}],
            structured_output={"merchant_assignments": plan.merchant_assignments},
            decision_reason="选择夜间适配度高且可承接活动任务的商户。",
            confidence=0.84,
            requires_human_approval=False,
        ),
        AgentStep(
            agent_name="RiskAgent",
            input_refs=["runtime_states", "budget", "route_points"],
            tool_calls=[{"tool": "risk.scan", "result": plan.risk_plan}],
            structured_output={"risks": plan.risk_plan},
            decision_reason="库存、天气和排队风险需要在发布前进入预案。",
            confidence=0.82,
            requires_human_approval=True,
        ),
    ]
    return AgentTrace(
        trace_id=f"trace_{event_id}_v{plan.version}",
        event_id=event_id,
        trigger="generate_plan",
        steps=steps,
        final_output_ref=f"plan:{event_id}:v{plan.version}",
        human_decision_ref=None,
    )
```

- [ ] **Step 3: Add planning service functions**

In `apps/api/app/services/planning.py`, add:

```python
def generate_plan_version(
    brief: EventBrief,
    merchants: list[MerchantProfile],
    route_points: list[RoutePoint],
    version: int,
    reason: str,
) -> PlanVersion:
    selected_merchants = [m.merchant_id for m in merchants[:6]]
    selected_points = route_points[:6]
    return PlanVersion(
        plan_id=f"{brief.event_id}:v{version}",
        event_id=brief.event_id,
        version=version,
        status="draft",
        created_by="OrchestratorAgent",
        created_reason=reason,
        route_points=selected_points,
        merchant_assignments=selected_merchants,
        budget_plan={
            "total_mop": brief.budget_mop,
            "merchant_support_mop": int(brief.budget_mop * 0.35),
            "marketing_mop": int(brief.budget_mop * 0.25),
            "staffing_mop": int(brief.budget_mop * 0.25),
            "contingency_mop": brief.budget_mop - int(brief.budget_mop * 0.85),
        },
        risk_plan=["inventory", "queue", "weather"],
        diff_from_previous=[] if version == 1 else [f"created version {version} from recovery proposal"],
    )
```

Add `generate_merchant_tasks(plan, merchants)` that returns `MerchantTask` records with `task_id=f"task_{plan.event_id}_{merchant_id}_v{plan.version}"`, `plan_version=plan.version`, and `task_status="active"`.

- [ ] **Step 4: Run trace test**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_agent_trace.py -q
```

Expected: `1 passed`.

### Task 5: PlanVersion API and Approval Gate

**Purpose:** Replace the weak “single EventPlan approval” path with explicit plan versions.

**Files:**

- Modify: `apps/api/app/main.py`
- Create: `apps/api/tests/test_v02_plan_versioning.py`

- [ ] **Step 1: Write API versioning test**

Create `apps/api/tests/test_v02_plan_versioning.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_generate_and_approve_plan_version_v1():
    client = TestClient(app)
    client.post("/api/events/demo/seed")

    response = client.post("/api/events/demo-night-tour/generate-plan")
    assert response.status_code == 200
    body = response.json()
    assert body["current_plan"]["version"] == 1
    assert len(body["agent_trace"]["steps"]) >= 5

    plans = client.get("/api/events/demo-night-tour/plans")
    assert plans.status_code == 200
    assert plans.json()[0]["version"] == 1

    approved = client.post("/api/events/demo-night-tour/plans/1/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    current = client.get("/api/events/demo-night-tour/plans/current")
    assert current.status_code == 200
    assert current.json()["version"] == 1
    assert current.json()["status"] == "approved"
```

- [ ] **Step 2: Update generate-plan endpoint**

In `apps/api/app/main.py`, keep the legacy return-compatible `EventPlan` storage, but make the endpoint return the v0.2 shape:

```python
plan_v1 = generate_plan_version(
    brief=brief,
    merchants=STORE.list_merchants(),
    route_points=STORE.list_route_points(),
    version=1,
    reason="initial_plan",
)
trace = build_planning_trace(event_id, plan_v1)
tasks = generate_merchant_tasks(plan_v1, STORE.list_merchants())
STORE.save_plan_version(plan_v1)
STORE.save_agent_trace(trace)
STORE.save_merchant_tasks(event_id, tasks)
```

Return:

```python
return {"current_plan": plan_v1, "agent_trace": trace, "merchant_tasks": tasks}
```

If legacy frontend still expects `EventPlan`, preserve `GET /api/events/{event_id}/plan` until Task 9 is complete.

- [ ] **Step 3: Add v0.2 plan endpoints**

Add:

```python
@app.get("/api/events/{event_id}/plans")
def list_plan_versions(event_id: str):
    return STORE.list_plan_versions(event_id)


@app.get("/api/events/{event_id}/plans/current")
def current_plan_version(event_id: str):
    event = STORE.get_event_summary(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    plan = STORE.get_plan_version(event_id, event.current_plan_version)
    if not plan:
        raise HTTPException(status_code=404, detail="current plan not found")
    return plan


@app.post("/api/events/{event_id}/plans/{version}/approve")
def approve_plan_version(event_id: str, version: int):
    plan = STORE.get_plan_version(event_id, version)
    event = STORE.get_event_summary(event_id)
    if not plan or not event:
        raise HTTPException(status_code=404, detail="plan or event not found")
    plan.status = "approved"
    plan.approved_by = "demo-organizer"
    plan.approved_at = datetime.now(UTC).isoformat()
    event.status = "active"
    event.current_plan_version = version
    event.public_release_status = "published"
    STORE.save_plan_version(plan)
    STORE.save_event_summary(event)
    audit(event_id, "organizer", "demo-organizer", "approve_plan_version", f"approved v{version}")
    return plan
```

- [ ] **Step 4: Run versioning test**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_plan_versioning.py -q
```

Expected: `1 passed`.

### Task 6: Merchant State -> Incident -> RecoveryProposal -> PlanVersion v2

**Purpose:** Create the real recovery loop required by the spec.

**Files:**

- Create: `apps/api/app/services/incidents.py`
- Modify: `apps/api/app/services/recovery.py`
- Modify: `apps/api/app/main.py`
- Create: `apps/api/tests/test_v02_incident_recovery.py`

- [ ] **Step 1: Write incident recovery test**

Create `apps/api/tests/test_v02_incident_recovery.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_merchant_inventory_update_creates_incident_and_v2_after_approval():
    client = TestClient(app)
    client.post("/api/events/demo/seed")
    client.post("/api/events/demo-night-tour/generate-plan")
    client.post("/api/events/demo-night-tour/plans/1/approve")

    state = client.post(
        "/api/merchants/m001/runtime-state",
        json={
            "inventory_status": "sold_out",
            "queue_status": "busy",
            "available_for_visitors": False,
            "temporary_note": "杏仁饼售罄",
        },
    )
    assert state.status_code == 200

    incidents = client.get("/api/events/demo-night-tour/incidents")
    assert incidents.status_code == 200
    incident = incidents.json()[0]
    assert incident["type"] == "inventory"
    assert incident["status"] in {"open", "proposal_ready"}

    proposal = client.post(
        f"/api/events/demo-night-tour/incidents/{incident['incident_id']}/recovery-proposals"
    )
    assert proposal.status_code == 200
    assert proposal.json()["approval_status"] == "pending"

    approved = client.post(
        f"/api/events/demo-night-tour/recovery-proposals/{proposal.json()['proposal_id']}/approve"
    )
    assert approved.status_code == 200
    assert approved.json()["current_plan"]["version"] == 2
    assert approved.json()["current_plan"]["diff_from_previous"]
    assert approved.json()["notice"]["publish_status"] == "published"

    public_event = client.get("/api/public/events/demo-night-tour")
    assert public_event.status_code == 200
    assert public_event.json()["current_plan_version"] == 2
    assert public_event.json()["notices"]
```

- [ ] **Step 2: Implement incident builder**

Create `apps/api/app/services/incidents.py`:

```python
from datetime import UTC, datetime

from app.schemas import Incident, MerchantRuntimeState


def incident_from_runtime_state(event_id: str, state: MerchantRuntimeState) -> Incident | None:
    if state.inventory_status == "sold_out":
        return Incident(
            incident_id=f"inc_{event_id}_{state.merchant_id}_inventory",
            event_id=event_id,
            type="inventory",
            severity="high",
            source="merchant",
            trigger_detail=f"{state.merchant_id} inventory_status=sold_out",
            affected_route_points=["rp001"],
            affected_merchants=[state.merchant_id],
            status="open",
            created_at=datetime.now(UTC).isoformat(),
        )
    if state.queue_status == "overloaded":
        return Incident(
            incident_id=f"inc_{event_id}_{state.merchant_id}_queue",
            event_id=event_id,
            type="queue",
            severity="medium",
            source="merchant",
            trigger_detail=f"{state.merchant_id} queue_status=overloaded",
            affected_route_points=["rp001"],
            affected_merchants=[state.merchant_id],
            status="open",
            created_at=datetime.now(UTC).isoformat(),
        )
    return None
```

- [ ] **Step 3: Update runtime-state endpoint**

In `apps/api/app/main.py`, after `STORE.save_runtime_state(next_state)`:

```python
incident = incident_from_runtime_state("demo-night-tour", next_state)
if incident:
    STORE.save_incident(incident)
    audit("demo-night-tour", "system", "incident-detector", "create_incident", incident.trigger_detail)
```

Return:

```python
return {"runtime_state": next_state, "incident": incident}
```

Update frontend later to read `runtime_state` from this response.

- [ ] **Step 4: Implement proposal builder and approval**

In `apps/api/app/services/recovery.py`, add:

```python
def build_recovery_proposal(incident: Incident) -> RecoveryProposal:
    if incident.type == "inventory":
        return RecoveryProposal(
            proposal_id=f"rec_{incident.incident_id}",
            incident_id=incident.incident_id,
            event_id=incident.event_id,
            recommended_changes=[
                "暂停库存售罄商户导流",
                "启用新街手信铺作为备用点",
                "向游客 H5 发布路线调整说明",
            ],
            plan_patch={"replace_route_points": [{"from": "rp001", "to": "rp007"}]},
            merchant_task_patch={incident.affected_merchants[0]: "paused", "m007": "active_backup"},
            public_notice_patch="福隆老饼家库存售罄，路线临时调整至新街手信铺。",
            impact_summary="影响 1 个路线点、2 个商户任务和游客端路线提示。",
            requires_approval=True,
            approval_status="pending",
        )
    return RecoveryProposal(
        proposal_id=f"rec_{incident.incident_id}",
        incident_id=incident.incident_id,
        event_id=incident.event_id,
        recommended_changes=["切换室内备用路线"],
        plan_patch={"rain_route": True},
        merchant_task_patch={"m008": "activate_backup"},
        public_notice_patch="因强降雨，活动切换至室内备用路线。",
        impact_summary="影响户外路线点和雨天备用点。",
        requires_approval=True,
        approval_status="pending",
    )
```

Add `apply_recovery_proposal(current_plan, proposal, route_points)` that returns `PlanVersion(version=current_plan.version + 1, status="approved", diff_from_previous=proposal.recommended_changes, ...)`.

- [ ] **Step 5: Add incident/proposal endpoints**

In `apps/api/app/main.py`, add:

```python
@app.get("/api/events/{event_id}/incidents")
def list_incidents(event_id: str):
    return STORE.list_incidents(event_id)


@app.post("/api/events/{event_id}/incidents/{incident_id}/recovery-proposals")
def create_recovery_proposal(event_id: str, incident_id: str):
    incident = STORE.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="incident not found")
    proposal = build_recovery_proposal(incident)
    incident.status = "proposal_ready"
    STORE.save_incident(incident)
    STORE.save_recovery_proposal(proposal)
    audit(event_id, "agent", "RecoveryAgent", "create_recovery_proposal", proposal.impact_summary)
    return proposal
```

Add approval endpoint that:

- marks proposal approved,
- creates plan version `current + 1`,
- saves updated merchant tasks,
- publishes `PublicNotice`,
- updates event `current_plan_version`,
- records audit and trace human decision reference,
- returns `{"proposal": proposal, "current_plan": next_plan, "notice": notice}`.

- [ ] **Step 6: Run recovery test**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_incident_recovery.py -q
```

Expected: `1 passed`.

### Task 7: Public H5 Projection and Review Metrics

**Purpose:** Make tourist and review data product-real, not admin previews.

**Files:**

- Create: `apps/api/app/services/publication.py`
- Modify: `apps/api/app/services/review.py`
- Modify: `apps/api/app/main.py`
- Create: `apps/api/tests/test_v02_public_projection.py`
- Create: `apps/api/tests/test_v02_review_metrics.py`

- [ ] **Step 1: Write public projection test**

Create `apps/api/tests/test_v02_public_projection.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_public_event_uses_route_points_and_notices():
    client = TestClient(app)
    client.post("/api/events/demo/seed")
    client.post("/api/events/demo-night-tour/generate-plan")
    client.post("/api/events/demo-night-tour/plans/1/approve")

    response = client.get("/api/public/events/demo-night-tour")
    assert response.status_code == 200
    body = response.json()
    assert body["event_id"] == "demo-night-tour"
    assert body["current_plan_version"] == 1
    assert body["route_points"]
    assert {"name", "story", "visitor_task", "linked_merchants"}.issubset(body["route_points"][0])
```

- [ ] **Step 2: Implement `publication.py`**

Create `apps/api/app/services/publication.py`:

```python
def build_public_event(event, plan, notices):
    return {
        "event_id": event.event_id,
        "title": event.title,
        "area": event.area,
        "status": event.status,
        "current_plan_version": plan.version,
        "route_points": [point.model_dump() for point in plan.route_points],
        "notices": [notice.model_dump() for notice in notices if notice.audience == "tourist"],
    }
```

- [ ] **Step 3: Update public endpoint**

In `apps/api/app/main.py`, replace the `PublicEvent` response path with `build_public_event(event, plan, notices)`. Keep old `PublicEvent` schema only if tests still import it.

- [ ] **Step 4: Write review metric test**

Create `apps/api/tests/test_v02_review_metrics.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_review_report_cites_operational_metrics():
    client = TestClient(app)
    client.post("/api/events/demo/seed")
    client.post("/api/events/demo-night-tour/generate-plan")
    client.post("/api/events/demo-night-tour/plans/1/approve")

    report = client.post("/api/events/demo-night-tour/review-report")
    assert report.status_code == 200
    body = report.json()
    joined = "\n".join(body["lessons_learned"] + body["next_event_recommendations"])
    assert "h5_visits" in joined or "访问" in joined
    assert "incident_response_minutes" in joined or "异常" in joined
```

- [ ] **Step 5: Update review service**

In `apps/api/app/services/review.py`, make `generate_review_report` accept `metrics: list[OperationalMetric]` and include metric names/values in `lessons_learned` and `next_event_recommendations`.

Example lesson:

```python
f"H5 访问量 {metric_map['h5_visits'].value:.0f} 次，说明公开入口可以作为游客通知主通道。"
```

- [ ] **Step 6: Run public/review tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest tests/test_v02_public_projection.py tests/test_v02_review_metrics.py -q
```

Expected: `2 passed`.

### Task 8: Frontend Routing and API Client Upgrade

**Purpose:** Enforce separate role entry points instead of a single-page toy shell.

**Files:**

- Modify: `apps/web/package.json`
- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/api.ts`
- Create: `apps/web/tests/routes.test.tsx`

- [ ] **Step 1: Add route tests**

Create `apps/web/tests/routes.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import App from "../src/App";

const mockFetch = () =>
  vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ route_points: [], notices: [], steps: [] }),
      text: () => Promise.resolve("")
    } as Response)
  );

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch());
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("organizer route renders organizer home", () => {
  window.history.pushState({}, "", "/organizer");
  render(<App />);
  expect(screen.getByText(/活动运营/)).toBeInTheDocument();
});

test("merchant route renders merchant workbench", () => {
  window.history.pushState({}, "", "/merchant/m001");
  render(<App />);
  expect(screen.getByText(/商户工作台/)).toBeInTheDocument();
});

test("public route renders tourist h5", () => {
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);
  expect(screen.getByText(/游客 H5/)).toBeInTheDocument();
});

test("review route renders review center", () => {
  window.history.pushState({}, "", "/review/demo-night-tour");
  render(<App />);
  expect(screen.getByText(/复盘中心/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Choose routing implementation**

Do not add `react-router-dom` unless the team wants a dependency. For this MVP, implement a tiny route resolver in `App.tsx`:

```tsx
const path = window.location.pathname;
if (path.startsWith("/merchant/")) return <MerchantWorkbenchPage merchantId={path.split("/")[2]} />;
if (path.startsWith("/public/events/")) return <TouristH5Page eventId={path.split("/")[3]} />;
if (path.startsWith("/review/")) return <ReviewCenterPage eventId={path.split("/")[2]} />;
if (path.startsWith("/organizer/events/") && path.endsWith("/exceptions")) {
  return <ExceptionCenterPage eventId={path.split("/")[3]} />;
}
if (path.startsWith("/organizer/events/")) return <ActivityWorkspacePage eventId={path.split("/")[3]} />;
return <OrganizerHomePage />;
```

This keeps the demo deterministic and avoids dependency churn.

- [ ] **Step 3: Update API client**

In `apps/web/src/api.ts`, add parameterized methods:

```ts
getEvents: () => json<EventSummary[]>(fetch(`${API_BASE}/api/events`)),
generatePlan: (eventId: string) => json<GeneratePlanResponse>(fetch(`${API_BASE}/api/events/${eventId}/generate-plan`, { method: "POST" })),
approvePlanVersion: (eventId: string, version: number) => json<PlanVersion>(fetch(`${API_BASE}/api/events/${eventId}/plans/${version}/approve`, { method: "POST" })),
getCurrentPlan: (eventId: string) => json<PlanVersion>(fetch(`${API_BASE}/api/events/${eventId}/plans/current`)),
getAgentTraces: (eventId: string) => json<AgentTrace[]>(fetch(`${API_BASE}/api/events/${eventId}/agent-traces`)),
getMerchantTasks: (eventId: string) => json<MerchantTask[]>(fetch(`${API_BASE}/api/events/${eventId}/merchant-tasks`)),
getMerchantWorkbench: (merchantId: string, eventId: string) => json<MerchantWorkbench>(fetch(`${API_BASE}/api/merchants/${merchantId}/workbench?event_id=${eventId}`)),
getIncidents: (eventId: string) => json<Incident[]>(fetch(`${API_BASE}/api/events/${eventId}/incidents`)),
createRecoveryProposal: (eventId: string, incidentId: string) => json<RecoveryProposal>(fetch(`${API_BASE}/api/events/${eventId}/incidents/${incidentId}/recovery-proposals`, { method: "POST" })),
approveRecoveryProposal: (eventId: string, proposalId: string) => json<ApproveRecoveryResponse>(fetch(`${API_BASE}/api/events/${eventId}/recovery-proposals/${proposalId}/approve`, { method: "POST" })),
getPublicEvent: (eventId: string) => json<PublicEventV2>(fetch(`${API_BASE}/api/public/events/${eventId}`)),
```

Keep old methods until old pages are removed.

- [ ] **Step 4: Run route tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test -- routes.test.tsx
```

Expected: route tests fail before pages exist, then pass after Task 9-12 pages are created.

### Task 9: Organizer Home and Activity Workspace

**Purpose:** Make the first screen a product workbench.

**Files:**

- Create: `apps/web/src/pages/OrganizerHomePage.tsx`
- Create: `apps/web/src/pages/ActivityWorkspacePage.tsx`
- Create: `apps/web/src/components/AgentTracePanel.tsx`
- Create: `apps/web/src/components/PlanVersionDiff.tsx`
- Modify: `apps/web/src/styles.css`

- [ ] **Step 1: Build Organizer Home**

Create `OrganizerHomePage.tsx` with:

- `PageHeader` style title text `活动运营`.
- Activity list table or list with `demo-night-tour`.
- Status cards for active event, pending approvals, risk alerts, and public release status.
- Navigation links using plain anchors:

```tsx
<a href="/organizer/events/demo-night-tour">进入活动工作区</a>
<a href="/organizer/events/demo-night-tour/exceptions">异常中心</a>
<a href="/review/demo-night-tour">复盘中心</a>
```

Do not render merchant or tourist pages inside this page.

- [ ] **Step 2: Build Activity Workspace**

Create `ActivityWorkspacePage.tsx` with:

- left column: event brief and plan version status,
- center: route point timeline and merchant task table,
- right column: approval actions and `AgentTracePanel`.

Required buttons:

```text
初始化演示活动
生成 v1 方案
确认 v1 方案
进入异常中心
打开游客 H5
```

Use anchors for separate entries:

```tsx
<a href="/public/events/demo-night-tour" target="_blank" rel="noreferrer">打开游客 H5</a>
<a href="/merchant/m001" target="_blank" rel="noreferrer">打开商户工作台</a>
```

- [ ] **Step 3: Build `AgentTracePanel`**

Render:

- step agent name,
- decision reason,
- confidence,
- tool calls,
- structured output collapsed in `pre`.

The panel title must be `Agent 证据链`.

- [ ] **Step 4: Build `PlanVersionDiff`**

Render:

- current version,
- status,
- `diff_from_previous` as a list,
- `approved_by` and `approved_at` if available.

If version is 1 and diff is empty, render `初始方案，无上一版本差异`.

- [ ] **Step 5: Run organizer tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test
```

Expected: existing smoke tests and route tests pass for organizer routes.

### Task 10: Exception Center and Merchant Workbench

**Purpose:** Make merchant state changes trigger visible incident handling.

**Files:**

- Create: `apps/web/src/pages/ExceptionCenterPage.tsx`
- Create: `apps/web/src/pages/MerchantWorkbenchPage.tsx`
- Create: `apps/web/src/components/IncidentQueue.tsx`
- Create: `apps/web/tests/merchant-incident.test.tsx`

- [ ] **Step 1: Add UI behavior test**

Create `apps/web/tests/merchant-incident.test.tsx`:

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";

test("merchant workbench exposes status update controls", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            merchant_id: "m001",
            tasks: [],
            runtime_state: { inventory_status: "normal", queue_status: "normal", available_for_visitors: true },
          }),
        text: () => Promise.resolve("")
      } as Response)
    )
  );
  window.history.pushState({}, "", "/merchant/m001");
  render(<App />);
  expect(screen.getByText(/商户工作台/)).toBeInTheDocument();
  expect(await screen.findByRole("button", { name: /上报库存售罄/ })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /上报库存售罄/ }));
  await waitFor(() => expect(fetch).toHaveBeenCalled());
});
```

- [ ] **Step 2: Build Merchant Workbench**

Create `MerchantWorkbenchPage.tsx`:

- load `/api/merchants/{merchantId}/workbench?event_id=demo-night-tour`,
- show today tasks,
- show preparation checklist,
- show current runtime status,
- provide buttons:
  - `上报库存正常`
  - `上报库存紧张`
  - `上报库存售罄`
  - `上报排队过载`

When posting state, call `api.updateRuntimeState(merchantId, payload)` and show the returned `incident` if any.

- [ ] **Step 3: Build Exception Center**

Create `ExceptionCenterPage.tsx`:

- load incidents,
- show incident queue,
- allow `生成恢复方案`,
- allow `主办方确认恢复`,
- after approval, show returned `current_plan.version` and public notice status.

Do not put tourist H5 content inline. Provide an anchor to `/public/events/demo-night-tour`.

- [ ] **Step 4: Build `IncidentQueue`**

Render incident cards or table rows with:

- incident type,
- severity,
- source,
- affected merchants,
- affected route points,
- status,
- action button.

- [ ] **Step 5: Run merchant/exception tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test -- merchant-incident.test.tsx routes.test.tsx
```

Expected: tests pass.

### Task 11: Tourist H5 and Review Center

**Purpose:** Make tourist and review endpoints feel like real use surfaces.

**Files:**

- Create: `apps/web/src/pages/TouristH5Page.tsx`
- Create: `apps/web/src/pages/ReviewCenterPage.tsx`
- Create: `apps/web/src/components/RoutePointTimeline.tsx`
- Create: `apps/web/src/components/MetricSummary.tsx`
- Create: `apps/web/tests/public-review.test.tsx`

- [ ] **Step 1: Add public/review tests**

Create `apps/web/tests/public-review.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import App from "../src/App";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            event_id: "demo-night-tour",
            title: "福隆新街周末旧区夜游",
            current_plan_version: 2,
            route_points: [
              {
                point_id: "rp001",
                name: "福隆新街开场点",
                story: "老字号街景",
                visitor_task: "完成问答",
                linked_merchants: ["m001"],
                is_indoor: false,
                current_status: "active"
              }
            ],
            notices: [{ message: "路线已更新", publish_status: "published" }],
            lessons_learned: ["H5 访问量 428 次"],
            next_event_recommendations: ["降低售罄商户导流权重"]
          }),
        text: () => Promise.resolve("")
      } as Response)
    )
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("tourist h5 renders route point story and notice", async () => {
  window.history.pushState({}, "", "/public/events/demo-night-tour");
  render(<App />);
  expect(await screen.findByText(/福隆新街周末旧区夜游/)).toBeInTheDocument();
  expect(screen.getByText(/老字号街景/)).toBeInTheDocument();
  expect(screen.getByText(/路线已更新/)).toBeInTheDocument();
});

test("review center renders metric-backed recommendations", async () => {
  window.history.pushState({}, "", "/review/demo-night-tour");
  render(<App />);
  expect(await screen.findByText(/复盘中心/)).toBeInTheDocument();
  expect(screen.getByText(/H5 访问量/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Build Tourist H5**

Create `TouristH5Page.tsx`:

- mobile-first layout,
- event title and status,
- current plan version,
- notices at top,
- `RoutePointTimeline`,
- no backend terms such as `RecoveryProposal` or `PlanVersion` in visible tourist copy.

- [ ] **Step 3: Build Review Center**

Create `ReviewCenterPage.tsx`:

- load or generate review report,
- show operational metrics through `MetricSummary`,
- show incident and approval timeline,
- show lessons and next event recommendations.

- [ ] **Step 4: Run public/review tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test -- public-review.test.tsx
```

Expected: tests pass.

### Task 12: Remove Single-Page Demo Coupling

**Purpose:** Enforce the spec rule that multiple roles are not one page.

**Files:**

- Modify: `apps/web/src/App.tsx`
- Modify: `apps/web/src/components/AppShell.tsx`
- Modify: `apps/web/tests/app.test.tsx`
- Modify: `apps/web/tests/routes.test.tsx`

- [ ] **Step 1: Replace view-state shell**

Remove this pattern from `App.tsx`:

```tsx
const [view, setView] = useState<AppView>("organizer");
```

Use path-based rendering instead.

- [ ] **Step 2: Update AppShell**

`AppShell` should render product navigation links, not switch local state. Links:

```text
/organizer
/organizer/events/demo-night-tour
/organizer/events/demo-night-tour/exceptions
/merchant/m001
/public/events/demo-night-tour
/review/demo-night-tour
```

The organizer side may include links to merchant and H5 entries, but must not inline their pages.

- [ ] **Step 3: Update smoke test**

Change `apps/web/tests/app.test.tsx` to assert:

```tsx
expect(screen.getByText(/活动运营/)).toBeInTheDocument();
expect(screen.queryByText(/上报库存售罄/)).not.toBeInTheDocument();
expect(screen.queryByText(/游客 H5/)).not.toBeInTheDocument();
```

This ensures the organizer home does not render merchant and tourist surfaces inline.

- [ ] **Step 4: Run full frontend tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test
npm run build
```

Expected: tests pass and build succeeds.

### Task 13: Full Backend Flow Test

**Purpose:** Prove v0.2 deterministic closed loop.

**Files:**

- Modify: `apps/api/tests/test_api_flow.py`

- [ ] **Step 1: Rewrite complete flow test around v0.2**

Update `test_complete_demo_loop` to assert this exact sequence:

```python
seed -> generate-plan -> approve v1 -> merchant status update -> incident -> proposal -> approve proposal -> current plan v2 -> public h5 v2 -> weather trigger -> review report
```

Key assertions:

```python
assert generated["current_plan"]["version"] == 1
assert len(generated["agent_trace"]["steps"]) >= 5
assert incident["type"] == "inventory"
assert approved_recovery["current_plan"]["version"] == 2
assert public_after["current_plan_version"] == 2
assert len(report["lessons_learned"]) >= 2
```

- [ ] **Step 2: Run all backend tests**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest -q
```

Expected: all backend tests pass.

### Task 14: Documentation and Handoff Update

**Purpose:** Keep future agents aligned with v0.2.

**Files:**

- Modify: `docs/demo/demo-script.md`
- Modify: `docs/demo/demo-checklist.md`
- Modify: `docs/ai/STATUS.md`
- Modify: `docs/ai/VERIFY.md`
- Modify: `docs/ai/NEXT.md`
- Modify: `README.md`

- [ ] **Step 1: Update demo script**

`docs/demo/demo-script.md` must describe the v0.2 story:

```text
主办方工作台 -> 活动工作区 -> 生成 v1 和 Agent trace -> 确认 v1 -> 商户工作台上报库存售罄 -> 异常中心生成恢复方案 -> 主办方确认 -> v2 diff -> 游客 H5 更新 -> 复盘中心
```

- [ ] **Step 2: Update demo checklist**

Add checklist items:

```markdown
- [ ] `/organizer` opens organizer home, not a marketing page.
- [ ] `/merchant/m001` opens merchant workbench as a separate entry.
- [ ] `/public/events/demo-night-tour` opens tourist H5 as a separate entry.
- [ ] `/review/demo-night-tour` opens review center as a separate entry.
- [ ] Agent trace shows at least 5 steps.
- [ ] Recovery approval creates `PlanVersion v2`.
- [ ] Public H5 shows `current_plan_version = 2` after recovery approval.
```

- [ ] **Step 3: Update `docs/ai/VERIFY.md` after commands actually run**

Record exact commands and outcomes:

```text
python -m pytest -q
npm run test
npm run build
manual smoke URL checks
```

Do not write planned results into `VERIFY.md`.

- [ ] **Step 4: Update `docs/ai/STATUS.md`**

Record:

- v0.2 redesign implementation status,
- deterministic fallback preserved,
- Qwen/QwenPaw not required,
- separate route entries implemented.

- [ ] **Step 5: Update `docs/ai/NEXT.md`**

Recommended next after v0.2 loop passes:

```text
Run browser review across /organizer, /merchant/m001, /public/events/demo-night-tour, and /review/demo-night-tour; then decide whether to polish UI or add optional Qwen structured output parsing.
```

### Task 15: Final Verification

**Purpose:** Ensure the implementation meets the spec before claiming completion.

**Files:**

- No source edits unless a verification failure identifies a concrete defect.

- [ ] **Step 1: Backend verification**

Run:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 2: Frontend verification**

Run:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run test
npm run build
```

Expected: all frontend tests pass and Vite build succeeds.

- [ ] **Step 3: Manual route smoke**

Start API:

```powershell
cd <PROJECT_ROOT>\apps\api
python -m uvicorn app.main:app --port 8000
```

Start web:

```powershell
cd <PROJECT_ROOT>\apps\web
npm run dev
```

Open:

```text
http://127.0.0.1:5173/organizer
http://127.0.0.1:5173/organizer/events/demo-night-tour
http://127.0.0.1:5173/organizer/events/demo-night-tour/exceptions
http://127.0.0.1:5173/merchant/m001
http://127.0.0.1:5173/public/events/demo-night-tour
http://127.0.0.1:5173/review/demo-night-tour
```

Expected:

- Organizer home is an operations workbench.
- Activity workspace shows plan version and Agent trace.
- Exception center shows incidents and recovery approval.
- Merchant workbench can submit status.
- Tourist H5 shows route point stories and public notices.
- Review center cites metrics.
- No page requires `DASHSCOPE_API_KEY`.

## 5. Implementation Order

Use this order:

1. Task 1: baseline guard tests.
2. Task 2: v0.2 domain contracts.
3. Task 3: store and seed.
4. Task 4: deterministic Agent trace and PlanVersion v1.
5. Task 5: plan version API.
6. Task 6: incident and recovery proposal loop.
7. Task 7: public projection and review metrics.
8. Task 8: frontend routing and API client.
9. Task 9: organizer product workbench.
10. Task 10: exception center and merchant workbench.
11. Task 11: tourist H5 and review center.
12. Task 12: remove single-page coupling.
13. Task 13: full backend flow test.
14. Task 14: docs and handoff.
15. Task 15: final verification.

Do not start UI page polish before Task 7 backend tests pass. Do not connect optional Qwen/QwenPaw parsing before Task 15 passes.

## 6. Self-Review Against v0.2 Spec

Spec coverage:

- Multi-use-end boundary: Tasks 8, 9, 10, 11, and 12.
- Organizer Home: Task 9.
- Activity Workspace: Task 9.
- Exception Center: Task 10.
- Merchant Workbench: Task 10.
- Tourist H5: Task 11.
- Review Center: Task 11.
- `PlanVersion`: Tasks 2, 4, 5, 6, and 13.
- `Incident`: Tasks 2, 3, 6, and 13.
- `RecoveryProposal`: Tasks 2, 6, and 13.
- `PublicNotice`: Tasks 2, 6, 7, and 13.
- `AgentTrace`: Tasks 2, 4, 5, and 9.
- `OperationalMetric`: Tasks 2, 3, 7, 11, and 14.
- Deterministic no-key demo: Tasks 4, 13, and 15.
- Human approval gate: Tasks 5, 6, 9, 10, and 13.

Accepted residual risk:

- This plan still uses mock route points and mock metrics. That is intentional for the competition MVP because the spec excludes real merchant integration, real traffic prediction, and hardware.

## 7. Execution Handoff

Recommended execution mode:

1. Use `superpowers:subagent-driven-development` if available: one focused worker per backend/frontend task, with review between tasks.
2. Use `superpowers:executing-plans` inline only if subagents are unavailable or the implementation needs close interactive control.

The first implementation checkpoint is after Task 7. At that checkpoint the backend should already prove the v0.2 state loop before frontend redesign proceeds.

