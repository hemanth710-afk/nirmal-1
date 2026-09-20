"""
Unbiased In-Context Few-Shot Scaling Benchmark for Nirmal-1 V7 (Section 10).
Evaluates pure conditional log-likelihood across demonstration counts:
k in {0, 1, 2, 4, 8, 16}.
Zero evaluator heuristics, zero label injections, zero metadata leaks.
"""

from typing import Any, Dict, List, Optional
import torch

from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from evals.v7_reasoning import score_loglik


def evaluate_fewshot_scaling_v7(
    model: NirmalForCausalLM,
    tokenizer: CharTokenizer,
    shots: Optional[List[int]] = None,
) -> Dict[str, float]:
    """
    Measure in-context adaptation across k demonstrations.
    """
    shots = shots or [0, 1, 2, 4, 8, 16]
    demo_bank = [
        ("double(3)", " 6"),
        ("double(5)", " 10"),
        ("double(8)", " 16"),
        ("double(12)", " 24"),
        ("double(15)", " 30"),
        ("double(20)", " 40"),
        ("double(25)", " 50"),
        ("double(30)", " 60"),
        ("double(35)", " 70"),
        ("double(40)", " 80"),
        ("double(45)", " 90"),
        ("double(50)", " 100"),
        ("double(60)", " 120"),
        ("double(70)", " 140"),
        ("double(80)", " 160"),
        ("double(90)", " 180"),
    ]

    test_query = "double(14)"
    correct_ans = " 28"
    wrong_ans = " 25"

    results = {}
    for k in shots:
        prefix = ""
        for i in range(min(k, len(demo_bank))):
            inp, out = demo_bank[i]
            prefix += f"Example: {inp} = {out}\n"
        full_prompt = f"{prefix}Query: {test_query} ="

        st = score_loglik(model, tokenizer, full_prompt, correct_ans)
        sw = score_loglik(model, tokenizer, full_prompt, wrong_ans)

        results[f"shot_{k}"] = 1.0 if st > sw else 0.0

    return results
