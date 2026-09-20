# NIRMAL-1 V10.10-SPEC-AMENDMENT-01 — APPROVED PROSPECTIVE SPECIFICATION

**Approval status:** Explicitly approved by the user as a new prospective scientific specification.

**Authorized scope:**

- amendment implementation;
- non-scientific implementation and safety validation;
- the previously authorized V10.9 continuity validation;
- return of a complete correction/revalidation report.

**Not authorized:**

- Phase A;
- Phase B;
- Phase C;
- Phase D;
- Phase E;
- Phase F;
- scientific V10.10 training;
- confirmation testing or confirmation-test access;
- locked testing or locked-test access;
- Candidate C;
- production training;
- architecture intervention;
- V10.11.

The amendment below is reproduced verbatim from the user-approved `V10.10-SPEC-AMENDMENT-01`. Its internal pre-approval status wording is retained unchanged as part of the verbatim approved text; the approval declaration above governs the artifact's current status.

---

# A. V10.10 AMENDMENT VERSION

**Proposed version:** `V10.10-SPEC-AMENDMENT-01`

**Status:** Prospective proposal awaiting explicit user approval.

This amendment creates five new scientific design decisions that were not recoverable from the original V10.10 materials:

1. numeric development and confirmation seeds;
2. token-level S1/S2/S3 definitions;
3. token-level Q1/Q2/Q3 definitions;
4. exact frozen L0/L1 identities;
5. numerical and logical G0–G6 criteria.

These are **NEWLY FROZEN AMENDMENT DECISIONS**, not recovered historical facts. No V10.10 scientific result was used to select them.

The following are **RECOVERED HISTORICAL FACTS**, not new choices:

- V10.9 F8 used L1, peak learning rate 0.001, batch size 256, 1,000 steps, and seed 42.
- The V10.9 continuity replay passed its historical tolerances.
- The authoritative corpus contains exactly 233,997 tokens.
- Candidate C has 25,908,188,576 parameters and has received zero updates.
- Production is STRICT NO-GO with 0/6 external approvals.

# B. FIVE NEWLY FROZEN DEFINITIONS

## 1. Seeds

### Root seeds

| Purpose | Frozen seed IDs |
|---|---|
| Development | `104729`, `130363`, `155921` |
| Confirmation | `196613`, `262147`, `393241` |

All six values are distinct. Seed 42 is not used in either new set.

These seed IDs are fixed prospectively and must not be changed after implementation validation or in response to model behavior.

### Deterministic namespace derivation

Every pseudorandom stream must derive its effective seed from this exact UTF-8 string:

```text
NIRMAL-1|V10.10-SPEC-AMENDMENT-01|purpose={purpose}|root={root_seed}|split={split}|level={level}|serialization={serialization}|query={query}|control={control}|index={index}|stream={stream}
```

Derivation procedure:

1. Compute SHA-256 over the exact UTF-8 string.
2. Interpret the first eight digest bytes as an unsigned 64-bit big-endian integer.
3. Compute `effective_seed = value mod 9223372036854775783`.
4. If the result is zero, use one.
5. Record the complete derivation string and effective seed in the manifest.

Allowed `purpose` values are exactly:

- `development`
- `confirmation`
- `diagnostic`
- `locked-test`
- `implementation-fixture`

Allowed primary `split` values are:

- `train`
- `development`
- `confirmation`
- `diagnostic`
- `locked-test`

Purpose and split must agree. A generator must reject, for example, `purpose=development` with `split=locked-test`.

Diagnostic streams use the `diagnostic` purpose and are never derived from a development or confirmation purpose string. Locked-test streams use `locked-test`. Namespace separation is therefore cryptographic and semantic even if another field is accidentally reused.

Implementation fixtures must never be accepted as scientific data.

### Access rules

- Development seeds may be used for configuration selection.
- Confirmation seeds may be accessed only after the configuration-selection record is frozen and hashed.
- Diagnostic episodes may not determine primary configuration selection.
- Locked-test episodes may be generated or decrypted only after confirmation criteria pass and the final analysis artifact is frozen.
- Locked-test access is one-time for a benchmark version.
- Seed 42 remains historical only and is excluded from the amended scientific campaign.

---

## 2. S1/S2/S3

### Symbol table

V10.10 uses a synthetic, direct integer-token interface. It does not modify any production tokenizer.

| ID/range | Symbol or role |
|---:|---|
| 0 | `<PAD>` |
| 1 | `<BOS>` |
| 2 | `<EOS>` |
| 3 | `<PAIR_OPEN>` |
| 4 | `<PAIR_CLOSE>` |
| 5 | `<KEY>` |
| 6 | `<VALUE>` |
| 7 | `<MAP>` |
| 8 | `<PAIR_SEP>` |
| 9 | `<RECORD_SEP>` |
| 10 | `<QUERY>` |
| 11 | `<LOOKUP>` |
| 12 | `<ANS>` |
| 13 | `<FILL>` |
| 14 | `<BAG>` |
| 15–31 | Reserved; prohibited in primary episodes |
| 32–63 | Key atoms |
| 64–95 | Value atoms |
| 96–127 | Diagnostic/noise atoms; prohibited in primary keys, values, and answers |

A key or value is a nonempty sequence of atoms from its designated range. Key and value atoms are always disjoint.

### Common support-stream structure

Every primary prompt begins with `<BOS>`, followed by all support records in the episode’s selected order, followed by a fixed-width query slot. The prompt terminates at `<ANS>`.

Every support record, including the final record, must contain its specified terminal boundary token. Missing or doubled boundaries are parser failures.

