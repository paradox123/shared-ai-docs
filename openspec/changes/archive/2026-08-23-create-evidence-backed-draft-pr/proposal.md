## Why

The pilot currently stops after a schema-valid implementation result and never promotes that isolated worktree into a reviewable GitHub artifact. Daniel therefore cannot inspect criterion-level, commit-exact behavioral evidence in the pull request surface that the later review workflow depends on.

## What Changes

- Validate a completed implementation's evidence package criterion by criterion and reject infrastructure-only, uncorrelated, stale, or unredacted proof before any GitHub publication.
- Commit the validated worktree, push its run-owned branch, and create exactly one draft pull request for the claimed issue through a replaceable Git/GitHub delivery boundary.
- Render the pull-request body as the canonical evidence package: every acceptance criterion receives a verdict, observation surface, expected result, and concrete redacted proof, with decisive REST excerpts, interaction screenshots, recovery/idempotency observations, and correlated logs embedded where available.
- Bind all evidence and verdicts to the published head commit and expose the draft pull request plus validation outcome through the durable workflow read model across restart and duplicate delivery.
- Add productive-HTTP behavior coverage for both sufficient and deliberately insufficient evidence packages.

## Capabilities

### New Capabilities

- `evidence-backed-draft-pr`: Defines evidence qualification, redaction, commit/head binding, idempotent branch publication, draft pull-request creation, canonical body rendering, and durable read-back.

### Modified Capabilities

None.

## Impact

- Extends `langgraph-github-issue-pilot` workflow state, persistence, implementation contracts, Git/GitHub ports, and HTTP read-back after successful worker execution.
- Adds a versioned evidence result contract and behavior/adapter tests without introducing live GitHub calls into the test suite.
- Git commits, branch pushes, and draft pull-request creation become explicit external effects; merge, deployment, review verdicts, and verification labels remain out of scope.
- Write-set is limited to `langgraph-github-issue-pilot/`, this OpenSpec change, the new canonical capability spec, pilot documentation, and Issue 03 status/evidence.
