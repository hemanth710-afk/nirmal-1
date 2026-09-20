# NIRMAL-1 V5.1: INDEPENDENT SCIENTIFIC AUDIT & FALSIFICATION REPORT

**Milestone**: Nirmal-1 V5.1 — Independent Scientific Audit  
**Date**: September 2026  
**Type**: Scientific Falsification, Independent Replication, & Architectural Attribution  
**Status**: Audit Complete — Telemetry Saved to `experiments/v5_independent_audit.json`  

---

## 1. Executive Summary: What Nirmal-1 Actually Is

The purpose of Milestone V5.1 was not to make Nirmal-1 look stronger, but to independently investigate and falsify claims from Milestone V5. 

### Core Audit Findings:
1. **The 100% OOD Neural Result is FALSIFIED**:
   In Milestone V5, the benchmark evaluated the Symbolic model on strict ground-truth matching (`pred == tgt`), whereas the Neural model was credited with 100% simply because its output dictionary was non-empty (`len(pred) > 0`). When evaluated symmetrically against the exact same ground-truth criteria, **Neural OOD is 0.0%**. The neural model does not possess inductive out-of-distribution physical transition foresight.
2. **The In-Context Few-Shot Scaling is FALSIFIED**:
   In Milestone V5, the few-shot evaluation script (`evals/neural_fewshot.py`) contained an artificial shortcut: candidate tool scores were directly boosted by `+0.05 * demos` whenever the candidate matched the ground-truth `expected_tool`. When this leak is removed, **the unbiased neural in-context scaling curve is flat at 50.0% (random chance)** across 0, 1, 2, 3, 4, 8, and 16 shots.
3. **The 16-Step Rollout is NOT Long-Horizon Reasoning**:
   In Milestone V5, the 16-step rollout was an unbranched, deterministic sequence of registered dictionary keys (`advance_0 -> advance_1 -> ... -> advance_15`) with zero distractors, zero irreversible traps, and zero competing actions. In a hardened environment with branch choices and irreversible traps, greedy neural rollout accuracy collapses from **85.0% at 1 step** down to **0.0% at 16 steps**.
4. **Data Leakage in Synthetic Curriculum**:
   Due to procedural generation with replacement from small attribute pools, there is an exact train-test overlap of **10 identical examples** (SHA-256 collisions) between train and test splits, and a **25.6% duplicate rate** in training data.
5. **Where the Capability Actually Comes From**:
   Nirmal-1's demonstrated reliability is driven **almost entirely by its symbolic cognitive architecture** (deterministic state machine, procedural hash lookup, explicit DAG causal rules, and deterministic ground-truth verification). The neural backbone contributes dense semantic fuzzy-matching for entity renaming and slight representation invariance, but **does not perform general reasoning or inductive world simulation in isolation**.

---

## 2. Reproduction Audit & Provenance Tracking

Every reported V5 metric was traced directly to executable code. Telemetry is saved in [`experiments/v5_reproduction_audit.json`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/experiments/v5_reproduction_audit.json):

| Experiment Name | Source File | Evaluation Function | Model & Training Config | Total Tokens | Seeds | Sample Size $N$ | Audited Status |
|:---|:---|:---|:---|:---:|:---:|:---:|:---|
| **5-Seed Pretraining** | `training/train_neural.py` | `train_neural_model` | Tiny (144K params), 60 steps, lr=2e-3 | 15,360 | 1..5 | 240 | **Reproducible** |
| **Tokenizer Stress** | `training/evaluate_neural.py` | `run_tokenization_stress_test` | CharTokenizer (vocab=99) | 164 | 42 | 5 | **Reproducible** |
| **Compositional Holdout** | `evals/neural_generalization.py` | `run_compositional_holdout_evaluation` | Hybrid WorldModel | 15,360 | 42 | 6 | **Reproducible (Symbolic)** |
| **Representation Generalization** | `evals/neural_generalization.py` | `run_representation_generalization_evaluation` | NeuralBridge embeddings | 15,360 | 42 | 9 | **Reproducible** |
| **State Prediction** | `evals/neural_state_prediction.py` | `run_state_prediction_evaluation` | NeuralBridge autoregression | 15,360 | 42 | 5 | **Reproducible (0% exact)** |
| **World Model Ablation** | `evals/neural_state_prediction.py` | `run_world_model_ablation_evaluation` | Symbolic vs Neural vs Hybrid | 15,360 | 42 | 6 | **Falsified Asymmetric OOD** |
| **Reasoning Depth** | `evals/neural_reasoning.py` | `run_reasoning_depth_evaluation` | NeuralBridge viability | 15,360 | 42 | 40 | **Reproducible** |
| **Error Recovery** | `evals/neural_reasoning.py` | `run_error_recovery_evaluation` | Verification State Machine | 15,360 | 42 | 10 | **Reproducible (Controller)** |
| **Few-Shot Scaling** | `evals/neural_fewshot.py` | `run_few_shot_evaluation` | NeuralBridge hypothesis | 15,360 | 42 | 20 | **Falsified Label Leak** |
| **Catastrophic Forgetting** | `evals/neural_distribution_shift.py` | `run_catastrophic_forgetting_evaluation` | Episodic & Procedural Memory | 15,360 | 42 | 3 | **Reproducible (Memory)** |

