"""
Novel Evaluation Task Families for Nirmal-1 Cognitive Learning V1.

Provides parameterized task generators across 3 novel task families:
1. EncodingPipelineFamily: Dynamic tool composition with parameter extraction and chaining.
2. ResourceDiscoveryFamily: Multi-step environment state tracking and verification.
3. DistractorRecoveryFamily: Novel task with distractors / failure modes requiring replanning and learning.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import hashlib

from nirmal.agent.controller import Goal


@dataclass
class NovelTaskInstance:
    """A parameterized instance of a novel evaluation task."""
    task_id: str
    task_family: str
    variation_id: str
    prompt: str
    expected_output: Any
    initial_env_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_goal(self) -> Goal:
        return Goal(
            goal_id=self.task_id,
            description=self.prompt,
            criteria=self.expected_output,
            task_family=self.task_family,
            metadata={"variation_id": self.variation_id, **self.metadata},
        )


class EncodingPipelineFamily:
    """Family 1: Parameter extraction and multi-stage tool composition.
    
    Transforms text through sequential operations and verifies checksum/count.
    """
    family_name = "encoding_pipeline"

    @classmethod
    def generate_tasks(cls) -> List[NovelTaskInstance]:
        tasks = []
        variations = [
            ("alpha", "CognitiveArchitecture", "uppercase", "reverse", "length", 21),
            ("beta", "AutonomousReasoningAgent", "lowercase", "reverse", "count_a", 3),
            ("gamma", "NeuralDeltaNetHybrid", "uppercase", "reverse", "length", 20),
            ("delta", "SelfImprovingSystem", "lowercase", "reverse", "count_s", 3),
            ("epsilon", "EmpiricalVerification", "uppercase", "reverse", "length", 21),
        ]

        for var_id, text, op1, op2, metric, expected in variations:
            if metric == "length":
                prompt = f"Transform text '{text}' with operation '{op1}', then '{op2}', and compute length."
            else:
                target_char = metric.split("_")[1]
                prompt = f"Transform text '{text}' with operation '{op1}', then '{op2}', and count character '{target_char}'."

            tasks.append(
                NovelTaskInstance(
                    task_id=f"enc_{var_id}",
                    task_family=cls.family_name,
                    variation_id=var_id,
                    prompt=prompt,
                    expected_output=expected,
                    metadata={"text": text, "op1": op1, "op2": op2, "metric": metric},
                )
            )
        return tasks


class ResourceDiscoveryFamily:
    """Family 2: Multi-step environment state inspection, route resolution, and state persistence.
    
    Requires inspecting config keys, resolving target port/node, and persisting active session.
    """
    family_name = "resource_discovery"

    @classmethod
    def generate_tasks(cls) -> List[NovelTaskInstance]:
        tasks = []
        configs = [
            ("cluster_east", {"service_east": "node_7", "node_7_port": "8080"}, "service_east", "node_7:8080"),
            ("cluster_west", {"service_west": "node_3", "node_3_port": "9090"}, "service_west", "node_3:9090"),
            ("cluster_north", {"service_north": "node_9", "node_9_port": "4430"}, "service_north", "node_9:4430"),
            ("cluster_south", {"service_south": "node_2", "node_2_port": "7070"}, "service_south", "node_2:7070"),
        ]

        for cluster_id, env_state, target_service, expected_endpoint in configs:
            prompt = f"Inspect cluster '{cluster_id}' to discover endpoint for '{target_service}' and write active_session."
            tasks.append(
                NovelTaskInstance(
                    task_id=f"res_{cluster_id}",
                    task_family=cls.family_name,
                    variation_id=cluster_id,
                    prompt=prompt,
                    expected_output=expected_endpoint,
                    initial_env_state=env_state,
                    metadata={"service": target_service, "cluster": cluster_id},
                )
            )
        return tasks


class DistractorRecoveryFamily:
    """Family 3: Novel task with distractors / failure modes requiring replanning and learning.
    
    Includes a primary path that hits a simulated roadblock/failure and requires fallback to a verified backup path.
    """
    family_name = "distractor_recovery"

    @classmethod
    def generate_tasks(cls) -> List[NovelTaskInstance]:
        tasks = []
        scenarios = [
            (
                "route_a",
                {"primary_gateway": "failing_gw", "backup_gateway": "active_gw_1", "active_gw_1_status": "ONLINE_READY"},
                "Connect to verified gateway and fetch status",
                "ONLINE_READY",
            ),
            (
                "route_b",
                {"primary_gateway": "failing_gw", "backup_gateway": "active_gw_2", "active_gw_2_status": "STANDBY_READY"},
                "Connect to verified gateway and fetch status",
                "STANDBY_READY",
            ),
            (
                "route_c",
                {"primary_gateway": "failing_gw", "backup_gateway": "active_gw_3", "active_gw_3_status": "SECURE_ACK"},
                "Connect to verified gateway and fetch status",
                "SECURE_ACK",
            ),
        ]

        for scenario_id, env_state, prompt, expected in scenarios:
            tasks.append(
                NovelTaskInstance(
                    task_id=f"dist_{scenario_id}",
                    task_family=cls.family_name,
                    variation_id=scenario_id,
                    prompt=f"{prompt} for {scenario_id}",
                    expected_output=expected,
                    initial_env_state=env_state,
                    metadata={"scenario": scenario_id},
                )
            )
        return tasks


def get_all_novel_tasks() -> List[NovelTaskInstance]:
    """Retrieve all novel task instances across all three families."""
    all_tasks = []
    all_tasks.extend(EncodingPipelineFamily.generate_tasks())
    all_tasks.extend(ResourceDiscoveryFamily.generate_tasks())
    all_tasks.extend(DistractorRecoveryFamily.generate_tasks())
    return all_tasks
