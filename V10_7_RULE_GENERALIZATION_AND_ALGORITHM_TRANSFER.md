# Nirmal-1 V10.7 — Rule Generalization and Algorithm Transfer Study

## 1. V10.6 Starting Evidence
The V10.6 study established:
- **Identity Baseline (A0):** `0.00% +/- 0.00%` fully-disjoint OOD accuracy across all evaluated rules.
- **Permutation Augmentation (A3):** Achieved `15.97% +/- 0.56%` OOD accuracy without adding extra parameters to the base model.
- **Dual-Channel + Consistency (A4, A5):** Reached `16.67% +/- 0.00%` OOD accuracy with zero cross-seed variance.
- **Scaffold-Off Evaluation (A6):** Maintained `16.67% +/- 0.00%` when evaluated strictly with ordinary tokens (no auxiliary signals or scaffolds).
- **Held-Out Rules:** Yielded `0.00%` OOD transfer.
- **Classification:** `PARTIAL_INTERNALIZATION` — permutation augmentation enabled transfer of a trained rule to novel symbols, but did not generalize to unseen rules.

## 2. Research Question
Can Nirmal:
1. Learn a rule,
2. Apply that rule to unseen symbols (**Rule Transfer**),
3. Distinguish different rules without mutual interference, and
4. Generalize to a rule that was not present during training (**Rule Generalization**)?

This distinction separates *"learning a specific rule over arbitrary symbols"* from *"learning the meta-algorithmic capacity to infer and execute arbitrary rules"*.

## 3. Rule Taxonomy
Six deterministic algorithmic transformations evaluated over integer vocabularies:
- **R1 COPY:** $[b, b, b]$
- **R2 INCREMENT:** $[b, b + 1, b + 2]$
- **R3 FIXED_SHIFT:** $[b, b + 3, b + 6]$
- **R4 DOUBLE_STEP:** $[b, b + 2, b + 4]$
- **R5 REVERSE:** $[b + 2, b + 1, b]$
- **R6 SIMPLE_COMPOSITION:** $[b, b + 1, b + 3]$

### Vocabulary Partitions:
- `TRAIN_VOCAB`: $[10, 110)$ (100 tokens)
- `PARTIAL_VOCAB`: $[70, 170)$ (100 tokens; 40 token overlap with train, 60 unseen)
- `DISJOINT_VOCAB`: $[130, 230)$ (100 tokens; strictly 0 token overlap with train)

## 4. Experiment Matrix
- **Exp A & B:** Multi-rule training and vocabulary transfer across Same, Partial, and Disjoint ranges.
- **Exp C:** Zero-shot generalization to completely held-out rules on known and disjoint vocabularies.
- **Exp D:** Few-shot in-context rule discovery ($k \in \{0, 1, 2, 4, 8\}$ demonstrations).
- **Exp E:** Cross-rule inductive transfer across structurally related rule pairs.
- **Exp F:** Permutation-intensity ablation ($F0$ to $F4$).
- **Exp G:** Representation diagnostics probing internal hidden states.
- **Exp H:** Catastrophic forgetting / interference across progressive sequential training stages.

---

## 5. Experiment B — Known Rule / New Symbol Transfer (Level 1)
Evaluates whether a rule seen during training can be applied to unseen vocabulary partitions.
| Rule | Same Vocab [10, 110) | Partial Vocab [70, 170) | Disjoint Vocab [130, 230) |
|---|---|---|---|
| **copy** | 4.17% +/- 1.67% | 4.17% +/- 4.41% | 9.38% +/- 5.77% |
| **increment** | 23.96% +/- 4.41% | 17.71% +/- 10.14% | 19.79% +/- 12.02% |
| **fixed_shift** | 0.00% +/- 0.00% | 0.00% +/- 0.00% | 2.08% +/- 1.67% |
| **double_step** | 21.88% +/- 5.77% | 9.38% +/- 5.00% | 17.71% +/- 10.93% |
| **reverse** | 1.04% +/- 1.67% | 0.00% +/- 0.00% | 1.04% +/- 1.67% |
| **simple_composition** | 34.38% +/- 5.77% | 21.88% +/- 7.64% | 33.33% +/- 7.27% |
| **OVERALL MEAN** | **14.24% +/- 1.21%** | **8.85% +/- 0.48%** | **13.89% +/- 1.21%** |

---

## 6. Experiment C — Held-Out Rule Generalization (Levels 2 & 3)
Evaluates whether the model can execute a rule never seen during training:
- **Level 2 (C1):** Unseen rule + Known vocabulary ($[10, 110)$)
- **Level 3 (C2):** Unseen rule + Disjoint vocabulary ($[130, 230)$)
| Held-Out Rule | C1: Known Vocab [10, 110) (Level 2) | C2: Disjoint Vocab [130, 230) (Level 3) | Generalization Verdict |
|---|---|---|---|
| **simple_composition** | 2.08% +/- 3.33% | 1.04% +/- 1.67% | `NO_TRANSFER` |
| **double_step** | 0.00% +/- 0.00% | 0.00% +/- 0.00% | `NO_TRANSFER` |

---

