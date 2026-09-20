"""
Transfer Learning V2 Evaluation Tasks & Dataset Partitioning.

Generates strictly partitioned datasets across deterministic seeds (1..5):
1. Experience Set: Training tasks for subskills X (Transformation), Y (Routing), Z (Checksumming), and Failure Traps.
2. Transfer Set: Novel instances with varied numeric parameters, object identifiers, ordering, distractor placement, and step counts.
3. Novel Composition Set: Unseen two-skill (X+Y) and three-skill (X+Y+Z) compound tasks.
4. Strict Holdout Set: Completely held-out evaluation configurations never seen in training.
"""

from dataclasses import dataclass, field
import random
from typing import Any, Dict, List, Optional, Tuple

from nirmal.agent.controller import Goal


@dataclass
class TransferTask:
    """A parameterized evaluation task instance for transfer learning benchmarking."""
    task_id: str
    task_family: str
    partition: str  # "experience", "transfer", "composition", "holdout"
    seed: int
    prompt: str
    expected_output: Any
    initial_env_state: Dict[str, Any] = field(default_factory=dict)
    subskills: List[str] = field(default_factory=list)  # ["X"], ["Y"], ["X", "Y"], etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_goal(self) -> Goal:
        return Goal(
            goal_id=self.task_id,
            description=self.prompt,
            criteria=self.expected_output,
            task_family=self.task_family,
            metadata={
                "partition": self.partition,
                "seed": self.seed,
                "subskills": self.subskills,
                **self.metadata,
            },
        )


# Pool of identifiers and word stems for procedural instance generation
WORD_STEMS = [
    "Adaptive", "Cybernetic", "Cognitive", "Distributed", "Epistemic",
    "Fractal", "Harmonic", "Inductive", "Kinetic", "Modular",
    "Neuromorphic", "Orthogonal", "Perceptual", "Quantum", "Resonant",
    "Stochastic", "Topological", "Universal", "Vortical", "Wavelet"
]


SERVICES = [
    "auth_service", "ingress_proxy", "telemetry_hub", "vault_router",
    "ledger_node", "stream_gateway", "compute_broker", "matrix_switch"
]


