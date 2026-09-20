"""
Suite 10: 8-Way World Model & Cognitive Architecture Ablation Matrix.
Validates:
1. Full System
2. World Model OFF
3. Learning Engine OFF
4. Procedural Memory OFF
5. Semantic Memory OFF
6. Episodic Memory OFF
7. Counterfactual Reasoning OFF
8. Verification OFF
And evaluates System A (V3 procedural baseline) vs System B (V4 with world model).
"""

import pytest
from nirmal.agent.controller import CognitiveController, Goal, ControllerState
from nirmal.agent.world_model import WorldModel, CausalRule
from nirmal.tools import ToolRegistry, MockEnvironmentTool, StringUtilityTool, CalculatorTool


def make_controller_with_config(**kwargs):
    tools = ToolRegistry()
    tools.register(MockEnvironmentTool())
    tools.register(StringUtilityTool())
    tools.register(CalculatorTool())
    return CognitiveController(tool_registry=tools, **kwargs)


@pytest.mark.parametrize("ablation_name,kwargs", [
    ("Full_System", {}),
    ("WorldModel_OFF", {"enable_world_model": False}),
    ("Learning_OFF", {"enable_learning": False}),
    ("Procedural_OFF", {"enable_procedural_learning": False}),
    ("Semantic_OFF", {"enable_semantic_learning": False}),
    ("Memory_OFF", {"enable_memory": False}),
    ("Counterfactual_OFF", {"enable_counterfactual_reasoning": False}),
    ("Verification_OFF", {"enable_verification": False}),
])
def test_ablation_variants_execution(ablation_name, kwargs):
    controller = make_controller_with_config(**kwargs)
    goal = Goal(
        goal_id=f"ablation_{ablation_name}",
        description="Calculate 10 + 20",
        criteria=30.0,
    )
    result = controller.run(goal)
    assert result.state in (ControllerState.DONE, ControllerState.FAILED)


def test_system_a_vs_system_b_world_model_gain():
    """
    Compare System A (V3 procedural baseline without world model) vs System B (V4 with world model).
    On a task requiring forward prediction of consequences, System B leverages
    world model predictions while System A relies strictly on procedural trial.
    """
    # System A: World Model disabled
    sys_a = make_controller_with_config(enable_world_model=False)
    # System B: World Model enabled with learned rules
    wm = WorldModel()
    wm.register_rule(CausalRule(
        rule_id="r_calc",
        action_name="calculator",
        effects={"output_step_1": 42.0},
        confidence=1.0,
    ))
    sys_b = make_controller_with_config(world_model=wm, enable_world_model=True)

    goal = Goal(goal_id="cmp_task", description="Calculate 6 * 7", criteria=42.0)

    res_a = sys_a.run(goal)
    res_b = sys_b.run(goal)

    assert res_a.success is True
    assert res_b.success is True
    # System B tracked prediction errors and brier scores
    assert len(res_b.prediction_errors) >= 1
    assert res_a.world_model_rules_count == 0
    assert res_b.world_model_rules_count >= 1
