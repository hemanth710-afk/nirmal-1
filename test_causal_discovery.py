"""
Suite 4: Causal Discovery from Unlabelled Transition Streams.
Validates:
- Synthesis of new CausalRules without pre-annotated strategy labels
- Construction of causal edges in the CausalGraph
- Convergence to correct causal preconditions and effects
"""

import pytest
from nirmal.agent.world_model import WorldModel
from evals.causal_simulator import CausalSimulator


def test_discovery_of_novel_causal_rules():
    wm = WorldModel()
    assert len(wm.rules) == 0

    # Stream unlabelled transitions
    transitions = [
        ({"valve": "closed", "flow": 0}, "turn_valve", {"valve": "open", "flow": 50}),
        ({"valve": "open", "flow": 50}, "turn_valve", {"valve": "closed", "flow": 0}),
        ({"switch": "off", "light": 0}, "flip_switch", {"switch": "on", "light": 1}),
    ]

    for s_t, act, s_t1 in transitions:
        wm.observe_transition(state_t=s_t, action_name=act, state_t1=s_t1)

    # World model should have discovered rules for 'turn_valve' and 'flip_switch'
    assert len(wm.rules) >= 2
    rule_actions = {r.action_name for r in wm.rules.values()}
    assert "turn_valve" in rule_actions
    assert "flip_switch" in rule_actions

    # Causal graph should contain edges from actions to changed variables
    assert wm.causal_graph.get_children("turn_valve") == {"valve", "flow"}
    assert wm.causal_graph.get_children("flip_switch") == {"switch", "light"}


def test_discovery_on_procedural_simulator():
    sim = CausalSimulator.create_linear_chain(length=4, seed=123)
    wm = WorldModel()

    # Step 1: Intervene on N0
    obs, info = sim.step({"type": "do", "target": "N0", "value": 1})
    wm.observe_transition(state_t=info["pre_state"], action_name="do_N0", state_t1=obs, is_intervention=True)

    # Step 2: Next cycle, N1 becomes 1
    obs2, info2 = sim.step({"type": "observe"})
    wm.observe_transition(state_t=info2["pre_state"], action_name="cycle", state_t1=obs2)

    # Verify rule creation and graph expansion
    assert len(wm.rules) >= 1
    assert any(r.is_causal for r in wm.rules.values())
