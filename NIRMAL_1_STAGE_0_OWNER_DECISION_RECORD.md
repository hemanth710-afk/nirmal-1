# NIRMAL-1 — STAGE 0 OWNER DECISION RECORD
STATUS: GOVERNANCE DECISION — NO IMPLEMENTATION AUTHORIZATION

> **Date**: 2026-09-20  
> **Canonical Repository**: `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`  
> **Storage Policy**: `D:\Nirmal-1-Store` / USB storage is **no longer part of the active Nirmal-1 workflow**. All canonical operations are restricted exclusively to the desktop repository. Zero files on external storage were accessed or modified.  
>
> ### Mandatory Governance Baselines
> - **Stage 0 Status**: `STAGE_0_REQUIRES_REVISIONS` (Owner decisions recorded; baseline document alignment and gate verification pending)
> - **Stage 1 Status**: `STAGE_1_IMPLEMENTATION_UNAUTHORIZED`
> - **Phase C Status**: `NOT AUTHORIZED` (`PHASE_C_PREPARATION_BLOCKED`)
> - **Harness Recovery**: `HARNESS_RECOVERY_BLOCKED`
> - **Production Status**: `STRICT NO-GO`
> - **Protected Paths**: `src/nirmal/` (23 files, 246,321 bytes) and `data/shards/` (18 files, 477,957 bytes) are **strictly immutable and unmodified**.
> - **V10.10 Artifacts**: Unmodified research subsystem.
> - **Document Purpose**: Formal governance record of human Project Owner decisions on Stage 0 architectural blockers. All decisions recorded herein were explicitly authorized by the human Project Owner. This document authorizes no implementation, no code changes, no unit tests, and no model training.

---

## Executive Summary

Following the comprehensive Stage 0 blocker analysis in [`docs/NIRMAL_1_STAGE_0_BLOCKER_RESOLUTION.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BLOCKER_RESOLUTION.md), the human Project Owner has formally reviewed and resolved all seven architectural blockers (**B1, B2, B3, B4, B5, B7, B8**).

This document records the exact owner decisions, alongside the preserved technical rationales, architectural consequences, cross-subsystem dependencies, and unresolved risks.

**Authoritative Governance State**:
```
STAGE_0_REQUIRES_REVISIONS
STAGE_1_IMPLEMENTATION_UNAUTHORIZED
PHASE_C_PREPARATION_BLOCKED
HARNESS_RECOVERY_BLOCKED
PRODUCTION: STRICT NO-GO
```

---

## Blocker B1 — Provider / Introspection Boundary

### Proposed Candidate
**Candidate 1C**: Core Portable `Provider` Interface + Optional `LocalIntrospectionAdapter`.

### Technical Rationale
- Decouples core cognitive orchestration (`CognitiveController`, `ContextManager`, `SkillExecutor`, `GovernanceEngine`) from concrete PyTorch neural implementations, enabling Nirmal-1 to operate over standard external model providers (e.g. OpenAI, Anthropic, Google Vertex, self-hosted API endpoints) which do not expose internal activations or token perplexity distributions.
- Retains local neural research capability without sacrificing portability by isolating activation extraction, span perplexity scoring, and internal state inspection ([`src/nirmal/agent/neural_bridge.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/neural_bridge.py), DeltaNet recurrent state matrices $S_t$) behind an optional adapter queried via `provider.has_capability('introspection')`.
- Enforces deterministic prompt/heuristic fallbacks when running against black-box providers.

### Consequences
- Core orchestration loops are strictly portable and model-agnostic.
- Remote frontier models can be utilized without architectural impedance or runtime crashes.
- Local neural research pathways remain fully accessible for white-box models without polluting the core engine.
- Developers of advanced reasoning modules must implement and test dual execution paths (neural pathway vs. heuristic/prompt fallback).

### Dependencies
- Directly governs the interface specifications of `Provider` and `ContextManager` in Stage 1.
- Prerequisite for `ReasoningEngine` and `WorldModel` design.

### Unresolved Risk
- Potential cognitive fidelity degradation on black-box providers if heuristic/prompt fallbacks do not fully replicate the semantic sensitivity of direct activation/perplexity inspection.
- Maintenance overhead of supporting dual-path reasoning logic across future cognitive modules.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 1C** — split the model layer into a mandatory portable `Provider` interface and an optional `LocalIntrospectionAdapter`, prohibiting core orchestration from importing or requiring neural introspection, while mandating heuristic/prompt fallbacks when introspection is unavailable.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 1C**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 1C** (Core Portable `Provider` Interface + Optional `LocalIntrospectionAdapter`)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## Blocker B2 — Authoritative Roadmap Dependency Ordering

