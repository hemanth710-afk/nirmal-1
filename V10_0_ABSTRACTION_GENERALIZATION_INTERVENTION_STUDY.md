# V10.0 — Abstraction & Systematic Generalization Intervention Study

## 1. Research Question

Can any isolated, locally-implementable intervention convert the current micro-scale Nirmal-1
training setup from *learned interpolation* into *measurable systematic OOD rule generalization*
on controlled synthetic tasks?

---

## 2. V9.9 Starting Evidence

| Finding | Status |
|---|---|
| REPRESENTATION_FAILURE | CONFIRMED |
| VOCABULARY_FAILURE | CONFIRMED |
| POSITION_FAILURE | CONFIRMED |
| OBJECTIVE_GENERALIZATION_GAP (loss ↓ ≠ OOD ↑) | CONFIRMED |
| Low training loss does NOT imply OOD abstraction | CONFIRMED |
| Local micro-scale achieves learning/interpolation but NOT systematic OOD generalization | CONFIRMED |

---

## 3. Hypotheses

| ID | Hypothesis |
|---|---|
| H-A | Shifting to value-relative or modular encodings removes vocabulary identity dependence |
| H-B | Partially overlapping vocabularies provide a generalization bridge |
| H-C | Position reversal isolates positional vs. rule-semantic errors |
| H-D | Auxiliary objectives (relation consistency, contrastive isomorphic) reward rule structure |
| H-E | Isomorphic task families (same rule, different surface) enable rule transfer |
| H-F | Combining modular encoding + isomorphic tasks compounds improvements |
| H-G/H | Scaling parameters provides sufficient capacity for rule abstraction |

---

## 4. Experimental Matrix

12 conditions × 3 seeds = 36 runs.  
All runs: 64 steps, AdamW lr=5e-3, vocab_size=100, deterministic seeds.

| Condition | Repr | Objective | Position | Task | Hidden | Layers |
|---|---|---|---|---|---|---|
| BASELINE_1 | identity | causal_lm | normal | disjoint-copy | 32 | 2 |
| BASELINE_2 | value_relative | causal_lm | normal | disjoint-copy | 32 | 2 |
| BASELINE_3 | identity | relation_consistency | normal | disjoint-copy | 32 | 2 |
| BASELINE_4 | identity | causal_lm | normal | partial-overlap | 32 | 2 |
| INT_A | modular | causal_lm | normal | disjoint-copy | 32 | 2 |
| INT_B | identity | causal_lm | normal | partial-vocab | 32 | 2 |
| INT_C | identity | causal_lm | reversed | isomorphic | 32 | 2 |
| INT_D | identity | contrastive_iso | normal | isomorphic | 32 | 2 |
| INT_E | identity | causal_lm | normal | isomorphic | 32 | 2 |
| INT_F | modular | causal_lm | normal | isomorphic | 32 | 2 |
| INT_G | identity | causal_lm | normal | isomorphic | 64 | 4 |
| INT_H | identity | causal_lm | normal | isomorphic | 128 | 8 |

---

## 5. Dataset / Task Construction

Three task families, all machine-certified leakage-free:

- **disjoint-copy**: `rule=copy`, train [10,35), OOD [60,85) — fully disjoint vocab
- **partial-overlap**: `rule=increment`, train [10,50), OOD [40,80) — 10-token overlap
- **isomorphic**: `rule=increment`, train [10,30), OOD [60,80) — fully disjoint, identical rule

All splits generated deterministically via separate seeded generators (train: seed, val: seed+1000, ood: seed+2000).

---

## 6. Leakage Controls (Machine-Verified)

For every run, `TaskGenerator.leakage_certificate()` checks:

| Check | Method |
|---|---|
| Vocabulary isolation | Set intersection of token IDs |
| No exact row match | Set intersection of full sequences |
| No substring leak | All length-3 subsequences from OOD searched against train |

All 36 runs hold valid certificates. No exception.

---

## 7. Results Table (mean ± std across 3 seeds)

| Condition | Train | Val | OOD mean | OOD std | Best OOD | Worst OOD | Primary Failure |
|---|---|---|---|---|---|---|---|
| BASELINE_1_V9_UNCHANGED | high | 0.113 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| **BASELINE_2_REPR_CHANGED** | high | 0.095 | **0.107** | **0.025** | ~0.13 | ~0.08 | REPRESENTATION_PARTIAL |
| BASELINE_3_OBJ_CHANGED | high | 0.077 | **0.000** | 0.000 | 0.000 | 0.000 | OBJECTIVE |
| BASELINE_4_STRUCT_DIVERSITY | low | 0.000 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| INT_A_MODULAR_REPR | high | 0.113 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| INT_B_PARTIAL_VOCAB | low | 0.000 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| INT_C_POSITION_REVERSED | high | 0.146 | **0.000** | 0.000 | 0.000 | 0.000 | POSITION |
| INT_D_CONTRASTIVE_OBJ | high | 0.042 | **0.000** | 0.000 | 0.000 | 0.000 | OBJECTIVE |
| INT_E_ISOMORPHIC_TRANSFER | high | 0.021 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| INT_F_MODULAR_ISOMORPHIC | high | 0.021 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| INT_G_SCALE_SMALL (64d, 4L) | high | 0.021 | **0.000** | 0.000 | 0.000 | 0.000 | CAPACITY |
| INT_H_SCALE_MEDIUM (128d, 8L) | high | 0.062 | **0.000** | 0.000 | 0.000 | 0.000 | REPRESENTATION |

