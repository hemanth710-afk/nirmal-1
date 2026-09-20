# Nirmal-1 V10.10 — Associative Binding Calibration Study

**Research status:** IMPLEMENTED / FINAL CAMPAIGN NOT RUN  
**Production status:** **STRICT NO-GO**  
**Candidate C:** unchanged, 25,908,188,576-parameter production target  
**Authoritative corpus:** 233,997 tokens, unchanged  
**External production approvals:** 0/6  
**Phase F:** prohibited unless a separate activation artifact passes

> **Central question:** Can Nirmal learn `KEY → VALUE` from episode-local support examples and use the association to answer a query?

No result in this document authorizes V10.11, production training, or a production architecture change.

## 1. V10.9 post-mortem

V10.9 Stage 0 passed: L0/L1 one-batch overfit reached 100%, direct-label sanity reached 100%, the label-permutation null remained near chance, the no-update control passed, and gradients and parameter updates were healthy. Stage 1A identity copy reached 100% train and validation accuracy across three seeds, including unseen query symbols. These results establish working labels, loss, optimization, answer positioning, and simple episodic symbol reproduction.

V10.9 Stage 1B remained near its declared 25% support-selection chance level. Correct support failed to reliably beat random or wrong support. The valid conclusion is narrow: **the tested configuration did not establish reliable episode-local associative binding**. It does not show that transformers, attention, Nirmal, or Candidate C are fundamentally incapable of binding.

## 2. Binding definition

For each episode, sample distinct keys \(K_E=\{k_1,\ldots,k_n\}\) and a fresh mapping \(m_E:K_E\to\{v_0,v_1,v_2,v_3\}\). Present support pairs \((k_i,m_E(k_i))\), then query one support key \(q\). The target is \(m_E(q)\). Mappings are independently resampled and satisfy \(P(m_E(k)=v_j\mid k)=1/4\), preventing a persistent global dictionary from outperforming chance.

Representation, retrieval, and generalization are separate. V10.10 primarily tests whether the association is represented and behaviorally retrieved. Hidden-state and attention diagnostics are secondary; the decisive result is causal behavior under matched support interventions.

## 3. Hypotheses and candidate causes

- **H1 Serialization:** pair boundaries or role encoding currently obscure the association.
- **H2 Query structure:** a dedicated query state improves retrieval.
- **H3 Difficulty:** B0/B1 can be learned even if B2 cannot.
- **H4 Optimization:** binding emerges later than identity copying.
- **H5 Training signal:** query-only loss is too sparse at the tested scale.
- **H6 Context access:** pair information is represented but not selected by the query.
- **H7 Capacity:** a larger matched research model may pass after a smaller model plateaus.
- **H8 Interference:** competing pairs, distance, or distractors create the first boundary.
- **H0:** no valid bounded condition solves the simplest binding task.

Candidate causes are discriminated by matched latent episodes. A format diagnosis requires a query-position-matched gain. An optimization diagnosis requires a registered step/LR gain. A capacity diagnosis requires smaller-model saturation. A context-access diagnosis requires decodable pair representations but weak native causal access.

## 4. Primary benchmark

The primary benchmark uses at least 32 single-token keys, exactly four single-token values, and distinct structural tokens. Key and value vocabularies are disjoint. B2 uses four distinct keys and a random bijection to the four values. The target, query-pair position, and support order are balanced. Output prediction is restricted to the four registered value classes, making chance exactly 25%.

Training contains correct support only. Controls are evaluation interventions and do not carry condition labels that the model could exploit.

## 5. Control set and counterfactuals

Each base episode generates five evaluation realizations:

1. **Correct:** original mapping.
2. **Random-deranged:** derange the same support-value multiset and guarantee that the query association changes.
3. **Targeted-wrong:** swap the query value with one distractor value while retaining all other associations.
4. **Placeholder absent:** replace support data tokens with neutral placeholders while preserving length and query position.
5. **Unpaired-bag absent:** preserve support key/value token counts but destroy pair boundaries.

The target remains the original target in every condition. Targeted-wrong evaluation additionally reports accuracy for the presented counterfactual and changes in the original and counterfactual logits. From B1 upward, correct, random, and wrong support retain the same key/value token multiset.

## 6. Phase 0 — Legacy continuity