### S1 — canonical serialization

For every pair `(k, v)`:

```text
<KEY> k <MAP> <VALUE> v <PAIR_SEP>
```

Complete support:

```text
<BOS>
<KEY> k1 <MAP> <VALUE> v1 <PAIR_SEP>
...
<KEY> kN <MAP> <VALUE> vN <PAIR_SEP>
```

Properties:

- `<KEY>` begins the key span.
- `<MAP>` terminates the key span and declares the relation.
- `<VALUE>` begins the value span.
- `<PAIR_SEP>` terminates the value and record.
- Record order is the sampled support order.

Scientific purpose: S1 is the readable canonical key→value representation and serves as the primary reference serialization.

### S2 — structured serialization

For every pair `(k, v)`:

```text
<PAIR_OPEN> <KEY> k <VALUE> v <PAIR_CLOSE> <RECORD_SEP>
```

Complete support:

```text
<BOS>
<PAIR_OPEN> <KEY> k1 <VALUE> v1 <PAIR_CLOSE> <RECORD_SEP>
...
<PAIR_OPEN> <KEY> kN <VALUE> vN <PAIR_CLOSE> <RECORD_SEP>
```

Properties:

- `<PAIR_OPEN>` and `<PAIR_CLOSE>` explicitly scope one record.
- `<KEY>` and `<VALUE>` identify roles.
- `<VALUE>` also terminates the variable-length key span.
- `<PAIR_CLOSE>` terminates the variable-length value span.
- `<RECORD_SEP>` is required after every record.

Scientific purpose: S2 tests whether explicit roles and record boundaries improve access to the correct episode-local relation.

### S3 — compact relational serialization

For every pair `(k, v)`:

```text
k <MAP> v <RECORD_SEP>
```

Complete support:

```text
<BOS>
k1 <MAP> v1 <RECORD_SEP>
...
kN <MAP> vN <RECORD_SEP>
```

Properties:

- The key begins immediately after `<BOS>` or the prior `<RECORD_SEP>`.
- `<MAP>` terminates the key span.
- `<RECORD_SEP>` terminates the value and record.
- No redundant role or bracket token is present.

Scientific purpose: S3 tests relational access with minimal structural overhead while retaining an explicit mapping operator.

### Padding and filler rules

- `<FILL>` is used only before the fixed-width query slot.
- It must never occur inside a key, value, or serialized pair.
- For matched comparisons, the query slot begins at the same absolute token index across S1–S3.
- The required support-slot width is the maximum valid primary support length for the compared cell.
- Shorter support streams receive `<FILL>` immediately before the query slot.
- `<FILL>` positions are excluded as attention keys/values and excluded from loss and scoring, but retain positional indices so the query position remains matched.
- `<PAD>` is used only after `<EOS>` for batch shape matching.
- `<PAD>` is excluded from attention, loss, and all metrics.
- Padding or filler may never truncate a support pair or answer span.

### Parser and round-trip invariants

For every valid episode and serialization:

1. Parsing must recover the ordered list of exact `(key-sequence, value-sequence)` pairs.
2. `parse(serialize(episode))` must equal the original ordered episode.
3. `serialize(parse(tokens))` must reproduce the same non-padding token stream byte-for-byte.
4. Duplicate structural markers, unclosed pairs, empty key/value spans, out-of-range atoms, malformed boundaries, and trailing non-padding tokens must fail closed.
5. Parsing must not inspect the target label.
6. The three primary conditions are exactly S1, S2, and S3.

F-A–F-D may remain only as deprecated legacy fixtures or explicitly exploratory aliases. No F-format result may influence primary selection, gates, classifications, stopping decisions, or primary multiplicity families.

---

## 3. Q1/Q2/Q3

### Common query rules

- The primary query slot occurs after the support stream.
- The queried support-record index is balanced exactly within each level, seed, split, serialization, and query format, with stratum counts differing by at most one.
- Query formats are crossed independently with S1–S3.
- The prompt terminates immediately after `<ANS>`.
- No target-value token may appear after the query key and before `<ANS>`.
- The answer is never part of the inference prompt.
- For scoring, the evaluator supplies the target value only as a label or teacher-forced continuation.
- Only the complete target-value span is scored.
- Prompt tokens, query-key tokens, structural markers, `<ANS>`, `<EOS>`, `<FILL>`, and `<PAD>` are excluded from primary scoring and loss.

### Q1 — explicit canonical query

```text
<QUERY> <KEY> q <ANS>
```

- Prefix: `<QUERY> <KEY>`
- Query key: immediately after `<KEY>`
- Answer marker: `<ANS>`
- Key span: from the token after `<KEY>` through the token before `<ANS>`
- Termination: immediately after `<ANS>`

Scientific interpretation: an explicit instruction-like query naming the role of the query span.

### Q2 — relational completion query

```text
q <MAP> <ANS>
```

- Prefix: none
- Query key: begins at query-slot content start
- Relation marker: `<MAP>`
- Answer marker: `<ANS>`
- Key span: from query-slot content start through the token before `<MAP>`
- Termination: immediately after `<ANS>`

Scientific interpretation: compact completion of the same relation used in the support records.

### Q3 — lookup query

```text
<LOOKUP> <PAIR_OPEN> <KEY> q <PAIR_CLOSE> <ANS>
```

- Prefix: `<LOOKUP> <PAIR_OPEN> <KEY>`
- Query key: immediately after `<KEY>`
- Closing marker: `<PAIR_CLOSE>`
- Answer marker: `<ANS>`
- Key span: from the token after `<KEY>` through the token before `<PAIR_CLOSE>`
- Termination: immediately after `<ANS>`

