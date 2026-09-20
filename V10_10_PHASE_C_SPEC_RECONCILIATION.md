# NIRMAL-1 V10.10 — PHASE C RECONCILIATION

> ## ⛔ STATUS: ANALYSIS DOCUMENT — NOT AUTHORITATIVE — AUTHORIZES NOTHING
>
> This document reconciles the **superseded** Phase C proposal against the
> **approved** V10.10 amendment. It records conflicts and *proposes* resolutions.
> It does not itself resolve anything, change any specification, or authorize
> any execution.

**Document ID:** `V10.10-PHASE-C-RECONCILIATION-00`
**Prepared:** 2026-09-18
**Companion:** `docs/V10_10_PHASE_C_SPEC_DRAFT.md`

---

## 1. THE TWO SOURCES

### 1.1 Authoritative constraint source

| Field | Value |
|---|---|
| Path | `docs/V10_10_SPEC_AMENDMENT_01_APPROVED.md` |
| Size | 44,475 bytes |
| SHA-256 | `f320ccd316940314b119a5378f8591c850fe1d603a822c8ef24fbf087c3f0a0b` |
| Verification | ✅ recomputed and matched during this preparation |
| Enforcement | `scripts/v10_10_run_study.py:578-580` hard-gates on this exact digest |

**This document governs.** Every conflict below is resolved in its favour unless a
future versioned amendment says otherwise.

### 1.2 Superseded proposal source

| Field | Value |
|---|---|
| Path | `docs/V10_10_ASSOCIATIVE_BINDING_CALIBRATION_STUDY.md` |
| Section | § 9 "Phase C — Optimization and objectives" (plus §§ 4, 8, 10, 13–15, 17 as dependencies) |
| Size | 18,302 bytes |
| SHA-256 (current) | `84a1c27f1862076bf85660738b5091bfaa7d7393ed23ffe9681c3f165db5a18b` |
| SHA-256 (pinned 13-09 in `implementation_validation.json`) | `eec75ccb7ec0a8d7121da11c44e27ecbce7cf17cc5a41566aa3e828bb06414a0` |
| Integrity status | ⚠️ **DRIFTED** — current content does not match the last recorded pin |

**Status:** pre-amendment, non-authoritative, and hash-drifted. It is retained as a
historical artifact (the amendment §H forbids deleting superseded artifacts) but
**must not** be treated as a specification.

### 1.3 A third, ambiguous source

`experiments/v10_10/study_plan.json` (self-hash `0e3f9629…`, verified) contains
concrete `lr_grid` and `step_grid` values that appear in **neither** document above as
authoritative text. It is an *implementation* artifact. Its values are surfaced in this
reconciliation as candidates requiring decision, not as inherited constraints.

---

## 2. VERBATIM TEXT OF THE OLD PHASE C PROPOSAL

Reproduced in full from § 9 so the review can assess it without re-opening the drifted file:

> ## 9. Phase C — Optimization and objectives
>
> A continuous 10,000-step run is evaluated at 400, 1,000, 2,000, 5,000, 8,000, and
> 10,000 updates. Poor accuracy does not trigger early stopping. Log fresh train
> accuracy, all validation conditions, counterfactual following, gradient norm,
> clipping, update ratio, entropy, output distribution, and position-conditioned
> accuracy.
>
> Learning-rate discovery tests 0.5×, 1.0×, and 2.0× the exact V10.9 peak LR, using the
> same schedule, warmup, batch, stream, and initialization where deterministic. Only
> the best schedule is promoted.
>
> Objectives are sequential:
>
> - **O-A:** query-answer loss only.
> - **O-B:** O-A plus 0.25-weight auxiliary query for a different support key.
> - **O-C:** O-A plus 0.10-weight support-pair-index matching. The index target depends
>   only on query-key identity and support position, never value or answer.
>
> O-C is conditional and cannot be activated automatically.

---

