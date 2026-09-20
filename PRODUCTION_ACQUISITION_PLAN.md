# NIRMAL-1: PRODUCTION DATA & COMPUTE ACQUISITION PLAN

**Specification ID:** `NIRMAL-PROD-PLAN-V1.0`  
**Author:** Google DeepMind / Nirmal-1 Research & Infrastructure Core  
**Date:** September 6, 2026  
**Target Model:** Candidate C (Hybrid DeltaNet + Periodic GQA + Sparse MoE)  
**Total Parameters:** 25,908,188,576 (25.91 Billion)  
**Active Parameters / Token:** 4,240,414,112 (4.24 Billion)  
**Target Verified Corpus:** $\ge 200,000,000,000$ verified tokens  
**Current Physically Verified Tokens:** $233,997$ tokens  
**Current Verified Deficit:** $199,999,766,003$ tokens ($99.999883\%$ deficit)  
**Production Readiness Status:** **NO-GO** (Pipeline Software Ready; Physical Data & Cluster Not Available)

---

## 1. Executive Summary & Verification Context

This document defines the authoritative, end-to-end production acquisition plan for **Nirmal-1 Candidate C**. It establishes the exact operational, legal, storage, compute, and networking requirements to bridge the gap between our fully verified local development state and full-scale production training.

### Verified Repository Baseline
- **Model Architecture Integrity:** Frozen Candidate C architecture. Parameter counts verified directly via PyTorch meta-device instantiation ($25,908,188,576$ total parameters, $4,240,414,112$ active parameters/token). Model architecture under [`src/nirmal/`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/src/nirmal/) remains 100% untouched.
- **Local CUDA Smokes & Workflow:** Real Nirmal-1 forward pass, backward pass, and AdamW optimizer step verified on local NVIDIA GeForce RTX 3050 6GB Laptop GPU (PyTorch 2.14.0+cu132, CUDA 13.2).
- **Distributed Training Integration:** Fully Sharded Data Parallel (FSDP / ZeRO-3) wrapping implemented in [`training/distributed.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/training/distributed.py) and verified.
- **Hardened Pipeline & Launcher:** Full preflight audit (Checks A–O) and 12 immutable production data gates locked in [`scripts/production_data_acquisition.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/scripts/production_data_acquisition.py).
- **Test Suite Status:** 276 / 276 unit and integration tests passing.

---

## 2. Data Acquisition Plan

All candidate sources are registered in [`data/source_registry.json`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/data/source_registry.json) and formalized in [`data/production_source_plan.json`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/data/production_source_plan.json).

> [!CAUTION]
> Expected tokens are analytical planning figures only. They DO NOT count toward verified tokens until physically acquired, deduplicated, tokenized, sharded, and verified on disk.

### Detailed Source Inspection Table

