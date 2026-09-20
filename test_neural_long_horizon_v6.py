"""
Evaluation test suite for long-horizon neural reasoning (V6 Section 12).
Evaluates branching decision sequences with irreversible traps across horizons 1, 2, 4, 8, 16.
"""

import pytest
import torch

from nirmal.configuration_nirmal import NirmalConfig
from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from training.evaluate_v6 import evaluate_neural_long_horizon_v6


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


def test_long_horizon_branching_rollout(test_model):
    tokenizer = CharTokenizer()
    results = evaluate_neural_long_horizon_v6(test_model, tokenizer, horizons=[1, 2, 4])
    assert "horizon_1" in results
    assert "horizon_2" in results
    assert "horizon_4" in results
