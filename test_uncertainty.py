"""
Suite 6: Uncertainty Estimation, Brier Calibration, and Active Experimentation.
Validates:
- Bayesian confidence calibration and Brier score evaluation
- High uncertainty on unseen / conflicting rules, low uncertainty on verified rules
- Active experimentation picks highest uncertainty actions for information gain
"""

import pytest
from nirmal.agent.world_model import WorldModel, CausalRule


def test_brier_score_calibration():
    wm = WorldModel()

    # Rule with 0.9 confidence that regularly succeeds
    wm.register_rule(CausalRule(
        rule_id="r_high_conf",
        action_name="action_a",
        effects={"status": "ok"},
        confidence=0.9,
    ))

    # Test predictions and actual outcomes
    state = {"status": "init"}
    pred1 = wm.predict(state, "action_a")
    # Outcome matches
    wm.observe_transition(state, "action_a", {"status": "ok"})

    # Brier component for step 1: (0.9 - 1.0)^2 = 0.01
    brier = wm.evaluate_calibration()
    assert brier == pytest.approx(0.01, abs=1e-3)

    # Now make an incorrect high-confidence prediction
    wm.get_rule("r_high_conf").confidence = 0.9
    pred2 = wm.predict(state, "action_a")
    # Unexpected outcome occurs
    wm.observe_transition(state, "action_a", {"status": "failed"})

    # Brier component for step 2: (0.9 - 0.0)^2 = 0.81
    # Average Brier = (0.01 + 0.81) / 2 = 0.41
    brier_after = wm.evaluate_calibration()
    assert brier_after == pytest.approx(0.41, abs=1e-3)


def test_active_experimentation_recommendation():
    wm = WorldModel()

    # Familiar action: tested 20 times, low uncertainty
    wm.register_rule(CausalRule(
        rule_id="r_familiar",
        action_name="familiar_act",
        effects={"x": 1},
        confidence=0.95,
        evidence_count=20,
        uncertainty=0.05,
    ))

    # Novel action: untested, high uncertainty
    wm.register_rule(CausalRule(
        rule_id="r_novel",
        action_name="novel_act",
        effects={"x": 2},
        confidence=0.5,
        evidence_count=1,
        uncertainty=0.85,
    ))

    candidates = [("familiar_act", {}), ("novel_act", {})]
    best_act, unc = wm.active_experiment_recommendation({"x": 0}, candidates)

    assert best_act[0] == "novel_act"
    assert unc == 0.85