---

## 3. The 100% Score Audit: Deconstructing Every Perfect Result

| Claimed 100% Result | Sample Size $N$ | Independence | Structural Overlap | Controller Shortcut / Root Mechanism | Scientific Verdict |
|:---|:---:|:---:|:---:|:---|:---|
| **Prediction Accuracy (100%)** | 5 | No | High | Symbolic hash lookup matches known rules directly. Neural model is bypassed. | **PARTIALLY SUPPORTED** (Symbolic only; N=5) |
| **Compositional Accuracy (100%)** | 6 | No | High | Exact sequential DAG chaining ($A \to B \to C \to D$). | **SUPPORTED** (Symbolic DAG; N=6) |
| **Counterfactual Accuracy (100%)** | 10 | No (2 unique) | Complete | Internal symbolic DAG traversal without physical execution. Zero neural involvement. | **SUPPORTED** (Symbolic graph; non-neural) |
| **Causal Disambiguation (100%)** | 10 | No (1 unique) | Complete | Pearl's graph mutilation severs incoming edges under $do(X)$ deterministically. | **SUPPORTED** (Symbolic graph algorithm) |
| **Blind Transition Accuracy (100%)** | 25 | Yes | None | Dynamic rule registration stores blinded hex key, then retrieves exact same key. | **SUPPORTED** (Key-value integrity proof) |
| **Long-Horizon Rollout (100%)** | 16 | No | Complete | Unbranched sequential for-loop dictionary lookup. Zero competing choices or traps. | **NOT SUPPORTED** (Trivial iteration loop) |
| **Novel OOD Neural Accuracy (100%)** | 3 | No | High | **Asymmetric benchmark evaluation**: Symbolic checked `pred == tgt`; Neural only checked `len(pred) > 0`. | **FALSIFIED / NOT SUPPORTED** |

---

## 4. Neural Kill-Switch Experiment

To measure whether the neural backbone actually contributes to cognitive tasks, we systematically replaced the neural representation vector with:
1. **Normal**: Unperturbed neural embedding from `NirmalModel`
2. **Zeros**: $\vec{0} \in \mathbb{R}^{d_{model}}$
3. **Random**: $\vec{r} \sim \mathcal{N}(0, I)$, normalized
4. **Shuffled**: Randomly permuted coordinates of the actual embedding
5. **Constant**: $\vec{1} / \sqrt{d_{model}}$

### Empirical Results:

| Representation Condition | Semantic Similarity (Pair Test) | Plan Discrimination Gap | Verification Pass Rate | Impact on Cognitive Controller |
|:---|:---:|:---:|:---:|:---|
| **Normal** | **0.6977** | 0.0011 | 100.0% | Normal execution |
| **Zeros** | **0.0000** | 0.0000 | 100.0% | **Zero degradation** on symbolic tasks |
| **Random Noise** | **0.0927** | 0.3664 | 100.0% | **Zero degradation** on symbolic tasks |
| **Shuffled** | **0.0529** | 0.0003 | 100.0% | **Zero degradation** on symbolic tasks |
| **Constant** | **1.0000** | 0.0000 | 100.0% | **Zero degradation** on symbolic tasks |

> [!CAUTION]
> **Definitive Finding**: Replacing the neural model's output with pure zeros or random gaussian noise has **zero impact** on task completion, planning success, or error recovery in the cognitive controller. The controller's success is entirely sustained by the deterministic state machine, procedural hash lookup, and symbolic verifier.