Scientific interpretation: an explicit lookup operation distinct from support-record serialization.

### Query length matching

For a given key length:

1. Compute the longest Q1/Q2/Q3 query sequence.
2. Create a query slot of that exact width.
3. Right-align the semantic Q sequence so `<ANS>` occupies the same final index.
4. Place `<FILL>` only at the beginning of shorter query slots.
5. The parser ignores leading query-slot `<FILL>` tokens.
6. Query-slot start, `<ANS>` position, and full prompt length must match across Q1–Q3.

For multi-token answers, if the target is `v1 … vm`, primary value-span scoring evaluates exactly the `m` answer tokens following `<ANS>`. Whole-span exact match is one only when every token and the answer length match.

---

## 4. L0/L1

These are new V10.10 research-model identities. They do not modify production architecture.

### Common architecture

- Decoder-only causal Transformer.
- Pre-LayerNorm.
- Learned token embeddings.
- Learned absolute positional embeddings.
- Full causal multi-head self-attention.
- Attention projections: separate Q, K, V, and output projections, all with biases.
- Feed-forward block: two biased linear layers with exact GELU activation.
- Dropout: zero.
- Final LayerNorm.
- Token embedding and output projection weights tied.
- No output-head bias.
- Vocabulary size: 128, using the direct integer symbol table above.
- Context length: 256 tokens.
- Inputs longer than 256 tokens are invalid; truncation is prohibited.
- Floating-point training state must be FP32.
- No pretrained checkpoint or production weight is used.

### L0

| Field | Frozen value |
|---|---|
| Hidden size | 32 |
| Decoder layers | 2 |
| Attention heads | 2 |
| Head dimension | 16 |
| Intermediate size | 128 |
| Vocabulary size | 128 |
| Context length | 256 |
| Expected trainable parameters | **37,632** |
| Fingerprint | `V10.10-A01-L0-h32-L2-a2-d16-ff128-v128-c256-preLN-GELU-tied-noLMbias` |

### L1

| Field | Frozen value |
|---|---|
| Hidden size | 64 |
| Decoder layers | 4 |
| Attention heads | 4 |
| Head dimension | 16 |
| Intermediate size | 256 |
| Vocabulary size | 128 |
| Context length | 256 |
| Expected trainable parameters | **224,128** |
| Fingerprint | `V10.10-A01-L1-h64-L4-a4-d16-ff256-v128-c256-preLN-GELU-tied-noLMbias` |

### Parameter-count convention

Count every unique trainable scalar exactly once. Tied embedding/output weights are counted once.

For hidden size `h`, intermediate size `i`, layer count `L`, vocabulary `V=128`, and context length `C=256`:

\[
P=Vh+Ch+L(4h^2+2hi+7h+i)+2h
\]

The terms cover token embeddings, positional embeddings, biased Q/K/V/O projections, two LayerNorms per block, biased feed-forward layers, and final LayerNorm.

An implementation whose count differs by even one trainable scalar fails identity validation.

### Initialization

For every root seed:

- all linear and embedding weights: independent normal distribution with mean 0 and standard deviation 0.02;
- all linear biases: zero;
- all LayerNorm scale parameters: one;
- all LayerNorm bias parameters: zero;
- no parameter may be initialized from a legacy, pretrained, or production checkpoint.

Initialization uses a dedicated `stream=model-initialization` namespace.

### Optimizer

- AdamW.
- `beta1=0.9`
- `beta2=0.999`
- `epsilon=1e-8`
- weight decay `0.01`
- global gradient-norm clipping at `1.0`
- no warm-up;
- constant learning rate within each learning-rate cell;
- batch size 128 episodes;
- no gradient accumulation;
- one step equals one completed AdamW update.

LayerNorm parameters and bias terms are excluded from weight decay; matrix weights and embeddings are included.

### Exclusions

- L2 and L3 are excluded.
- Candidate C is excluded.
- No production architecture or checkpoint may be instantiated.
- Legacy counts 84,000 and 170,048 are **not adopted**.
- The amendment prospectively freezes 37,632 and 224,128 as the only valid L0/L1 counts.

---

## 5. G0–G6

Unless otherwise stated:

- development evaluation uses at least 1,000 newly generated episodes per seed and cell;
- confirmation evaluation uses exactly 2,000 episodes per confirmation seed and cell;
- locked-test evaluation uses exactly 4,000 episodes per confirmation-trained model and primary cell;
- all three required seeds must be reported;
- no averaging may conceal a failing seed.

### G0 — Artifact integrity

**Inputs**

- protected-path snapshots;
- production-configuration snapshot;
- corpus count;
- Candidate C access/update log;
- benchmark and generator manifests;
- tokenizer/symbol-table fingerprint;
- split and namespace audits;
- episode and mapping collision audits;
- truncation audit;
- test-access log.

**Metrics and thresholds**

- protected-path differences: exactly 0;
- production-configuration differences: exactly 0;
- corpus tokens: exactly 233,997;
- Candidate C instantiations, evaluations, and updates: exactly 0;
- external approvals: exactly 0/6;
- production status: exactly STRICT NO-GO;
- hash mismatches: 0;
- malformed records: 0;
- cross-split exact episode collisions: 0;
- cross-split order-invariant episode collisions: 0;
- unauthorized locked-test accesses: 0;
- truncated prompts or answer spans: 0;
- target-count imbalance within a required stratum: maximum minus minimum no greater than 1;
- query-position count imbalance: maximum minus minimum no greater than 1.

