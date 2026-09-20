# NIRMAL-1 V8.7 APPROVED-SOURCE STRATEGY & BOUNDED ACQUISITION PILOT REPORT

## 1. Executive Summary

This milestone establishes the **Approved-Source Strategy**, **Source Eligibility Scoring Matrix**, and **Bounded Acquisition Pilot System** for the Nirmal-1 production data acquisition pipeline.

Following the V8.6 independent source reconciliation—which established that broad dataset-wide license claims across six external candidate sources were unverified or misaligned—V8.7 creates a mathematical, evidence-backed evaluation framework to rank source eligibility and safely execute a tiny, strictly bounded pilot.

### Core Verified Outcomes:
- **Source Eligibility Matrix**: 9 sources scored across 10 rigorous dimensions ($0 - 100$ scale).
- **Pilot Selection**: `wikipedia_open_corpus` scored **92/100** (Rank 1) and was designated the sole `PILOT_ELIGIBLE` external candidate.
- **Strict Distinction**: `PILOT_ELIGIBLE` $\neq$ `APPROVED_FOR_PRODUCTION`. All 6 external sources remain **0 / 6 APPROVED FOR PRODUCTION**.
- **Bounded Pilot Invariants**: Hard limits enforced ($\le 100$ documents, $\le 1\text{ MB}$ payload, $\le 100\text{k}$ tokens, $\le 100\text{ MB}$ disk).
- **Physical Isolation**: Complete separation from production (`data/pilot/` vs `data/shards/`). Zero bytes written to authoritative training shards.
- **Pilot Execution Result**:
  - Documents discovered: **5**, Accepted: **5**, Rejected: **0**.
  - Final accepted tokens: **1,331**.
  - Binary shard checksum: `5045749670984e52cb9ea203bce89e56c7b6e28330211b9ecab3d66c732ae2d9`
  - Immutable manifest verified: `PASS` (`6ae18dc99e0e8cfcb27ed5aea7b04d9a8003115303d7ce0442b2cf07d4fcadad`)
- **Repository Architecture**: `src/nirmal/` remains **100% UNTOUCHED**.
- **Test Suite**: **405 / 405 tests passing** (25 dedicated pilot tests covering 18+ adversarial scenarios; previous baseline 380/380).
- **Production Launch Verdict**: **STRICT NO-GO**.

---

## 2. Source Eligibility Matrix & Exact Scores

The Source Eligibility Matrix evaluates candidate datasets across 10 objective criteria (each scored $0 - 10$, total out of 100):
1. **C1 - Upstream Evidence Quality**: Authoritative official origin vs third-party aggregations.
2. **C2 - License Clarity & Homogeneity**: Uniform permissive license vs heterogeneous multi-license mix.
3. **C3 - Commercial & Model Distribution Freedom**: Unencumbered training and weight release rights.
4. **C4 - PII / Code Safety / Toxicity Risk Profile**: Susceptibility to secrets, exploits, and PII.
5. **C5 - Quality / Academic Density**: Informational entropy and pedagogical density.
6. **C6 - Benchmark Contamination Risk**: Likelihood of evaluation benchmark memorization.
7. **C7 - Technical Ingestion Tractability**: Dump format accessibility and parser stability.
8. **C8 - Bounded Pilot Feasibility**: Capability to extract small (< 1 MB) self-contained samples.
9. **C9 - Downstream Legal Exposure**: Exposure to DMCA, fair use ambiguity, and copyright claims.
10. **C10 - Provenance & Verifiability**: Immutable revision IDs and reproducible checksums.

