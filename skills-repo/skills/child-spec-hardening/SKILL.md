---
name: child-spec-hardening
description: Harden child specs into implementation-ready delivery specs after a parent/master spec or spec-orchestrator queue exists. Use when the user wants to make one or more child specs implementation-ready, deepen generated child specs, fill contract depth, derive harness cases, inherit verification commands from accepted slices, run a doc-coauthoring-style refinement plus auto-resolve loop, or turn a spec-orchestrator hardening queue into ready child delivery packs. Do not use for blank parent specs or runtime implementation.
---

# Child Spec Hardening

Turn a child spec draft or spec-orchestrator hardening queue item into an implementation-ready delivery spec without turning the orchestrator into a monolith.

## Core Promise

Produce depth, not code:

1. preserve parent scope,
2. harden the child contract,
3. derive concrete cases and verification,
4. run a content-quality and auto-resolve loop,
5. stop for real decisions,
6. finish with an implementation-readiness verdict.

Use `doc-coauthoring` principles for writing missing spec content, and `doc-review-autoresolve` principles for cleanup and re-review. Do not hallucinate missing product decisions.

## Shared Workflow Contract

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical reference for the Session Briefing, Review Control Surface, Parallel Work Control Surface, DoR/DoD, Decision Freeze Pack, and Mini-Retro.

At the start of larger or resumed hardening work, clarify or infer:
- active mode/skill,
- source of truth child, parent, index, and predecessor specs,
- target child goal,
- non-goals,
- in-scope hardening output,
- expected deliverable,
- verification/review path,
- open decisions.

Every hardened child spec must include a short Review Control Surface near the top with goal, in scope, out of scope, key test/harness cases, key verification commands, open decisions, and readiness status. It is the user's fast review path and must stay synchronized with the detailed child contract.

## When To Use

Use this skill when the request includes:

- "make this child spec implementation-ready"
- "harden this child spec"
- "deepen S3/S4/S5"
- "fill the hardening queue"
- "turn these generated child specs into real specs"
- "add contract depth / harness cases / verification commands"
- "run Doc Co-Authoring plus Auto-Resolve on child specs"

Use `spec-orchestrator` first when the child set, parent coverage, dependencies, or parallelization order is unclear.
Use `doc-coauthoring` first when there is no parent/master spec yet.
Use `spec-change-delivery` only after this skill reports `IMPLEMENTATION READY` for the target child.

## Required Inputs

Discover before asking:

1. Child spec path or hardening queue item.
2. Parent/master spec path.
3. Child index or slice plan, if present.
4. Accepted prior slices and their verification commands.
5. Target repo/runtime conventions.
6. Existing OpenSpec artifacts, if the project uses them.

Ask only if the target child or parent cannot be inferred safely.

## Workflow

### 1. Load Scope Sources

Read:

- target child spec,
- parent/master spec sections the child touches,
- child index/slice plan,
- accepted predecessor specs,
- verification commands from accepted similar slices.

Do not use old/legacy specs as normative sources unless the parent explicitly says they remain authoritative for this child.

### 2. Normalize Child Contract

Ensure the child has:

- date/status/scope,
- Review Control Surface,
- in scope and out of scope,
- parent/master coverage,
- parent scope conformance table,
- dependencies, hardening write-set, and shared/read-only files when parallel hardening is plausible,
- closeout sync targets,
- history and `SessionId`.

Parent conformance statuses are:

- `preserves`,
- `extends`,
- `narrows_with_rationale`,
- `defers_to_child`,
- `missing_from_child`,
- `contradicts_parent`.

`contradicts_parent` and unexplained `missing_from_child` block implementation-readiness.

### 3. Add Normative Contract Depth

For every important behavior, artifact, state, API, content schema, runtime gate, or operational flow in scope, define the normative contract at the level needed for implementation:

- required fields and allowed values,
- status values and failure states,
- canonical serialization/hash/signature rules when integrity matters,
- source/identity/provenance/version fields when downstream interpretation depends on them,
- compatibility and fallback rules,
- security/redaction rules,
- examples or fixture sketches when ambiguity would otherwise remain.

Use domain-specific fields only when the child's own downstream flow requires them. Do not turn examples from another domain into universal requirements.

### 4. Decide Canonical Examples vs Fixtures

For contract-heavy children, explicitly decide how canonical examples are represented.

Treat a child as contract-heavy when it defines any of these:

- manifest, schema, API, status, hash, signature, entitlement, migration, fallback, report, artifact or case-file format,
- data consumed by later slices or external tools,
- security/redaction or compatibility-sensitive structures,
- content packages where identity, provenance or versioning matters.

Choose one of these patterns and record it in the child spec:

- **Embedded canonical examples**: use when the example is short, normative, and needed by readers to understand the contract.
- **Referenced fixture files**: use when examples are large, numerous, executable by the harness, or likely to evolve with tests.
- **Hybrid**: include a compact canonical example in the spec and require full fixtures as harness files.

If examples are referenced instead of embedded, the spec must state:

- required fixture paths or naming pattern,
- which cases each fixture covers,
- which fields/values are normative,
- whether fixtures must exist before implementation starts or are in scope for implementation,
- how harness verification proves the fixtures were actually exercised.

If a contract-heavy child has neither embedded examples nor required fixture references, mark it `NEEDS HARDENING`.

### 5. Derive Acceptance and Harness Cases

A child spec is not implementation-ready with generic acceptance prose alone.

