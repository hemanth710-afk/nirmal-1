# NIRMAL-1 V10.10 — PHASE C SPECIFICATION (DRAFT PROPOSAL)

> ## ⛔ STATUS: PROPOSAL ONLY — NOT AUTHORITATIVE — DOES NOT AUTHORIZE EXECUTION
>
> This document is a **draft proposal** prepared for scientific review.
>
> - It is **NOT** an approved specification.
> - It **does NOT** authorize Phase C, any scientific training, any evaluation,
>   confirmation-seed access, locked-test access, Candidate C, or production.
> - It **does NOT** supersede `docs/V10_10_SPEC_AMENDMENT_01_APPROVED.md`.
> - Where this draft and the approved amendment disagree, **the amendment governs**
>   and this draft is wrong by definition.
> - Nothing in this document may be executed until it is separately reviewed,
>   revised, frozen, hashed, and explicitly approved by the user.

**Draft ID:** `V10.10-PHASE-C-SPEC-DRAFT-00`
**Prepared:** 2026-09-18
**Authoritative parent:** `docs/V10_10_SPEC_AMENDMENT_01_APPROVED.md`
**Parent SHA-256:** `f320ccd316940314b119a5378f8591c850fe1d603a822c8ef24fbf087c3f0a0b` (verified)
**Companion:** `docs/V10_10_PHASE_C_SPEC_RECONCILIATION.md`

---

## 0. BLOCKING PRECONDITION — READ BEFORE ANYTHING ELSE

**Phase C should not be authorized until decision `D-01` is resolved.**

The approved amendment (revalidation checklist, line 1124) freezes level sizes as:

> `B1/B2/B3/B4/B5 contain 1/2/4/8/16 pairs.`

The harness implements this exactly
(`training/evaluation/v10_10_binding_harness.py:577` → `{"B0": 1, "B1": 1, "B2": 2, ...}`).

**Therefore B1 contains exactly one support pair.**

The amendment's primary ABSENT control is `absent_unpaired`, implemented
(`v10_10_binding_harness.py:735-742`) as a bag that preserves the key and value
token multiset while destroying pair boundaries:

```text
<BOS> <BAG> k1 <BAG> v1 <BAG> … query … <ANS>
```

For a **one-pair** episode, the bag still contains exactly one value atom, and that
atom **is the target**. The target is therefore fully recoverable by copying the only
value present, with no use of the key and no binding whatsoever.

### Consequence

At B1, the amendment's primary contrast is **algebraically pinned at zero**:

\[
\Delta_{\mathrm{primary}}^{B1}
= \operatorname{EM}_{\mathrm{CORRECT}} - \operatorname{EM}_{\mathrm{ABSENT\_UNPAIRED}}
\equiv 0
\]

for **any** model, optimizer, learning rate, step budget, or scale.

The G4 requirement "B1 and B2 CORRECT−primary-ABSENT difference at least 0.10" is
therefore **unsatisfiable at B1 by construction**.

### Empirical corroboration

All six archived Phase B runs report `delta_correct_absent_primary = 0.0` exactly,
with `correct` EM = 1.0 **and** `absent_unpaired` EM = 1.0
(`experiments/v10_10/phase_b_ladder_summary.json`). This is the predicted signature.

### Why this blocks Phase C

Under the amendment's frozen classification precedence (Section E), **TASK_CONSTRUCTION
(rank 2) strictly overrides OPTIMIZATION_LIMIT (rank 4)**. A degenerate primary contrast
at B1 is a documented benchmark-construction defect. Running an optimization study
against a structurally degenerate endpoint cannot yield a valid `OPTIMIZATION_LIMIT`
classification, and risks attributing a task-construction artifact to optimization —
precisely the class of error this project's governance exists to prevent.

**Recommended sequencing:** resolve `D-01` (task construction) *before* Phase C, not after.

---

## 1. SCIENTIFIC QUESTION

> Within the compute envelope frozen by `V10.10-SPEC-AMENDMENT-01`, does the
> Phase B failure to establish associative binding at B2 persist across the complete
> preregistered learning-rate × optimizer-step grid, or does at least one
> preregistered optimization cell produce a materially non-zero
> CORRECT − ABSENT_UNPAIRED contrast?

