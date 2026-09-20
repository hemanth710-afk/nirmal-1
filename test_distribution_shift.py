"""
Suite 8: Distribution Shift Adaptation Across Partially Overlapping Environments.
Validates:
- Shift sequence: Env A -> Env B -> Env C
- Invariant causal core retention without catastrophic forgetting
- Outdated / shifted dynamics adaptation
"""

import pytest
from evals.causal_simulator import CausalSimulator
from nirmal.agent.world_model import WorldModel, CausalRule


def test_three_environment_distribution_shift():
    env_a, env_b, env_c = CausalSimulator.create_distribution_shift_family(seed=100)
    wm = WorldModel()

    # --- Environment A Training ---
    wm.environment_id = "env_a"
    # Learn invariant rule 1 (v1 -> v2)
    wm.register_rule(CausalRule(
        rule_id="rule_v1_to_v2",
        action_name="step_v1",
        preconditions={"v1": 1},
        effects={"v2": 1},
        confidence=0.9,
    ))
    # Learn shifted rule (v3 -> out1 = 1)
    wm.register_rule(CausalRule(
        rule_id="rule_v3_to_out1",
        action_name="step_v3",
        preconditions={"v3": 1},
        effects={"out1": 1},
        confidence=0.9,
    ))

    assert len(wm.rules) == 2

    # --- Shift to Environment B ---
    report_b = wm.adapt_to_distribution_shift("env_b")
    assert report_b["new_environment_id"] == "env_b"
    assert report_b["retained_rules_count"] == 2

    # In Env B, v3 -> out1 is shifted: out1 becomes 0 when v3=1
    # Observe transition in Env B
    wm.observe_transition(
        state_t={"v3": 1, "out1": 0},
        action_name="step_v3",
        state_t1={"v3": 1, "out1": 0},
    )

    # Invariant rule v1 -> v2 remains high confidence
    rule_inv = wm.get_rule("rule_v1_to_v2")
    assert rule_inv.confidence == 0.9

    # Shifted rule v3 -> out1 confidence decays or is contradicted
    rule_shifted = wm.get_rule("rule_v3_to_out1")
    assert rule_shifted.confidence < 0.9

    # --- Shift to Environment C ---
    report_c = wm.adapt_to_distribution_shift("env_c")
    assert report_c["new_environment_id"] == "env_c"
    assert "rule_v1_to_v2" in wm.rules