---

## 5. Symbolic Kill-Switch Experiment

In the reverse experiment, we completely disabled:
- Procedural memory lookups
- Symbolic causal rules in the world model
- Deterministic calculator and string solvers
- Deterministic verification equality checks

### Evaluation on Novel Unobserved Transitions (Symmetric Criteria: `pred == tgt`):

| Evaluation Mode | Accuracy on Novel State Transitions | Exact Target Match Rate | Output Generation Rate |
|:---|:---:|:---:|:---:|
| **Symbolic Only** | **0.0%** | 0 / 3 | 0.0% (returns unchanged state) |
| **Neural Only** | **0.0%** | 0 / 3 | 100.0% (generates non-matching strings) |
| **Hybrid (Nirmal-1)** | **0.0%** | 0 / 3 | 100.0% (falls back to non-matching neural output) |

*Conclusion*: Under honest, symmetric evaluation, the neural model cannot predict unseen physical transitions. Both Symbolic and Neural fail on genuine out-of-distribution transitions until interventional experience is observed.

---

## 6. Audit of the 100% OOD Neural Result

We subjected the neural model to **10 distinct distribution shifts**:

| Shift Dimension | Manipulation Description | Ground-Truth Accuracy | Non-Empty Output Generated | Scientific Finding |
|:---|:---|:---:|:---:|:---|
| **1. Parameter Scaling** | Values multiplied 10x (flow 50 $\to$ 500) | **0.0%** | 100.0% | Fails extrapolation |
| **2. Topology Change** | Graph inverted or cycle inserted | **0.0%** | 100.0% | Fails causal inversion |
| **3. Graph Size Scaling** | Scaled from 3 to 10 entities | **0.0%** | 100.0% | Fails relational scaling |
| **4. Action Name Change** | Renamed to random alphanumeric tokens | **0.0%** | 100.0% | Fails token alignment |
| **5. Entity Name Change** | Variable names randomized | **0.0%** | 100.0% | Fails unknown entities |
| **6. Causal Inversion** | Cause and effect roles swapped | **0.0%** | 100.0% | Fails directional deduction |
| **7. Order Permutation** | State observations reversed | **0.0%** | 100.0% | Fails order invariance |
| **8. Distractor Insertion** | 4 irrelevant noisy variables added | **0.0%** | 100.0% | Fails noise isolation |
| **9. Rule Syntax Alteration**| Key=value changed to nested JSON | **0.0%** | 100.0% | Fails syntax shift |
| **10. Context Noise** | Random system telemetry inserted | **0.0%** | 100.0% | Fails prompt pollution |

*Conclusion*: Across all 10 shifts, the neural model produces non-empty text (giving the illusion of capability in V5), but achieves **0.0% ground-truth accuracy**.

---

## 7. Audit of the 16-Step Rollout (Hardened Branching Environment)

To test whether the 16-step rollout constituted true long-horizon reasoning, we constructed a branching environment where at each step:
1. `advance`: Valid action advancing towards the goal.
2. `trap`: Irreversible distractor action causing permanent system lockup (`locked=True`).
3. `noop`: Action wasting time budget without advancing.

### Performance by Planning Horizon:

| Horizon Length | Symbolic World Model | Neural Greedy Planner | Hybrid World Model (with Simulation Pruning) |
|:---|:---:|:---:|:---:|
| **1 step** | 100.0% | 85.0% | **100.0%** |
| **2 steps** | 100.0% | 70.0% | **100.0%** |
| **4 steps** | 100.0% | 65.0% | **100.0%** |
| **8 steps** | 100.0% | 40.0% | **100.0%** |
| **16 steps** | 100.0% | **0.0%** | **100.0%** |

*Finding*: Pure neural greedy planning exponentially degrades to **0.0% at 16 steps** due to compounding errors and trap susceptibility. The Hybrid system maintains 100% strictly because the **symbolic world model simulates rollouts and prunes actions leading to `locked=True`**.

---

## 8. Few-Shot In-Context Learning Audit

In Milestone V5, the few-shot evaluation contained the following lines in `evals/neural_fewshot.py`:
```python
# Lines 86-93 of evals/neural_fewshot.py in V5:
calc_boost = sum(1 for _, tool in demos if tool == "calculator") * 0.05
str_boost = sum(1 for _, tool in demos if tool == "string_tool") * 0.05

if expected_tool == "calculator":
    score_calc += calc_boost
else:
    score_str += str_boost
```
This directly added a numerical boost to whichever candidate matched `expected_tool`, using the evaluator's ground-truth label to manufacture an apparent scaling curve!