Phase C is an **optimization-adequacy** study. It is explicitly **not** a binding
study, not a capacity study, and not a representation study.

### What Phase C can establish

- That the Phase B optimization point was, or was not, a limiting factor **within the
  frozen envelope**.
- Development-stage evidence supporting or excluding rank-4 `OPTIMIZATION_LIMIT`
  as a *candidate* explanation.

### What Phase C cannot establish — stated explicitly

- It **cannot** establish `OPTIMIZATION_LIMIT` as a final classification.
  The amendment defines that classification as requiring another preregistered
  LR/step cell to **pass G4** (Section E, item 4). G4 requires **locked-test**
  evaluation at 4,000 episodes per confirmation-trained model seed. Phase C run on
  development seeds cannot reach G4. See `D-04`.
- It **cannot** establish binding, capacity limits, or architectural conclusions.
- It **cannot** authorize Phase D, E, or F, Candidate C, or production.
- It **cannot** rule out a task-construction defect. Precedence forbids reaching
  rank 4 while rank 2 is unresolved.

---

## 2. HYPOTHESIS

**H-C0 (null, favoured by current evidence).**
Within the frozen envelope (≤64 optimizer updates, ≤128 episodes per update, constant
LR, no warm-up), the B2 CORRECT − ABSENT_UNPAIRED contrast remains below 0.10 in every
preregistered LR × step cell, for every development seed, for both frozen
configurations.

**H-C1 (alternative).**
At least one preregistered LR × step cell yields B2 CORRECT − ABSENT_UNPAIRED ≥ 0.10
in every development seed, with a hierarchical-bootstrap 95% lower bound > 0.

**Prior from Phase B.** Observed B2 margins spanned −0.001 to +0.022 (max +0.0220) at
lr = 0.001, 64 steps. H-C1 requires roughly a 4.5× increase in the contrast from grid
search alone. This is stated so the review can judge whether Phase C is worth its
compute before it is authorized, and so that a null result is not later reported as
a surprise.

**Falsifiability note.** H-C0 is the outcome most consistent with existing evidence.
Phase C is therefore primarily a *rule-out* study. It should be authorized only if a
rule-out has decision value for the project. If the project would proceed identically
under either outcome, Phase C should not be run.

---

## 3. TASK CONSTRUCTION

Inherited **unchanged** from the approved amendment. No Phase C redefinition.

| Property | Frozen value | Amendment source |
|---|---|---|
| Symbol table | 128 integer symbols, table as frozen | §B.2 |
| Key atoms | IDs 32–63 | §B.2 |
| Value atoms | IDs 64–95 | §B.2 |
| Diagnostic atoms | 96–127, prohibited in primary keys/values/answers | §B.2 |
| Reserved | 15–31, prohibited in primary episodes | §B.2 |
| Context length | 256 tokens; truncation prohibited | §B.4 |
| Level under test | **B2 only** (2 pairs) | §I checklist L1124 |
| Training support | correct support only | inherited |
| Prompt termination | immediately after `<ANS>` | §B.3 |
| Scoring | whole target-value span, exact match | §B.3 |
| Excluded from scoring/loss | prompt, query-key, markers, `<ANS>`, `<EOS>`, `<FILL>`, `<PAD>` | §B.3 |
| Balance | query-record index balanced, stratum counts differ by ≤1 | §B.3 |

**B1 is excluded from Phase C** pending `D-01` (Section 0).
**B3–B5 are excluded from Phase C** — they are robustness levels governed by G5 and are
out of scope for an optimization study.

⚠️ **DECISION REQUIRED `D-06` — effective value cardinality.**
Every archived Phase A and Phase B run reports `absent_placeholder` accuracy of exactly
`0.25`, across all nine configurations and all three seeds. Exact quarter-accuracy is
the signature of a **four-way** effective output space, consistent with the superseded
calibration study's "exactly four single-token values, chance exactly 25%" — but the
approved amendment specifies 32 value atoms (64–95) and whole-span scoring over the
full vocabulary, and does **not** define a four-class restriction anywhere.

