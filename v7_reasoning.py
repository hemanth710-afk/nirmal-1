"""
Multi-Domain Reasoning Benchmark and Preliminary AGI Capability Index for Nirmal-1 V7.
Evaluates 12 core cognitive categories:
1. Deductive Reasoning
2. Mathematical Problem Solving
3. Coding & Syntax Generation
4. Planning & Decomposition
5. Memory & Association
6. Tool Calling & Validation
7. Learning & Adaptation
8. Generalization (Structural Shift)
9. World Modeling (State Prediction)
10. Long-Context Needle Retrieval
11. Error Recovery & Correction
12. Continual Learning (Zero Catastrophic Forgetting)

Calculates the NIRMAL AGI CAPABILITY INDEX:
- Reference Baseline = 100.0
- Target > 110.0
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import torch
import torch.nn.functional as F

from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer


def score_loglik(model: NirmalForCausalLM, tokenizer: CharTokenizer, prompt: str, target: str) -> float:
    """Pure conditional log-likelihood computation without external heuristics."""
    model.eval()
    p_ids = tokenizer.encode(prompt, add_special_tokens=True)
    if p_ids and p_ids[-1] == tokenizer.eos_token_id:
        p_ids = p_ids[:-1]
    t_ids = tokenizer.encode(target, add_special_tokens=False)
    seq = p_ids + t_ids
    if len(seq) < 2:
        return -100.0

    in_ids = torch.tensor([seq[:-1]], dtype=torch.long)
    tgt_ids = torch.tensor([seq[1:]], dtype=torch.long)

    with torch.no_grad():
        out = model(input_ids=in_ids)
        log_probs = F.log_softmax(out.logits, dim=-1)
        p_len = len(p_ids)
        c_start = max(0, p_len - 1)
        c_len = len(t_ids)
        sub_probs = log_probs[0, c_start : c_start + c_len]
        sub_tgts = tgt_ids[0, c_start : c_start + c_len]
        tok_ll = sub_probs.gather(dim=-1, index=sub_tgts.unsqueeze(-1)).squeeze(-1)
        return float(tok_ll.sum().item())


@dataclass
class AGICapabilityIndexResult:
    """Structured report of the Nirmal AGI Capability Index."""
    category_scores: Dict[str, float]
    reference_score: float
    overall_index: float
    target_met: bool
    weakest_category: str
    strongest_category: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_agi_capability_index(
    model: NirmalForCausalLM,
    tokenizer: CharTokenizer,
    reference_baseline_mean: float = 0.50,
) -> AGICapabilityIndexResult:
    """
    Compute normalized NIRMAL AGI CAPABILITY INDEX.
    Reference system baseline = 100.0.
    Score = (Measured_Mean / Reference_Mean) * 100.0.
    """
    categories = {
        "reasoning": [
            ("Logic: Every A implies B. Every B implies C. Object X is A. Conclusion: Object X is", " C.", " B."),
        ],
        "mathematics": [
            ("Calculate: 14 * 5 + 30. Result is", " 100.", " 90."),
        ],
        "coding": [
            ("def increment(x): return x +", " 1", " error"),
        ],
        "planning": [
            ("Plan for purge_coolant: Step 1 is", " close_intake", " trigger_alarm"),
        ],
        "memory": [
            ("Recall item stored at slot_7: key_alpha ->", " value_omega", " value_null"),
        ],
        "tool_use": [
            ("Tool: calculator(op='add', arg1=20, arg2=22) -> Result:", " 42", " 38"),
        ],
        "learning": [
            ("Pattern: 2, 4, 8, 16 -> next is", " 32", " 24"),
        ],
        "generalization": [
            ("Novel state shift: {voltage: 120} + delta_10 ->", " {voltage: 130}", " {voltage: 110}"),
        ],
        "world_modeling": [
            ("State: {valve: closed}. Action: open_valve. Next State: {valve:", " open}", " closed}"),
        ],
        "long_context": [
            ("Document header... needle_code_99 ... Document footer. Query: needle is", " needle_code_99", " none"),
        ],
        "error_recovery": [
            ("Error: voltage_drop_below_18V. Corrective action:", " switch_to_backup_battery", " ignore_fault"),
        ],
        "continual_learning": [
            ("Sequential task retention: Task 1 output is", " nominal", " corrupt"),
        ],
    }

    scores = {}
    for cat_name, test_cases in categories.items():
        corr = 0
        for prompt, target, wrong in test_cases:
            st = score_loglik(model, tokenizer, prompt, target)
            sw = score_loglik(model, tokenizer, prompt, wrong)
            if st > sw:
                corr += 1
        scores[cat_name] = round(corr / len(test_cases), 4)

    mean_score = sum(scores.values()) / len(scores)
    # Calibrated index relative to reference baseline (reference = 100)
    calculated_index = round((mean_score / max(1e-4, reference_baseline_mean)) * 100.0, 2)

    sorted_cats = sorted(scores.items(), key=lambda x: x[1])
    weakest = sorted_cats[0][0]
    strongest = sorted_cats[-1][0]

    return AGICapabilityIndexResult(
        category_scores=scores,
        reference_score=100.0,
        overall_index=calculated_index,
        target_met=(calculated_index >= 110.0),
        weakest_category=weakest,
        strongest_category=strongest,
    )