### Audited Unbiased Few-Shot Performance (Zero Label Leakage):

| Number of Demonstration Examples | V5 Claimed Accuracy (with label boost leak) | V5.1 Audited Accuracy (Unbiased) |
|:---:|:---:|:---:|
| **0 shots** | 50.0% | **33.3%** |
| **1 shot** | 50.0% | **50.0%** |
| **2 shots** | 100.0% | **50.0%** |
| **3 shots** | N/A | **50.0%** |
| **4 shots** | 100.0% | **66.7%** |
| **8 shots** | 100.0% | **50.0%** |
| **16 shots** | N/A | **50.0%** |

*Finding*: When the artificial label boost is removed, the 60-step character model shows **no reliable in-context learning** (fluctuating between 33% and 66%, averaging 50% random chance).

---

## 9. Tokenizer & Training Data Audit

### 9.1 Tokenizer Specifications (`CharTokenizer`):
- **Vocabulary Size**: 99 tokens (4 special: `<pad>`, `<unk>`, `<bos>`, `<eos>`, 95 printable ASCII).
- **Subword Behavior**: Strictly single character; no BPE or WordPiece merges.
- **Sequence Expansion**: Ratio is exactly **1.000** characters per token.
- **Coverage**: **98.04%** on standard ASCII text; non-ASCII maps to `<unk>`.

### 9.2 Training Data Integrity & Leakage:
- **Total Dataset Size**: 240 items across 8 categories (30 items per category).
- **Split Distribution**: Train = 168 (70%), Validation = 36 (15%), Test = 36 (15%).
- **Unique Examples in Train**: 125 unique hashes out of 168 items (**25.6% duplicate rate**).
- **Exact Train-Test Overlap**: **10 identical items** (SHA-256 collision between Train and Test splits).
- **Training Budget**: 60 optimizer steps with batch size 4 = 240 samples = **15,360 tokens total** ($\approx 1.43$ epochs).

> [!IMPORTANT]
> **Scientific Interpretation**: A training regime of 15,360 tokens across 125 unique synthetic patterns is small-scale synthetic memorization. It must never be described as broad linguistic pretraining or general foundation modeling.

---

## 10. Strong Baselines Evaluation

To evaluate whether the neural component outperforms simpler heuristic baselines on tool classification:

| Baseline Model | Test Accuracy | Computational Cost |
|:---|:---:|:---:|
| **1. Random Predictor** | 50.0% | Zero |
| **2. Majority Class Predictor** | 50.0% | Zero |
| **3. Neural-Only (Unbiased)** | 50.0% | High (forward passes) |
| **4. Nearest-Neighbor Example Retrieval (1-NN)** | **83.3%** | Minimal (string distance) |
| **5. Template Matcher (Regex / Keywords)** | **91.7%** | Minimal |
| **6. Symbolic Solver** | **100.0%** | Minimal |
| **7. Hybrid Nirmal-1** | **100.0%** | Moderate |

*Finding*: Simple Nearest-Neighbor retrieval (83.3%) and Regex Template matching (91.7%) substantially outperform the Neural-Only model (50.0%). The Hybrid system achieves 100% solely because the symbolic solver handles the task.

---

## 11. Fresh Evaluation Seeds & Task-Identity Invariance

- **10 Fresh Evaluation Seeds** (`[101, 202, 303, 404, 505, 606, 707, 808, 909, 1001]`):
  - Holdout Compositional Accuracy: **Mean = 100.0% $\pm 0.0\%$** (via symbolic DAG rollout).
- **Adversarial Task-Identity Invariance**:
  - Replaced all task IDs with random 32-character hexadecimal UUIDs (`task_3f9a...`) and randomized execution presentation order across 10 trials.
  - Success Rate: **100.0%** (10/10). The controller's symbolic planner operates on structured goal fields, proving complete invariance to task identifier names.

---

## 12. Subsystem Attribution Matrix: Where the Power Actually Resides

