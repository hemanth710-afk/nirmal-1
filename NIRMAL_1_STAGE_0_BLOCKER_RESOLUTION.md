# NIRMAL-1 — STAGE 0 BLOCKER RESOLUTION
STATUS: DECISION PREPARATION — NO IMPLEMENTATION AUTHORIZATION

> **Date**: 2026-09-20  
> **Canonical Repository**: `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`  
> **Storage Policy Note**: `D:\Nirmal-1-Store` / USB storage is **no longer part of the active Nirmal-1 workflow**. The canonical desktop repository is the sole environment. Zero files were accessed or modified on external storage.  
>
> ### Mandatory Governance State
> - **Stage 0 Status**: `STAGE_0_REQUIRES_REVISIONS`
> - **Stage 1 Status**: `STAGE_1_IMPLEMENTATION_UNAUTHORIZED`
> - **Production**: `STRICT NO-GO`
> - **Phase C**: `NOT AUTHORIZED` (`PHASE_C_PREPARATION_BLOCKED`)
> - **Harness Recovery**: `HARNESS_RECOVERY_BLOCKED`
> - **Protected Paths**: `src/nirmal/` (23 files, 246,321 bytes) and `data/shards/` (18 files, 477,957 bytes) are **strictly immutable and unmodified**.
> - **V10.10 Artifacts**: Unmodified research subsystem.
> - **Document Purpose**: Decision preparation only. Authorizes no implementation, no code changes, no tests, and no training.

---

## Executive Summary

Following the Stage 0 baseline review ([`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md)), the project status was classified as `STAGE_0_REQUIRES_REVISIONS`. While storage boundary concerns have been isolated to the local repository context, seven architectural blockers (**B1, B2, B3, B4, B5, B7, B8**) must be resolved by the human Project Owner before Stage 1 interface contracts and the manifest schema can be formally frozen.

This report prepares the comprehensive decision record for each blocker, providing:
1. Exact issue description
2. Direct repository and documentary evidence
3. Architectural impact
4. Candidate decisions
5. Cross-blocker dependency implications
6. Required owner decision
7. Proposed definitive wording for the architecture baseline

---

## 1. Blocker B1 — Provider / Introspection Boundary

### 1.1 Current Issue
The architecture draft aims to establish model-agnosticism by decoupling the cognitive orchestrator from concrete model implementations via an abstract `Provider` interface. However, Section 6 of the draft designates [`src/nirmal/agent/neural_bridge.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/neural_bridge.py) as the "reference implementation of the Reasoning Interface for the local Nirmal core". In reality, `NeuralBridge` directly accesses intermediate layer hidden states, attention maps, DeltaNet recurrent state matrices ($S_t$), and token-level log-probabilities across arbitrary prompt spans. Standard external model providers (e.g. OpenAI, Anthropic, Google Vertex, or black-box API endpoints) do not expose internal activations or logit distributions. If core cognitive subsystems require introspection, the system cannot run over external providers, creating latent coupling to `NirmalForCausalLM`.

### 1.2 Evidence
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md) §6, lines 398–399:  
  *"`neural_bridge.py` becomes the reference implementation of the Reasoning Interface for the local Nirmal core — behind the interface, not imported directly."*
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §5.2:  
  *Identifies that `NeuralBridge` depends on internal residual streams and token perplexity unavailable in remote model APIs.*
