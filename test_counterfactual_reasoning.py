"""
Suite 3: Counterfactual Reasoning Without Environment Execution.
Validates:
- 'What would have happened if action A was taken instead of B?'
- Evaluates candidate branches purely within the learned world model.
- Accurately discriminates safer / optimal actions before commitment.
"""

import pytest
from nirmal.agent.world_model import WorldModel, CausalRule
from nirmal.agent.controller import CognitiveController, Goal
from nirmal.tools import ToolRegistry, MockEnvironmentTool, StringUtilityTool


def test_counterfactual_query_evaluation():
    wm = WorldModel()
    # Learned dynamics:
    # Action 'route_fast': delivers packet in 10ms, but loss_rate=0.4
    # Action 'route_safe': delivers packet in 50ms, loss_rate=0.0
    wm.register_rule(CausalRule(
        rule_id="r_fast",
        action_name="route_fast",
        effects={"latency": 10, "loss_rate": 0.4},
        confidence=0.9,
    ))
    wm.register_rule(CausalRule(
        rule_id="r_safe",
        action_name="route_safe",
        effects={"latency": 50, "loss_rate": 0.0},
        confidence=0.95,
    ))

    # Real world took 'route_fast' and packet was lost
    factual_state = {"packet_status": "pending", "latency": 0, "loss_rate": 0.0}
    factual_action = "route_fast"
    factual_outcome = {"packet_status": "lost", "latency": 10, "loss_rate": 0.4}

    # Counterfactual query: What if we had taken 'route_safe' instead?
    cf_pred = wm.counterfactual(
        factual_state=factual_state,
        factual_action=factual_action,
        counterfactual_action="route_safe",
        factual_outcome=factual_outcome,
    )

    assert cf_pred.predicted_state["loss_rate"] == 0.0
    assert cf_pred.predicted_state["latency"] == 50
    assert cf_pred.confidence == 0.95


def test_controller_counterfactual_decision_branching():
    tools = ToolRegistry()
    tools.register(MockEnvironmentTool())
    tools.register(StringUtilityTool())

    wm = WorldModel()
    # Action branch A causes failure
    wm.register_rule(CausalRule(
        rule_id="rule_branch_a",
        action_name="unsafe_path",
        effects={"status": "error"},
        confidence=0.9,
    ))
    # Action branch B succeeds
    wm.register_rule(CausalRule(
        rule_id="rule_branch_b",
        action_name="safe_path",
        effects={"status": "completed"},
        confidence=0.9,
    ))

    controller = CognitiveController(tool_registry=tools, world_model=wm, enable_world_model=True)

    # Agent checks candidate actions counterfactually
    state = {"status": "idle"}
    pred_unsafe = controller.simulate_action({"tool": "unsafe_path", "args": {}})
    pred_safe = controller.simulate_action({"tool": "safe_path", "args": {}})

    assert pred_unsafe.predicted_state.get("status") == "error"
    assert pred_safe.predicted_state.get("status") == "completed"

    # Counterfactual comparison chooses safe path
    chosen_action = "safe_path" if pred_safe.predicted_state.get("status") == "completed" else "unsafe_path"
    assert chosen_action == "safe_path"
