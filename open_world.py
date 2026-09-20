"""
Open-World Simulation Environment for Nirmal-1 V3 Evaluations.

Features:
- Dynamic latent conditions: "stable", "congested", "secure", "degraded".
- Partial observability: certain state variables are masked unless explicitly probed.
- Action costs & risk levels: latency, energy, and risk tracking.
- Latent transition rules and counterfactual condition dependencies.
- Ground-truth state verification decoupled from superficial action outputs.
"""

from dataclasses import dataclass, field
import random
import time
from typing import Any, Dict, List, Optional, Set

from nirmal.tools import Tool, ToolResult


@dataclass
class ActionCost:
    latency_ms: float
    energy_units: float
    risk_score: float

    @property
    def total_cost(self) -> float:
        return self.latency_ms + (self.energy_units * 2.0) + (self.risk_score * 10.0)


class OpenWorldEnvironment:
    """Simulated dynamic open-world environment with latent rules and partial observability."""

    BASE_COSTS = {
        "probe": ActionCost(10.0, 1.0, 0.0),
        "observe": ActionCost(5.0, 0.5, 0.0),
        "acquire_token": ActionCost(25.0, 2.0, 0.1),
        "route_direct": ActionCost(20.0, 2.0, 0.2),
        "route_fallback": ActionCost(45.0, 4.0, 0.05),
        "write_data": ActionCost(30.0, 3.0, 0.15),
        "verify_channel": ActionCost(15.0, 1.5, 0.0),
        "optimize_stream": ActionCost(40.0, 3.5, 0.05),
        "compute_transform": ActionCost(20.0, 2.0, 0.0),
        "commit_batch": ActionCost(35.0, 3.0, 0.1),
    }

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.state: Dict[str, Any] = {}
        self.masked_keys: Set[str] = {"latent_condition", "auth_token", "congestion_level", "degraded_subsystems"}
        self.action_history: List[Dict[str, Any]] = []
        self.cumulative_cost: float = 0.0
        self.reset(seed)

    def reset(self, seed: Optional[int] = None, scenario: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reset the environment to an initial state."""
        if seed is not None:
            self.seed = seed
            self.rng = random.Random(seed)

        self.action_history.clear()
        self.cumulative_cost = 0.0

        # Base default initial state
        default_state: Dict[str, Any] = {
            "status": "ready",
            "phase": "initialized",
            "latent_condition": "stable",
            "channel_verified": False,
            "auth_token": None,
            "has_token": False,
            "congestion_level": 1.0,
            "degraded_subsystems": [],
            "data_store": {},
            "active_route": None,
            "processed_items": 0,
            "optimized": False,
            "stream_ready": True,
        }

        if scenario:
            default_state.update(scenario)

        self.state = default_state
        return self.observe()

    def observe(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Return observations. By default, masks latent internal variables.
        If a specific scope is requested (probe), returns that scope's details.
        """
        if scope is None or scope == "public":
            # Filter out masked latent keys for partial observability
            obs = {k: v for k, v in self.state.items() if k not in self.masked_keys}
            obs["cumulative_cost"] = self.cumulative_cost
            return obs
        elif scope == "latent_condition" or scope == "environment":
            return {
                "latent_condition": self.state.get("latent_condition", "stable"),
                "congestion_level": self.state.get("congestion_level", 1.0),
                "degraded_subsystems": list(self.state.get("degraded_subsystems", [])),
            }
        elif scope == "security":
            return {
                "has_token": self.state.get("has_token", False),
                "channel_verified": self.state.get("channel_verified", False),
            }
        else:
            return {"error": f"Unknown observation scope: {scope}"}

    def act(self, action_name: str, **kwargs: Any) -> ToolResult:
        """
        Execute an action against the environment subject to latent rules and costs.
        """
        condition = self.state.get("latent_condition", "stable")
        cost_spec = self.BASE_COSTS.get(action_name, ActionCost(20.0, 2.0, 0.1))
        cost_multiplier = self.state.get("congestion_level", 1.0) if condition == "congested" else 1.0
        step_cost = cost_spec.total_cost * cost_multiplier
        self.cumulative_cost += step_cost

        action_record = {
            "action": action_name,
            "kwargs": kwargs,
            "condition": condition,
            "cost": step_cost,
            "timestamp": time.time(),
        }

        # Handle actions under latent rules
        if action_name == "observe":
            scope = kwargs.get("scope")
            obs = self.observe(scope=scope)
            action_record["success"] = True
            action_record["output"] = obs
            self.action_history.append(action_record)
            return ToolResult(success=True, output=obs, execution_time_sec=step_cost / 1000.0)

        elif action_name == "probe":
            target = kwargs.get("target", "latent_condition")
            if target in ("latent_condition", "environment", "condition"):
                found_cond = self.state.get("latent_condition", "stable")
                out = {"latent_condition": found_cond, "status": "probed"}
                action_record["success"] = True
                action_record["output"] = out
                self.action_history.append(action_record)
                return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)
            elif target == "security":
                out = {"has_token": self.state.get("has_token", False), "status": "probed"}
                action_record["success"] = True
                action_record["output"] = out
                self.action_history.append(action_record)
                return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)
            else:
                out = {"target": target, "value": self.state.get(target, None)}
                action_record["success"] = True
                action_record["output"] = out
                self.action_history.append(action_record)
                return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "acquire_token":
            self.state["auth_token"] = f"AUTH_{self.rng.randint(1000, 9999)}"
            self.state["has_token"] = True
            out = {"token_acquired": True, "auth_token": self.state["auth_token"]}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "verify_channel":
            self.state["channel_verified"] = True
            out = {"channel_verified": True}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "optimize_stream":
            self.state["optimized"] = True
            if condition == "congested":
                self.state["congestion_level"] = 1.0  # Alleviates congestion
            out = {"optimized": True, "congestion_level": self.state.get("congestion_level", 1.0)}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "route_direct":
            # Latent rule: fails if degraded
            if condition == "degraded" or "direct_route" in self.state.get("degraded_subsystems", []):
                err = "Action failed: direct route is degraded. Fallback route required."
                action_record["success"] = False
                action_record["error"] = err
                self.action_history.append(action_record)
                return ToolResult(success=False, error=err, execution_time_sec=step_cost / 1000.0)

            self.state["active_route"] = "direct"
            out = {"route": "direct", "status": "active"}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "route_fallback":
            self.state["active_route"] = "fallback"
            out = {"route": "fallback", "status": "active"}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "write_data":
            # Latent rule: requires auth_token if condition == "secure"
            key = kwargs.get("key", "default_key")
            value = kwargs.get("value", "default_value")
            if condition == "secure" and not self.state.get("has_token"):
                err = "Action failed: security condition requires auth_token before write."
                action_record["success"] = False
                action_record["error"] = err
                self.action_history.append(action_record)
                return ToolResult(success=False, error=err, execution_time_sec=step_cost / 1000.0)

            # Latent rule: requires an active route
            if self.state.get("active_route") is None:
                err = "Action failed: no active route established for data write."
                action_record["success"] = False
                action_record["error"] = err
                self.action_history.append(action_record)
                return ToolResult(success=False, error=err, execution_time_sec=step_cost / 1000.0)

            self.state["data_store"][key] = value
            out = {"written": True, "key": key, "value": value}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "commit_batch":
            if condition == "congested" and not self.state.get("optimized", False):
                err = "Action failed: network congested. Stream must be optimized prior to batch commit."
                action_record["success"] = False
                action_record["error"] = err
                self.action_history.append(action_record)
                return ToolResult(success=False, error=err, execution_time_sec=step_cost / 1000.0)

            self.state["phase"] = "committed"
            self.state["processed_items"] += int(kwargs.get("batch_size", 10))
            out = {"committed": True, "phase": "committed", "total_processed": self.state["processed_items"]}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        elif action_name == "compute_transform":
            val = str(kwargs.get("data", ""))
            mode = kwargs.get("mode", "upper")
            res = val.upper() if mode == "upper" else val.lower()
            out = {"transformed": res}
            action_record["success"] = True
            action_record["output"] = out
            self.action_history.append(action_record)
            return ToolResult(success=True, output=out, execution_time_sec=step_cost / 1000.0)

        else:
            err = f"Unknown open-world action: {action_name}"
            action_record["success"] = False
            action_record["error"] = err
            self.action_history.append(action_record)
            return ToolResult(success=False, error=err, execution_time_sec=step_cost / 1000.0)

    def verify_state(self, target_criteria: Dict[str, Any]) -> bool:
        """
        Verify whether the ground-truth state satisfies target criteria.
        Decoupled from superficial action strings or traces.
        """
        for k, expected_v in target_criteria.items():
            if k == "data_store":
                if not isinstance(expected_v, dict):
                    return False
                for d_k, d_v in expected_v.items():
                    if self.state.get("data_store", {}).get(d_k) != d_v:
                        return False
            elif self.state.get(k) != expected_v:
                return False
        return True


class OpenWorldTool(Tool):
    """Tool adapter wrapping OpenWorldEnvironment for Nirmal-1 ToolRegistry."""

    name = "open_world_env"
    description = "Interact with the open-world environment: observe, probe, and act."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "observe",
                    "probe",
                    "acquire_token",
                    "verify_channel",
                    "optimize_stream",
                    "route_direct",
                    "route_fallback",
                    "write_data",
                    "commit_batch",
                    "compute_transform",
                ],
                "description": "Environment action to execute",
            },
            "scope": {"type": "string", "description": "Scope for observe/probe"},
            "target": {"type": "string", "description": "Target field to probe"},
            "key": {"type": "string", "description": "Key for write_data"},
            "value": {"type": "string", "description": "Value for write_data"},
            "batch_size": {"type": "integer", "description": "Batch size for commit"},
            "data": {"type": "string", "description": "Data payload for transform"},
            "mode": {"type": "string", "description": "Transform mode"},
        },
        "required": ["action"],
    }

    def __init__(self, env: Optional[OpenWorldEnvironment] = None) -> None:
        self.env = env if env is not None else OpenWorldEnvironment()

    def execute(self, action: str, **kwargs: Any) -> ToolResult:
        return self.env.act(action, **kwargs)
