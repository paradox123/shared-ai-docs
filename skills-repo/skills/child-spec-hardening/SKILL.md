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

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical reference for the Session Briefing, Review Control Surface, Parallel Work Control Surface, DoR/DoD, Decision Freeze Pack, Spec Goldstandard, and Mini-Retro.

At the start of larger or resumed hardening work, clarify or infer:
- active mode/skill,
- source of truth child, parent, index, and predecessor specs,
- target child goal,
- non-goals,
- in-scope hardening output,
- expected deliverable,
- verification/review path,
- open decisions.

Every hardened child spec must include a short Review Control Surface near the top with spec variant, Goldstandard status, goal, in scope, out of scope, key test/harness cases, key verification commands, open decisions, and readiness status. It is the user's fast review path and must stay synchronized with the detailed child contract.

For Parent/Child work, the Child Index is the operational control surface. A hardening run must read it when present and update it when editing shared control artifacts is in scope. The Child Index row must include or receive a `Session Handoff` pointer for the child before implementation can be allowed. If the lane may not edit shared files, report the exact integration-owner patch and use `NEEDS PARENT/ORCHESTRATOR SYNC` until the child spec, Child Index/queue state, and handoff pointer agree.

Child hardening is not predecessor closeout. Treat parent specs, slice plans, accepted predecessor children, and existing OpenSpec archives as read-only unless the user explicitly asks for an integration-owner or closeout-sync run. If stale predecessor or parent/slice-plan status is discovered, report the exact sync patch or follow-up instead of silently changing those artifacts inside the target-child hardening run.

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
3. Child index or slice plan.
4. Accepted prior slices and their verification commands.
5. Target repo/runtime conventions.
6. Existing OpenSpec artifacts, if the project uses them.
7. Parent/Child delivery ledger decision; for Spec Sizing Gate work, expect OpenSpec as the default unless explicitly overridden.

Ask only if the target child or parent cannot be inferred safely. If no Child Index exists for a Parent/Child effort, create or propose the minimal Child Index row instead of treating the child as independently ready.

## Tool Gate

This skill includes a local validator:

`/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs`

Before reporting `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES` for a Parent/Child target, run the validator from a neutral directory such as `/tmp` with absolute target-repository paths. This avoids inheriting a target repo `global.json` or SDK pin that can make the .NET 10 file-based app unavailable even when .NET 10 is installed:

```sh
cd /tmp
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index /absolute/path/to/project/_specs/2026-05-05-free-entry-v2-child-specs-index.md \
  --child S3 \
  --handoff /absolute/path/to/project/_specs/child-session-handoffs/s3-session-handoff.md
```

Use the actual project paths and child id. The validator enforces:

- exact operational Child Index columns,
- target child row exists,
- target child row uses the same stable child id supplied to the validator and handoff,
- required cells are non-empty,
- persisted handoff exists and agrees with the Child Index verdict,
- `Allowed Write-Set` is concrete and not approximate,
- obvious placeholder values do not pass as ready.

If the validator fails, do not report `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`. Use `NEEDS PARENT/ORCHESTRATOR SYNC` for Child Index/handoff schema or pointer failures, and `NEEDS HARDENING` for approximate write-set or child-spec content failures. If .NET 10 file-based app execution is unavailable in the environment, report the validator as blocked and do not claim an implementation-allowing verdict unless the user explicitly authorizes an equivalent local validator execution.

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
- an implementation write-set that is enforceable for the next `spec-change-delivery` run when the verdict may become `IMPLEMENTATION READY`,
- closeout sync targets,
- history and `SessionId`.
- a hardening verdict section or Review Control Surface verdict that can be mirrored in the Child Index.
- a persisted Child Session Handoff target, normally `child-session-handoffs/<child-id>-session-handoff.md` beside the Child Index, or an exact integration-owner patch if the current lane cannot write it.

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

Embedded machine-readable examples must be parseable when they are described as canonical, copyable, or normative. YAML, JSON, TOML, schema, manifest, or API examples that are only illustrative must be labelled as pseudo/example sketches and must not be used as canonical implementation inputs. If a normative embedded example does not parse, mark the child `NEEDS HARDENING`.

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
- command-contract rehearsal for high-risk commands when safe before implementation,
- deterministic readiness handling before endpoint assertions,
- gate verification commands,
- local and container/harness gates when the parent or predecessors require them,
- concrete success criteria for exit codes and output/artifacts,
- anti-loop rule: do not add commands that only verify the verification.

Treat these as high-risk by default: SDK/runtime selection, absolute paths, commands affected by parent `global.json` or cwd, Docker/Compose, service readiness probes, branch/diff guards, credential/secret checks, network/infra checks, and build/test commands with fragile flags such as `--no-build` or `--no-restore`.

Before reporting `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`, run safe command-contract rehearsals for high-risk verification commands. Rehearsal means proving the command contract is valid (tool/runtime selection, paths, flags, cwd/shell, daemon availability), not proving the future implementation behavior. If a high-risk command cannot be safely rehearsed, record the reason and keep a blocking marker unless a later owner and validation point are explicit. A high-risk command with no rehearsal evidence is `NEEDS HARDENING`, not a non-blocking note.

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

Do not mark a child implementation-ready just because it has the expected section headings. `IMPLEMENTATION READY` requires all of these to be true:

