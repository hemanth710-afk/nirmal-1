"""
Tests for OpenWorldEnvironment:
- Latent condition transitions
- Action cost and risk tracking
- Partial observability masking
- Ground-truth state verification decoupled from action strings
"""

import pytest
from evals.open_world import OpenWorldEnvironment, OpenWorldTool
from nirmal.tools import ToolRegistry


def test_open_world_initialization_and_masking():
    env = OpenWorldEnvironment(seed=42)
    obs = env.observe()

    # Public observation should NOT expose masked latent variables directly
    assert "latent_condition" not in obs
    assert "auth_token" not in obs
    assert "status" in obs
    assert obs["status"] == "ready"
    assert "cumulative_cost" in obs
    assert obs["cumulative_cost"] == 0.0


def test_open_world_probe_unmasks_latent_condition():
    env = OpenWorldEnvironment(seed=42)
    env.state["latent_condition"] = "secure"

    # Direct observe still masks it
    obs = env.observe()
    assert "latent_condition" not in obs

    # Probing the environment unmasks latent condition
    res = env.act("probe", target="latent_condition")
    assert res.success is True
    assert res.output["latent_condition"] == "secure"


def test_open_world_action_costs_and_congestion():
    env = OpenWorldEnvironment(seed=42)
    res1 = env.act("verify_channel")
    assert res1.success is True
    cost1 = env.cumulative_cost
    assert cost1 > 0.0

    # Congested condition multiplies costs
    env.state["latent_condition"] = "congested"
    env.state["congestion_level"] = 2.5
    cost_before = env.cumulative_cost
    res2 = env.act("verify_channel")
    assert res2.success is True
    cost_step2 = env.cumulative_cost - cost_before
    assert cost_step2 == pytest.approx(cost1 * 2.5)


def test_open_world_latent_rule_enforcement():
    env = OpenWorldEnvironment(seed=42)
    env.state["latent_condition"] = "secure"
    env.act("route_direct")

    # Attempting to write data without acquiring token under secure condition must fail
    res_fail = env.act("write_data", key="k1", value="v1")
    assert res_fail.success is False
    assert "auth_token before write" in res_fail.error

    # Acquire token then write
    res_token = env.act("acquire_token")
    assert res_token.success is True
    res_write = env.act("write_data", key="k1", value="v1")
    assert res_write.success is True
    assert res_write.output["written"] is True


def test_open_world_ground_truth_verification():
    env = OpenWorldEnvironment(seed=42)
    env.state["latent_condition"] = "stable"
    env.act("route_direct")
    env.act("write_data", key="config_a", value="prod")
    env.act("commit_batch", batch_size=25)

    # Decoupled state verification checks actual internal world state
    assert env.verify_state({"data_store": {"config_a": "prod"}, "phase": "committed"}) is True
    assert env.verify_state({"processed_items": 25}) is True
    assert env.verify_state({"data_store": {"config_a": "staging"}}) is False


def test_open_world_tool_registry_integration():
    registry = ToolRegistry()
    env = OpenWorldEnvironment(seed=123)
    tool = OpenWorldTool(env=env)
    registry.register(tool)

    assert "open_world_env" in registry.list_tools()
    res = registry.execute("open_world_env", {"action": "route_direct"})
    assert res.success is True
    assert env.state["active_route"] == "direct"
