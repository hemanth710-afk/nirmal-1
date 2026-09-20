# Nirmal-1 V10.6 — Symbol/Relation Decoupling Study

## 1. V10.5 Starting Evidence
V10.5 rigorously established that the fully-disjoint OOD accuracy is exactly **0.00% ± 0.00%** across $k=0,1,2,4,8$ in-context demonstrations, across 3 seeds, across 6 rule families, and across all demonstration quality and order conditions. The fundamental bottleneck is that the standard token embedding lookup associates rule structure with specific token integer identities, making transfer to entirely unseen token ranges impossible.

## 2. Research Question
Can Nirmal learn to represent TOKEN IDENTITY and RELATIONAL STRUCTURE separately — and then apply the learned rule to completely unseen token identities?

The desired behavior: train on rules over `TRAIN_VOCAB` $[10, 110)$; test on disjoint `DISJOINT_OOD` $[130, 230)$ using ordinary token inputs only.

## 3. Representation Architecture
A dual-channel model wraps the base `L0` transformer:
- **Identity Channel:** Standard token embedding from the base model (unchanged).
- **Relation Channel (learned):** `PairwiseRelationEncoder` — computes sequential token differences at runtime (no external labels), maps them through a trainable embedding and linear projection, and additively augments the base logits.
- **Control Channel (frozen):** `RandomRelationEncoder` — frozen random embedding; should NOT improve OOD (A2 control).
- **Permutation Augmentor:** Randomly remaps surface token identities while preserving rule structure during training.
- **Permutation Consistency Loss:** Encourages the relation channel to produce compatible representations across isomorphic remappings.

## 4. Exact Parameter Counts

| Ablation | Description | Parameter Count |
|---|---|---|
| A0 | Identity Only (Baseline) | ~64K |
| A1 | Identity + Pairwise Relation | ~67K |
| A2 | Identity + Random Frozen Relation | ~67K |
| A3 | Identity + Perm Augmentation | ~64K |
| A4 | Identity + Relation + Perm Aug | ~67K |
| A5 | Identity + Relation + Perm Aug + Consistency | ~67K |
| A6 | Full (Scaffold Removed at Eval) | ~67K |

(Exact counts recorded per seed in machine-readable JSON.)

## 5. Baseline Controls
| Ablation | Description | Params | Train Acc | OOD Acc | Held-Out OOD | OOD Gain |
|---|---|---|---|---|---|---|
| **A0** | Identity Only (Baseline) | 73,714 | 16.15% ± 0.48% | 0.00% ± 0.00% | 0.00% ± 0.00% | +0.00% |
| **A1** | Identity + Pairwise Relation | 82,258 | 15.62% ± 1.27% | 0.00% ± 0.00% | 0.00% ± 0.00% | +0.00% |
| **A2** | Identity + Random Frozen Relation (Control) | 78,258 | 12.15% ± 3.38% | 0.00% ± 0.00% | 0.00% ± 0.00% | +0.00% |
| **A3** | Identity + Perm Augmentation | 82,258 | 16.32% ± 0.56% | 15.97% ± 0.56% | 0.00% ± 0.00% | +15.97% |
| **A4** | Identity + Relation + Perm Aug | 82,258 | 15.80% ± 0.74% | 16.67% ± 0.00% | 0.00% ± 0.00% | +16.67% |
| **A5** | Identity + Relation + Perm Aug + Consistency | 82,258 | 15.80% ± 0.74% | 16.67% ± 0.00% | 0.00% ± 0.00% | +16.67% |
| **A6** | Full (Scaffold Removed at Eval) | 82,258 | 15.80% ± 0.74% | 16.67% ± 0.00% | 0.00% ± 0.00% | +16.67% |

## 6. Per-Rule OOD Results
| Rule | A0 OOD | A1 OOD | A2 OOD | A3 OOD | A4 OOD | A5 OOD | A6 OOD |
|---| --- | --- | --- | --- | --- | --- | --- |
| **copy** | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 13.54% ± 1.67% | 14.58% ± 1.67% | 14.58% ± 1.67% | 14.58% ± 1.67% |
| **increment** | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 35.42% ± 1.67% | 40.62% ± 2.89% | 40.62% ± 2.89% | 40.62% ± 2.89% |
| **fixed_shift** | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 17.71% ± 14.53% | 16.67% ± 7.27% | 16.67% ± 7.27% | 16.67% ± 7.27% |
| **simple_composition** | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 29.17% ± 10.14% | 28.12% ± 10.41% | 28.12% ± 10.41% | 28.12% ± 10.41% |
| **double_step** | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% |
| **reverse** | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% |

## 7. Relation Invariance Diagnostics
`d_same` = mean distance between same-rule / different-surface representations.  
`d_diff` = mean distance between different-rule representations.  
A larger **invariance gap** (`d_diff - d_same`) suggests the relation channel is capturing rule-level structure.

| Ablation | d_same | d_diff | Invariance Gap |
|---|---|---|---|
| A1 | 0.0000 | 2.9665 | 2.9665 |
| A4 | 0.0000 | 2.4693 | 2.4693 |
| A5 | 0.0000 | 2.4693 | 2.4693 |

> **Important:** Hidden-state similarity is a diagnostic only. The primary metric is scaffold-off OOD accuracy.

## 8. Scaffold-Off Results (Phase 7)
A6 represents the best-performing model with all auxiliary training signals disabled at evaluation time:
- Permutation consistency loss: **disabled**.
- Relation encoder: **disabled** (`use_relation=False`).
- Input: ordinary tokens only.
- This measures whether the rule was genuinely internalized into the base model weights.

## 9. Leakage Certificates
- vocab_disjoint: `True`
- no_row_overlap: `True`
- no_subseq_leak: `True`
- valid: `True`

## 10. Failure Classification
**Classification:** `SCAFFOLD_DEPENDENT`

Marginal improvement (16.67% gain) that did not survive scaffold removal.

## 11. Limitations
- All experiments use micro-scale models ($L0$, $\sim 64\text{K}$ parameters).
- The pairwise difference encoding (sequential position-0 to position-1 delta) is a local relational signal and may not be sufficient for longer-range or compositional rule detection.
- 500 training steps may be insufficient for strong relational channel learning with small batch sizes.

## 12. Recommendation for V10.7
**Recommendation for V10.7:** Investigate stronger equivariance constraints or symbolic token decoupling.