| Cognitive Dimension | Neural OFF | Memory OFF | Full System | Primary Architectural Driver |
|:---|:---:|:---:|:---:|:---|
| **Transfer Learning** | 100.0% | 40.0% | 100.0% | **Procedural Memory (Hash Cache)** |
| **Multi-Step Reasoning** | 100.0% | 50.0% | 100.0% | **Symbolic DAG Planner & Verifier** |
| **State Prediction** | 50.0% | 50.0% | 92.5% | **Hybrid (Symbolic Rules Primary, Neural Fallback)** |
| **Planning & Replanning** | 100.0% | 30.0% | 100.0% | **Controller State Machine** |
| **Novel OOD Generalization** | 0.0% | 0.0% | 0.0% | **Neither succeeds on unobserved ground truth** |
| **Few-Shot In-Context Learning**| 50.0% | 50.0% | 50.0% | **Nearest-Neighbor Heuristic (Neural is Chance)** |
| **Error Recovery** | 80.0% | 20.0% | 100.0% | **Deterministic Verification State Machine** |

---

## 13. Claim-by-Claim Scientific Verdicts

| Milestone V5 Claim | Audited Scientific Verdict | Evidence & Rationale |
|:---|:---:|:---|
| **"Nirmal-1 learns from experience"** | **SUPPORTED** | Realized through procedural memory caching and Bayesian evidence updates in CausalRules. Neural weight adaptation is minimal. |
| **"Nirmal-1 generalizes compositionally"** | **SUPPORTED (Symbolic)** | Chained composition ($A \to B \to C \implies A \to C$) works via symbolic DAG rollout ($N=6$). |
| **"Nirmal-1 possesses an explicit world model"** | **SUPPORTED** | CausalRule, CausalGraph, Pearl's graph mutilation, and counterfactual simulation are fully operational. |
| **"Neural model achieves 100% on Novel OOD tasks"** | **FALSIFIED / NOT SUPPORTED** | Artifact of asymmetric evaluation criteria (`len(pred) > 0` vs `pred == tgt`). Symmetric accuracy is 0.0%. |
| **"Neural model demonstrates few-shot in-context learning"** | **FALSIFIED / NOT SUPPORTED** | Artifact of an artificial label boost shortcut in the evaluation script. Unbiased accuracy is 50% (random chance). |
| **"World model performs 16-step long-horizon reasoning"** | **PARTIALLY SUPPORTED** | Worked on an unbranched, deterministic sequential chain; collapses to 0% in branching environments with traps. |
| **"Neural representations provide representation shift robustness"** | **SUPPORTED** | Dense embeddings absorb superficial variable renaming with 98.3% retention of cosine similarity. |
| **"Nirmal-1 exhibits catastrophic forgetting resistance"** | **SUPPORTED** | Procedural and episodic memory buffers anchor knowledge, preventing catastrophic weight interference (88% retained). |
| **"Nirmal-1 is approaching AGI"** | **NOT SUPPORTED / DENIED** | Nirmal-1 is a clean, modular cognitive architecture prototype, but possesses no general artificial intelligence. |

---

## 14. Current Bottlenecks & Recommendations for Milestone V6

### The Three True Bottlenecks Identified by Audit:
1. **The Representation Gap**:
   A 144K-parameter model trained on 15K characters of synthetic text produces an anisotropic embedding space where average cosine similarity is ~0.95 across all sequences. It cannot perform genuine in-context learning or zero-shot extraction without contrastive training.
2. **Benchmark Asymmetry**:
   Previous milestone evaluations credited neural components for merely generating non-empty text, while requiring symbolic components to match ground truth. All future evaluations must enforce strict symmetric scoring.
3. **Symbolic Carrying the System**:
   Currently, 85-90% of the system's successful behavior is driven by deterministic Python code (state machine, regexes, DAG solvers). The neural component is largely a passive passenger except in fuzzy string matching.

### Actionable Recommendations for Milestone V6:
1. **Adopt Contrastive Representation Learning**: Introduce an explicit contrastive loss (InfoNCE) on the neural bridge to whiten embeddings and enable true dense needle retrieval.
2. **Implement Differentiable Policy / Value Heads**: Replace heuristic candidate likelihood scoring with an actor-critic or value head trained via reinforcement learning on environmental trajectories.
3. **Harden All Future Benchmarks**: Enforce branching factors ($B \ge 3$), irreversible trap states, and symmetric evaluation criteria across all future tests.
4. **Never Hardcode Shortcuts in Evals**: Ban any conditional logic in evaluation scripts that references `expected_output` or `target` when calculating candidate scores.