## 3. CONFLICT REGISTER

Severity key — **CRITICAL**: would violate a frozen invariant or hard ceiling.
**MAJOR**: would violate a frozen protocol or statistical rule.
**MODERATE**: definitional divergence that would corrupt interpretation.

### C-01 — Step budget — **CRITICAL**

| | |
|---|---|
| **Old proposal** | "A continuous **10,000-step** run" |
| **Amendment** | §D compute ceiling: "Any run requests **more than 64 optimizer updates** … **Reject before execution.**" |
| **Conflict** | 10,000 ≫ 64. Approximately **156×** the ceiling. |
| **Enforcement** | `scripts/v10_10_run_study.py:89` `MAX_OPTIMIZER_STEPS = 64`, raises `ValueError` |
| **Proposed resolution** | **Reject** the 10,000-step design. Adopt a step grid at or below 64 (`D-03`), *or* formally raise the ceiling by versioned amendment (`D-10`). |
| **Status** | ⚠️ Unresolved — `D-03`, `D-10` |

### C-02 — Warm-up — **CRITICAL**

| | |
|---|---|
| **Old proposal** | "using the same schedule, **warmup**, batch, stream, and initialization" |
| **Amendment** | §B.4 Optimizer: "**no warm-up**" |
| **Conflict** | Direct contradiction of a frozen optimizer field. |
| **Proposed resolution** | **Reject** warm-up entirely. Amendment governs. |
| **Status** | ✅ Resolved in draft §6 |

### C-03 — Learning-rate schedule — **CRITICAL**

| | |
|---|---|
| **Old proposal** | "the same **schedule**"; "Only the best **schedule** is promoted" (V10.9 used cosine decay — see `v10_10_run_study.py:219` `legacy_v10_9_cosine_lr`) |
| **Amendment** | §B.4: "**constant learning rate** within each learning-rate cell" |
| **Conflict** | A decaying schedule is prohibited. "Promoting a schedule" is not a meaningful operation under a constant-LR freeze. |
| **Proposed resolution** | **Reject** all schedules. Phase C varies LR **between** cells and holds it constant **within** each cell. Reframe "schedule discovery" as "LR-cell discovery". |
| **Status** | ✅ Resolved in draft §§6–7 |

### C-04 — Learning-rate anchor and grid — **MAJOR**

| | |
|---|---|
| **Old proposal** | "0.5×, 1.0×, and 2.0× the exact V10.9 peak LR" → {0.0005, 0.001, 0.002} |
| **Amendment** | References a "learning-rate grid" (line 736) and "the complete fair optimization grid" (lines 761, 956) but **defines no values anywhere** |
| **Implementation** | `study_plan.json`: `[0.00025, 0.0005, 0.001, 0.002, 0.004]` |
| **Conflict** | The authoritative document has a **gap**, not a contradiction. The old proposal's subset and the implementation's superset both exist unauthorised. |
| **Proposed resolution** | Do **not** inherit either. Require an explicit decision. Note the implementation grid is a strict superset of the old proposal's and centres on Phase B's operating point. |
| **Status** | ⚠️ Unresolved — `D-02` |

### C-05 — Batch size — **CRITICAL**

| | |
|---|---|
| **Old proposal** | "the same … **batch** …" — inheriting V10.9 F8's **batch 256** (amendment §A records V10.9 F8 as batch 256) |
| **Amendment** | §B.4 "batch size **128** episodes"; §D ceiling "more than **128 episodes per update** → Reject before execution" |
| **Conflict** | 256 > 128. Exceeds a hard ceiling. |
| **Enforcement** | `v10_10_run_study.py:90` `MAX_BATCH_SIZE = 128`, raises |
| **Proposed resolution** | **Reject** batch 256. Batch is fixed at 128 and is not a Phase C variable. |
| **Status** | ✅ Resolved in draft §9 |

### C-06 — Evaluation checkpoints — **CRITICAL**

