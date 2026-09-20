"""
Evaluation test suite for neural world-model state prediction (V6 Section 13).
Evaluates next-state prediction on unseen state combinations.
"""

import pytest
import torch

from nirmal.configuration_nirmal import NirmalConfig
from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from training.evaluate_v6 import evaluate_neural_world_model_v6


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


def test_neural_world_model_prediction(test_model):
    tokenizer = CharTokenizer()
    results = evaluate_neural_world_model_v6(test_model, tokenizer)
    assert "world_model_acc" in results
    assert 0.0 <= results["world_model_acc"] <= 1.0
    assert results["test_count"] > 0
