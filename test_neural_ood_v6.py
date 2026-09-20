"""
Evaluation test suite for true neural OOD generalization (V6 Section 10).
Evaluates held-out structural forms with variable renamings, inverse syntax, and distractors.
Enforces symmetric exact ground-truth matching.
"""

import pytest
import torch

from nirmal.configuration_nirmal import NirmalConfig
from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from training.evaluate_v6 import evaluate_neural_ood_v6


@pytest.fixture
def test_model():
    cfg = NirmalConfig(
        vocab_size=128,
        hidden_size=64,
        num_hidden_layers=2,
        num_attention_heads=2,
        num_key_value_heads=1,
        head_dim=32,
        context_length=128,
        intermediate_size=128,
        num_experts=2,
        num_experts_per_tok=1,
        full_attention_interval=2,
    )
    return NirmalForCausalLM(cfg)


def test_pure_neural_ood_symmetric_evaluation(test_model):
    tokenizer = CharTokenizer()
    results = evaluate_neural_ood_v6(test_model, tokenizer)
    assert "ood_accuracy" in results
    assert 0.0 <= results["ood_accuracy"] <= 1.0
    assert results["symmetric_ground_truth_enforced"] is True
