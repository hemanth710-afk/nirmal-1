"""
Dynamic Replanning & Failure Recovery Evaluations (Task C & Ablation).
Evaluates plan perturbation, verification failure detection, dynamic replanning,
and comparative recovery with Replanning ON vs OFF.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal
from nirmal.planning import PlanNode, PlanStatus


def test_plan_failure_recovery_task_c(controller, mock_env):
    """Task C: Intermediate action fails -> verifier catches it -> planner recovers via dynamic replanning."""
    # Program mock_env to fail on its next action
    mock_env.set_fail_next(True, message="Simulated hardware connection drop.")

    plan = controller.planner.create_linear_plan(
        goal="Configure hardware environment",
        steps=[
            {
                "id": "step_write",
                "description": "Initialize hardware register",
                "tool_name": "mock_env",
                "tool_args": {"action": "write", "key": "sensor_port", "value": "COM3"},
            },
        ],
    )

    controller.reset()
    goal = Goal(goal_id="task_c_replan", description="Configure hardware environment")
    controller.current_goal = goal
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description=goal.description)
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.active_plan = plan
    controller.state = ControllerState.PLAN

    # Run loop
    while controller.state not in (ControllerState.DONE, ControllerState.FAILED):
        controller.step()

    # Verify that the controller detected the failure, triggered replanning, and recovered
    assert controller.state == ControllerState.DONE
    assert controller.replan_count == 1
    assert "recovery_for_step_write" in controller.active_plan.nodes
    assert controller.active_plan.nodes["recovery_for_step_write"].status == PlanStatus.COMPLETED
    assert mock_env.state.get("sensor_port") == "COM3"


def test_replanning_ablation_disabled(tool_registry, semantic_memory, episodic_memory, procedural_memory, verifier, mock_env):
    """Verify that with Replanning OFF, an action failure leads to immediate terminal FAILED state."""
    controller_no_replan = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_replanning=False,
    )

    mock_env.set_fail_next(True, message="Simulated network failure.")

    plan = controller_no_replan.planner.create_linear_plan(
        goal="Connect to remote server",
        steps=[
            {
                "id": "step_conn",
                "description": "Establish connection",
                "tool_name": "mock_env",
                "tool_args": {"action": "write", "key": "conn", "value": "active"},
            },
        ],
    )

    controller_no_replan.reset()
    controller_no_replan.current_goal = Goal(goal_id="g_no_replan", description="Connect to remote server")
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller_no_replan.world_state = WorldState(goal_description="Connect to remote server")
    controller_no_replan.working_memory = WorkingMemory(max_token_budget=1024)
    controller_no_replan.active_plan = plan
    controller_no_replan.state = ControllerState.PLAN

    while controller_no_replan.state not in (ControllerState.DONE, ControllerState.FAILED):
        controller_no_replan.step()

    assert controller_no_replan.state == ControllerState.FAILED
    assert controller_no_replan.replan_count == 0
    assert "Simulated network failure" in str(controller_no_replan.error_message)


def test_replanning_exceeds_max_attempts(controller):
    """Verify that persistent failure terminates cleanly once max_replan_attempts is reached."""
    # Custom failing tool step
    plan = controller.planner.create_linear_plan(
        goal="Execute persistently failing action",
        steps=[
            {
                "id": "fail_step",
                "description": "Failing action",
                "tool_name": "mock_env",
                "tool_args": {"action": "fail_action"},
            },
        ],
    )

    controller.reset()
    controller.max_replan_attempts = 2
    controller.current_goal = Goal(goal_id="g_max_replan", description="Execute persistently failing action")
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description="Execute persistently failing action")
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.active_plan = plan
    controller.state = ControllerState.PLAN

    while controller.state not in (ControllerState.DONE, ControllerState.FAILED):
        controller.step()

    assert controller.state == ControllerState.FAILED
    assert controller.replan_count == 2