The effective chance level of the primary endpoint is therefore **not determined by the
authoritative artifact**. Because every Phase C threshold is an absolute accuracy
difference, the chance level must be pinned before any threshold is meaningful.
I have **not** guessed a value. **DECISION REQUIRED.**

---

## 4. SERIALIZATION AND QUERY CONFIGURATION

Phase C **inherits the Phase A frozen selection and must not re-open it.** The amendment
(§C, Configuration selection) states: "After confirmation begins, no configuration, seed,
threshold, metric, or analysis rule may change."

| Item | Value | Source |
|---|---|---|
| Frozen configurations | `S2_Q2`, `S3_Q2` | `experiments/v10_10/phase_a_selection.json` (self-hash verified) |
| Primary serializations | S1–S3 only; F-A…F-D prohibited as primary | §B.2 |
| Primary query formats | Q1–Q3 only; Q-A…Q-C prohibited as primary | §B.3 |
| Query slot | fixed width, right-aligned, `<ANS>` at matched index | §B.3 |
| `<FILL>` | leading positions of query slot only; excluded from attention/loss/scoring; positions retained | §B.2 |

⚠️ **DECISION REQUIRED `D-08` — Phase C configuration breadth.**
Run the LR×step grid on both frozen configurations (doubling cost, preserving the
Phase A freeze), or on `S2_Q2` alone (rank-1 by the frozen selection rule)?
Both are defensible; the amendment does not decide it. **DECISION REQUIRED.**

---

## 5. MODEL SCALE

| Field | L1 (proposed Phase C scale) | Verified |
|---|---|---|
| Hidden size | 64 | ✅ |
| Layers | 4 | ✅ |
| Heads | 4 | ✅ |
| Head dimension | 16 | ✅ |
| Intermediate | 256 | ✅ |
| Vocabulary | 128 | ✅ |
| Context | 256 | ✅ |
| **Trainable parameters** | **224,128** | ✅ instantiated and counted |
| Fingerprint | `V10.10-A01-L1-h64-L4-a4-d16-ff256-v128-c256-preLN-GELU-tied-noLMbias` | §B.4 |

Architecture frozen by §B.4: decoder-only, pre-LN, learned token + learned absolute
position embeddings, full causal MHA with separate **biased** Q/K/V/O, 2 biased FFN
linears, exact GELU, dropout 0, final LayerNorm, **tied** embedding/output weights,
**no output bias**, FP32, no pretrained weights.

Parameter formula (§B.4): \( P = Vh + Ch + L(4h^2 + 2hi + 7h + i) + 2h \)

Independently confirmed three ways during preparation — spec text (224,128),
closed-form formula (224,128), and live instantiation of `build_amended_model("L1")`
(224,128). L0 likewise confirmed at 37,632.

**Excluded:** L0 (Phase C is not a scaling study — that is G6/Phase D), L2, L3,
Candidate C, and all production configurations. `build_amended_model` fail-closes on
any other scale.

**Parameter count is an invariant, not a target.** Any Phase C variant that changes
the count — including any auxiliary head — is out of specification. See `D-05`.

---

## 6. OPTIMIZER

Inherited **verbatim and unchanged** from the approved amendment §B.4 (Optimizer).
The superseded calibration study's Phase C optimizer language is **rejected in full**
(see reconciliation `C-02`, `C-03`, `C-05`).

| Field | Frozen value |
|---|---|
| Family | AdamW |
| β₁ | 0.9 |
| β₂ | 0.999 |
| ε | 1e-8 |
| Weight decay | 0.01 |
| Decay exclusions | LayerNorm parameters and all bias terms excluded; matrices and embeddings included |
| Gradient clipping | global gradient-norm clipping at **1.0** |
| **Warm-up** | **none** |
| Schedule | **constant LR within each learning-rate cell** |
| Batch size | **128 episodes** |
| Gradient accumulation | **prohibited** |
| Step definition | one step = one completed AdamW update |
| Precision | FP32 |
| Initialization | N(0, 0.02) weights; biases 0; LN scale 1; LN bias 0; `stream=model-initialization` namespace |

---

## 7. LEARNING-RATE REGIME

⚠️ **DECISION REQUIRED `D-02` — the LR grid is referenced but never defined in the
authoritative amendment.**

