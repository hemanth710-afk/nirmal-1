"""
Evaluation Suite: Fine-Grained Credit Assignment vs Naive Uniform Attribution.

Tests:
1. Fine-grained causal credit assignment isolates failure to the culprit step (-1.0) while protecting prerequisite steps (+0.2).
2. Naive uniform attribution penalizes all steps indiscriminately (-1.0 to all).
3. Success credit rewards terminal nodes (+1.0) and dependencies (+0.8).
4. Running credit accumulation updates strategy.action_credits correctly.
"""

import pytest
from nirmal.agent.learning_engine import CognitiveLearningEngine
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy
from nirmal.learning import Experience


def test_fine_grained_credit_assignment_on_failure():
    engine = CognitiveLearningEngine(enable_credit_assignment=True)
    proc = ProceduralMemory()

    strat = Strategy(
        strategy_id="strat_multi_step",
        name="strat_multi_step",
        task_family="test",
        description="Multi-step test strategy",
        steps=[
            {"id": "step_1", "description": "Step 1", "tool_name": "t1", "tool_args": {}},
            {"id": "step_2", "description": "Step 2", "tool_name": "t2", "tool_args": {}},
            {"id": "step_3", "description": "Step 3", "tool_name": "t3", "tool_args": {}},
        ],
        success_rate=0.7,
    )
    proc.register_strategy(strat)

    # Simulated failing experience where step 2 failed
    exp = Experience(
        task_id="t_fail",
        trajectory_id="traj_fail",
        task_family="test",
        context="",
        goal="Test multi-step execution",
        retrieved_memory=[],
        proposed_plan={
            "nodes": {
                "step_1": {"node_id": "step_1", "status": "completed", "tool_name": "t1", "dependencies": []},
                "step_2": {"node_id": "step_2", "status": "failed", "tool_name": "t2", "dependencies": ["step_1"]},
                "step_3": {"node_id": "step_3", "status": "pending", "tool_name": "t3", "dependencies": ["step_2"]},
            }
        },
        actions=[
            {"action_id": "act_step_1_0", "tool_name": "t1", "arguments": {}},
            {"action_id": "act_step_2_1", "tool_name": "t2", "arguments": {}},
        ],
        observations=["Step 1 ok", "Step 2 execution error: out of memory"],
        verification_result={"is_valid": False, "score": 0.0, "message": "Step 2 failed"},
        reward=0.0,
        success=False,
        failure_reason="Step 2 failed",
        strategy_used="strat_multi_step",
        timestamp=100.0,
        episode_index=1,
    )

    report = engine.learn_from_experience(exp, procedural_memory=proc, enable_credit_assignment=True)

    # Step 2 was the culprit: should have negative credit
    assert "step_2" in strat.action_credits
    assert strat.action_credits["step_2"] < 0.0

    # Step 1 succeeded before the failure: should NOT be heavily penalized
    assert "step_1" in strat.action_credits
    assert strat.action_credits["step_1"] > strat.action_credits["step_2"]


def test_naive_uniform_attribution_penalizes_all():
    # When enable_credit_assignment is False, naive uniform attribution is applied
    engine = CognitiveLearningEngine(enable_credit_assignment=False)
    proc = ProceduralMemory()

    strat = Strategy(
        strategy_id="strat_naive",
        name="strat_naive",
        task_family="test",
        description="Naive attribution strategy",
        steps=[
            {"id": "step_1", "description": "Step 1", "tool_name": "t1", "tool_args": {}},
            {"id": "step_2", "description": "Step 2", "tool_name": "t2", "tool_args": {}},
        ],
        success_rate=0.7,
    )
    proc.register_strategy(strat)

    exp = Experience(
        task_id="t_fail_naive",
        trajectory_id="traj_naive",
        task_family="test",
        context="",
        goal="Test naive execution",
        retrieved_memory=[],
        proposed_plan={
            "nodes": {
                "step_1": {"node_id": "step_1", "status": "completed", "tool_name": "t1", "dependencies": []},
                "step_2": {"node_id": "step_2", "status": "failed", "tool_name": "t2", "dependencies": ["step_1"]},
            }
        },
        actions=[
            {"action_id": "act_step_1_0", "tool_name": "t1", "arguments": {}},
            {"action_id": "act_step_2_1", "tool_name": "t2", "arguments": {}},
        ],
        observations=["Step 1 ok", "Step 2 fail"],
        verification_result={"is_valid": False, "score": 0.0, "message": "Failed"},
        reward=0.0,
        success=False,
        failure_reason="Failed",
        strategy_used="strat_naive",
        timestamp=100.0,
        episode_index=1,
    )

    engine.learn_from_experience(exp, procedural_memory=proc, enable_credit_assignment=False)

    # In naive uniform attribution, both steps get identical negative credit (-0.3 via running update from 0.0)
    assert "step_1" in strat.action_credits
    assert "step_2" in strat.action_credits
    assert strat.action_credits["step_1"] == strat.action_credits["step_2"]
    assert strat.action_credits["step_1"] == pytest.approx(-0.3)


def test_success_credit_assignment():
    engine = CognitiveLearningEngine(enable_credit_assignment=True)
    proc = ProceduralMemory()

    strat = Strategy(
        strategy_id="strat_success",
        name="strat_success",
        task_family="test",
        description="Success strategy",
        steps=[
            {"id": "step_1", "description": "Step 1", "tool_name": "t1", "tool_args": {}},
            {"id": "step_2", "description": "Step 2", "tool_name": "t2", "tool_args": {}, "dependencies": ["step_1"]},
        ],
        success_rate=0.5,
    )
    proc.register_strategy(strat)

    exp = Experience(
        task_id="t_success",
        trajectory_id="traj_success",
        task_family="test",
        context="",
        goal="Test success execution",
        retrieved_memory=[],
        proposed_plan={
            "nodes": {
                "step_1": {"node_id": "step_1", "status": "completed", "tool_name": "t1", "dependencies": []},
                "step_2": {"node_id": "step_2", "status": "completed", "tool_name": "t2", "dependencies": ["step_1"]},
            }
        },
        actions=[
            {"action_id": "act_step_1_0", "tool_name": "t1", "arguments": {}},
            {"action_id": "act_step_2_1", "tool_name": "t2", "arguments": {}},
        ],
        observations=["Step 1 ok", "Step 2 ok"],
        verification_result={"is_valid": True, "score": 1.0, "message": "Success"},
        reward=1.0,
        success=True,
        failure_reason=None,
        strategy_used="strat_success",
        timestamp=100.0,
        episode_index=1,
    )

    engine.learn_from_experience(exp, procedural_memory=proc, enable_credit_assignment=True)

    # Terminal node step_2 receives highest credit (0.3), dependency step_1 receives 0.24
    assert strat.action_credits["step_2"] > strat.action_credits["step_1"] > 0.0
    assert strat.action_credits["step_2"] == pytest.approx(0.3)
    assert strat.action_credits["step_1"] == pytest.approx(0.24)
