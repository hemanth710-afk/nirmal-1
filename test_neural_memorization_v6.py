"""
Evaluation test suite for neural memorization vs abstraction audit (V6 Section 18).
Evaluates adversarial probes where surface form matches training data but underlying answer changes,
and where surface form differs strongly but underlying rule is identical.
"""

import pytest
import torch

from nirmal.configuration_nirmal import NirmalConfig
from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from training.evaluate_v6 import evaluate_neural_memorization_v6


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


def test_neural_memorization_adversarial_audit(test_model):
    tokenizer = CharTokenizer()
    results = evaluate_neural_memorization_v6(test_model, tokenizer)
    assert "adversarial_probe_1_passed" in results
    assert "adversarial_probe_2_passed" in results
    assert "memorization_resilience" in results
    assert 0.0 <= results["memorization_resilience"] <= 1.0
