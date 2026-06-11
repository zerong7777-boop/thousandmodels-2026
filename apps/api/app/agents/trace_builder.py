from app.schemas import AgentStep, AgentTrace, PlanVersion


def build_trace_from_steps(
    event_id: str,
    trigger: str,
    steps: list[AgentStep],
    final_output_ref: str,
    trace_id: str,
    human_decision_ref: str | None = None,
) -> AgentTrace:
    return AgentTrace(
        trace_id=trace_id,
        event_id=event_id,
        trigger=trigger,
        steps=steps,
        final_output_ref=final_output_ref,
        human_decision_ref=human_decision_ref,
    )


def build_planning_trace(event_id: str, plan: PlanVersion) -> AgentTrace:
    steps = [
        AgentStep(
            agent_name="OrchestratorAgent",
            input_refs=[f"event_brief:{event_id}"],
            tool_calls=[{"tool": "task.decompose", "result": "6 planning tasks"}],
            structured_output={
                "tasks": ["narrative", "route", "merchant", "risk", "budget", "publication"]
            },
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
