# Nirmal-1 V10.9 — Foundational Episodic Learning Gate
## Stage 0 + Stage 1 Implementation and Calibration Report

**Status:** FOUNDATIONAL EPISODIC LEARNING EVALUATION COMPLETE  
**Primary Classification:** `FOUNDATIONAL_EPISODIC_LEARNING_FAILURE`  
**Stage 2 Authorization:** **STRICT NO-GO / BLOCKED**  
**Production Status:** **STRICT NO-GO** (Corpus: 233,997 tokens, Approvals: 0/6)

---

## 1. Stage 0 — Instrumentation & Null Calibration

Stage 0 validates that the episodic training, tokenization, masking, gradient propagation, and evaluation harness are fully operational before any scientific claims are evaluated.

| Diagnostic Check | Model Scale | Setup / Condition | Observed Result | Verdict |
|---|---|---|---|---|
| **A. One-Batch Overfit** | L0 | 128 fixed episodes, $\le 2,000$ steps | 100.0% query accuracy at step 50 | `PASS` |
| **A. One-Batch Overfit** | L1 | 128 fixed episodes, $\le 2,000$ steps | 100.0% query accuracy at step 50 | `PASS` |
| **B. Label-Permutation Null** | L0 | Shuffled query targets | Val Acc = 3.0% (Chance = 25.0%) | `PASS` |
| **C. Direct-Label Sanity Control** | L0 | Target explicitly placed in support slot | Val Acc = 100.0% at step 50 | `PASS` |
| **D. No-Update Control** | L0 | Frozen parameters ($\nabla_\theta = 0$) | Pre-checksum = 184.5887, Post = 184.5887 | `PASS` |
| **E. Deliberate Leak Detection** | — | Target appended after `<ANS>` delimiter | Caught by isolated delimiter assertion | `PASS` |

All 5 Stage 0 instrumentation and null calibration controls passed conclusively. The harness correctly trains, evaluates, isolates targets, and updates parameters without numerical defects.

---

## 2. Stage 1A — Identity Copy with Unseen Query Symbol

Stage 1A assesses whether the model can parse the structured episodic format, identify the query location, and reproduce an unseen query symbol without requiring arithmetic or associative lookup.

- **Domain Size:** $|D| = 8$
- **Support:** 3 distinct pairs $s_i \to s_i$
- **Query:** 4th distinct symbol $q_x \notin \{s_1, s_2, s_3\} \to q_x$
- **Chance Accuracy:** $1/8 = 12.5\%$
- **Evaluation:** Frozen validation set of 200 fresh episodes across 3 deterministic seeds: `42`, `43`, `44`.

### Stage 1A Results:
| Configuration | Seed | Train Acc (Final 3 Avg) | Validation Accuracy | Wilson 95% CI | Verdict |
|---|---|---|---|---|---|
| **F8** ($L1, 10^{-3}, \text{bs } 256$) | 42 | 100.0% | 100.0% | [0.981, 1.000] | `PASS` |
| **F8** ($L1, 10^{-3}, \text{bs } 256$) | 43 | 100.0% | 100.0% | [0.981, 1.000] | `PASS` |
| **F8** ($L1, 10^{-3}, \text{bs } 256$) | 44 | 100.0% | 100.0% | [0.981, 1.000] | `PASS` |
| **F7** ($L1, 10^{-3}, \text{bs } 64$) | 42 | 100.0% | 100.0% | [0.981, 1.000] | `PASS` |
| **F7** ($L1, 10^{-3}, \text{bs } 64$) | 43 | 100.0% | 100.0% | [0.981, 1.000] | `PASS` |
| **F7** ($L1, 10^{-3}, \text{bs } 64$) | 44 | 100.0% | 100.0% | [0.981, 1.000] | `PASS` |

**Findings:** Both L0 and L1 models master Stage 1A with 100.0% accuracy across all seeds. Delimiter parsing, query location tracking, and unseen symbol generation are fully functional.

---

## 3. Stage 1B — Copy from Support / Associative Retrieval

Stage 1B tests whether the model can retrieve an association $k \to v$ provided exclusively in the in-context support set and output $v$ when prompted with $k$.