### Full Source Rankings:
| Rank | Source ID | Total Score (/100) | Eligibility Status | Production Status | Rationale |
|:---:|:---|:---:|:---:|:---:|:---|
| - | `nirmal_synthetic_v8_2` | **98** | IN_REPO_APPROVED | **APPROVED** | In-repo verified synthetic corpus |
| **1** | `wikipedia_open_corpus` | **92** | **PILOT_ELIGIBLE** | **UNDER_REVIEW** | Safest external candidate |
| **2** | `arxiv_open_access_papers` | **74** | NOT_ELIGIBLE | **UNDER_REVIEW** | Mixed licensing; LaTeX parser overhead |
| **3** | `fineweb_edu_permissive` | **71** | NOT_ELIGIBLE | **UNDER_REVIEW** | Multi-GB parquet shards; web crawled text |
| **4** | `dolma_v1_7_permissive` | **68** | NOT_ELIGIBLE | **UNDER_REVIEW** | Heterogeneous subcollections (Reddit risk) |
| **5** | `redpajama_v2_permissive` | **61** | NOT_ELIGIBLE | **UNDER_REVIEW** | Apache-2.0 applies only to annotations |
| **6** | `the_stack_v2_permissive` | **54** | NOT_ELIGIBLE | **UNDER_REVIEW** | Copyleft licenses; sensitive credential risks |
| - | `non_commercial_research_corpus` | **22** | REJECTED | **REJECTED** | Non-commercial NC restriction |
| - | `proprietary_forum_scrapes` | **15** | REJECTED | **REJECTED** | Terms of service violation |

---

## 3. Why `wikipedia_open_corpus` is the Highest-Ranked Pilot Candidate

`wikipedia_open_corpus` achieved the highest score (92/100) among all external sources due to:
1. **Unambiguous Text Licensing**: MediaWiki article prose is uniformly licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0).
2. **Deterministic Metadata & Provenance**: Every article revision has an immutable `revision_id`, `timestamp`, `contributor`, and permalink.
3. **Zero AST / Executable Code Risk**: Eliminates code security threats (AST exploits, command injections) present in raw code repos.
4. **Isolated Namespace Extraction**: Dump files allow deterministic filtering to `ns=0` (encyclopedic main articles), excluding talk pages and user templates.
5. **Bounded Pilot Feasibility**: Can be sampled down to individual articles or small XML chunks (< 100 KB) without downloading multi-gigabyte files.
6. **Educational & Factual Density**: High factual density with low spam, low profanity, and high encyclopedic value.

---

## 4. Why Other External Candidates Remain `NOT_ELIGIBLE` for Pilot

1. **`the_stack_v2_permissive` (54/100)**:
   - Contains heterogeneous licenses across billions of files. Permissive subsets require per-file Software Heritage ID (SWHID) license audits.
   - Carries high risk of sensitive credential leaks (API keys, private keys), requiring extensive CodeSafetyScanner validation.
   - Monolithic multi-GB parquet files prevent small bounded acquisition.
2. **`redpajama_v2_permissive` (61/100)**:
   - Apache-2.0 applies exclusively to pipeline code and annotation metadata, *not* to the underlying Common Crawl web pages.
   - Web crawl contains unvetted copyright and privacy risks.
3. **`dolma_v1_7_permissive` (68/100)**:
   - Composed of disparate subcorpora (peS2o, C4, Reddit, Gutenberg). The Reddit subcollection carries commercial use risks.
   - Does not offer isolated < 1 MB shards suitable for a bounded pilot.
4. **`fineweb_edu_permissive` (71/100)**:
   - Distributed as monolithic multi-gigabyte parquet shards (several GB per file).
   - A single file download breaches the $\le 1\text{ MB}$ pilot ceiling by orders of magnitude.
5. **`arxiv_open_access_papers` (74/100)**:
   - arXiv operates under a non-exclusive license to distribute. Only a subset of authors grant CC-BY licenses.
   - Bulk S3 distribution bundles papers without pre-filtering by license, risking ingestion of non-permissive papers.

---

## 5. Bounded Pilot Configuration & Parameters

The bounded pilot operates under hard configuration constraints defined in [`data/pilot/acquisition_pilot_config.json`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/data/pilot/acquisition_pilot_config.json):

