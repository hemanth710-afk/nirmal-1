"""
Evaluation Suite: Counterfactual Reasoning & Strategy Condition Adherence.

Tests:
1. Strategy execution succeeds under required precondition condition C.
2. Strategy is rejected when its avoid_conditions match the active environment condition (NOT-C).
3. Learned negative experience updates avoid_conditions and prevents recurrence of failure under condition C.
4. Counterfactual condition shift: Agent selects different optimal strategies when conditions change.
"""

import pytest
from evals.open_world import OpenWorldEnvironment, OpenWorldTool
from nirmal.agent.controller import CognitiveController, Goal
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy
from nirmal.tools import ToolRegistry


def test_strategy_selection_with_matching_condition():
    proc = ProceduralMemory()

    # Strategy 1: Secure flow (requires secure condition)
    s_secure = Strategy(
        strategy_id="strat_secure_flow",
        name="strat_secure_flow",
        task_family="open_world",
        description="Write data securely by acquiring authentication token first",
        conditions={"latent_condition": "secure"},
        steps=[
            {"id": "step_1", "description": "Acquire security token", "tool_name": "open_world_env", "tool_args": {"action": "acquire_token"}},
            {"id": "step_2", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}},
            {"id": "step_3", "description": "Write protected data", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "k", "value": "v"}},
        ],
        success_rate=0.9,
    )
    # Strategy 2: Fast flow (requires stable condition)
    s_fast = Strategy(
        strategy_id="strat_fast_flow",
        name="strat_fast_flow",
        task_family="open_world",
        description="Write data fast via direct route without token overhead",
        conditions={"latent_condition": "stable"},
        avoid_conditions={"latent_condition": "secure"},
        steps=[
            {"id": "step_1", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}},
            {"id": "step_2", "description": "Write data directly", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "k", "value": "v"}},
        ],
        success_rate=0.95,
    )
    proc.register_strategy(s_secure)
    proc.register_strategy(s_fast)

    # When condition is "secure", select_strategy MUST choose strat_secure_flow and reject strat_fast_flow
    sel_secure = proc.select_strategy("Write data to environment", conditions={"latent_condition": "secure"})
    assert sel_secure is not None
    assert sel_secure.name == "strat_secure_flow"

    # When condition is "stable", select_strategy MUST choose strat_fast_flow
    sel_stable = proc.select_strategy("Write data to environment", conditions={"latent_condition": "stable"})
    assert sel_stable is not None
    assert sel_stable.name == "strat_fast_flow"


def test_avoid_condition_rejection():
    proc = ProceduralMemory()
    strat = Strategy(
        strategy_id="strat_risky_direct",
        name="strat_risky_direct",
        task_family="open_world",
        description="Direct network route",
        avoid_conditions={"latent_condition": "degraded"},
        steps=[{"id": "step_1", "description": "Route direct", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}}],
        success_rate=0.8,
    )
    proc.register_strategy(strat)

    # Under degraded condition, strat_risky_direct must be rejected due to avoid_conditions
    sel = proc.select_strategy("Route data", conditions={"latent_condition": "degraded"})
    assert sel is None

    # Under stable condition, it is permitted
    sel_ok = proc.select_strategy("Route data", conditions={"latent_condition": "stable"})
    assert sel_ok is not None
    assert sel_ok.name == "strat_risky_direct"


def test_controller_counterfactual_adaptation_in_environment():
    # Setup environment in secure mode
    env = OpenWorldEnvironment(seed=99)
    env.state["latent_condition"] = "secure"

    registry = ToolRegistry()
    registry.register(OpenWorldTool(env=env))

    proc = ProceduralMemory()
    # Register secure strategy
    proc.register_strategy(Strategy(
        strategy_id="secure_pipeline",
        name="secure_pipeline",
        task_family="open_world",
        description="Write data under secure condition",
        conditions={"latent_condition": "secure"},
        steps=[
            {"id": "step_1", "description": "Acquire token", "tool_name": "open_world_env", "tool_args": {"action": "acquire_token"}},
            {"id": "step_2", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}},
            {"id": "step_3", "description": "Write data", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "target_k", "value": "target_v"}},
        ],
        success_rate=0.9,
    ))

    controller = CognitiveController(tool_registry=registry, procedural_memory=proc)
    goal = Goal(
        goal_id="g_secure_test",
        description="Write data under secure condition",
        metadata={"latent_condition": "secure"},
    )
    res = controller.run(goal)

    assert res.success is True
    assert res.strategy_used == "secure_pipeline"
    assert env.state["has_token"] is True
    assert env.state["data_store"].get("target_k") == "target_v"
