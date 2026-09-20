"""
Causal Simulator for Nirmal-1 V4 World Model & General Reasoning Evaluations.
Provides a procedural Causal DAG environment with:
- True causal directed relations
- Spurious correlations / confounding (latent variable U -> A, U -> B)
- Pearl's do-calculus interventions: do(X=v) breaking incoming edges
- Multi-step causal chains across horizons (1, 2, 4, 8, 16)
- Unexpected side effects
- Multi-environment distribution shifts (Env A -> Env B -> Env C)
"""

from dataclasses import dataclass, field
import random
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


@dataclass
class CausalNode:
    """Represents a variable in the causal simulator."""
    name: str
    default_value: Any = 0
    domain: List[Any] = field(default_factory=lambda: [0, 1])
    is_latent: bool = False


@dataclass
class CausalMechanism:
    """Structural equation or transition mechanism for node given parent values."""
    target: str
    parents: List[str]
    func: Callable[[Dict[str, Any]], Any]
    side_effects: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


class CausalSimulator:
    """
    Procedural Causal Environment simulator.
    Maintains ground-truth causal DAG and evaluates state transitions under
    observational conditioning vs. interventional do(X) actions.
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.nodes: Dict[str, CausalNode] = {}
        self.mechanisms: Dict[str, CausalMechanism] = {}
        self.state: Dict[str, Any] = {}
        self.step_history: List[Dict[str, Any]] = []
        self.interventions_active: Dict[str, Any] = {}

    def add_node(self, name: str, default_value: Any = 0, domain: Optional[List[Any]] = None, is_latent: bool = False) -> None:
        self.nodes[name] = CausalNode(
            name=name,
            default_value=default_value,
            domain=domain or [0, 1],
            is_latent=is_latent,
        )
        self.state[name] = default_value

    def add_mechanism(
        self,
        target: str,
        parents: List[str],
        func: Callable[[Dict[str, Any]], Any],
        side_effects: Optional[Dict[str, Any]] = None,
        description: str = "",
    ) -> None:
        self.mechanisms[target] = CausalMechanism(
            target=target,
            parents=parents,
            func=func,
            side_effects=side_effects or {},
            description=description,
        )

    def reset(self, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reset environment to initial state."""
        self.interventions_active.clear()
        self.step_history.clear()
        self.state.clear()
        for name, node in self.nodes.items():
            self.state[name] = node.default_value
        if initial_state:
            for k, v in initial_state.items():
                if k in self.nodes:
                    self.state[k] = v
        return self.get_observable_state()

    def get_observable_state(self) -> Dict[str, Any]:
        """Return state of non-latent variables."""
        return {k: v for k, v in self.state.items() if not self.nodes[k].is_latent}

    def get_full_state(self) -> Dict[str, Any]:
        """Return state including latent variables."""
        return dict(self.state)

    def step(self, action: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Execute one transition step.
        If action is an intervention 'do(var, val)', incoming edges to 'var' are severed.
        Returns: (observable_state, step_info)
        """
        pre_state = dict(self.state)
        applied_interventions: Dict[str, Any] = {}

        if action:
            act_type = action.get("type", "set")
            var = action.get("target") or action.get("variable")
            val = action.get("value", 1)

            if act_type in ("do", "intervene") and var in self.nodes:
                applied_interventions[var] = val
                self.state[var] = val
            elif act_type == "observe":
                # Passive observation: do nothing to force variables
                pass
            elif var in self.nodes:
                applied_interventions[var] = val
                self.state[var] = val

        # Forward evaluate structural equations for non-intervened nodes in topological order
        # Nodes with no mechanisms remain unchanged unless intervened
        updated_state = dict(self.state)
        side_effects_triggered = {}

        for target, mech in self.mechanisms.items():
            if target in applied_interventions:
                # Intervened: structural equation severed
                continue
            parent_vals = {p: self.state.get(p, self.nodes[p].default_value if p in self.nodes else 0) for p in mech.parents}
            new_val = mech.func(parent_vals)
            updated_state[target] = new_val

            # Check if side-effects trigger
            if mech.side_effects:
                for se_var, se_val in mech.side_effects.items():
                    if se_var not in applied_interventions:
                        updated_state[se_var] = se_val
                        side_effects_triggered[se_var] = se_val

        self.state = updated_state
        step_info = {
            "pre_state": pre_state,
            "action": action,
            "interventions": applied_interventions,
            "side_effects": side_effects_triggered,
            "post_state": dict(self.state),
        }
        self.step_history.append(step_info)
        return self.get_observable_state(), step_info

    @classmethod
    def create_confounded_system(cls, seed: int = 42) -> "CausalSimulator":
        """
        Constructs a system with confounder U:
        U -> X and U -> Y (spurious correlation)
        X does NOT cause Y.
        Z is an independent cause: Z -> Y.
        Under P(Y|X=1), Y is correlated with X due to U.
        Under do(X=1), Y does NOT change.
        """
        sim = cls(seed=seed)
        sim.add_node("U", default_value=0, is_latent=True)
        sim.add_node("X", default_value=0)
        sim.add_node("Y", default_value=0)
        sim.add_node("Z", default_value=0)

        # Mechanism for X from U
        sim.add_mechanism("X", ["U"], lambda p: p["U"], description="X depends on latent U")
        # Mechanism for Y from U and Z (not X!)
        sim.add_mechanism("Y", ["U", "Z"], lambda p: 1 if (p["U"] == 1 or p["Z"] == 1) else 0, description="Y depends on U and Z")

        return sim

    @classmethod
    def create_linear_chain(cls, length: int = 4, seed: int = 42) -> "CausalSimulator":
        """
        Constructs a causal chain of length N:
        N0 -> N1 -> N2 -> ... -> N_{length-1}
        Each node Ni activates when Ni-1 is active.
        """
        sim = cls(seed=seed)
        sim.add_node("N0", default_value=0)
        for i in range(1, length):
            sim.add_node(f"N{i}", default_value=0)
            parent = f"N{i-1}"
            sim.add_mechanism(f"N{i}", [parent], lambda p, p_name=parent: p[p_name], description=f"{parent} -> N{i}")
        return sim

    @classmethod
    def create_branching_system(cls, seed: int = 42) -> "CausalSimulator":
        """
        Constructs a branching DAG with side-effects:
        Action on A activates B and C.
        B activates D.
        C activates E with side-effect: alarm=1 if E is activated without bypass.
        """
        sim = cls(seed=seed)
        sim.add_node("A", default_value=0)
        sim.add_node("B", default_value=0)
        sim.add_node("C", default_value=0)
        sim.add_node("D", default_value=0)
        sim.add_node("E", default_value=0)
        sim.add_node("alarm", default_value=0)

        sim.add_mechanism("B", ["A"], lambda p: p["A"], description="A -> B")
        sim.add_mechanism("C", ["A"], lambda p: p["A"], description="A -> C")
        sim.add_mechanism("D", ["B"], lambda p: p["B"], description="B -> D")
        sim.add_mechanism(
            "E",
            ["C"],
            lambda p: p["C"],
            side_effects={"alarm": 1},
            description="C -> E triggers alarm side-effect",
        )
        return sim

    @classmethod
    def create_distribution_shift_family(cls, seed: int = 42) -> Tuple["CausalSimulator", "CausalSimulator", "CausalSimulator"]:
        """
        Creates three environments: Env_A, Env_B, Env_C.
        - Env_A: base causal dynamics (rule 1, rule 2, rule 3)
        - Env_B: rule 1 & 2 invariant, rule 3 inverted, new rule 4 added
        - Env_C: rule 1 invariant, rule 2 modified, rule 4 invariant, new rule 5 added
        """
        # Env A
        env_a = cls(seed=seed)
        for v in ["v1", "v2", "v3", "out1"]:
            env_a.add_node(v, default_value=0)
        env_a.add_mechanism("v2", ["v1"], lambda p: p["v1"], description="v1 -> v2")
        env_a.add_mechanism("v3", ["v2"], lambda p: p["v2"], description="v2 -> v3")
        env_a.add_mechanism("out1", ["v3"], lambda p: 1 if p["v3"] == 1 else 0, description="v3 -> out1")

        # Env B
        env_b = cls(seed=seed + 1)
        for v in ["v1", "v2", "v3", "v4", "out1"]:
            env_b.add_node(v, default_value=0)
        env_b.add_mechanism("v2", ["v1"], lambda p: p["v1"], description="v1 -> v2 (invariant)")
        env_b.add_mechanism("v3", ["v2"], lambda p: p["v2"], description="v2 -> v3 (invariant)")
        env_b.add_mechanism("v4", ["v2"], lambda p: 1 if p["v2"] == 1 else 0, description="v2 -> v4 (new)")
        # Inverted out1: out1 = 1 if v3 == 0
        env_b.add_mechanism("out1", ["v3"], lambda p: 1 if p["v3"] == 0 else 0, description="v3 -> out1 (shifted)")

        # Env C
        env_c = cls(seed=seed + 2)
        for v in ["v1", "v2", "v3", "v4", "v5", "out1"]:
            env_c.add_node(v, default_value=0)
        env_c.add_mechanism("v2", ["v1"], lambda p: p["v1"], description="v1 -> v2 (invariant)")
        # v3 now requires v4 as well
        env_c.add_mechanism("v3", ["v2", "v4"], lambda p: 1 if (p["v2"] == 1 and p["v4"] == 1) else 0, description="v2,v4 -> v3 (shifted)")
        env_c.add_mechanism("v4", ["v1"], lambda p: p["v1"], description="v1 -> v4 (new mechanism)")
        env_c.add_mechanism("v5", ["v3"], lambda p: p["v3"], description="v3 -> v5 (new)")
        env_c.add_mechanism("out1", ["v5"], lambda p: p["v5"], description="v5 -> out1 (new target)")

        return env_a, env_b, env_c