Create a cases table when runtime, data, contracts, security, or user flow are involved:

| Case | Purpose | Inputs / Fixture | Expected Exit / Status | Expected Artifacts | Negative / Secret Assertions |
|---|---|---|---|---|---|

Include positive, negative, blocked, fallback, and security/redaction cases when relevant. Link cases to embedded examples or fixture files when the child is contract-heavy. Mark unavailable downstream cases as `blocked`, never passed or skipped-as-success.

### 6. Harden Verification Commands

Inherit command style from accepted predecessor slices when possible.

Verification commands must include, when relevant:

- execution context: cwd, shell, target runtime, platform assumptions,
- SDK/runtime selection details,
- risk-based preflight,
- deterministic readiness handling before endpoint assertions,
- gate verification commands,
- local and container/harness gates when the parent or predecessors require them,
- concrete success criteria for exit codes and output/artifacts,
- anti-loop rule: do not add commands that only verify the verification.

Do not silently simplify commands. If a simplification changes the gate, mark `[DECISION verification command simplification approval]`.

### 7. Run Content Quality Review

Review the whole child against:

- correctness/domain fit,
- necessity/scope discipline,
- completeness,
- consistency,
- unambiguity,
- feasibility,
- verifiability/testability,
- traceability,
- atomicity/abstraction level,
- operational/lifecycle fit.

Fix safely inferable issues. Mark true decisions as `[DECISION ...]` or `[MISSING ...]`.

### 8. Auto-Resolve Loop

After edits, run the `doc-review-autoresolve` loop conceptually:

1. re-review touched sections and parent references,
2. fix autonomous inconsistencies,
3. repeat until only true decision blockers remain,
4. assign readiness verdict.

Stop when resolving a finding would require a new product, scope, architecture, security, legal, or data-contract decision.

### 9. Assign Readiness

Use exactly one final status:

- `IMPLEMENTATION READY`: all hardening gates pass and no blocking markers remain.
- `READY WITH NON-BLOCKING NOTES`: implementation can start, but explicit non-blocking notes remain.
- `NEEDS USER DECISION`: one or more decisions are required.
- `NEEDS PARENT/ORCHESTRATOR SYNC`: child scope conflicts with parent/index or missing coverage destination.
- `NEEDS HARDENING`: required contract, case, verification, or DoR depth is still missing.

Do not mark a child implementation-ready just because it has the expected section headings.

After assigning the final status, update or report the child spec's Review Control Surface so its `Offene Entscheidungen` and `Readiness Status` match the verdict.

## Required Delivery Sections

Use or adapt these sections in the child spec:

```md
## Goal
## Review Control Surface
## In Scope
## Out of Scope
## Parent/Master Coverage
## Parent Scope Conformance
## Decision Freeze Pack
## Normative Contract
## Canonical Examples and Fixtures
## Control Flow and Failure Cases
## Harness and Verification Cases
## Verification Commands
## Definition of Ready for Implementation
## Definition of Done / Closeout Evidence
## Dependencies and Write-Set
## Closeout Sync Targets
```

For very small governance children, a compact variant is acceptable if the omitted sections are explicitly irrelevant.

When parallel hardening is plausible, the `Dependencies and Write-Set` section must define:
- the child spec/doc write-set owned by this hardening lane,
- shared files that are read-only for this hardening lane,
- dependencies and serial prerequisites,
- lane-level review/consistency verification commands,
- integration owner for shared control files,
- merge/sync order relative to sibling children.

If the child also claims it can later be implemented in parallel, this section must additionally define the future runtime/code write-set and any shared runtime files/helpers/harnesses. If those fields cannot be made explicit, mark only the implementation as not safe for parallel execution and route implementation parallelization back to `spec-orchestrator`.

## Output Contract

After hardening, report:

1. Target child spec(s).
2. Changes applied or proposed.
3. Parent conformance result.
4. Content-quality result.
5. Review Control Surface status.
6. Verification depth result.
7. Final readiness verdict.
8. Exact decision blockers, if any.
9. Mini-Retro after substantial hardening blocks or before handoff/context loss: decisions, changes, open items, missing evidence, skill/workflow friction, and whether to continue in this session or start a new one.

Use reader-calibrated findings for all blockers or noteworthy non-blocking notes. Assume the user may have reviewed only goal, in scope, out of scope, verification commands, and test cases. For each finding, explain:

- short finding,
- why it matters,
- where to check in the spec,
- concrete example,
- needed action or decision.

Do not report only terse technical labels such as "contract-heavy fixture decision missing". Explain that this means the spec must decide whether the implementer reads a small canonical example inside the spec, or uses named fixture files that the harness will execute.

When editing files, append one concise history row and preserve `SessionId`.

## Guardrails

- Do not implement runtime code.
- Do not leave the Review Control Surface stale after changing scope, cases, commands, open decisions, or readiness.
- Do not widen child scope without parent conformance and a re-entry path.
- Do not invent missing product decisions.
- Do not use skipped cases as passed evidence.
- Do not let generic commands replace accepted-slice verification patterns.
- Do not mark `done` or `accepted` unless evidence exists; use `parent_claims_done` or `reference_done` only with cited evidence.
- Do not block parallel hardening just because later implementation write-sets are unknown; keep those as implementation-readiness gaps.
- Do not mark a child safe for parallel implementation when allowed runtime/code write-sets, shared/read-only runtime files, integration owner, or merge/sync order are missing.
