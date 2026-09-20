"""
Suite 2: State Prediction Before Action Execution.
Validates:
- Prediction generated prior to executing physical action
- Prediction error computed accurately against true post-action state
- Predictor confidence calibration
"""

import pytest
from nirmal.agent.controller import CognitiveController, Goal, ControllerState
from nirmal.agent.world_model import WorldModel, CausalRule
from nirmal.tools import ToolRegistry, MockEnvironmentTool, StringUtilityTool, CalculatorTool


def test_predict_before_act_execution():
    wm = WorldModel()
    wm.register_rule(CausalRule(
        rule_id="rule_calc",
        action_name="calculator",
        preconditions={},
        effects={"output_step_1": 225.0},
        confidence=0.9,
    ))

    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(StringUtilityTool())

    controller = CognitiveController(tool_registry=tools, world_model=wm, enable_world_model=True)
    goal = Goal(
        goal_id="pred_test_1",
        description="Calculate 15 * 12 + 45",
        criteria=225.0,
    )

    result = controller.run(goal)
    assert result.success is True
    # Verify controller tracked prediction errors
    assert hasattr(result, "prediction_errors")
    assert len(result.prediction_errors) >= 1
    # Verify last prediction was generated
    assert controller.last_prediction is not None
    assert controller.last_prediction.confidence > 0.0


def test_prediction_error_calculation():
    wm = WorldModel()
    pred = wm.predict(
        current_state={"speed": 50, "gear": 3},
        action_name="accelerate",
    )
    # Since no rule is learned yet, predicted matches current state
    assert pred.predicted_state == {"speed": 50, "gear": 3}

    # Actual outcome after acceleration
    actual_state = {"speed": 70, "gear": 4}
    err = pred.evaluate_error(actual_state)
    # Both speed and gear differ -> error = 2/2 = 1.0
    assert err == 1.0
    assert pred.prediction_error == 1.0

    # Partial match
    partial_actual = {"speed": 50, "gear": 4}
    err_partial = pred.evaluate_error(partial_actual)
    assert err_partial == 0.5


def test_prediction_confidence_growth_with_evidence():
    wm = WorldModel()
    state_s = {"door": "closed"}
    state_s1 = {"door": "open"}
    action = "open_door"

    # Initially no rule exists
    pred_0 = wm.predict(state_s, action)
    initial_conf = pred_0.confidence

    # Observe 5 consistent transitions
    for i in range(5):
        wm.observe_transition(state_t=state_s, action_name=action, state_t1=state_s1, episode_id=f"ep_{i}")

    pred_after = wm.predict(state_s, action)
    assert pred_after.predicted_state.get("door") == "open"
    assert pred_after.confidence > initial_conf
    assert pred_after.uncertainty < pred_0.uncertainty