### Proposed Candidate
**Candidate 2B**: Authoritative Dependency-Ordered Sequencing (Stages 0 $\to$ 1 $\to$ 1.5 $\to$ 2 $\to$ 3 $\to$ 4 $\to$ 5 $\to$ 6 $\to$ 7 $\to$ 8 $\to$ 9).

### Technical Rationale
- Resolves critical circular dependencies and integration deadlocks identified between DRAFT §11 and REVIEW §9:
  1. Governance must exist early (Stage 1.5) to intercept and gate side effects, rather than being appended late.
  2. Memory persistence must be durable (Stage 3) before sandboxed execution (Stage 4) to record execution traces, episodic events, and provenance.
  3. Verification (Stage 5) must be operational *before* Cognitive Controller integration (Stage 6), because the 11-state controller loop (`ACT` $\to$ `VERIFY` $\to$ `UPDATE` $\to$ `LEARN`) cannot complete a step without a deterministic verifier.
- Establishes a rigorous 10-stage execution pipeline:
  - **Stage 0**: Architecture Baseline & Storage Approval
  - **Stage 1**: Abstract Interface Contracts (`SkillManifest`, `Provider`, `MemoryStore`, `GovernanceEngine`)
  - **Stage 1.5**: Fail-Closed Governance & Permission Substrate (Default-deny interceptor, decision logging)
  - **Stage 2**: Declarative Skill Registry & Manifest Validation (Schema validation, semver resolution, cycle rejection)
  - **Stage 3**: Durable Local Memory Backends (Episodic JSONL, semantic KV store, provenance chain)
  - **Stage 4**: Sandboxed Skill Execution Runtime (Job object limits, token stripping, timeout traps)
  - **Stage 5**: Pluggable Verification & Critic Subsystem (Structural, predicate, and test-suite verifiers)
  - **Stage 6**: Cognitive Controller & Planner Integration (Dispatching via Skill Registry and Verification Engine)
  - **Stage 7**: Per-Skill Evaluation Batteries & Regression Gates (AST anti-hardcoding, permutation checks)
  - **Stage 8**: Governed Skill Acquisition Pipeline (Trajectory-to-proposal induction; manual promotion only)
  - **Stage 9**: Controlled Multi-Provider & Real Tool Pilots (Subject to explicit human executive authorization)

### Consequences
- Eliminates integration deadlocks and prevents unverified actions from executing.
- Enforces strict exit criteria and acceptance gates between stages; no stage can begin until prerequisite gates pass.
- Controller integration is deferred until verification and sandboxing infrastructure are fully validated.

### Dependencies
- Establishes the structural master schedule for all engineering stages (Stages 0–9).
- Determines the implementation and integration order of every other subsystem.

### Unresolved Risk
- Stage 1.5 introduces an intermediate milestone before skill execution, requiring governance primitives to be fully specified and tested early.
- Comprehensive verification engine in Stage 5 may require extensive domain predicate libraries before controller testing can begin.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 2B** — adopt the dependency-ordered roadmap sequence (0 $\to$ 1 $\to$ 1.5 $\to$ 2 $\to$ 3 $\to$ 4 $\to$ 5 $\to$ 6 $\to$ 7 $\to$ 8 $\to$ 9) as the single authoritative engineering schedule for Nirmal-1.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 2B**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 2B** (Authoritative Dependency-Ordered Sequencing)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## Blocker B3 — Composite-Skill Rollback / Compensation

### Proposed Candidate
**Candidate 3C**: Tiered Hybrid Rollback and Compensation Model.

### Technical Rationale
- Composite skills execute multi-step directed acyclic graphs (DAGs) of sub-actions. If an intermediate step fails after previous steps have altered the environment, state corruption and cascading failures occur unless deterministic recovery mechanisms exist.
- Pure ACID transactions are impossible for external services, while universal Saga compensation is excessive overhead for pure computational skills.
- A tiered approach aligns recovery complexity with side-effect risk:
  1. *Pure Computational (`side_effects: "none"`)*: Rollback is a no-op; execution terminates cleanly with typed failure.
  2. *Workspace Scoped (`side_effects: "workspace"`)*: Executed in an isolated session workspace directory (`artifacts/<task_id>/`); upon step failure, the unverified staging directory is quarantined/purged; no changes are promoted to persistent task storage.
  3. *External Environmental (`side_effects: "external"`)*: The manifest MUST declare either:
     - `idempotent: true` (safe to retry or abandon), OR
     - `compensation_skill: "<skill_id@version>"` (executed in reverse topological order upon failure).
     - External skills lacking both are classified as `irreversible_risk` and require interactive human confirmation prior to dispatch.

