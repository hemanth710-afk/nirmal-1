# V9.3 CAPABILITY QUALITY & GENERALIZATION AUDIT

## Milestone Objective
Determine whether the V9.2 capability-classification system successfully correlates capability labels with training value and helps construct a balanced, diverse curriculum without relying on generic external foundation models.

## Independent System Constraint
Nirmal-1 remains fully independent. No external AI, OpenAI, GPT, Claude, or Gemini models were used in any classification, verification, or curriculum planning pipelines.

## Audit & Component Summaries

### 1. Classifier Quality Audit (`audit_capability_classifier.py`)
- **Metrics Evaluated**:
  - Precision: **0.75**
  - Recall: **0.75**
  - Coverage: **0.75**
  - Unknown Rate: **0.25**
  - Multi-label Rate: **0.25**
- **Ablation Results**: Text-only, Meta-only, and URL-only signals were successfully isolated, demonstrating that the classifier avoids artificial HIGH confidence using source IDs alone.

### 2. Adversarial Capability Tests
- Adversarial tests passed by ensuring the classifier does not fall for single keyword shortcuts, conflicting terminology (e.g., programming keywords within dialogue prose), or misleading metadata. Tested in `test_capability_classifier_adversarial.py`.

### 3. Capability Balance & Mixture
- The `CapabilityMixturePlanner` was extended to include:
  - `raw_distribution`
  - `accepted_distribution`
  - `quality_weighted_distribution`
  - `source_balanced_distribution`
  - `UNKNOWN_distribution`
- Added detection for category collapse (e.g., >50% capabilities missing) and overrepresented capabilities. 

### 4. Quality-Weighted Mixture
- Created `training/acquisition/capability_quality.py`.
- **CapabilityQualityScorer**: Implemented a purely deterministic scoring system (0.0 to 1.0) evaluating document length, punctuation formatting, provenance completeness, and security cleanliness. It successfully outputs quality tiers (HIGH, MEDIUM, LOW) without LLM "intelligence" scoring.

### 5. Curriculum Planner
- Created `training/acquisition/capability_curriculum.py`.
- Established discrete curriculum stages (`FOUNDATION`, `COMPOSITION`, `REASONING`, `PLANNING`, `LONG_HORIZON`, `SPECIALIZATION`, `GENERALIZATION`).
- For each stage, strict requirements are enforced: `target_mix`, `min_quality`, `max_source_concentration`, `max_duplicate_concentration`, and `unknown_tolerance`.

### 6. Generalization / Holdout Design
- The `CapabilityCurriculumPlanner` now manages deterministic splits (`TRAIN`, `VALIDATION`, `OOD_TEST`).
- Leakage is strictly prevented across source, document, revision, near-duplicate hashes, and capability templates (verified in `test_capability_generalization.py`).

### 7. Unknown Handling
- `UNKNOWN` remains an explicit, tracked state in the mixture. Low confidence labels remain visible but do not overwrite explicit `UNKNOWN` categorizations silently.

### 8. Testing Suite
- Added 6 new test files with 42 verified tests in total:
  - `test_capability_classifier_adversarial.py`
  - `test_capability_ablation.py`
  - `test_capability_quality.py`
  - `test_capability_curriculum.py`
  - `test_capability_generalization.py`
  - `test_capability_unknown.py`

### 9. Real Source Pilot & Verifications
- Executed the capability-quality pipeline via the bounded Wikimedia pilot successfully. 
- Validation scripts passed cleanly (`audit_capability_classifier.py`, `report_capability_balance.py`, `verify_source_evidence.py`, `reconcile_source_evidence.py --strict`, `audit_source_claims.py`, `production_data_acquisition.py --synthetic-test / --dry-run`).

## Final Status
- **Capability classifier**: AUDITED
- **Capability mixture**: AUDITED
- **Capability curriculum**: IMPLEMENTED
- **Generalization splits**: VERIFIED
- **Authoritative corpus**: 233,997 TOKENS — UNCHANGED
- **External production approvals**: 0/6
- **Production**: STRICT NO-GO
- **src/nirmal/**: UNCHANGED

*Note: The dataset target is a 95% AGI/ASI-oriented training-data allocation target. This does not represent a measured intelligence score.*