| | |
|---|---|
| **Old proposal** | Evaluate at 400 / 1,000 / 2,000 / 5,000 / 8,000 / 10,000 updates |
| **Amendment** | Maximum 64 updates |
| **Conflict** | **Every one** of the six checkpoints is unreachable. The lowest (400) is 6.25× the ceiling. |
| **Proposed resolution** | **Reject** in full. Replace with checkpoints inside the envelope (`study_plan.json` offers `[0, 1, 2, 4, 8, 16, 32, 64]`, where `step = 0` supplies the untrained reference that G2's "exceed step-0 by ≥0.50 nats" criterion requires). |
| **Status** | ⚠️ Unresolved — `D-03` |

### C-07 — Objective O-B (auxiliary query loss) — **MAJOR**

| | |
|---|---|
| **Old proposal** | "O-A plus **0.25-weight auxiliary query** for a different support key" |
| **Amendment** | §B.3: "**Only the complete target-value span is scored.** Prompt tokens, query-key tokens, structural markers, `<ANS>`, `<EOS>`, `<FILL>`, and `<PAD>` are excluded from primary scoring **and loss**." |
| **Conflict** | O-B adds a loss term on a second query's answer span. Whether this is permitted turns on whether "primary scoring and loss" forbids *any* additional supervised term or only forbids scoring non-answer tokens. The amendment does not say. |
| **Proposed resolution** | Treat O-B as **out of specification pending explicit decision**. If admitted, it must be a separate preregistered arm with its own multiplicity handling, never pooled with O-A. |
| **Status** | ⚠️ Unresolved — `D-05` |

### C-08 — Objective O-C (pair-index matching head) — **CRITICAL**

| | |
|---|---|
| **Old proposal** | "O-A plus **0.10-weight support-pair-index matching**" |
| **Amendment** | §B.4 freezes L1 at **exactly 224,128** trainable parameters. §I checklist: "L1 count is exactly 224,128." `build_amended_model` raises on mismatch. §B.4 Exclusions: "The amendment prospectively freezes 37,632 and 224,128 as the only valid L0/L1 counts." |
| **Conflict** | A support-pair-index matching objective requires an **index-prediction head**, which adds parameters. Any such head changes the count away from 224,128 and **fails the frozen model identity**. The tied-embedding output path (`F.linear(x, tok_emb.weight, bias=None)`) provides no spare head to reuse. |
| **Proposed resolution** | **Reject O-C** under the current amendment. It is not implementable without breaking the frozen parameter identity. Admitting it would require a new model identity, a new fingerprint, a new parameter count, and a versioned amendment. |
| **Status** | ⚠️ Unresolved — `D-05` (recommendation: reject) |

### C-09 — Promotion / selection rule — **MAJOR**

| | |
|---|---|
| **Old proposal** | "Only the **best schedule** is promoted" |
| **Amendment** | §C Configuration selection: development-only; rank by passing G0–G2; **maximize B2 development CORRECT − primary-ABSENT**; tie-break by B2 CORRECT EM; then lexicographic; **freeze at most two** configurations; nothing changes after confirmation begins |
| **Conflict** | "Best schedule" is undefined under the frozen rule, and the frozen rule selects *configurations* (S×Q), not schedules. Phase A already consumed the selection budget by freezing `S2_Q2` and `S3_Q2`. |
| **Proposed resolution** | **Reject** the promotion language. Phase C must not re-open the Phase A freeze (draft rule `PC-S3`). Any LR/step "promotion" is a distinct decision requiring its own preregistered rule. |
| **Status** | ✅ Resolved in draft §4 / `PC-S3` |

### C-10 — Classification list — **MODERATE**

| | |
|---|---|
| **Old proposal** (§15) | 1 `INVALID_EXPERIMENT`, 2 `TASK_CONSTRUCTION_FAILURE`, 3 `SERIALIZATION_LIMIT`, 4 `OPTIMIZATION_LIMIT`, 5 `CAPACITY_LIMIT`, 6 `REPRESENTATION_LIMIT`, 7 `CONTEXT_ACCESS_LIMIT`, **8 `PARTIAL_ASSOCIATIVE_BINDING`, 9 `ASSOCIATIVE_BINDING_FAILURE`**, 10 `ASSOCIATIVE_BINDING_ESTABLISHED` |
| **Amendment** (§E) | … **8 `ASSOCIATIVE_BINDING_FAILURE`, 9 `PARTIAL_ASSOCIATIVE_BINDING`**, 10 `ASSOCIATIVE_BINDING_ESTABLISHED` |
| **Conflict** | Ranks **8 and 9 are swapped**, and ranks 1–2 use different identifiers. Since "earlier classifications always override later ones," a swap changes outcomes: under the old list a partial result would outrank a failure verdict; under the amendment it would not. |
| **Proposed resolution** | **Amendment order governs.** The implementation already matches it (`study_plan.json` `classifications`). Old identifiers are retired. |
| **Status** | ✅ Resolved in draft §16 |

### C-11 — "Stronger-absent" contrast — **MAJOR**

| | |
|---|---|
| **Old proposal** (§13 Gate 3) | "correct-minus-**stronger-absent** ≥10 points" |
| **Amendment** | §C Control freeze: "**No maximum, minimum, best-of, or stronger-of selection is allowed.**" Primary ABSENT is fixed as `absent_unpaired`; `absent_placeholder` is secondary and reported only. |
| **Conflict** | Direct prohibition. Selecting the "stronger" absent control post hoc is exactly the optimistic-selection pattern the amendment forbids. |
| **Proposed resolution** | **Reject.** Use `absent_unpaired` as primary, unconditionally. Report `absent_placeholder` separately with no gate authority. |
| **Status** | ✅ Resolved in draft §13 |

### C-12 — Sample sizes — **MAJOR**

| | |
|---|---|
| **Old proposal** (§14) | "at least **10,000** frozen base episodes per seed and condition for confirmation" |
| **Amendment** | §C: development ≥1,000; confirmation **exactly 2,000**; locked core **exactly 4,000**; robustness 2,000 with ≥200 per stratum. Plus: "Increasing a frozen sample size after inspecting outcomes is prohibited." |
| **Conflict** | 10,000 ≠ exactly 2,000. "At least" vs "exactly" is itself the conflict — the amendment deliberately removed the discretion. |
| **Proposed resolution** | **Reject** the ≥10,000 rule. Use amendment counts. Phase C is development-stage, so the ≥1,000 minimum applies, with an exact count to be fixed prospectively. |
| **Status** | ⚠️ Partially resolved — exact count is `D-07` |

### C-13 — Model scales — **CRITICAL**

| | |
|---|---|
| **Old proposal** (§10) | "The repository's approximately **1M-parameter L3 builder** is reported as the optional V10.10 **L2** research control" |
| **Amendment** | §B.4 Exclusions: "**L2 and L3 are excluded.**" §I: "Only L0 and L1 are accepted. L2, L3, Candidate C, and production configurations are rejected." |
| **Conflict** | Direct prohibition. |
| **Proposed resolution** | **Reject.** Phase C uses L1 only. `build_amended_model` already fail-closes on any other scale. |
| **Status** | ✅ Resolved in draft §5 |

### C-14 — Compute ledger — **CRITICAL**

| | |
|---|---|
| **Old proposal** (§17) | Core study ≈ **0.8–1.3B tokens, 1–3 PFLOP**; optional cap ≈ 1.8B tokens, 5 PFLOP; "1,000-step measured throughput pilot" |
| **Amendment** | ≤64 updates × ≤128 episodes = **≤8,192 episodes of gradient exposure per run** |
| **Conflict** | Off by many orders of magnitude. The 1,000-step pilot alone exceeds the ceiling ~15.6×. |
| **Proposed resolution** | **Reject** the entire ledger as inapplicable. Phase C cost must be recomputed from the frozen envelope. |
| **Status** | ✅ Resolved in draft §8 |

### C-15 — Serialization and query formats — **MAJOR**

| | |
|---|---|
| **Old proposal** (§7) | Pair formats F-A…F-D; query formats Q-A…Q-C; "one seed, **2,000 steps**" |
| **Amendment** | §B.2/§B.3: primary formats are **exactly** S1–S3 and Q1–Q3. "F-A–F-D may remain only as deprecated legacy fixtures … No F-format result may influence primary selection, gates, classifications, stopping decisions, or primary multiplicity families." |
| **Conflict** | Format families are superseded; 2,000 steps also breaches C-01. |
| **Proposed resolution** | **Reject.** Phase C uses the Phase A frozen `S2_Q2` and `S3_Q2` only. |
| **Status** | ✅ Resolved in draft §4 |

### C-16 — Difficulty-level pair counts — **CRITICAL** ⭐

| | |
|---|---|
| **Old proposal** (§8) | B0 = 1 pair; **B1 = 2 pairs**; **B2 = 4 keys and 4 values**; B3 = B2 + 4 distractors; B4 = 8 pairs; B5 = B2 presented twice |
| **Amendment** (§I line 1124) | "B1/B2/B3/B4/B5 contain **1/2/4/8/16** pairs" → **B1 = 1**, **B2 = 2**, B3 = 4, B4 = 8, B5 = 16 |
| **Implementation** | `v10_10_binding_harness.py:577` → `{"B0": 1, "B1": 1, "B2": 2, "B3": 4, "B4": 8, "B5": 16}` — **matches the amendment** |
| **Conflict** | The two documents disagree about what B1 and B2 *are*. This is the most consequential conflict in the register. |

**Why this is critical — the degeneracy proof.**

Under the amendment, **B1 has exactly one pair**. The primary ABSENT control
`absent_unpaired` preserves the key/value token multiset and destroys pair boundaries
(`v10_10_binding_harness.py:735-742`), producing for a one-pair episode:

```text
<BOS> <BAG> k1 <BAG> v1 <BAG> … query … <ANS>
```

The single value `v1` **is the target**. It is recoverable by copying the only value
present — no key use, no binding. Therefore

\[
\Delta_{\mathrm{primary}}^{B1}
= \operatorname{EM}_{\mathrm{CORRECT}} - \operatorname{EM}_{\mathrm{ABSENT\_UNPAIRED}} \equiv 0
\]

identically, for any model, optimizer, LR, step budget, or scale. The G4 requirement
"B1 and B2 CORRECT−primary-ABSENT difference at least 0.10" is **unsatisfiable at B1 by
construction**.

**Empirical corroboration.** All six Phase B runs report
`delta_correct_absent_primary = 0.0` exactly, with `correct` EM = 1.0 **and**
`absent_unpaired` EM = 1.0. This is the predicted signature, observed without exception.

**Consequence for the recorded Phase B result.** "B1 FAILED" is best read as a
**benchmark-construction** outcome (precedence rank 2, `TASK_CONSTRUCTION`), not as
evidence about the model. Under the frozen precedence, rank 2 **overrides** rank 4
(`OPTIMIZATION_LIMIT`) — so this must be resolved before an optimization phase can be
interpreted at all.

| | |
|---|---|
| **Proposed resolution** | Escalate as **blocking**. Options: (a) formally classify the B1 cell `TASK_CONSTRUCTION` and exclude B1 from the primary contrast; (b) amend the primary ABSENT control at B1 to something non-degenerate at one pair; (c) amend level sizes so B1 has ≥2 pairs (aligning with the old proposal's intent). **Each requires a versioned amendment.** |
| **Status** | ⚠️ **UNRESOLVED — BLOCKING** — `D-01` |

### C-17 — Gate namespace collision — **MODERATE**

| | |
|---|---|
| **Old proposal** (§13) | "Gate 0" … "Gate 5" — six readiness gates with their own thresholds (e.g. Gate 2 "correct-support validation ≥80%") |
| **Amendment** (§B.5) | "G0" … "G6" — seven gates with entirely different definitions (e.g. G2 is a B0 identity-copy positive control at ≥0.99) |
| **Conflict** | Similar names, **different semantics and different numbering**. A reader or script conflating "Gate 2" with "G2" would apply an 0.80 threshold where 0.99 is required. |
| **Proposed resolution** | Retire "Gate N" vocabulary from all forward-looking documents. Use **G0–G6** exclusively. Consider an explicit deprecation banner on the calibration study. |
| **Status** | ✅ Resolved in draft (G-notation only) |

### C-18 — Value cardinality and chance level — **MAJOR**

| | |
|---|---|
| **Old proposal** (§4) | "at least 32 single-token keys, **exactly four single-token values**"; "Output prediction is **restricted to the four registered value classes**, making chance exactly 25%" |
| **Amendment** (§B.2) | Value atoms occupy IDs **64–95** (32 atoms); values are "a nonempty sequence of atoms"; scoring is whole-span exact match. **No four-class restriction appears anywhere.** |
| **Observed** | `absent_placeholder` = exactly **0.25** in all 9 Phase A configurations and all 6 Phase B runs — the signature of a four-way effective output space |
| **Conflict** | The executed behaviour matches the **superseded** document, not the amendment. Either a four-class restriction survives in the implementation (undocumented in the amendment), or the coincidence needs another explanation. |
| **Proposed resolution** | Determine the effective output cardinality empirically and pin it in the Phase C spec. Every Phase C threshold is an absolute accuracy difference and is therefore meaningless until chance level is fixed. **No value has been guessed.** |
| **Status** | ⚠️ Unresolved — `D-06` |

### C-19 — Legacy continuity replay — **MODERATE**

| | |
|---|---|
| **Old proposal** (§6) | Replay V10.9 F8: L1, peak LR 0.001, **batch 256**, **1,000 steps**, **seed 42** |
| **Amendment** | Explicitly authorizes "the previously authorized V10.9 continuity validation" (header) while excluding seed 42 from "the amended scientific campaign" and capping V10.10 runs at 64×128 |
| **Conflict** | Not a true contradiction — continuity replay is a *separate, pre-authorized* activity outside the V10.10 campaign — but the two regimes are easy to conflate, and a conflation would breach the compute ceiling and reintroduce seed 42. |
| **Proposed resolution** | Keep continuity strictly quarantined: distinct code path, distinct artifacts, `purpose` never `development`/`confirmation`, and never counted as a V10.10 scientific result. The runner already separates it (`run_legacy_continuity`, `legacy_v10_9_cosine_lr`). Phase C must not invoke it. |
| **Status** | ✅ Resolved by quarantine |

---

## 4. CONFLICT SUMMARY

| Severity | Count | IDs |
|---|---:|---|
| **CRITICAL** | 7 | C-01, C-02, C-03, C-05, C-06, C-08, C-13, C-14, C-16 *(9 rows; C-13/C-14 counted with criticals)* |
| **MAJOR** | 7 | C-04, C-07, C-09, C-11, C-12, C-15, C-18 |
| **MODERATE** | 3 | C-10, C-17, C-19 |
| **Total** | **19** | C-01 … C-19 |

| Resolution status | Count | IDs |
|---|---:|---|
| ✅ Resolved in the draft (amendment governs) | 10 | C-02, C-03, C-05, C-09, C-10, C-11, C-13, C-14, C-15, C-17, C-19 |
| ⚠️ Unresolved — decision required | 8 | C-01, C-04, C-06, C-07, C-08, C-12, C-16, C-18 |
| 🚫 **Blocking** | **1** | **C-16 → `D-01`** |

**Verdict: the old Phase C proposal cannot be executed in any form.** Of its four
substantive design elements — 10,000-step budget, warm-up + schedule, LR anchoring, and
the O-A/O-B/O-C objective ladder — three violate frozen invariants outright and the
fourth (LR) targets a grid the authoritative document never defines.

---

## 5. UNRESOLVED DECISIONS

Cross-referenced to the draft's Section 19 register.

| ID | Decision | From | Blocking? |
|---|---|---|---|
| **D-01** | **B1 primary contrast degenerate by construction (Δ ≡ 0). Reclassify as `TASK_CONSTRUCTION` and/or amend the level or control definition?** | **C-16** | **YES** |
| **D-02** | Authoritative LR grid values | C-04 | YES |
| **D-03** | Authoritative step grid values | C-01, C-06 | YES |
| **D-04** | `OPTIMIZATION_LIMIT` requires a cell to pass **G4** (locked test). Is Phase C non-classifying by design? | §E rank 4 | YES |
| **D-05** | Admissibility of O-B; recommendation to **reject O-C** (breaks 224,128 parameter freeze) | C-07, C-08 | YES |
| **D-06** | Effective value cardinality / chance level | C-18 | YES |
| **D-07** | Exact episodes per seed per cell | C-12 | No |
| **D-08** | Both frozen configurations or `S2_Q2` only | §C | No |
| **D-09** | G2 specifies **confirmation** seeds; Phase A used a development analogue | §B.5 | No |
| **D-10** | Respect the 64-step ceiling, or raise it by versioned amendment | C-01, C-14 | YES |
| **D-11** | Namespace `purpose`: `development` vs `diagnostic` | §B.1 | YES |
| **D-12** | No Holm family covers LR/step multiplicity | §C | YES |

---

## 6. RECOMMENDED SEQUENCE

Offered as a recommendation for review, not as an authorization.

1. **Resolve `D-01` first, and independently of Phase C.** The B1 degeneracy is a
   rank-2 finding. Under the frozen precedence it outranks everything Phase C could
   produce. Resolving it may also change what Phase C should even ask.
2. **Resolve `D-06`** (chance level). Every threshold is an absolute difference;
   without a pinned chance level no threshold has meaning.
3. **Decide `D-10`** (envelope). This determines whether Phase C is a small in-envelope
   rule-out or requires a versioned amendment — and therefore its cost and its power.
4. **Decide `D-12`** (multiplicity) and `D-04` (classification reachability). Together
   these determine whether Phase C is inferential or exploratory.
5. **Fix `D-02`, `D-03`, `D-05`, `D-11`**, then `D-07`, `D-08`, `D-09`.
6. **Refresh G0** on the post-amendment state
   (`experiments/v10_10/PROPOSAL_g0_integrity_manifest.json`) — currently there is no
   valid integrity baseline.
7. **Adopt the provenance schema**
   (`experiments/v10_10/PROPOSAL_execution_provenance_schema.json`) *before* any further
   run, so no future run can repeat the Phase B provenance gap.
8. Only then: freeze, hash, implement, revalidate, and seek explicit Phase C authorization.

---

## 7. WHAT THIS DOCUMENT DOES NOT DO

- It does not modify `docs/V10_10_ASSOCIATIVE_BINDING_CALIBRATION_STUDY.md`.
- It does not modify the approved amendment.
- It does not modify, reinterpret, or rewrite any Phase A or Phase B artifact.
- It does not reclassify the recorded Phase B result. `BINDING_NOT_ESTABLISHED_AT_B2`
  stands as recorded; C-16 is raised as a **finding for review**, not an applied change.
- It does not resolve any decision.
- It does not authorize any execution.

---

*End of reconciliation. Non-authoritative. No scientific execution is authorized by this document.*