| Source | License | Evidence Available? | Expected Tokens | Verified Tokens | Data Format | Acquisition Method | Known Risks | Status |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **FineWeb-Edu Filtered** | ODC-By | Partially (Dataset card & SPDX) | 50,000,000,000 | 0 | Parquet / JSONL.zst | Hugging Face Snapshot Sync | Lower educational tier noise; attribution metadata preservation; eval contamination | **PLANNED** |
| **The Stack v2 Permissive** | Apache-2.0 | Partially (BigCode filter tags) | 40,000,000,000 | 0 | Parquet & Git Blobs | BigCode Permissive Export / S3 | Secret/credential leakage; copyleft misclassification; high syntax token density | **PLANNED** |
| **arXiv Open Access** | CC-BY-4.0 | Partially (Bulk metadata index) | 35,000,000,000 | 0 | LaTeX / Extracted PDF text | arXiv Bulk S3 Sync | LaTeX parsing artifacts; corrupted mathematical notation; non-commercial license leakage | **PLANNED** |
| **Dolma v1.7 Permissive** | Apache-2.0 | Partially (AI2 distribution terms) | 35,000,000,000 | 0 | JSONL.gz | AllenAI S3 Bulk Export | Cross-source near-duplicate overlap with FineWeb; OCR noise in older scans | **PLANNED** |
| **RedPajama v2 Permissive** | Apache-2.0 | Partially (Together AI license) | 25,000,000,000 | 0 | JSONL | Together AI CLI / S3 | Lower average text quality; web paywall text leakage requiring aggressive GCLM filtering | **PLANNED** |
| **Wikimedia Open Corpus** | CC0-1.0 | Partially (Wikimedia Foundation terms) | 15,000,000,000 | 0 | CirrusSearch JSON / XML | Wikimedia Enterprise Snapshot | Wikitext markup stripping artifacts; table and infobox linearization corruption | **PLANNED** |
| **Nirmal Synthetic Shards** | Apache-2.0 | Yes (In-repo generation pipeline) | 233,997 | 233,997 | uint16 `.bin` / int64 `.idx` | In-Repo Staged Shards | None (Fully verified and locked on disk) | **VERIFIED** |
| **Proprietary Forum Scrapes** | Proprietary | Yes (ToS violation confirmed) | 0 | 0 | HTML / JSON | Web Scraping | ToS violation; legal liability; commercial training prohibition | **REJECTED** |
| **Non-Commercial Academic** | CC-BY-NC-4.0 | Yes (NC clause detected) | 0 | 0 | Tarball | Direct Download | Non-commercial restriction violates open commercial weight distribution | **REJECTED** |

---

## 3. 200B Token Mixture Plan

To ensure the production dataset reaches $\ge 200,000,000,000$ verified tokens after filtering, syntax parsing, decontamination, exact deduplication, and MinHash near-deduplication, a **headroom multiplier of $1.225\times$** ($22.5\%$ overage) is applied to raw acquisition.

### Mixture Allocation & Headroom Table

| Mixture Domain | Target Mix (%) | Target Verified Tokens | Raw Staged Target (with Headroom) | Expected Yield Post-Filter | Physically Verified Tokens |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Educational & Web Reasoning** (FineWeb-Edu) | 25.0% | 50,000,000,000 | 62,500,000,000 | 51,200,000,000 | 0 |
| **Code & Algorithms** (The Stack v2) | 20.0% | 40,000,000,000 | 49,000,000,000 | 40,800,000,000 | 0 |
| **Formal STEM & Mathematics** (arXiv) | 17.5% | 35,000,000,000 | 42,000,000,000 | 35,700,000,000 | 0 |
| **Curated Science & Reasoning** (Dolma v1.7) | 17.5% | 35,000,000,000 | 42,500,000,000 | 35,500,000,000 | 0 |
| **Broad Knowledge & Logic** (RedPajama v2) | 12.5% | 25,000,000,000 | 31,500,000,000 | 25,800,000,000 | 0 |
| **Encyclopedic Reference** (Wikipedia) | 7.5% | 15,000,000,000 | 17,500,000,000 | 15,800,000,000 | 0 |
| **Algorithmic Synthetic Bootstrap** (Nirmal) | <0.001% | 233,997 | 233,997 | 233,997 | 233,997 |
| **TOTALS** | **100.0%** | **200,000,000,000** | **245,000,233,997** | **204,800,233,997** | **233,997** |

---

## 4. Legal & License Verification Plan

Every planned source must satisfy the project's whitelist policy defined in [`training/v8_4_manifest.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/training/v8_4_manifest.py):
`["Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "CC-BY-4.0", "CC0-1.0", "Open-Data-Commons-Attribution", "ODC-By"]`.

### Legal Verification Matrix

