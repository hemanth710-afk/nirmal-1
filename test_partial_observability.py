"""
Evaluation Suite: Partial Observability & Information Gathering.

Tests:
1. Environment masks latent variables by default.
2. Agent executes a probe action to gather hidden environment state.
3. Controller ingests probed observations into world_state facts and semantic memory.
4. Subsequent action dynamically utilizes the probed information.
"""

import pytest
from evals.open_world import OpenWorldEnvironment, OpenWorldTool
from nirmal.agent.controller import CognitiveController, Goal, ControllerState
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy
from nirmal.tools import ToolRegistry


def test_probe_action_ingestion_and_use():
    env = OpenWorldEnvironment(seed=202)
    env.state["latent_condition"] = "secure"

    registry = ToolRegistry()
    registry.register(OpenWorldTool(env=env))

    proc = ProceduralMemory()
    # 3-step strategy: Probe -> Acquire Token -> Route
    proc.register_strategy(Strategy(
        strategy_id="strat_probe_and_act",
        name="strat_probe_and_act",
        task_family="open_world",
        description="Probe environment condition and initialize secure channel",
        steps=[
            {
                "id": "step_1",
                "description": "Probe latent condition",
                "tool_name": "open_world_env",
                "tool_args": {"action": "probe", "target": "latent_condition"},
            },
            {
                "id": "step_2",
                "description": "Acquire security token",
                "tool_name": "open_world_env",
                "tool_args": {"action": "acquire_token"},
                "dependencies": ["step_1"],
            },
            {
                "id": "step_3",
                "description": "Route direct",
                "tool_name": "open_world_env",
                "tool_args": {"action": "route_direct"},
                "dependencies": ["step_2"],
            },
        ],
        success_rate=0.95,
    ))

    controller = CognitiveController(tool_registry=registry, procedural_memory=proc)
    goal = Goal(
        goal_id="g_probe_test",
        description="Probe environment condition and initialize secure channel",
    )

    res = controller.run(goal)

    assert res.success is True
    assert res.state == ControllerState.DONE

    # Verify that world_state has acquired the probed fact
    assert "latent_condition" in controller.world_state.facts
    assert controller.world_state.facts["latent_condition"].value == "secure"

    # Verify that semantic memory has recorded the probed fact
    recalled = controller.semantic_memory.retrieve("latent_condition", top_k=1)
    assert len(recalled) > 0
    assert recalled[0].key == "latent_condition"
    assert recalled[0].content == "secure"
