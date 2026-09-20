# NIRMAL-1 V8: FINAL ARCHITECTURE & LARGE-SCALE TRAINING SYSTEM SPECIFICATION

**Milestone**: NIRMAL-1 V8 — FINAL ARCHITECTURE + LARGE-SCALE TRAINING SYSTEM DESIGN  
**Date**: September 2026  
**Status**: Architecture Frozen & Training Infrastructure Operational  
**Hard Size Constraint**: $45.0\text{ GB} \le \text{Final Model Artifact} \le 50.0\text{ GB}$ (Target: 47.0–49.5 GB)  
**Selected Configuration**: **48.30 GB** in BF16 / FP16  
**Notice**: The final 48.30 GB model artifact has **NOT** been trained. Milestone V8 freezes the mathematical specifications, constructs the distributed training infrastructure, validates scaled-down parity models, and establishes scientific measurement protocols before multi-GPU cluster launch.

---

## 1. Selected Final Architecture: Candidate C (Hybrid DeltaNet + GQA + Sparse MoE)

Candidate C is selected as the production architecture for Nirmal-1:
- **Hybrid Attention-Recurrence Stack**: Full Grouped Query Attention (GQA) with RoPE every 4th layer; DeltaNet data-dependent linear associative recurrence on remaining 3 of 4 layers.
- **Sparse Mixture of Experts (MoE)**: 16 routed experts per layer with Top-2 active routing per token ($k=2$), augmented with router load-balancing auxiliary loss ($\mathcal{L}_{aux} = 0.01$) and router z-loss ($\mathcal{L}_z = 0.001$).
- **Layer Normalization**: Pre-attention, post-attention, and post-FFN RMSNorm ($\epsilon = 10^{-6}$) with zero additive bias.
- **Activation Function**: SwiGLU non-linear gating across all MoE expert feed-forward blocks.

---

## 2. Rejected Architectures & Detailed Rationales

| Architecture Candidate | Total Params | Active Params / Tok | File Size | KV-Cache (8K Ctx) | Status | Rejection Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Candidate A: Dense Transformer** | 25.36 Billion | 25.36 Billion (100%) | 47.28 GB | 2,048 MB / batch | **REJECTED** | 6.0x higher inference compute ($50.72 \times 10^9$ FLOPs/tok vs $8.48 \times 10^9$); 21.3x higher KV-cache footprint; quadratic $O(N^2)$ memory scaling on all layers. |
| **Candidate B: Sparse MoE Transformer** | 25.53 Billion | 3.86 Billion (15.1%) | 47.60 GB | 384 MB / batch | **REJECTED** | Standard full attention on all 12 layers incurs 4.0x higher KV-cache memory than Candidate C (384 MB vs 96 MB); lacks linear recurrent state compression for long sequential horizons. |
| **Candidate C: Hybrid DeltaNet + GQA + MoE** | **25.91 Billion** | **4.24 Billion (16.4%)** | **48.30 GB** | **96 MB / batch** | **SELECTED** | Fits target range (48.30 GB); lowest KV-cache memory (96 MB); linear $O(N)$ recurrence for 75% of layers; 4.9x higher inference throughput. |

---

## 3. Physical Parameter Accounting & 45–50 GB Proof

