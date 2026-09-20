# NIRMAL-1 — STAGE 0 ARCHITECTURE BASELINE REVIEW
STATUS: REVIEW ONLY — NO IMPLEMENTATION AUTHORIZATION

> **Date**: 2026-09-19
> **Reviewed documents** (both unmodified by this review):
> - `docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md` (the DRAFT)
> - `docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md` (the REVIEW)
>
> **Governance baselines preserved**:
> - Production: **STRICT NO-GO**
> - Phase C: **NOT AUTHORIZED** — `PHASE_C_PREPARATION_BLOCKED`
> - Harness recovery: `HARNESS_RECOVERY_BLOCKED`
> - V10.10: research subsystem only; artifacts unmodified
> - Protected paths: `src/nirmal/`, `data/shards/` — unmodified
>
> This document authorizes nothing. It classifies Stage 0 readiness only.

---

## 1. Architecture Baseline (TASK 1)

### 1.1 Agreed architecture (both documents concur)
- Nirmal-1 is a **skill-based AGI/ASI-oriented system**; skills are the versioned,
  verified, provenance-tracked unit of capability.
- 16-subsystem decomposition (Core Intelligence → Model/Provider Layer).
- Six logical memory layers (Working, Episodic, Semantic, Procedural, Task, Provenance);
  Semantic accepts **verified writes only**; Provenance is append-only and tamper-evident.
- Skill lifecycle: Discover → Select → Execute → Verify → Compose → Propose →
  Evaluate → **manually gated** Promote. No autonomous self-improvement is
  implemented or claimed.
- Governance gates all side effects; fail-closed; policy is data.
- Strict firewall between V10.x research and the architecture track; benchmarks
  are not treated as proof of AGI/ASI.
- Storage: Git-tracked metadata (skills, manifests, frozen benchmarks, configs)
  vs. local-only bulk (weights, checkpoints, memory stores, forensic logs, scratch);
  full-scale datasets remain cluster-side.

### 1.2 Contradictions between DRAFT and REVIEW (NOT silently resolved)

| # | Contradiction | DRAFT position | REVIEW position | Required decision |
|---|---|---|---|---|
| C1 | **Neural bridge as Reasoning Interface reference** | §6: `neural_bridge.py` becomes reference implementation of the Reasoning Interface | §5.2: `NeuralBridge` reads hidden states / token-level perplexity unavailable from external provider APIs — latent coupling | Split Reasoning Interface into a provider-portable core and an **optional introspection extension**? Owner must decide before interfaces freeze. |
| C2 | **Roadmap ordering** | §11: linear Stages 0–9; Verification at Stage 6 *after* controller integration (Stage 5) | §9: inserts **Stage 1.5 Governance substrate**; puts Verification (S6) *before* controller refactor (S5); memory (S4) parallel-early | Adopt one authoritative ordering. The REVIEW ordering is safer (fail-closed governance first) but is not yet the approved baseline. |
| C3 | **`compose_strategies()` status** | §3.7: composition "evolves" existing `procedural.compose_strategies()` `[PARTIAL]` | §2 item 7: existing implementation is **hardcoded to toy X/Y/Z subskills** — `CONFLICTS WITH CURRENT DESIGN`; must be replaced, not evolved | Reclassify composition as new-build (`MISSING`, replace) or evolve-with-rewrite. Affects Stage 2/3 scope. |
| C4 | **Governance implementation locus** | §3.15 defines GovernanceEngine but not its substrate position | §3.1 item 5: governance must be an **independent deterministic substrate beneath the skill system** (never itself a skill) to avoid circular dependency | Codify "governance is not a skill" as a frozen architectural invariant. |

### 1.3 Missing interfaces / gaps (identified by REVIEW, absent from DRAFT)
- **Typed failure taxonomy** for `SkillResult` (TIMEOUT, PRECONDITION_FAILED,
  SANDBOX_VIOLATION, PERMISSION_DENIED, INTERNAL_EXCEPTION, VERIFICATION_FAILED).