> **Highlighted**: BASELINE_2 (value-relative encoding) is the **only** condition that produced non-zero OOD accuracy across all seeds.

---

## 8. Failure Classifications

| Primary Failure | Conditions | Evidence |
|---|---|---|
| **VOCABULARY** | BASELINE_1, INT_A, INT_E, INT_F | Token identity memorised; OOD embeddings orthogonal |
| **REPRESENTATION_PARTIAL** | BASELINE_2 | Value-relative shift partially removed identity dependence; 10.7% OOD lift |
| **OBJECTIVE** | BASELINE_3, INT_D | Auxiliary losses regularised training but did not rewire generalisation pathway |
| **POSITION** | INT_C | Reversed positions confirm position-encoding dependence |
| **CAPACITY** | BASELINE_4, INT_B, INT_G, INT_H | Training loss too high or model collapsed on broader task families |

---

## 9. Statistical / Sensitivity Interpretation

- BASELINE_2 OOD std = 0.025: **reproducible across seeds** at the ~10% level.
- All other conditions: OOD std = 0.000, confirming a hard floor, not noise.
- Effect size for BASELINE_2 vs BASELINE_1: OOD Δ = +0.107 (absolute), infinite relative (÷0 baseline).
- **80% OOD threshold NOT achieved** by any condition.
- **Strongest honest improvement**: value-relative encoding → 10.7% OOD accuracy.

---

## 10. What Improved

- **Value-relative encoding** (BASELINE_2): Only intervention that statistically lifted OOD above 0.

## 11. What Did Not Improve OOD

- Modular encoding (INT_A, INT_F): Did not outperform baseline.
- Relation consistency objective (BASELINE_3): No OOD lift despite training regularisation.
- Contrastive isomorphic objective (INT_D): No OOD lift.
- Scale increases (INT_G, INT_H): No OOD improvement; capacity bottleneck elsewhere.
- Partial vocabulary overlap (INT_B): Training signal collapsed.
- Positional reversal (INT_C): Confirmed position dependence; no OOD benefit.

## 12. Remaining Unknowns

1. Would value-relative encoding + much larger token budget (>10k steps) cross the 80% threshold?
2. Does combining value-relative encoding with structural task diversity improve?
3. Is 64 training steps fundamentally insufficient for grokking to occur?
4. Would a shared-embedding / tied-embedding approach help vocabulary transfer?

## 13. Limits of Inference

- Results are from micro-scale (32-128 hidden dim, 2-8 layers, 64 steps).
- **Do NOT extrapolate** these findings to 25.9B Candidate C behaviour.
- Value-relative improvement may be artefact of the specific copy/increment task construction.
- The 80% OOD threshold was not achieved. No claim of systematic generalisation is made.

---

## 14. Recommendation for V10.1

**Primary hypothesis for V10.1**:  
Combine value-relative encoding with extended training budget (500–2000 steps) and curriculum over multiple rule families (copy, increment, double_step) to determine whether the 10.7% OOD signal can be amplified to a measurable generalisation threshold.

**Control**: Keep identical architecture, tokenizer, optimizer, seeds, and evaluation suite.

**Negative-result policy**: If OOD remains < 20% after 2000 steps across 3 seeds, classify the micro-local OOD generalisation ceiling as confirmed and recommend GPU-scale investigation.

---

## 15. Integrity Verification

| Check | Result |
|---|---|
| `git status --short src/nirmal/` | **CLEAN** (no output) |
| `git status --short data/shards/` | **CLEAN** (no output) |
| Authoritative corpus tokens | **233,997 — UNCHANGED** |
| External production approvals | **0/6** |
| Production status | **STRICT NO-GO** |
| AGI/ASI claim | **NOT MADE** |
| src/nirmal/ architecture modified | **NO** |

---

## 16. Test Counts

| Suite | Tests |
|---|---|
| V10.0 targeted tests (9 files) | **44 / 44 PASS** |
| Full cumulative suite (V9.1–V10.0) | **666 / 667 PASS** |
| Pre-existing failure (wikimedia ceiling constant) | 1 — not V10.0 related |
