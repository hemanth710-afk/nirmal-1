"""
Hierarchical DAG Planning & Ablation Evaluations (Planning & Verification Axes).
Evaluates DAG dependency ordering, parallel branch resolution, and comparative
behavior with Planner ON vs Direct, and Verification ON vs Bypassed.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal
from nirmal.planning import TaskGraph, PlanNode, PlanStatus


def test_dag_topological_execution_order(controller):
    """Verify that a branching DAG executes strictly according to dependency topological constraints."""
    graph = TaskGraph(goal="Diamond workflow")

    # Step 1: Base string
    n1 = PlanNode(
        node_id="init_step",
        description="Initialize text",
        tool_name="string_util",
        tool_args={"operation": "lowercase", "text": "AI_SYSTEM"},
    )
    # Step 2a: Branch A (depends on init)
    n2a = PlanNode(
        node_id="branch_a",
        description="Uppercase Branch A",
        tool_name="string_util",
        tool_args={"operation": "uppercase", "text": "{init_step}"},
        dependencies=["init_step"],
    )
    # Step 2b: Branch B (depends on init)
    n2b = PlanNode(
        node_id="branch_b",
        description="Reverse Branch B",
        tool_name="string_util",
        tool_args={"operation": "reverse", "text": "{init_step}"},
        dependencies=["init_step"],
    )
    # Step 3: Join node (depends on 2a and 2b)
    n3 = PlanNode(
        node_id="join_step",
        description="Join branches",
        tool_name="string_util",
        tool_args={"operation": "length", "text": "{branch_a}"},
        dependencies=["branch_a", "branch_b"],
    )

    graph.add_node(n1)
    graph.add_node(n2a)
    graph.add_node(n2b)
    graph.add_node(n3)

    controller.reset()
    goal = Goal(goal_id="g_dag", description="Diamond workflow")
    controller.current_goal = goal
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    controller.world_state = WorldState(goal_description=goal.description)
    controller.working_memory = WorkingMemory(max_token_budget=1024)
    controller.active_plan = graph
    controller.state = ControllerState.PLAN

    execution_order = []
    while controller.state not in (ControllerState.DONE, ControllerState.FAILED):
        if controller.state == ControllerState.ACT and controller.current_node:
            if not execution_order or execution_order[-1] != controller.current_node.node_id:
                execution_order.append(controller.current_node.node_id)
        controller.step()

    assert controller.state == ControllerState.DONE
    # Topological order guarantees: init_step must precede branch_a and branch_b; join_step must come last
    assert execution_order[0] == "init_step"
    assert "branch_a" in execution_order[1:3]
    assert "branch_b" in execution_order[1:3]
    assert execution_order[-1] == "join_step"


def test_planner_ablation_on_vs_off(tool_registry, semantic_memory, episodic_memory, procedural_memory, verifier):
    """Task E (Planner Axis): Compare multi-step task execution with Planner ON vs Planner OFF (Direct)."""
    # 1. With Planning ON: Multi-step arithmetic runs through procedural decomposition
    controller_planned = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_planning=True,
    )
    res_planned = controller_planned.run(Goal(goal_id="g_plan_on", description="Calculate 20 * 5", criteria=100.0))
    assert res_planned.success is True
    assert res_planned.final_output == 100.0
    assert len(res_planned.execution_trace) > 4

    # 2. With Planning OFF: Bypasses DAG decomposition and performs direct single step
    controller_direct = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_planning=False,
    )
    res_direct = controller_direct.run(Goal(goal_id="g_plan_off", description="Direct echo"))
    assert res_direct.state in (ControllerState.DONE, ControllerState.LEARN)
    assert res_direct.total_steps <= res_planned.total_steps


def test_verification_ablation_on_vs_off(tool_registry, semantic_memory, episodic_memory, procedural_memory, verifier):
    """Task E (Verification Axis): Compare behavior when Verification is active vs bypassed."""
    # Step where expected != actual
    def build_mismatch_plan(ctrl):
        return ctrl.planner.create_linear_plan(
            goal="Mismatch test",
            steps=[
                {
                    "id": "step_mismatch",
                    "description": "Output mismatching number",
                    "tool_name": "calculator",
                    "tool_args": {"expression": "5 + 5", "expected": 999.0},
                }
            ],
        )

    # 1. Verification ON: Rejects invalid result
    ctrl_verif_on = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_verification=True,
        enable_replanning=False,  # So it immediately fails on rejection
    )
    from nirmal.agent.world_state import WorldState
    from nirmal.memory import WorkingMemory

    ctrl_verif_on.reset()
    ctrl_verif_on.current_goal = Goal(goal_id="g_v_on", description="Mismatch test")
    ctrl_verif_on.world_state = WorldState(goal_description="Mismatch test")
    ctrl_verif_on.working_memory = WorkingMemory(max_token_budget=1024)
    ctrl_verif_on.active_plan = build_mismatch_plan(ctrl_verif_on)
    ctrl_verif_on.state = ControllerState.PLAN

    while ctrl_verif_on.state not in (ControllerState.DONE, ControllerState.FAILED):
        ctrl_verif_on.step()

    # Rejection caught!
    assert ctrl_verif_on.state == ControllerState.FAILED
    assert "Numeric mismatch" in str(ctrl_verif_on.error_message)

    # 2. Verification OFF: Bypasses check and accepts mismatch
    ctrl_verif_off = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_verification=False,
    )
    ctrl_verif_off.reset()
    ctrl_verif_off.current_goal = Goal(goal_id="g_v_off", description="Mismatch test")
    ctrl_verif_off.world_state = WorldState(goal_description="Mismatch test")
    ctrl_verif_off.working_memory = WorkingMemory(max_token_budget=1024)
    ctrl_verif_off.active_plan = build_mismatch_plan(ctrl_verif_off)
    ctrl_verif_off.state = ControllerState.PLAN

    while ctrl_verif_off.state not in (ControllerState.DONE, ControllerState.FAILED):
        ctrl_verif_off.step()

    # With verification bypassed, mismatch is silently accepted as DONE
    assert ctrl_verif_off.state == ControllerState.DONE
    assert ctrl_verif_off.final_output == 10.0
