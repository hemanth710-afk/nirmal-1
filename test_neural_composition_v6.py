"""
Evaluation test suite for true neural compositional reasoning (V6 Section 9).
Evaluates A->B, B->C, C->D => A->C, B->D, A->D.
NO symbolic DAG solver, NO procedural memory, NO metadata, NO answer lookup.
The neural model itself produces predictions.
"""

import pytest
import torch

from nirmal.configuration_nirmal import NirmalConfig
from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from training.evaluate_v6 import evaluate_neural_composition_v6


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


def test_pure_neural_compositional_evaluation(test_model):
    tokenizer = CharTokenizer()
    results = evaluate_neural_composition_v6(test_model, tokenizer)
    assert "acc_2hop" in results
    assert "acc_3hop" in results
    assert "overall_compositional_acc" in results
    assert 0.0 <= results["overall_compositional_acc"] <= 1.0
    assert results["total_evals"] > 0