**Confidence interval**

Not applicable; all conditions are deterministic invariants.

**Pass**

All conditions equal their required values.

**Fail**

Any single invariant fails or cannot be verified.

**Stopping consequence**

Classify `INVALID`; stop all V10.10 execution. Do not inspect outcomes further.

### G1 — Harness validity

**Inputs**

- serializer/parser round-trip fixtures;
- control-generation fixtures;
- value-span scoring fixtures;
- multi-token fixtures;
- namespace fixtures;
- manifest-tampering fixtures;
- negative leakage and malformed-record fixtures;
- V10.9 continuity replay.

**Minimum sample size**

At least 1,000 generated episodes for every combination of:

- B0–B5;
- S1–S3 where applicable;
- Q1–Q3;
- CORRECT, RANDOM, WRONG, primary ABSENT, and secondary ABSENT.

B0 uses its applicable identity-control forms.

**Metrics and thresholds**

- valid-case round-trip success: 100%;
- malformed-case rejection: 100%;
- answer leakage: 0 cases;
- non-answer tokens entering primary score: 0 cases;
- incorrect answer-span lengths accepted: 0 cases;
- invalid derangements accepted: 0;
- incorrect targeted lures accepted: 0;
- primary/secondary ABSENT misclassification: 0;
- V10.9 continuity checks: all within the frozen historical tolerances.

**Confidence interval**

Not applicable to deterministic fixtures. The continuity replay uses its historical tolerance rules.

**Pass**

All implementation fixtures pass and continuity passes.

**Fail**

Any fixture fails, scoring is ambiguous, or continuity fails.

**Stopping consequence**

Stop before scientific training. Classify `INVALID` unless a documented benchmark-construction defect requires `TASK_CONSTRUCTION`.

### G2 — Positive control

**Inputs**

B0 identity-copy results for all three confirmation seeds, 2,000 episodes per seed.

**Metrics**

- whole-value-span exact-match accuracy;
- 95% Wilson interval per seed;
- target-span mean log probability;
- NaN/Inf count.

**Thresholds**

For every confirmation seed:

- exact match at least 0.99;
- Wilson 95% lower bound at least 0.98;
- NaN/Inf count exactly 0;
- target-span mean log probability after training must exceed step-0 value by at least 0.50 natural-log units.

**Pass**

Every threshold passes for every seed.

**Fail**

Any seed fails any threshold.

**Stopping consequence**

Stop the ladder and all binding interpretation. Do not proceed to B2 or later gates. Apply `TASK_CONSTRUCTION` only if a documented task defect explains failure; otherwise the experiment cannot support a binding conclusion.

### G3 — Negative-control specificity

**Inputs**

Paired B2 confirmation episodes under:

- CORRECT;
- RANDOM;
- WRONG;
- primary ABSENT (`absent_unpaired`).

Secondary placeholder ABSENT is reported but cannot determine G3.

**Metrics**

For every seed:

- CORRECT−RANDOM exact-match difference;
- CORRECT−WRONG exact-match difference;
- CORRECT−ABSENT exact-match difference;
- WRONG lure exact match minus original-target exact match;
- paired target-span log-probability differences.

**Thresholds**

For every confirmation seed:

- each CORRECT−control exact-match difference must be at least 0.10;
- WRONG lure exact match minus original-target exact match must be at least 0.10.

Across seeds:

- Holm-adjusted two-sided 95% hierarchical-bootstrap interval for each of the three CORRECT−control contrasts must have lower bound greater than 0;
- adjusted `p < 0.05` for all three contrasts.

**Pass**

Every per-seed margin and every adjusted cross-seed requirement passes.

**Fail**

Any required contrast or lure-specificity condition fails.

**Stopping consequence**

Do not claim core binding. Do not open the locked test. Continue only with preregistered task/serialization diagnostics that do not use locked-test data.

### G4 — Core binding

**Inputs**

Frozen selected configuration evaluated once on locked B1 and B2 test episodes, with 4,000 episodes per trained confirmation-seed model and level.

**Metrics**

- CORRECT whole-span exact match;
- Wilson 95% interval per model seed;
- primary CORRECT−ABSENT paired contrast;
- target-span log-probability contrast;
- G3 specificity contrasts.

**Thresholds**

For every model seed:

- B1 CORRECT exact match at least 0.90;
- B1 Wilson lower bound at least 0.88;
- B2 CORRECT exact match at least 0.80;
- B2 Wilson lower bound at least 0.78;
- B1 and B2 CORRECT−primary-ABSENT difference at least 0.10.

Across seeds:

- hierarchical-bootstrap 95% lower bound for B1 and B2 CORRECT−ABSENT must be greater than 0;
- Holm-adjusted `p < 0.05` for both level contrasts;
- G3 remains passed on the corresponding locked cells.

**Pass**

All requirements pass.

**Fail**

Any requirement fails.

**Stopping consequence**

Do not classify `ASSOCIATIVE_BINDING_ESTABLISHED`. Continue only to preregistered diagnostic classification steps; do not modify architecture.

### G5 — Robustness

**Inputs**

Locked or preregistered untouched robustness cells covering:

- S1–S3;
- Q1–Q3;
- B3–B5;
- support-order reversal;
- query-record position;
- query-slot location;
- record distance;
- neutral filler;
- multi-token spans;
- B5 prefix-overlap strata.

**Minimum sample size**

2,000 episodes per model seed and robustness cell. Every position or overlap stratum must contain at least 200 episodes per seed.

