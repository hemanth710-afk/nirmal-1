"""
Compositional Reasoning Scaling Benchmark for Nirmal-1 V7 (Section 11).
Evaluates standalone neural capability on multi-hop transitive deductions:
- 2-hop (A -> B -> C => A -> C)
- 4-hop (A -> B -> C -> D -> E => A -> E)
- 8-hop (8-link transitive inference)
- 16-hop (16-link transitive inference)
Strictly WITHOUT symbolic DAG solvers, procedural memory, or answer lookups.
"""

from typing import Any, Dict, List, Optional, Tuple
import torch

from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from evals.v7_reasoning import score_loglik


def evaluate_compositional_scaling(
    model: NirmalForCausalLM,
    tokenizer: CharTokenizer,
    hops_to_test: Optional[List[int]] = None,
) -> Dict[str, float]:
    """
    Measure exact multi-hop deduction accuracy across 2-hop, 4-hop, 8-hop, 16-hop.
    """
    hops_to_test = hops_to_test or [2, 4, 8, 16]
    results = {}

    for hops in hops_to_test:
        # Construct linear transitive chain: N_0 -> N_1 -> ... -> N_hops
        nodes = [f"Node_{i}" for i in range(hops + 1)]
        premises = " ".join(f"Premise {i+1}: {nodes[i]} connects to {nodes[i+1]}." for i in range(hops))
        prompt = f"Graph Deduction: {premises} Query: {nodes[0]} reaches target"
        correct_target = f" {nodes[-1]}."
        wrong_target = f" {nodes[1]}."

        st = score_loglik(model, tokenizer, prompt, correct_target)
        sw = score_loglik(model, tokenizer, prompt, wrong_target)

        results[f"{hops}_hop"] = 1.0 if st > sw else 0.0

    mean_acc = sum(results.values()) / len(results)
    results["mean_composition_acc"] = round(mean_acc, 4)
    return results
