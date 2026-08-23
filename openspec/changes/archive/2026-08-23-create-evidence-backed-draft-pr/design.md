## Context

The persistent workflow already turns a claimed issue into a bounded assignment, creates a run-owned worktree, invokes Codex through a replaceable worker port, validates a versioned result, and exposes that result through the productive HTTP read model. It deliberately stops before Git commit/push and pull-request mutation. Issue 03 adds that promotion boundary while preserving one active run per repository and keeping merge, deployment, and reviews outside this slice.

Worker evidence is currently only an unstructured criterion/proof pair. That shape cannot distinguish a direct behavioral read-back from a healthcheck, cannot prove negative side-effect absence or eventual background results, and cannot safely render a commit-bound PR body. Git and GitHub are external boundaries; SQLite and LangGraph checkpointing remain real infrastructure in workflow tests.

## Goals / Non-Goals

**Goals:**

- Validate one complete, typed, criterion-level behavioral evidence package before GitHub publication.
- Reject deliberately insufficient packages without committing, pushing, or creating a pull request.
- Commit and push the run-owned worktree, obtain the exact head SHA, and create or recover exactly one draft pull request for the issue.
- Render a compact canonical PR body with the full acceptance matrix and decisive redacted evidence embedded at the relevant criterion.
- Persist the publication outcome, head binding, pull-request identity, body, and rejection reason for HTTP read-back across process restart.
- Exercise orchestration through the signed webhook and workflow-state endpoints, controlling only Git/GitHub and worker boundaries.

**Non-Goals:**

- Requirements, code, or architecture review; `verified`/`awaiting-review` labels; findings repair; human feedback; merge; deployment; or release.
- General workflow crash reconciliation beyond idempotent draft-PR lookup by run branch; broader resume semantics belong to Issue 08.
- Uploading new binary screenshot assets to GitHub. Workers provide repository-relative or already-published safe image references; the renderer embeds those references.
- Proving the actual feature implemented by a fake test repository. The behavior test proves the pilot's evidence gate and publication transition; live feature evidence remains the worker's responsibility.

## Decisions

### Promote only a versioned structured evidence result

Add `worker-result-v2.json` and select it in the Codex adapter. Each evidence item names exactly one acceptance criterion, a `pass` verdict, evidence kind, observed interface, expected result, and typed observations. Observation phases provide the minimum semantic vocabulary needed for REST request/response/read-back, UI interaction/screenshot, recovery restart/read-back, idempotent repeat/read-back, negative rejection/side-effect read-back, and background eventual result. Correlated logs may supplement any item but never satisfy a required phase.

The evidence gate validates schema, exact criterion coverage with no duplicates, all-pass verdicts, and kind-specific phase requirements. It rejects known infrastructure-surrogate-only descriptions and missing inline artifacts for decisive responses/screenshots/log excerpts. This is deliberately stricter than accepting free-form proof prose.

Alternative considered: infer evidence quality from the current free-form `proof` string. That would be brittle, impossible to validate reliably, and unable to render a stable matrix.

### Separate evidence qualification, source publication, and PR projection

The workflow adds a `publish_draft_pr` node after successful worker execution. A pure evidence qualifier/redactor returns a safe package or a typed rejection. A replaceable `SourceControlPort` owns changed-diff inspection, commit, head resolution, and push. The repository adapter owns `ensure_draft_pull_request`, which reuses an existing open pull request for the run branch or creates one when absent.

The production Git adapter stages the run worktree, scans only the outgoing staged diff plus configured sensitive values, creates a fixed issue-scoped commit when changes remain, verifies the branch is ahead of its base, pushes the explicit run branch, and returns the 40-character head SHA. The GitHub HTTP adapter queries by head branch before POSTing a draft PR, making the external operation idempotent under retry.

Alternative considered: shell out to `gh pr create` from the graph. A dedicated port keeps credentials and API behavior at the GitHub boundary, supports deterministic contract tests, and gives the controller an explicit idempotency contract.

### Bind body rendering to the observed pushed head

Evidence is qualified before source publication, then the returned pushed head SHA is injected into every matrix row and the body header. The renderer never accepts a caller-supplied SHA from worker output. The stored publication record contains the same SHA, body, URL, PR number, and draft state returned by the adapter.

Any later commit necessarily produces a different SHA and therefore cannot match the stored package. Revalidation after later commits belongs to Issues 06/08, but stale evidence is already distinguishable and cannot be represented as current by this slice.

Alternative considered: include only the branch name. Branches move; a SHA is the immutable review binding required by the domain language.

### Redact output and fail closed on branch leakage

The redactor replaces configured secret values, authorization headers, GitHub-style tokens, email addresses, and obvious credential fields in evidence descriptions, artifacts, diagnostic excerpts, and PR text before persistence or publication. The schema excludes raw request payloads in favor of compact excerpts. Source publication scans the outgoing diff for configured secrets, token forms, authorization values, and email addresses; a match blocks commit/push rather than silently rewriting source code.

Errors persisted to the workflow use stable redacted categories, not subprocess stderr or raw evidence. The fixed commit message and branch name include only the issue/run identity.

Alternative considered: redact source files automatically. Silent source mutation could break the implementation or conceal a security flaw, so branch leakage fails closed.

### Persist one publication record per run

Add a one-to-one `draft_pr_publications` record keyed by run ID with `rejected`, `publishing`, or `published` status. Evidence rejection is stored with a safe reason and no Git/GitHub effects. Successful publication stores qualified evidence, head SHA, rendered body, PR identity, and timestamps. The HTTP workflow read model exposes this record under `draft_pull_request` and survives application reconstruction against the same database.

The existing duplicate-delivery rule prevents graph reinvocation. The GitHub adapter's head-branch lookup is the second line of defense if publication is retried after an ambiguous network outcome.

Alternative considered: rely only on the LangGraph checkpoint. The durable domain record is easier to query, constrains uniqueness directly, and does not expose graph internals.

## Risks / Trade-offs

- [A worker can misstate an observation even when its shape is valid] → Require direct typed observations, bind them to the pushed head, and leave independent review of truthfulness to Issue 04.
- [A screenshot reference may not render outside the source repository] → Require an inline Markdown-safe reference and retain it adjacent to the UI criterion; binary upload support can be added behind the PR adapter later.
- [Regex redaction can over-redact harmless email-like or token-like strings] → Prefer safe review output and fail closed for outgoing source diffs; make configured exact secrets additive to conservative built-ins.
- [Git commit succeeds locally but push or PR creation fails] → Persist `publishing` until the operation completes, use a fixed run branch, and let GitHub PR lookup recover an ambiguous create; full automatic restart continuation remains Issue 08.
- [GitHub's PR body size limit can be exceeded by verbose evidence] → Keep schema excerpts compact, reject oversized rendered bodies before the GitHub call, and embed references rather than binary data.

## Migration Plan

1. Add the v2 worker-result contract, evidence validator/redactor/renderer, source-control port, and idempotent draft-PR adapter behavior.
2. Add the publication table with `CREATE TABLE IF NOT EXISTS`; existing runs remain readable with `draft_pull_request: null` and are not retroactively published.
3. Configure the Git executable and optional exact sensitive values alongside existing implementation services; reuse the repository adapter's GitHub credentials.
4. Deploy the extended graph for newly claimed issues. Rollback uses the previous runtime; the additive table and already-created draft PRs remain inspectable and are never merged automatically.

## Open Questions

None for this slice. Screenshot asset upload, crash-time continuation, revalidation after human commits, and review labels are assigned to later issues.
