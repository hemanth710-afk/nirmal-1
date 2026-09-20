"""
Compositional Learning Evaluation Suite.

Evaluates:
1. Dynamic chaining of subskills learned in isolation (Skill X: Transformation, Skill Y: Routing, Skill Z: Checksum).
2. Two-skill composition (X + Y): Baseline (0.0) vs Learned (1.0).
3. Three-skill composition (X + Y + Z): Prerequisite gating (requires all 3 subskills).
4. Compositional transfer across 5 seeds (1..5).
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


def train_on_specific_subskills(agent: CognitiveController, env: MockEnvironmentTool, exp_tasks: list[TransferTask], subskills: list[str]) -> None:
    """Train the agent exclusively on tasks corresponding to specified subskills."""
    for task in exp_tasks:
        if any(s in task.subskills for s in subskills):
            env.state.clear()
            env.state.update(task.initial_env_state)
            agent.run(task.to_goal())


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_two_skill_composition_across_seeds(seed: int):
    """Verify that agent possessing subskills X and Y can solve novel compound tasks (X+Y)."""
    suite = get_task_suite_for_seed(seed)
    env = MockEnvironmentTool()
    comp_task = next(t for t in suite["composition"] if t.task_family == "composition_xy")

    # 1. Baseline Agent: No learned subskills in procedural memory
    baseline_agent = create_agent(env)
    env.state.clear()
    env.state.update(comp_task.initial_env_state)
    baseline_res = baseline_agent.run(comp_task.to_goal())
    assert baseline_res.success is False, f"Baseline agent should not solve compound task {comp_task.task_id} without subskills"

    # 2. Learned Agent: Trained on isolated subskills X and Y
    learned_agent = create_agent(env)
    train_on_specific_subskills(learned_agent, env, suite["experience"], subskills=["X", "Y"])

    env.state.clear()
    env.state.update(comp_task.initial_env_state)
    learned_res = learned_agent.run(comp_task.to_goal())

    assert learned_res.success is True, f"Learned agent failed to compose subskills X+Y on seed {seed}"
    assert learned_res.final_output == comp_task.expected_output
    assert "composed" in str(learned_res.strategy_used).lower()


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_three_skill_composition_prerequisite_gating(seed: int):
    """Verify 3-skill compound task (X+Y+Z) strictly requires all 3 constituent subskills."""
    suite = get_task_suite_for_seed(seed)
    env = MockEnvironmentTool()
    comp_task = next(t for t in suite["composition"] if t.task_family == "composition_xyz")

    # Partial Agent: Has subskills X and Y, but MISSING Z (checksum)
    partial_agent = create_agent(env)
    train_on_specific_subskills(partial_agent, env, suite["experience"], subskills=["X", "Y"])

    env.state.clear()
    env.state.update(comp_task.initial_env_state)
    partial_res = partial_agent.run(comp_task.to_goal())
    # Missing subskill Z must prevent successful composition
    assert partial_res.success is False, f"Partial agent should fail compound task without subskill Z"

    # Complete Agent: Has all three subskills X, Y, and Z
    complete_agent = create_agent(env)
    train_on_specific_subskills(complete_agent, env, suite["experience"], subskills=["X", "Y", "Z"])

    env.state.clear()
    env.state.update(comp_task.initial_env_state)
    complete_res = complete_agent.run(comp_task.to_goal())

    assert complete_res.success is True, f"Complete agent failed to compose subskills X+Y+Z on seed {seed}"
    assert complete_res.final_output == comp_task.expected_output
    assert "composed" in str(complete_res.strategy_used).lower()


def test_compositional_isolation_invariant():
    """Verify procedural memory dynamically composes without ever seeing compound examples in training."""
    suite = get_task_suite_for_seed(seed=1)
    env = MockEnvironmentTool()
    agent = create_agent(env)

    # Train only on single-skill experience tasks
    train_on_specific_subskills(agent, env, suite["experience"], subskills=["X", "Y", "Z"])

    # Ensure no compound strategy existed prior to evaluation
    prior_strategies = [s.name for s in agent.procedural_memory.list_strategies()]
    assert not any("composed" in name for name in prior_strategies)

    # Trigger composition
    comp_task = suite["composition"][0]
    env.state.clear()
    env.state.update(comp_task.initial_env_state)
    res = agent.run(comp_task.to_goal())

    assert res.success is True
    assert res.final_output == comp_task.expected_output