## 7. Experiment D — Few-Shot In-Context Rule Discovery
Evaluates whether presenting $k$ context demonstrations enables in-context inference of the held-out rule on disjoint vocabulary:
| Held-Out Rule | k=0 Shots | k=1 Shot | k=2 Shots | k=4 Shots | k=8 Shots |
|---|---|---|---|---|---|
| **simple_composition (Disjoint)** | 3.12% +/- 2.89% | 11.46% +/- 6.01% | 11.46% +/- 7.27% | 18.75% +/- 2.89% | 7.29% +/- 1.67% |
| **double_step (Disjoint)** | 2.08% +/- 3.33% | 4.17% +/- 1.67% | 6.25% +/- 5.77% | 3.12% +/- 2.89% | 8.33% +/- 1.67% |

---

## 8. Experiment E — Cross-Rule Inductive Transfer
Evaluates whether training on an elementary rule induces inductive bias toward an unseen, structurally related rule:
| Source Rule -> Target Rule | Source Disjoint OOD | Target Known Vocab | Target Disjoint OOD | Transfer Status |
|---|---|---|---|---|
| **increment -> double_step** | 100.00% +/- 0.00% | 0.00% +/- 0.00% | 0.00% +/- 0.00% | `ISOLATED` |
| **copy -> reverse** | 100.00% +/- 0.00% | 0.00% +/- 0.00% | 0.00% +/- 0.00% | `ISOLATED` |
| **fixed_shift -> simple_composition** | 100.00% +/- 0.00% | 0.00% +/- 0.00% | 0.00% +/- 0.00% | `ISOLATED` |

---

## 9. Experiment F — Permutation-Intensity Ablation
Evaluates how permutation pressure during training modulates rule transfer and generalization:
| Intensity Level | Permutation Probability | Train Accuracy | Known Rule Disjoint OOD | Held-out Rule Disjoint OOD |
|---|---|---|---|---|
| **F0_none** | 0% | 20.83% +/- 0.83% | 0.00% +/- 0.00% | 0.00% +/- 0.00% |
| **F1_low** | 25% | 23.18% +/- 2.21% | 12.50% +/- 2.50% | 0.00% +/- 0.00% |
| **F2_med** | 50% | 22.14% +/- 1.10% | 17.45% +/- 1.50% | 0.00% +/- 0.00% |
| **F3_heavy** | 75% | 22.14% +/- 0.42% | 20.05% +/- 3.01% | 0.00% +/- 0.00% |
| **F4_full** | 100% | 20.57% +/- 2.32% | 20.31% +/- 1.25% | 0.00% +/- 0.00% |

---

## 10. Experiment G — Representation Diagnostics
Probing internal layer representations ($d_{same}$ vs $d_{diff}$):
- Same-rule cross-vocab distance ($d_{same}$): `3.7498 +/- 0.2912`
- Different-rule distance ($d_{diff}$): `2.4792 +/- 0.2814`
- Invariance Gap ($d_{diff} - d_{same}$): `-1.2706 +/- 0.2960`
- Distance Ratio ($d_{same} / d_{diff}$): `1.5222`

---

## 11. Experiment H — Catastrophic Forgetting & Retention
Measures retention across progressive stages (Stage 1: Copy -> Stage 2: +Incr -> Stage 3: +Shift -> Stage 4: All):
| Training Stage | **copy** | **increment** | **fixed_shift** | **double_step** | **reverse** | **simple_composition** |
|---| --- | --- | --- | --- | --- | --- |
| Stage 1 (Copy) | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| Stage 2 (+Incr) | 40.6% | 58.3% | 0.0% | 0.0% | 0.0% | 0.0% |
| Stage 3 (+Shift) | 35.4% | 24.0% | 34.4% | 0.0% | 0.0% | 0.0% |
| Stage 4 (All) | 11.5% | 32.3% | 2.1% | 13.5% | 1.0% | 21.9% |

- **Average Forgetting across Stages:** 36.72%
- **Average Final Retention:** 14.84%

---

## 12. Primary Success Levels Summary
- **Level 1 — Rule Transfer (Known Rule + Unseen Vocab):** `13.89%`
- **Level 2 — Rule Generalization (Unseen Rule + Known Vocab):** `1.04%`
- **Level 3 — Compositional Generalization (Unseen Rule + Unseen Vocab):** `0.52%`

## 13. Scientific Classification
**Assigned Classifications:** `VOCABULARY_DEPENDENT`, `NO_RULE_GENERALIZATION`, `RULE_SPECIFIC_MEMORIZATION`

## 14. Leakage Certificate
- `vocab_disjoint`: `True`
- `no_row_overlap`: `True`
- `no_subseq_leak`: `True`
- `valid`: `True`

## 15. Limits of Inference & Non-Claims
1. **No Claims of General Rule Induction:** Permutation augmentation successfully breaks the symbol-binding bottleneck for *trained* rules, but does not provide general algorithm induction for *untrained* rules.
2. **Context Demonstrations:** Few-shot demonstrations in the evaluated micro-scale architecture do not dynamically reprogram the model's forward path to compute unseen arithmetic functions without prior gradient-based exposure.
3. **Capacity Constraints:** All tests were conducted under the micro-scale ($L0$, $\sim 64\text{K}$ parameters). Architectural capacity limits may prevent multi-task rule arbitration without explicit modular routing.

## 16. Recommendation for V10.8
1. **Modular Rule Routing:** Explore mixture-of-experts or routing mechanisms that separate rule selection from execution.
2. **Meta-Learning Objectives:** Evaluate explicit meta-learning (MAML-style or episode-based learning-to-learn) to determine if few-shot rule discovery can be trained directly.
3. **Capacity Scaling:** Check whether scaling to $L1$ or $L2$ under multi-rule permutation training permits cross-rule induction without interference.