The amendment refers to a "learning-rate grid" (§B.5, G6 fairness inputs, line 736) and
to "the complete fair optimization grid" (lines 761, 956), and classification rank 4
depends on "another preregistered LR/step cell" — but **no LR values appear anywhere in
the amendment text.**

Concrete values exist **only** in the non-authoritative implementation artifact
`experiments/v10_10/study_plan.json`:

```json
"lr_grid": [0.00025, 0.0005, 0.001, 0.002, 0.004]
```

Per handoff rule 6 ("do not silently inherit conflicting values") and rule 7, I have
**not** adopted these as authoritative. They are recorded here as the *implementation's
current values*, for the reviewer to accept, amend, or reject.

Additional context for the decision:

- Phase B executed at **lr = 0.001**, which is the centre of the implementation grid
  and equals the recovered historical V10.9 F8 peak LR.
- The superseded calibration study proposed 0.5× / 1.0× / 2.0× of 0.001
  → {0.0005, 0.001, 0.002}, a strict subset of the implementation grid.
- Adopting the implementation grid would make Phase B's point the grid centre, which is
  reasonable, but this must be an explicit decision, not an inheritance.

**DECISION REQUIRED.** No LR grid is proposed as authoritative by this draft.

**Constraint that holds regardless of the chosen values:** the LR must be **constant
within each cell**, with **no warm-up** and **no decay schedule**. Any cosine, linear,
step, or warm-up schedule is prohibited by §B.4.

---

## 8. STEP BUDGET

⚠️ **DECISION REQUIRED `D-03` — the step grid is likewise referenced but undefined in
the authoritative amendment.**

The hard ceiling **is** defined, in §D (Stopping-rule freeze):

> **Compute ceiling** — "Any run requests more than **64 optimizer updates**, more than
> **128 episodes per update**, or unapproved gradient accumulation → **Reject before
> execution.**"

This ceiling is enforced in code (`scripts/v10_10_run_study.py:89-90`,
`MAX_OPTIMIZER_STEPS = 64`, `MAX_BATCH_SIZE = 128`, both raising on violation).

The step grid values exist only in `study_plan.json`:

```json
"step_grid": [0, 1, 2, 4, 8, 16, 32, 64]
```

Note `step = 0` provides the untrained reference needed for the G2 log-probability-gain
criterion ("must exceed **step-0** value by at least 0.50 natural-log units").

**DECISION REQUIRED** on whether to adopt this grid.

### `D-10` — the envelope question the review must actually decide

The superseded calibration study's Phase C assumed **10,000** optimizer updates,
evaluated at 400/1,000/2,000/5,000/8,000/10,000. That is ~156× the frozen ceiling.

This is the single most consequential open question in Phase C:

- **Option A — respect the 64-step ceiling.** Phase C stays inside the approved
  envelope and requires no amendment. But it can only ever test optimization adequacy
  *within a very small budget*, and a null result will not distinguish "optimization is
  not the limit" from "64 steps is too few to tell."
- **Option B — raise the ceiling via a new versioned amendment.** The amendment's own
  stopping rule requires this: "Unapproved specification change … Stop and request a
  versioned amendment." This would permit a scientifically stronger study but is a
  formal specification change requiring explicit approval.

⚠️ **DECISION REQUIRED.** This draft does **not** propose raising the ceiling, and
under Option A the honest statement of Phase C's power must be recorded in the report.

---

## 9. BATCH SIZE

**128 episodes per optimizer update.** Frozen by §B.4 and re-asserted as a hard ceiling
by §D. No gradient accumulation. Not open for Phase C modification.

The superseded calibration study's implicit batch 256 (inherited from the V10.9 F8
replay via "same … batch") is **rejected** — see reconciliation `C-05`.

---

## 10. SEEDS

| Role | Seeds | Phase C access |
|---|---|---|
| Development | `104729`, `130363`, `155921` | **PERMITTED** |
| Confirmation | `196613`, `262147`, `393241` | **PROHIBITED in Phase C** |
| Locked test | — | **PROHIBITED in Phase C** |
| Historical | `42` | **EXCLUDED** from the campaign |