**Thresholds**

For every seed:

- B3 CORRECT exact match at least 0.75;
- B4 CORRECT exact match at least 0.60;
- B5 CORRECT exact match at least 0.45;
- CORRECT−primary-ABSENT difference at least 0.10 at B3, B4, and B5;
- maximum minus minimum B2 query-record-position accuracy no greater than 0.10;
- minimum B2 position accuracy at least 0.70;
- absolute support-order reversal difference no greater than 0.05;
- absolute matched-filler difference no greater than 0.05;
- prefix-overlap versus non-overlap accuracy gap no greater than 0.10;
- no S or Q primary format may trail the best S or Q format by more than 0.10 on matched B2 cells.

Across seeds:

- Holm-adjusted 95% hierarchical-bootstrap lower bound for every B3–B5 CORRECT−ABSENT contrast must be greater than 0;
- adjusted `p < 0.05`;
- no required robustness contrast may reverse sign in any seed.

**Pass**

All thresholds pass for all required cells and seeds.

**Fail**

Any threshold fails or any required cell is missing.

**Stopping consequence**

Core binding, if G4 passed, may be classified only as partial unless the classification precedence identifies a higher-priority serialization, representation, context-access, or other limitation. Do not treat G5 failure as architecture authorization.

### G6 — Scaling

**Inputs**

Matched L0 and L1 results using identical:

- development/confirmation/locked episodes;
- initialization-root policy;
- S/Q/control conditions;
- optimizer family;
- learning-rate grid;
- step grid;
- batch size;
- selection rule;
- evaluation metrics.

Minimum evaluation is 4,000 locked episodes per model seed and primary cell.

**Metric**

\[
\Delta_{\mathrm{scale}}
=
\operatorname{EM}_{L1,\mathrm{CORRECT}}
-
\operatorname{EM}_{L0,\mathrm{CORRECT}}
\]

Primary scaling comparison is B2. B3–B5 are secondary scaling comparisons.

**Permitted conclusive outcomes**

A **capacity-effect conclusion** requires all of:

- L1 passes G4;
- L0 fails G4 after the complete fair optimization grid;
- `Δscale ≥ 0.10` in every seed;
- hierarchical-bootstrap 95% lower bound greater than 0;
- Holm-adjusted `p < 0.05`.

A **no-material-scaling conclusion** requires all of:

- L0 and L1 have the same G4 pass/fail outcome;
- the two-sided 95% hierarchical-bootstrap interval lies entirely within `[-0.05, 0.05]`.

**Pass**

All fairness requirements are met and one permitted conclusive outcome is obtained.

**Fail/inconclusive**

Fairness is violated, neither conclusion satisfies its interval requirements, or seed effects conflict.

**Stopping consequence**

Report G6 as inconclusive. Do not assert a capacity limit. No production or architecture action follows automatically.

### Summary Boolean

```text
all_passed = G0 and G1 and G2 and G3 and G4 and G5 and G6
```

`all_passed` is reporting convenience only. It is not a gate and does not replace G6.

# C. COMPLETE STATISTICAL FREEZE

## Primary endpoint

The primary inferential endpoint is the paired B2 locked-test difference in whole-value-span exact match:

\[
\Delta_{\mathrm{primary}}
=
\operatorname{EM}_{\mathrm{CORRECT}}
-
\operatorname{EM}_{\mathrm{ABSENT\_UNPAIRED}}
\]

The unit of pairing is the complete base episode: mapping, query key, target value, support order, serialization, query format, and position assignment.

## Control freeze

- Primary ABSENT: `absent_unpaired`.
- Secondary ABSENT: `absent_placeholder`.
- No maximum, minimum, best-of, or stronger-of selection is allowed.
- CORRECT, RANDOM, WRONG, and both ABSENT variants must be reported separately.

## Sample sizes

- Development: minimum 1,000 episodes per development seed and cell.
- Confirmation: exactly 2,000 episodes per confirmation seed and cell.
- Locked core test: exactly 4,000 episodes per trained confirmation-seed model and cell.
- Robustness: 2,000 episodes per model seed and cell, with at least 200 per required stratum.

Increasing a frozen sample size after inspecting outcomes is prohibited. Operational loss of episodes invalidates that cell unless the loss was covered by a prospectively documented deterministic exclusion rule.

## Hierarchical bootstrap

Use exactly 10,000 replicates.

For replicate `b`:

1. Sample three seed slots with replacement from the three confirmation model seeds.
2. For each selected seed occurrence, sample that seed’s base-episode indices with replacement, using the original per-seed episode count.
3. For each sampled episode index, retrieve both paired outcomes from the same base episode.
4. Compute the mean paired difference within each selected seed occurrence.
5. Compute the unweighted mean of the three selected seed-level means.
6. Store that replicate’s statistic.

If a seed is selected twice, perform independent within-seed episode resampling for each occurrence.

The same procedure applies to log-probability contrasts.

## Confidence intervals

- Binary accuracy within a single seed: two-sided 95% Wilson interval.
- Paired cross-seed contrasts: two-sided 95% percentile interval from the 10,000 hierarchical-bootstrap replicates.
- Report the 2.5th and 97.5th empirical percentiles.
- Gate language referring to a lower bound uses the lower endpoint of this two-sided interval.
- No normal-theory substitution is permitted.

## Hypothesis tests

For a directional paired contrast, compute the unadjusted bootstrap p-value as:

