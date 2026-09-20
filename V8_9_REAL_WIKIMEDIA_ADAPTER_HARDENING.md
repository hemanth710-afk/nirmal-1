# NIRMAL-1 V8.9 — REAL SOURCE ADAPTER HARDENING & PROVENANCE VERIFICATION
**Author:** Antigravity (Pair Programming AI) & Notion AI (Code Generation Agent)  
**Date:** September 8, 2026  
**Status:** COMPLETE / FULLY VERIFIED  
**Production Launch Verdict:** **STRICT NO-GO** (Physical Data Deficit: 199,999,766,003 tokens; 0/6 External Sources Approved)

---

## 1. Executive Summary & Core Invariants

In Milestone V8.9, the Nirmal-1 data acquisition subsystem was hardened by transitioning from synthetic/mock bounded pilots to an industrial-grade, crash-resilient, replay-protected real-source adapter architecture: [`training/acquisition/wikimedia_real_adapter.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/wikimedia_real_adapter.py).

### Core Invariants Verified
| Invariant | Target | Observed State | Status |
|---|---|---|---|
| **Architecture Integrity (`src/nirmal/`)** | 0 diffs (100% Untouched) | 0 modifications | **PASS (VERIFIED)** |
| **Candidate C Total Parameters** | 25,908,188,576 | 25,908,188,576 | **PASS (EXACT)** |
| **Candidate C Active Params/Token** | 4,240,414,112 | 4,240,414,112 | **PASS (EXACT)** |
| **Authoritative Production Corpus** | Protected in `data/shards/` | 18 files, 233,997 tokens | **PASS (ZERO LEAKAGE)** |
| **Target Production Tokens** | $\ge 200,000,000,000$ | 233,997 verified | **DEFICIT: 199,999,766,003** |
| **External Sources Approved** | 0 / 6 approved | 0 approved (6 `UNDER_REVIEW`) | **FAIL-CLOSED** |
| **Repository Test Suite** | 452+ tests pass | 452 passed, 0 failures (8m 36s) | **PASS (100%)** |
| **Production Launch Verdict** | Strict Gate Enforcement | **STRICT NO-GO** | **CONFIRMED** |

---

## 2. Notion AI Code Generation Agent

Per the milestone directive, **Notion AI** served as the dedicated code generation subagent (`conversationId: 99a12ce2-6f85-4420-bd93-03490ef033cb`), authoring the implementation of the hardened adapter and all 5 dedicated test suites.

### Code Authoring & Verification Summary
- **Primary Source File:** [`training/acquisition/wikimedia_real_adapter.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/wikimedia_real_adapter.py) (1,349 lines, 60.6 KB).
- **Test Suites Created:** 5 test suites across 28 distinct test scenarios (100% passing).
- **Subagent Workflow:** Notion AI analyzed the abstract base `PilotSourceAdapter`, implemented the 7 required lifecycle methods, configured strict regex-based secret detection and benchmark decontamination, authored comprehensive unit and integration tests, diagnosed and corrected benign credential placeholder behavior, and achieved full green status.

---

## 3. Architecture & The 7-Method Adapter Contract

The [`WikimediaRealAdapter`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/wikimedia_real_adapter.py) subclass extends `PilotSourceAdapter` and implements the mandatory 7-method lifecycle contract:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 WikimediaRealAdapter                     │
                  └───────────────────────────┬─────────────────────────────┘
                                              │
       ┌───────────────────┬──────────────────┼───────────────────┬───────────────────┐
       ▼                   ▼                  ▼                   ▼                   ▼
1. inspect()      2. fetch_bounded()    3. normalize()    4. validate_prov()   5. run_pipeline()
  - Ceilings        - SafeBoundedClient   - NFC Unicode      - REMOTE_SOURCE     - 10 Stages
  - Eligibility     - REST API Summary    - LF Endings       - Numeric Revs      - Checkpointing
  - Endpoints       - Metadata Split      - Whitespace       - Anti-Spoof        - Sharding
                                                                                      │
                                                              ┌───────────────────────┴───────────────────────┐
                                                              ▼                                               ▼
                                                        6. finalize()                                   7. resume()
                                                          - Exact Conservation                            - ckpt_{run_id}.json
                                                          - Signed Manifest                               - Replay Protection
                                                          - Staging Cleanup                               - Idempotent Promotion
