# NIRMAL-1 — Skill-Based AGI/ASI Architecture

> ## 🔴 DRAFT / NOT AUTHORIZED FOR IMPLEMENTATION
>
> **Status**: DESIGN DRAFT ONLY — planning artifact, not an authorization.
> **Date**: 2026-09-19
> **Governance state at time of writing**:
> - Production: **STRICT NO-GO**
> - Phase C: **NOT AUTHORIZED** — `PHASE_C_PREPARATION_BLOCKED`
> - Harness recovery: `HARNESS_RECOVERY_BLOCKED`
> - Protected paths (unmodified by this document): `src/nirmal/`, `data/shards/`
>
> This document does **not** modify, supersede, or reinterpret any authoritative
> V10.x study document. It does **not** claim that AGI/ASI has been established.
> Nirmal-1 is an experimental research system; V10.10 associative-binding research
> is one research subsystem, not the whole system.

---

## Table of Contents

1. [Current Repository Findings (TASK 1)](#1-current-repository-findings)
2. [Architecture Overview (TASK 2)](#2-architecture-overview)
3. [Subsystem Definitions (TASK 2)](#3-subsystem-definitions)
4. [Skill System Design (TASK 3)](#4-skill-system-design)
5. [Memory Architecture (TASK 4)](#5-memory-architecture)
6. [Model / Intelligence Layer (TASK 5)](#6-model--intelligence-layer)
7. [300 GB Dedicated Storage Plan (TASK 6)](#7-300-gb-dedicated-storage-plan)
8. [Research vs. Production Separation (TASK 7)](#8-research-vs-production-separation)
9. [Data Flow](#9-data-flow)
10. [Dependency Graph](#10-dependency-graph)
11. [Implementation Roadmap (TASK 9)](#11-implementation-roadmap)
12. [Unresolved Decisions](#12-unresolved-decisions)
13. [Risks](#13-risks)
14. [Provenance Requirements](#14-provenance-requirements)

---

## 1. Current Repository Findings

Read-only inspection of the working tree (2026-09-19):

### 1.1 Core neural model — `src/nirmal/` (PROTECTED)
- `configuration_nirmal.py`, `model.py`, `attention.py` (GQA + RoPE + RMSNorm),
  `delta_net.py` (linear associative recurrence), `moe.py` (sparse Top-2 MoE),
  `generation.py` (autoregressive decoding).
- Prototype scale: 512 hidden / 12 layers / 32K vocab / 8K context.
  Frozen Candidate C design (V8): ~25.91B total / ~4.24B active params, 48.30 GB BF16 artifact.

### 1.2 Cognitive agent — `src/nirmal/agent/` (PROTECTED)
- `controller.py` — deterministic 11-state cognitive loop
  (IDLE→OBSERVE→RETRIEVE→REASON→PLAN→ACT→VERIFY→UPDATE→LEARN→DONE/FAILED).
- `learning_engine.py` — semantic + procedural knowledge induction, Bayesian reliability.
- `world_state.py`, `world_model.py` — grounded state, causal graph, predict-before-act.
- `verification.py` — deterministic ground-truth verification.
- `memory/` — `semantic.py`, `episodic.py`, `procedural.py`.
- `neural_bridge.py` — 7 neural pathways connecting the frozen core to cognition (V5).

### 1.3 Skill-related modules (existing precursors)
- **Procedural memory** (`agent/memory/procedural.py`) already implements strategy
  storage, reinforcement, penalization, and `compose_strategies()` (subskill
  composition, prerequisite gating) — this is the natural seed of the Skill System.
- No standalone skill registry, skill manifest format, or skill versioning exists yet.

### 1.4 Tool / computer-control modules
- `src/nirmal/tools.py` — Tool registry, sandboxed execution, JSON-schema function
  specs, built-ins (Calculator, StringUtility, MockEnvironment).
- No real computer-control (filesystem/browser/OS) surface exists; only mock/sandbox tools.

### 1.5 Provider / model infrastructure
- Training-side: `training/` (train pipelines V6–V8, tokenizers, data engines,
  distributed/mixed-precision/checkpointing infra, cost models).
- No runtime "provider abstraction" exists — the agent couples directly to
  `NirmalForCausalLM` via `neural_bridge.py`.

### 1.6 Evaluation infrastructure
- `evals/` — ~50 behavioral test modules (controller, memory, transfer, world model,
  causal, neural V5–V7 suites), procedural environments, holdout sets.
- `training/evaluation/` — V10.2–V10.9 research harnesses.
  **Note**: `v10_10_binding_harness.py` is absent (consistent with
  `HARNESS_RECOVERY_BLOCKED`).
- `scripts/` — study runners V9.x/V10.x, gate audits, readiness checks.

### 1.7 Configuration & data artifacts
- `pyproject.toml` (package), `data/NIRMAL-1-PRETRAIN-CONFIG-V1.json` (frozen
  pretrain config), `data/NIRMAL-DATA-V8.2.manifest.json` (shard checksums),
  `data/source_registry.json`, staging/promotion/acquisition records.
- `experiments/` — V5–V10.10 result JSONs and per-study directories.
- `docs/` — authoritative study reports V5–V10.10, Phase C spec drafts
  (V10_10_PHASE_C_SPEC_DRAFT.md — **not authorized**).
- `AGI_SPEC.md` — working specification with honest `[IMPLEMENTED]/[PLANNED]` status labels.

### 1.8 Gaps relative to a skill-based AGI architecture
| Needed subsystem | Current state |
|---|---|
| Skill Registry / manifests / versioning | Absent (only procedural strategies) |
| Skill acquisition pipeline | Partial (strategy synthesis in learning engine) |
| Governance/permission enforcement layer | Documented conventions only, not code |
| Model/provider abstraction | Absent (direct coupling via neural_bridge) |
| Real computer-control tool surface | Absent (mock tools only) |
| Persistent memory backends | In-memory only; no on-disk stores |
| Dedicated storage layout | Ad hoc (`experiments/`, `data/staging/`) |

---

## 2. Architecture Overview

Nirmal-1 is a **skill-based general-intelligence system**: a governed cognitive
orchestrator that acquires, verifies, composes, and executes *skills* over a
pluggable model layer, with persistent multi-layer memory and auditable provenance.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        GOVERNANCE / PERMISSION SYSTEM                      │
│   (gates every side-effecting operation; provenance + audit is mandatory)  │
└──────┬─────────────────────────────────────────────────────────────────────┘
       │ authorizes
┌──────▼─────────────────────────────────────────────────────────────────────┐
│                           CORE INTELLIGENCE (Orchestrator)                 │
│                                                                            │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Reasoning │  │  Planning /  │  │ Verification │  │   Learning /     │   │
│  │  Engine   │  │ Decomposition│  │ Critic System│  │ Improvement Loop │   │
│  └─────┬─────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│        │               │                 │                   │             │
│  ┌─────▼───────────────▼─────────────────▼───────────────────▼─────────┐   │
│  │                          SKILL SYSTEM                               │   │
│  │  Skill Registry · Skill Selection · Skill Execution · Composition   │   │
│  │  Skill Acquisition / Learning · Skill Verification                  │   │
│  └─────┬───────────────────────────────────────────────────┬──────────┘   │
│        │                                                   │              │
│  ┌─────▼──────────────┐                       ┌────────────▼───────────┐  │
│  │   MEMORY SYSTEM    │                       │ TOOL / ENV INTERFACE   │  │
│  │ working·episodic·  │                       │  Tool Registry ·       │  │
│  │ semantic·procedural│                       │  Computer Control ·    │  │
│  │ task·provenance    │                       │  Sandboxing            │  │
│  └─────┬──────────────┘                       └────────────┬───────────┘  │
│        │             ┌──────────────────┐                  │              │
│        └────────────►│ CONTEXT MANAGER  │◄─────────────────┘              │
│                      └────────┬─────────┘                                 │
└───────────────────────────────┼───────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                       MODEL / PROVIDER LAYER                              │
│  Provider registry · capability metadata · inference/tool-call interfaces │
│  (Nirmal core model = one provider among N; no coupling to a single model)│
└───────────────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                        EVALUATION SYSTEM                                  │
│  behavioral evals · skill evals · regression gates · leakage audits       │
└───────────────────────────────────────────────────────────────────────────┘
```

Design principles:

1. **Skills are the unit of capability.** Everything the system can *do* is a
   versioned, verified, provenance-tracked skill.
2. **Verification over confidence.** No skill result is trusted without an
   objective check (inherited from the existing `DeterministicVerifier` ethos).
3. **Model-agnostic intelligence.** The skill system never imports a model class;
   it talks to a provider interface.
4. **Governed execution.** Side effects (filesystem, network, training runs,
   Phase-gated research) pass through the permission system; denials are logged.
5. **Honest status labeling.** Every subsystem carries
   `[IMPLEMENTED]/[PARTIAL]/[PLANNED]` labels; autonomous self-improvement is
   **NOT implemented** and is not claimed.

---

## 3. Subsystem Definitions

Status legend: existing code noted where applicable; everything else is `[PLANNED]`.

### 3.1 Core Intelligence (Orchestrator) — evolves `agent/controller.py` `[PARTIAL]`
- **Purpose**: Top-level cognitive loop; owns goal lifecycle.
- **Responsibilities**: goal intake, state-machine progression, dispatch to
  reasoning/planning/skills, termination decisions.
- **Inputs**: goals, observations, governance policy.
- **Outputs**: verified results, execution traces, learning events.
- **Dependencies**: all subsystems below.
- **Persistent data**: execution traces → provenance memory.
- **Interfaces**: `run(goal) -> Outcome`; `step()`; trace inspection API.

### 3.2 Reasoning Engine — evolves `reasoning.py` `[PARTIAL]`
- **Purpose**: structured inference (deduction/induction/abduction/critique).
- **Inputs**: goal, retrieved memory, world state. **Outputs**: `ReasoningTrace`,
  action/skill recommendations.
- **Dependencies**: Model layer (for neural scoring), Memory, World model.
- **Persistent data**: reasoning traces (episodic/provenance memory).
- **Interfaces**: `reason(context) -> ReasoningTrace`; verification hooks.

### 3.3 Planning / Task Decomposition — evolves `planning.py` `[PARTIAL]`
- **Purpose**: decompose goals into DAGs of skill invocations.
- **Inputs**: goal, reasoning trace, skill registry query results.
- **Outputs**: `TaskGraph` whose nodes reference **skill IDs + versions**.
- **Dependencies**: Skill Registry, Reasoning, Memory (procedural templates).
- **Persistent data**: plans and replanning history → task memory.
- **Interfaces**: `plan(goal) -> TaskGraph`; `replan(node, failure)`.

### 3.4 Skill System (execution runtime) `[PLANNED]`
- **Purpose**: resolve, sandbox, and execute skills; enforce constraints.
- **Inputs**: skill invocation (id, version, args), execution context.
- **Outputs**: `SkillResult` (value + evidence + resource usage).
- **Dependencies**: Skill Registry, Tool Interface, Governance, Verification.
- **Persistent data**: execution records → provenance memory.
- **Interfaces**: `execute(skill_ref, args, context) -> SkillResult`.

### 3.5 Skill Registry `[PLANNED]`
- **Purpose**: authoritative catalog of skill manifests and versions.
- **Inputs**: skill manifests, trust-level updates, deprecations.
- **Outputs**: query results (by capability, prerequisite closure, trust ≥ X).
- **Dependencies**: storage (`skills/` area), Governance (registration gate).
- **Persistent data**: manifests, dependency graph, index.
- **Interfaces**: `register`, `resolve(id, version_spec)`, `search(capability)`,
  `dependency_closure(id)`.

### 3.6 Skill Acquisition / Learning — evolves `learning_engine.py` strategy synthesis `[PARTIAL]`
- **Purpose**: turn experience/instruction into *proposed* skills.
- **Inputs**: episodic trajectories, verified successes, human-authored specs.
- **Outputs**: **skill proposals** (trust level `proposed`, never auto-trusted).
- **Dependencies**: Episodic memory, Verification, Evaluation, Governance.
- **Persistent data**: proposals + supporting evidence.
- **Interfaces**: `propose_from_trajectory(episodes) -> SkillProposal`.
- **Constraint**: promotion `proposed → trusted` requires evaluation evidence
  **and** governance approval. Autonomous self-improvement is not implemented
  and is not authorized by this document.

### 3.7 Skill Composition — evolves `procedural.compose_strategies()` `[PARTIAL]`
- **Purpose**: build compound skills from constituent skills (DAG stitching,
  prerequisite gating, IO type matching).
- **Inputs**: constituent skill manifests, composition spec.
- **Outputs**: composite skill manifest (provenance = list of constituents).
- **Dependencies**: Registry, Planning, Verification.
- **Interfaces**: `compose([skill_refs], wiring) -> SkillManifest`.

### 3.8 Memory System `[PARTIAL — in-memory only]` — see §5.

### 3.9 Context Management `[PLANNED]`
- **Purpose**: assemble bounded model context from memory layers under token budget;
  eviction, summarization, relevance ranking.
- **Inputs**: goal, memory query results, budget from model capability metadata.
- **Outputs**: ordered context package for the provider interface.
- **Dependencies**: Memory, Model layer metadata.
- **Interfaces**: `build_context(goal, budget) -> ContextPackage`.

### 3.10 Tool / Environment Interface — evolves `tools.py` `[PARTIAL]`
- **Purpose**: uniform, sandboxed, schema-described actions on environments.
- **Inputs**: tool invocations from skill execution. **Outputs**: observations.
- **Dependencies**: Governance (permission per tool class), sandboxes.
- **Persistent data**: tool call log → provenance memory.
- **Interfaces**: `ToolRegistry.invoke(name, args, permissions) -> Observation`.

### 3.11 Computer Control `[PLANNED — high risk, gated]`
- **Purpose**: real filesystem/process/browser control as a *tool family*.
- **Constraints**: allowlist paths, dry-run mode, mandatory audit records,
  never enabled by default; requires explicit governance grant per session.

### 3.12 Verification / Critic System — evolves `agent/verification.py` `[PARTIAL]`
- **Purpose**: objective checking of skill results, plans, and proposals;
  adversarial critique (inheriting the V5.1 falsification ethos).
- **Inputs**: result + success criteria from the skill manifest.
- **Outputs**: pass/fail + evidence; calibration statistics.
- **Interfaces**: `verify(result, criteria) -> Verdict`; pluggable verifiers
  (predicate, numeric tolerance, string/regex, structural, test-suite, prover `[PLANNED]`).

### 3.13 Learning / Improvement Loop `[PARTIAL]`
- **Purpose**: post-task credit assignment, memory consolidation, skill
  reliability updates (Laplace-smoothed, as today), proposal generation.
- **Outputs**: memory writes, reliability updates, skill proposals.
- **Constraint**: weight updates to any neural model are a **training event**
  governed by the training gates (V8.3/V8.4 NO-GO applies); never silent.

### 3.14 Evaluation System — evolves `evals/` `[PARTIAL]`
- **Purpose**: behavioral eval suites, per-skill eval batteries, regression
  gates, leakage audits, frozen benchmarks.
- **Persistent data**: eval artifacts, frozen benchmark hashes.
- **Interfaces**: `evaluate(skill_ref) -> EvalReport`; CI-style gates.

### 3.15 Governance / Permission System `[PLANNED — highest priority]`
- **Purpose**: encode the rules currently held as conventions:
  protected paths, phase gates (Phase C blocked), production NO-GO,
  training-launch gates, tool permissions, skill trust promotion.
- **Inputs**: requested operations. **Outputs**: grant/deny + audit record.
- **Persistent data**: policy files (version-controlled), decision log (append-only).
- **Interfaces**: `check(operation, context) -> Decision`; policy is data, not code.

### 3.16 Model / Provider Layer `[PLANNED]` — see §6.

---

## 4. Skill System Design

### 4.1 Skill manifest (abstraction)

A skill is a declarative manifest plus an executable body (code, plan template,
or prompt program). Proposed manifest schema (YAML/JSON):

```yaml
skill:
  id: "nirmal.text.checksum_route"        # stable, namespaced identity
  version: "1.2.0"                        # semver; immutable once published
  kind: "procedural"                      # procedural | code | prompt | composite
  capabilities: ["routing", "checksum"]   # searchable capability tags
  prerequisites:                          # skills that must exist & be trusted
    - { id: "nirmal.text.transform", version: ">=1.0" }
  inputs:
    - { name: "payload", type: "string", required: true }
  outputs:
    - { name: "route", type: "string" }
  tools_required: ["mock_environment"]    # tool classes, permission-checked
  memory_requirements:
    reads: ["semantic", "procedural"]
    writes: ["episodic"]
  execution_constraints:
    timeout_s: 30
    max_tool_calls: 20
    sandbox: "restricted"
    side_effects: "none"                  # none | workspace | external (gated)
  verification:
    method: "structural"                  # predicate|numeric|string|structural|test_suite
    success_criteria: { assert: "route in observed_valid_routes" }
  provenance:
    origin: "learned"                     # authored | learned | composed
    source_trajectories: ["episode:abc123", "episode:def456"]
    created_by: "learning_engine@v3"
    evidence: ["evals/skill/checksum_route/report_0007.json"]
  trust_level: "proposed"                 # proposed | evaluated | trusted | deprecated
  dependency_graph: ["nirmal.text.transform@1.x"]
  composition:
    composable: true
    exposes_ports: { in: ["payload"], out: ["route"] }
```

### 4.2 Skill lifecycle

| Operation | Mechanism |
|---|---|
| **Discover** | Registry search by capability tags + input/output type match + trust filter; planner queries during decomposition. |
| **Select** | Score = capability match + prerequisite satisfaction + empirical reliability (Laplace-smoothed, as in current procedural memory) + cost estimate; governance filter last. |
| **Execute** | Resolve version → check prerequisites → acquire tool permissions → run in sandbox under constraints → produce `SkillResult` with full trace. |
| **Verify** | Apply manifest `verification` via Critic; attach verdict + evidence to result; failed verification never writes semantic facts. |
| **Compose** | Type-checked DAG wiring of exposed ports; prerequisite gating (compound fails if a constituent is missing — preserves current honest-failure behavior); emits a `composite` manifest with constituent provenance. |
| **Update** | New semver version; old versions immutable; reliability stats carry over only with explicit migration note. |
| **Propose (new skill)** | Learning engine lifts parameters from verified trajectories → `trust_level: proposed`; stored in registry but not selectable by default. |
| **Evaluate (learned skill)** | Dedicated eval battery: held-out instances, permutation invariance, AST anti-hardcoding scan (existing tooling), ablation vs. no-skill baseline; report stored as evidence. |
| **Promote** | `proposed → evaluated` on passing battery; `evaluated → trusted` requires governance approval (human decision). **No autonomous promotion.** |

### 4.3 Explicit non-claims
- Skill *proposal* pipelines exist in embryonic form (strategy synthesis);
  a full acquisition/evaluation/promotion loop is `[PLANNED]`.
- Autonomous self-improvement (system modifying its own skills/weights without
  gated review) is **not implemented and not authorized**.

---

## 5. Memory Architecture

Six logical layers. Current code (`WorkingMemory`, `SemanticMemory`,
`EpisodicMemory`, `ProceduralMemory`) provides in-memory implementations of four;
persistence backends are `[PLANNED]` (interfaces first, backends later).

| Layer | Purpose | Storage format (proposed) | Retrieval | Write policy | Verification requirement | Retention |
|---|---|---|---|---|---|---|
| **Working / context** | Active goal, scratchpad, token-budgeted context | RAM only; snapshot JSON on trace capture | direct / recency | orchestrator only | none (transient) | discarded at task end; snapshot to episodic |
| **Episodic** | Full trajectories (goal, plan, actions, observations, outcome, reward) | append-only JSONL + embedding index | goal-similarity (vector) + filters (family, success) | append-only at LEARN state | trajectory must include verifier verdicts | rolling window + consolidation; never silently deleted (archived) |
| **Semantic** | Verified facts, constraints, contradiction-resolved knowledge | versioned KV/triple store + vector index; `is_outdated` flags kept | hybrid keyword+vector, recency-weighted, exclude-outdated default | **only verified facts** (verifier-passed); contradictions archive old value | mandatory — no unverified writes | long-lived; superseded facts archived with version chain |
| **Procedural / skill** | Skill manifests, reliability stats, composition graphs | registry files (see §7 `skills/`) + stats DB | registry query (capability, trust, reliability) | via registry lifecycle only (§4.2) | promotion gates (§4.2) | versions immutable; deprecation instead of deletion |
| **Task** | Active/paused plans, replanning history, task queue | JSON state files | by task id / status | planner + orchestrator | plan nodes must reference resolvable skills | completed tasks compacted into episodic |
| **Provenance / audit** | Execution traces, governance decisions, hashes, forensic records | append-only, hash-chained JSONL (tamper-evident) | by time/task/skill id | append-only; **no rewrites ever** | each record self-describing with SHA-256 of payload | permanent (subject only to explicit governed archival) |

Consolidation ("sleep cycle", currently `[PLANNED]` in AGI_SPEC §3.1) runs as a
governed batch job: episodic clusters → semantic facts + skill proposals, with
every consolidation output carrying provenance links to source episodes.

---

## 6. Model / Intelligence Layer

Goal: the skill system must never know *which* model it is talking to.

Separated concerns:

| Component | Responsibility |
|---|---|
| **Model Provider** | Lifecycle of a backend (load/unload local weights, or session mgmt for a remote/API model). One provider per backend implementation. |
| **Model Identity** | Immutable descriptor: name, version, weights hash, tokenizer hash, training-data manifest ref. The Nirmal core model (Candidate C when/if trained) is *one identity*; prototype checkpoints are others. |
| **Inference Interface** | `generate(context, params) -> tokens/logits`; batch + streaming variants. |
| **Reasoning Interface** | Higher-level scoring ops used by cognition: likelihood scoring, ranking, embedding extraction (formalizes today's `neural_bridge.py` pathways). |
| **Tool-Calling Interface** | Structured function-call emission/parsing against JSON schemas from the Tool Registry; capability-flagged (not all models support it). |
| **Context Interface** | Token budget, tokenizer access, context-window metadata for the Context Manager. |
| **Capability Metadata** | Declared + measured: context length, tool-calling support, eval scores per capability, cost/latency profile. Selection decisions cite measured evidence, not vendor claims. |

Rules:
- No external model is assumed equivalent to Nirmal-1; capability metadata is
  per-identity and empirically measured by the Evaluation System.
- Provider selection is a policy decision (governance-visible), not hardcoded.
- `neural_bridge.py` becomes the *reference implementation* of the Reasoning
  Interface for the local Nirmal core — behind the interface, not imported directly.

---

## 7. 300 GB Dedicated Storage Plan

~300 GB reserved. **Not to be pre-allocated or filled**; areas grow on demand.

### 7.1 Designated Storage Root Registration (DESIGN DECISION / DOCUMENTATION UPDATE)
- **Repository Location**: `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`  
  Houses codebase, test batteries, specifications, documentation, and lightweight Git-tracked manifests.
- **Designated External Storage Root**: `D:\Nirmal-1-Store`  
  Designated local drive root for large project data, models, datasets, checkpoints, durable memory, and forensic logs, isolated outside the OneDrive synchronization tree.

Existing registered subdirectories at `D:\Nirmal-1-Store`:
- `models\` — Model identities, safetensors weights, tokenizers, checkpoints
- `datasets\` — Raw, processed, tokenized shards, local dataset subsets
- `skills\` — Skill registry manifests, executables, dependency indexes
- `memory\` — Persistent backends (episodic JSONL, semantic store, embeddings)
- `training\` — Run configurations, training metrics, execution logs
- `experiments\` — Experimental study results, outputs, evaluations
- `evaluation\` — Frozen benchmarks, test batteries, evaluation reports
- `artifacts\` — Runtime scratch artifacts, tool outputs, sandbox runs
- `forensic\` — Tamper-evident hash-chained provenance logs, decision logs
- `backups\` — Scheduled snapshots of memory, skills, and audit logs
- `scratch\` — Disposable temporary working directory

### 7.2 Directory Layout & Retention Policy

| Area | Purpose / contents | Growth | Retention | Version control |
|---|---|---|---|---|
| `models/` | Model identities: weights (safetensors shards), tokenizers, identity manifests w/ hashes | Step-wise, large (prototype ckpts MBs–GBs; Candidate C would be ~48.3 GB *if ever trained — currently NO-GO*) | Keep identities referenced by evals/provenance; prune orphans via governed job | **Local-only / object storage**; manifests Git-tracked |
| `models/checkpoints/` | Training checkpoints (optimizer state incl.) | Bursty during runs (each full ckpt ≫ model size) | Keep last-N + milestone ckpts | Local-only |
| `datasets/` | Raw/clean/tokenized corpora, binary shards (`.bin/.idx`), split manifests | Largest area; 200B-token plan ≈ 372 GB uint16 **exceeds 300 GB — full-scale corpus must live on cluster storage (per V8.2), only subsets/pilots here** | Raw pruned after verified tokenization; shards kept while referenced | Manifests + checksums Git-tracked; data local-only |
| `skills/` | Skill manifests, skill bodies, reliability stats, dependency index | Small, steady (KBs per skill) | Immutable versions; deprecate not delete | **Git-tracked** (registry is code-like) |
| `memory/` | Persistent memory backends: episodic JSONL, semantic store, task state, embedding indexes | Steady, moderate (GBs over time) | Consolidation + archival policy (§5) | Local-only; schema Git-tracked |
| `training/` | Run configs, logs, metrics, dry-run artifacts | Bursty per run | Configs permanent; logs compressed after N days | Configs Git-tracked; logs local-only |
| `experiments/` | Research study outputs (V9.x/V10.x style JSON, per-study dirs) | Steady, small–moderate | Permanent for published studies | Result JSONs Git-tracked (as today); bulk local-only |
| `evaluation/` | Frozen benchmarks (hash-locked), eval reports, skill eval batteries | Small, steady | Frozen benchmarks permanent | Git-tracked (freezing depends on it) |
| `artifacts/` | Runtime artifacts: generated files, tool outputs, sandbox workspaces | Churny | TTL cleanup (e.g., 30 days) unless pinned | Local-only |
| `forensic/` | Provenance chain, governance decision log, recovery/incident records (e.g., harness-recovery evidence) | Small, append-only | **Permanent, append-only, never rewritten** | Local-only + periodic hash anchors Git-tracked |
| `backups/` | Snapshots of `skills/`, `memory/`, `forensic/`, manifests | Periodic | Rolling (e.g., 4 weekly + 6 monthly) | Local-only |
| `scratch/` | Disposable working space | Churny | Auto-clean | Local-only, gitignored |

Indicative budget guidance (not reservations): datasets ≤ 120 GB local subset,
models+checkpoints ≤ 100 GB, memory ≤ 20 GB, backups ≤ 30 GB, everything else ≤ 10 GB,
keeping ≥ 20 GB free headroom at all times (alert at 85% utilization).

**Documentation-only update**: No files are moved or copied by this registration.
Migration of existing `experiments/` and `data/staging/` content is a Stage-1+ decision (§11)
requiring its own governed plan. Protected trees (`src/nirmal/`, `data/shards/`) remain unmodified.

---

## 8. Research vs. Production Separation

| | V10.x research track | Nirmal-1 AGI architecture track |
|---|---|---|
| Scope | Associative binding, rule induction, scaling studies (V9.x/V10.x) | System architecture: skills, memory, governance, providers |
| Artifacts | `docs/V10_*.md`, `training/evaluation/*harness*.py`, `experiments/v10_*` | This document; future `src/` interfaces (Stage 1+) |
| Authority | Governed by approved amendments (V10_10 AMENDMENT_01) — **unmodified** | DRAFT only — no authority |
| Current state | `PHASE_C_PREPARATION_BLOCKED`, `HARNESS_RECOVERY_BLOCKED` | Stage 0 (architecture definition) |
| Cross-effects | None: this document does not alter, reinterpret, or authorize anything in the V10.x track | Skill/eval design *borrows methodology* (anti-leakage, ablations, falsification) but no code or data coupling |

Explicit statements:
- The V10.10 amendment is **not modified** by this document.
- Research proposals herein are **not** authorizations.
- Current benchmarks (incl. the NIRMAL AGI CAPABILITY INDEX and any V10.x result)
  are **not** treated as proof that AGI/ASI has been established.

---

## 9. Data Flow

Primary task flow:

```
Goal ─► Governance.check ─► Orchestrator
  ─► Context Manager (◄─ Memory: working/semantic/episodic)
  ─► Reasoning Engine (◄─ Model layer: reasoning interface)
  ─► Planner ─► Skill Registry (discover/select)
  ─► Skill Execution ─► Tool Interface ─► Environment
        │                    │
        ▼                    ▼
   Verification ◄─── Observations
        │ pass                │ fail
        ▼                     ▼
   Memory writes         Replan / recover
   (semantic: verified only;
    episodic: full trajectory;
    provenance: always)
        ▼
   Learning loop ─► reliability updates ─► skill proposals ─► Evaluation
                                                    │
                                          Governance promotion gate
```

Every arrow that causes a side effect (tool call, memory write, registry change,
training event) also emits a provenance record.

## 10. Dependency Graph

```
Governance ──(gates)──► everything below
Model/Provider layer ◄── Reasoning, Context Mgr, Skill Execution (via interfaces only)
Skill Registry ◄── Planner, Skill Execution, Composition, Acquisition, Evaluation
Memory ◄── Orchestrator, Context Mgr, Learning, Skill Execution
Tool Interface ◄── Skill Execution (only path to environments)
Verification ◄── Skill Execution, Learning, Acquisition, Evaluation
Evaluation ◄── Acquisition (promotion evidence), Model layer (capability metadata)
Provenance memory ◄── all subsystems (append-only sink; depends on nothing)
```

Inversion rule: nothing above the Model/Provider layer may import a concrete
model; nothing outside the Tool Interface may touch an environment; nothing
outside Governance may grant permissions.

## 11. Implementation Roadmap

> Staged plan only — **execution of any stage is NOT authorized by this document.**

| Stage | Content | Exit criterion |
|---|---|---|
| **0 — Architecture definition** | This document; review; resolve §12 decisions | Approved architecture baseline |
| **1 — Core interfaces** | Define Python interfaces/dataclasses: SkillManifest, SkillResult, Provider, Verifier, MemoryLayer, PermissionCheck (new modules; no protected-path edits) | Interfaces + unit tests, zero behavior change |
| **2 — Skill registry** | Manifest schema validation, versioning, storage in `skills/`, search API | Registry round-trip + query tests |
| **3 — Skill execution** | Sandboxed executor honoring constraints; tool permission checks; provenance records | Existing mock-tool tasks runnable as skills |
| **4 — Memory** | Persistent backends for episodic/semantic/procedural/provenance per §5 | Durability + retrieval parity with in-memory impls |
| **5 — Planning/reasoning integration** | Planner nodes reference skill refs; controller states dispatch through skill system | Existing eval suites pass through new path |
| **6 — Verification** | Pluggable verifier registry; critic reports; calibration tracking | Verifier parity + new structural/test-suite modes |
| **7 — Skill acquisition** | Proposal pipeline from trajectories; trust levels; **manual** promotion workflow | Proposals generated + evaluated, none auto-promoted |
| **8 — Evaluation** | Per-skill eval batteries, regression gates, frozen-benchmark integration | Eval reports attached as promotion evidence |
| **9 — Controlled scaling** | Only after all prior gates + governance sign-off: larger models/providers, real computer-control pilots (heavily sandboxed) | Explicit governance authorization per step |

## 12. Unresolved Decisions

1. **Storage root location (RESOLVED / REGISTERED)**: Formally registered as
   `D:\Nirmal-1-Store` (external NVMe/drive dedicated root outside OneDrive sync scope).
   The repository remains at `C:\Users\L.Thirumala Teja\OneDrive\Desktop\Nirmal 1`.
   Existing subdirectories `models\`, `datasets\`, `skills\`, `memory\`, `training\`,
   `experiments\`, `evaluation\`, `artifacts\`, `forensic\`, `backups\`, and `scratch\`
   are designated for large project data. No files are moved by this registration.
2. **Semantic store backend**: SQLite vs. embedded KV (LMDB) vs. flat JSONL+index.
3. **Embedding source** for memory retrieval: frozen prototype core vs. dedicated
   small embedder — and its identity/versioning in provenance.
4. **Skill body formats**: which of {code, plan-template, prompt-program} are
   allowed at which trust levels; code-skill sandboxing technology on Windows.
5. **Governance policy format**: YAML policy files vs. Python rule engine;
   who holds approval authority for trust promotions.
6. **Provider API shape**: sync vs. async; streaming as core or extension.
7. **Relationship of `nirmal-1/` and `niraml-1/` placeholder dirs** (each contains
   only a README) to the storage plan — consolidate or remove (needs owner decision).
8. **Migration plan** for existing `experiments/` + `data/staging/` into the new
   layout (Stage ≥ 1, separate proposal).
9. **V10.10 harness recovery** remains blocked; whether Phase C preparation ever
   resumes is outside this document's scope.

## 13. Risks

| Risk | Mitigation (design-level) |
|---|---|
| **Capability overclaiming** (repeating V5-era artifacts) | V5.1 falsification methodology mandatory in skill eval batteries; symmetric ground-truth checks; anti-leakage audits |
| **Skill registry poisoning** (bad learned skills gain trust) | Trust levels, immutable versions, mandatory eval evidence, human promotion gate |
| **Ungoverned side effects** (computer control) | Tool permission classes, default-deny, dry-run mode, append-only audit |
| **Provenance loss** (as in the harness-recovery incident) | Hash-chained append-only forensic log; backups area; manifests with SHA-256 everywhere |
| **Storage exhaustion** (300 GB is small vs. 200B-token ambitions) | Dataset full-scale staging remains cluster-side (V8.2 architecture); local subsets only; 85% alerts |
| **Model coupling creep** | Interface-only rule enforced by import-linting in CI (Stage 1) |
| **Catastrophic forgetting / memory corruption** | Contradiction archival (never overwrite), consolidation as governed batch jobs, retention policies |
| **Scope creep: research ↔ architecture entanglement** | §8 separation; architecture code never imports research harnesses |

## 14. Provenance Requirements

Every subsystem MUST:
1. Emit an append-only provenance record for each side-effecting operation
   (actor, operation, inputs hash, outputs hash, timestamp, governance decision id).
2. Reference immutable identities (skill id+version, model identity hash,
   dataset manifest hash) — never mutable names.
3. Store evidence for every trust/quality claim (eval report paths, seeds, hashes).
4. Preserve superseded data (archive, version chain) rather than overwrite.
5. Treat the forensic area as permanent and tamper-evident (hash chaining,
   periodic anchors committed to Git).

---

*End of draft. This document is a planning artifact only.*

**FINAL STATUS: PHASE_C_PREPARATION_BLOCKED — Phase C is NOT authorized. Production remains STRICT NO-GO.**
