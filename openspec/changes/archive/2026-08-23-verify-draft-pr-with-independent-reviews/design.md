## Context

The persistent pilot already publishes one evidence-qualified draft pull request whose body, evidence package, source branch, and exact head SHA are durable and observable through the signed HTTP workflow seam. The implementation worker is replaceable, policy-controlled, and writable only inside its run-owned worktree. The workflow currently ends at draft publication and has no reviewer contracts, review persistence, aggregation, or successful-review label projection.

Issue 04 inserts a review boundary after publication. The three perspectives have different contracts and must not share conversational state or influence one another. Their common immutable input is the published PR head plus the claimed requirements, qualified evidence, repository guidance, and source diff. GitHub and Codex remain external boundaries; SQLite and LangGraph persistence remain real in workflow behavior tests.

## Goals / Non-Goals

**Goals:**

- Execute requirements, code-quality, and architecture review as three separate, fresh, read-only Codex invocations bound to one published head SHA.
- Validate and durably expose a versioned verdict for each axis, including rationale, concrete findings, model/reasoning/access policy, and skill provenance.
- Make routing explicit and contract-tested: the spec and standards axes of `code-review` remain distinct, while architecture uses `codebase-design` and `domain-modeling`.
- Aggregate fail-closed and project `verified` plus `awaiting-review` only for an unchanged head after every applicable axis passes.
- Prove blocked and successful outcomes through the signed delivery/read-back seam and controlled Codex/GitHub boundaries.

**Non-Goals:**

- Repairing review findings or implementing the bounded three-round repair loop from Issue 05.
- Invalidating verification after later commits or handling human review feedback from Issue 06.
- Merging, deploying, releasing, or synthesizing missing product decisions.
- Running live Codex or GitHub calls in tests.

## Decisions

### Use one immutable review assignment and three isolated invocations

Add a versioned review-assignment contract derived only after draft publication. It contains the claimed requirements, repository context, qualified evidence, PR identity, base/head refs, and the adapter-observed head SHA. The workflow invokes the review worker once per fixed axis with a new invocation ID and no earlier verdicts in the input. All three invocations receive the same assignment/head and a `read-only` access profile.

The production adapter starts a separate non-interactive `codex exec` process for every axis. It uses Terra with `xhigh`, the axis-specific skill contract, the packaged verdict schema, and the existing run worktree as a read-only source view. Review instructions explicitly prohibit source edits, findings repair, merge/deploy operations, and product decisions. The enforced read-only sandbox is the authority; prompt wording is defense in depth.

Alternative considered: one reviewer that produces three sections. That shares context, permits one perspective to compensate for another, and cannot demonstrate independent execution.

### Keep axis routing declarative and provenance-bearing

Extend the packaged skill-routing contract with three review roles. Requirements receives only the spec axis of `code-review`; code quality receives only its standards axis; architecture receives `codebase-design` and `domain-modeling`. Each selected skill is resolved from the configured Matt-Pocock skill root and recorded with its content hash beside the verdict. Model, reasoning, access profile, axis, and invocation ID are persisted with the same result.

The review assignment describes the axis-specific scope: requirements compares requirements, implementation, and evidence; code quality checks repository standards and relevant code smells; architecture checks domain language, ADRs, modules, interfaces, seams, adapters, depth, and test surfaces.

Alternative considered: encode routing only in prompt prose. A declarative packaged contract makes drift detectable before worker launch and gives contract tests a stable public adapter boundary.

### Validate individual verdicts before fail-closed aggregation

Add a versioned verdict JSON Schema with `pass`, `fail`, and `not_applicable`, a non-empty rationale, and a findings list with concrete locations/descriptions. Requirements may never return `not_applicable`; code and architecture may do so when their axis genuinely does not apply. Worker failure, invalid JSON/schema, missing axis, wrong head, wrong policy/routing metadata, duplicate axis, or forbidden requirements `not_applicable` becomes a durable blocked review outcome rather than a partial success.

The deterministic aggregator preserves all three axis results. Any `fail` blocks verification. Success requires requirements `pass` and every other axis to be either `pass` or validly `not_applicable`; no verdict can override another. Findings remain advisory output for the later repair slice and are never applied by reviewers.

Alternative considered: allow a majority or supervisor verdict. That contradicts the independent axes and could hide a failed requirement or architectural boundary.

### Bind successful projection to the still-current published head

Persist one review batch keyed by run and published head, plus exactly one result per axis. Before projecting success, the repository adapter reads the current PR head and must observe the same SHA. The adapter then atomically converges workflow labels: add `verified` and `awaiting-review`, remove `agent-running`, and leave the triage label unchanged. The stored verification record includes the reviewed SHA and projected labels.

If aggregation blocks or the head differs, the workflow performs no success-label projection and exposes the safe blocked reason and separate verdicts through `GET /workflows/...`. Later-head invalidation and automatic reruns remain later slices, but stale results can never mark a different head verified.

Alternative considered: trust the stored branch name without a GitHub head read-back. Branches move, so this would permit stale verification to be projected.

### Persist review state as a durable domain record

Add additive review-batch and review-result tables with uniqueness on run/head and batch/axis. The workflow read model exposes the batch status, reviewed head, independent results, metadata, aggregation reason, and projected labels. Application reconstruction against the same database returns the same completed batch without invoking reviewers or GitHub again.

Alternative considered: store reviews only in LangGraph checkpoints. Explicit domain records enforce axis/head uniqueness and make the public read model independent of graph implementation details.

## Risks / Trade-offs

- [Three xhigh model calls increase latency and cost] → Run the independent calls from the same graph fan-out where practical and keep inputs bounded to the immutable assignment, diff, repository context, and evidence.
- [A model can claim it reviewed the wrong source] → Bind the assignment and result to the adapter-observed SHA, enforce the source working directory, and re-read the GitHub head before projection.
- [A future skill installation changes content] → Resolve and persist content hashes per invocation; reject unresolved or mismatched routing before launch.
- [Read-only sandbox support could regress] → Assert exact production CLI access arguments in boundary contracts and keep source mutation methods out of the review port.
- [GitHub label calls can partially fail] → Use the repository adapter's convergent label projection and persist verification success only after the complete projection returns.
- [Restart after model completion could duplicate review calls] → Persist the batch/results by run, head, and axis and reuse completed schema-valid results; broader crash-window reconciliation remains Issue 08.

## Migration Plan

1. Add review contracts, policy/routing selections, and the read-only review worker adapter behavior.
2. Add additive review persistence and public read-model fields; existing published runs continue to return no review batch.
3. Insert review execution and aggregation after successful draft publication, then add current-head label projection.
4. Deploy for newly published draft PRs. Rollback uses the previous graph; additive records and labels already projected remain observable and no pull request is merged or source branch changed.

## Open Questions

None for this slice. Findings repair, later-head invalidation, feedback batches, and crash-time continuation are assigned to later issues.