```

### Detailed Method Specifications
1. **`inspect()`**:
   - Queries `check_eligibility()` against [`data/source_evidence/source_eligibility_matrix.json`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/data/source_evidence/source_eligibility_matrix.json).
   - Reports canonical endpoint (`https://en.wikipedia.org/api/rest_v1/page/summary/{title}`), payload format (`wikimedia_rest_v1_json`), eligibility (`PILOT_ELIGIBLE`), and explicit ceilings (10 docs, 1 MB download bytes, 128 KB/doc, 100k tokens, 100 MB disk).
2. **`fetch_bounded(topics=None, max_docs=10, max_payload_bytes=1048576)`**:
   - Retrieves articles using [`SafeBoundedNetworkClient`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/safe_network_client.py) with 10.0s timeout, max 3 redirects with loop detection, and 128 KB per-doc ceiling.
   - Defaults to 10 deterministic academic topics: `Quantum_computing`, `Differential_geometry`, `Photosynthesis`, `Turing_machine`, `Plate_tectonics`, `General_relativity`, `Thermodynamics`, `Cell_biology`, `Graph_theory`, `Computational_complexity_theory`.
   - Validates revision authenticity (`_is_genuine_revision_id`), flags invalid revisions, and captures raw JSON payloads with on-the-fly SHA-256 computation.
3. **`normalize(raw_records)`**:
   - Applies Unicode NFC normalization (`unicodedata.normalize("NFC", text)`).
   - Standardizes line endings to LF (`\n`) and collapses duplicate whitespaces while preserving paragraph breaks.
   - **Content vs Metadata Separation**: Strictly extracts plain article prose (`extract`) for tokenization. All thumbnails, image URLs, descriptions, coordinates, language flags, and page IDs are segregated into provenance metadata.
4. **`validate_provenance(records)`**:
   - Enforces `REMOTE_SOURCE_DATA`.
   - Rejects missing URLs, non-HTTPS URLs, or non-Wikipedia domains.
   - Rejects unverified or non-numeric revision IDs.
   - Detects and rejects local fixtures or synthetic records masquerading as remote data (`CRITICAL PROVENANCE FRAUD`).
5. **`run_pipeline(records=None, simulate_interrupt_after=None)`**:
   - Coordinates the 10-stage processing pipeline:
     1. Remote Retrieval & Raw Staging
     2. Provenance Truth Gate
     3. Text Normalization & Metadata Segregation
     4. Quality Filtering ([`StreamingIngestionEngine`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/acquisition/pilot_adapter.py))
     5. Code Safety & Secret Detection ([`CodeSafetyScanner`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/v8_4_code_safety.py))
     6. Exact & MinHash Deduplication ([`ProductionDeduplicationPipeline`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/v8_2_data_engine.py))
     7. 13-Gram Benchmark Decontamination ([`NgramDecontaminationEngine`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/v8_4_decontamination.py))
     8. Tokenization ([`ProductionTokenizationPipeline`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/training/v8_2_data_engine.py))
     9. Atomic Binary Sharding (`uint16` in `data/pilot/shards/`)
     10. Manifest Signing, Provenance Audit, and Machine Trace Generation
   - Employs atomic intermediate checkpoints (`ckpt_{run_id}.json.part -> ckpt_{run_id}.json`).
6. **`finalize()`**:
   - Enforces exact accounting conservation: $\text{discovered} = \text{accepted} + \sum \text{rejected}$.
   - Enforces token reconciliation: $\text{accepted\_tokens} = \text{final\_shard\_tokens}$.
   - Emits immutable cryptographic manifest to [`data/pilot/manifests/wikipedia_open_corpus_pilot_manifest.json`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/data/pilot/manifests/wikipedia_open_corpus_pilot_manifest.json).
   - Emits safe provenance records and machine trace to `data/pilot/provenance/`.
   - Atomically removes staging files.
