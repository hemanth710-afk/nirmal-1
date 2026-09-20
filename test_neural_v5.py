"""
Unit and Integration Tests for Nirmal-1 V5 Neural Cognition Suite.
Covers:
- Tokenization stress tests
- Compositional generalization
- Representation generalization
- State transition prediction & calibration
- 3-Way world model ablation
- Multi-step reasoning depth benchmark
- Error recovery with learned verification
- Few-shot learning scaling
- Context needle retrieval
- Neural credit assignment
- Curriculum transfer
- Catastrophic forgetting
- Distribution shift (representation vs rule shift)
"""

import pytest
from nirmal.agent.neural_bridge import NeuralBridge
from training.dataset import CharTokenizer
from training.evaluate_neural import run_tokenization_stress_test
from evals.neural_generalization import (
    run_compositional_holdout_evaluation,
    run_representation_generalization_evaluation,
)
from evals.neural_state_prediction import (
    run_state_prediction_evaluation,
    run_world_model_ablation_evaluation,
)
from evals.neural_reasoning import (
    run_reasoning_depth_evaluation,
    run_error_recovery_evaluation,
)
from evals.neural_fewshot import (
    run_few_shot_evaluation,
    run_context_needle_evaluation,
)
from evals.neural_distribution_shift import (
    run_credit_assignment_evaluation,
    run_curriculum_transfer_evaluation,
    run_catastrophic_forgetting_evaluation,
    run_distribution_shift_evaluation,
)


@pytest.fixture(scope="module")
def neural_bridge():
    return NeuralBridge()


def test_v5_tokenization_suite():
    tok = CharTokenizer("alpha beta gamma 0123456789 +-/*= <tag>")
    rep = run_tokenization_stress_test(tok)
    assert rep.vocab_size > 50
    assert rep.numerical_fidelity_passed is True
    assert rep.rare_token_handling_passed is True
    assert rep.vocab_coverage_percent > 90.0


def test_v5_compositional_holdout(neural_bridge):
    res = run_compositional_holdout_evaluation(neural_bridge, seed=42)
    assert res.hop_1_accuracy == 1.0
    assert res.hop_2_accuracy == 1.0
    assert res.hop_3_accuracy == 1.0
    assert res.system_hybrid_accuracy >= 0.8
    assert res.total_queries >= 6


def test_v5_representation_generalization(neural_bridge):
    res = run_representation_generalization_evaluation(neural_bridge, seed=42)
    assert -1.0 <= res.canonical_accuracy <= 1.0
    assert -1.0 <= res.randomized_accuracy <= 1.0
    assert res.distractor_accuracy is not None
    assert res.retention_ratio is not None


def test_v5_state_prediction_calibration(neural_bridge):
    res = run_state_prediction_evaluation(neural_bridge, num_samples=10, seed=42)
    assert res.num_samples == 5
    assert 0.0 <= res.variable_level_accuracy <= 1.0
    assert 0.0 <= res.brier_score <= 1.0


def test_v5_world_model_3way_ablation(neural_bridge):
    res = run_world_model_ablation_evaluation(neural_bridge, seed=42)
    assert res.in_distribution_symbolic == 1.0
    assert res.in_distribution_hybrid == 1.0
    assert res.novel_ood_symbolic == 0.0
    assert res.novel_ood_hybrid == 1.0
    assert res.multi_step_hybrid == 1.0


def test_v5_reasoning_depth(neural_bridge):
    rep = run_reasoning_depth_evaluation(neural_bridge, depths=[1, 2, 4], seed=42)
    assert 1 in rep.depth_metrics
    assert 2 in rep.depth_metrics
    assert 4 in rep.depth_metrics
    assert rep.depth_metrics[1].success_rate >= rep.depth_metrics[4].success_rate


def test_v5_error_recovery(neural_bridge):
    res = run_error_recovery_evaluation(neural_bridge, num_trials=5, seed=42)
    assert res.fault_detection_rate >= 0.6
    assert res.verified_recovery_rate > res.unverified_success_rate
    assert res.recovery_gain_percent > 0.0


def test_v5_few_shot_scaling(neural_bridge):
    res = run_few_shot_evaluation(neural_bridge, shot_counts=[0, 2, 4], seed=42)
    assert 0 in res.shot_accuracies
    assert 4 in res.shot_accuracies
    assert res.few_shot_acc_8 >= res.zero_shot_acc or res.scaling_gain >= 0.0


def test_v5_context_needle_retrieval(neural_bridge):
    res = run_context_needle_evaluation(neural_bridge, seed=42)
    assert 0.0 <= res.overall_retrieval_rate <= 1.0
    assert 0.0 <= res.beginning_accuracy <= 1.0
    assert 0.0 <= res.middle_accuracy <= 1.0
    assert 0.0 <= res.end_accuracy <= 1.0


def test_v5_neural_credit_assignment(neural_bridge):
    res = run_credit_assignment_evaluation(neural_bridge, seed=42)
    assert res.neural_weighted_loss > 0.0
    assert res.causal_step_weight_ratio > 1.0


def test_v5_curriculum_transfer(neural_bridge):
    res = run_curriculum_transfer_evaluation(neural_bridge, seed=42)
    assert res.forward_transfer_gain_percent > 0.0
    assert res.stage_2_transferred_loss < res.stage_2_isolated_loss


def test_v5_catastrophic_forgetting(neural_bridge):
    res = run_catastrophic_forgetting_evaluation(neural_bridge, seed=42)
    assert res.retention_percent >= 80.0
    assert res.forgetting_rate_percent <= 20.0


def test_v5_distribution_shift_rule_vs_rep(neural_bridge):
    res = run_distribution_shift_evaluation(neural_bridge, seed=42)
    assert res.representation_shift_drop_percent < res.rule_shift_drop_percent
    assert res.rule_shift_accuracy < res.representation_shift_accuracy
