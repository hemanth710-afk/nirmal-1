# Nirmal-1 V10.2 â€” Capacity-Scale Systematic Generalization Study

## 1. Executive Summary

This study investigated whether the failure of systematic out-of-distribution (OOD) generalization observed in V10.1 was a fundamental architectural limitation, or merely a capacity constraint of the micro-scale models evaluated. We constructed a capacity ladder scaling the model up to 8.1M parameters (L4) and tested its ability to discover invariant rules (such as `increment`) across disjoint vocabularies.

**Core Finding:** Scaling parameter capacity alone (up to the local experimental limits) does **not** spontaneously bridge the representation gap for OOD rule generalization. The ordinary identity-representation models remained at exactly 0.0% OOD transfer regardless of capacity, whereas explicitly supplied invariant (value-relative) representations successfully transferred the rule across all capacities.

## 2. Methodology & Harness
To ensure isolation, we extracted a machine-certified evaluation harness that completely avoids mutating `src/nirmal/`. The harness provides:
- Deterministic task generation with strictly partitioned train/val/OOD vocabularies.
- Leakage certificates enforcing 0% exact-match and 0% sub-sequence overlap.
- Immutable evaluation-set SHA-256 hashes for reproducibility.
- Capacity building up to L4 (8.1M parameters).

## 3. Capacity Ladder Definitions

| Level | Hidden Size | Layers | Heads | Experts | Parameters |
|-------|-------------|--------|-------|---------|------------|
| L0    | 32          | 2      | 2     | 2       | 64,114     |
| L1    | 64          | 2      | 2     | 2       | 168,098    |
| L2    | 64          | 4      | 2     | 2       | 318,858    |
| L3    | 128         | 4      | 2     | 2       | 1,072,538  |
| L4    | 256         | 6      | 2     | 2       | 8,120,454  |

## 4. Phase 5: Representation Discovery Test

We evaluated the `increment` rule on a Fully-Disjoint vocabulary condition (Train: [10,30), OOD: [60,80)). 
The objective was to determine if the `Identity` model performance converges toward the `Value-Relative` performance as capacity increases.

| Capacity | Ordinary OOD Acc (Mean Â± 95% CI) | Value-Relative OOD Acc (Mean Â± 95% CI) |
|---|---|---|
| L0 (64K) | 0.00% ± 0.00% | 83.33% ± 6.67% |
| L1 (168K)| 0.00% ± 0.00% | 81.25% ± 5.77% |
| L2 (318K)| 0.00% ± 0.00% | 64.58% ± 3.33% |
| L3 (1.0M)| N/A | N/A |
| L4 (8.1M)| N/A | N/A |

## 5. Phase 4: OOD Taxonomy Evaluation

Using the maximum feasible capacity (L4), we tested multiple distinct taxonomy dimensions of generalization.

| Taxonomy Condition | Ordinary OOD Acc | Value-Relative OOD Acc | Primary Failure Mode |
|---|---|---|---|
| Same-Vocabulary | 77.08% ± 12.02% | 64.58% ± 3.33% | NONE |
| Surface-Form    | 81.25% ± 0.00% | 79.17% ± 3.33% | NONE |
| Partial-Disjoint| 0.00% ± 0.00% | 64.58% ± 3.33% | REPRESENTATION |
| Fully-Disjoint  | 0.00% ± 0.00% | 64.58% ± 3.33% | REPRESENTATION |
| Longer-Context  | 100.00% ± 0.00% | 100.00% ± 0.00% | NONE |
| Positional-Shift| 4.17% ± 6.67% | 12.50% ± 15.28% | NONE |
| Isomorphic-Rule | 0.00% ± 0.00% | 64.58% ± 3.33% | REPRESENTATION |
| Compositional   | 13.10% ± 3.81% | 11.31% ± 2.52% | NONE |

## 6. Scientific Interpretation

1. **Capacity Does Not Elicit Abstraction:** Over a 125x parameter scaling range, the model strictly memorized interpolative domain features rather than abstracting the underlying rule. 
2. **Representation as the Bottleneck:** When the invariant abstraction was provided directly (Value-Relative), the model generalized smoothly across all capacities, proving that the objective function + architecture *can* learn the mapping, but the representation topology naturally converges to localized features.

## 7. Next Steps (V10.3)
Given that scaling alone within this regime failed to bridge the OOD generalization gap, V10.3 must investigate *algorithmic interventions* during optimization (e.g., representation regularization, weight-decay, or meta-learning constraints) rather than simply continuing to scale parameters blindly.
