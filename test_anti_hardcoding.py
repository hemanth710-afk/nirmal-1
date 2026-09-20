"""
Anti-Hardcoding & Generalization Verification Suite.

Asserts:
1. AST audit: Agent source code contains NO hardcoded benchmark answers or task solutions.
2. Robustness to Task ID permutation: Agent execution is agnostic to task_id values.
3. Random input generalization: Arbitrary unseen random string transformations succeed dynamically.
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


FORBIDDEN_BENCHMARK_LITERALS = [
    "node_7:8080",
    "node_3:9090",
    "node_9:4430",
    "node_2:7070",
    "ONLINE_READY",
    "STANDBY_READY",
    "SECURE_ACK",
    "CognitiveArchitecture",
    "AutonomousReasoningAgent",
    "NeuralDeltaNetHybrid",
    "SelfImprovingSystem",
    "EmpiricalVerification",
]


def test_ast_scan_no_hardcoded_benchmark_solutions():
    """Scan all Python files in src/ to ensure benchmark answers and task IDs are never hardcoded."""
    src_dir = Path(__file__).resolve().parent.parent / "src" / "nirmal"
    python_files = list(src_dir.rglob("*.py"))

    assert len(python_files) > 0, "No source files found in src/nirmal"

    violations = []

    for file_path in python_files:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for forbidden in FORBIDDEN_BENCHMARK_LITERALS:
                    if forbidden.lower() in node.value.lower():
                        violations.append(
                            f"{file_path.name}:{node.lineno} contains forbidden literal '{forbidden}'"
                        )

    assert not violations, f"Anti-hardcoding violation(s) detected:\n" + "\n".join(violations)


def test_task_id_agnostic_execution():
    """Verify that replacing task_id with random UUIDs does not alter behavior or success."""
    env = MockEnvironmentTool()
    tools = ToolRegistry()
    tools.register(env)

    controller = CognitiveController(
        tool_registry=tools,
        semantic_memory=SemanticMemory(),
        episodic_memory=EpisodicMemory(),
        procedural_memory=ProceduralMemory(),
        verifier=DeterministicVerifier(),
        learning_engine=CognitiveLearningEngine(),
        episodic_buffer=EpisodicBuffer(),
    )

    env.execute("write", key="service_east", value="node_7")
    env.execute("write", key="node_7_port", value="8080")

    # Use completely random GUID as task_id
    random_task_id = f"custom_uuid_{uuid.uuid4().hex}"
    goal = Goal(
        goal_id=random_task_id,
        description="Inspect cluster 'cluster_east' to discover endpoint for 'service_east' and write active_session.",
        criteria="node_7:8080",
        task_family="resource_discovery",
    )

    result = controller.run(goal)
    assert result.success is True
    assert result.final_output == "node_7:8080"
    assert result.experience.task_id == random_task_id


def test_random_string_dynamic_generalization():
    """Verify execution on entirely random input strings without memorization."""
    tools = ToolRegistry()
    controller = CognitiveController(tool_registry=tools)

    # Generate a random 15-character string
    random_word = "".join(random.choices(string.ascii_letters, k=15))
    expected_length = 15

    goal = Goal(
        goal_id=f"rand_{uuid.uuid4().hex[:6]}",
        description=f"Transform text '{random_word}' with operation 'uppercase', then 'reverse', and compute length.",
        criteria=expected_length,
        task_family="encoding_pipeline",
    )

    result = controller.run(goal)
    assert result.success is True
    assert result.final_output == expected_length