**Phase C is proposed as a development-only study.** The amendment (§B.1, Access rules)
permits development seeds for configuration selection; confirmation access requires a
frozen, hashed selection record, and locked-test access requires passed confirmation.
Phase C satisfies neither precondition.

Namespace derivation is inherited verbatim (§B.1):

```text
NIRMAL-1|V10.10-SPEC-AMENDMENT-01|purpose={purpose}|root={root_seed}|split={split}|level={level}|serialization={serialization}|query={query}|control={control}|index={index}|stream={stream}
```

SHA-256 over exact UTF-8 → first 8 bytes big-endian uint64 → mod `9223372036854775783`
→ zero becomes one. Full derivation string and effective seed recorded in the manifest.

⚠️ **DECISION REQUIRED `D-11` — namespace `purpose` for Phase C.**
Allowed values are `development`, `confirmation`, `diagnostic`, `locked-test`,
`implementation-fixture`. An optimization sweep is arguably `development` (it informs
selection) or `diagnostic` (it is a diagnostic sweep). The two produce **different
effective seeds and therefore different episodes**, and the amendment states diagnostic
episodes "may not determine primary configuration selection." The choice materially
changes what Phase C results may be used for. **DECISION REQUIRED.**

---

## 11. EVALUATION PROTOCOL

| Item | Proposed | Basis |
|---|---|---|
| Level | B2 | Section 3 |
| Scale | L1 | Section 5 |
| Configurations | per `D-08` | Section 4 |
| Cells | (LR values × step values), per `D-02`/`D-03` | — |
| Seeds | 3 development | Section 10 |
| Conditions per cell | all five controls, reported separately | §C Control freeze |
| Episodes | ≥1,000 per development seed per cell (amendment minimum) — exact count is `D-07` | §B.5, §C |
| Scoring | whole target-value span exact match | §B.3 |
| Pairing unit | complete base episode (mapping, query key, target, support order, serialization, query format, position) | §C |
| Teacher forcing | target supplied only as label/teacher-forced continuation | §B.3 |
| NaN/Inf | counted; any occurrence stops the affected run and marks it **failed, not missing** | §D |

**Per-seed reporting is mandatory.** "No averaging may conceal a failing seed" (§B.5).
Every executed cell, every failed cell, and every aborted cell must appear in the report
with sample counts, point estimates, intervals, raw and Holm-adjusted p-values,
target-span log probability, lure metrics, stop reason, and excluded-episode counts
(§C Reporting). Selective omission is prohibited.

⚠️ **DECISION REQUIRED `D-07`.** The amendment sets a *minimum* of 1,000 development
episodes per seed per cell but does not fix an exact Phase C count. With a
5 × 8 grid × 3 seeds × 2 configurations × 5 controls, the count drives total cost
directly. **DECISION REQUIRED.**

---

## 12. PRIMARY ENDPOINT

Inherited unchanged from §C:

\[
\Delta_{\mathrm{primary}}
= \operatorname{EM}_{\mathrm{CORRECT}} - \operatorname{EM}_{\mathrm{ABSENT\_UNPAIRED}}
\]

evaluated at **B2**, paired at the level of the complete base episode.

**Phase C secondary endpoint (reported, never decisive):** target-span mean log
probability under CORRECT, and its gain over the step-0 reference.

**Phase C reports one additional derived quantity:**

\[
\Delta^{\max}_{\mathrm{grid}} = \max_{\text{cells}} \ \min_{\text{seeds}} \ \Delta_{\mathrm{primary}}
\]

i.e. the best cell judged by its **worst** seed. The min-over-seeds inner term is
deliberate: it prevents a cell from being promoted on the strength of one lucky seed,
consistent with the amendment's per-seed requirements. This quantity is **descriptive**
and does not by itself satisfy any gate.

---

## 13. CONTROLS

Frozen by §C (Control freeze). All five reported separately in every cell:

| Control | Role | Notes |
|---|---|---|
| `correct` | primary condition | original mapping |
| `absent_unpaired` | **PRIMARY ABSENT** | key/value multiset preserved, pair boundaries destroyed |
| `absent_placeholder` | **SECONDARY ABSENT** | reported; may not determine gates |
| `random_deranged` | specificity | derangement guaranteed to change the query association |
| `targeted_wrong` | specificity | query value swapped with one distractor; lure metrics reported |

