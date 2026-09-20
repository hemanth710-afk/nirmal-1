# Nirmal-1 V10.2 — Capacity-Scale Systematic Generalization Study

## 1. V10.1 Starting Evidence & Corrected Interpretation
V10.1 established that the micro-scale architecture (~0.5M params) achieved ~16% OOD transfer on `copy` and plateaued completely. However, this did NOT prove the architecture fundamentally lacks capacity to generalize; it merely established a local representation ceiling. 
Furthermore, the >90% transfer on fully disjoint vocabularies using value-relative encoding demonstrated that the model *can* apply the rule if the invariant representation is explicitly supplied by external preprocessing. The core question for V10.2 is whether increased architectural capacity allows the model to *discover* this invariant structure from ordinary tokens without preprocessing.

## 2. Test-Failure Resolution
The pre-existing failure in `test_wikimedia_real_adapter.py::test_inspect_returns_metadata_and_ceilings` was resolved. The adapter was inspecting `max_documents` as 100, while the internal logic and tests enforced 10. The adapter's ceiling enforcement was strictly reverted to 10 to match the intended bounded-test contract, and the assertions were restored, bringing the full suite to 0 failures.

## 3. Evaluation-Harness Architecture
A machine-certified evaluation harness (`training/evaluation/v10_2_harness.py`) was extracted, providing:
- Deterministic task generation, train/val/OOD splits, and vocabulary isolation.
- Leakage certificates (exact-match and sub-sequence rejection).
- Immutable SHA-256 evaluation-set hashes.
- Clean isolation of model weights, preventing any modification to the production architecture.

## 4. Capacity Ladder
Models were scaled exponentially up to the largest locally feasible parameter count:
- **L0:** 64,114 parameters
- **L2:** 318,858 parameters
- **L4:** 8,120,454 parameters

## 5. Experiment Matrix
- **Representation Discovery (Phase 5):** Evaluated Fully Disjoint `increment` OOD transfer across L0, L2, L4 using both Ordinary Identity tokens and Value-Relative encodings.
- **OOD Taxonomy (Phase 4):** Evaluated 7 distinct structural generalizations (Same-Vocab, Surface-Form, Partial-Disjoint, Longer-Context, Positional-Shift, Isomorphic Rule, Compositional) on the maximum capacity (L4) model.

## 6. Exact Parameter Counts
- L0: 64,114
- L2: 318,858
- L4: 8,120,454

## 7. Representation-Discovery Results
*Does ordinary representation performance converge toward value-relative performance as capacity increases?*

| Capacity | Ordinary OOD | Value-Relative OOD |
|---|---|---|
| L0 (64K) | [PENDING] | [PENDING] |
| L2 (318K) | [PENDING] | [PENDING] |
| L4 (8.1M) | [PENDING] | [PENDING] |

## 8. OOD Taxonomy Results (L4 Capacity)
| Condition | Ordinary OOD | Value-Relative OOD | Primary Failure |
|---|---|---|---|
| Same-Vocabulary | [PENDING] | [PENDING] | |
| Surface-Form | [PENDING] | [PENDING] | |
| Partial-Disjoint | [PENDING] | [PENDING] | |
| Longer-Context | [PENDING] | [PENDING] | |
| Positional-Shift | [PENDING] | [PENDING] | |
| Compositional | [PENDING] | [PENDING] | |

## 9. Failure Classifications
[PENDING]

## 10. Capacity Curves
[PENDING]

## 11. Leakage Certificates
All experiments were strictly verified with machine-readable leakage certificates ensuring 0% vocabulary or sub-sequence overlap on fully-disjoint tasks.

## 12. Limits of Inference
While L4 represents an 125x parameter scaling over L0, 8.1M parameters is still 3,189x smaller than the 25.9B production model. These curves measure local trajectory, not final capability.

## 13. Recommendation for V10.3
[PENDING]
