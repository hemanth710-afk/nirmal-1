# Nirmal-1 V10.3 â€” Algorithmic Representation Discovery Study

## 1. V10.2 Starting Evidence
V10.2 established that increasing parameter capacity alone (up to 8.1M parameters) did not spontaneously elicit systematic out-of-distribution (OOD) generalization. Ordinary token identity representations remained stranded at 0% OOD on fully disjoint vocabularies, even though explicitly supplying invariant value-relative structures enabled strong generalization (>80%). 

## 2. Research Question
**Can the model learn to discover the invariant representation itself?**
Without manually preprocessing inputs into invariant value-relative codes, can specialized training algorithms force the standard autoregressive architecture to internalize abstract relational structures?

## 3. Hypotheses
The primary hypothesis is that the failure of ordinary identity representation is caused by insufficient pressure to discover representation-invariant structure. We hypothesize that algorithmic interventionsâ€”such as multi-surface diversity, relational consistency objectives, contrastive isometric training, or meta-algorithmic curriculaâ€”can induce abstraction while preserving a standard token representation at inference time.

## 4. Anti-Cheating Rules
To rigorously ensure the model generalizes structurally:
1. **Scaffold-Off Inference:** The final evaluation must not receive value-relative encoding, numeric token mappings, or structural labels.
2. **Ordinary Tokens:** The model must process standard token inputs only.
3. **Training Isolation:** Any auxiliary structural supervision must be disabled during the testing phase.

## 5. Experimental Matrix & Task Construction
The study evaluated a matrix of training interventions applied to the micro `L0` architecture on the `increment` rule across varied surface forms:
- **E1 Baseline:** Standard autoregressive training.
- **E2 Diversity:** Training on multiple disjoint surface vocabularies simultaneously.
- **E3 Relational Consistency:** Auxiliary MSE objective enforcing identical latent states for isomorphic rule pairs.
- **E4 Contrastive Isomorphic:** Contrastive loss pulling isomorphic instances closer and pushing disparate rule instances apart.
- **E5-E7 Combinations:** Combinations of Diversity + Relational/Contrastive.
- **E8 Curriculum:** Progressive learning from `copy` â†’ `single-step` â†’ `increment` â†’ `double-step`.

## 6. Scaffold-Off OOD Results
The most decisive metric is the model's accuracy on the held-out Fully-Disjoint vocabulary condition with all scaffolds removed.

| Intervention | Train Acc | Val Acc | Scaffold-Off OOD Acc (Mean Â± 95% CI) |
|---|---|---|---|
| **E1 Baseline** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |
| **E2 Diversity** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |
| **E3 Relational Only** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |
| **E4 Contrastive Only** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |
| **E5 Diversity + Relational** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |
| **E6 Diversity + Contrastive** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |
| **E7 Diversity + Rel + Cont** | 33.33% ± 26.67% | 33.33% ± 26.67% | 0.00% ± 0.00% |
| **E8 Curriculum** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% |

## 7. Failure Classification
**NO_INTERNALIZED_INVARIANCE_DETECTED**

The most effective algorithmic interventions peaked at 0.00% OOD accuracy. Compared to the E1 baseline of 0.00%, this indicates: NO_INTERNALIZED_INVARIANCE_DETECTED.

## 8. Leakage Certificates
All configurations maintained strict vocabulary disjointness between training conditions and the OOD test set, verifying 0% exact-match and 0% sub-sequence leakage.

## 9. Limits of Inference
These experiments utilized micro-capacity models (`L0`) to rapidly prototype algorithmic representations. While these signals define optimization pathways, large-scale behavior might exhibit different local minima. 

## 10. Recommendation for V10.4
**Recommendation:** Algorithmic interventions failed to induce representation abstraction. Rethink fundamentally.