| Source | Declared License | Required Verification Evidence | Legal Action Status |
| :--- | :--- | :--- | :---: |
| **FineWeb-Edu Permissive** | ODC-By | Complete SPDX dataset card validation; verified retention of ODC-By attribution notice in shard header | **REQUIRES REVIEW** |
| **The Stack v2 Permissive** | Apache-2.0 | Software Heritage license detector tags cryptographically matching permissive licenses; opt-out exclusion list applied | **REQUIRES REVIEW** |
| **arXiv Open Access** | CC-BY-4.0 | Metadata parsing confirming paper-level CC-BY-4.0 license; rejection of non-exclusive arXiv perpetual distribution licenses | **REQUIRES REVIEW** |
| **Dolma v1.7 Permissive** | Apache-2.0 | AI2 open science license manifest signed; audit of underlying sub-collections | **REQUIRES REVIEW** |
| **RedPajama v2 Permissive** | Apache-2.0 | Together AI crawl provenance documentation; URL blacklist exclusion audit | **REQUIRES REVIEW** |
| **Wikimedia Open Corpus** | CC0-1.0 | Wikimedia Foundation terms review; verification of CC0 public domain dedication vs CC-BY-SA terms compatibility | **REQUIRES REVIEW** |
| **Nirmal Synthetic Shards** | Apache-2.0 | Internal synthetic pipeline output ([`training/v8_2_data_engine.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/training/v8_2_data_engine.py)); 100% clean provenance | **ACCEPT** |
| **Proprietary Forum Scrapes** | Proprietary | Commercial training prohibition in Terms of Service | **REJECT** |
| **Non-Commercial Academic** | CC-BY-NC-4.0 | CC Non-Commercial clause prohibits commercial use or open weights | **REJECT** |

---

## 5. Storage Plan

Storage calculations are derived directly from [`training/final_size_calculator.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/training/final_size_calculator.py) using the exact 25.91B parameter model and 200B token corpus specification.

### Granular Storage Component Breakdown

1. **Tokenized Corpus (200B Tokens)**:
   - Data Shards: $200\times 10^9 \text{ tokens} \times 2\text{ bytes (uint16)} = \mathbf{400.00\text{ GB}}$ ($\mathbf{372.53\text{ GiB}}$).
   - Document Index Files: ~500M documents $\times 8\text{ bytes (int64)} = \mathbf{4.00\text{ GB}}$ ($\mathbf{3.73\text{ GiB}}$).
   - Total Tokenized Corpus: $\mathbf{404.00\text{ GB}}$ ($\mathbf{376.26\text{ GiB}}$).
2. **Raw Source & Compressed Archives (245B Staged Tokens)**:
   - Compressed JSONL.zst / Parquet (~1.5 bytes/token): $\mathbf{367.50\text{ GB}}$ ($\mathbf{342.26\text{ GiB}}$).
   - Uncompressed UTF-8 Staging Buffer (~3.8 bytes/token): $\mathbf{931.00\text{ GB}}$ ($\mathbf{867.06\text{ GiB}}$).
3. **Deduplication & Contamination Indexes**:
   - Exact SHA-256 Bloom Filter & SQLite Hash Index: $\mathbf{50.00\text{ GB}}$ ($\mathbf{46.57\text{ GiB}}$).
   - MinHash LSH Buckets (64 perms $\times 4\text{ bytes} = 256\text{ bytes/doc}$ for 500M docs): $\mathbf{128.00\text{ GB}}$ ($\mathbf{119.21\text{ GiB}}$).
   - Benchmark 13-gram Inverted Index: $\mathbf{25.00\text{ GB}}$ ($\mathbf{23.28\text{ GiB}}$).
   - Total Dedup & Contamination Index: $\mathbf{203.00\text{ GB}}$ ($\mathbf{189.06\text{ GiB}}$).
4. **Model Checkpoints**:
   - Single Full Checkpoint ($P \times 16\text{ bytes}$: BF16 weights $51.82\text{ GB}$ + FP32 AdamW $310.90\text{ GB}$): $\mathbf{362.71\text{ GB}}$ ($\mathbf{337.80\text{ GiB}}$).
   - Retained Checkpoints ($6\times$: last 5 regular + best validation checkpoint): $\mathbf{2,176.26\text{ GB}} = \mathbf{2.176\text{ TB}}$ ($\mathbf{2,026.80\text{ GiB}} = \mathbf{1.979\text{ TiB}}$).
   - In-Flight Atomic Checkpoint Writing Buffer ($1\times$): $\mathbf{362.71\text{ GB}}$ ($\mathbf{337.80\text{ GiB}}$).
   - Total Checkpoint Allocation: $\mathbf{2,538.97\text{ GB}} = \mathbf{2.539\text{ TB}}$ ($\mathbf{2,364.60\text{ GiB}} = \mathbf{2.309\text{ TiB}}$).
5. **Logs, Telemetry & Metadata Manifests**:
   - Manifests, WandB logs, TensorBoard events, loss curves across 122K steps: $\mathbf{25.00\text{ GB}}$ ($\mathbf{23.28\text{ GiB}}$).

### Aggregate Storage Tier Summary

| Storage Scenario | Decimal Units (GB / TB) | Binary Units (GiB / TiB) | Primary Inclusions |
| :--- | :---: | :---: | :--- |
| **MINIMUM** | **2,500 GB (2.50 TB)** | **2,328 GiB (2.27 TiB)** | 200B shards + 3 checkpoints + compressed raw sources |
| **RECOMMENDED** | **5,000 GB (5.00 TB)** | **4,657 GiB (4.55 TiB)** | 245B raw + staging + 200B shards + 6 checkpoints + dedup indexes |
| **WITH SAFETY HEADROOM** | **7,500 GB (7.50 TB)** | **6,985 GiB (6.82 TiB)** | $1.5\times$ Recommended for parallel eval snapshots & disk IOPS buffer |

---

## 6. GPU Cluster Plan

The compute and memory requirements for Candidate C ($25,908,188,576$ parameters, $4,240,414,112$ active parameters/token) are calculated from the verified analytical resource model in [`training/final_size_calculator.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/training/final_size_calculator.py).

### Baseline Memory Breakdown
- **Static Model State (Whole Model)**:
  - BF16 Weights ($2\text{ bytes/param}$): $51.82\text{ GB}$ ($48.26\text{ GiB}$) [EXACT]
  - BF16 Gradients ($2\text{ bytes/param}$): $51.82\text{ GB}$ ($48.26\text{ GiB}$) [EXACT]
  - FP32 AdamW Optimizer State ($12\text{ bytes/param}$): $310.90\text{ GB}$ ($289.55\text{ GiB}$) [EXACT]
  - **Total Static State**: **414.53 GB (386.06 GiB)** [EXACT]
- **Dynamic Working Memory per GPU (under ZeRO-3 / FSDP FULL_SHARD)**:
  - Checkpointed Activations ($b=1, s=8192$, selective checkpointing): $11.08\text{ GiB}$ [ANALYTICAL ESTIMATE]
  - Unsharded Layer Execution Buffer (gathered MoE block: 2.15B params in BF16): $4.00\text{ GiB}$ [ANALYTICAL ESTIMATE]
  - Autograd & Gradient Accumulation Working Buffer: $4.00\text{ GiB}$ [ANALYTICAL ESTIMATE]
  - Communication & MoE All-to-All Routing Buffers: $4.00\text{ GiB}$ [ANALYTICAL ESTIMATE]
  - CUDA Runtime & PyTorch Caching Driver Overhead: $2.00\text{ GiB}$ [ANALYTICAL ESTIMATE]
  - **Total Dynamic Working Memory per GPU**: **25.08 GiB** [ANALYTICAL ESTIMATE]

### Cluster Size Comparison Table

| Metric | 8 GPUs (1 Node) | 16 GPUs (2 Nodes) | 32 GPUs (4 Nodes) | 64 GPUs (8 Nodes - RECOMMENDED) |
| :--- | :---: | :---: | :---: | :---: |
| **GPU Model & VRAM** | NVIDIA H100 80GB | NVIDIA H100 80GB | NVIDIA H100 80GB | NVIDIA H100 80GB |
| **Static Sharded State / GPU** | **48.26 GiB** [EXACT] | **24.13 GiB** [EXACT] | **12.06 GiB** [EXACT] | **6.03 GiB** [EXACT] |
| **Dynamic Working Memory / GPU** | **25.08 GiB** [EST.] | **25.08 GiB** [EST.] | **25.08 GiB** [EST.] | **25.08 GiB** [EST.] |
| **Peak VRAM / GPU** | **73.34 GiB** [EST.] | **49.21 GiB** [EST.] | **37.14 GiB** [EST.] | **31.11 GiB** [EST.] |
| **Estimated Headroom (80 GiB)** | **6.66 GiB (8.3%)** | **30.79 GiB (38.5%)** | **42.86 GiB (53.6%)** | **48.89 GiB (61.1%)** |
| **Feasibility Assessment** | Tight; OOM risk on spikes | Safe; standard training | Highly comfortable | Highly optimal; high MFU |
| **Interconnect Requirement** | NVLink 4 (900 GB/s) | InfiniBand NDR 400G | InfiniBand NDR 400G | InfiniBand NDR 400G (Rail) |
| **Cluster Verification Status** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** |

---

## 7. Software Environment Specification

To eliminate divergence between local development and production training, the target production software stack is standardized below:

### Production Environment Matrix
- **Operating System:** Ubuntu 22.04 LTS or Ubuntu 24.04 LTS (`x86_64`, Linux kernel `6.8.0+`)
- **Python Runtime:** Python 3.11.9 or 3.12.4
- **Accelerated Compute Framework:** PyTorch 2.4.0+cu124 or 2.5.0+cu124
- **CUDA Toolkit:** CUDA 12.4.1 (Driver $\ge 550.54.14$)
- **Collective Communications:** NCCL 2.20.5+ with AWS OFI NCCL / MLNX_OFED 24.04 InfiniBand verbs
- **Distributed Strategy Configuration:**
  - `ShardingStrategy.FULL_SHARD` (ZeRO-3 equivalent)
  - `BackwardPrefetch.BACKWARD_PRE`
  - `limit_all_gathers = True` (8–16 GPUs) / `False` (64 GPUs)
  - `MixedPrecision(param_dtype=torch.bfloat16, reduce_dtype=torch.bfloat16, buffer_dtype=torch.bfloat16)`
  - Selective activation checkpointing wrapped around [`NirmalBlock`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal 1/src/nirmal/model.py)
- **Production Tokenizer:** ByteLevelBPETokenizer 32,000 vocab, immutable checksum:
  `21e5e370e3e1c0e396f65d19925e851e540ca17e70d4236763326def714251cf`
- **Core Dependencies:**
  `torch==2.4.0`, `numpy==2.1.0`, `transformers==4.44.2`, `flash-attn==2.6.3`, `triton>=3.0.0`, `safetensors>=0.4.4`, `zstandard>=0.23.0`, `pydantic>=2.8.0`, `psutil>=6.0.0`, `wandb>=0.17.0`.

---

## 8. Multi-GPU Validation Plan

When a Linux multi-GPU cluster is provisioned, the following **16-step automated validation procedure** must be executed before pretraining starts:

```
+--------------------------------------------------------------------------------+
|                        MULTI-GPU VALIDATION PROCEDURE                          |
+--------------------------------------------------------------------------------+
 1. GPU Discovery              Assert torch.cuda.device_count() == WORLD_SIZE
 2. NCCL Initialization        dist.init_process_group(backend="nccl", init_method="env://")
 3. All-Reduce Validation      Assert bit-exact dist.all_reduce() across ranks (FP32 & BF16)
 4. All-Gather Validation      Validate tensor gathering across all ranks
 5. Reduce-Scatter Validation  Validate shard scattering across all ranks
 6. FSDP FULL_SHARD Wrapping   Wrap NirmalForCausalLM; assert flat parameter partition is 1/N
 7. BF16 Precision Test        Verify autocast, parameter representations, and buffer dtypes
 8. Activation Checkpointing   Verify backward pass recomputation without memory leakage
 9. Nirmal-1 Forward Pass      Forward pass (s=8192, b=1); verify logits [1, 8192, 32000] & loss
10. Backward Pass               Backward pass; assert gradient propagation through all modules
11. AdamW Optimizer Step       Execute optimizer.step(); verify master weight synchronization
12. Gradient Synchronization   Clip grad norm; assert identical grad norms across all ranks
13. MoE Routing Test           Verify expert assignment, load balancing & all-to-all communication
14. Checkpoint Save            Save sharded checkpoint state dict without file lock conflicts
15. Checkpoint Restore         Reload checkpoint onto clean model; verify bit-exact parameter match
16. Multi-Rank Consistency     Execute 10 steps; assert loss trajectory is identical across ranks
+--------------------------------------------------------------------------------+
```

---

## 9. Production Launch Sequence

The production launch sequence is strictly sequential and fail-closed:

```mermaid
graph TD
    S1[1. DATA SOURCE APPROVAL] --> S2[2. DATA ACQUISITION]
    S2 --> S3[3. DEDUPLICATION]
    S3 --> S4[4. CONTAMINATION CHECK]
    S4 --> S5[5. TOKENIZATION]
    S5 --> S6[6. SHARDING]
    S6 --> S7[7. MANIFEST GENERATION]
    S7 --> S8[8. >=200B VERIFIED TOKENS AUDIT]
    S8 --> S9[9. LINUX CLUSTER PROVISIONED]
    S9 --> S10[10. NCCL VALIDATION]
    S10 --> S11[11. FSDP MULTI-GPU VALIDATION]
    S11 --> S12[12. PILOT TRAINING 500 STEPS]
    S12 --> S13[13. FULL PRETRAINING 122K STEPS]
    S13 --> S14[14. CHECKPOINT VALIDATION]
    S14 --> S15[15. FINAL MODEL PACKAGING]
    S15 --> S16[16. INDEPENDENT EVALUATION]
```

---

## 10. Machine-Checkable Hard Production Gates

Pretraining cannot commence unless all 12 hard production gates pass:

| Gate Identifier | Machine-Checkable Invariant | Current Evaluation | Verdict |
| :--- | :--- | :---: | :---: |
| **GATE A: TOKEN COUNT** | $\ge 200,000,000,000$ physically verified tokens | $233,997\text{ tokens}$ | ❌ **FAIL** |
| **GATE B: SPLIT ISOLATION** | $\text{Train} \cap \text{Val} = \emptyset, \text{Train} \cap \text{Test} = \emptyset, \text{Val} \cap \text{Test} = \emptyset$ | 0 cross-split violations | ✅ **PASS** |
| **GATE C: TOKENIZER HASH** | SHA-256 == `21e5e370e3e1c0e396f65d19925e851e540ca17e70d4236763326def714251cf` | Exact match | ✅ **PASS** |
| **GATE D: SHARD INTEGRITY** | Every `.bin` and `.idx` has valid headers, monotonic offsets, valid checksums | All 6 shards valid | ✅ **PASS** |
| **GATE E: MANIFEST INTEGRITY**| Manifest self-signature and checksum match on-disk files | Verified valid | ✅ **PASS** |
| **GATE F: PROVENANCE** | 100% of documents contain source ID, license tag, timestamp, content hash | Complete | ✅ **PASS** |
| **GATE G: LICENSE COMPLIANCE**| 100% of active sources compliant with permissive license whitelist | Verified clean | ✅ **PASS** |
| **GATE H: LINUX ENVIRONMENT** | Linux OS, Kernel $\ge 6.8$, PyTorch 2.4+, CUDA 12.4+, Driver $\ge 550$ | Windows 11 detected | ❌ **FAIL** |
| **GATE I: NCCL VALIDATION** | NCCL multi-GPU collective communications passing on cluster | Single GPU (No NCCL) | ❌ **FAIL** |
| **GATE J: MULTI-GPU FSDP** | FSDP forward, backward, and optimizer step passing across cluster GPUs | Single GPU only | ❌ **FAIL** |
| **GATE K: CHECKPOINT CYCLE** | Distributed checkpoint save and load bit-exact on cluster storage | Local verified only | ❌ **FAIL** |
| **GATE L: PILOT TRAINING** | 500-step training completed with loss reduction, router entropy $\ge 0.20$ | Not yet executed | ❌ **FAIL** |

---

## 11. Current Production Gap Analysis

The table below contrasts currently verified local assets against full production requirements:

| Resource | Currently Available | Required for Production | Absolute Deficit | Verified? |
| :--- | :---: | :---: | :---: | :---: |
| **Tokens** | **233,997** | **200,000,000,000** | **199,999,766,003** | ❌ **NO (99.999883% deficit)** |
| **GPU Count** | **1 (RTX 3050)** | **8 to 64 (H100 80GB)** | **7 to 63 GPUs** | ❌ **NO** |
| **Total VRAM** | **6.0 GB** | **640 GB to 5,120 GB** | **634 GB to 5,114 GB** | ❌ **NO** |
| **System RAM** | **15.69 GB** | **512 GB to 2,048 GB** | **496 GB to 2,032 GB** | ❌ **NO** |
| **Disk Capacity** | **50.88 GB free** | **5,000 GB to 7,500 GB** | **4,949 GB to 7,449 GB** | ❌ **NO** |
| **Operating System** | **Windows 11** | **Ubuntu 22.04 / 24.04 LTS** | **Linux OS required** | ❌ **NO** |
| **NCCL Interconnect** | **None (Single-GPU)** | **NCCL 2.20+ with InfiniBand** | **Multi-GPU fabric** | ❌ **NO** |
| **Cluster Storage** | **Local NVMe SSD** | **5–8 TB High-IOPS NVMe** | **Production storage** | ❌ **NO** |
| **Networking Fabric**| **Consumer WiFi/Eth**| **InfiniBand NDR 400G (Rail)** | **400G fabric required** | ❌ **NO** |
| **Pretrained Model** | **Untrained Meta/Init**| **25.91B Pretrained Model** | **Full pretraining needed**| ❌ **NO** |
| **Checkpoint Store** | **<10 GB scratch** | **2.5 TB dedicated store** | **~2.5 TB dedicated store**| ❌ **NO** |

---

## 12. Next Action Plan

```
[ IMMEDIATE ACTIONS ]
├── 1. Freeze docs/PRODUCTION_ACQUISITION_PLAN.md and data/production_source_plan.json.
├── 2. Maintain repository integrity (ensure test suite remains 276/276 PASS).
└── 3. Submit the 6 candidate sources to legal review for formal signoff.

[ NEXT STAGE ]
├── 4. Provision minimum 5 TB NVMe staging scratch storage.
├── 5. Execute source-by-source downloading and staging into data/staging/.
└── 6. Run scripts/production_data_acquisition.py --execute until >= 200B verified tokens exist.

[ AFTER DATA ACQUISITION ]
├── 7. Verify Gates A through G (tokens, splits, tokenizer, shards, manifest, provenance, licenses).
├── 8. Provision 8x to 64x H100 80GB Linux GPU cluster with InfiniBand NDR 400G.
└── 9. Run the 16-step multi-GPU validation procedure on Linux (Pass Gates H through K).

[ FINAL PRETRAINING ]
├── 10. Execute 500-step pilot training run (Pass Gate L).
├── 11. Launch 122,070-step production pretraining run on 200B tokens using FSDP FULL_SHARD.
├── 12. Complete final model checkpoint validation, SafeTensors packaging, and evals.
```

---

## 13. Production Readiness Verdict

```
======================================================================
FINAL PRODUCTION READINESS VERDICT
======================================================================
DATA AVAILABLE NOW:           233,997 verified tokens
DATA REQUIRED:                >= 200,000,000,000 verified tokens
DATA DEFICIT:                 199,999,766,003 tokens (99.999883% deficit)
GPU CLUSTER AVAILABLE NOW:    1x NVIDIA GeForce RTX 3050 6GB (Local Laptop)
GPU CLUSTER REQUIRED:         8x to 64x NVIDIA H100 80GB SXM5 (Linux Cluster)
SOFTWARE READY:               YES (Pipeline, Launcher, FSDP, 276/276 Tests Pass)
PRODUCTION TRAINING:          NO-GO
======================================================================
```
