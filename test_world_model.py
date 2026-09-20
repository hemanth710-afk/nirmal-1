"""
Suite 1: World Model Representation, Rule Updates, and Causal Graph Structures.
Validates:
- Entity and relationship graph semantics
- CausalRule Bayesian Laplace smoothing
- CausalGraph DAG traversal, ancestor/descendant sets, and Pearl mutilation
- Serialization / deserialization
"""

import pytest
from nirmal.agent.world_model import (
    Entity,
    Relationship,
    CausalRule,
    CausalGraph,
    WorldModel,
    StatePrediction,
)


def test_entity_and_relationship_management():
    wm = WorldModel()
    valve = Entity(name="valve_1", entity_type="actuator", properties={"state": "closed", "flow_rate": 0})
    tank = Entity(name="tank_1", entity_type="container", properties={"level": 50, "max_capacity": 100})
    wm.add_entity(valve)
    wm.add_entity(tank)

    assert "valve_1" in wm.entities
    assert "tank_1" in wm.entities
    assert wm.entities["valve_1"].properties["state"] == "closed"

    rel = Relationship(source="valve_1", target="tank_1", relation_type="controls_inflow", confidence=0.95)
    wm.add_relationship(rel)
    assert len(wm.relationships) == 1
    assert wm.relationships[0].relation_type == "controls_inflow"


def test_causal_rule_bayesian_confidence_updates():
    rule = CausalRule(
        rule_id="rule_pump_pressure",
        action_name="activate_pump",
        preconditions={"pump_status": "off"},
        effects={"pump_status": "on", "pressure": 100},
    )

    # Initial Laplace smoothed prior: (0 + 1) / (0 + 0 + 2) = 0.5
    assert rule.confidence == 0.5
    assert rule.evidence_count == 0

    # 3 supporting transitions
    rule.update_evidence(supported=True, episode_id="ep_1")
    assert rule.confidence == pytest.approx((1 + 1) / (1 + 0 + 2), abs=1e-3)  # 2/3 = 0.6667

    rule.update_evidence(supported=True, episode_id="ep_2")
    assert rule.confidence == pytest.approx((2 + 1) / (2 + 0 + 2), abs=1e-3)  # 3/4 = 0.75

    rule.update_evidence(supported=True, episode_id="ep_3")
    assert rule.confidence == pytest.approx((3 + 1) / (3 + 0 + 2), abs=1e-3)  # 4/5 = 0.80

    # 1 contradicting transition
    rule.update_evidence(supported=False, episode_id="ep_4")
    assert rule.confidence == pytest.approx((3 + 1) / (3 + 1 + 2), abs=1e-3)  # 4/6 = 0.6667
    assert len(rule.contradicting_episodes) == 1
    assert rule.evidence_count == 4


def test_causal_graph_traversal_and_pearl_mutilation():
    graph = CausalGraph()
    # Build DAG: A -> B -> C -> D, and X -> C
    graph.add_edge("A", "B", confidence=1.0)
    graph.add_edge("B", "C", confidence=1.0)
    graph.add_edge("C", "D", confidence=1.0)
    graph.add_edge("X", "C", confidence=1.0)

    assert graph.get_parents("C") == {"B", "X"}
    assert graph.get_children("B") == {"C"}
    assert graph.get_ancestors("D") == {"A", "B", "C", "X"}
    assert graph.get_descendants("A") == {"B", "C", "D"}

    paths_a_to_d = graph.find_paths("A", "D")
    assert paths_a_to_d == [["A", "B", "C", "D"]]

    # Pearl's do-operator on C: do(C=c) severs all incoming arrows to C (B->C and X->C are severed)
    mutilated = graph.apply_intervention("C")
    assert mutilated.get_parents("C") == set()
    assert mutilated.get_children("C") == {"D"}
    assert mutilated.get_children("B") == set()  # B no longer connects to C
    assert mutilated.get_ancestors("D") == {"C"}  # A, B, X are disconnected from D


def test_world_model_serialization():
    wm = WorldModel()
    rule = CausalRule(
        rule_id="r1",
        action_name="heat",
        preconditions={"temp": 20},
        effects={"temp": 100},
        side_effects={"steam": True},
        confidence=0.85,
    )
    wm.register_rule(rule)
    data = wm.to_dict()

    wm2 = WorldModel.from_dict(data)
    assert "r1" in wm2.rules
    assert wm2.rules["r1"].action_name == "heat"
    assert wm2.rules["r1"].effects["temp"] == 100
    assert wm2.rules["r1"].side_effects["steam"] is True
    assert wm2.rules["r1"].confidence == 0.85
