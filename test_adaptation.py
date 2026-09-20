"""
Evaluation Suite: Plan Adaptation & Environmental Disruption Recovery.

Tests:
1. Dynamic plan recovery when intermediate step fails due to environmental shift (A -> B -> C to A -> D -> C).
2. Comparison between Adaptive Agent (replan ON) vs Rigid Agent (replan OFF).
3. Verification of ground-truth state completion despite mid-plan disruption.
"""

import pytest
from evals.open_world import OpenWorldEnvironment, OpenWorldTool
from nirmal.agent.controller import CognitiveController, Goal, ControllerState
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy
from nirmal.planning import TaskGraph, PlanNode
from nirmal.tools import ToolRegistry


def test_rigid_agent_fails_on_environmental_disruption():
    env = OpenWorldEnvironment(seed=101)
    env.state["latent_condition"] = "degraded"  # Direct route will fail
    registry = ToolRegistry()
    registry.register(OpenWorldTool(env=env))

    proc = ProceduralMemory()
    proc.register_strategy(Strategy(
        strategy_id="strat_rigid_pipeline",
        name="strat_rigid_pipeline",
        task_family="open_world",
        description="Execute pipeline via direct route",
        steps=[
            {"id": "step_1", "description": "Verify channel", "tool_name": "open_world_env", "tool_args": {"action": "verify_channel"}},
            {"id": "step_2", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}, "dependencies": ["step_1"]},
            {"id": "step_3", "description": "Write payload", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "k", "value": "v"}, "dependencies": ["step_2"]},
        ],
        success_rate=0.9,
    ))

    # Rigid agent: replanning disabled
    rigid_controller = CognitiveController(
        tool_registry=registry,
        procedural_memory=proc,
        enable_replanning=False,
    )
    goal = Goal(goal_id="g_rigid", description="Execute pipeline via direct route")
    res = rigid_controller.run(goal)

    assert res.success is False
    assert res.state == ControllerState.FAILED
    assert "direct route is degraded" in str(res.error)
    assert env.state.get("active_route") is None


def test_adaptive_agent_replanning_and_recovery():
    env = OpenWorldEnvironment(seed=102)
    env.state["latent_condition"] = "degraded"  # Direct route fails
    registry = ToolRegistry()
    registry.register(OpenWorldTool(env=env))

    proc = ProceduralMemory()
    proc.register_strategy(Strategy(
        strategy_id="strat_adaptive_pipeline",
        name="strat_adaptive_pipeline",
        task_family="open_world",
        description="Execute pipeline with fallback capability",
        steps=[
            {"id": "step_1", "description": "Verify channel", "tool_name": "open_world_env", "tool_args": {"action": "verify_channel"}},
            {"id": "step_2", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}, "dependencies": ["step_1"]},
            {"id": "step_3", "description": "Write payload", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "k", "value": "v"}, "dependencies": ["step_2"]},
        ],
        success_rate=0.9,
    ))

    # Custom planner recovery in controller handles degraded route
    adaptive_controller = CognitiveController(
        tool_registry=registry,
        procedural_memory=proc,
        enable_replanning=True,
        max_replan_attempts=2,
    )

    # Inject fallback into planner for step_2 failure
    original_update = adaptive_controller.planner.update_plan
    def custom_update_plan(plan, failed_step, error):
        if failed_step.node_id == "step_2":
            # Replace step_2 with fallback route step
            fallback_node = PlanNode(
                node_id="step_2_fallback",
                description="Establish fallback route",
                tool_name="open_world_env",
                tool_args={"action": "route_fallback"},
                dependencies=["step_1"],
            )
            plan.add_node(fallback_node)
            # Update step_3 dependency to step_2_fallback
            if "step_3" in plan.nodes:
                plan.nodes["step_3"].dependencies = ["step_2_fallback"]
            return plan
        return original_update(plan, failed_step, error)

    adaptive_controller.planner.update_plan = custom_update_plan

    goal = Goal(goal_id="g_adapt", description="Execute pipeline with fallback capability")
    res = adaptive_controller.run(goal)

    assert res.success is True
    assert res.state == ControllerState.DONE
    assert adaptive_controller.replan_count == 1
    # Verify that the environment successfully reached fallback route and committed write
    assert env.state["active_route"] == "fallback"
    assert env.state["data_store"].get("k") == "v"
    assert env.verify_state({"active_route": "fallback", "data_store": {"k": "v"}}) is True