Replay exactly one archived V10.9 F8 Stage 1B condition: L1, peak LR 0.001, batch 256, 1,000 steps, seed 42, archived serialization/generator, and archived validation seed. Compare correct, random, wrong, and final loss with preregistered tolerances. Failure produces `REPOSITORY_OR_CONFIGURATION_DRIFT` and blocks experimental phases. The implementation must not silently repair or replace the legacy condition.

## 7. Phase A — Serialization and query study

Pair formats:

- F-A: `KEY VALUE`
- F-B: `KEY <SEP> VALUE`
- F-C: `KEY <MAP> VALUE`
- F-D: `<KEY> KEY <VALUE> VALUE`

Query formats:

- Q-A: `KEY <MAP> <ANS>`
- Q-B: `<QRY> KEY <ANS>`
- Q-C: `<LOOKUP> KEY <ANS>`

Discovery uses one seed, 2,000 steps, one fixed model/optimizer/data stream, all four pair formats with Q-B, then query-format follow-up on the promoted format only. At most two combined candidates are promoted to three-seed confirmation. Query-position-matched filler controls prevent shorter serialization from masquerading as a format advantage. Natural-language instructions are not part of the primary benchmark.

## 8. Phase B — Difficulty ladder

- **B0:** one pair; prerequisite only because the sole value can be copied.
- **B1:** two pairs; first level requiring selection among competing values.
- **B2:** four distinct keys and four distinct values; primary foundational acceptance benchmark.
- **B3:** B2 plus four explicitly marked distractor triples.
- **B4:** eight valid pairs with each value appearing exactly twice.
- **B5:** the same B2 mapping presented twice in independently shuffled order.

No level advances until the previous level's registered gate passes. B3–B5 are stress tests and are not required for foundational establishment.

For B2, compare curriculum continuation against a matched from-scratch run. Curriculum pass plus scratch fail is `curriculum-dependent`; both pass means directly learnable; both fail means binding is not established.

## 9. Phase C — Optimization and objectives

A continuous 10,000-step run is evaluated at 400, 1,000, 2,000, 5,000, 8,000, and 10,000 updates. Poor accuracy does not trigger early stopping. Log fresh train accuracy, all validation conditions, counterfactual following, gradient norm, clipping, update ratio, entropy, output distribution, and position-conditioned accuracy.

Learning-rate discovery tests 0.5×, 1.0×, and 2.0× the exact V10.9 peak LR, using the same schedule, warmup, batch, stream, and initialization where deterministic. Only the best schedule is promoted.

Objectives are sequential:

- **O-A:** query-answer loss only.
- **O-B:** O-A plus 0.25-weight auxiliary query for a different support key.
- **O-C:** O-A plus 0.10-weight support-pair-index matching. The index target depends only on query-key identity and support position, never value or answer.

O-C is conditional and cannot be activated automatically.

## 10. Phase D — Capacity

Required matched scales are L0 and L1. The repository's approximately 1M-parameter L3 builder is reported as the optional V10.10 L2 research control to avoid changing existing production code or builder semantics. All size comparisons match optimizer, LR, schedule, batch, steps, tokenizer, precision, episode order, and evaluation manifests across three seeds.

The optional size may run only if L1 beats L0 by at least 10 points, reaches 60–80% after plateau, or shows registered size-dependent diagnostic improvement. A model is step-saturated only when the 8,000-to-10,000-step accuracy gain is under two points and relative loss improvement is under 1%.

## 11. Phase E — Representation and context diagnostics

Capture hidden states without changing production files. Compare query-key similarity with matching and nonmatching support keys. Use support-value or pair-end states for pair probes because a causally earlier key state cannot see a later value. Frozen linear probes use separate mappings and never update Nirmal weights.

Report layer-wise value decodability and, where existing attention layers permit, attention mass to matching keys, matching values, complete matching pairs, and distractors. Attention visualization is not proof.

Evaluation-only causal diagnostics block or ablate the correct pair, one distractor pair, or all support while preserving sequence length, positions, query, and target. For the hybrid architecture, reports must distinguish true attention-layer masking from whole-model token ablation; DeltaNet access must not be silently described as blocked when it is not.

## 12. Phase F — Conditional architecture intervention

Phase F is not implemented or activated by default. It requires failed B0/B1 non-architectural controls, healthy and saturated L1 optimization, decodable pair representations, a specific `CONTEXT_ACCESS_LIMIT` diagnosis, and a separate preregistered activation artifact.