- [`src/nirmal/agent/neural_bridge.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/neural_bridge.py) lines 1–12:  
  *Defines 7 neural pathways explicitly coupled to `NirmalForCausalLM` tensor internals (perception dense embedding, memory dense retrieval, state transition prediction, perplexity scoring, viability scoring, semantic verification scoring, credit learning).*

### 1.3 Architectural Impact
If core cognitive loops depend on hidden-state introspection, Nirmal-1 remains tightly coupled to `NirmalForCausalLM` (or local PyTorch models), making multi-provider support impossible and preventing deployment over remote frontier models.

### 1.4 Candidate Decisions
- **Candidate 1A (Universal Lowest Common Denominator)**: Eliminate all hidden-state introspection. Force all cognition to operate exclusively through text generation and coarse API-level embeddings.  
  *Limitation*: Destroys the research value of local white-box neural models and discards the V5 neural pathways.
- **Candidate 1B (Mandatory White-Box Introspection)**: Require all providers to expose PyTorch activations.  
  *Limitation*: Permanently prevents Nirmal-1 from using external frontier models or API providers.
- **Candidate 1C (Core Portable Provider + Optional LocalIntrospectionAdapter — RECOMMENDED)**: Formally split the provider contract into:
  1. `Provider` (Portable Core): Text/token generation, token counting/conservative upper-bound estimation, declared capability metadata, and structured tool-calling.
  2. `LocalIntrospectionAdapter` (Optional Capability Extension): Activation extraction, span perplexity scoring, and internal state inspection.
  *Subsystem Dependency Rules*:
  - Core orchestration (`CognitiveController`, `ContextManager`, `SkillExecutor`, `GovernanceEngine`) **must depend exclusively on the portable `Provider`**.
  - Advanced reasoning (`ReasoningEngine`, `WorldModel`) may query `provider.has_capability('introspection')` to use neural pathways when available, but **must provide deterministic heuristic/prompt fallbacks** when operating over black-box providers.

### 1.5 Dependency Implications
B1 directly governs the interface definitions of `Provider` and `ContextManager` in Stage 1. It must be resolved before Stage 1 contracts can freeze.

### 1.6 Required Owner Decision
Approve **Candidate 1C**: Split the provider boundary into a portable core `Provider` contract and an optional `LocalIntrospectionAdapter`, prohibiting core execution subsystems from requiring introspection.

### 1.7 Proposed Specification Wording
> *"The Model/Provider Layer defines two distinct contracts: (1) the portable `Provider` interface (implementing text/token generation, token counting/estimation, structured tool calling, and declared capability metadata) required for all backends, and (2) an optional `LocalIntrospectionAdapter` (implementing hidden-state extraction, token-level perplexity across spans, and recurrent state inspection) available only for white-box local neural weights. Core cognitive orchestration (`CognitiveController`, `ContextManager`, `SkillExecutor`, `GovernanceEngine`) MUST NOT import or require `LocalIntrospectionAdapter`. Cognitive reasoning and world modeling MAY query `provider.has_capability('introspection')` and utilize introspection pathways when available, but MUST provide deterministic prompt/heuristic fallbacks when running over standard black-box providers."*

---

## 2. Blocker B2 — Authoritative Roadmap Dependency Ordering

### 2.1 Current Issue
A structural contradiction exists between the linear stage progression in DRAFT §11 and the dependency-ordered progression in REVIEW §9:
1. DRAFT §11 places Governance implementation late without an explicit stage, whereas governance must gate side effects from the beginning.
2. DRAFT §11 places Verification (Stage 6) *after* Controller Integration (Stage 5), creating a deadlock because the 11-state `CognitiveController` cannot verify actions or update memory without a functional verifier.
3. DRAFT §11 places Memory persistence at Stage 4 (after Skill Execution at Stage 3), even though skill execution requires episodic and provenance logging.

### 2.2 Evidence
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md) §11:  
  *Stage sequence: 0 (Architecture) $\to$ 1 (Interfaces) $\to$ 2 (Registry) $\to$ 3 (Execution) $\to$ 4 (Memory) $\to$ 5 (Planning/Reasoning Integration) $\to$ 6 (Verification) $\to$ 7 (Acquisition) $\to$ 8 (Evaluation) $\to$ 9 (Scaling).*
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §9:  
  *Flowchart requires Stage 1.5 Governance Substrate first, durable Memory early, and Verification prior to Controller Integration.*
- [`src/nirmal/agent/controller.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/controller.py) lines 33–45:  
  *State machine requires `ACT` $\to$ `VERIFY` $\to$ `UPDATE` $\to$ `LEARN`. The controller cannot complete a step without `DeterministicVerifier`.*

### 2.3 Architectural Impact
A linear progression attempts to execute unverified actions in Stage 5 before verification exists, and attempts skill execution before a fail-closed governance interceptor or durable provenance sink is operational.

### 2.4 Candidate Decisions
- **Candidate 2A (DRAFT Linear Sequencing)**: Retain Stages 0–9 as written in DRAFT §11.  
  *Limitation*: Violates architectural invariants; attempts to integrate the cognitive loop before verification and provenance logging exist.
- **Candidate 2B (Authoritative Dependency-Ordered Sequencing — RECOMMENDED)**:
  Formally adopt the dependency-correct sequence:
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

### 2.5 Dependency Implications
B2 establishes the master execution prerequisite chain for the entire project. All subsequent blocker resolutions fit into this ordering.

