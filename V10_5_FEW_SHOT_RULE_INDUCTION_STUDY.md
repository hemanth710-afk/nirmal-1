# Nirmal-1 V10.5 — Few-Shot Rule Induction Study

## 1. Research Question
Can the current Nirmal experimental model discover and execute a new transformation rule from in-context demonstrations at inference time, instead of relying on memorization from training?

Specifically, does increasing the number of valid demonstrations on a completely unseen, fully-disjoint vocabulary induce the underlying relational transformation, or does performance remain tethered to zero-shot memorization boundaries?

## 2. V10.4 Starting Evidence
- **V10.2:** Model scale alone (L0 -> L2) did not elicit out-of-distribution (OOD) transfer under ordinary token representations (0.00% across scales).
- **V10.3:** Algorithmic training objectives (multi-surface diversity, relational consistency, contrastive isomorphism, progressive curriculum) failed to induce scaffold-off rule abstraction (all 0.00% OOD across 3 seeds).
- **V10.4:** Inductive bias interventions (continuous relative offsets, dynamic hypernetwork weight-binding, recurrent GRU state transitions, latent teacher supervision) all collapsed to 0.00% OOD transfer under ordinary token inputs, and hidden state isomorphic probes registered 0.0% similarity.
- **Cumulative test suite:** 770/770 tests passing; `src/nirmal/` strictly unchanged; authoritative corpus = 233,997 tokens; production STRICT NO-GO.

## 3. Hypotheses
- **Hypothesis 1 (Contextual Induction):** Attention across in-context demonstration examples allows the model to dynamically bind relative transformations, improving prediction accuracy on unseen vocabularies as demonstration count increases ($0 \to 1 \to 2 \to 4 \to 8$).
- **Hypothesis 2 (Memorization Ceiling / Null Hypothesis):** The model relies strictly on token-level transition statistics learned during training. In-context demonstrations on disjoint vocabularies will fail to bridge the semantic gap, yielding flat performance regardless of demonstration count.

## 4. Task Families
The study evaluates 6 deterministic rule transformations:
1. `COPY`: $[b, b, b]$
2. `INCREMENT`: $[b, b+1, b+2]$
3. `DOUBLE_STEP`: $[b, b+2, b+4]$ (Held-out from training)
4. `REVERSE`: $[b+2, b+1, b]$ (Held-out from training)
5. `FIXED_SHIFT`: $[b, b+3, b+6]$
6. `SIMPLE_COMPOSITION`: $[b, b+1, b+3]$

Training rules: `COPY`, `INCREMENT`, `FIXED_SHIFT`, `SIMPLE_COMPOSITION` on `TRAIN_VOCAB` $[10, 110)$.
Held-out evaluation rules: `DOUBLE_STEP`, `REVERSE`.
Disjoint vocabulary: `DISJOINT_OOD_VOCAB` $[130, 230)$ (100 tokens, 100% disjoint from training).

## 5. Demonstration Construction
Each sequence consists of $k \in \{0, 1, 2, 4, 8\}$ demonstrations followed by an evaluation query:
$$\text{Sequence} = [d_1, \text{SEP}, d_2, \text{SEP}, \dots, d_k, \text{SEP}, q_0, q_1, q_2]$$
where each demonstration $d_i$ is a 3-token instance of the rule, $\text{SEP} = 1$, and the query is $[q_0, q_1, q_2]$.
Evaluation metric: Top-1 exact match accuracy in predicting $q_2$ given preceding context.

## 6. Leakage Controls
- **Vocabulary Disjointness:** Verified zero token overlap between `TRAIN_VOCAB` and `DISJOINT_OOD_VOCAB`.
- **Row & Subsequence Isolation:** 0% row overlap and 0% 3-gram subsequence leakage between training instances and evaluation batches.
- **Immutable Hashes:** SHA-256 evaluation set digests recorded.
- **Anti-Cheating:** Ordinary token inputs only. No numeric/value-relative mappings, no hidden rule labels, no inference-time scaffolds.

## 7. Experiment Matrix
- **Exp A / G:** Demonstration count scaling ($k \in \{0, 1, 2, 4, 8\}$) on in-distribution vs fully-disjoint OOD vocabulary.
- **Exp B:** Disjoint vocabulary transfer across demonstration counts.
- **Exp C:** Held-out rule induction (`DOUBLE_STEP`, `REVERSE`).
- **Exp D:** Demonstration quality and controls (Correct vs Random Noise vs Mismatched Rule vs Distractor Tokens).
- **Exp E:** Order robustness (Original vs Reversed vs Permuted demonstration order).
- **Exp F:** Surface remapping across 3 disjoint sub-partitions.

## 8. Demonstration-Count Curve (Exp A & G)
Evaluation across $k \in \{0, 1, 2, 4, 8\}$ demonstrations (Mean ± 95% CI across 3 seeds):

