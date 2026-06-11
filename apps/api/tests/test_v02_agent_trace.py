from app.agents.trace_builder import build_planning_trace
from app.seed import seed_demo
from app.services.planning import generate_merchant_tasks, generate_plan_version
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
