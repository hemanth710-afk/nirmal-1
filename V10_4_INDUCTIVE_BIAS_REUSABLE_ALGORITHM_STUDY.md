# Nirmal-1 V10.4 â€” Inductive Bias and Reusable Algorithm Representation Study

## 1. V10.3 Starting Evidence
V10.3 established that explicit algorithmic loss functions (diversity, relational consistency, contrastive isomorphism, curriculum learning) entirely failed to bridge the representation gap on fully-disjoint vocabularies when evaluated on ordinary token inputs. The model interpolated the training domain perfectly but scored 0.00% OOD in all conditions.

## 2. Hypotheses
The primary hypothesis is that the standard autoregressive, position-bound transformer block architecture fundamentally lacks the inductive bias necessary to encode transition rules *independently* from the symbols they act upon. We hypothesize that introducing alternative architectural biasesâ€”such as continuous relation mechanisms, rule weight-binding, or recurrent state transitionsâ€”might allow the model to discover and reuse latent algorithmic structures.

## 3. Architecture Modifications
Modifications were implemented as evaluation harness wrappers around the immutable `L0` micro-model:
- **E_A Baseline:** Ordinary autoregressive prediction.
- **E_B Continuous Relation Representation:** A learned continuous transition pathway applying relative offsets to token embeddings before processing.
- **E_C Reusable Rule / Weight-Binding:** A hypernetwork pathway extracting pooled latent contexts and dynamically binding rule weights to the hidden states.
- **E_D Recurrent State-Transition:** An explicit recurrent (GRU) block appended across the sequence length.
- **E_E Latent Rule Discovery Probe:** Direct latent rule supervision during training followed by a scaffold removal phase.

## 4. Scaffold-Off OOD Results
The most decisive metric is the model's accuracy on the held-out Fully-Disjoint vocabulary condition with all architectural scaffolds restricted to processing ordinary token sequences.

| Intervention | Train Acc | Val Acc | Scaffold-Off OOD Acc (Mean Â± 95% CI) | Isomorphic Probe Success |
|---|---|---|---|---|
| **E_A Baseline** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% | 0.0% |
| **E_B Continuous Relation** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% | 0.0% |
| **E_C Weight-Binding** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% | 0.0% |
| **E_D Recurrent State** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% | 0.0% |
| **E_E Latent Probe** | 100.00% ± 0.00% | 100.00% ± 0.00% | 0.00% ± 0.00% | 0.0% |

## 5. Failure Classification
**NO_SIGNAL**

The most effective intervention peaked at 0.00% OOD accuracy.

## 6. Limits of Inference
These experiments utilized micro-capacity models (`L0`). While these signals define optimization pathways, large-scale behavior might exhibit different local minima. 

## 7. Recommendation for V10.5
**Recommendation:** Inductive bias modifications failed to induce representation abstraction.