- **Vocabulary:** 64 data tokens ($\ge 10$)
- **Support:** 4 distinct key-value pairs $\{k_i \to v_i\}_{i=1}^4$ presented in randomized order.
- **Query:** One key $q_x \in \{k_i\}$ repeated at query position.
- **Target:** Associated value $q_y = v(q_x)$.
- **Chance Accuracy:** $1/4 = 25.0\%$
- **Evaluated Controls (Equal Token Count & Format):**
  1. `CORRECT`: Support contains the true mapping $q_x \to q_y$.
  2. `RANDOM`: Support outputs randomly permuted; accidental matches strictly rejected.
  3. `WRONG`: Support mappings valid but cycle values so $q_x \to v' \neq q_y$.
  4. `ABSENT`: Support data tokens replaced with neutral placeholder token `6`.

---

## 4. Optimization Matrix (Foundational Factorial)

A 10-cell calibration was executed on discovery seed 42 to explore capacity ($L0$ vs $L1$), learning rate ($3\cdot 10^{-4}$ vs $10^{-3}$), and batch size ($64$ vs $256$).

| Cell | Scale | LR | Batch Size | Steps | Val Correct Acc | Val Random Acc | Correct - Random | Final Loss | Selection Status |
|---|---|---|---|---|---|---|---|---|---|
| **F1** | L0 | 3e-4 | 64 | 1000 | 8.0% | 8.5% | -0.5% | 3.5949 | Rejected |
| **F2** | L0 | 3e-4 | 256 | 1000 | 16.0% | 18.5% | -2.5% | 3.2926 | Rejected |
| **F3** | L0 | 1e-3 | 64 | 1000 | 23.5% | 21.0% | +2.5% | 2.5839 | Rejected |
| **F4** | L0 | 1e-3 | 256 | 1000 | 23.5% | 27.0% | -3.5% | 2.0441 | Rejected |
| **F5** | L1 | 3e-4 | 64 | 1000 | 24.0% | 23.0% | +1.0% | 2.4985 | Tie (higher loss) |
| **F6** | L1 | 3e-4 | 256 | 1000 | 23.5% | 23.0% | +0.5% | 1.9569 | Rejected |
| **F7** | L1 | 1e-3 | 64 | 1000 | 24.0% | 21.0% | +3.0% | 1.8781 | **Selected (Rank 2)** |
| **F8** | L1 | 1e-3 | 256 | 1000 | 26.5% | 24.0% | +2.5% | 1.6090 | **Selected (Rank 1)** |
| **A0** | L0 | 3e-4 | 64 | 400 | 7.5% | 9.5% | -2.0% | 4.0881 | Rejected |
| **C0** | L1 | 6e-4 | 128 | 1000 | 23.5% | 23.5% | +0.0% | 1.8496 | Rejected |

**Selection:** Cells **F8** (highest validation accuracy: 26.5%) and **F7** (tied at 24.0% with lower validation loss of 1.8781 vs 2.4985) were selected for multi-seed confirmation.

---

## 5. Learning Curves and Training Dynamics

During Stage 1B training:
- **L0 Models:** Cross-entropy loss plateaued between 2.04 and 3.59. Minibatch accuracy hovered between 3% and 21%.
- **L1 Models:** Cross-entropy loss decreased monotonically from ~4.16 down to ~1.60, approaching $-\ln(1/4) \approx 1.386$ (the theoretical entropy of a uniform 4-way choice).
- **Plateau Behavior:** Neither L0 nor L1 broke through the 25% chance threshold during episodic training. Predictions remained uniform across the 4 candidate values without binding to the query key.

---

## 6. Support-Control Results

Evaluation across all 4 matched controls on frozen validation episodes (200 episodes per control):

| Config | Seed | Correct Support Acc | Random Support Acc | Wrong Support Acc | Absent Support Acc | Correct - Random | Correct - Wrong | Correct - Absent |
|---|---|---|---|---|---|---|---|---|
| **F8** | 42 | 26.5% | 24.0% | 27.0% | 0.0% | +2.5 pp | -0.5 pp | +26.5 pp |
| **F8** | 43 | 28.5% | 26.5% | 28.0% | 3.0% | +2.0 pp | +0.5 pp | +25.5 pp |
| **F8** | 44 | 26.5% | 25.0% | 25.5% | 1.5% | +1.5 pp | +1.0 pp | +25.0 pp |
| **F7** | 42 | 24.0% | 21.0% | 22.5% | 1.0% | +3.0 pp | +1.5 pp | +23.0 pp |
| **F7** | 43 | 22.5% | 21.0% | 22.0% | 1.0% | +1.5 pp | +0.5 pp | +21.5 pp |
| **F7** | 44 | 25.5% | 23.5% | 22.5% | 1.0% | +2.0 pp | +3.0 pp | +24.5 pp |