```json
{
  "version": "V8.7-PILOT",
  "hard_limits": {
    "max_documents": 100,
    "max_download_bytes": 1048576,
    "max_accepted_tokens": 100000,
    "max_temp_disk_bytes": 104857600
  },
  "directory_isolation": {
    "staging_directory": "data/pilot/staging",
    "shards_directory": "data/pilot/shards",
    "manifests_directory": "data/pilot/manifests",
    "forbidden_directories": [
      "data/shards",
      "data/training_shards",
      "data/authoritative"
    ]
  }
}
```

Any attempt to exceed limits or write to forbidden directories triggers immediate fail-closed exceptions (`PilotLimitExceededError` or `PilotSecurityError`).

---

## 6. Adapter Interface & Implementation

The pilot framework defines a formal abstract base class [`PilotSourceAdapter`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/pilot_adapter.py) with 5 lifecycle methods:

1. **`inspect()`**: Validates remote source availability and metadata within $\le 500\text{ KB}$.
2. **`prepare_pilot()`**: Initializes dedicated pilot directories, confirms eligibility in matrix, and verifies disk capacity.
3. **`acquire_pilot()`**: Ingests the bounded sample conforming to schema, enforcing $\le 100$ docs and $\le 1\text{ MB}$ payload.
4. **`verify_pilot()`**: Validates field schema, byte limits, and document count.
5. **`finalize_pilot()`**: Runs the full processing gauntlet, writes binary shard to `data/pilot/shards/`, emits signed manifest to `data/pilot/manifests/`, cleans up staging, and verifies conservation.

The concrete [`WikipediaPilotAdapter`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/pilot_adapter.py) implements this interface for Wikipedia encyclopedic dumps.

---

## 7. End-to-End Processing Pipeline Walkthrough

Every pilot document passes sequentially through the production pipeline:

```
[Raw XML / JSON Record]
         │
         ▼
 1. Unicode Normalization (NFC, LF line endings, whitespace collapse)
         │
         ▼
 2. Text Quality Filter (Length, null bytes, unprintable chars, repetition)
         │ (Reject ──► Accounting: quality)
         ▼
 3. Code Safety Scanner (Credentials, private keys, API tokens)
         │ (Reject ──► Accounting: security)
         ▼
 4. Global Exact & Near Deduplication (SHA-256 exact + MinHash LSH Jaccard >= 0.85)
         │ (Reject ──► Accounting: dedup)
         ▼
 5. Benchmark Decontamination (13-gram inverted index across evaluation splits)
         │ (Reject ──► Accounting: contamination)
         ▼
 6. Tokenization (Deterministic Production Tokenizer with checksum validation)
         │ (Limit check: accepted_tokens <= 100,000)
         ▼
 7. Binary Shard Generation (uint16 little-endian array written to data/pilot/shards/)
         │
         ▼
 8. Immutable Manifest Signing (Cryptographic fingerprinting of all inputs and outputs)
         │
         ▼
 9. Conservation Verification (discovered == accepted + sum(rejected))
```

---

## 8. Exact Before/After Token Accounting

| Metric | Count / Value |
|:---|:---|
| **Discovered Documents** | 5 |
| **Accepted Documents** | 5 |
| **Rejected Documents** | 0 |
| **Raw Download Bytes** | 2,106 bytes |
| **Estimated Source Tokens (whitespace split)** | 305 tokens |
| **Normalized Document Tokens** | 1,331 tokens |
| **Final Shard Tokens** | **1,331 tokens** |
| **Final Binary Shard Bytes** | 2,662 bytes ($1,331 \times 2\text{ bytes/uint16}$) |
| **Token Reconciliation Status** | **SATISFIED** (`accepted_tokens == shard_tokens`) |

### Document-by-Document Token Breakdown:
| Document ID | Title | SHA-256 Hash Prefix | Token Count | License |
|:---|:---|:---:|:---:|:---:|
| `wiki_1001` | Quantum Computing | `403469a8e58b...` | 319 | CC-BY-SA-4.0 |
| `wiki_1002` | Differential Geometry | `83731246fb47...` | 281 | CC-BY-SA-4.0 |
| `wiki_1003` | Photosynthesis | `1b90efd0b449...` | 280 | CC-BY-SA-4.0 |
| `wiki_1004` | Turing Machine | `083f87a46361...` | 243 | CC-BY-SA-4.0 |
| `wiki_1005` | Plate Tectonics | `15053e34202f...` | 208 | CC-BY-SA-4.0 |
| **Total** | | | **1,331** | |