class TransferTaskGenerator:
    """Deterministic generator producing strictly non-overlapping task partitions."""

    def __init__(self, seed: int = 1):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_experience_set(self) -> List[TransferTask]:
        """Tasks the agent is allowed to solve and learn from during training."""
        tasks = []
        # Skill X: Text Transformation
        stem1 = WORD_STEMS[self.seed % len(WORD_STEMS)]
        tasks.append(
            TransferTask(
                task_id=f"exp_skill_x_s{self.seed}",
                task_family="skill_transformation",
                partition="experience",
                seed=self.seed,
                prompt=f"Transform text '{stem1}' with operation 'uppercase', then 'reverse'.",
                expected_output=stem1.upper()[::-1],
                subskills=["X"],
                metadata={"stem": stem1},
            )
        )

        # Skill Y: Environment Routing
        svc = SERVICES[self.seed % len(SERVICES)]
        node_id = f"node_{self.seed * 11}"
        port = f"{8000 + self.seed * 10}"
        tasks.append(
            TransferTask(
                task_id=f"exp_skill_y_s{self.seed}",
                task_family="skill_routing",
                partition="experience",
                seed=self.seed,
                prompt=f"Route service '{svc}' through discovered port and write active_route.",
                expected_output=f"{node_id}:{port}",
                initial_env_state={svc: node_id, f"{node_id}_port": port},
                subskills=["Y"],
                metadata={"service": svc, "node": node_id, "port": port},
            )
        )

        # Skill Z: Validation Checksum
        val_text = f"SESSION_{self.seed * 101}"
        tasks.append(
            TransferTask(
                task_id=f"exp_skill_z_s{self.seed}",
                task_family="skill_checksum",
                partition="experience",
                seed=self.seed,
                prompt=f"Validate payload '{val_text}' by computing length.",
                expected_output=len(val_text),
                subskills=["Z"],
                metadata={"payload": val_text},
            )
        )

        # Negative Learning Experience Task (Strategy fails under condition C: traffic=congested)
        tasks.append(
            TransferTask(
                task_id=f"exp_neg_s{self.seed}",
                task_family="skill_resilient_routing",
                partition="experience",
                seed=self.seed,
                prompt="Select verified route when network traffic is congested.",
                expected_output=f"stable_hub_{self.seed}:9000",
                initial_env_state={
                    "network_traffic": "congested",
                    "express_route": "failing_trap",
                    "resilient_route": f"stable_hub_{self.seed}",
                    f"stable_hub_{self.seed}_port": "9000",
                },
                subskills=["Y"],
                metadata={"condition": "congested"},
            )
        )

        return tasks

    def generate_transfer_set(self) -> List[TransferTask]:
        """Related tasks with varied parameters, identifiers, ordering, and distractors.
        
        Must NEVER share exact instances with the Experience set.
        """
        tasks = []
        # Instance novelty: Offset index by +7 to ensure distinct stems, ports, and services
        stem_tr = WORD_STEMS[(self.seed + 7) % len(WORD_STEMS)]
        target_char = "e"
        expected_count = stem_tr.lower().count(target_char)
        # Parameter variation & different ordering: lowercase then reverse then count
        tasks.append(
            TransferTask(
                task_id=f"trans_param_s{self.seed}",
                task_family="skill_transformation",
                partition="transfer",
                seed=self.seed,
                prompt=f"Transform text '{stem_tr}' with operation 'lowercase', then 'reverse', and count character '{target_char}'.",
                expected_output=expected_count,
                subskills=["X"],
                metadata={"stem": stem_tr, "char": target_char},
            )
        )

        # Environment routing with novel service identifier and distractor keys
        svc_tr = SERVICES[(self.seed + 5) % len(SERVICES)]
        node_tr = f"cluster_node_{self.seed * 37}"
        port_tr = f"{9200 + self.seed * 5}"
        tasks.append(
            TransferTask(
                task_id=f"trans_distract_s{self.seed}",
                task_family="skill_routing",
                partition="transfer",
                seed=self.seed,
                prompt=f"Route service '{svc_tr}' through discovered port and write active_route.",
                expected_output=f"{node_tr}:{port_tr}",
                initial_env_state={
                    svc_tr: node_tr,
                    f"{node_tr}_port": port_tr,
                    # Distractor entries
                    "dummy_deadend_svc": "offline_node",
                    "offline_node_port": "0000",
                },
                subskills=["Y"],
                metadata={"service": svc_tr, "node": node_tr, "port": port_tr},
            )
        )

        # Unseen Negative Learning Transfer Task (Condition: congested)
        # Verifies that agent generalizes negative constraint to novel identifiers
        novel_hub = f"hardened_node_{self.seed * 19}"
        novel_port = f"{7500 + self.seed}"
        tasks.append(
            TransferTask(
                task_id=f"trans_neg_s{self.seed}",
                task_family="skill_resilient_routing",
                partition="transfer",
                seed=self.seed,
                prompt="Select verified route when network traffic is congested.",
                expected_output=f"{novel_hub}:{novel_port}",
                initial_env_state={
                    "network_traffic": "congested",
                    "express_route": "unreachable_trap",
                    "resilient_route": novel_hub,
                    f"{novel_hub}_port": novel_port,
                },
                subskills=["Y"],
                metadata={"condition": "congested", "hub": novel_hub},
            )
        )

        return tasks

    def generate_composition_set(self) -> List[TransferTask]:
        """Previously unseen combinations of known subskills (X+Y and X+Y+Z)."""
        tasks = []
        # Two-Skill Composition: Skill X (Transform) + Skill Y (Routing)
        comp_stem = WORD_STEMS[(self.seed + 3) % len(WORD_STEMS)]
        comp_svc = f"svc_{comp_stem.lower()}"
        comp_node = f"node_{comp_stem.lower()}"
        comp_port = f"{5000 + self.seed}"

        tasks.append(
            TransferTask(
                task_id=f"comp_xy_s{self.seed}",
                task_family="composition_xy",
                partition="composition",
                seed=self.seed,
                prompt=f"Compose: transform key '{comp_stem}' with operation 'lowercase', resolve service endpoint, and write active_route.",
                expected_output=f"{comp_node}:{comp_port}",
                initial_env_state={
                    comp_svc: comp_node,
                    f"{comp_node}_port": comp_port,
                },
                subskills=["X", "Y"],
                metadata={"stem": comp_stem, "service": comp_svc},
            )
        )

        # Three-Skill Composition: Skill X (Transform) + Skill Y (Routing) + Skill Z (Checksum)
        tasks.append(
            TransferTask(
                task_id=f"comp_xyz_s{self.seed}",
                task_family="composition_xyz",
                partition="composition",
                seed=self.seed,
                prompt=f"Compose: transform key '{comp_stem}' with operation 'uppercase', route service, and compute endpoint length.",
                expected_output=len(f"{comp_node}:{comp_port}"),
                initial_env_state={
                    f"svc_{comp_stem.upper()}": comp_node,
                    f"{comp_node}_port": comp_port,
                },
                subskills=["X", "Y", "Z"],
                metadata={"stem": comp_stem},
            )
        )

        return tasks

    def generate_holdout_set(self) -> List[TransferTask]:
        """Strictly held-out evaluation tasks never used for tuning or intermediate debugging."""
        tasks = []
        # Held-out novel permutation with distractor insertion
        holdout_stem = f"ExoticVariant_{self.seed * 97}"
        target_char = "a"
        expected_cnt = holdout_stem.lower().count(target_char)
        tasks.append(
            TransferTask(
                task_id=f"holdout_s{self.seed}_1",
                task_family="skill_transformation",
                partition="holdout",
                seed=self.seed,
                prompt=f"Transform text '{holdout_stem}' with operation 'lowercase', then 'reverse', and count character '{target_char}'.",
                expected_output=expected_cnt,
                subskills=["X"],
                metadata={"stem": holdout_stem},
            )
        )

        # Held-out resilient route resolution under stress
        holdout_hub = f"isolated_gateway_{self.seed * 41}"
        holdout_port = f"{3000 + self.seed}"
        tasks.append(
            TransferTask(
                task_id=f"holdout_s{self.seed}_2",
                task_family="skill_resilient_routing",
                partition="holdout",
                seed=self.seed,
                prompt="Select verified route when network traffic is congested.",
                expected_output=f"{holdout_hub}:{holdout_port}",
                initial_env_state={
                    "network_traffic": "congested",
                    "express_route": "fatal_broken_path",
                    "resilient_route": holdout_hub,
                    f"{holdout_hub}_port": holdout_port,
                },
                subskills=["Y"],
                metadata={"condition": "congested"},
            )
        )

        return tasks


def get_task_suite_for_seed(seed: int) -> Dict[str, List[TransferTask]]:
    """Generate all partitioned task sets for a specific random seed."""
    gen = TransferTaskGenerator(seed=seed)
    return {
        "experience": gen.generate_experience_set(),
        "transfer": gen.generate_transfer_set(),
        "composition": gen.generate_composition_set(),
        "holdout": gen.generate_holdout_set(),
    }
