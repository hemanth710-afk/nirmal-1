"""
Cognitive Learning V1 Behavioral Evaluation Suite.

Evaluates:
1. Three-phase protocol: Pre-experience baseline vs Post-experience learning gain.
2. Strategy transfer across unseen parameter variations.
3. Long-term memory retention across working memory context clears.
4. Interference & catastrophic forgetting immunity (sequential task learning).
5. Learning from failure: empirical penalization of failing procedures and fallback selection.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy
from nirmal.agent.memory.semantic import SemanticMemory
from nirmal.agent.memory.episodic import EpisodicMemory
from nirmal.agent.learning_engine import CognitiveLearningEngine
from nirmal.agent.verification import DeterministicVerifier
from nirmal.learning import EpisodicBuffer
from nirmal.tools import ToolRegistry, MockEnvironmentTool
from evals.novel_tasks import (
    EncodingPipelineFamily,
    ResourceDiscoveryFamily,
    DistractorRecoveryFamily,
)


def _setup_controller(mock_env: MockEnvironmentTool) -> CognitiveController:
    tools = ToolRegistry()
    tools.register(mock_env)
    return CognitiveController(
        tool_registry=tools,
        semantic_memory=SemanticMemory(),
        episodic_memory=EpisodicMemory(),
        procedural_memory=ProceduralMemory(),
        verifier=DeterministicVerifier(),
        learning_engine=CognitiveLearningEngine(),
        episodic_buffer=EpisodicBuffer(),
        enable_learning=True,
        enable_strategy_selection=True,
    )


def test_phase1_vs_phase3_learning_gain():
    """Evaluate learning gain: Phase 1 (cold start) vs Phase 3 (post-experience) on DistractorRecovery."""
    env = MockEnvironmentTool()
    controller = _setup_controller(env)

    # Phase 1: Pre-experience cold start (variation route_a)
    env.execute("write", key="primary_gateway", value="failing_gw")
    env.execute("write", key="backup_gateway", value="active_gw_1")
    env.execute("write", key="active_gw_1_status", value="ONLINE_READY")

    goal_a = Goal(
        goal_id="dist_phase1",
        description="Connect to verified gateway and fetch status for route_a",
        criteria="ONLINE_READY",
        task_family="distractor_recovery",
    )
    result_phase1 = controller.run(goal_a)

    assert result_phase1.success is True
    assert result_phase1.final_output == "ONLINE_READY"
    # Phase 1 encountered failure on primary gateway and required dynamic replan
    phase1_replans = result_phase1.episode.reasoning_summary if result_phase1.episode else ""
    assert "Replans: 1" in phase1_replans
    assert controller.strategy_used == "dynamic_linear_planner" or controller.strategy_used is None

    # Phase 2: Experience gathering (learning engine synthesized strategy from Phase 1)
    learned_strategies = [s for s in controller.procedural_memory.list_strategies() if s.task_family == "distractor_recovery"]
    assert len(learned_strategies) >= 1
    learned_strat = learned_strategies[0]
    assert learned_strat.reliability > 0.6  # Bayesian reliability increased from Laplace prior

    # Phase 3: Post-experience held-out test (variation route_b)
    env.execute("write", key="primary_gateway", value="failing_gw")
    env.execute("write", key="backup_gateway", value="active_gw_2")
    env.execute("write", key="active_gw_2_status", value="STANDBY_READY")

    goal_b = Goal(
        goal_id="dist_phase3",
        description="Connect to verified gateway and fetch status for route_b",
        criteria="STANDBY_READY",
        task_family="distractor_recovery",
    )
    result_phase3 = controller.run(goal_b)

    assert result_phase3.success is True
    assert result_phase3.final_output == "STANDBY_READY"
    # Phase 3 utilized the learned strategy directly, requiring 0 replans
    assert result_phase3.strategy_used == learned_strat.name
    phase3_replans = result_phase3.episode.reasoning_summary if result_phase3.episode else ""
    assert "Replans: 0" in phase3_replans
    assert result_phase3.total_steps < result_phase1.total_steps


def test_strategy_transfer_unseen_parameters():
    """Verify procedural strategy transfers to unseen parameters on EncodingPipelineFamily."""
    env = MockEnvironmentTool()
    controller = _setup_controller(env)

    # Episode 1: Initial task instance (alpha)
    goal_alpha = Goal(
        goal_id="enc_alpha",
        description="Transform text 'CognitiveArchitecture' with operation 'uppercase', then 'reverse', and compute length.",
        criteria=21,
        task_family="encoding_pipeline",
    )
    res_alpha = controller.run(goal_alpha)
    assert res_alpha.success is True
    assert res_alpha.final_output == 21

    # Verify strategy was synthesized
    enc_strats = [s for s in controller.procedural_memory.list_strategies() if s.task_family == "encoding_pipeline"]
    assert len(enc_strats) >= 1
    strat = enc_strats[0]
    initial_reliability = strat.reliability

    # Episode 2: Unseen parameter combination (gamma: 20-char text)
    goal_gamma = Goal(
        goal_id="enc_gamma",
        description="Transform text 'NeuralDeltaNetHybrid' with operation 'uppercase', then 'reverse', and compute length.",
        criteria=20,
        task_family="encoding_pipeline",
    )
    res_gamma = controller.run(goal_gamma)
    assert res_gamma.success is True
    assert res_gamma.final_output == 20
    assert res_gamma.strategy_used == strat.name
    # Strategy was reinforced through successful transfer
    assert strat.reliability > initial_reliability
    assert strat.success_count == 2


def test_retention_after_context_clear():
    """Verify long-term procedural and semantic memory retention after working memory context is wiped."""
    env = MockEnvironmentTool()
    controller = _setup_controller(env)

    # Train on resource discovery task
    env.execute("write", key="service_east", value="node_7")
    env.execute("write", key="node_7_port", value="8080")

    goal_train = Goal(
        goal_id="res_train",
        description="Inspect cluster 'cluster_east' to discover endpoint for 'service_east' and write active_session.",
        criteria="node_7:8080",
        task_family="resource_discovery",
    )
    res_train = controller.run(goal_train)
    assert res_train.success is True
    assert res_train.final_output == "node_7:8080"

    # Verify learned strategy is saved in long-term memory
    res_strats = [s for s in controller.procedural_memory.list_strategies() if s.task_family == "resource_discovery"]
    assert len(res_strats) >= 1

    # SIMULATE CONTEXT CLEAR: Wipe controller runtime state and working memory
    controller.reset()
    assert controller.working_memory is None
    assert controller.world_state is None
    assert controller.active_plan is None

    # Test retention on new cluster variation
    env.execute("write", key="service_north", value="node_9")
    env.execute("write", key="node_9_port", value="4430")

    goal_retained = Goal(
        goal_id="res_north",
        description="Inspect cluster 'cluster_north' to discover endpoint for 'service_north' and write active_session.",
        criteria="node_9:4430",
        task_family="resource_discovery",
    )
    res_retained = controller.run(goal_retained)
    assert res_retained.success is True
    assert res_retained.final_output == "node_9:4430"
    assert res_retained.strategy_used == res_strats[0].name


def test_interference_sequential_learning():
    """Verify that learning task family B does not degrade retained performance on task family A."""
    env = MockEnvironmentTool()
    controller = _setup_controller(env)

    # Step 1: Learn Task Family A (EncodingPipeline)
    goal_a1 = Goal(
        goal_id="enc_a1",
        description="Transform text 'CognitiveArchitecture' with operation 'uppercase', then 'reverse', and compute length.",
        criteria=21,
        task_family="encoding_pipeline",
    )
    res_a1 = controller.run(goal_a1)
    assert res_a1.success is True

    # Step 2: Learn Task Family B (DistractorRecovery)
    env.execute("write", key="primary_gateway", value="failing_gw")
    env.execute("write", key="backup_gateway", value="active_gw_1")
    env.execute("write", key="active_gw_1_status", value="ONLINE_READY")

    goal_b = Goal(
        goal_id="dist_b",
        description="Connect to verified gateway and fetch status for route_a",
        criteria="ONLINE_READY",
        task_family="distractor_recovery",
    )
    res_b = controller.run(goal_b)
    assert res_b.success is True

    # Step 3: Re-evaluate on Task Family A (unseen instance epsilon)
    goal_a2 = Goal(
        goal_id="enc_a2",
        description="Transform text 'EmpiricalVerification' with operation 'uppercase', then 'reverse', and compute length.",
        criteria=21,
        task_family="encoding_pipeline",
    )
    res_a2 = controller.run(goal_a2)
    assert res_a2.success is True
    assert res_a2.final_output == 21
    # Check that Task A's strategy was still matched and selected
    strat_a = [s for s in controller.procedural_memory.list_strategies() if s.task_family == "encoding_pipeline"][0]
    assert res_a2.strategy_used == strat_a.name
    # Verify no catastrophic forgetting: reliability of Task A is preserved and enhanced
    assert strat_a.reliability >= 0.66


def test_learning_from_failure_penalization():
    """Verify that execution/verification failures penalize strategy reliability and record negative constraints."""
    env = MockEnvironmentTool()
    controller = _setup_controller(env)

    # Register an intentionally faulty strategy with initial high reliability
    faulty_strategy = Strategy(
        name="faulty_arithmetic",
        task_family="arithmetic",
        description="Faulty arithmetic strategy with incorrect operation",
        trigger_patterns=["faulty_task", "perform faulty calculation"],
        when_applies=["faulty_task", "perform faulty calculation"],
        steps=[
            {
                "id": "step_fail",
                "description": "Execute failing operation",
                "tool_name": "calculator",
                "tool_args": {"expression": "invalid_variable_name + 1"},
            }
        ],
        total_trials=2,
        success_count=2,
        failure_count=0,
        reliability=0.75,  # (2 + 1) / (2 + 2)
    )
    controller.procedural_memory.register_strategy(faulty_strategy)
    initial_rel = faulty_strategy.reliability

    # Run controller on a goal matching the faulty strategy with Replanning OFF
    # to test failure recording
    controller.enable_replanning = False
    goal = Goal(
        goal_id="fail_eval",
        description="perform faulty calculation on input",
        criteria=42,
        task_family="arithmetic",
    )
    result = controller.run(goal)

    assert result.success is False
    assert result.state == ControllerState.FAILED
    assert result.error is not None

    # Verify that the strategy's reliability was penalized via Laplace update
    assert faulty_strategy.total_trials == 3
    assert faulty_strategy.failure_count == 1
    # New reliability = (2 + 1) / (3 + 2) = 3/5 = 0.60
    assert faulty_strategy.reliability < initial_rel
    assert faulty_strategy.reliability == pytest.approx(0.60, abs=1e-3)

    # Verify that the failure experience was stored in EpisodicBuffer
    failed_exps = controller.episodic_buffer.query(success=False)
    assert len(failed_exps) >= 1
    assert failed_exps[-1].task_id == "fail_eval"
    assert failed_exps[-1].failure_reason is not None

    # Verify negative constraint knowledge was stored in SemanticMemory
    constraints = [f for f in controller.semantic_memory.list_facts() if f.key.startswith("constraint_")]
    assert len(constraints) >= 1
    assert "Avoid path" in constraints[-1].content
