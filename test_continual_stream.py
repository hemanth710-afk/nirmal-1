"""
Evaluation Suite: Continual Task Stream & Catastrophic Forgetting Prevention.

Tests:
1. 100-task sequential stream across three distinct phases:
   - Phase A (Tasks 1-30): Baseline stable condition.
   - Phase B (Tasks 31-70): Shifted secure condition requiring token acquisition.
   - Phase C (Tasks 71-100): Mixed holdout tasks evaluating both Phase A and Phase B.
2. Measures:
   - Forward transfer into Phase B.
   - Phase A retention (anti-forgetting) in Phase C.
   - Overall stream success rate > 90%.
"""

import pytest
from evals.open_world import OpenWorldEnvironment, OpenWorldTool
from nirmal.agent.controller import CognitiveController, Goal, ControllerState
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy
from nirmal.agent.memory.semantic import SemanticMemory
from nirmal.tools import ToolRegistry


def test_100_task_continual_stream():
    env = OpenWorldEnvironment(seed=777)
    registry = ToolRegistry()
    registry.register(OpenWorldTool(env=env))

    proc = ProceduralMemory()
    # Seed base primitive strategies
    proc.register_strategy(Strategy(
        strategy_id="stable_writer",
        name="stable_writer",
        task_family="open_world",
        description="Write data in stable environment",
        conditions={"latent_condition": "stable"},
        avoid_conditions={"latent_condition": "secure"},
        steps=[
            {"id": "step_1", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}},
            {"id": "step_2", "description": "Write data", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "k_{idx}", "value": "v_{idx}"}, "dependencies": ["step_1"]},
        ],
        success_rate=0.8,
    ))

    proc.register_strategy(Strategy(
        strategy_id="secure_writer",
        name="secure_writer",
        task_family="open_world",
        description="Write data in secure environment",
        conditions={"latent_condition": "secure"},
        steps=[
            {"id": "step_1", "description": "Acquire security token", "tool_name": "open_world_env", "tool_args": {"action": "acquire_token"}},
            {"id": "step_2", "description": "Establish direct route", "tool_name": "open_world_env", "tool_args": {"action": "route_direct"}, "dependencies": ["step_1"]},
            {"id": "step_3", "description": "Write data", "tool_name": "open_world_env", "tool_args": {"action": "write_data", "key": "k_{idx}", "value": "v_{idx}"}, "dependencies": ["step_2"]},
        ],
        success_rate=0.8,
    ))

    sem = SemanticMemory()
    controller = CognitiveController(
        tool_registry=registry,
        procedural_memory=proc,
        semantic_memory=sem,
        enable_learning=True,
    )

    phase_a_results = []
    phase_b_results = []
    phase_c_stable_results = []
    phase_c_secure_results = []

    # Stream of 100 tasks
    for i in range(100):
        if i < 30:
            # Phase A: 30 Stable tasks
            phase = "A"
            condition = "stable"
            env.reset(seed=i, scenario={"latent_condition": condition})
            goal = Goal(
                goal_id=f"task_{i}",
                description="Write data in stable environment",
                metadata={"latent_condition": condition, "idx": i},
            )
            res = controller.run(goal)
            phase_a_results.append(res.success)

        elif i < 70:
            # Phase B: 40 Secure tasks
            phase = "B"
            condition = "secure"
            env.reset(seed=i, scenario={"latent_condition": condition})
            goal = Goal(
                goal_id=f"task_{i}",
                description="Write data in secure environment",
                metadata={"latent_condition": condition, "idx": i},
            )
            res = controller.run(goal)
            phase_b_results.append(res.success)

        else:
            # Phase C: 30 Mixed Holdout tasks (alternating stable and secure)
            phase = "C"
            condition = "stable" if i % 2 == 0 else "secure"
            env.reset(seed=i, scenario={"latent_condition": condition})
            desc = "Write data in stable environment" if condition == "stable" else "Write data in secure environment"
            goal = Goal(
                goal_id=f"task_{i}",
                description=desc,
                metadata={"latent_condition": condition, "idx": i},
            )
            res = controller.run(goal)
            if condition == "stable":
                phase_c_stable_results.append(res.success)
            else:
                phase_c_secure_results.append(res.success)

    # Compute metrics
    acc_a = sum(phase_a_results) / len(phase_a_results)
    acc_b = sum(phase_b_results) / len(phase_b_results)
    acc_c_stable = sum(phase_c_stable_results) / len(phase_c_stable_results)
    acc_c_secure = sum(phase_c_secure_results) / len(phase_c_secure_results)
    total_acc = (sum(phase_a_results) + sum(phase_b_results) + sum(phase_c_stable_results) + sum(phase_c_secure_results)) / 100.0

    print(f"\nContinual Stream: Acc A = {acc_a:.2%}, Acc B = {acc_b:.2%}, Acc C(stable) = {acc_c_stable:.2%}, Acc C(secure) = {acc_c_secure:.2%}, Total = {total_acc:.2%}")

    # Assertions
    assert acc_a >= 0.90, f"Phase A performance degraded: {acc_a:.2%}"
    assert acc_b >= 0.90, f"Phase B performance degraded: {acc_b:.2%}"
    # Anti-forgetting test: Phase A tasks tested in Phase C must NOT have dropped below 90%
    assert acc_c_stable >= 0.90, f"Catastrophic forgetting detected for stable tasks in Phase C: {acc_c_stable:.2%}"
    assert acc_c_secure >= 0.90, f"Holdout performance degraded for secure tasks in Phase C: {acc_c_secure:.2%}"
    assert total_acc >= 0.90, f"Total stream accuracy below threshold: {total_acc:.2%}"