**Explicitly prohibited:** maximum, minimum, best-of, or **stronger-of** selection
across controls (§C). The superseded calibration study's "correct-minus-stronger-absent"
Gate 3 is **rejected** — see reconciliation `C-11`.

The target remains the original target in every condition.

---

## 14. STATISTICAL TESTS

Inherited unchanged from §C.

- **Within-seed binary accuracy:** two-sided 95% **Wilson** interval.
- **Cross-seed paired contrasts:** two-sided 95% **percentile** interval from
  **exactly 10,000** hierarchical-bootstrap replicates. Report 2.5th and 97.5th
  empirical percentiles. **No normal-theory substitution.**
- **Hierarchical bootstrap procedure** (§C), per replicate:
  1. sample three seed slots with replacement;
  2. for each selected seed occurrence, resample that seed's base-episode indices with
     replacement at the original per-seed count (independently per occurrence if a seed
     is drawn twice);
  3. retrieve both paired outcomes from the same base episode;
  4. mean paired difference within each selected seed occurrence;
  5. unweighted mean of the three seed-level means.
- **p-value:**
  \( p = 2\min\!\left(\frac{1+\#(\Delta_b \le 0)}{10001}, \frac{1+\#(\Delta_b \ge 0)}{10001}\right) \), capped at 1.

### ⚠️ DECISION REQUIRED `D-12` — no Holm family exists for Phase C

The amendment freezes **exactly six** Holm families (§C): specificity, core,
serialization, query, ladder, scaling. **None covers LR/step comparisons.**

A grid of 5 LRs × 8 step counts is 40 cells per configuration. Reporting the best cell
without multiplicity control would be exactly the "apparently strong result that does
not survive scrutiny" failure mode this project has repeatedly encountered.

Options for the reviewer:

- **(a)** Add a seventh preregistered family, "optimization: each non-reference LR/step
  cell versus the Phase B reference cell," via a versioned amendment.
- **(b)** Declare Phase C wholly exploratory and non-inferential — descriptive statistics
  and intervals only, no p-values, no classification contribution. Note the amendment
  already says exploratory analyses "cannot change primary decisions."
- **(c)** Restrict Phase C to a small preregistered subset of cells sized so the
  existing multiplicity philosophy still applies.

I have **not** selected one. **DECISION REQUIRED.**

---

## 15. STOPPING RULES

All §D triggers apply **unchanged and fail-closed**. Reproduced for operational use:

| Trigger | Condition | Action |
|---|---|---|
| Artifact integrity | any G0 invariant fails or cannot be verified | abort; classify `INVALID`; do not inspect outcomes |
| Leakage | answer token in prompt, forbidden split collision, or confirmation/locked data influencing selection | abort affected + downstream; invalidate exposed test version |
| Parser failure | valid record fails round-trip, or malformed record accepted | stop; repair only after new review |
| Scoring failure | non-answer token scored, answer length mishandled, whole-span scoring not reproducible | abort; invalidate all results from that scorer |
| **Protected path** | any change under `src/nirmal/` or `data/shards/` | **abort immediately**; V10.10 remains invalid |
| Corpus count | ≠ exactly 233,997 | abort; do not recount as new baseline |
| **Candidate C** | any instantiation, evaluation, loading, update, or training | **abort; record critical safety violation** |
| Production config | any detected difference | abort immediately |
| NaN/Inf | in loss, logits, parameters, gradients, optimizer state, metric, or CI | stop run; mark **failed, not missing**; no silent restart with changed settings |
| **Compute ceiling** | > 64 updates, > 128 episodes/update, or unapproved accumulation | **reject before execution** |
| Missing seed/cell | required result absent | gate fails; do not average over the remainder |
| Unapproved spec change | seed, threshold, format, query, model, metric, or analysis differs from the amendment | **stop and request a versioned amendment** |

### Phase C additional stopping rules (proposed)

- **PC-S1 — Phase boundary.** Phase C terminates at the Phase C boundary. It must not
  initiate Phase D, E, or F under any outcome, including a positive one.
- **PC-S2 — No confirmation escalation.** A positive Phase C result does **not**
  authorize confirmation-seed access. That requires a separately frozen and hashed
  selection record plus explicit user authorization.
- **PC-S3 — No re-freezing.** Phase C must not alter the Phase A frozen configurations
  (`S2_Q2`, `S3_Q2`) regardless of outcome.
- **PC-S4 — Degenerate-contrast guard.** If any cell's primary contrast is degenerate by
  construction (as B1 is, per Section 0), that cell is `INVALID` and must not be
  reported as a model result.
- **PC-S5 — Grid completeness.** A partially executed grid may not be reported as a
  completed optimization search, and may not support any `OPTIMIZATION_LIMIT` reasoning.
  The amendment requires "the **complete** fair optimization grid."

---

## 16. CLASSIFICATION PRECEDENCE

The amendment's §E ten-item order is inherited **verbatim and unchanged**. Evaluate in
order; stop at the first satisfied condition; earlier always overrides later.

1. `INVALID`
2. `TASK_CONSTRUCTION`
3. `SERIALIZATION_LIMIT`
4. `OPTIMIZATION_LIMIT`
5. `CAPACITY_LIMIT`
6. `REPRESENTATION_LIMIT`
7. `CONTEXT_ACCESS_LIMIT`
8. `ASSOCIATIVE_BINDING_FAILURE`
9. `PARTIAL_ASSOCIATIVE_BINDING`
10. `ASSOCIATIVE_BINDING_ESTABLISHED`

> **Note:** the superseded calibration study §15 lists items 8 and 9 in the **opposite**
> order and uses different identifiers. The amendment order above is authoritative.
> See reconciliation `C-10`.

### What Phase C may and may not conclude

- Phase C **may** contribute development-stage evidence toward rank 4.
- Phase C **may not** assign `OPTIMIZATION_LIMIT`. That requires a preregistered
  LR/step cell to **pass G4** (locked test, 4,000 episodes per confirmation-trained
  model seed, ≥0.10 gain in every seed, Holm-adjusted lower bound > 0). Phase C reaches
  none of these. See `D-04`.
- Phase C **may not** reach rank 4 at all while rank 2 (`TASK_CONSTRUCTION`) is
  unresolved — see Section 0.
- Phase C **may** trigger rank 1 (`INVALID`) if G0/G1 fail.
- Phase C **must** record its classification contribution as *provisional and
  development-stage*.

---

## 17. ARTIFACT REQUIREMENTS

Every Phase C run must emit, at minimum:

1. **Execution-provenance block** conforming to
   `experiments/v10_10/PROPOSAL_execution_provenance_schema.json`
   (spec SHA-256, model fingerprint, parameter count, optimizer, LR, warm-up, batch,
   steps, clipping, seed, split, purpose, serialization, query format — plus the
   remaining required fields in that schema). This closes the Phase B provenance gap in
   which run artifacts recorded no execution metadata at all.
2. **Refreshed G0 evidence** per
   `experiments/v10_10/PROPOSAL_g0_integrity_manifest.json`, captured **before** and
   **after** execution, including **content hashes** of `src/nirmal/` and
   `data/shards/` (not merely git status — see the G0 proposal for why that check is
   currently vacuous for `data/shards/`).
3. **Per-cell result records** — one artifact per (configuration, LR, steps, seed),
   containing all five controls, counts, Wilson intervals, and NaN/Inf counts.
4. **Grid summary** with canonical self-hash under the existing convention
   (`json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True)`, SHA-256),
   matching the verified Phase A/B pattern.
5. **Benchmark manifest** for all generated episodes, with per-file and top-level
   SHA-256 and full namespace-derivation strings.
6. **Complete ledger** — every executed, failed, and aborted cell. Deletion of failed or
   superseded artifacts is prohibited (§H).
7. **Spec-hash gate** — Phase C code must verify the parent amendment digest
   `f320ccd3…f0a0b` at entry and fail closed, mirroring
   `scripts/v10_10_run_study.py:578-580`.

**Existing Phase A and Phase B artifacts must not be modified, rewritten, or deleted.**
Phase C writes only new files.

---

## 18. SAFETY AND PROTECTED-PATH RULES

**Absolute prohibitions for Phase C:**

- ❌ No modification of `src/nirmal/` (23 tracked files; rollup recorded in the G0 proposal).
- ❌ No modification of `data/shards/` (18 files; **gitignored — content hashing mandatory**).
- ❌ No Candidate C instantiation, loading, evaluation, update, or training. Zero remains zero.
- ❌ No production training. Production remains **STRICT NO-GO**, external approvals **0/6**.
- ❌ No production-configuration change.
- ❌ No confirmation-seed access.
- ❌ No locked-test generation, decryption, or access.
- ❌ No architecture intervention; no Phase F.
- ❌ No V10.11 initiation.
- ❌ No corpus modification. Authoritative corpus remains exactly **233,997** tokens.
- ❌ No modification of V10.9 history.
- ❌ No use of L0, L2, L3, or any production configuration as the Phase C model.
- ❌ No external AI, API, or network dependency at any point in training, inference, or
  evaluation. Nirmal-1 remains independent and offline.

**Required affirmative checks, before and after every Phase C run:**

- `src/nirmal/` content rollup unchanged.
- `data/shards/` content rollup unchanged.
- Corpus token count exactly 233,997.
- Candidate C access/update log: exactly 0.
- External approvals exactly 0/6; production status exactly STRICT NO-GO.
- Locked-test access log: zero unauthorized accesses.

Any failure ⇒ abort immediately, classify `INVALID`, do not inspect scientific outcomes.

---

## 19. CONSOLIDATED "DECISION REQUIRED" REGISTER

| ID | Decision | Blocking? |
|---|---|---|
| **D-01** | **B1 primary contrast is degenerate by construction (1 pair ⇒ Δ ≡ 0). Resolve as `TASK_CONSTRUCTION` before Phase C?** | **YES — blocking** |
| **D-02** | Authoritative LR grid values (undefined in amendment; implementation has 5 values) | YES |
| **D-03** | Authoritative step grid values (undefined in amendment; implementation has 8 values) | YES |
| **D-04** | `OPTIMIZATION_LIMIT` requires passing G4 (locked test). Is Phase C therefore non-classifying by design, or is a different route intended? | YES |
| **D-05** | Are auxiliary objectives (O-B, O-C) admissible at all? O-C requires a pair-index head, which changes the frozen 224,128 parameter count | YES |
| **D-06** | Effective value cardinality / chance level (observed 0.25 vs 32 value atoms in spec) | YES |
| **D-07** | Exact episodes per seed per cell (amendment sets only a ≥1,000 minimum) | No |
| **D-08** | Run grid on both frozen configurations or `S2_Q2` only | No |
| **D-09** | G2 as written uses **confirmation** seeds; Phase A applied a development analogue. Which governs a development-stage Phase C? | No |
| **D-10** | Respect the 64-step ceiling (Option A) or raise it by versioned amendment (Option B) | YES |
| **D-11** | Namespace `purpose` for Phase C: `development` or `diagnostic` (changes episodes and permitted use) | YES |
| **D-12** | Multiplicity control — no Holm family covers LR/step; add family, go exploratory, or restrict grid | YES |

**Nine of twelve decisions are blocking. This draft is not executable in its current
state, and that is intentional.**

---

## 20. APPROVAL BOUNDARY

This draft, if approved **as-is**, would authorize **nothing**. It is a proposal
awaiting resolution of the register in Section 19.

A future authorization of Phase C would require, in order:

1. Resolution of `D-01` (task construction) — recommended **first**, independently.
2. Resolution of all remaining blocking decisions.
3. A revised, frozen, SHA-256-pinned Phase C specification.
4. Implementation and non-scientific revalidation of that specification.
5. A refreshed G0 pass on the post-amendment repository state.
6. **Explicit user authorization naming Phase C and only Phase C.**

Phase C execution must stop at the Phase C boundary. Phases D, E, and F remain
unauthorized. Candidate C remains untouched. Production remains STRICT NO-GO.

---

*End of draft proposal. Non-authoritative. No scientific execution is authorized by this document.*