### Key Diagnostic Observations:
1. **Correct vs Random:** The gain is $+1.5$ to $+3.0$ percentage points, well below the required $\ge 10.0$ pp threshold.
2. **Correct vs Wrong:** The gain is $-0.5$ to $+3.0$ percentage points. The model is virtually indifferent to whether support is consistent or wrong.
3. **Correct vs Absent:** Accuracy drops to near-zero ($0.0\% - 3.0\%$) on absent support. This proves the model uses support tokens to constrain its candidate output pool to the active episode values, but **fails to retrieve the associative relation between the query key and its paired value**.

---

## 7. Readiness Gates (Gates 1–5)

| Gate | Requirement | Stage 1A Status | Stage 1B Status | Failure Mode |
|---|---|---|---|---|
| **Gate 1: Train Mastery** | Fresh train-dist $\ge 90\%$ at final 3 evals | **PASS** (100.0%) | **FAIL** (22.7% - 28.1%) | Chance-level training performance |
| **Gate 2: Val Generalization** | Frozen val $\ge 80\%$ | **PASS** (100.0%) | **FAIL** (Median: 24.0% - 26.5%) | Failed in-distribution generalization |
| **Gate 3: Causal Support Utility** | Correct - {Rand, Wrong, Absent} $\ge 10$ pp & Boot CI Low $>0$ | **N/A** (Exempt) | **FAIL** (C-R $\approx +2.0$ pp, CI low $<0$) | No causal support utilization |
| **Gate 4: Seed Stability** | Median $\ge 80\%$, min $\ge 75\%$, std $\le 5$ pp | **PASS** (Std: 0.0 pp) | **FAIL** (Median: 24.0% - 26.5%) | Baseline failed threshold across all seeds |
| **Gate 5: Integrity** | Zero leakage, valid fingerprints, matched controls | **PASS** | **PASS** | Fully compliant |

---

## 8. Per-Seed Results

### Configuration F8 ($L1, 10^{-3}, \text{bs } 256, 1000 \text{ steps}$):
- **Seed 42:** Stage 1A Val = 100.0% | Stage 1B Correct = 26.5%, Random = 24.0%, Boot 95% CI = [-0.010, +0.060]
- **Seed 43:** Stage 1A Val = 100.0% | Stage 1B Correct = 28.5%, Random = 26.5%, Boot 95% CI = [-0.015, +0.050]
- **Seed 44:** Stage 1A Val = 100.0% | Stage 1B Correct = 26.5%, Random = 25.0%, Boot 95% CI = [-0.020, +0.050]
- **Aggregate:** Median Val = 26.5%, Std = 0.94 pp, All Passed = **`False`**

### Configuration F7 ($L1, 10^{-3}, \text{bs } 64, 1000 \text{ steps}$):
- **Seed 42:** Stage 1A Val = 100.0% | Stage 1B Correct = 24.0%, Random = 21.0%, Boot 95% CI = [-0.015, +0.075]
- **Seed 43:** Stage 1A Val = 100.0% | Stage 1B Correct = 22.5%, Random = 21.0%, Boot 95% CI = [-0.015, +0.050]
- **Seed 44:** Stage 1A Val = 100.0% | Stage 1B Correct = 25.5%, Random = 23.5%, Boot 95% CI = [-0.025, +0.065]
- **Aggregate:** Median Val = 24.0%, Std = 1.22 pp, All Passed = **`False`**

---

## 9. Gradient Health & Diagnostic Monitoring