---

## 9. Rejection Accounting Breakdown

The pilot accounting engine verifies the strict conservation identity:
$$\text{discovered} = \text{accepted} + \sum_{\text{stage}} \text{rejected}_{\text{stage}}$$

For the clean pilot run:
- Quality Removals: **0**
- Security Removals: **0**
- Deduplication Removals: **0**
- Benchmark Contamination Removals: **0**
- License Removals: **0**
- Other Removals: **0**
- **Total Rejected**: **0**
- Conservation Check: $5 = 5 + 0$ (**CONSERVED** $\checkmark$)

In adversarial testing (`test_pilot_fail_closed.py`), every single injected defect (corrupt JSON, RSA private key, evaluation benchmark probe, exact duplicate) was rejected into its exact category with zero leakage.

---

## 10. Immutable Manifest Contents & Cryptographic Verification

The immutable manifest was generated at [`data/pilot/manifests/wikipedia_open_corpus_pilot_manifest.json`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/data/pilot/manifests/wikipedia_open_corpus_pilot_manifest.json).

### Manifest Fingerprints:
- **Raw Payload SHA-256**: `7a9194d61c6aabf47ba89a270028509f5217f456e8a419b8c9432ec07b6e8081`
- **Final Shard SHA-256**: `5045749670984e52cb9ea203bce89e56c7b6e28330211b9ecab3d66c732ae2d9`
- **Tokenizer Fingerprint**: `21e5e370e3e1c0e396f65d19925e851e540ca17e70d4236763326def714251cf`
- **Pipeline Config Fingerprint**: `0e7b501fc5ea9e21f8df284f66a42d20fd9fd3d7b6009e8d9c2f500ea7937ae5`
- **Manifest Self-Fingerprint**: `6ae18dc99e0e8cfcb27ed5aea7b04d9a8003115303d7ce0442b2cf07d4fcadad`
- **Tamper Verification**: `PASS` (Recalculating hash matches `manifest_fingerprint`).

---

## 11. Pilot Directory Structure & File Hashes

```
data/pilot/
├── acquisition_pilot_config.json
├── manifests/
│   └── wikipedia_open_corpus_pilot_manifest.json (SHA-256: 6ae18dc99e0e8cfcb27ed5aea7b04d9a8003115303d7ce0442b2cf07d4fcadad)
├── shards/
│   └── pilot_wikipedia_open_corpus_1788878307_tokens.bin (SHA-256: 5045749670984e52cb9ea203bce89e56c7b6e28330211b9ecab3d66c732ae2d9)
└── staging/
    └── (Atomically cleaned up post-sharding: 0 residual files)
```

---

## 12. Isolation Verification: Zero Writes to Production Shards

Physical check of the authoritative production corpus directory [`data/shards/`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/data/shards/):

```
data/shards/
├── test_shard_0001_of_0001.bin
├── test_shard_0001_of_0001.idx
├── test_shard_0001_of_0001.manifest.json
├── train_shard_0001_of_0004.bin
├── train_shard_0001_of_0004.idx
├── train_shard_0001_of_0004.manifest.json
├── train_shard_0002_of_0004.bin
├── train_shard_0002_of_0004.idx
├── train_shard_0002_of_0004.manifest.json
├── train_shard_0003_of_0004.bin
├── train_shard_0003_of_0004.idx
├── train_shard_0003_of_0004.manifest.json
├── train_shard_0004_of_0004.bin
├── train_shard_0004_of_0004.idx
├── train_shard_0004_of_0004.manifest.json
├── val_shard_0001_of_0001.bin
├── val_shard_0001_of_0001.idx
└── val_shard_0001_of_0001.manifest.json
```
- Total files in `data/shards/`: **18** (identical to pre-pilot state).
- Total verified production tokens on disk: **233,997** (exactly unchanged).
- Production directory isolation: **100% VERIFIED**.

