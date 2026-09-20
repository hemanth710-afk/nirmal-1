# NIRMAL-1 — STAGE 1 GATE REVIEW
STATUS: GOVERNANCE EVALUATION — IMPLEMENTATION UNAUTHORIZED

> **Date**: 2026-09-20  
> **Canonical Repository**: `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`  
> **Storage Policy**: `D:\Nirmal-1-Store` / USB storage is **no longer part of the active Nirmal-1 workflow**. Operations are strictly confined to the desktop repository. Zero files on external storage were accessed or modified.  
>
> ### Authoritative Governance State
> - **Stage 0 Status**: `STAGE_0_REQUIRES_REVISIONS` (Owner decisions recorded; baseline document alignment and gate verification pending)
> - **Stage 1 Status**: `STAGE_1_IMPLEMENTATION_UNAUTHORIZED`
> - **Phase C Status**: `NOT AUTHORIZED` (`PHASE_C_PREPARATION_BLOCKED`)
> - **Harness Recovery**: `HARNESS_RECOVERY_BLOCKED`
> - **Production Status**: `STRICT NO-GO`
> - **Protected Paths**: `src/nirmal/` (23 files, 246,321 bytes) and `data/shards/` (18 files, 477,957 bytes) are **strictly immutable and unmodified**.
> - **V10.10 Artifacts**: Unmodified research subsystem.
> - **Document Purpose**: Formal acceptance-gate evaluation for Stage 1 implementation entry. Under Nirmal-1 governance rules, approval of architectural proposals does not grant implementation authorization. Implementation remains strictly unauthorized until all twelve acceptance gates are completely resolved and verified.

---

## 1. Recorded Owner Decisions

The human Project Owner has formally reviewed [`docs/NIRMAL_1_STAGE_0_OWNER_DECISION_RECORD.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_OWNER_DECISION_RECORD.md) and recorded explicit approvals for all seven Stage 0 architectural blockers:

| Blocker ID | Description | Approved Candidate | Decision Status | Decision Timestamp | Authority |
|---|---|---|---|---|---|
| **B1** | Provider / Introspection Boundary | **Candidate 1C** (Core Portable `Provider` + Optional `LocalIntrospectionAdapter`) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B2** | Authoritative Roadmap Sequence | **Candidate 2B** (Authoritative Dependency-Ordered Sequencing: 0 $\to$ 1 $\to$ 1.5 $\to$ ... $\to$ 9) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B3** | Rollback & Compensation Model | **Candidate 3C** (Tiered Hybrid Rollback/Compensation Model) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B4** | Windows Sandbox Mechanism | **Candidate 4B** (Tiered Native Windows Isolation via Job Objects & Restricted Tokens) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B5** | Skill Trust Demotion & Revocation | **Candidate 5B** (Complete 5-State Trust Lifecycle with Quarantine Circuit Breakers) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B7** | Governance Policy & Authority | **Candidate 7B** (Declarative YAML Policies + Human Project Owner Authority) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B8** | Skill Composition Architecture | **Candidate 8A** (Clean Subsystem Replacement in `nirmal.skills.composition`) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |

---

## 2. Stage 1 Acceptance-Gate Matrix

In accordance with [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §6, all twelve Stage-1 acceptance gates are evaluated below against the current repository state:

| Gate ID | Gate Description | Status | Primary Reference / Blocker |
|:---:|---|:---:|---|
| **G1** | All 8 interface contracts frozen without `UNRESOLVED` markers | **BLOCKED** | Formal versioned specification document not yet created on disk |
| **G2** | Subsystem dependency graph proven acyclic | **PASS** | Proven in Review §9 & Blocker Resolution §8; Candidate 2B adopted |
| **G3** | Provider boundary documented and signed off (introspection = optional adapter) | **PASS** | Signed off via Owner Decision B1 (Candidate 1C) |
| **G4** | Memory boundaries and write ACLs documented and accepted | **PASS** | Codified in Baseline Review §4.2 (6-tier memory access matrix) |
| **G5** | GovernanceEngine contract documented with fail-closed default-deny | **BLOCKED** | Concrete typed interface not yet authored into frozen specification |
| **G6** | SkillManifest schema frozen incorporating B3, B4, B5 fields | **BLOCKED** | Machine-validatable schema file not yet synthesized on disk |
| **G7** | Storage boundary decided: approved root location outside OneDrive | **NEEDS REVISION** | Baseline references obsolete `D:\Nirmal-1-Store`; local off-OneDrive root required |
| **G8** | Behavior preservation defined: existing tests/evals pass unchanged | **PASS** | Invariant codified; Stage 1 adds new interfaces only; zero regression |
| **G9** | Protected-path write deny-list encoded (`src/nirmal/`, `data/shards/`) | **PASS** | Encoded in baseline JSON; 100% SHA-256 match verified |
| **G10** | Rollback requirements defined: changes revertible by removing new modules | **PASS** | Revertibility criteria established; clean module namespace |
| **G11** | Test plan specified per interface with fail-closed cases | **PASS** | Test matrices and fail-closed cases codified in Baseline Review §2 |
| **G12** | Roadmap ordering contradiction resolved and one sequence adopted | **PASS** | Resolved via Owner Decision B2 (Candidate 2B) |

### Gate Summary:
- **PASS**: 8 gates (**G2, G3, G4, G8, G9, G10, G11, G12**)
- **BLOCKED**: 3 gates (**G1, G5, G6**)
- **NEEDS REVISION**: 1 gate (**G7**)

---

## 3. Evidence for Passed Gates

### Gate G2: Subsystem Dependency Graph Proven Acyclic
- **Status**: **PASS**
- **Evidence**:
  - [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §9 and [`docs/NIRMAL_1_STAGE_0_BLOCKER_RESOLUTION.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BLOCKER_RESOLUTION.md) §8 rigorously establish the acyclic, layered dependency hierarchy:
    ```
    Level 0: Governance Substrate & Policy Schema (depends on nothing)
    Level 1: Abstract Interface Contracts (Provider, MemoryStore, SkillManifest, SandboxDriver)
    Level 2: Skill Registry & Semantic Schema Validation
    Level 3: Durable Memory Backends & Append-Only Provenance Sink
    Level 4: Sandboxed Skill Execution Runtime
    Level 5: Pluggable Verification Engine & Critic Subsystem
    Level 6: Cognitive Controller & Deliberative Planning
    Level 7: Evaluation Batteries & Behavioral Regression Gates
    Level 8: Skill Acquisition Pipeline & Manual Promotion Gate
    Level 9: Multi-Provider Scaling & Controlled Tool Pilots
    ```
  - The provenance sink depends on zero cognitive subsystems and is append-only.
  - Owner approval of Candidate 2B formally solidifies this DAG as the authoritative engineering order.

