"""
Transfer Learning V2 Evaluation Suite.

Evaluates:
1. Baseline Agent vs Learned Agent across seeds (1..5).
2. Positive Transfer Gain: Gain = Learned - Baseline > 0.
3. Parameter and distractor generalization.
4. Retention across working memory reset.
5. Replan and step count efficiency gain.
"""

from typing import List
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


def train_agent(controller: CognitiveController, env: MockEnvironmentTool, experience_tasks: List[TransferTask]) -> None:
    """Train the agent by sequentially executing tasks from the experience partition."""
    for task in experience_tasks:
        env.state.clear()
        env.state.update(task.initial_env_state)
        controller.run(task.to_goal())


def evaluate_agent(controller: CognitiveController, env: MockEnvironmentTool, eval_tasks: List[TransferTask]) -> float:
    """Evaluate agent success rate over a given task partition."""
    successes = 0
    for task in eval_tasks:
        env.state.clear()
        env.state.update(task.initial_env_state)
        res = controller.run(task.to_goal())
        if res.success and res.final_output == task.expected_output:
            successes += 1
    return successes / len(eval_tasks) if eval_tasks else 0.0


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_transfer_learning_gain_across_seeds(seed: int):
    """Assert positive transfer gain (Learned > Baseline) on novel transfer tasks across 5 seeds."""
    suite = get_task_suite_for_seed(seed)
    env = MockEnvironmentTool()

    # 1. Baseline Agent: Cold start without experience partition training
    baseline_agent = create_agent(env)
    baseline_score = evaluate_agent(baseline_agent, env, suite["transfer"])

    # 2. Learned Agent: Trained on Experience partition
    learned_agent = create_agent(env)
    train_agent(learned_agent, env, suite["experience"])
    learned_score = evaluate_agent(learned_agent, env, suite["transfer"])

    transfer_gain = learned_score - baseline_score

    # Learned agent must achieve superior performance over baseline
    assert learned_score == 1.0, f"Seed {seed}: Learned agent did not solve all transfer tasks ({learned_score})"
    assert baseline_score < 1.0, f"Seed {seed}: Baseline agent did not fail on trap tasks ({baseline_score})"
    assert transfer_gain > 0.0, f"Seed {seed}: Transfer gain must be strictly positive (got {transfer_gain})"


def test_transfer_memory_retention_across_resets():
    """Verify learned transfer strategies persist across working memory resets and episodes."""
    suite = get_task_suite_for_seed(seed=1)
    env = MockEnvironmentTool()
    agent = create_agent(env)

    # Train on experience partition
    train_agent(agent, env, suite["experience"])

    # Explicitly clear working memory and reset transient session state
    agent.reset()
    assert agent.working_memory is None
    assert agent.world_state is None

    # Long-term procedural and semantic memory must retain learned capabilities
    assert len(agent.procedural_memory.list_strategies()) > 2
    assert len(agent.semantic_memory.fact_dict) >= 1

    # Transfer evaluation must succeed immediately
    transfer_score = evaluate_agent(agent, env, suite["transfer"])
    assert transfer_score == 1.0


def test_replan_efficiency_gain_on_transfer():
    """Verify learned agent solves novel resilient tasks with 0 replan attempts."""
    suite = get_task_suite_for_seed(seed=2)
    env = MockEnvironmentTool()

    agent = create_agent(env)
    train_agent(agent, env, suite["experience"])

    # Find novel congested transfer task
    neg_transfer_task = next(t for t in suite["transfer"] if t.task_family == "skill_resilient_routing")
    env.state.clear()
    env.state.update(neg_transfer_task.initial_env_state)

    res = agent.run(neg_transfer_task.to_goal())
    assert res.success is True
    assert res.final_output == neg_transfer_task.expected_output
    assert res.episode is not None
    assert "Replans: 0" in res.episode.reasoning_summary
