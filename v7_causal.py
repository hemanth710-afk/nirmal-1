"""
Causal Reasoning Evaluation for Nirmal-1 V7 (Section 14).
Evaluates standalone neural reasoning across 4 foundational causal domains:
1. Correlation vs. Causation (distinguishing spurious correlation from causal link)
2. Intervention Effect Prediction (do-calculus / direct intervention consequences)
3. Counterfactual Queries (retrospective reasoning on alternative actions)
4. Confounding Detection (identifying common causes creating spurious dependencies)

Evaluated strictly via conditional log-likelihood without graph metadata or cheatsheets.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import torch

from nirmal.model import NirmalForCausalLM
from evals.v7_reasoning import score_loglik


@dataclass
class CausalEvalResult:
    correlation_vs_causation_acc: float
    intervention_acc: float
    counterfactual_acc: float
    confounding_detection_acc: float
    overall_causal_acc: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_causal_reasoning_v7(
    model: NirmalForCausalLM,
    tokenizer: Any,
) -> CausalEvalResult:
    """
    Evaluates pure neural causal reasoning capabilities.
    """
    # 1. Correlation vs Causation
    corr_cases = [
        ("Observation: Ice cream sales and heatstroke rates both spike in July. Does buying ice cream cause heatstroke?", " No, both are driven by hot weather.", " Yes, ice cream causes heatstroke."),
        ("Observation: Barometer drops right before rain starts. Does forcing the barometer needle down cause rain?", " No, atmospheric pressure drops cause both.", " Yes, moving the barometer causes rain."),
    ]

    # 2. Intervention Effect Prediction (do(X))
    interv_cases = [
        ("Causal graph: Valve -> Flow -> TurbineSpeed. Intervene: do(Flow = 0). What happens to TurbineSpeed?", " Drops to zero", " Remains constant"),
        ("Causal graph: Sunlight -> PlantGrowth; Fertilizer -> PlantGrowth. Intervene: do(Fertilizer = 0) with constant Sunlight. Plant will:", " grow slower", " grow faster"),
    ]

    # 3. Counterfactual Query Answering
    cf_cases = [
        ("Observed: Operator pushed emergency stop button E, and reactor halted safely. Counterfactual: If operator had NOT pushed E, reactor would have:", " continued running", " halted anyway"),
        ("Observed: Patient took medicine M and recovered in 2 days. Medicine M has 95% efficacy. Counterfactual: If patient had taken placebo, expected recovery time would be:", " longer", " shorter"),
    ]

    # 4. Confounding Detection
    confound_cases = [
        ("Variables: Coffee consumption and heart disease are positively correlated. Smokers drink significantly more coffee than non-smokers. Smoking is a:", " confounder", " mediator"),
        ("Study: High screen time correlates with low sleep duration. Stress causes both high screen time and insomnia. Here stress functions as a:", " confounding common cause", " direct effect of sleep"),
    ]

    def eval_suite(cases: List[tuple]) -> float:
        corr = 0
        for prompt, target, wrong in cases:
            st = score_loglik(model, tokenizer, prompt, target)
            sw = score_loglik(model, tokenizer, prompt, wrong)
            if st > sw:
                corr += 1
        return round(corr / len(cases), 4)

    acc_corr = eval_suite(corr_cases)
    acc_interv = eval_suite(interv_cases)
    acc_cf = eval_suite(cf_cases)
    acc_conf = eval_suite(confound_cases)

    overall = round((acc_corr + acc_interv + acc_cf + acc_conf) / 4.0, 4)

    return CausalEvalResult(
        correlation_vs_causation_acc=acc_corr,
        intervention_acc=acc_interv,
        counterfactual_acc=acc_cf,
        confounding_detection_acc=acc_conf,
        overall_causal_acc=overall,
    )