### 2.6 Required Owner Decision
Approve **Candidate 2B** as the single authoritative roadmap sequence for Nirmal-1.

### 2.7 Proposed Specification Wording
> *"The authoritative implementation roadmap strictly follows the dependency-ordered sequence: Stage 0 (Architecture Baseline & Storage Approval) $\to$ Stage 1 (Interface Contracts) $\to$ Stage 1.5 (Fail-Closed Governance Substrate) $\to$ Stage 2 (Skill Registry & Manifest Validation) $\to$ Stage 3 (Durable Memory Backends) $\to$ Stage 4 (Sandboxed Skill Executor) $\to$ Stage 5 (Pluggable Verification & Critic Engine) $\to$ Stage 6 (Cognitive Controller & Planner Integration) $\to$ Stage 7 (Evaluation Batteries & Regression Gates) $\to$ Stage 8 (Skill Acquisition & Manual Promotion Workflow) $\to$ Stage 9 (Controlled Scaling & Tool Expansion). No stage may begin execution until the exit criteria and acceptance gates of all prerequisite stages have formally passed."*

---

## 3. Blocker B3 — Composite-Skill Rollback / Compensation

### 3.1 Current Issue
Composite skills execute DAGs of sub-actions. If Step 3 of a 5-step composite fails after Step 2 has altered environment state, how is state restored? The draft defines `side_effects` but provides zero recovery semantics.

### 3.2 Evidence
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md) §4.1 line 319:  
  *Declares `side_effects: "none" | "workspace" | "external"` without specifying failure recovery semantics.*
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §3.1 item 2:  
  *Flags total absence of rollback/compensation semantics for intermediate composite step failures.*

### 3.3 Architectural Impact
Without rollback/compensation, intermediate failures leave environments in corrupted, unrecoverable states, causing cascading task failures and poisoning episodic memory.

### 3.4 Candidate Decisions
- **Candidate 3A (Pure Transactional Rollback)**: Require all operations to be fully ACID transactional.  
  *Limitation*: External environments, mock services, and API endpoints cannot support filesystem-level transactions.
- **Candidate 3B (Pure Saga Compensation)**: Require every skill to implement a compensating reverse action.  
  *Limitation*: High authoring overhead for read-only or pure computational skills.
- **Candidate 3C (Tiered Hybrid Architecture — RECOMMENDED)**:
  1. *Pure Computational (`side_effects: "none"`)*: Rollback is a no-op; execution terminates cleanly with typed failure.
  2. *Workspace Scoped (`side_effects: "workspace"`)*: Executed in an isolated session workspace directory (`artifacts/<task_id>/`). If any step fails, the staging directory is quarantined/purged; no changes are promoted to persistent task storage.
  3. *External Environmental (`side_effects: "external"`)*: The manifest MUST declare either:
     - `idempotent: true` (safe to retry or abandon), OR
     - `compensation_skill: "<skill_id@version>"` (executed in reverse topological order upon failure).
     - External skills lacking both are classified as `irreversible_risk` and require interactive human confirmation prior to dispatch.

### 3.5 Dependency Implications
Directly dictates schema fields in `SkillManifest` (`compensation_skill`, `idempotent`, `workspace_isolation`), execution logic in `SkillExecutor`, permission rules in `GovernanceEngine`, and trace logging in `Provenance`.

### 3.6 Required Owner Decision
Approve **Candidate 3C** and mandate `compensation_skill` and `workspace_isolation` in the `SkillManifest` schema.

### 3.7 Proposed Specification Wording
> *"Side-effecting skill execution enforces a tiered rollback and compensation architecture. Skills declaring `side_effects: 'none'` require no rollback. Skills declaring `side_effects: 'workspace'` execute inside a dedicated, isolated workspace sandbox under `artifacts/<task_id>/`; upon failure, all unverified staging modifications are discarded prior to committing to task memory. Skills declaring `side_effects: 'external'` MUST define either an idempotent invocation contract (`idempotent: true`) or an explicit compensation skill (`compensation_skill: '<id@ver>'`) executed in reverse topological order upon failure. External side-effecting skills lacking automated compensation are classified as high-risk and require explicit interactive human approval per invocation."*

---

## 4. Blocker B4 — Windows Sandbox Mechanism