\[
p=2\min\left(
\frac{1+\#(\Delta_b\le0)}{10001},
\frac{1+\#(\Delta_b\ge0)}{10001}
\right)
\]

Cap at one.

## Holm families

Apply Holm–Bonferroni separately to these preregistered families:

1. **Specificity family:** B2 CORRECT−RANDOM, CORRECT−WRONG, and CORRECT−primary-ABSENT.
2. **Core family:** B1 and B2 CORRECT−primary-ABSENT.
3. **Serialization family:** S2−S1 and S3−S1 on matched B2 CORRECT accuracy.
4. **Query family:** Q2−Q1 and Q3−Q1 on matched B2 CORRECT accuracy.
5. **Ladder family:** B3, B4, and B5 CORRECT−primary-ABSENT.
6. **Scaling family:** L1−L0 at B2, B3, B4, and B5.

Exploratory formats and secondary ABSENT analyses are not included in primary families and cannot change primary decisions.

## Configuration selection

- Development-only selection.
- Rank candidates first by passing G0–G2.
- Among eligible candidates, maximize B2 development CORRECT−primary-ABSENT.
- Break exact ties using B2 CORRECT whole-span exact match.
- Break any remaining exact tie by lexicographic configuration identifier.
- Freeze at most two configurations for confirmation.
- After confirmation begins, no configuration, seed, threshold, metric, or analysis rule may change.

## Reporting

Every report must include:

- every seed;
- every executed cell;
- every failed and aborted cell;
- sample counts;
- point estimates;
- intervals;
- raw and Holm-adjusted p-values;
- target-span log probability;
- lure metrics;
- stop reason;
- excluded-episode count and reason;
- all secondary and exploratory results clearly separated.

Selective omission is prohibited.

# D. COMPLETE STOPPING-RULE FREEZE

| Trigger | Exact condition | Required action |
|---|---|---|
| Artifact integrity | Any G0 invariant fails or cannot be verified | Abort immediately; classify INVALID; do not inspect scientific outcomes further. |
| Leakage | Any answer token appears in a prompt, any forbidden split collision occurs, or confirmation/locked data influence selection | Abort affected and downstream phases; invalidate exposed test version. |
| Parser failure | Any valid record fails round-trip or malformed record is accepted | Stop before training or stop the active run; repair only after a new review. |
| Scoring failure | Any non-answer token enters primary scoring, answer length is mishandled, or whole-span scoring cannot be reproduced | Abort; invalidate all results produced by that scorer. |
| Protected path | Any change under `src/nirmal/` or `data/shards/` | Abort immediately; restore only under user-controlled production governance; V10.10 remains invalid. |
| Corpus count | Count differs from exactly 233,997 | Abort immediately; do not recount as a new baseline. |
| Candidate C | Any attempted instantiation, evaluation, loading, update, or training | Abort immediately and record a critical safety violation. |
| Production configuration | Any detected difference | Abort immediately. |
| NaN/Inf | Any NaN or Inf in loss, logits, parameters, gradients, optimizer state, metric, or confidence calculation | Stop the affected run immediately; mark it failed, not missing; do not silently restart with changed settings. |
| Test invalidation | Locked-test hash mismatch, premature access, leakage, mutation, or analysis change after opening | Retire the entire locked-test version; never reuse it. |
| Failed B0 | Any G2 condition fails | Stop before B2 and later binding claims. |
| Failed primary controls | G3 fails | Do not open locked test; do not claim core binding. |
| Compute ceiling | Any run requests more than 64 optimizer updates, more than 128 episodes per update, or unapproved gradient accumulation | Reject before execution. |
| Confirmation failure | No frozen candidate passes confirmation G2 and G3 | Stop; do not access locked test. |
| Missing seed/cell | Required seed or cell result is absent | Gate fails; do not average over remaining results. |
| Unapproved specification change | Seed, threshold, format, query, model, metric, or analysis differs from this amendment | Stop and request a versioned amendment. |

## Invalidated locked test

After invalidation:

1. mark the current benchmark version permanently invalid;
2. preserve its manifest and access log;
3. do not delete or overwrite its results;
4. increment the benchmark version;
5. generate a new locked-test namespace using the new version string;
6. create new files and hashes;
7. perform implementation-only validation;
8. obtain explicit user approval before reopening testing.

An invalidated locked test may never be rehabilitated by regenerating the same seed namespace.

# E. COMPLETE CLASSIFICATION FREEZE

Evaluate classifications in this exact order. Stop at the first satisfied condition.

1. **INVALID**  
   G0 or G1 fails; locked-test integrity is compromised; scoring, parsing, leakage, protected scope, or required evidence is invalid.

2. **TASK_CONSTRUCTION**  
   Integrity is otherwise valid, but a documented benchmark or task construction defect explains the result and a prospectively corrected task passes the applicable validation. No model-limit conclusion is allowed.

3. **SERIALIZATION_LIMIT**  
   A preregistered alternate primary serialization passes G4 while the canonical serialization fails, with a matched accuracy gain of at least 0.10 in every seed and a Holm-adjusted hierarchical-bootstrap lower bound greater than zero.

4. **OPTIMIZATION_LIMIT**  
   The initially referenced optimization point fails G4, but another preregistered LR/step cell passes G4, with at least 0.10 gain in every seed and a Holm-adjusted lower bound greater than zero.

5. **CAPACITY_LIMIT**  
   L0 fails G4 after the complete fair optimization grid, L1 passes G4, and G6 satisfies the capacity-effect criterion.

6. **REPRESENTATION_LIMIT**  
   Integrity, task, serialization, optimization, and capacity explanations are ruled out; preregistered held-out relation probes remain at or below their shuffled-label-adjusted threshold while identity probes pass. Probe thresholds require a separately frozen Phase E diagnostic specification before use.

7. **CONTEXT_ACCESS_LIMIT**  
   Earlier explanations are ruled out; held-out relation information is decodable, but preregistered correct→absent/wrong patching and reverse interventions show that the native prediction does not causally access it. Intervention thresholds require a separately frozen Phase E specification before use.

8. **ASSOCIATIVE_BINDING_FAILURE**  
   G0–G3 pass, all higher-priority explanations are ruled out, G4 fails across both L0 and L1, and no partial criterion is satisfied.

9. **PARTIAL_ASSOCIATIVE_BINDING**  
   G4 passes but G5 does not, or preregistered evidence is above chance and control-specific but does not satisfy every G4 requirement.

10. **ASSOCIATIVE_BINDING_ESTABLISHED**  
    G0–G5 pass; no higher-priority classification applies; B1/B2 locked-test core criteria and required causal-specificity criteria pass across all confirmation-trained model seeds.

Earlier classifications always override later classifications. G6 may support a capacity conclusion but is not required to establish binding for a single approved scale. No classification authorizes production training, Candidate C, architecture changes, or V10.11.

# F. RATIONALE FOR EACH NEW DESIGN DECISION

## Seeds

The six prime-valued roots are arbitrary with respect to model behavior, mutually distinct, and fixed before scientific execution. Their purpose is reproducibility and separation—not favorable random outcomes. Excluding seed 42 avoids overlap with the historical replay and the earlier invalid development/confirmation arrangement.

## Serialization

S1–S3 vary structural explicitness while keeping the same episode, mapping, answer, and causal question:

- S1 is a canonical labeled mapping;
- S2 makes pair and role boundaries explicit;
- S3 minimizes structural overhead while preserving a relation operator.

This tests whether apparent failure is serialization-specific without introducing a fourth primary condition.

## Queries

Q1–Q3 express the same lookup request through instruction-like, relational-completion, and explicit-lookup forms. Right-aligned fixed-width slots prevent prompt length or answer position from explaining format differences.

## Model identities

The new L0/L1 definitions are small enough for synthetic micro-scale study but sufficiently separated for a meaningful capacity comparison. Both use the same architecture family and token interface. Width, depth, heads, and feed-forward size change prospectively and transparently. Exact formulas prevent silent architectural drift.

The legacy 84,000 and 170,048 counts are deliberately not adopted because their authority could not be established.

## Gates

The gates separate validity from scientific evidence:

- G0 and G1 establish whether interpretation is permissible.
- G2 establishes learnability of the positive control.
- G3 requires causal specificity.
- G4 tests the core unseen-episode binding claim.
- G5 tests robustness against alternative explanations.
- G6 limits scaling conclusions to a fair replicated comparison.

Absolute accuracy thresholds prevent statistically significant but scientifically weak effects from passing. Per-seed requirements prevent pooled averages from hiding instability. Confidence intervals and Holm correction control uncertainty and multiplicity.

## Statistical design

The primary paired CORRECT−unpaired-ABSENT contrast isolates relation use better than aggregate accuracy or placeholder removal. Outer seed resampling represents initialization/training variability; inner episode resampling represents episode variability. Fixing 10,000 replicates prospectively prevents result-dependent precision choices.

# G. WHAT REMAINS UNCHANGED FROM ORIGINAL V10.10

The following remain unchanged:

- the central scientific question;
- evidence must come from unseen episodes with newly sampled mappings;
- aggregate accuracy alone is insufficient;
- CORRECT, RANDOM, WRONG, and ABSENT causal controls are required;
- B0 is an identity-copy positive control;
- B1/B2 are foundational binding tasks;
- representation probes are diagnostic, not causal;
- architecture intervention requires completion of the approved diagnostic prerequisites;
- classification precedence governs interpretation;
- V10.9 chance-level binding did not prove architectural, capacity, optimization, representation, or context-access impossibility;
- `src/nirmal/` remains unchanged;
- `data/shards/` remains unchanged;
- the authoritative corpus remains exactly 233,997 tokens;
- Candidate C remains at zero updates and must not be instantiated;
- external approvals remain 0/6;
- production remains STRICT NO-GO;
- production configuration remains unchanged;
- V10.9 history remains unchanged;
- no production training is authorized;
- no architecture intervention is authorized;
- no automatic progression to V10.11 is authorized;
- Phase F remains prohibited unless separately and prospectively specified.

# H. ANTIGRAVITY IMPLEMENTATION SPECIFICATION

After—and only after—explicit user approval of this amendment, Antigravity may:

1. update only V10.10 research-harness, specification, manifest, matrix, reporting, and test files;
2. implement the six frozen seed roots and exact namespace derivation;
3. implement the exact 128-symbol table;
4. implement S1, S2, and S3 as the only primary serializations;
5. implement Q1, Q2, and Q3 with fixed-width right-aligned query slots;
6. implement variable-length key/value sequences and whole-span scoring;
7. implement the newly frozen L0 and L1 identities and exact parameter-count checks;
8. reject all other model scales, including L2, L3, and Candidate C;
9. implement G0–G6 exactly;
10. implement the statistical and stopping rules exactly;
11. implement the frozen classification order;
12. retire the existing V10.10 benchmark manifest because its definitions no longer match the amendment;
13. create a new implementation-validation benchmark version under an amendment-specific namespace;
14. preserve the earlier benchmark and manifest as superseded historical artifacts;
15. update tests to validate the amendment prospectively.

Antigravity must not:

- run Phase A or any scientific training;
- use development, confirmation, diagnostic, or locked outcomes to alter the amendment;
- modify protected production paths or production configuration;
- modify the corpus or V10.9 record;
- instantiate Candidate C;
- treat legacy F/Q/model/gate definitions as primary;
- delete failed or superseded artifacts.

Only deterministic generation fixtures, parser/scorer tests, negative safety fixtures, parameter-count validation, manifest validation, and the previously authorized V10.9 continuity check may be run during implementation revalidation.

# I. ANTIGRAVITY REVALIDATION CHECKLIST

Antigravity must return evidence for every item below.

## Governance and scope

- [ ] User approval of `V10.10-SPEC-AMENDMENT-01` recorded before changes.
- [ ] Complete changed-file list.
- [ ] Zero changes to `src/nirmal/`.
- [ ] Zero changes to `data/shards/`.
- [ ] Zero production-configuration changes.
- [ ] Corpus count exactly 233,997.
- [ ] Candidate C: zero instantiations, evaluations, and updates.
- [ ] External approvals 0/6.
- [ ] Production STRICT NO-GO.
- [ ] V10.9 history unchanged.
- [ ] Phases A–F not run.

## Seeds and partitions

- [ ] Development roots exactly `104729,130363,155921`.
- [ ] Confirmation roots exactly `196613,262147,393241`.
- [ ] No overlap.
- [ ] SHA-256 namespace derivation matches the specified test vectors generated during implementation.
- [ ] Diagnostic and locked-test purpose strings are isolated.
- [ ] Confirmation access requires a frozen-selection artifact.
- [ ] Locked-test access requires a passed confirmation artifact.
- [ ] Locked-test access log and one-time guard work.

## Serialization and queries

- [ ] Exact S1 round-trip tests pass.
- [ ] Exact S2 round-trip tests pass.
- [ ] Exact S3 round-trip tests pass.
- [ ] Primary format enumeration contains exactly S1–S3.
- [ ] F formats cannot enter primary selection, gates, classification, or multiplicity.
- [ ] Exact Q1/Q2/Q3 parsing passes.
- [ ] Query slots are right-aligned and length matched.
- [ ] Query-slot start and `<ANS>` positions match.
- [ ] Prompt terminates at `<ANS>`.
- [ ] No answer token leaks into prompts.
- [ ] Only complete value spans are scored.
- [ ] Key, marker, filler, padding, and delimiter tokens are excluded.

## Benchmark construction

- [ ] B0 identity-copy is distinct from binding.
- [ ] B1/B2/B3/B4/B5 contain 1/2/4/8/16 pairs.
- [ ] B4 includes multi-token keys and values.
- [ ] B5 includes sixteen pairs and required prefix-overlap strata.
- [ ] Target and query positions differ in count by no more than one.
- [ ] Exact and order-invariant duplicate detection passes.
- [ ] Cross-split collisions are zero.
- [ ] All sequences fit within 256 tokens.
- [ ] Truncation is impossible and tested.
- [ ] Primary absent is always unpaired.
- [ ] Placeholder absent remains secondary.
- [ ] No stronger-of logic exists.

## Model identity

- [ ] L0 count is exactly 37,632.
- [ ] L1 count is exactly 224,128.
- [ ] Every architecture field matches its fingerprint.
- [ ] Initialization fixtures match the frozen rules.
- [ ] AdamW configuration matches exactly.
- [ ] Batch size is 128 with no accumulation.
- [ ] One step equals one optimizer update.
- [ ] Only L0 and L1 are accepted.
- [ ] L2, L3, Candidate C, and production configurations are rejected.

## Gates, statistics, and stopping

- [ ] G0–G6 are seven separate gates.
- [ ] Every gate has the exact inputs, thresholds, formulas, and consequences above.
- [ ] `all_passed` is only a summary.
- [ ] Seed-level failures cannot be hidden by pooling.
- [ ] Hierarchical bootstrap resamples seeds, then paired episodes.
- [ ] Exactly 10,000 replicates are used.
- [ ] Wilson and percentile intervals match reference fixtures.
- [ ] Holm families are separate and exact.
- [ ] Every executed cell is reported.
- [ ] Missing cells fail rather than disappear.
- [ ] Each stopping trigger has a negative fixture.
- [ ] Invalidated locked tests require a new version.
- [ ] Classification precedence matches the exact ten-item order.
- [ ] Every earlier classification overrides every later one.

## Permitted revalidation results

- [ ] All non-scientific implementation tests pass.
- [ ] Negative fixtures fail closed.
- [ ] V10.9 continuity remains within historical tolerance.
- [ ] No V10.10 model-learning, accuracy, control, probe, causal, robustness, capacity, or scaling result is generated.

# J. EXPLICIT APPROVAL BOUNDARY

This document is a **proposed prospective amendment**, not evidence that the amendment has been approved, implemented, validated, or scientifically executed.

User approval of the amendment would authorize only:

1. amendment-scoped implementation;
2. non-scientific revalidation;
3. return of a compliance report.

It would not authorize:

- Phase A;
- any V10.10 scientific training;
- confirmation or locked-test access;
- Candidate C;
- production training;
- architecture intervention;
- Phase F;
- V10.11.

After implementation and revalidation, a separate compliance review must determine whether Phase A can be authorized.

**Phase A remains unauthorized until the user explicitly approves this new V10.10 specification amendment and Antigravity successfully implements and revalidates it.**