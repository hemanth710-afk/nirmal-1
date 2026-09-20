"""
Tool Execution & Environment Interaction Evaluations (Task B).
Evaluates safe tool dispatch, parameter validation, arithmetic computation,
and multi-step tool execution.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal
from nirmal.planning import PlanNode, PlanStatus


def test_multistep_arithmetic_task_b(controller):
    """Task B: Multi-step arithmetic evaluation using safe calculator tool."""
    goal = Goal(
        goal_id="task_b_calc",
        description="Calculate 15 * 12 + 45",
        criteria=225.0,
    )
    result = controller.run(goal)

    assert result.success is True
    assert result.state == ControllerState.DONE
    assert result.final_output == 225.0

    # Ensure tool action was recorded in execution trace
    act_records = [r for r in result.execution_trace if r.state == ControllerState.ACT]
    assert len(act_records) >= 1
    assert act_records[0].action.tool_name == "calculator"
    assert act_records[0].action_result.success is True
    assert act_records[0].action_result.output == 225.0


def test_string_tool_execution(controller):
    """Verify text transformation using StringUtilityTool."""
    # Build a linear plan with two consecutive string operations
    plan = controller.planner.create_linear_plan(
        goal="Format text to uppercase",
        steps=[
            {
                "id": "step_upper",
                "description": "Convert to uppercase",
                "tool_name": "string_util",
                "tool_args": {"operation": "uppercase", "text": "nirmal aoi"},
            },
            {
                "id": "step_reverse",
                "description": "Reverse uppercase string",
                "tool_name": "string_util",
                "tool_args": {"operation": "reverse", "text": "{step_upper}"},
            },
        ],
    )
    controller.reset()
    controller.current_goal = Goal(goal_id="g_str", description="Format text to uppercase")
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description="Format text to uppercase")
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.active_plan = plan
    controller.state = ControllerState.PLAN

    while controller.state not in (ControllerState.DONE, ControllerState.FAILED):
        controller.step()

    assert controller.state == ControllerState.DONE
    assert controller.final_output == "IOA LAMRIN"


def test_mock_environment_read_write(tool_registry, mock_env):
    """Verify MockEnvironmentTool stateful write and read capabilities."""
    write_res = tool_registry.execute("mock_env", {"action": "write", "key": "motor_state", "value": "active"})
    assert write_res.success is True
    assert mock_env.state["motor_state"] == "active"

    read_res = tool_registry.execute("mock_env", {"action": "read", "key": "motor_state"})
    assert read_res.success is True
    assert read_res.output == "active"
