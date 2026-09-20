"""
Negative Learning & Constraint Acquisition Evaluation Suite.

Evaluates:
1. Trap failure rate before negative learning under condition C (network_traffic = congested).
2. Cognitive failure extraction: semantic constraint generation and strategy penalization.
3. Reduction in failure rate on novel transfer tasks under condition C after negative learning.
4. Generalization across seeds 1..5 and on held-out tasks.
"""

import pytest

from nirmal.agent.controller import CognitiveController, Goal
from nirmal.agent.memory.procedural import ProceduralMemory
from nirmal.agent.memory.semantic import SemanticMemory
from nirmal.agent.memory.episodic import EpisodicMemory
from nirmal.agent.learning_engine import CognitiveLearningEngine
from nirmal.agent.verification import DeterministicVerifier
from nirmal.learning import EpisodicBuffer
from nirmal.tools import ToolRegistry, MockEnvironmentTool
from evals.transfer_tasks import TransferTask, get_task_suite_for_seed


def create_agent(env: MockEnvironmentTool) -> CognitiveController:
    """Instantiate a clean cognitive controller connected to the environment."""
    tools = ToolRegistry()
    tools.register(env)
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


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_negative_learning_failure_reduction_across_seeds(seed: int):
    """Verify failure rate under trap condition C drops significantly after experiencing failure."""
    suite = get_task_suite_for_seed(seed)
    env = MockEnvironmentTool()
    neg_exp_task = next(t for t in suite["experience"] if t.task_family == "skill_resilient_routing")
    neg_transfer_task = next(t for t in suite["transfer"] if t.task_family == "skill_resilient_routing")

    # 1. Pre-negative-learning baseline agent
    baseline_agent = create_agent(env)
    env.state.clear()
    env.state.update(neg_transfer_task.initial_env_state)
    pre_result = baseline_agent.run(neg_transfer_task.to_goal())

    # Naive baseline MUST fall into trap
    failure_rate_before = 1.0 if not pre_result.success else 0.0
    assert failure_rate_before == 1.0, f"Baseline agent unexpectedly passed trap task {neg_transfer_task.task_id}"

    # 2. Provide negative experience under condition C
    learned_agent = create_agent(env)
    env.state.clear()
    env.state.update(neg_exp_task.initial_env_state)
    exp_res = learned_agent.run(neg_exp_task.to_goal())
    assert exp_res.success is False, "Experience task must trigger initial environmental trap failure"

    # Verify semantic memory acquired constraint
    congested_facts = [
        content for key, content in learned_agent.semantic_memory.fact_dict.items()
        if "congested" in key.lower() or "congested" in content.lower()
    ]
    assert len(congested_facts) >= 1, "Agent failed to store semantic avoidance constraint after failure"

    # 3. Post-negative-learning evaluation on novel transfer task under condition C
    env.state.clear()
    env.state.update(neg_transfer_task.initial_env_state)
    post_result = learned_agent.run(neg_transfer_task.to_goal())

    failure_rate_after = 0.0 if post_result.success else 1.0
    assert failure_rate_after == 0.0, f"Learned agent failed to avoid trap on novel transfer task {neg_transfer_task.task_id}"
    assert post_result.final_output == neg_transfer_task.expected_output

    # 4. Assert failure rate reduction
    failure_reduction = failure_rate_before - failure_rate_after
    assert failure_reduction == 1.0, f"Failure reduction must be 1.0 (got {failure_reduction})"


def test_negative_learning_generalizes_to_strict_holdout():
    """Verify learned negative constraint generalizes to held-out task configurations."""
    suite = get_task_suite_for_seed(seed=3)
    env = MockEnvironmentTool()
    neg_exp_task = next(t for t in suite["experience"] if t.task_family == "skill_resilient_routing")
    holdout_task = next(t for t in suite["holdout"] if t.task_family == "skill_resilient_routing")

    agent = create_agent(env)
    # Experience failure
    env.state.clear()
    env.state.update(neg_exp_task.initial_env_state)
    agent.run(neg_exp_task.to_goal())

    # Evaluate on held-out configuration
    env.state.clear()
    env.state.update(holdout_task.initial_env_state)
    res = agent.run(holdout_task.to_goal())

    assert res.success is True
    assert res.final_output == holdout_task.expected_output