- **Rollback / compensation semantics** for composite skills with side effects
  (`compensation_skill` or transactional rollback).
- **Trust demotion path**: `trusted → quarantined → deprecated` (DRAFT only defines promotion).
- **Windows sandboxing technology** unspecified (AppContainer vs. Docker vs. Job Objects).
- **SkillExecutor** and **ContextManager** have no formal contracts (addressed in §2 below).
- **Registration-time DAG validation** for composite skill recursion.
- **Tokenizer-independent token budgeting** for external providers.

### 1.4 Ambiguous terminology (must be defined before Stage 1)
- `sandbox: "restricted"` — no defined semantics.
- `trust_level` values — promotion criteria defined, demotion undefined.
- `capabilities` tags — no controlled vocabulary.
- Skill `kind: prompt` — execution semantics undefined.
- Reliability "carry over with explicit migration note" — migration note format undefined.

### 1.5 Unsafe assumptions flagged
- Storage under OneDrive tree (both documents agree this is unsafe; REVIEW marks it CAUTION).
- Availability of hidden states / local tokenizers from all providers (C1).
- Windows POSIX-style isolation availability (none exists natively).
- **Candidate C anchoring**: sizing language gravitates to the 48.3 GB checkpoint;
  REVIEW requires it be treated as one unverified local provider, not an anchor.