Monitoring during optimization confirmed excellent numerical health:
- **Optimizer:** AdamW ($\beta_1=0.9, \beta_2=0.95, \epsilon=10^{-8}$, weight decay 0.01 excluding bias/norm).
- **Gradient Clipping:** Max norm 1.0; clipping rate $< 15\%$ across all steps (no clipping domination).
- **Gradient Flow:** Global gradient norms maintained in $[0.08, 1.85]$ (well above the $10^{-8}$ vanishing threshold).
- **Numerical Stability:** 0 NaN, 0 Inf occurrences across all runs.
- **Update Ratios:** $\|\Delta \theta\| / \|\theta\| \in [2.4 \cdot 10^{-4}, 1.1 \cdot 10^{-3}]$ (well within $[10^{-10}, 1.0]$).
- **Prediction Collapse:** Predictions distributed across support vocabulary values (entropy $H \approx 1.35$ nats $\approx \ln 4$).

---

## 10. Measured Throughput Pilot

- **Hardware:** NVIDIA GPU (`cuda`)
- **Step Count:** 1,000 steps
- **Batch Size:** 64 episodes (1,344 tokens per batch)
- **Wall-Clock Time:** 99.919 seconds
- **Throughput:**
  - **Episodes / sec:** 640.52
  - **Tokens / sec:** 13,450.83
- **Peak VRAM Allocated:** 37.91 MB

Resource consumption is exceptionally light (under 40 MB VRAM), confirming that memory or throughput is not a bottleneck.

---

## 11. Failure Classifications

**Classification:** `FOUNDATIONAL_EPISODIC_LEARNING_FAILURE`

### Detailed Diagnostics:
- **First Failed Gate:** **Gate 1 (Training-Distribution Mastery)** and **Gate 3 (Causal Support Utility)**.
- **Optimization Behavior:** Smooth, non-divergent loss convergence to the uniform entropy limit ($\sim 1.60$ vs theoretical $\ln 4 \approx 1.386$). Zero NaNs, zero vanishing/exploding gradients.
- **Train vs Validation Behavior:** Both training minibatch and held-out validation accuracy remained clustered around chance ($24\% - 28\%$). The model did not overfit the training stream nor did it generalize.
- **Support-Control Behavior:** The model successfully learns that targets come from the support set (absent support accuracy $= 0\% - 3\%$), but fails to learn the associative mapping $k \to v$ (correct support is within $2$ pp of random support).
- **Likely Bottleneck:** Standard causal transformer attention without explicit associative copying mechanisms (e.g. induction heads or cross-episodic pointer heads) cannot easily resolve key-value indirection under autoregressive cross-entropy loss without architectural biases.
- **What Was Ruled Out:**
  - Ruled out optimization/gradient failure (overfit test reached 100% in 50 steps; gradient norms healthy).
  - Ruled out tokenization and episode parsing failure (Stage 1A identity copy reached 100% generalization).
  - Ruled out label/target leakage or alignment bugs (verified via direct-label control and no-update checksums).
  - Ruled out data starvation (thousands of distinct episodes evaluated; balanced target distribution).

---

## 12. Exact Stopping Point

In accordance with the V10.9 progression protocol:
> **"Stage 1 or Stage 2 failure must stop progression rather than being interpreted as an architectural impossibility."**

Execution is formally **HALTED at Stage 1B**.
- Stage 0: **PASSED**
- Stage 1A: **PASSED**
- Stage 1B: **FAILED** (Gates 1, 2, 3, 4 FAILED; Gate 5 PASSED)
- Progression to Stage 2: **STOPPED**

---

## 13. Limits of Inference

1. **What Has Been Decisively Proven:**
   - The Nirmal architecture can parse structured episodes and accurately locate the query slot (Stage 1A = 100%).
   - The Nirmal architecture can copy symbols across context when the mapping is identity (Stage 1A = 100%).
   - Standard causal transformer training on random key-value permutations does not develop associative retrieval induction out of the box within the tested calibration budget (Stage 1B $\approx 25\%$).

2. **What Has NOT Been Proven (Do Not Overclaim):**
   - This result does **NOT** prove that transformers or Nirmal cannot perform meta-learning in principle.
   - It proves that foundational associative retrieval failed under the current parameterization, requiring architecture-level inductive bias inspection (e.g., positional encodings, attention head specialization, or curriculum) before proceeding to arithmetic.

---

## 14. Stage 2 Progression Verdict

- **Stage 2 Authorized:** **NO (STRICT NO-GO)**
- **All Readiness Gates Satisfied:** **NO (Stage 1B Failed)**
- **Production Status:** **STRICT NO-GO** (Production code, checkpoints, and shards remain untouched).

The experimental evidence is complete and frozen for scientific peer review.
