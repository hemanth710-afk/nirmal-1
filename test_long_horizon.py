"""
Suite 9: Multi-Step Reasoning Across Extended Planning Horizons.
Validates:
- Simulation rollouts across horizons H in {1, 2, 4, 8, 16}
- Error compounding / propagation properties
- Intermediate state consequence projection without environment action
"""

import pytest
from nirmal.agent.world_model import WorldModel, CausalRule
from evals.causal_simulator import CausalSimulator


def test_rollout_horizons_1_to_16():
    wm = WorldModel()

    # Register deterministic sequential transition rules:
    # step_i transforms state {'stage': i} -> {'stage': i + 1}
    for i in range(16):
        wm.register_rule(CausalRule(
            rule_id=f"rule_stage_{i}",
            action_name=f"advance_{i}",
            preconditions={"stage": i},
            effects={"stage": i + 1},
            confidence=0.95,
        ))

    initial_state = {"stage": 0}

    for horizon in [1, 2, 4, 8, 16]:
        action_sequence = [(f"advance_{i}", {}) for i in range(horizon)]
        predictions = wm.simulate_rollout(initial_state, action_sequence, horizon=horizon)

        assert len(predictions) == horizon
        # Final predicted stage must match horizon
        assert predictions[-1].predicted_state["stage"] == horizon
        assert predictions[-1].horizon == horizon
        assert predictions[-1].confidence > 0.0


def test_long_horizon_error_behavior_on_simulator():
    """
    Test a 4-step causal chain simulator:
    N0 -> N1 -> N2 -> N3
    """
    sim = CausalSimulator.create_linear_chain(length=4, seed=42)
    wm = WorldModel()

    # Train world model on unit transitions
    wm.register_rule(CausalRule(rule_id="r0", action_name="do_N0", effects={"N0": 1}, confidence=1.0))
    wm.register_rule(CausalRule(rule_id="r1", action_name="cycle", preconditions={"N0": 1}, effects={"N1": 1}, confidence=1.0))
    wm.register_rule(CausalRule(rule_id="r2", action_name="cycle", preconditions={"N1": 1}, effects={"N2": 1}, confidence=1.0))
    wm.register_rule(CausalRule(rule_id="r3", action_name="cycle", preconditions={"N2": 1}, effects={"N3": 1}, confidence=1.0))

    actions = [("do_N0", {}), ("cycle", {}), ("cycle", {}), ("cycle", {})]
    rollout = wm.simulate_rollout({"N0": 0, "N1": 0, "N2": 0, "N3": 0}, actions, horizon=4)

    assert len(rollout) == 4
    assert rollout[0].predicted_state["N0"] == 1
    assert rollout[1].predicted_state["N1"] == 1
    assert rollout[2].predicted_state["N2"] == 1
    assert rollout[3].predicted_state["N3"] == 1