- **New (this review)**: assumption that ~300 GB is available at `C:\` — physically
  measured **false** (see §5).

### 1.6 Implementation dependencies (consolidated)
Governance substrate → interfaces → registry/memory → executor → verification →
controller integration → acquisition → evaluation → scaling. Exact order is
blocked on decision C2.

---

## 2. Stage-1 Interface Contracts (TASK 2) — SPECIFICATION ONLY, NO CODE

Assessment verdicts: ✅ sufficiently specified in baseline · ⚠️ specified here, needs freeze · ❌ was missing, defined here for the first time.

### 2.1 `SkillManifest` ⚠️
- **Purpose**: declarative, immutable description of a skill (identity → composition ports).
- **Inputs**: authored/generated manifest data conforming to §3 schema.
- **Outputs**: validated, canonicalized manifest object; content hash.
- **Lifecycle**: draft → validated → registered (immutable per version) → deprecated/quarantined.
- **Error model**: `SCHEMA_INVALID`, `VERSION_CONFLICT`, `DEPENDENCY_UNRESOLVED`, `DAG_CYCLE`.
- **Versioning**: semver; published versions immutable; any change = new version.
- **Provenance**: mandatory `provenance` block (origin, evidence, creator identity); manifest hash recorded on registration.
- **Permissions**: registration requires `WRITE(skill_registry)` grant.
- **Dependencies**: none (pure data contract) — must remain dependency-free.
- **Testability**: schema round-trip, canonical hash stability, invalid-manifest rejection matrix.

### 2.2 `SkillRegistry` ⚠️
- **Purpose**: authoritative catalog; resolve, search, dependency closure, trust state.
- **Inputs**: manifests, version specs, capability queries, trust transitions.
- **Outputs**: resolved manifest (exact version), search results, dependency closures, trust state.
- **Lifecycle**: load catalog → serve queries → append registrations → never delete (deprecate only).
- **Error model**: `NOT_FOUND`, `AMBIGUOUS_VERSION`, `DAG_CYCLE` (registration-time rejection per C4/§1.3), `TRUST_TRANSITION_DENIED`.
- **Versioning**: registry format itself versioned; catalog is Git-tracked.
- **Provenance**: every registration/trust transition emits an audit record with actor + evidence refs.
- **Permissions**: reads open; writes and trust transitions gated by GovernanceEngine; `proposed→evaluated→trusted` requires evaluation evidence + human approval flag.
- **Dependencies**: SkillManifest, GovernanceEngine, storage (`skills/` area).
- **Testability**: round-trip persistence, closure correctness, cycle rejection, trust-gate fail-closed tests.

### 2.3 `SkillExecutor` ❌ (previously missing as a contract)
- **Purpose**: sole runtime for skill invocation under manifest constraints.
- **Inputs**: skill ref (id@version), typed args, execution context (budget, permissions, sandbox policy).
- **Outputs**: `SkillResult` = { status, value, evidence, resource_usage, trace_id }.
- **Lifecycle**: resolve → precondition check → permission acquisition → sandboxed run → verification handoff → provenance emit.
- **Error model (frozen taxonomy)**: `TIMEOUT`, `PRECONDITION_FAILED`, `SANDBOX_VIOLATION`, `PERMISSION_DENIED`, `INTERNAL_EXCEPTION`, `VERIFICATION_FAILED` — no untyped failures.
- **Versioning**: executor version recorded in every trace.
- **Provenance**: one record per invocation (inputs hash, outputs hash, decision id, resource usage).
- **Permissions**: may only reach environments via Tool Interface; every tool class checked per call.
- **Dependencies**: Registry, Tool Interface, GovernanceEngine, VerificationEngine, Provenance memory.
- **Testability**: constraint-violation injection (timeout, over-budget tool calls), permission-denial paths, deterministic trace capture. **Rollback semantics: UNRESOLVED (blocker B3).**

### 2.4 `Provider` ⚠️ — see §4 for boundary resolution.
- **Purpose**: model-agnostic access to inference capabilities.
- **Inputs**: `ContextPackage`, generation params, optional tool schemas.
- **Outputs**: completions/scores/embeddings + usage metadata.
- **Lifecycle**: register identity → capability probe (measured, not claimed) → serve → retire.
- **Error model**: `UNAVAILABLE`, `CONTEXT_OVERFLOW`, `CAPABILITY_UNSUPPORTED`, `PROVIDER_ERROR(detail)`.
- **Versioning**: immutable Model Identity (name, version, weights/tokenizer hashes where available).
- **Provenance**: every call logs model identity hash + parameters.
- **Permissions**: provider registration and selection are governance-visible policy decisions.
- **Dependencies**: none upward (leaf layer).
- **Testability**: contract conformance suite runnable against a stub provider; capability metadata must be reproducibly measurable.

### 2.5 `MemoryStore` ⚠️
- **Purpose**: uniform persistence contract for the six layers (§3, TASK 5 boundaries in §4 below).
- **Inputs**: layer-typed records; queries (key, filter, similarity).
- **Outputs**: records + provenance refs; never silently empty on error.
- **Lifecycle**: open → read/append → consolidate (governed batch) → archive; **no in-place update on Semantic/Provenance**.
- **Error model**: `WRITE_REJECTED_UNVERIFIED` (semantic), `APPEND_ONLY_VIOLATION`, `STORE_CORRUPT`, `CONFLICT_ARCHIVED` (contradiction path).
- **Versioning**: schema versioned; migration scripts governed.
- **Provenance**: every write carries actor + verification verdict reference.
- **Permissions**: per-layer write ACLs (§4).
- **Dependencies**: GovernanceEngine (write gates), storage root (§5).
- **Testability**: durability (kill/restart), contradiction-archival, append-only enforcement, retrieval parity with current in-memory implementations.

### 2.6 `GovernanceEngine` ❌ — minimum Stage-1 contract (TASK 6)
- **Purpose**: deterministic, fail-closed permission substrate **beneath** the skill system (never a skill — frozen invariant per C4).
- **Must represent (minimum)**: operations `READ` / `WRITE` / `EXECUTE` on typed resources; **denial with machine-readable reason**; resource limits (time, calls, bytes); audit events; provenance linkage (decision id in every downstream record); **skill trust state** transitions; **human-approval-required** flag that software cannot satisfy on its own.
- **Inputs**: `(actor, operation, resource, context)`.
- **Outputs**: `Decision { grant|deny, reason, limits, decision_id, human_approval_required }`.
- **Lifecycle**: load policy (version-controlled data files) → evaluate → append decision log; policy changes are themselves audited events.
- **Error model**: evaluation failure ⇒ **DENY** (fail-closed); `POLICY_INVALID` blocks startup.
- **Versioning**: policy files versioned; decision log records policy version used.
- **Provenance**: append-only decision log, hash-chained.
- **Permissions**: policy edits require human action outside the engine.
- **Dependencies**: none (substrate). Everything else depends on it.
- **Testability**: default-deny matrix, protected-path denial tests (`src/nirmal/`, `data/shards/`, V10.10 artifacts), human-gate non-bypass test. **Real computer control remains disabled — not represented as grantable in Stage 1 policy.**

### 2.7 `VerificationEngine` ⚠️
- **Purpose**: objective verdicts on skill results/proposals; pluggable verifiers (predicate, numeric-tolerance, string/regex, structural, test-suite; prover later).
- **Inputs**: `SkillResult` + manifest `verification` block.
- **Outputs**: `Verdict { pass|fail, evidence, verifier_id, calibration_stats }`.
- **Lifecycle**: resolve verifier by method → run in isolation → attach verdict → feed calibration tracking.
- **Error model**: `VERIFIER_UNAVAILABLE`, `CRITERIA_INVALID`, verifier crash ⇒ **fail** verdict (fail-closed).
- **Versioning**: verifier implementations versioned; verdict records verifier version.
- **Provenance**: verdicts stored with evidence; semantic memory writes require verdict reference.
- **Permissions**: test-suite verifiers run inside sandbox policy.
- **Dependencies**: sandbox (for test-suite mode), Provenance memory.
- **Testability**: symmetric ground-truth checks (V5.1 falsification ethos), injected-invalid-result detection, calibration (Brier-style) tracking tests.

### 2.8 `ContextManager` ❌ — minimum conceptual boundary (TASK 7)
- **Purpose**: assemble bounded, provenance-preserving context for any provider.
- **Responsibilities**: memory retrieval orchestration; relevance filtering/ranking; **token budgeting via the provider's Context Interface** (with a conservative provider-supplied estimator when no local tokenizer exists — resolves the C1-adjacent tokenizer assumption); deterministic truncation/eviction policy; provenance tags on every included fragment (source layer + record id).
- **Inputs**: goal, budget (from provider capability metadata), memory handles.
- **Outputs**: `ContextPackage` (ordered fragments + provenance map + budget report).
- **Error model**: `BUDGET_UNSATISFIABLE`, `RETRIEVAL_FAILED(layer)`.
- **Versioning**: assembly policy versioned; package records policy version.
- **Provenance**: fragment→source mapping mandatory (enables post-hoc audit of what the model saw).
- **Permissions**: read ACLs of memory layers apply (§4).
- **Dependencies**: MemoryStore, Provider capability metadata. **Never depends on a concrete model or tokenizer implementation.**
- **Testability**: budget-compliance property tests, eviction determinism, provenance-map completeness.

---

## 3. Skill Manifest — Minimum Authoritative Schema Baseline (TASK 3)

Baseline = DRAFT §4.1 schema **plus** the following mandatory amendments (from §1.3).
Fields marked ⊕ are additions; no actual skills are created.

| Field | Requirement |
|---|---|
| `skill_id` | Stable, namespaced (`nirmal.<domain>.<name>`), globally unique |
| `version` | Semver; immutable once registered |
| `capabilities` | Tags from a **controlled vocabulary** ⊕ (vocabulary file itself versioned) |
| `prerequisites` | Skill refs with version constraints; must resolve at registration |
| `inputs` / `outputs` | Typed schemas (JSON-Schema style); required for composition type-checking |
| `tools_required` | Tool classes only (never concrete endpoints); permission-checked at execution |
| `resource_limits` ⊕ | `timeout_s`, `max_tool_calls`, `max_memory_mb`, `max_output_bytes` (renames DRAFT `execution_constraints`, adds byte/memory caps) |
| `permissions` ⊕ | Explicit operation set requested (`READ`/`WRITE`/`EXECUTE` × resource classes) — evaluated by GovernanceEngine |
| `sandbox_policy` ⊕ | Named policy id with defined semantics (replaces ambiguous `sandbox: "restricted"`); **policy catalog is a Stage-1 deliverable; engine choice on Windows is UNRESOLVED (B4)** |
| `side_effects` | `none | workspace | external`; if not `none`: `compensation_skill` ref **or** `rollback: transactional` ⊕ (B3 must be decided to freeze semantics) |
| `verification` | Method + success criteria (as DRAFT) |
| `provenance` | Origin (`authored|learned|composed`), source trajectories, creator, evidence refs — mandatory |
| `trust_state` ⊕ | `proposed | evaluated | trusted | quarantined | deprecated` (adds demotion states; renames `trust_level`) |
| `dependency_graph` | Resolved closure; **registry must reject cycles at registration** ⊕ |
| `composition` | `composable` flag + typed in/out ports |

Schema freeze is **blocked** until B3 (rollback) and B4 (sandbox) are decided.

---

## 4. Provider Abstraction Boundary (TASK 4) and Memory Boundaries (TASK 5)

### 4.1 Provider: abstract contract vs. model-specific adapters

The core architecture must never require: one model, one provider, hidden-state
access, one tokenizer implementation, or one inference API.

| Belongs in the **abstract Provider contract** (portable) | Belongs in **model-specific adapters** (optional extensions) |
|---|---|
| `generate(context, params)` — text/tokens out | Hidden-state / activation access |
| `count_tokens(text)` — may be an estimator; contract requires only a **conservative upper bound** | Exact local tokenizer objects |
| Capability metadata (measured context length, tool-call support, cost/latency) | Token-level perplexity / logit scoring over arbitrary spans |
| Optional declared capabilities: `embed()`, `score(choices)` (coarse), structured tool-calling | Layer-wise introspection, gradient access |
| Model Identity descriptor (hashes where obtainable) | Weight loading/unloading mechanics |
| Typed error model (§2.4) | Provider-specific retry/batching internals |

**Resolution of C1 (proposed, requires owner sign-off)**: `neural_bridge.py`
functionality becomes a **`LocalIntrospectionAdapter`** — an optional extension
interface implemented only by local Nirmal providers. No core subsystem
(Reasoning, ContextManager, SkillExecutor) may *require* it; subsystems may
*prefer* it when the active provider declares the capability. Until signed off,
C1 remains an open contradiction.

Candidate C is one unverified local provider identity — never an architectural anchor.

### 4.2 Memory layer Stage-1 boundaries

| Layer | Write access | Read access | Verification req. | Persistence | Provenance | Conflict handling | Retention boundary |
|---|---|---|---|---|---|---|---|
| **Working** | Orchestrator only | Orchestrator, ContextManager, Reasoning | None (transient; never propagates unverified content to Semantic) | RAM; snapshot into episodic trace at task end | Snapshot tagged with task id | N/A (scratch) | Purged at goal termination |
| **Episodic** | Orchestrator at LEARN state (append-only) | Learning loop, Acquisition, ContextManager, Evaluation | Trajectory must embed verifier verdicts | Durable, append-only | Full trace + decision ids | Records history as-it-happened; no rewrites | Rolling window + governed consolidation; archive, never delete |
| **Semantic** | VerificationEngine-approved writers only (Learning loop with verdict ref) | All cognition subsystems | **Mandatory** — unverified writes rejected (`WRITE_REJECTED_UNVERIFIED`) | Durable, versioned | Verdict ref per fact | Contradiction ⇒ archive old fact (`is_outdated`, version chain); never overwrite | Indefinite with version chains |
| **Procedural/Skill** | SkillRegistry lifecycle only | Planner, Executor, Acquisition, Evaluation | Promotion battery + human gate; demotion path required | Durable; Git-tracked manifests | Registration/transition audit records | Version pinning (`id@exact`) for active tasks | Immutable versions; deprecate/quarantine only |
| **Task** | Planner + Orchestrator | Orchestrator, ContextManager | Plan nodes must resolve to registered skill refs | Durable session state | Replan history kept | Replan cap (`max_replan_attempts`) ⇒ typed failure | Completed plans compacted into Episodic |
| **Provenance** | All subsystems, **append-only** | Auditors, Evaluation, Governance | Self-describing SHA-256 per record | Durable, hash-chained, permanent | Is itself the provenance sink | None possible (no mutation ops) | **Permanent**; archival only via explicit governed action |

No concrete database backend is selected here (consistent with the approved
architecture leaving this open — DRAFT §12.2); Stage-1 requires only the
interface contract (§2.5).

---

## 5. Storage Root Decision (TASK 8)

**Designated Root**: `D:\Nirmal-1-Store` (registered external storage root).

| Criterion | Assessment |
|---|---|
| Separation from OneDrive/repo | ✅ `D:\Nirmal-1-Store` is physically on a separate drive (D:), completely outside the OneDrive sync tree (`C:\...\OneDrive\Desktop\Nirmal 1`) — resolves the REVIEW §6.2 CAUTION (lock contention, sync corruption, bandwidth exhaustion) |
| Suitability for memory DBs, forensic archives, scratch | ✅ Suitable in kind: local filesystem, zero cloud sync interference. *Note on filesystem*: Drive D: is exFAT. Software-level permissions must be strictly enforced by GovernanceEngine since exFAT lacks native NTFS ACLs. |
| Model/checkpoint storage | ✅ Ample capacity for model weights and rolling training checkpoints |
| Large datasets | ⚠️ Local subsets/pilots only; full-scale 200B-token corpora remain cluster-side (V8.2 architecture) |
| **Capacity — VERIFIED RESOLVED** | ✅ **Physically measured 2026-09-19: Drive D: has 440.11 GB free (468.74 GB total, healthy).** The 300 GB storage requirement is fully satisfied with 140+ GB safety headroom. |
| Backup requirements | `skills/`, `memory/`, `forensic/`, manifests need periodic snapshots to a separate backup destination |

**Decision status: RESOLVED & REGISTERED.**
The repository remains at `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`.
The external storage root is formally registered as `D:\Nirmal-1-Store`.
The 11 registered subdirectories (`models\`, `datasets\`, `skills\`, `memory\`, `training\`, `experiments\`, `evaluation\`, `artifacts\`, `forensic\`, `backups\`, `scratch\`) are designated for project data.
No files are moved or copied by this documentation update.

---

## 6. Stage-1 Acceptance Gates (TASK 9) — defined, NOT executed

Stage 1 implementation may be authorized only when ALL gates pass:

| Gate | Criterion (objective) | Status |
|---|---|---|
| G1 | All 8 interface contracts (§2) frozen in a versioned spec document; no `UNRESOLVED` markers remain | BLOCKED (pending B1, B3, B4, B7) |
| G2 | Subsystem dependency graph proven acyclic (governance substrate at the bottom; provenance sink depends on nothing) | PASSABLE (design verified) |
| G3 | Provider boundary documented incl. C1 resolution (introspection = optional adapter capability) signed off | BLOCKED (pending B1) |
| G4 | Memory boundaries (§4.2) documented and accepted, incl. write ACLs and contradiction handling | PASSABLE (boundaries defined) |
| G5 | GovernanceEngine contract documented; fail-closed default-deny stated; "governance is not a skill" invariant frozen | BLOCKED (pending B7) |
| G6 | SkillManifest schema frozen — requires B3 (rollback) and B4 (sandbox) decisions | BLOCKED (pending B3, B4) |
| G7 | Storage boundary decided: approved root location outside OneDrive with verified capacity | **PASSED** (resolved by `D:\Nirmal-1-Store`, 440.11 GB free) |
| G8 | Behavior-preservation requirement defined: Stage 1 introduces interfaces only; all existing `tests/` + `evals/` suites must pass unchanged (zero behavior change) | PASSABLE |
| G9 | Protected-path policy encoded as reviewable data: `src/nirmal/`, `data/shards/`, V10.10 artifacts deny-listed for writes | PASSABLE |
| G10 | Rollback requirements defined: Stage-1 changes revertible by removing new modules; no edits to existing modules | PASSABLE |
| G11 | Test plan specified per interface (§2 testability rows) with fail-closed cases enumerated | PASSABLE |
| G12 | Roadmap ordering contradiction (C2) resolved and one sequence adopted as authoritative | BLOCKED (pending B2) |

---

## 7. Research / Production Separation (reaffirmed)

- V10.10 remains a research subsystem only; its artifacts are unmodified.
- Nothing in this review converts research results into capability claims.
- Production remains **STRICT NO-GO**; Phase C remains **NOT AUTHORIZED**.
- This review does not authorize Stage 1; it defines what authorization requires.

---

## 8. Blocking Issues (TASK 10 detail)

| ID | Issue | Evidence | Affected interface | Required decision | Status |
|---|---|---|---|---|---|
| B1 | Reasoning-interface coupling to hidden-state introspection (contradiction C1) | DRAFT §6 vs REVIEW §5.2 | Provider, ContextManager, Reasoning | Adopt optional-adapter split (§4.1) or revise DRAFT §6 | **OPEN** |
| B2 | Conflicting roadmap orderings (C2) | DRAFT §11 vs REVIEW §9 (Stage 1.5 governance-first; S6 before S5) | All (sequencing) | Owner adopts one authoritative sequence | **OPEN** |
| B3 | No rollback/compensation semantics for side-effecting composite skills | REVIEW §3.1 item 2; absent from DRAFT §4 | SkillManifest, SkillExecutor | Choose `compensation_skill` vs transactional rollback (or hybrid); freeze in schema | **OPEN** |
| B4 | Windows sandbox engine unspecified (`sandbox: "restricted"` undefined) | REVIEW §3.1 item 3; DRAFT §12.4 open | SkillExecutor, SkillManifest, VerificationEngine (test-suite mode) | Select engine (AppContainer / Job Objects / container) for the Stage-1 policy catalog | **OPEN** |
| B5 | Trust demotion/revocation path missing | REVIEW §3.1 item 4; DRAFT defines promotion only | SkillRegistry, SkillManifest (`trust_state`) | Adopt `quarantined`/`deprecated` states + demotion triggers (§3 baseline) and sign off | **OPEN** |
| B6 | Storage root location and capacity | Prior draft C: (53.5 GB free) vs 300 GB plan | MemoryStore, storage layout | **RESOLVED**: Formally registered as `D:\Nirmal-1-Store` (440.11 GB free, outside OneDrive) | **RESOLVED** |
| B7 | Governance policy format & approval authority undecided | DRAFT §12.5; REVIEW Stage 1.5 requirement | GovernanceEngine | Choose policy representation (data files) and name human approval authority | **OPEN** |
| B8 | Composition precursor conflict (C3): existing `compose_strategies()` is toy-hardcoded | REVIEW §2 item 7 | SkillRegistry, SkillExecutor (composition) | Reclassify as replace-not-evolve; adjust Stage 2/3 scope | **OPEN** |

Non-blocking (track for Stage 1): controlled capability vocabulary (§1.4),
reliability-migration note format, placeholder dirs `nirmal-1/`/`niraml-1/` cleanup decision.

---

## 9. Final Stage-0 Status (TASK 10)

While B6 (storage root) has been successfully resolved by the registration of `D:\Nirmal-1-Store`,
seven architectural blocking issues (B1–B5, B7–B8) remain open and require owner decisions
before interface contracts and the manifest schema can be formally frozen for Stage 1. Therefore:

```
STAGE_0_REQUIRES_REVISIONS
```

Preserved governance state (unchanged by this review):

```
PHASE_C_PREPARATION_BLOCKED
HARNESS_RECOVERY_BLOCKED
PRODUCTION: STRICT NO-GO
```

*End of Stage 0 baseline review. This document is a review artifact only and
authorizes no implementation.*