The only permitted research intervention is a learned query-to-prior-context attention readout with no hard-coded equality, pair index, dictionary, symbolic lookup, external memory, target feature, or direct answer path. It requires unmodified and parameter-matched controls and may never propagate into Candidate C.

## 13. Readiness gates

- **Gate 0:** deterministic oracle, valid immutable hashes, no split collision, target balance, valid controls, no answer leakage, and no test-based checkpoint selection.
- **Gate 1:** fresh train-distribution accuracy ≥90% at the final three scheduled evaluations.
- **Gate 2:** correct-support validation ≥80%; for B2 every seed must independently reach 80%.
- **Gate 3:** every final seed has correct-minus-random, correct-minus-wrong, and correct-minus-stronger-absent ≥10 points; Holm-adjusted paired-bootstrap lower bounds are positive.
- **Gate 4:** exactly three seeds, every seed passes Gates 1–3, validation standard deviation ≤5 points, and no negative correct-control effect.
- **Gate 5:** for B2, every query-pair position ≥70%, position gap ≤10 points, and support reversal/shuffle accuracy change ≤5 points.

## 14. Statistical methodology

Use at least 10,000 frozen base episodes per seed and condition for confirmation. Report counts, accuracy, chance, and Wilson 95% intervals. Contrasts use at least 10,000 paired bootstrap resamples of whole base-episode control sets. Apply Holm–Bonferroni to the random, wrong, and stronger-absent contrasts. Report every seed, mean, median, standard deviation, and worst seed. Three seeds are replications; pooled episode count cannot hide a failed seed.

Discovery results are not confirmatory. All registered runs, including failures, must remain in the ledger. OOD or control metrics cannot select checkpoints.

## 15. Deterministic classifications

Classification is priority ordered and machine evaluated:

1. `INVALID_EXPERIMENT`
2. `TASK_CONSTRUCTION_FAILURE`
3. `SERIALIZATION_LIMIT`
4. `OPTIMIZATION_LIMIT`
5. `CAPACITY_LIMIT`
6. `REPRESENTATION_LIMIT`
7. `CONTEXT_ACCESS_LIMIT`
8. `PARTIAL_ASSOCIATIVE_BINDING`
9. `ASSOCIATIVE_BINDING_FAILURE`
10. `ASSOCIATIVE_BINDING_ESTABLISHED`

`ASSOCIATIVE_BINDING_ESTABLISHED` requires a complete B2 Gate 0–5 pass. Lower-level success, probe accuracy, attention selectivity, or one successful seed cannot produce this classification.

## 16. Leakage certificate and immutable benchmark

Use separate seed namespaces for initialization, training, fresh-train evaluation, validation, final test, controls, probes, and bootstrap. Fingerprints include benchmark version, selected vocabulary, mapping, support order, query, target, serialization, and control. Instance and order-invariant fingerprints are audited. Low-cardinality B0/B1 semantic repetition is reported rather than misrepresented as OOD generalization; B2 is the primary collision-controlled benchmark.

Each benchmark manifest records generator version/hash, tokenizer/vocabulary hashes, seeds, episode counts, serialization, controls, per-file SHA-256, and a top-level SHA-256. Evaluation aborts on mismatch.

Key-only and position-only diagnostics must remain at chance. A positive diagnostic invalidates the affected benchmark until a new version is generated.

## 17. Compute ledger and campaign cap

The planned core study is approximately 0.8–1.3B tokens and 1–3 PFLOP. The optional B3–B5, objective rescue, optional capacity control, and conditional intervention cap is approximately 1.8B tokens and 5 PFLOP. A 1,000-step measured throughput pilot must replace estimated wall time before campaign execution.

No final campaign is part of the implementation handoff. Training commands require explicit execution and large-campaign acknowledgements.

## 18. Risks and confounds

- B0 may be solved by copying the sole value; B2 remains mandatory.
- Random and wrong controls are operational variants of an arbitrary remapping; targeted wrong is the stronger causal intervention.
- Format length can confound retrieval distance; matched-query-position controls are required.
- Disjoint vocabularies simplify role identification intentionally and do not prove shared-vocabulary generalization.
- A curriculum pass does not imply from-scratch learnability.
- Auxiliary objectives change the supervision regime.
- Linear probes may expose unused information.
- Attention mass is not a causal explanation.
- Larger models may learn faster without having a different asymptotic capacity.
- B4 value collisions change the interference structure and are reported separately.

## 19. What V10.10 can and cannot prove

