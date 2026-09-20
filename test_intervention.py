"""
Suite 5: Interventional Reasoning and Disambiguating Correlation from Causation.
Validates:
- Disambiguation of P(Y | X) vs P(Y | do(X))
- Confounder handling: latent variable U causes spurious correlation between X and Y
- Graph mutilation severing spurious incoming edges under active intervention
"""

import pytest
from evals.causal_simulator import CausalSimulator
from nirmal.agent.world_model import WorldModel, CausalGraph


def test_observational_correlation_vs_interventional_causation():
    """
    In the confounded simulator:
    U is latent. U -> X and U -> Y.
    Therefore, passively observing X=1 is correlated with Y=1.
    However, actively intervening do(X=1) does NOT cause Y=1, because X has no directed path to Y.
    True cause of Y is Z: do(Z=1) causes Y=1.
    """
    sim = CausalSimulator.create_confounded_system(seed=42)

    # 1. Passive observation: when U=1, X=1 and Y=1
    sim.state["U"] = 1
    obs_corr, _ = sim.step({"type": "observe"})
    assert obs_corr["X"] == 1
    assert obs_corr["Y"] == 1  # Correlated!

    # 2. Reset simulator to baseline (U=0, X=0, Y=0, Z=0)
    sim.reset({"U": 0, "X": 0, "Y": 0, "Z": 0})
    obs_baseline = sim.get_observable_state()
    assert obs_baseline["X"] == 0
    assert obs_baseline["Y"] == 0

    # 3. Intervene on X: do(X=1). Since X does NOT cause Y, Y must remain 0!
    obs_intervene_x, info_x = sim.step({"type": "do", "target": "X", "value": 1})
    assert obs_intervene_x["X"] == 1
    assert obs_intervene_x["Y"] == 0, "Intervention on X erroneously affected Y! Confounder not severed."

    # 4. Intervene on Z: do(Z=1). Z is a true cause of Y, so Y must become 1!
    obs_intervene_z, info_z = sim.step({"type": "do", "target": "Z", "value": 1})
    assert obs_intervene_z["Z"] == 1
    assert obs_intervene_z["Y"] == 1, "Intervention on true cause Z failed to activate Y."


def test_world_model_causal_flag_attribution():
    wm = WorldModel()

    # Transition 1: passive observation without intervention
    wm.observe_transition(
        state_t={"X": 0, "Y": 0},
        action_name="observe_env",
        state_t1={"X": 1, "Y": 1},
        is_intervention=False,
    )
    rule_obs = list(wm.rules.values())[0]
    assert rule_obs.is_causal is False
    assert rule_obs.observational_count == 1
    assert rule_obs.interventional_count == 0

    # Transition 2: active intervention do(X=1) produces no effect on Y
    wm.observe_transition(
        state_t={"X": 0, "Y": 0},
        action_name="do_X",
        state_t1={"X": 1, "Y": 0},
        is_intervention=True,
    )
    rule_intervene = [r for r in wm.rules.values() if r.action_name == "do_X"][0]
    assert rule_intervene.is_causal is True
    assert rule_intervene.interventional_count == 1
    assert "Y" not in rule_intervene.effects
