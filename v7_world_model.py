"""
World-Model Generalization Evaluation for Nirmal-1 V7 (Section 13).
Evaluates next-state prediction, structural shift, conservation laws, and counterfactuals:
- Parameter shifts (novel continuous/discrete values)
- Structural shifts (unseen graph topologies and node connections)
- Physical conservation law adherence
- Counterfactual intervention prediction
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import torch

from nirmal.model import NirmalForCausalLM
from evals.v7_reasoning import score_loglik


@dataclass
class WorldModelEvalResult:
    standard_acc: float
    param_shift_acc: float
    structural_shift_acc: float
    conservation_adherence: float
    counterfactual_acc: float
    overall_accuracy: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_world_model_v7(
    model: NirmalForCausalLM,
    tokenizer: Any,
) -> WorldModelEvalResult:
    """
    Evaluates neural world model across standard, shifted, conservation, and counterfactual tests.
    """
    # 1. Standard State Transition
    standard_cases = [
        ("State: {valve: closed, tank: empty}. Action: open_valve. Next State: {valve: open, tank:", " filling}", " empty}"),
        ("State: {pump: off, pressure: 10}. Action: start_pump. Next State: {pump: on, pressure:", " 50}", " 0}"),
    ]

    # 2. Parameter Shifts (novel values unseen in simple nominal distributions)
    param_shift_cases = [
        ("State: {pressure: 450_kPa, temp: 85_C}. Action: inject_coolant. Next State: {pressure: 450_kPa, temp:", " 65_C}", " 105_C}"),
        ("State: {current: 12.5_A, load: 80_W}. Action: add_resistor. Next State: {current:", " 10.0_A", " 15.0_A"),
    ]

    # 3. Structural Shifts (novel topology routing)
    structural_shift_cases = [
        ("Topology: Pipeline [Source] -> [NodeX] -> [Sink]. Valve at NodeX is closed. Flow Source to Sink:", " blocked", " active"),
        ("Topology: Mesh [A] linked to [B, C]; [B] linked to [D]; [C] broken. Path from A to D:", " via_B", " via_C"),
    ]

    # 4. Conservation Laws (mass / energy / state conservation)
    conservation_cases = [
        ("Law of Mass Conservation: Inflow=50 L/min, Outflow=50 L/min. Storage change is:", " 0 L/min", " 100 L/min"),
        ("Conservation: Closed system energy total is 500 J. Heat lost = 50 J. Work done is:", " 450 J", " 550 J"),
    ]

    # 5. Counterfactual Reasoning
    counterfactual_cases = [
        ("History: Action was close_switch -> circuit completed. Counterfactual: If open_switch had occurred, circuit would be:", " open", " shorted"),
        ("History: Coolant added at t=2 -> overheat prevented. Counterfactual: If coolant had NOT been added, system would be:", " overheated", " nominal"),
    ]

    def eval_suite(cases: List[tuple]) -> float:
        corr = 0
        for prompt, target, wrong in cases:
            st = score_loglik(model, tokenizer, prompt, target)
            sw = score_loglik(model, tokenizer, prompt, wrong)
            if st > sw:
                corr += 1
        return round(corr / len(cases), 4)

    acc_std = eval_suite(standard_cases)
    acc_param = eval_suite(param_shift_cases)
    acc_struct = eval_suite(structural_shift_cases)
    acc_cons = eval_suite(conservation_cases)
    acc_cf = eval_suite(counterfactual_cases)

    overall = round((acc_std + acc_param + acc_struct + acc_cons + acc_cf) / 5.0, 4)

    return WorldModelEvalResult(
        standard_acc=acc_std,
        param_shift_acc=acc_param,
        structural_shift_acc=acc_struct,
        conservation_adherence=acc_cons,
        counterfactual_acc=acc_cf,
        overall_accuracy=overall,
    )