### 4.1 Current Issue
`sandbox: "restricted"` in the draft is undefined. Windows OS does not possess POSIX namespaces or native cgroups. Running unverified, learned, or user-contributed Python skills without real sandboxing risks arbitrary code execution, filesystem corruption, and data leakage.

### 4.2 Evidence
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md) §4.1 line 318 (`sandbox: "restricted"`).
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §3.1 item 3:  
  *Points out that Windows process isolation is undefined and non-trivial.*

### 4.3 Evaluation of Mechanisms

| Evaluation Dimension | 1. Windows AppContainer | 2. Windows Job Objects + Restricted Token (RECOMMENDED) | 3. OCI / Docker Containers |
|---|---|---|---|
| **Process Isolation** | High (UWP sandbox) | Strong (OS-level job boundary + token stripping) | Full virtualization / Linux namespace |
| **Filesystem Access** | Severely restricted (breaks Python stdlib & C-extensions) | Fine-grained path allowlisting; read-only repo, scoped temp | Isolated container filesystem with volume mounts |
| **Network Control** | Default blocked | Default-deny socket creation | Virtual network bridge control |
| **Resource Limits** | Difficult to configure dynamically | Hard native ceilings (`JobMemoryLimit`, CPU rate caps) | Docker runtime resource flags (`--memory`, `--cpus`) |
| **Process Cleanup** | Automatic on container teardown | `KillOnJobClose` guarantees full tree termination | Automatic on container removal |
| **Auditability** | Windows Event Log | Windows Event Log + process exit codes in provenance | Docker daemon logs |
| **Windows Compatibility**| Windows 10/11 native | Windows 10/11 native (no external dependencies) | Requires Docker Desktop / WSL2 active |
| **Operational Complexity**| Very High (breaks pip environments) | **Low (Sub-10ms overhead, pure Python `ctypes`/Win32)** | High (daemon latency, container spin-up overhead) |

### 4.4 Candidate Decisions
- **Candidate 4A (Defer Sandboxing)**: Defer sandboxing to Stage 9. (Leaves Stages 1–8 unprotected).
- **Candidate 4B (Mandatory Docker/WSL2)**: Require Docker Desktop for all skills. (Heavyweight, high latency, operational failure if daemon down).
- **Candidate 4C (Native Windows Job Objects + Restricted Token + Scoped Temp Directories — RECOMMENDED)**: Use native Windows Job Objects with Restricted Tokens for Stages 1–8. Reserve full OCI/Docker containerization strictly for Stage 9 real computer control pilots.

### 4.5 Dependency Implications
Must be decided to freeze the `sandbox_policy` field in `SkillManifest` and implement process supervision in `SkillExecutor`.

### 4.6 Required Owner Decision
Approve **Candidate 4C** as the sandboxing standard for Stages 1–8.

### 4.7 Proposed Specification Wording
> *"Skill execution sandboxing on Windows utilizes a native tiered process isolation model: (1) Resource Quotas: Subprocesses are assigned to a Windows Job Object enforcing hard memory limits (`max_memory_mb`), CPU rate caps, and `KillOnJobClose`, ensuring that timeouts trigger complete process-tree termination without orphan processes. (2) Privilege Scoping: Subprocesses execute under a Restricted Token barring write access to repository source (`src/nirmal/`), data shards (`data/shards/`), and operating system trees; writable access is strictly confined to a dedicated temporary directory (`scratch/<run_id>/`). (3) Network Isolation: Subprocesses are barred from creating outbound network sockets unless the manifest explicitly declares `network: 'outbound'` and the GovernanceEngine issues an auditable grant. (4) Teardown: Job termination immediately purges memory and scrubs scratch workspaces."*

---

## 5. Blocker B5 — Skill Trust Demotion & Revocation

### 5.1 Current Issue
DRAFT §4 defines unidirectional promotion (`proposed` $\to$ `evaluated` $\to$ `trusted`). It provides no mechanism for demoting degraded, buggy, or vulnerable skills, nor does it specify how active tasks behave when a skill is revoked.