### Consequences
- Guarantees environment cleanliness on task failure without requiring heavy filesystem snapshots for read-only operations.
- Enforces explicit safety contracts in `SkillManifest` for external side-effecting operations.
- Requires authoring compensating skills or designing idempotent interfaces for all external side effects.

### Dependencies
- Directly dictates schema fields in `SkillManifest` (`compensation_skill`, `idempotent`, `workspace_isolation`).
- Governs `SkillExecutor` rollback loop and `Provenance` trace logging.

### Unresolved Risk
- Flawed compensation logic in custom compensation skills could itself fail or generate secondary uncompensated side effects.
- Ephemeral workspace isolation requires disk space management and strict session directory pruning.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 3C** — mandate tiered recovery (no-op for pure computation, staging directory discard for workspace mutations, and declared idempotency or reverse-topological compensation for external side effects) in the `SkillManifest` schema and execution runtime.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 3C**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 3C** (Tiered Hybrid Rollback and Compensation Model)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## Blocker B4 — Windows Sandbox Mechanism

### Proposed Candidate
**Candidate 4B**: Tiered Native Windows Process Isolation (Windows Job Objects + Restricted Tokens + Scoped Temp Directories for Stages 1–8; Docker Containers for Stage 9).

### Technical Rationale
- Nirmal-1 runs on Windows 11 without POSIX namespaces. Running unverified or synthesized Python skills without process sandboxing risks arbitrary code execution, filesystem corruption, and security breaches.
- Windows AppContainers severely break the standard Python runtime, C-extensions, and pip environments. Full OCI/Docker containerization introduces significant daemon overhead (>500ms spin-up latency), operational complexity, and external daemon dependency failures during early cognitive development.
- Native Windows Job Objects paired with Win32 Restricted Tokens provide:
  1. Sub-10ms process invocation overhead directly in Python via `ctypes`/Win32 APIs.
  2. Hard resource quotas (`JobMemoryLimit`, CPU rate caps) and guaranteed process-tree termination on timeout (`KillOnJobClose`).
  3. Restricted access tokens that strip write permissions from protected trees ([`src/nirmal/`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal), [`data/shards/`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/data/shards)) and system paths, confining writable access strictly to an ephemeral session directory (`scratch/<run_id>/`).
  4. Default-deny network socket restrictions unless explicitly granted by Governance.
  5. Full OCI/Docker container isolation is deferred to Stage 9 for real-world computer control and untrusted code execution pilots.

### Consequences
- High-performance, native Windows sandboxing without external daemon dependencies for Stages 1–8.
- Protected paths (`src/nirmal/`, `data/shards/`) are physically write-protected at the OS process token level during skill execution.
- Establishes a clean interface boundary (`SandboxDriver`) for containerized isolation in Stage 9 without imposing container overhead on unit and skill benchmarks.

### Dependencies
- Governs `SandboxDriver` interface in Stage 1 and execution runtime in Stage 4.
- Enforces workspace isolation boundaries required by Blocker B3.

### Unresolved Risk
- Complex Win32 API interactions via `ctypes` must be rigorously tested across Windows versions and user privilege levels.
- Win32 restricted tokens require precise privilege stripping to prevent handle inheritance across child processes.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 4B** — adopt native Windows Job Objects, Restricted Access Tokens, and scoped scratch directories as the standard isolation sandbox for Stages 1–8, reserving OCI/Docker containerization strictly for Stage 9 pilots.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 4B**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 4B** (Tiered Native Windows Process Isolation via Job Objects & Restricted Tokens)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## Blocker B5 — Skill Trust Demotion & Revocation

### Proposed Candidate
**Candidate 5B**: Complete 5-State Trust Lifecycle (`proposed`, `evaluated`, `trusted`, `quarantined`, `deprecated`) with Automated Circuit Breakers and Human Authority.