### Gate G3: Provider Boundary Documented and Signed Off
- **Status**: **PASS**
- **Evidence**:
  - [`docs/NIRMAL_1_STAGE_0_OWNER_DECISION_RECORD.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_OWNER_DECISION_RECORD.md) records formal owner approval of **Candidate 1C** at `2026-09-20T01:42:25+05:30`.
  - The architectural boundary is formally defined: core orchestration (`CognitiveController`, `ContextManager`, `SkillExecutor`, `GovernanceEngine`) is strictly bound to the portable `Provider` interface (`generate`, `count_tokens`, `get_capabilities`, tool calling).
  - Neural introspection ([`src/nirmal/agent/neural_bridge.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/neural_bridge.py), DeltaNet recurrent states $S_t$) is isolated into the optional `LocalIntrospectionAdapter`.
  - Cognitive reasoning subsystems are mandated to provide deterministic heuristic/prompt fallbacks when running over standard black-box providers.

### Gate G4: Memory Boundaries and Write ACLs Documented and Accepted
- **Status**: **PASS**
- **Evidence**:
  - [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §4.2 establishes the comprehensive 6-tier memory specification table:
    1. *Working Memory*: Orchestrator-only writes, in-memory transient scratchpad, purged at task termination.
    2. *Episodic Memory*: Append-only writes at `LEARN` state; embeds verifier verdicts; rolling window with permanent archival.
    3. *Semantic Memory*: VerificationEngine-approved writes only (`WRITE_REJECTED_UNVERIFIED` for unverified writes); immutable version chains; no destructive overwrites.
    4. *Procedural/Skill Memory*: SkillRegistry lifecycle writes only; Git-tracked manifests; human gate for `trusted`; deprecate/quarantine transitions.
    5. *Task Memory*: Planner/Orchestrator session state; resolved skill refs; capped replanning attempts.
    6. *Provenance Memory*: All subsystems append-only; self-describing SHA-256 hash chains; permanent retention.

### Gate G8: Behavior Preservation Requirement Defined
- **Status**: **PASS**
- **Evidence**:
  - Codified in [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §6 and [`docs/NIRMAL_1_STAGE_0_BLOCKER_RESOLUTION.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BLOCKER_RESOLUTION.md) §9.
  - Stage 1 consists exclusively of new abstract type definitions and interface declarations in a dedicated namespace.
  - Zero modifications to existing files or test suites are permitted. All existing tests in `tests/` and behavioral evaluations in `evals/` must execute with 100% identical outcomes.

### Gate G9: Protected-Path Write Deny-List Encoded
- **Status**: **PASS**
- **Evidence**:
  - Protected scopes are formally codified in `experiments/v10_10/g0_protected_paths_baseline.json`:
    - `src/nirmal/`: 23 files, 246,321 bytes (SHA-256 verified 100% intact).
    - `data/shards/`: 18 files, 477,957 bytes (SHA-256 verified 100% intact).
  - V10.10 research artifacts are classified as an immutable research baseline.
  - Deny-list rules are codified in governance documents barring any write operations, deletes, or modifications to these directories.

### Gate G10: Rollback Requirements Defined
- **Status**: **PASS**
- **Evidence**:
  - Codified in [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §6.
  - Stage 1 introduces only new, additive interface files in a isolated directory (e.g. `nirmal/interfaces/` or `nirmal/core/`).
  - Rollback is completely deterministic: deleting the newly introduced interface directory reverts the repository to the exact pre-Stage-1 commit state without residual side effects.

### Gate G11: Test Plan Specified Per Interface
- **Status**: **PASS**
- **Evidence**:
  - [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §2 details explicit testability criteria and fail-closed test cases for all 8 interfaces:
    - `Provider`: Capability interrogation, token counting conservative bounds, structured call validation, typed timeout handling.
    - `SkillExecutor`: Sandboxed resource ceiling enforcement, timeout traps, token stripping verification.
    - `MemoryStore`: Unverified write rejection (`WRITE_REJECTED_UNVERIFIED`), contradiction version chaining, append-only provenance validation.
    - `GovernanceEngine`: Fail-closed default-deny evaluation, unauthorized self-promotion rejection, decision hash integrity.
    - `SandboxDriver`: Job object quota enforcement, process tree cleanup (`KillOnJobClose`), network socket deny-by-default.
    - `CognitiveController`: State transition validity, unverified action blocking, replan limit enforcement.
    - `ContextManager`: Token budget overflow prevention, sliding window preservation.
    - `VerificationEngine`: Deterministic predicate evaluation, semantic verification failure handling.

### Gate G12: Roadmap Ordering Contradiction Resolved
- **Status**: **PASS**
- **Evidence**:
  - [`docs/NIRMAL_1_STAGE_0_OWNER_DECISION_RECORD.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_OWNER_DECISION_RECORD.md) records formal owner approval of **Candidate 2B** at `2026-09-20T01:42:25+05:30`.
  - The conflicting linear sequencing from DRAFT §11 has been formally superseded by the dependency-ordered roadmap (Stages 0 $\to$ 1 $\to$ 1.5 $\to$ 2 $\to$ 3 $\to$ 4 $\to$ 5 $\to$ 6 $\to$ 7 $\to$ 8 $\to$ 9).

---

## 4. Exact Blockers for Non-PASS Gates

### Gate G1: All 8 Interface Contracts Frozen Without `UNRESOLVED` Markers
- **Current Status**: **BLOCKED**
- **Root Cause**: While candidate decisions B1, B3, B4, and B7 have been approved by the owner, the actual versioned interface specification document containing complete typed Python signatures (`typing.Protocol` / `abc.ABC`), method contracts, exception hierarchies, and data classes has not yet been authored and frozen on disk.
- **Evidence**: No interface specification file exists in `docs/` or `specs/`. No code exists in `src/nirmal/interfaces/`.
- **Unblocking Requirement**: Author an authoritative, versioned specification document (`docs/NIRMAL_1_STAGE_1_INTERFACE_SPECIFICATION.md`) defining all 8 interface contracts in full typed detail incorporating the approved B1, B3, B4, B7 decisions, with zero `UNRESOLVED` or `PROPOSED` markers.

### Gate G5: GovernanceEngine Contract Frozen with Fail-Closed Default-Deny
- **Current Status**: **BLOCKED**
- **Root Cause**: While Blocker B7 (Candidate 7B) was approved, the concrete programmatic interface contract for `GovernanceEngine` (including `evaluate_pre_execution`, `evaluate_post_execution`, `PolicyContext`, and the `Decision` record structure) has not yet been frozen into an authoritative specification document.
- **Evidence**: `NIRMAL_1_STAGE_0_BASELINE_REVIEW.md` §2.6 defines the high-level requirements, but notes "contract documented; fail-closed default-deny stated". This must be formally codified in the Stage 1 specification document.
- **Unblocking Requirement**: Include the frozen `GovernanceEngine` interface contract and typed `Decision` record schema in `docs/NIRMAL_1_STAGE_1_INTERFACE_SPECIFICATION.md`.

### Gate G6: SkillManifest Schema Frozen Incorporating B3, B4, B5
- **Current Status**: **BLOCKED**
- **Root Cause**: Owner decisions B3 (Candidate 3C: tiered rollback/compensation), B4 (Candidate 4B: native Windows Job Objects / restricted tokens), and B5 (Candidate 5B: 5-state trust lifecycle) have established the required schema fields. However, the machine-validatable JSON Schema and Python Pydantic/dataclass schema for `SkillManifest` have not yet been synthesized and frozen into an authoritative specification artifact.
- **Evidence**: `NIRMAL_1_STAGE_0_BASELINE_REVIEW.md` §3 explicitly states: *"Schema freeze is blocked until B3 (rollback) and B4 (sandbox) are decided."* Now that decisions are made, the schema itself must be formally written.
- **Unblocking Requirement**: Author and freeze the complete, machine-validatable `SkillManifest` JSON Schema and data model incorporating `side_effects`, `compensation_skill`, `idempotent`, `workspace_isolation`, `sandbox_policy`, and `trust_state`.

### Gate G7: Storage Boundary Decided
- **Current Status**: **NEEDS REVISION**
- **Root Cause**: `NIRMAL_1_STAGE_0_BASELINE_REVIEW.md` §5 records `D:\Nirmal-1-Store` (440.11 GB free) as the resolved storage root. However, the Project Owner has explicitly ruled that `D:\Nirmal-1-Store` / USB storage is **no longer part of the active Nirmal-1 workflow**, and operations are strictly confined to the desktop repository (`C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`). To prevent OneDrive sync lock contention, latency spikes, and file corruption during skill execution and memory persistence, a local off-OneDrive scratch and cache root (e.g. `%LOCALAPPDATA%\Nirmal-1\scratch` or a dedicated local directory on C:) must be formally designated in the baseline architecture documentation to supersede the obsolete external drive specification.
- **Evidence**: Discrepancy between `NIRMAL_1_STAGE_0_BASELINE_REVIEW.md` §5 (designating `D:\Nirmal-1-Store`) and the authoritative governance directive restricting operations strictly to the desktop repository.
- **Unblocking Requirement**: Update the architecture documentation to formally decommission `D:\Nirmal-1-Store` and define the canonical local staging/cache path outside OneDrive synchronization.

---

## 5. Required Revisions

To resolve all remaining blocked gates and transition Stage 1 to authorized status, the following four documentation and specification revisions are required:

1. **Revision 1 — Author Authoritative Stage 1 Interface Specification**:
   - Create `docs/NIRMAL_1_STAGE_1_INTERFACE_SPECIFICATION.md` freezing all 8 interface contracts (`Provider`, `SkillExecutor`, `MemoryStore`, `GovernanceEngine`, `SandboxDriver`, `CognitiveController`, `ContextManager`, `VerificationEngine`) with complete typed signatures, parameter descriptions, exception hierarchies, and fail-closed behaviors. (Resolves **G1** and **G5**).

2. **Revision 2 — Author Authoritative SkillManifest Schema**:
   - Create the frozen machine-validatable JSON Schema for `SkillManifest` incorporating all approved fields from B3 (tiered recovery), B4 (native Windows Job Object policies), and B5 (5-state trust lifecycle). (Resolves **G6**).

3. **Revision 3 — Reconcile Storage Boundary Specification**:
   - Update architecture baseline documentation to formally retire `D:\Nirmal-1-Store` and specify the canonical local staging root outside OneDrive sync for scratch workspaces, compiler caches, and memory database locks. (Resolves **G7**).

4. **Revision 4 — Consolidate and Certify Stage 0 Architecture Baseline**:
   - Update `docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md` and `docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md` to reflect the 7 approved owner decisions (replacing outdated linear roadmap, `neural_bridge.py` coupling, and `D:` storage references), enabling Stage 0 to be formally certified as `STAGE_0_APPROVED`.

---

## 6. Implementation Authorization Statement

In accordance with strict Nirmal-1 governance rules:
- Complexity never grants authorization.
- Software agents may not authorize themselves.
- A gate may not be bypassed while its criteria remain unfulfilled.
- The approval of design candidates (B1–B8) is a governance decision that prepares specifications; it does not constitute implementation authorization.
- Because gates **G1**, **G5**, and **G6** remain **BLOCKED**, and gate **G7** **NEEDS REVISION**:

```
====================================================================
AUTHORIZATION VERDICT:
STAGE_1_IMPLEMENTATION_UNAUTHORIZED
====================================================================
```

Zero implementation files may be created in `src/` or `nirmal/`. Zero existing code may be modified. Zero unit tests may be executed. Stage 1 implementation remains strictly unauthorized until the required specification documents are authored and all twelve acceptance gates are formally certified as **PASS**.
