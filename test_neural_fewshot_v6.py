"""
Evaluation test suite for unbiased few-shot in-context learning (V6 Section 11).
Evaluates 0, 1, 2, 4, 8, 16 shots without label boosts or evaluator metadata.
"""

import pytest
import torch

from nirmal.configuration_nirmal import NirmalConfig
from nirmal.model import NirmalForCausalLM
from training.dataset import CharTokenizer
from training.evaluate_v6 import evaluate_neural_fewshot_v6


@pytest.fixture
def test_model():
    cfg = NirmalConfig(
        vocab_size=128,
        hidden_size=64,
        num_hidden_layers=2,
        num_attention_heads=2,
        num_key_value_heads=1,
        head_dim=32,
        context_length=256,
        intermediate_size=128,
        num_experts=2,
        num_experts_per_tok=1,
        full_attention_interval=2,
    )
    return NirmalForCausalLM(cfg)


def test_unbiased_fewshot_evaluation(test_model):
    tokenizer = CharTokenizer()
    results = evaluate_neural_fewshot_v6(test_model, tokenizer, shot_counts=[0, 1, 2, 4])
    assert "shot_0" in results
    assert "shot_1" in results
    assert "shot_2" in results
    assert "shot_4" in results
    for v in results.values():
        assert v in (0.0, 1.0)