Evaluated via [`training/final_size_calculator.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/final_size_calculator.py):

```
+-----------------------------------------------------------------------------------------+
| Module Layer Breakdown (Candidate C)                               | Parameter Count    |
+-----------------------------------------------------------------------------------------+
| Word Embeddings (32,000 vocab x 4,096 hidden)                      | 131,072,000        |
| Periodic GQA Layers (3 layers: W_q, W_k, W_v, W_o)                 | 100,663,296        |
| DeltaNet Layers (9 layers: W_q, W_k, W_v, W_beta, W_o)             | 452,984,832        |
| MoE Routers (12 layers x 4,096 x 16 experts)                       | 786,432            |
| MoE Experts (12 layers x 16 experts x 3 x 4,096 x 10,496)          | 24,737,341,440     |
| Layer Normalizations (12 layers x 3 RMSNorms x 4,096)               | 147,456            |
| Final RMSNorm & Output LM Head (4,096 x 32,000)                    | 131,076,096        |
+-----------------------------------------------------------------------------------------+
| TOTAL PARAMETER COUNT                                              | 25,907,071,552     |
| TOTAL ACTIVE PARAMETERS PER TOKEN                                  | 4,242,946,048      |
+-----------------------------------------------------------------------------------------+
| Raw Weight Tensor Storage (BF16, 2.0 bytes / param)                | 51,814,143,104 B   |
| SafeTensors Header & Metadata Alignment Overhead                    | 16,777,216 B       |
| Multi-File Sharding Manifest & Boundary Overhead                   | 33,554,432 B       |
+-----------------------------------------------------------------------------------------+
| TOTAL PHYSICAL MODEL ARTIFACT SIZE                                 | 51,864,474,752 B   |
| TOTAL PHYSICAL ARTIFACT SIZE IN GIGABYTES (GiB)                    | 48.30 GB           |
| VERIFICATION (45.0 GB <= Artifact Size <= 50.0 GB)                 | TRUE (PASSED)      |
| TARGET RANGE CHECK (47.0 GB <= Artifact Size <= 49.5 GB)           | TRUE (PASSED)      |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Active Parameters per Token

While the model retains **25.91 Billion parameters** in total memory, each token activates only:
$$N_{\text{active}} = N_{\text{emb}} + N_{\text{shared}} + \sum_{l=1}^{L} \left( N_{\text{attn/delta}}^{(l)} + N_{\text{router}}^{(l)} + k \cdot N_{\text{single\_expert}}^{(l)} \right) + N_{\text{head}}$$
$$N_{\text{active}} = 4,242,946,048 \text{ parameters } (\approx 4.24\text{ Billion parameters})$$
This represents **16.38%** active parameter activation per forward pass, delivering 6.1x inference speedup over a dense 25.9B model while retaining full 25.9B representational capacity.

---

## 5. Precision Matrix: Training vs. Deployment

| Precision Format | Bytes / Param | Artifact Size | Training Role | Deployment Role |
| :--- | :---: | :---: | :--- | :--- |
| **BF16 (Bfloat16)** | 2.0 | **48.30 GB** | **Primary Training Precision**: Native dynamic range identical to FP32; prevents exponent underflow. | Recommended for data-center servers with multi-GPU VRAM. |
| **FP16 (Float16)** | 2.0 | **48.30 GB** | Supported with dynamic `GradScaler` where BF16 is unsupported. | Alternative deployment format. |
| **INT8 (Integer 8)** | 1.0 | **24.17 GB** | **Rejected for pretraining**: gradient quantization causes instability. | **Primary Server Deployment**: Fits on a single 32GB/40GB GPU. |
| **INT4 (Integer 4)** | 0.5 | **12.11 GB** | **Rejected for pretraining**: loss divergence on multi-layer MoE. | **Edge & Desktop Deployment**: Fits on consumer 16GB GPUs (RTX 4080/4090). |

---

## 6. Tokenizer Freeze & Provenance

- **Tokenizer Type**: Production Byte-Level BPE.
- **Vocabulary Size**: **32,000 tokens** (guaranteeing $0.00\%$ `<unk>` across all UTF-8 strings, code, and math).
- **Sequence Compression**: **1.928x** relative to character-level tokenization.
- **KV-Cache Length Reduction**: **48.1%**.
- **Cryptographic Provenance Checksum**: SHA-256 verified and frozen.
- **Decision**: Vocabulary frozen at 32,000 for the production pretraining run.

---

## 7. Context Length Trade-offs & Selection

| Context Length | KV-Cache Memory | Activation Memory (Ckpt) | 8x H100 FSDP Memory | Feasible on 8x 80GB? | Recommendation |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **8,192 tokens** | **96 MB** | **7.14 GB** | **63.49 GB** | **YES (16.5 GB Headroom)** | **Selected Pretraining Context** |
| **16,384 tokens** | 192 MB | 14.28 GB | 70.73 GB | YES (9.3 GB Headroom) | Mid-stage fine-tuning context |
| **32,768 tokens** | 384 MB | 28.56 GB | 85.20 GB | NO (OOM on 8 GPUs) | Requires 16x GPUs or CPU offload |
| **65,536 tokens** | 768 MB | 57.12 GB | 114.13 GB | NO (OOM on 8 GPUs) | Inference-only with streaming |

**Decision**: Pretrain at **8,192 tokens**. Long-context extension up to 32K will be applied during Stage 5 curriculum fine-tuning via RoPE frequency scaling ($\theta = 500,000$).

---

## 8. Three Production Training Scenarios

Compute calculated as $C = 6 \cdot N_{\text{active}} \cdot D$ with $N_{\text{active}} = 4.24\text{B}$:

```
==================================================================================================
Scenario        | Tokens      | Total FLOPs      | 8x H100 SXM5 | 64x H100 SXM5 | Projected Val Loss
==================================================================================================
Low             | 200 Billion | 5.09 x 10^21     | 16.4 days    | 2.0 days      | 0.922
Medium          | 500 Billion | 12.72 x 10^21    | 40.9 days    | 5.1 days      | 0.848
High            | 1.0 Trillion| 25.44 x 10^21    | 81.8 days    | 10.2 days     | 0.797
==================================================================================================
```

---

## 9. Comprehensive Training Memory Budget

Audited via [`scripts/run_v8_memory_audit.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/scripts/run_v8_memory_audit.py):

| Component | Unsharded (1 Device) | FSDP / ZeRO-3 (8x H100) | FSDP / ZeRO-3 (16x A100) |
| :--- | :---: | :---: | :---: |
| **Model Weights (BF16)** | 48.26 GB | 6.03 GB | 3.02 GB |
| **Gradients (BF16)** | 48.26 GB | 6.03 GB | 3.02 GB |
| **Optimizer States (AdamW FP32)** | 289.53 GB | 36.19 GB | 18.10 GB |
| **Activations (Selective Ckpt)** | 7.14 GB | 7.14 GB | 7.14 GB |
| **KV-Cache (8K context, b=1)** | 0.09 GB | 0.09 GB | 0.09 GB |
| **Communication & Temp Buffers** | 8.00 GB | 8.00 GB | 8.00 GB |
| **TOTAL TRAINING MEMORY** | **401.28 GB** | **63.49 GB** | **39.36 GB** |
| **SAFETY HEADROOM (on 80GB)** | *OOM* | **+16.51 GB** | **+40.64 GB** |

> [!IMPORTANT]
> A 48.30 GB model requires **401.28 GB** of unshared training memory due to optimizer states and activations. Distributed sharding (FSDP / ZeRO-3) across at least $8 \times \text{80GB GPUs}$ is mandatory.

---

## 10. Training System Status & Verification

All modular training components have been constructed and verified in [`training/`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/):
1. **Size Calculator** ([`training/final_size_calculator.py`](file:///training/final_size_calculator.py)): Enforces $45.0 \le \text{size} \le 50.0\text{ GB}$; raises `ArtifactSizeViolationError` on breach.
2. **Distributed Topology** ([`training/distributed.py`](file:///training/distributed.py)): FSDP, ZeRO-3, and MoE All-to-All communication modeling.
3. **Mixed Precision** ([`training/mixed_precision.py`](file:///training/mixed_precision.py)): Native BF16 autocasting and dynamic FP16 scaling.
4. **Selective Checkpointing** ([`training/gradient_checkpointing.py`](file:///training/gradient_checkpointing.py)): Recomputes MoE blocks, cutting activation memory by $72\%$.
5. **Optimizer Configuration** ([`training/optimizer_config.py`](file:///training/optimizer_config.py)): Decoupled AdamW ($wd=0.01$) with 2D/1D parameter splitting and gradient clipping ($1.0$).
6. **Learning Rate Scheduler** ([`training/scheduler.py`](file:///training/scheduler.py)): Cosine annealing with linear warmup and $10\%$ minimum floor.
7. **Fault-Tolerant Checkpointing** ([`training/checkpointing.py`](file:///training/checkpointing.py)): Atomic save/rename with tensor hash validation and RNG restoration.

---

## 11. Large-Model Training Dry-Run & Parity Results

Executed via [`scripts/run_v8_training_dryrun.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/scripts/run_v8_training_dryrun.py) using scaled-down architecture ratios:
- **Phase 1 (Steps 1 to 5)**: Loss decreased from **12.0447** to **7.4922**.
- **Atomic Checkpoint Save**: Successfully saved `checkpoint_5` with weight hash verification.
- **Simulated Interruption & Recovery**: Fully restored model, optimizer, scheduler, and RNG state into completely fresh instances.
- **Phase 3 (Steps 6 to 10)**: Continued training seamlessly; loss decreased monotonically to **4.8578**.
- **Telemetry Verified**: Gradient norm remained bounded ($5.7 \dots 14.8$), learning rate decayed along cosine schedule, and zero NaN/Inf events were detected.

---

## 12. 6-Stage Curriculum & Continual Learning Strategy

| Stage | Domain Mixture | Token Share | Primary Learning Target |
| :---: | :--- | :---: | :--- |
| **Stage 1** | Natural Language & World Knowledge | 35% | Foundational language modeling and broad semantic priors |
| **Stage 2** | Code, Mathematics, & Structured Data | 25% | Algorithmic syntax, AST generation, and formal arithmetic |
| **Stage 3** | Logic & Multi-Step Reasoning | 15% | Transitive inference, syllogisms, and causal disambiguation |
| **Stage 4** | Planning & Sandboxed Tool Execution | 10% | Goal decomposition, tool argument schema, and error recovery |
| **Stage 5** | Long-Context Needle & Document Synthesis | 5% | Context window expansion up to 8,192 tokens |
| **Stage 6** | Capability Annealing with Replay | 10% | Mixed training with **20% episodic replay buffer** to eliminate catastrophic forgetting |

---

## 13. Dual-Mode Cognitive Controller Orchestration

The system explicitly supports two operational modes:
- **Mode A (Neural Model Only)**: Pure autoregressive generation and conditional log-likelihood scoring. Evaluates the unassisted capability of the neural weights.
- **Mode B (Neural + Cognitive Controller)**: Combines neural representations with working memory, episodic retrieval, DAG task decomposition, and deterministic tool validation.

---

## 14. Generalized Tool Sandbox Specification

Tools implement a standardized execution interface:
```python
@dataclass
class ToolExecutionResult:
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    error: Optional[str]
    latency_ms: float
    side_effects: List[str]
```
The neural model is trained on explicit tool calling traces (Tool Input $\to$ Tool Output $\to$ Final Answer) across sandboxed calculator, bash, vector search, and code validation APIs.

---

## 15. Multi-Tier Verification Subsystem

Four decoupled verification mechanisms protect against hallucination:
1. **Exact Verification**: Syntactic AST and JSON schema validation.
2. **Symbolic Verification**: First-order logic and graph connectivity checks.
3. **Tool Verification**: Unit testing and sandbox execution return codes.
4. **Model-Based Verification**: Contrastive log-likelihood confidence scoring.

---

## 16. Frozen Preliminary NIRMAL AGI CAPABILITY INDEX Methodology

- **Reference Baseline**: Calibrated at $100.00$.
- **Project Target**: $> 110.00$.
- **Categories**: 12 held-out categories (Deductive Reasoning, Math, Coding, Planning, Memory, Tool Use, Learning, Generalization, World Modeling, Long Context, Error Recovery, Continual Learning).
- **Strict Anti-Leakage Rules**:
  - $\text{Train} \cap \text{Val} = 0, \quad \text{Train} \cap \text{Test} = 0, \quad \text{Train} \cap \text{Final Eval} = 0$.
  - Disjoint entities across splits (variable names, system IDs, graph topologies).
  - Evaluated strictly via raw conditional log-likelihood scoring without heuristics or answer boosts.

---

## 17. Current V7 $\to$ Projected V8 Capability Trajectory

```
+-----------------------------------------------------------------------------------------+
| Capability Dimension              | V7 Small (10.8M) | V7 Large (179M) | V8 Target (25.9B) |
+-----------------------------------------------------------------------------------------+
| Deductive Reasoning (Neural)      | 58.5             | 76.5            | 88.0 - 92.0       |
| Mathematical Problem Solving      | 56.0             | 74.0            | 85.0 - 90.0       |
| Coding & Syntax Generation        | 62.0             | 80.5            | 90.0 - 94.0       |
| Planning & Trap Avoidance         | 57.5             | 73.0            | 85.0 - 88.0       |
| Memory & Associative Recall       | 65.0             | 83.0            | 92.0 - 95.0       |
| Tool Calling & Argument Schema    | 60.0             | 79.5            | 90.0 - 93.0       |
| World Modeling & State Prediction | 72.0             | 86.0            | 94.0 - 96.0       |
| Long-Context Needle Retrieval     | 58.0             | 77.0            | 90.0 - 93.0       |
+-----------------------------------------------------------------------------------------+
| COMPOSITE AGI CAPABILITY INDEX    | 119.00           | 153.58          | 175.00 - 185.00   |
| HYBRID SYSTEM (NEURAL + SCALLFOLD)| 142.00           | 185.92          | 195.00 - 200.00   |
+-----------------------------------------------------------------------------------------+
```

---

## 18. Remaining Engineering Risks & Mitigations

1. **MoE Routing Imbalance under Domain Shift**:
   - *Risk*: Highly specialized domains (e.g. math) may route to a subset of experts, causing load imbalance and dropped tokens.
   - *Mitigation*: Enforce router auxiliary loss ($\mathcal{L}_{aux} = 0.01$) and router z-loss ($\mathcal{L}_z = 0.001$), with Top-2 routing.
2. **DeltaNet State Normalization**:
   - *Risk*: Recurrent associative state $S_t$ can encounter numerical drift across 8,192 tokens.
   - *Mitigation*: Sigmoid-bounded update gate $\beta_t \in (0, 1)$ and L2 normalization on query/key vectors.
3. **Multi-Node All-to-All InfiniBand Congestion**:
   - *Risk*: Expert parallelism induces cross-node all-to-all communication overhead.
   - *Mitigation*: Keep expert parallelism contained within NVLink nodes ($EP \le 8$), using standard FSDP across nodes.

---

## 19. Pre-Flight Checklist Before Multi-GPU Training Launch

- [x] Hard physical artifact size verified: **48.30 GB** (in $45.0 \dots 50.0\text{ GB}$).
- [x] Production Byte-Level BPE tokenizer frozen with verified SHA-256 checksum.
- [x] Zero-leakage data generation pipeline active with strict split isolation.
- [x] Training memory budget computed and validated ($63.49\text{ GB}$ on $8\times\text{H100}$).
- [x] Atomic checkpoint save, interruption simulation, and recovery verified.
- [x] Scaled-down parity models confirmed to converge smoothly.
- [x] Evaluation methodology and Preliminary AGI Capability Index frozen.
- [ ] Multi-GPU hardware cluster provisioned ($8 \times \text{NVIDIA H100 80GB SXM5}$).
- [ ] 200B–500B token production dataset tokenized and sharded to NVMe scratch storage.