A passing B2 result can establish episode-local binding, causal support use, and reproducibility under the registered synthetic distribution. It cannot establish rule induction, unseen-parameter transfer, arbitrary symbol generalization, natural-language memory, production readiness, production-scale behavior, or mathematical necessity of any mechanism.

## 20. Stopping rule and V10.11 recommendation

Do not start V10.11 automatically. If B2 passes without architecture change, stop and review the evidence before beginning a no-arithmetic deterministic transformation study. If only B0/B1 passes, continue binding/interference calibration. If only auxiliary supervision passes, test its binding generalization first. If only a future Phase F intervention passes, replicate and parameter-match before rule induction. If B0 fails, stop at B0.

## 21. Implementation package status

The implementation package contains the binding harness, safe study runner, report filler, frozen study/matrix artifacts, deterministic benchmark manifest support, and targeted tests. Phase F remains blocked. The large campaign has not been executed, so this report makes no binding-performance claim.

<!-- V10_10_GENERATED_RESULTS_START -->
## Generated execution results

- **Benchmark hash:** `9030dccd759dfe5d5afe57226434104a128328ed9937aa2d2328f153eef2840f`
- **Benchmark:** B2 / validation / 10000 episodes per seed
- **Legacy continuity:** `CONTINUITY_PASS`

### Registered run ledger

| Run | Phase | Level | Format | Query | Objective | Scale | Seed | Steps | Correct | Random | Wrong | Placeholder absent | Unpaired absent | Status |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| phase_a_S1_Q1 | phase-a | B2 | S1 | Q1 | O-A | L1 | 104729 | 64 | 96.60% | 93.90% | 93.90% | 25.00% | 95.70% | `COMPLETED` |
| phase_a_S1_Q2 | phase-a | B2 | S1 | Q2 | O-A | L1 | 104729 | 64 | 96.60% | 94.00% | 94.00% | 25.00% | 96.60% | `COMPLETED` |
| phase_a_S1_Q3 | phase-a | B2 | S1 | Q3 | O-A | L1 | 104729 | 64 | 96.60% | 93.80% | 93.80% | 25.00% | 94.90% | `FAILED_G2` |
| phase_a_S2_Q1 | phase-a | B2 | S2 | Q1 | O-A | L1 | 104729 | 64 | 96.60% | 93.30% | 93.30% | 24.00% | 96.60% | `COMPLETED` |
| phase_a_S2_Q2 | phase-a | B2 | S2 | Q2 | O-A | L1 | 104729 | 64 | 96.90% | 93.60% | 93.60% | 25.00% | 95.00% | `COMPLETED` |
| phase_a_S2_Q3 | phase-a | B2 | S2 | Q3 | O-A | L1 | 104729 | 64 | 96.90% | 93.80% | 93.80% | 25.00% | 95.90% | `COMPLETED` |
| phase_a_S3_Q1 | phase-a | B2 | S3 | Q1 | O-A | L1 | 104729 | 64 | 96.60% | 93.80% | 93.80% | 25.00% | 95.90% | `COMPLETED` |
| phase_a_S3_Q2 | phase-a | B2 | S3 | Q2 | O-A | L1 | 104729 | 64 | 96.60% | 93.20% | 93.20% | 25.00% | 94.80% | `COMPLETED` |
| phase_a_S3_Q3 | phase-a | B2 | S3 | Q3 | O-A | L1 | 104729 | 64 | 96.90% | 93.90% | 93.90% | 25.00% | 96.20% | `COMPLETED` |

### Readiness gates and classification

- No three-seed gate artifact exists. Classification: `NOT EVALUATED`.

### Execution claim boundary

Only artifacts listed above were executed. Missing phases remain `NOT RUN`. No associative-binding result is claimed without a passing B2 three-seed gate artifact.
<!-- V10_10_GENERATED_RESULTS_END -->

## 22. Production integrity

- Candidate C: unchanged.
- Production target: 25,908,188,576 parameters.
- Authoritative corpus: 233,997 tokens.
- External production approvals: 0/6.
- Production status: **STRICT NO-GO**.
- `src/nirmal/`: protected.
- `data/shards/`: protected.
- Nirmal execution: local/offline; no external model/API dependency.

## 23. Exact review boundary

The next authorized action is implementation review and targeted test execution. Legacy continuity and the final experimental campaign require explicit user authorization. No V10.11 task is authorized by this package.