| Demonstration Count ($k$) | In-Vocab Validation Accuracy | Fully-Disjoint OOD Accuracy | OOD Gain from Demos |
|---|---|---|---|
| **k = 0 (Zero-Shot)** | 26.56% ± 1.91% | 0.00% ± 0.00% | 0.00% |
| **k = 1** | 27.08% ± 5.42% | 0.00% ± 0.00% | +0.00% |
| **k = 2** | 22.66% ± 1.25% | 0.00% ± 0.00% | +0.00% |
| **k = 4** | 27.86% ± 4.70% | 0.00% ± 0.00% | +0.00% |
| **k = 8** | 20.31% ± 2.60% | 0.00% ± 0.00% | +0.00% |

## 9. Held-Out-Rule Results (Exp C)
Performance on structurally related transformation rules never seen during training:

| Held-Out Rule | Metric | k = 0 | k = 1 | k = 2 | k = 4 | k = 8 |
|---|---|---|---|---|---|---|
| **DOUBLE_STEP** | In-Vocab Val | 4.17% ± 4.41% | 10.42% ± 1.67% | 6.25% ± 2.89% | 6.25% ± 2.89% | 9.38% ± 5.77% |
| **DOUBLE_STEP** | Disjoint OOD | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% |
| **REVERSE** | In-Vocab Val | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% |
| **REVERSE** | Disjoint OOD | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% |

## 10. Vocabulary-Remapping Results (Exp F)
Evaluating isomorphic rule transfer ($k=4$) across 3 disjoint sub-partitions of the unseen vocabulary space:
- Sub-Block 1 $[130, 160)$: 0.00% ± 0.00%
- Sub-Block 2 $[160, 190)$: 0.00% ± 0.00%
- Sub-Block 3 $[190, 220)$: 0.00% ± 0.00%
- **Mean Remapped Accuracy:** 0.00% ± 0.00%

## 11. Order-Robustness Results (Exp E)
Evaluating sensitivity to demonstration sequence permutations ($k=4$ on disjoint vocabulary):
- **Original Order:** 0.00% ± 0.00%
- **Reversed Order:** 0.00% ± 0.00%
- **Permuted Order:** 0.00% ± 0.00%

## 12. Distractor & Demonstration Quality Results (Exp D)
Evaluating whether the model selectively utilizes informative demonstrations over noise:
- **Control 1 (Random Noise Demonstrations):** 0.00% ± 0.00%
- **Control 2 (Mismatched Rule Demonstrations):** 0.00% ± 0.00%
- **Control 3 (Correct Rule Demonstrations, k=4):** 0.00% ± 0.00%
- **D1 (Single Demonstration, k=1):** 0.00% ± 0.00%
- **D4 (Demonstrations with Distractor Markers):** 0.00% ± 0.00%

## 13. Per-Seed Results
Empirical breakdown across evaluated seeds (42, 43, 44):
| Seed | k=0 OOD | k=1 OOD | k=2 OOD | k=4 OOD | k=8 OOD | Held-Out DoubleStep (k=4) |
|---|---|---|---|---|---|---|
| 42 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| 43 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| 44 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |

## 14. Mean / Std Summary
- **In-Distribution Validation Accuracy (k=4):** 27.86% ± 4.70%
- **Fully-Disjoint OOD Accuracy (k=0, Zero-Shot):** 0.00% ± 0.00%
- **Fully-Disjoint OOD Accuracy (k=4, Few-Shot):** 0.00% ± 0.00%
- **Fully-Disjoint OOD Accuracy (k=8, Few-Shot):** 0.00% ± 0.00%
- **Held-Out Rule DoubleStep Disjoint OOD (k=4):** 0.00% ± 0.00%
- **Held-Out Rule Reverse Disjoint OOD (k=4):** 0.00% ± 0.00%

## 15. Failure Classification
**Classification:** `MEMORIZATION_ONLY`

The empirical evidence demonstrates that the model only succeeds on rules and surface symbols encountered during training:
- Within the seen training vocabulary, the model achieves ~27.86% validation accuracy across rules (vs 1.0% random baseline).
- On the completely unseen, fully-disjoint vocabulary, increasing the number of demonstrations from 0 to 1, 2, 4, and 8 yields **flat 0.00% ± 0.00% accuracy** (0.00% OOD gain across all demonstration counts).
- Demonstrations of held-out rules (`DOUBLE_STEP`, `REVERSE`) similarly achieve 0.00% on disjoint vocabulary.
- The model exhibits no capacity to infer abstract relational transformations from in-context examples when surface token embeddings are ungrounded / out-of-distribution.

## 16. Limits of Inference
- These experiments were conducted on micro-scale experimental models ($L0$, $\sim 64\text{K}$ parameters).
- While few-shot in-context learning is known to emerge at massive parameter scales ($>1\text{B}$ parameters) in pre-trained LLMs, this study rigorously demonstrates that in the micro-scale autoregressive regime, few-shot prompting does not spontaneously bridge vocabulary disjointness without explicit relational inductive biases or pre-existing token co-occurrence grounding.

## 17. Recommendation for V10.6
**Recommendation:** Contextual demonstration alone does not solve the representation-level generalization gap. Since in-weights training interventions (V10.3), inductive biases (V10.4), and in-context demonstrations (V10.5) all fail to generalize to disjoint vocabularies with ordinary tokens, V10.6 should investigate **Meta-Learning with Symbolic Grounding / Pointer Networks** or **Equivariant Embedding Projectors** that decouple symbol token IDs from relation operators before attention layers.
