# DocWorkflow Calibration: S3 Hardening Review Feedback

## Context

This report records the process-level lessons from reviewing a real KI-fuer-KMU S3 child-spec-hardening run. The goal is not to fix KI-fuer-KMU from this repository, but to harden the shared DocWorkflow and skills so future Parent/Child specs produce the correct verdict automatically.

## Review Findings Converted Into Workflow Rules

### 1. Partial Child Index Cannot Support IMPLEMENTATION READY

Observed failure:

- The real S3 run marked S3 as `IMPLEMENTATION READY`.
- The Child Index only had `Slice | Spec | Status | Hardening Verdict | Session Handoff`.
- The new DocWorkflow requires the full operational row: Parent Coverage, readiness verdict, handoff, OpenSpec/ledger, dependencies, write-set, verification, evidence/closeout, backlog/re-entry, and next action.

Process change:

- `docs/doc-workflow.md`, `spec-orchestrator`, `child-spec-hardening`, and `spec-change-delivery` now state that a partial Child Index is only a migration intermediate.
- A child with a partial index must use `NEEDS PARENT/ORCHESTRATOR SYNC`, not `IMPLEMENTATION READY`.

### 2. Contract-Heavy Canonical Examples Must Parse

Observed failure:

- S3 contained a canonical embedded YAML example that did not parse.
- Because S3 is contract-heavy, implementers and fixtures may copy those examples.

Process change:

- Contract-heavy embedded YAML/JSON/TOML/schema/manifest examples described as canonical, copyable, or normative must parse.
- Non-parseable examples must be clearly labelled as pseudo/sketch/excerpt and cannot be the canonical implementation source.
- Parse failures block readiness with `NEEDS HARDENING`.

### 3. Hardening Verification Must Actually Be Green

Observed failure:

- The S3 run claimed `git diff --check` as hardening verification, but the resulting worktree failed `git diff --check`.

Process change:

- `child-spec-hardening` now requires `git diff --check` before `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`.
- If `git diff --check` fails, the verdict is `NEEDS HARDENING`.

### 4. Child Hardening Is Not Predecessor Closeout

Observed failure:

- The S3 hardening run also touched S2 closeout/OpenSpec/archive, parent status, and the slice plan.
- That may be legitimate in a separate integration-owner sync, but it should not be silently bundled into target-child hardening.

Process change:

- `child-spec-hardening` now treats parent specs, slice plans, accepted predecessor children, and OpenSpec archives as read-only unless the user explicitly requests integration/closeout sync.
- Stale predecessor or parent/slice-plan status should be reported as a follow-up patch, not silently changed inside the target-child verdict.

## Expected Future Behavior

A future S3-like child hardening run should:

1. Upgrade or patch the Child Index to the full operational schema before claiming readiness.
2. Parse or explicitly de-scope embedded canonical machine-readable examples.
3. Run and report `git diff --check`.
4. Keep predecessor closeout and parent/slice-plan sync out of scope unless explicitly requested.
5. Return `NEEDS PARENT/ORCHESTRATOR SYNC` or `NEEDS HARDENING` instead of optimistic `IMPLEMENTATION READY` when any of these gates fail.