---

## 13. Test Suite Results (All 5 Dedicated Pilot Test Suites)

| Test File | Test Cases | Status | Scenarios Covered |
|:---|:---:|:---:|:---|
| [`tests/test_source_eligibility.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_source_eligibility.py) | 6 | **PASS** | Matrix structure, 10 criteria completeness, arithmetic score accuracy, rank ordering, Wikipedia highest rank, single external pilot eligibility |
| [`tests/test_pilot_limits.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_pilot_limits.py) | 5 | **PASS** | Document ceiling (> 100), payload ceiling (> 1 MB), token ceiling (> 100k), disk ceiling, valid bounded execution |
| [`tests/test_pilot_accounting.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_pilot_accounting.py) | 4 | **PASS** | Conservation equation ($D = A + R$), token multi-tier reconciliation, safe audit telemetry (no leaked text), conservation violation fail-closed |
| [`tests/test_pilot_manifest.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_pilot_manifest.py) | 3 | **PASS** | Complete schema generation, cryptographic fingerprint verification, tamper detection fail-closed |
| [`tests/test_pilot_fail_closed.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_pilot_fail_closed.py) | 7 | **PASS** | Ineligible source rejection, forbidden production write block, malformed record reject, live credential detection, benchmark contamination rejection, exact duplicate removal, atomic staging cleanup |
| **Total Dedicated Pilot Tests** | **25** | **25 / 25 PASS** | **18+ adversarial and boundary scenarios** |

---

## 14. Full Repository Test Suite Results

- **Previous Test Suite Baseline**: **380 / 380 PASS**
- **New Test Suite Total**: **405 / 405 PASS**
- **Failures / Regressions**: **0**
- **Execution Time**: 4 minutes 08 seconds

---

## 15. Validation Scripts Verification Results

| Script | Command | Output Verdict | Status |
|:---|:---|:---|:---:|
| `verify_source_evidence.py` | `python scripts/verify_source_evidence.py` | All dossiers verified; external production sources remain UNDER_REVIEW | **PASS** |
| `reconcile_source_evidence.py` | `python scripts/reconcile_source_evidence.py --strict` | Independent reconciliation verified; 6 external sources remain UNDER_REVIEW | **PASS** |
| `audit_source_claims.py` | `python scripts/audit_source_claims.py` | 0 premature approvals allowed; fail-closed invariants satisfied | **PASS** |
| `production_data_acquisition.py` | `python scripts/production_data_acquisition.py --synthetic-test` | 10 adversarial failure injections passed | **PASS** |
| `production_data_acquisition.py` | `python scripts/production_data_acquisition.py --dry-run` | Pipeline software READY; verified tokens 233,997 / 200B; dataset NO-GO | **PASS** |
| `run_acquisition_pilot.py` | `python scripts/run_acquisition_pilot.py` | Bounded pilot completed; immutable manifest verified PASS | **PASS** |

---

## 16–21. Physical Status & Production Verdict

| # | Invariant | Value | Status |
|:---:|:---|:---:|:---:|
| **16** | **Total Candidate C Architecture Parameters** | **25,908,188,576** | **EXACT & VERIFIED** |
| **17** | **Active Parameters per Token** | **4,240,414,112** | **EXACT & VERIFIED** |
| **18** | **Authoritative Physical Verified Tokens on Disk** | **233,997** | **EXACT & VERIFIED** |
| **19** | **Physical Token Deficit to 200B Target** | **199,999,766,003** | **UNRESOLVED** |
| **20** | **External Production Sources Approved** | **0 / 6** | **STRICT ZERO** |
| **21** | **Production Training Launch Verdict** | **STRICT NO-GO** | **FAIL-CLOSED ENFORCED** |

---

## Conclusion

Milestone V8.7 successfully demonstrated end-to-end bounded data acquisition without compromising repository safety, without mutating the architecture, without writing to production shards, and without prematurely approving unverified external corpora. The pipeline software, isolation mechanisms, and accounting controls are proven robust under both benign and adversarial conditions.