### 5.2 Evidence
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md) §4.1 line 328 & §4.2.
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §3.1 item 4.
- [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §3 and §8 (Blocker B5).

### 5.3 Architectural Impact
Without trust demotion, a compromised or regressed skill remains trusted indefinitely, poisoning the skill catalog and degrading cognitive performance.

### 5.4 Candidate Decisions
- **Candidate 5A (In-Place Skill Deletion)**: Delete bad skills from the registry. (Destroys provenance and historical reproducibility; crashes active tasks).
- **Candidate 5B (Complete 5-State Trust Lifecycle with Quarantine Semantics — RECOMMENDED)**:
  - 5 States: `proposed`, `evaluated`, `trusted`, `quarantined`, `deprecated`.
  - *Allowed Transitions & Authority*:
    - `proposed` $\to$ `evaluated`: Automated (passes evaluation battery).
    - `evaluated` $\to$ `trusted`: Human Project Owner sign-off required.
    - Any state $\to$ `quarantined`: Automated (empirical reliability drops $< 0.30$, verification failure spike, or sandbox violation) OR Human Owner command.
    - `quarantined` $\to$ `deprecated`: Human Owner command.
    - `quarantined` $\to$ `evaluated`: Human Owner command (after verified bug fix).
  - *Effect on Running Tasks*:
    - If a skill enters `quarantined`: Active tasks executing that skill immediately abort with typed error `SKILL_QUARANTINED` and trigger replanning.
    - If a skill enters `deprecated`: Existing tasks pinned to exact semver are allowed to complete, but `SkillRegistry.search()` and `Planner` are barred from selecting it for new plans.
  - *Provenance*: Every transition records actor, timestamp, prior state, new state, and evidence hash in the append-only audit trail.

### 5.5 Dependency Implications
Affects `SkillManifest` (`trust_state`), `SkillRegistry` state machine, `SkillExecutor` dispatch gates, and `GovernanceEngine` audit trails.

### 5.6 Required Owner Decision
Approve **Candidate 5B**.

### 5.7 Proposed Specification Wording
> *"The skill trust lifecycle implements five discrete states: `proposed`, `evaluated`, `trusted`, `quarantined`, and `deprecated`. Promotion from `proposed` to `evaluated` requires passing the automated evaluation battery; promotion from `evaluated` to `trusted` requires explicit human governance sign-off. Demotion to `quarantined` occurs automatically if empirical reliability drops below 0.30 or if verification/sandbox violations occur, immediately barring the skill from execution and triggering replanning in active tasks. Demotion to `deprecated` is a permanent administrative state barring selection for new tasks while preserving the immutable artifact for audit and historical provenance."*

---

## 6. Blocker B7 — Governance Policy Representation & Approval Authority

### 6.1 Current Issue
DRAFT §12.5 leaves policy format (YAML vs. Python) and approval authority unspecified. Executing arbitrary Python code for governance checks introduces security vulnerabilities and circular dependencies. An ambiguous approval authority risks autonomous self-promotion.

### 6.2 Evidence
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_DRAFT.md) §12 item 5.
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §2 item 15.
- [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §2.6 and §8 (Blocker B7).

### 6.3 Candidate Decisions
- **Candidate 7A (Executable Python Rule Engine)**: Express policies as executable Python functions. (High security risk, difficult auditability).
- **Candidate 7B (Declarative YAML Data + Designated Human Authority — RECOMMENDED)**:
  - *Data Format*: Declarative YAML files in `governance/policies/` validated against a frozen JSON Schema at startup.
  - *Evaluation*: Deterministic lookup with an unconditional fail-closed default-deny rule.
  - *Authority*: Human Project Owner is the sole authority for policy modifications, phase advancements, and `evaluated → trusted` promotions. Software agents are explicitly barred from self-authorization.
  - *Integrity*: Policy files are Git-tracked with SHA-256 hashes recorded in every decision log.

### 6.4 Consequences
Candidate 7B enforces the invariant that "governance is data, not code", guarantees transparent Git-diffable audit trails, and eliminates autonomous privilege escalation.

### 6.5 Dependency Implications
Must be decided before `GovernanceEngine` (Stage 1.5) can be implemented.

### 6.6 Required Owner Decision
Approve **Candidate 7B**.

### 6.7 Proposed Specification Wording
> *"Governance policy is defined strictly as declarative, version-controlled data files in YAML format conforming to a frozen JSON Schema, located in `governance/policies/`. Policy evaluation is purely deterministic with an unconditional fail-closed default-deny rule. Every access check evaluates to a typed `Decision` record containing a unique `decision_id`, rule reference, and policy hash, appended to the tamper-evident provenance log. Policy changes require human git commits; skill trust promotions (`evaluated → trusted`) and phase-gate advancements strictly require manual approval signed by the human Project Owner, which software agents cannot self-authorize."*

---

## 7. Blocker B8 — Skill Composition Architecture & Legacy Compatibility

### 7.1 Current Issue
DRAFT §3.7 claims skill composition "evolves `procedural.compose_strategies()`", but [`src/nirmal/agent/memory/procedural.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/memory/procedural.py) lines 360–448 is hardcoded to synthetic toy subskills ('X', 'Y', 'Z') using mock tools. Modifying it violates the protected path `src/nirmal/`.

### 7.2 Evidence
- [`src/nirmal/agent/memory/procedural.py`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/src/nirmal/agent/memory/procedural.py) lines 360–448:  
  *Explicit string matching on `skill == "X"`, `skill == "Y"`, `skill == "Z"` synthesizing hardcoded 5-step mock plans.*
- [`docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_AGI_ARCHITECTURE_REVIEW.md) §2 item 7:  
  *Classifies the composition subsystem as `CONFLICTS WITH CURRENT DESIGN`.*
- [`docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md`](file:///c:/Users/L.Thirumala%20Teja/OneDrive/Desktop/Nirmal%201/docs/NIRMAL_1_STAGE_0_BASELINE_REVIEW.md) §1.2 item C3 and §8 (Blocker B8).

### 7.3 Candidate Decisions
- **Candidate 8A (Evolve In-Place)**: Refactor `compose_strategies()` in `src/nirmal/agent/memory/procedural.py`. (Violates protected tree immutability).
- **Candidate 8B (Wrap In-Place)**: Write a wrapper around `compose_strategies()`. (Perpetuates toy technical debt).
- **Candidate 8C (Clean Subsystem Replacement + Legacy Adapter — RECOMMENDED)**:
  - Classify generic Skill Composition as a **brand-new Stage 2/3 subsystem** (`nirmal.skills.composition`) built in new files outside protected paths.
  - Implement full DAG port typing, JSON Schema input/output wiring, and cycle detection from first principles.
  - Leave `src/nirmal/agent/memory/procedural.py` **strictly unmodified** in the protected tree.
  - Provide a lightweight adapter (`LegacyStrategyAdapter`) during Stage 6 controller migration so that existing behavioral evaluations (`evals/`) pass without regression.

### 7.4 Consequences
Candidate 8C keeps `src/nirmal/` 100% untouched, eliminates toy technical debt, and allows generic DAG composition to be designed cleanly.

### 7.5 Dependency Implications
Clarifies that Stage 1–3 work does not touch `src/nirmal/` and establishes clean separation between legacy strategies and modern skills.

### 7.6 Required Owner Decision
Approve **Candidate 8C**.

### 7.7 Proposed Specification Wording
> *"Generic Skill Composition is an entirely new architectural subsystem (`nirmal.skills.composition`) designed from first principles with typed IO ports, topological DAG scheduling, and prerequisite resolution. The existing `compose_strategies()` method in `src/nirmal/agent/memory/procedural.py` is classified as a legacy prototype hardcoded to synthetic evaluation tasks; it remains strictly unmodified within the protected `src/nirmal/` baseline. A lightweight compatibility adapter will bridge legacy procedural strategies to modern skill manifests during Stage 6 orchestrator integration, guaranteeing zero regression across existing behavioral test suites."*

---

## 8. Cross-Blocker Dependency Analysis

An analysis of inter-blocker prerequisites reveals the fundamental causal structure of Stage 0 decisions:

```
[B7: Governance Policy & Authority]
   │
   ├──► [B2: Authoritative Roadmap Sequence]
   │       └── (Gates execution ordering for all subsequent stages)
   │
   ├──► [B1: Provider / Introspection Boundary]
   │       └── (Unlocks Provider & ContextManager interface contracts)
   │
   ├──► [B5: Trust Demotion Lifecycle]
   │       └── (Unlocks SkillRegistry & SkillManifest trust states)
   │
   └──► [B3: Rollback & Compensation Model]
           ▲
           │
[B4: Windows Sandbox Engine] ───────────────┘
           │
           └──► (Enforces workspace isolation for B3)
                   │
                   ▼
        [B8: Skill Composition Clean Replacement]
```

### Minimum Decision Sequence to Clear Stage 0:
1. **Decision 1: Blocker B7 (Governance Policy & Authority)**  
   *Foundation for all permission evaluation, default-deny, and human gating.*
2. **Decision 2: Blocker B2 (Authoritative Roadmap Order)**  
   *Establishes the master staging order and resolves the verification/controller deadlock.*
3. **Decision 3: Blocker B1 (Provider / Introspection Boundary)**  
   *Ffreezes the portable Provider interface and decouples core orchestration from neural internals.*
4. **Decision 4: Blocker B4 (Windows Sandbox Tiered Engine)**  
   *Defines the execution isolation primitives necessary for rollback and execution.*
5. **Decision 5: Blocker B3 (Rollback / Compensation Model)**  
   *Ffreezes the failure recovery contract in `SkillManifest`.*
6. **Decision 6: Blocker B5 (Trust Demotion Lifecycle)**  
   *Ffreezes the 5-state trust lifecycle and quarantine circuit-breakers.*
7. **Decision 7: Blocker B8 (Skill Composition Architecture)**  
   *Confirms new-build status and protects `src/nirmal/` from modification.*

---

## 9. Stage 1 Acceptance Gates Readiness

Evaluating the 12 Stage-1 acceptance gates against the current repository state:

| Gate ID | Gate Description | Status | Blocking Blocker |
|---|---|---|---|
| **G1** | All 8 interface contracts frozen without `UNRESOLVED` markers | **BLOCKED** | Blockers B1, B3, B4, B7 |
| **G2** | Subsystem dependency graph proven acyclic | **PASSABLE** | Design validated in review |
| **G3** | Provider boundary frozen (introspection = optional adapter) | **BLOCKED** | Blocker B1 |
| **G4** | Memory boundaries and write ACLs frozen | **PASSABLE** | Boundaries defined in baseline review |
| **G5** | GovernanceEngine contract frozen with fail-closed default-deny | **BLOCKED** | Blocker B7 |
| **G6** | SkillManifest schema frozen | **BLOCKED** | Blockers B3, B4, B5 |
| **G7** | Storage boundary decided (Desktop repository canonical; off-OneDrive) | **PASSABLE** | Canonical desktop scope established |
| **G8** | Zero behavior change in existing `tests/` and `evals/` | **PASSABLE** | Stage 1 defines interfaces only |
| **G9** | Protected-path write deny-list encoded (`src/nirmal/`, `data/shards/`) | **PASSABLE** | Deny-list rules defined |
| **G10** | Rollback requirements defined (new files only) | **PASSABLE** | Stage 1 adds only new modules |
| **G11** | Test plan specified per contract with fail-closed cases | **PASSABLE** | Specified in baseline review |
| **G12** | Roadmap ordering contradiction resolved | **BLOCKED** | Blocker B2 |

### Stage 0 Status:
Because formal human owner sign-off on Blockers B1–B5, B7, B8 has not yet been enacted:
```
STAGE_0_REQUIRES_REVISIONS
```

---

## 10. Safety Verification & Audit Trail

An automated integrity check of the desktop repository was executed immediately upon completing this report:

1. **Repository Identity**: Exclusively `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`.
2. **External Storage**: `D:\Nirmal-1-Store` was **NOT accessed, read, moved, copied, or modified**.
3. **Protected Path `src/nirmal/`**: 23 files, 246,321 bytes, SHA-256 `73b698d050b9fcc02ec1f898321b00980f2d0258e608dae32fc8aa994b6d33fb` (**100% Intact**).
4. **Protected Path `data/shards/`**: 18 files, 477,957 bytes, SHA-256 `cc66653f4f9771e4501af4f1ad25987a31469ab49b9c2d36a4bd9203f68dfdc1` (**100% Intact**).
5. **V10.10 Research Artifacts**: Unmodified.
6. **Training / Experiments**: Zero runs executed.
7. **Phase C Execution**: Zero executed (`PHASE_C_PREPARATION_BLOCKED`).
8. **Stage 1 Implementation**: Zero code written (`STAGE_1_IMPLEMENTATION_UNAUTHORIZED`).
9. **Git Tree**: Zero commits created.

```
FINAL GOVERNANCE STATUS:
STAGE_0_REQUIRES_REVISIONS
PHASE_C_PREPARATION_BLOCKED
HARNESS_RECOVERY_BLOCKED
PRODUCTION: STRICT NO-GO
STAGE_1_IMPLEMENTATION_UNAUTHORIZED
```
