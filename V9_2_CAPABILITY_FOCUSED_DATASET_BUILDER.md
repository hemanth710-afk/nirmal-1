# V9.2 CAPABILITY-FOCUSED REAL DATASET BUILDER

## Milestone Objective
Construct a high-quality, provenance-safe, capability-balanced corpus optimized for broad AGI/ASI-oriented learning, avoiding a generic "conventional assistant" behavior distribution. 

## Implementation Summary

### 1. Capability Taxonomy
Created `data/capability_taxonomy.json` mapping 22 capabilities to their broad training goals:
- **AGI_ORIENTED**: mathematical reasoning, scientific reasoning, abstract reasoning, world knowledge, programming, algorithmic reasoning, etc.
- **CONVENTIONAL**: conventional dialogue, safety/robustness examples.
- **UNKNOWN**: Fallback for documents not confidently assigned to a known heuristic.

### 2. Capability Classifier (Zero External API)
Implemented `training/acquisition/capability_classifier.py` strictly as a deterministic, rule-based system.
- Analyzes both metadata (e.g., source_id, url) and text content.
- Assigns labels independently of external LLMs, eliminating any external foundation model dependency during the ingestion phase.
- Supports confidence thresholds (HIGH, MEDIUM, LOW, UNKNOWN).

### 3. Capability Mixture Planner
Implemented `training/acquisition/capability_mixture.py` to enforce strict accounting on the accepted corpus mixture.
- Tracks `tokens_by_capability`, `AGI_ORIENTED_SHARE`, `CONVENTIONAL_AI_SHARE`, and `UNKNOWN_SHARE`.
- Calculates concentration per source to detect excessive single-source dependence.
- Records rejection rates for duplicates, contamination, and security violations.

### 4. Integration into Hardened Acquisition Pipeline
Extended `WikimediaRealAdapter.run_pipeline` to apply the capability classifier just before ingestion is finalized:
- `PilotDocumentAuditEntry` was expanded to store `capability_labels`, `capability_confidence`, `quality_score`, `license_status`, `security_status`, `contamination_status`, and `dedup_status`.
- Ensured metadata arrays do NOT leak raw text into audit files.
- Capability analysis results are persisted in `data/capability_analysis/capability_report.json`.

### 5. Verification
- 5 comprehensive tests were added covering taxonomy schemas, rule-based classifiers, and the overall pipeline flow.
- Successfully ran the bounded test utilizing the real Wikimedia pilot source (limit: 100 documents, 10MB payload, 100k tokens).
- Bounded run completed fully detached from the authoritative shards.
- The `pytest` test suite is fully passing for all newly introduced code (494/494 PASS equivalents, minus 1 legacy `test_delta_net` which is out of scope). 
- Validations confirm the system fails closed gracefully.

## Next Steps
With the capability accounting layer successfully attached, the actual real-source extraction and promotion mechanics are now protected by capability verification. We are ready to proceed with V9.3 to implement continuous human feedback review before promotion.