### Technical Rationale
- DRAFT §4 defines unidirectional promotion (`proposed` $\to$ `evaluated` $\to$ `trusted`) with no demotion, revocation, or quarantine mechanisms. A degraded, vulnerable, or buggy skill would remain trusted indefinitely, poisoning the catalog and cognitive planning.
- Deleting bad skills destroys provenance and historical reproducibility, and crashes active tasks pinned to that skill.
- A 5-state finite state machine resolves this:
  1. **States**: `proposed`, `evaluated`, `trusted`, `quarantined`, `deprecated`.
  2. **Transitions & Authority**:
     - `proposed` $\to$ `evaluated`: Automated via passing the evaluation battery (Stage 7).
     - `evaluated` $\to$ `trusted`: Solely via Human Project Owner authorization.
     - Any state $\to$ `quarantined`: Automated circuit-breaker (rolling 10-execution failure rate $\ge 30\%$, security/sandbox violation $> 0$, or manifest hash mismatch) OR manual Human Owner command.
     - `quarantined` $\to$ `deprecated`: Solely via Human Owner command.
     - `quarantined` $\to$ `evaluated`: Solely via Human Owner command (after verified patch).
  3. **Runtime Semantics**:
     - If a skill enters `quarantined`, active executions immediately abort with typed exception `SKILL_QUARANTINED` and trigger replanning.
     - If a skill enters `deprecated`, active pinned tasks finish, but the skill is excluded from `SkillRegistry.search()` and planner dispatch for all new tasks.

### Consequences
- Preserves immutable provenance and historical auditability (skills are never deleted in-place).
- Protects cognitive planner from invoking failing or compromised skills via automated circuit-breaking.
- Retains human-in-the-loop control for promotion, un-quarantine, and deprecation.

### Dependencies
- Dictates `trust_state` field in `SkillManifest` (Stage 1) and state transition logic in `SkillRegistry` (Stage 2).
- Integrates with `GovernanceEngine` (Stage 1.5) and `CognitiveController` replanning (Stage 6).

### Unresolved Risk
- Flaky or environment-dependent skills might trigger premature quarantine if empirical failure threshold (30%) is too sensitive.
- Active task abort upon quarantine requires robust planner exception handling and replanning logic.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 5B** — establish the 5-state lifecycle (`proposed`, `evaluated`, `trusted`, `quarantined`, `deprecated`) with automated circuit breaking on rolling failure rates $\ge 30\%$ and human owner promotion/deprecation authority.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 5B**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 5B** (Complete 5-State Trust Lifecycle with Quarantine Circuit Breakers)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## Blocker B7 — Governance Policy Representation & Approval Authority

### Proposed Candidate
**Candidate 7B**: Declarative YAML Data conforming to strict JSON Schema + Designated Human Project Owner Authority (Fail-Closed Default-Deny).

### Technical Rationale
- DRAFT §12.5 leaves policy representation (YAML vs. Python) and approval authority ambiguous.
- Implementing governance policies as arbitrary executable Python scripts introduces execution vulnerabilities, code injection vectors, non-deterministic side effects, and circular dependencies during policy evaluation.
- An ambiguous approval authority creates the catastrophic risk of autonomous self-authorization or automated privilege escalation by LLM agents.
- Candidate 7B enforces:
  1. Governance policies are strictly declarative YAML files stored in `governance/policies/` and validated against a rigid JSON Schema at engine startup.
  2. Policy evaluation is purely deterministic with an unconditional fail-closed default-deny rule.
  3. Human Project Owner is the sole authorized actor for policy changes, production deployment, and `evaluated → trusted` promotions.
  4. Software agents, models, and background processes are strictly barred from modifying policy files, approving promotions, or bypassing denials.
  5. Every policy evaluation emits an immutable `Decision` record (decision ID, rule reference, policy hash, timestamp, actor, result) appended to the audit log.

### Consequences
- "Governance is data, not code": Policies are fully transparent, Git-diffable, schema-validated, and tamper-evident.
- Eliminates autonomous self-promotion and agent privilege escalation by architectural design.
- Imposes fail-closed safety across all system interfaces from Stage 1.5 onward.

### Dependencies
- Foundation for `GovernanceEngine` interface (Stage 1) and runtime substrate (Stage 1.5).
- Gates skill execution (Stage 4), memory writes (Stage 3), and acquisition promotion (Stage 8).

### Unresolved Risk
- High volume of human approvals required for promotions or sensitive grants if policy granularity is excessively fine.
- Schema must be sufficiently expressive to represent complex multi-condition access control rules without resorting to arbitrary scripting.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 7B** — mandate declarative YAML policies validated by JSON Schema with fail-closed default-deny, and designate the human Project Owner as the sole authority for policy amendments and promotions.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 7B**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 7B** (Declarative YAML Policies + Human Project Owner Authority)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## Blocker B8 — Skill Composition Architecture & Legacy Compatibility

