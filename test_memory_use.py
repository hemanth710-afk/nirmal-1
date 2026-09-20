"""
Memory Subsystem Behavioral Evaluations (Task A & Task E Ablation).
Evaluates semantic memory fact retrieval, episodic recording/recall,
and empirical performance with Memory ON vs Memory OFF.
"""

import pytest
from nirmal.agent.controller import CognitiveController, ControllerState, Goal
from nirmal.agent.memory.procedural import ProcedureTemplate


def test_semantic_memory_recall_task_a(controller):
    """Task A: Goal requiring factual memory retrieval to solve."""
    # Memory was pre-seeded with secret_access_code = "omega-42" in fixture
    goal = Goal(
        goal_id="task_a_mem",
        description="What is the secret_access_code?",
        criteria="omega-42",
    )
    result = controller.run(goal)

    assert result.success is True
    assert result.state == ControllerState.DONE
    assert result.final_output == "omega-42"
    # Verify memory retrieval step is in trace
    retrieval_steps = [s for s in result.execution_trace if s.state == ControllerState.RETRIEVE]
    assert len(retrieval_steps) >= 1
    assert "secret_access_code" in controller.world_state.facts


def test_memory_ablation_comparison_task_e(tool_registry, semantic_memory, episodic_memory, procedural_memory, verifier):
    """Task E (Memory Axis): Compare performance with Memory ON vs Memory OFF on knowledge retrieval."""
    goal_query = "What is the capital_of_france?"

    # 1. Run with Memory ON
    controller_on = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_memory=True,
    )
    result_on = controller_on.run(Goal(goal_id="g_mem_on", description=goal_query, criteria="Paris"))
    assert result_on.success is True
    assert result_on.final_output == "Paris"

    # 2. Run with Memory OFF
    controller_off = CognitiveController(
        tool_registry=tool_registry,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        procedural_memory=procedural_memory,
        verifier=verifier,
        enable_memory=False,
    )
    result_off = controller_off.run(Goal(goal_id="g_mem_off", description=goal_query, criteria="Paris"))
    # Without memory, the controller cannot produce the ungrounded fact "Paris"
    assert result_off.final_output != "Paris"
    assert "capital_of_france" not in controller_off.world_state.facts


def test_episodic_memory_storage_and_retrieval(controller, episodic_memory):
    """Verify that successful execution runs deposit rich episodes into EpisodicMemory."""
    assert len(episodic_memory.episodes) == 0

    result = controller.run("Calculate 8 * 9")
    assert result.success is True

    # Check that an Episode was deposited
    assert len(episodic_memory.episodes) == 1
    episode = episodic_memory.episodes[0]
    assert episode.goal == "Calculate 8 * 9"
    assert episode.success is True
    assert episode.reward == 1.0
    assert len(episode.actions) >= 1
    assert episode.outcome == 72.0

    # Retrieve similar episodes by keyword
    retrieved = episodic_memory.retrieve_similar("Calculate", top_k=2)
    assert len(retrieved) == 1
    assert retrieved[0].episode_id == episode.episode_id


def test_procedural_memory_matching_and_reinforcement(procedural_memory):
    """Verify that procedural templates match relevant goals and record success counts."""
    matched = procedural_memory.find_matching_procedure("Please compute 45 * 2")
    assert matched is not None
    assert matched.name == "arithmetic_eval"

    init_count = matched.success_count
    procedural_memory.record_success("arithmetic_eval")
    assert procedural_memory.get_procedure("arithmetic_eval").success_count == init_count + 1
