"""
Suite 7: Model Revision on Unexpected Consequences and Side-Effects.
Validates:
- Observation of unexpected consequences / secondary side-effects
- Automatic update of rule.side_effects
- Monotonic reduction of prediction error after revision
"""

import pytest
from nirmal.agent.world_model import WorldModel, CausalRule
from evals.causal_simulator import CausalSimulator


def test_unexpected_side_effect_absorption():
    wm = WorldModel()
    # Initial incomplete rule: expects 'coolant_flow' to change 'temp', but does not know about 'pressure_drop'
    wm.register_rule(CausalRule(
        rule_id="r_coolant",
        action_name="inject_coolant",
        effects={"temp": 20},
        confidence=0.8,
    ))

    # Initial state
    s0 = {"temp": 80, "pressure": 100}
    pred_initial = wm.predict(s0, "inject_coolant")
    assert "pressure" not in pred_initial.predicted_state or pred_initial.predicted_state["pressure"] == 100

    # Reality: injection drops temp to 20 BUT ALSO drops pressure to 40 (unexpected side-effect)
    s1 = {"temp": 20, "pressure": 40}
    err_1 = pred_initial.evaluate_error(s1)
    assert err_1 > 0.0, "Initial incomplete model should exhibit non-zero prediction error."

    # Update world model from this transition
    wm.observe_transition(state_t=s0, action_name="inject_coolant", state_t1=s1)

    # Check that the rule learned the unexpected side effect
    rule = wm.get_rule("r_coolant")
    assert "pressure" in rule.side_effects
    assert rule.side_effects["pressure"] == 40

    # Subsequent prediction from same state must now predict BOTH temp and pressure drop accurately
    pred_revised = wm.predict(s0, "inject_coolant")
    assert pred_revised.predicted_state["temp"] == 20
    assert pred_revised.predicted_state["pressure"] == 40
    err_2 = pred_revised.evaluate_error(s1)
    assert err_2 == 0.0, "Revised model prediction error must be 0.0 on identical transition."


def test_branching_side_effect_in_simulator():
    sim = CausalSimulator.create_branching_system(seed=99)
    wm = WorldModel()

    # Reset simulator
    sim.reset({"A": 1, "alarm": 0})
    # Step: A=1 triggers B=1 and C=1
    obs1, info1 = sim.step({"type": "observe"})
    wm.observe_transition(info1["pre_state"], "observe", obs1)

    # Step: C=1 triggers E=1 and alarm=1 (side effect)
    obs2, info2 = sim.step({"type": "observe"})
    wm.observe_transition(info2["pre_state"], "observe", obs2)

    # World model should have recorded the alarm side effect
    rules_with_alarm = [r for r in wm.rules.values() if "alarm" in r.effects or "alarm" in r.side_effects]
    assert len(rules_with_alarm) >= 1
