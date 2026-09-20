"""
Compositional Generalization Evaluations (Task D).
Evaluates novel combination of previously known primitives across different tool classes
without hardcoded procedural templates.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal


def test_compositional_cross_tool_chaining_task_d(controller):
    """Task D: Compose string manipulation and arithmetic calculation in a single pipeline."""
    # Pipeline:
    # 1. Lowercase text "NIRMAL-AGI" -> "nirmal-agi"
    # 2. Compute length of string -> 10
    # 3. Calculate 10 * 10 + 5 using calculator -> 105.0
    plan = controller.planner.create_linear_plan(
        goal="Compose string and calculator pipeline",
        steps=[
            {
                "id": "step_lower",
                "description": "Lowercase string",
                "tool_name": "string_util",
                "tool_args": {"operation": "lowercase", "text": "NIRMAL-AGI"},
            },
            {
                "id": "step_len",
                "description": "Calculate string length",
                "tool_name": "string_util",
                "tool_args": {"operation": "length", "text": "{step_lower}"},
                "dependencies": ["step_lower"],
            },
            {
                "id": "step_calc",
                "description": "Compute expression with length",
                "tool_name": "calculator",
                "tool_args": {"expression": "{step_len} * 10 + 5", "expected": 105.0},
                "dependencies": ["step_len"],
            },
        ],
    )

    controller.reset()
    goal = Goal(
        goal_id="task_d_gen",
        description="Compose string and calculator pipeline",
        criteria=105.0,
    )
    controller.current_goal = goal
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description=goal.description)
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.active_plan = plan
    controller.state = ControllerState.PLAN

    while controller.state not in (ControllerState.DONE, ControllerState.FAILED):
        controller.step()

    assert controller.state == ControllerState.DONE
    assert controller.final_output == 105.0
    assert controller.world_state.get_fact("output_step_lower") == "nirmal-agi"
    assert controller.world_state.get_fact("output_step_len") == 10
    assert controller.world_state.get_fact("output_step_calc") == 105.0


def test_computation_to_environment_pipeline(controller, mock_env):
    """Verify chaining computation into stateful environment write and read."""
    plan = controller.planner.create_linear_plan(
        goal="Compute and persist environment state",
        steps=[
            {
                "id": "step_calc",
                "description": "Compute target parameter",
                "tool_name": "calculator",
                "tool_args": {"expression": "25 * 4"},
            },
            {
                "id": "step_write",
                "description": "Persist parameter to environment",
                "tool_name": "mock_env",
                "tool_args": {"action": "write", "key": "threshold", "value": "{step_calc}"},
                "dependencies": ["step_calc"],
            },
            {
                "id": "step_read",
                "description": "Read back persisted parameter",
                "tool_name": "mock_env",
                "tool_args": {"action": "read", "key": "threshold", "expected": "100.0"},
                "dependencies": ["step_write"],
            },
        ],
    )

    controller.reset()
    goal = Goal(goal_id="g_env_chain", description="Compute and persist environment state", criteria="100.0")
    controller.current_goal = goal
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description=goal.description)
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.active_plan = plan
    controller.state = ControllerState.PLAN

    while controller.state not in (ControllerState.DONE, ControllerState.FAILED):
        controller.step()

    assert controller.state == ControllerState.DONE
    assert float(controller.final_output) == 100.0
    assert float(mock_env.state.get("threshold")) == 100.0