1. Review Control Surface and detail sections agree.
2. Parent/Master coverage and Parent Scope Conformance have no blocking gaps.
3. Decision Freeze Pack has no blocking `[MISSING ...]`, `[DECISION ...]`, or blocking `[REVIEW ...]` markers.
4. Normative Contract and Canonical Examples/Fixtures decision are deep enough for the child variant.
5. Harness/Verification Cases include the relevant positive, negative, blocked, fallback, and security/redaction cases.
6. Verification Commands include execution context, preflight when needed, gate verification, success criteria, runtime-readiness when relevant, and anti-loop rule.
7. Dependencies, allowed write-set, shared/read-only files, DoR, DoD, and Closeout Sync Targets are explicit.
8. Content-quality review has no blocking findings.
9. High-risk Verification Commands have successful command-contract rehearsal evidence, or the child remains `NEEDS HARDENING` with an explicit `[MISSING command contract rehearsal]` / `[REVIEW command contract not rehearsed: <reason>]` marker.
10. Child Index or Hardening Queue row is updated, uses the exact operational minimum column names, has no required gate hidden inside compressed/aliased substitute columns, and agrees with the child verdict.
11. A persisted Child Session Handoff is produced and the Child Index `Session Handoff` pointer links to it.
12. `Allowed Write-Set` in the Child Index, child spec, and handoff is enforceable: it names concrete paths, directories, or glob patterns and excludes shared/read-only files. It must not use uncertain language such as `voraussichtlich`, `likely`, `probably`, `expected`, `TBD`, `as needed`, `related files`, or `etc.`.
13. Hardening verification has run and passed: the `ValidateChildReadiness.cs` tool, `git diff --check`, plus parse/lint checks for embedded canonical machine-readable examples when such examples exist and local tooling is available.

If any item is missing, use `NEEDS HARDENING`, `NEEDS USER DECISION`, or `NEEDS PARENT/ORCHESTRATOR SYNC`; do not downgrade the gate into a non-blocking note. If an otherwise ready child only lacks shared Child Index or handoff-pointer sync because the current lane cannot edit shared files, report the exact integration-owner patch and use `NEEDS PARENT/ORCHESTRATOR SYNC`. If the Child Index uses compressed/aliased columns instead of the exact operational schema, use `NEEDS PARENT/ORCHESTRATOR SYNC`. If the implementation write-set is approximate, use `NEEDS HARDENING`. If `ValidateChildReadiness.cs`, `git diff --check`, or a canonical embedded example parse check fails, use `NEEDS HARDENING` or `NEEDS PARENT/ORCHESTRATOR SYNC` according to the failing gate until corrected and rechecked.

After assigning the final status, update or report the child spec's Review Control Surface so its `Offene Entscheidungen` and `Readiness Status` match the verdict.

When the verdict is `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`, always produce a persisted Child Session Handoff for the implementation run using the shared workflow template: parent path, stable child id, child spec path, child index/queue path, handoff file path, target repository / working directory, next mode/skill, current verdict, scope summary, non-goals, enforceable allowed write-set, shared/read-only files, verification commands, evidence/OpenSpec, open non-blocking notes, and whether a fresh session is recommended. Link the same handoff from the Child Index. For large Parent/Child work, prefer a fresh implementation session per child.

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
## Child Session Handoff
```

For very small governance children, a compact variant is acceptable if the omitted sections are explicitly irrelevant. For Parent/Child implementation handoff, prefer a persisted handoff file and keep only a short pointer or summary in the child spec when duplication would create drift.

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
9. Child Index / Hardening Queue update, including `Session Handoff`, or exact integration-owner patch if sync is still blocking.
10. Persisted Child Session Handoff path for an implementation-ready child.
11. Hardening verification results, including `ValidateChildReadiness.cs`, `git diff --check`, and any parse/lint checks for embedded canonical examples.
12. Any out-of-scope predecessor/parent/slice-plan sync findings reported as follow-up patches, not silently bundled into the target-child verdict.
13. Mini-Retro after substantial hardening blocks or before handoff/context loss: decisions, changes, open items, missing evidence, skill/workflow friction, and whether to continue in this session or start a new one.

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
- Do not mark `IMPLEMENTATION READY` without a documented hardening verdict, synchronized Child Index/Hardening Queue row, persisted Child Session Handoff, and matching Child Index pointer.
- Do not mark `IMPLEMENTATION READY` from a partial, compressed, or aliased Child Index row. Missing exact operational Child Index columns, renamed substitute columns, merged gate columns, or empty gate-relevant cells require `NEEDS PARENT/ORCHESTRATOR SYNC`.
- Do not mark `IMPLEMENTATION READY` while the implementation `Allowed Write-Set` is approximate, advisory, or phrased with `voraussichtlich`, `likely`, `probably`, `expected`, `TBD`, `as needed`, `related files`, or `etc.`. Use `NEEDS HARDENING` until the write-set is enforceable.
- Do not mark `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES` unless `ValidateChildReadiness.cs` passes for the target Child Index row and persisted handoff.
- Do not mark `IMPLEMENTATION READY` when `git diff --check` fails or when an embedded canonical YAML/JSON/TOML/schema/manifest example fails to parse.
- Do not mutate accepted predecessor specs, parent closeout status, slice-plan coverage, or OpenSpec archives during child hardening unless that integration/closeout sync is explicitly in scope.
- Do not leave the Child Index/Hardening Queue stale; update it or return `NEEDS PARENT/ORCHESTRATOR SYNC` with the exact integration-owner patch.
- Do not block parallel hardening just because later implementation write-sets are unknown; keep those as implementation-readiness gaps.
- Do not mark a child safe for parallel implementation when allowed runtime/code write-sets, shared/read-only runtime files, integration owner, or merge/sync order are missing.
