"""
Controller State-Machine & Lifecycle Evaluations.
Verifies explicit state transitions, inspectable trace auditability, and execution control.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal


def test_controller_state_cycle(controller):
    """Verify that the controller cycles through the explicit deterministic state sequence."""
    goal_text = "Calculate 10 + 20"
    controller.reset()
    controller.current_goal = Goal(goal_id="g_test_1", description=goal_text, criteria=30.0)
    controller.world_state = None  # Will be initialized on run or step
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description=goal_text)
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.working_memory.set_goal(goal_text)
    controller.state = ControllerState.OBSERVE

    visited_states = [controller.state]

    # Step sequentially through the cognitive loop
    for _ in range(20):
        next_state = controller.step()
        visited_states.append(next_state)
        if next_state in (ControllerState.DONE, ControllerState.FAILED):
            break

    # Ensure key cognitive cycle states were visited in proper order
    assert ControllerState.OBSERVE in visited_states
    assert ControllerState.RETRIEVE in visited_states
    assert ControllerState.REASON in visited_states
    assert ControllerState.PLAN in visited_states
    assert ControllerState.ACT in visited_states
    assert ControllerState.VERIFY in visited_states
    assert ControllerState.UPDATE in visited_states
    assert ControllerState.LEARN in visited_states
    assert visited_states[-1] == ControllerState.DONE


def test_controller_execution_trace_inspectability(controller):
    """Verify that execution_trace produces a fully inspectable, timestamped audit log."""
    result = controller.run("Calculate 5 * 6", max_steps=20)
    assert result.success is True
    assert result.state == ControllerState.DONE
    assert len(result.execution_trace) > 0

    states_in_trace = set()
    for idx, record in enumerate(result.execution_trace):
        assert record.step_index == idx
        assert isinstance(record.state, ControllerState)
        assert record.timestamp > 0
        assert len(record.description) > 0
        states_in_trace.add(record.state)

    # Required states must be recorded in trace
    assert ControllerState.OBSERVE in states_in_trace
    assert ControllerState.ACT in states_in_trace
    assert ControllerState.VERIFY in states_in_trace
    assert ControllerState.UPDATE in states_in_trace
    assert ControllerState.LEARN in states_in_trace


def test_controller_reset(controller):
    """Verify that resetting the controller cleans runtime state."""
    controller.run("Calculate 1 + 1")
    assert controller.state == ControllerState.DONE
    assert len(controller.execution_trace) > 0

    controller.reset()
    assert controller.state == ControllerState.IDLE
    assert controller.current_goal is None
    assert controller.world_state is None
    assert controller.active_plan is None
    assert len(controller.execution_trace) == 0
    assert controller.step_counter == 0


def test_controller_max_step_termination(controller):
    """Verify that exceeding max_steps terminates cleanly without throwing an unhandled exception."""
    # Run with an artificially tiny max_steps
    result = controller.run("Calculate 100 * 200", max_steps=2)
    assert result.total_steps == 2
    assert result.success is False
    assert result.state not in (ControllerState.DONE,)
