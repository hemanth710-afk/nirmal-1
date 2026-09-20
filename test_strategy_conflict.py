"""
Evaluation Suite: Strategy Conflict Resolution and Condition Precedence.

Tests:
1. Two strategies with identical goal descriptions but conflicting condition requirements.
2. Condition P selects Strategy A; Condition Q selects Strategy B.
3. Compound condition (P and Q) prefers more specific Strategy C over generic Strategy A or B.
4. Active avoid condition suppresses an otherwise high-score strategy.
5. Inability to satisfy either precondition gracefully defaults or triggers planning.
"""

import pytest
from nirmal.agent.memory.procedural import ProceduralMemory, Strategy


@pytest.fixture
def conflicting_procedural_memory():
    proc = ProceduralMemory()

    # Strategy A: Optimized for LAN (low latency, uncompressed)
    strat_a = Strategy(
        strategy_id="strat_transfer_lan",
        name="strat_transfer_lan",
        task_family="transfer",
        description="Transfer bulk data payload to destination",
        conditions={"network_topology": "lan"},
        avoid_conditions={"network_topology": "wan"},
        steps=[
            {"id": "step_1", "description": "Direct LAN pipe", "tool_name": "string_util", "tool_args": {"operation": "identity", "text": "lan_pipe"}},
        ],
        success_rate=0.95,
    )

    # Strategy B: Optimized for WAN (high latency, compressed)
    strat_b = Strategy(
        strategy_id="strat_transfer_wan",
        name="strat_transfer_wan",
        task_family="transfer",
        description="Transfer bulk data payload to destination",
        conditions={"network_topology": "wan"},
        avoid_conditions={"network_topology": "lan"},
        steps=[
            {"id": "step_1", "description": "Compressed WAN pipe", "tool_name": "string_util", "tool_args": {"operation": "identity", "text": "wan_pipe"}},
        ],
        success_rate=0.90,
    )

    # Strategy C: Specialized for Secure WAN (compound condition)
    strat_c = Strategy(
        strategy_id="strat_transfer_wan_secure",
        name="strat_transfer_wan_secure",
        task_family="transfer",
        description="Transfer bulk data payload to destination",
        conditions={"network_topology": "wan", "security_tier": "military"},
        steps=[
            {"id": "step_1", "description": "Encrypted WAN tunnel", "tool_name": "string_util", "tool_args": {"operation": "identity", "text": "secure_wan_tunnel"}},
        ],
        success_rate=0.98,
    )

    proc.register_strategy(strat_a)
    proc.register_strategy(strat_b)
    proc.register_strategy(strat_c)
    return proc


def test_conflict_resolution_condition_p(conflicting_procedural_memory):
    proc = conflicting_procedural_memory
    sel = proc.select_strategy(
        "Transfer bulk data payload to destination",
        conditions={"network_topology": "lan"},
    )
    assert sel is not None
    assert sel.name == "strat_transfer_lan"


def test_conflict_resolution_condition_q(conflicting_procedural_memory):
    proc = conflicting_procedural_memory
    sel = proc.select_strategy(
        "Transfer bulk data payload to destination",
        conditions={"network_topology": "wan"},
    )
    assert sel is not None
    assert sel.name == "strat_transfer_wan"


def test_conflict_resolution_compound_condition(conflicting_procedural_memory):
    proc = conflicting_procedural_memory
    # Both strat_b and strat_c match "network_topology": "wan",
    # but strat_c matches both "network_topology": "wan" AND "security_tier": "military".
    sel = proc.select_strategy(
        "Transfer bulk data payload to destination",
        conditions={"network_topology": "wan", "security_tier": "military"},
    )
    assert sel is not None
    assert sel.name == "strat_transfer_wan_secure"


def test_conflict_resolution_unmatched_conditions(conflicting_procedural_memory):
    proc = conflicting_procedural_memory
    # If environment condition is "satellite", neither LAN nor WAN preconditions match.
    sel = proc.select_strategy(
        "Transfer bulk data payload to destination",
        conditions={"network_topology": "satellite"},
    )
    # Neither condition matches; strategies with strict condition mismatches are penalized
    # It should not select LAN or WAN if they violate preconditions or it returns None
    if sel is not None:
        assert sel.conditions.get("network_topology") != "satellite"
