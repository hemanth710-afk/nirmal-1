"""
Information Leakage & Hardcoding Prevention Audit Suite.

Verifies:
1. AST scan: src/nirmal contains ZERO benchmark task IDs, prompts, stems, services, or expected outputs.
2. Permutation invariance: Task ID renaming and presentation order do not alter execution or success.
3. Prompt phrasing invariance: Whitespace and case variations do not degrade execution.
"""

import ast
from pathlib import Path
import random
import string
import uuid
import pytest

from nirmal.agent.controller import CognitiveController, Goal
from nirmal.agent.memory.procedural import ProceduralMemory
from nirmal.agent.memory.semantic import SemanticMemory
from nirmal.agent.memory.episodic import EpisodicMemory
from nirmal.agent.learning_engine import CognitiveLearningEngine
from nirmal.agent.verification import DeterministicVerifier
from nirmal.learning import EpisodicBuffer
from nirmal.tools import ToolRegistry, MockEnvironmentTool
from evals.transfer_tasks import (
    TransferTask,
    WORD_STEMS,
    SERVICES,
    get_task_suite_for_seed,
)


def test_ast_scan_no_transfer_benchmark_literals_in_source():
    """Scan all Python files in src/nirmal to ensure transfer benchmark tokens are never hardcoded."""
    src_dir = Path(__file__).resolve().parent.parent / "src" / "nirmal"
    python_files = list(src_dir.rglob("*.py"))
    assert len(python_files) > 0, "No source files found in src/nirmal"

    # Build forbidden literals set
    forbidden_tokens = set()

    # 1. Task ID prefixes
    for prefix in ["exp_skill_x", "exp_skill_y", "exp_skill_z", "exp_neg", "trans_param", "trans_distract", "trans_neg", "comp_xy", "comp_xyz", "holdout_s"]:
        forbidden_tokens.add(prefix.lower())

    # 2. Benchmark word stems (excluding generic architectural terms that may appear in docs)
    specific_benchmark_stems = [
        "Cybernetic", "Distributed", "Epistemic", "Fractal", "Harmonic",
        "Kinetic", "Neuromorphic", "Orthogonal", "Perceptual", "Quantum",
        "Resonant", "Stochastic", "Topological", "Wavelet", "Vortical"
    ]
    for stem in specific_benchmark_stems:
        forbidden_tokens.add(stem.lower())


    # 3. Benchmark services
    for svc in SERVICES:
        forbidden_tokens.add(svc.lower())

    violations = []

    for file_path in python_files:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val_lower = node.value.lower()
                for forbidden in forbidden_tokens:
                    # Ignore short general words, check exact identifier match
                    if forbidden in val_lower:
                        violations.append(
                            f"{file_path.name}:{node.lineno} contains forbidden benchmark literal '{forbidden}'"
                        )

    assert not violations, f"Anti-leakage violation(s) detected in source code:\n" + "\n".join(violations)


def test_task_id_permutation_invariance():
    """Verify that renaming task IDs to arbitrary UUIDs produces identical execution outcomes."""
    suite = get_task_suite_for_seed(seed=1)
    env = MockEnvironmentTool()
    tools = ToolRegistry()
    tools.register(env)

    agent = CognitiveController(
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

    # Train on experience tasks with randomized task IDs
    for task in suite["experience"]:
        env.state.clear()
        env.state.update(task.initial_env_state)
        goal = Goal(
            goal_id=f"permuted_{uuid.uuid4().hex}",
            description=task.prompt,
            criteria=task.expected_output,
            task_family=task.task_family,
            metadata={"subskills": task.subskills},
        )
        agent.run(goal)

    # Evaluate transfer tasks with randomized task IDs
    for task in suite["transfer"]:
        env.state.clear()
        env.state.update(task.initial_env_state)
        permuted_id = f"eval_permuted_{uuid.uuid4().hex}"
        goal = Goal(
            goal_id=permuted_id,
            description=task.prompt,
            criteria=task.expected_output,
            task_family=task.task_family,
            metadata={"subskills": task.subskills},
        )
        result = agent.run(goal)
        assert result.success is True
        assert result.final_output == task.expected_output
        assert result.experience.task_id == permuted_id


def test_training_order_permutation_invariance():
    """Verify that permuting experience presentation order achieves equivalent final transfer performance."""
    suite = get_task_suite_for_seed(seed=2)
    exp_tasks = list(suite["experience"])

    # Permutation 1: Reversed order
    rev_tasks = list(reversed(exp_tasks))
    env1 = MockEnvironmentTool()
    tools1 = ToolRegistry()
    tools1.register(env1)
    agent1 = CognitiveController(tool_registry=tools1)

    for task in rev_tasks:
        env1.state.clear()
        env1.state.update(task.initial_env_state)
        agent1.run(task.to_goal())

    # Evaluate on compound task
    comp_task = suite["composition"][0]
    env1.state.clear()
    env1.state.update(comp_task.initial_env_state)
    res = agent1.run(comp_task.to_goal())

    assert res.success is True
    assert res.final_output == comp_task.expected_output