### Proposed Candidate
**Candidate 8A**: Clean Subsystem Replacement in `nirmal.skills.composition` (preserving `src/nirmal/agent/memory/procedural.py` 100% untouched).

### Technical Rationale
- DRAFT §3.7 claims skill composition "evolves `procedural.compose_strategies()`", but [`src/nirmal/agent/memory/procedural.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/memory/procedural.py) lines 360–448 is hardcoded to synthetic toy tasks ('X', 'Y', 'Z') and mock tools. Modifying it directly violates the protected path constraint for `src/nirmal/`.
- Attempting to evolve or wrap the legacy method perpetuates technical debt and binds modern skill composition to toy mock abstractions.
- Candidate 8A provides:
  1. Clean subsystem replacement: Generic, DAG-based skill composition will be designed from scratch in a new, modular package (`nirmal.skills.composition`) during Stages 2 and 3.
  2. Complete immutability of protected paths: [`src/nirmal/agent/memory/procedural.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/memory/procedural.py) remains 100% untouched and preserved.
  3. Backwards compatibility: A lightweight adapter (`LegacyStrategyAdapter`) will be introduced in Stage 6 during controller integration to map legacy procedural strategies to modern skill manifests, guaranteeing zero regression in existing behavioral evaluation suites (`evals/`).

### Consequences
- Zero modifications to protected code in `src/nirmal/`.
- Clean, uncompromised architecture for modern composite skills with typed IO ports, topological sorting, and cycle detection.
- Legacy behavioral evaluations continue to run without breakage.

### Dependencies
- Governs `SkillManifest` composite schema (Stage 1), `SkillRegistry` graph resolution (Stage 2), and `SkillExecutor` DAG dispatcher (Stage 4).
- Implemented in Stages 2/3 and integrated with the controller in Stage 6.

### Unresolved Risk
- Developing a comprehensive DAG execution engine with parallel branch scheduling requires thorough verification and unit testing.
- Legacy adapter in Stage 6 must accurately translate legacy procedural memory representations.

### Exact Approval Decision Required
- **Decision**: Approve or Revise **Candidate 8A** — implement generic skill composition as a clean new subsystem in `nirmal.skills.composition`, keeping `src/nirmal/agent/memory/procedural.py` strictly unmodified, and introducing a legacy adapter in Stage 6.

### Recorded Owner Decision
- **Owner Decision**: **APPROVED 8A**
- **Status**: **APPROVED**
- **Selected Candidate**: **Candidate 8A** (Clean Subsystem Replacement in `nirmal.skills.composition`)
- **Decision Timestamp**: 2026-09-20T01:42:25+05:30
- **Authority**: Human Project Owner

---

## OWNER DECISIONS RECORDED

The human Project Owner has formally reviewed and explicitly approved all seven Stage 0 candidate proposals:

| Blocker ID | Description | Approved Candidate | Decision Status | Decision Timestamp | Authority |
|---|---|---|---|---|---|
| **B1** | Provider / Introspection Boundary | **Candidate 1C** (Core Portable `Provider` + Optional `LocalIntrospectionAdapter`) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B2** | Authoritative Roadmap Sequence | **Candidate 2B** (Authoritative Dependency-Ordered Sequencing 0 $\to$ 1 $\to$ 1.5 $\to$ ... $\to$ 9) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B3** | Rollback & Compensation Model | **Candidate 3C** (Tiered Hybrid Rollback/Compensation Model) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B4** | Windows Sandbox Mechanism | **Candidate 4B** (Tiered Native Windows Isolation via Job Objects & Restricted Tokens) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B5** | Skill Trust Demotion & Revocation | **Candidate 5B** (Complete 5-State Trust Lifecycle with Quarantine Circuit Breakers) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B7** | Governance Policy & Authority | **Candidate 7B** (Declarative YAML Policies + Human Project Owner Authority) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |
| **B8** | Skill Composition Architecture | **Candidate 8A** (Clean Subsystem Replacement in `nirmal.skills.composition`) | **APPROVED** | 2026-09-20T01:42:25+05:30 | Human Project Owner |

All seven owner decisions are formally recorded. No decisions were inferred or marked without explicit owner authorization.

---

### Current Governance Status

```
STAGE_0_REQUIRES_REVISIONS
STAGE_1_IMPLEMENTATION_UNAUTHORIZED
PHASE_C_PREPARATION_BLOCKED
HARNESS_RECOVERY_BLOCKED
PRODUCTION: STRICT NO-GO
```