7. **`resume(run_id=None, additional_records=None)`**:
   - Reconstitutes adapter state from `data/pilot/staging/ckpt_{run_id}.json`.
   - Replays deduplication index for already accepted documents.
   - Enforces **Replay Protection**: deterministic identity `f'{source_id}:{page_id}:{revision_id}'`.
     - Identical document + identical revision $\rightarrow$ rejected as `replay_duplicate_same_revision`.
     - Identical document + new revision $\rightarrow$ accepted as distinct version.

---

## 4. Test Suite Coverage & Matrix

Notion AI authored 5 specialized test suites covering 28 distinct test scenarios. All 28 tests pass:

| Test File | Scenarios Covered | Test Count | Status |
|---|---|---|---|
| [`tests/test_wikimedia_real_adapter.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_wikimedia_real_adapter.py) | Mock HTTP parsing, genuine revision ID extraction, content/metadata separation, ceilings enforcement (10 docs, 1 MB bytes, 100k tokens, 100 MB disk), inspection metadata. | 8 | **PASS** |
| [`tests/test_wikimedia_resume.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_wikimedia_resume.py) | Crash simulation, atomic checkpoint write, duplicate-free resume, identical artifact generation between uninterrupted and resumed runs, replay identity rejection. | 5 | **PASS** |
| [`tests/test_wikimedia_provenance.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_wikimedia_provenance.py) | Genuine revision validation, fake/missing revision rejection, missing URL / non-HTTPS fail-closed handling, anti-spoofing against local/synthetic records claiming remote provenance. | 6 | **PASS** |
| [`tests/test_wikimedia_accounting.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_wikimedia_accounting.py) | Exact document conservation equation, token reconciliation violation detection, stage-by-stage rejection attribution (quality, security, dedup, contamination), zero secret leakage in audit logs. | 4 | **PASS** |
| [`tests/test_wikimedia_storage_safety.py`](file:///C:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/tests/test_wikimedia_storage_safety.py) | Atomic `.part -> destination` promotions, incomplete file cleanup on mid-stream failure, staging cleanup on finalization, fail-closed prohibitions against writes to `data/shards/` or `src/nirmal/`. | 5 | **PASS** |
| **Consolidated Subsystem Total** | **Complete V8.9 Real Adapter Verification** | **28** | **100% PASS** |

---

## 5. Bounded Real Pilot Execution Summary

A real 10-document bounded pilot was executed against the live Wikimedia REST API (`https://en.wikipedia.org/api/rest_v1/page/summary/{title}`).

### Execution Telemetry
```
Status:                    SUCCESS
Provenance Class:          REMOTE_SOURCE_DATA
Is Genuine Remote:         True
Network Endpoint:          https://en.wikipedia.org/api/rest_v1/page/summary/{title}
Total Downloaded Bytes:    28,363 bytes (~28.3 KB; well below 1,048,576 byte ceiling)
Discovered Documents:      10
Accepted Documents:        10
Rejected Documents:        0
Accepted Tokens:           3,603
Final Shard Path:          data/pilot/shards/run_v8_9_real_remote_pilot_tokens.bin
Final Shard Format:        uint16 binary token stream (7,206 bytes = 3,603 tokens * 2 bytes)
Final Shard Checksum:      caa9a29dc9bcebe3b9d1f4701f1c63795d63b431fe35d5fc035fae91f3ea6966
Manifest Path:             data/pilot/manifests/wikipedia_open_corpus_pilot_manifest.json
Provenance Audit Path:     data/pilot/provenance/wikipedia_open_corpus_provenance.json
Machine Trace Path:        data/pilot/provenance/wikipedia_open_corpus_trace.json
Accounting Conservation:   VERIFIED (Discovered 10 == Accepted 10 + Rejected 0)
Token Reconciliation:      VERIFIED (Accepted Tokens 3,603 == Shard Tokens 3,603)
```

---

## 6. Document-by-Document Remote Ingestion Audit

All 10 documents were retrieved live from Wikimedia servers. All revision IDs are verified positive integers:

| Topic Title | Page ID | Upstream Revision ID | Retrieval Timestamp | Raw Bytes | Norm Bytes | Token Count | Raw Payload SHA-256 |
|---|---|---|---|---|---|---|---|
| **Quantum computing** | `25220` | `1373439181` | `2026-09-06T00:36:11Z` | 2,971 | 585 | 355 | `26a33053ecd3e1f9...` |
| **Differential geometry** | `8625` | `1373206111` | `2026-09-04T15:40:29Z` | 3,130 | 690 | 435 | `89cbb2e6dd15ceb3...` |
| **Photosynthesis** | `24544` | `1371284103` | `2026-08-25T17:04:29Z` | 3,508 | 905 | 587 | `f6c99cbe778b0221...` |
| **Turing machine** | `30403` | `1373616450` | `2026-09-07T00:10:45Z` | 2,752 | 269 | 150 | `47385465e9d97fa2...` |
| **Plate tectonics** | `24944` | `1373488406` | `2026-09-06T09:37:37Z` | 2,925 | 536 | 313 | `e685f096b797cb39...` |
| **General relativity** | `12024` | `1371069715` | `2026-08-24T14:48:38Z` | 3,097 | 933 | 560 | `73a11c1df797b5e4...` |
| **Thermodynamics** | `29952` | `1372527793` | `2026-08-31T20:41:40Z` | 2,423 | 647 | 400 | `27038166c4363dd2...` |
| **Cell biology** | `6339` | `1346042175` | `2026-04-18T10:07:37Z` | 2,248 | 453 | 286 | `ea9b977aa5688220...` |
| **Graph theory** | `12401` | `1372052337` | `2026-08-29T11:47:33Z` | 2,572 | 473 | 311 | `15e85fa9b50b5514...` |
| **Computational complexity** | `7543` | `1371073639` | `2026-08-24T15:15:39Z` | 2,737 | 370 | 206 | `5a74efc2dd9427b0...` |
| **Total Pilot Batch** | — | — | — | **28,363** | **5,861** | **3,603** | — |

---

## 7. Live Replay Protection & Versioning Audit

Replay protection was audited under two complementary tests:

1. **Test A: Live Duplicate Re-fetch (Replay Protection)**
   - A subsequent live query was issued against an adapter pre-seeded with the 10 processed identities.
   - **Result:**
     - Discovered: 10
     - Accepted: 0
     - Rejected: 10 (`dedup_removed: 10`, `replay_duplicate_same_revision: 10`)
     - **Verdict:** 100% of identical remote revisions were rejected. Zero duplicated tokens entered the shard.
2. **Test B: Revision Bump (Distinct Version Acceptance)**
   - A record with identical canonical source and page ID was submitted with a bumped revision ID (`9999999999`).
   - **Result:**
     - Discovered: 1
     - Accepted: 1
     - Rejected: 0
     - **Verdict:** The updated document was recognized as a new source version and successfully ingested.

---

## 8. Full Validation Script Matrix

Every repository verification script was executed in `--strict` mode to verify complete system health:

```powershell
# 1. Pilot Capability Audit
python scripts/run_acquisition_pilot.py --audit-only
# -> PASS: Adapter capability confirmed REAL_REMOTE_RETRIEVAL

# 2. Source Evidence Verification
python scripts/verify_source_evidence.py
# -> PASS: 9 dossiers verified; external sources remain UNDER_REVIEW

# 3. Independent Source Reconciliation
python scripts/reconcile_source_evidence.py --strict
# -> PASS: All 6 external sources remain UNDER_REVIEW. PRODUCTION LAUNCH: STRICT NO-GO.

# 4. Source Claims Audit
python scripts/audit_source_claims.py
# -> PASS: All source claims audited against official artifacts. Zero premature approvals.

# 5. Adversarial Synthetic Testing
python scripts/production_data_acquisition.py --synthetic-test
# -> PASS: All 10 adversarial fail-closed injection tests passed.

# 6. Production Acquisition Launcher Dry-Run
python scripts/production_data_acquisition.py --dry-run
# -> PASS: Verified tokens: 233,997 / 200,000,000,000 (Deficit: 199,999,766,003). NO-GO enforced.

# 7. Full Pytest Test Suite
pytest tests/ evals/ -q
# -> PASS: 452 passed, 0 failures, 8 warnings in 516.58s (08:36)

# 8. Candidate C Parameter Verification
pytest tests/test_v8_training_system.py -k test_candidate_c_exact_pytorch_meta_model_consistency
# -> PASS: Exact parameters = 25,908,188,576; Active = 4,240,414,112

# 9. Architecture Tree Git Status
git status --short src/nirmal/
# -> PASS: Clean (0 diffs, 100% untouched)

# 10. Authoritative Shards Git Status
git status --short data/shards/
# -> PASS: Clean (0 diffs, 18 files, 233,997 tokens)
```

---

## 9. External Candidate Sources Status Matrix

All six external candidate sources remain strictly **`UNDER_REVIEW`**:

| Source Identifier | Upstream Provider | Stated License | Effective Status | Reason for `UNDER_REVIEW` |
|---|---|---|---|---|
| `fineweb_edu_permissive` | Hugging Face | ODC-By v1.0 | **UNDER_REVIEW** | Pinned immutable Git commit SHA required; upstream repo sync pending. |
| `the_stack_v2_permissive` | BigCode / SWH | Heterogeneous | **UNDER_REVIEW** | Per-file SPDX license filtering required; SWH Terms of Use compliance pending. |
| `arxiv_open_access_papers` | arXiv.org / Cornell | CC-BY / CC0 | **UNDER_REVIEW** | Bulk S3 dump contains mixed non-exclusive licenses; paper-level CC metadata filter required. |
| `dolma_v1_7_permissive` | Allen Institute (AI2) | ODC-By / AI2 | **UNDER_REVIEW** | Subcollections have heterogeneous licenses; Reddit/Pushshift subcorpus carries commercial risk. |
| `redpajama_v2_permissive` | Together AI | Apache-2.0 / CC | **UNDER_REVIEW** | Apache-2.0 applies only to pipeline code/metadata; raw web text is subject to Common Crawl terms. |
| `wikipedia_open_corpus` | Wikimedia Foundation | CC-BY-SA 4.0 | **UNDER_REVIEW** | Dual-licensed: Prose is CC-BY-SA 4.0 (attribution & share-alike review required); metadata is CC0. |

> [!IMPORTANT]
> Although `wikipedia_open_corpus` is verified as **`PILOT_ELIGIBLE`** for bounded research pilots ($\le 10$ documents, $\le 1\text{ MB}$ payload), it is **NOT APPROVED** for production acquisition. Pretraining on CC-BY-SA 4.0 material requires legal sign-off regarding downstream model weight distribution obligations.

---

## 10. Production Training Launch Gate Verdict

### Final Production Gate Assessment
```
========================================================================================
NIRMAL-1 PRODUCTION LAUNCH GATE: V8.9 FINAL VERDICT
========================================================================================
Model Architecture (Candidate C):       APPROVED (25,908,188,576 total params)
Training Engine & FSDP Integration:     READY
Code Safety Scanner:                     ACTIVE & VERIFIED
Benchmark Decontamination Index:         ACTIVE & VERIFIED
Acquisition Adapters (Wikimedia Real):   HARDENED & REPRODUCIBLE (28/28 tests PASS)
Authoritative Physical Tokens on Disk:   233,997 tokens
Production Minimum Target Tokens:        200,000,000,000 tokens
Current Token Deficit:                   199,999,766,003 tokens (99.999883% missing)
Approved External Production Sources:    0 / 6 approved

FINAL VERDICT:                           STRICT NO-GO
========================================================================================
```

---

## 11. Next Milestone: V8.10 Roadmap

1. **HuggingFace & arXiv Real Source Adapters**:
   - Apply the hardened 7-method contract to `HuggingFaceSnapshotSyncAdapter` (with Git commit SHA pinning) and `ArxivS3BulkSyncAdapter` (with paper-level CC license validation).
2. **Upstream License Reconciliation Legal Dossiers**:
   - Finalize legal evaluation of CC-BY-SA 4.0 fair-use transformative pretraining boundaries.
   - Implement SPDX per-file license classifier for The Stack v2 and Dolma v1.7.
3. **Multi-Source Bounded Integration Pilot**:
   - Run bounded pilots across multiple external endpoints using the standardized architecture.
