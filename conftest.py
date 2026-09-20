"""
Pytest configuration and shared fixtures for Nirmal-1 evaluations.
"""

import pytest
from nirmal.tools import ToolRegistry, MockEnvironmentTool, CalculatorTool, StringUtilityTool
from nirmal.agent.verification import DeterministicVerifier
from nirmal.agent.memory.semantic import SemanticMemory
from nirmal.agent.memory.episodic import EpisodicMemory
from nirmal.agent.memory.procedural import ProceduralMemory
from nirmal.agent.controller import CognitiveController


@pytest.fixture
def mock_env():
    """Provides a fresh MockEnvironmentTool instance."""
    return MockEnvironmentTool()


@pytest.fixture
def tool_registry(mock_env):
    """Provides a ToolRegistry configured with standard tools and mock env."""
    reg = ToolRegistry()
    reg.register(mock_env)
    return reg


@pytest.fixture
def semantic_memory():
    """Provides a SemanticMemory instance pre-seeded with benchmark facts."""
    mem = SemanticMemory()
    mem.store_fact("secret_access_code", "omega-42")
    mem.store_fact("system_status", "operational")
    mem.store_fact("capital_of_france", "Paris")
    mem.store_fact("pi_approx", "3.14159")
    return mem


@pytest.fixture
def episodic_memory():
    """Provides a fresh EpisodicMemory instance."""
    return EpisodicMemory()


@pytest.fixture
def procedural_memory():
    """Provides a fresh ProceduralMemory instance with default skills."""
    return ProceduralMemory()


@pytest.fixture
def verifier():
    """Provides a DeterministicVerifier instance."""
    return DeterministicVerifier(numeric_tolerance=1e-5)


@pytest.fixture
def controller(tool_registry, semantic_memory, episodic_memory, procedural_memory, verifier):
    """Provides a default CognitiveController configured with full capabilities."""
    return CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_memory=True,
        enable_planning=True,
        enable_verification=True,
        enable_replanning=True,
    )
