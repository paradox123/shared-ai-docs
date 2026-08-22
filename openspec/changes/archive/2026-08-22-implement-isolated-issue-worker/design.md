## Context

The first pilot slice accepts and claims one eligible issue, persists a LangGraph run, and exposes it through the HTTP workflow read model. The graph currently ends after projecting `agent-running`. Issue 02 must extend that same persistent run through a bounded implementation assignment, isolated Git worktree, and replaceable Codex CLI worker while keeping Daniel's checkout, sibling runs, and existing pull requests outside the worker's write surface.

The runtime is a local, single-process Python application. Git and Codex are external system boundaries; SQLite and LangGraph checkpointing remain real application infrastructure. Official Codex CLI documentation and the installed CLI expose stable non-interactive flags for model selection, config overrides, a working directory, `workspace-write`, JSONL, and JSON-schema-constrained final output.

## Goals / Non-Goals

**Goals:**

- Build and persist a versioned assignment containing exactly the issue, extracted requirements, configured repository context, a pre-implementation evidence matrix, and current findings.
- Create one run-owned Git worktree before worker execution and expose its branch/path in the workflow read model.
- Select model, reasoning, skills, and rights from versioned policy and reject unsupported combinations before process launch.
- Run the implementer through a replaceable `WorkerPort`; provide a production `codex exec` adapter using Terra/`xhigh`, the issue-type skills, `workspace-write`, JSONL, and a versioned output schema.
- Validate and persist structured Red-Green results or durable failure details on the same run.
- Prove orchestration through the productive HTTP seam and prove Git/Codex adapters through narrow boundary contract tests.

**Non-Goals:**

- Pull-request creation or mutation, deterministic project-specific verification after the worker, review agents, finding-repair rounds, merge, deployment, or release.
- Cloudflare ingress, startup reconciliation, process supervision, or concurrent implementation of multiple issues in one repository.
- Experimental Codex app-server or exec-server integration.
- Cleanup or automatic deletion of a failed run's worktree.

## Decisions

### Extend the existing graph with prepare and execute nodes

After `project_claim`, the graph prepares the assignment and worktree, then invokes the worker. Each node returns domain state that is checkpointed under the existing persisted run ID. The GET workflow read model adds one `implementation` object assembled from durable application records rather than exposing graph node names or database rows.

Alternative considered: start an unrelated subprocess from the HTTP route. That would detach worker ownership from the LangGraph run and weaken restart observation and idempotency.

### Keep assignment construction deterministic and bounded

The GitHub port returns issue title, body, type, and findings with current eligibility. Acceptance criteria are extracted from checkbox lines in the issue body. Configured repository context supplies only a base ref and explicit instructions. For each criterion, the controller creates a planned evidence entry naming the stable repository behavior seam, the criterion as expected result, and a Red-Green/direct-read-back proof plan. The assignment schema rejects additional properties, preventing accidental prompt expansion.

Alternative considered: pass the entire webhook payload, repository, conversation, or Codex session. Those inputs are neither required by the issue nor bounded enough for a reproducible worker contract.

### Use ports for worktree creation and worker execution

`WorktreePort` creates a run-owned worktree and returns its path, branch, and base ref. `WorkerPort` accepts an immutable invocation and returns untrusted structured data. Production implementations use `git worktree add` and `codex exec`; tests control only those external seams while exercising the real graph, store, assignment builder, schema validator, and HTTP read model.

Alternative considered: depend directly on Codex server APIs. The issue explicitly excludes that experimental coupling, while a process adapter is replaceable and contract-testable.

### Make model, skill, and access selection data-driven and fail closed

Versioned JSON policy maps deterministic control-plane work to no model, presentation to Luna/`medium`, regular agent work to Terra/`xhigh`, and only enumerated escalation reasons to Sol/`xhigh`. A second versioned routing map assigns `triage`, `to-tickets`, `implement` plus `tdd`, or `diagnosing-bugs` plus `tdd` by task/issue type. Access selection gives `workspace-write` only to implementation and findings-repair roles; other agent roles are read-only. Runtime overrides must equal the selected policy or validation fails before worktree or worker side effects.

Skill provenance is a SHA-256 of each routed vendored `SKILL.md` plus its logical name. A missing skill fails preparation instead of silently launching with an incomplete contract.

### Use Codex structured output and validate it again in the control plane

The CLI adapter invokes `codex exec --model <model> -c model_reasoning_effort=<effort> -c approval_policy=never --sandbox workspace-write --cd <worktree> --output-schema <schema> --output-last-message <temporary-file> --json -`. The JSON assignment is sent on stdin, and routed skill names are explicit in the instruction. The final JSON is parsed and validated by the application against the same packaged schema; completed feature/bug results must contain at least one Red-Green slice.

Alternative considered: trust exit code or free-form final prose. Neither proves schema compliance nor gives the graph stable fields for evidence and later review nodes.

### Persist execution before and after the worker boundary

The store writes assignment, evidence matrix, worktree identity, selected model/reasoning, skill provenance, and access profile before launching the worker. Success stores the validated result; exceptions, non-zero exits, or invalid results store a redacted failure and leave the worktree available for inspection. The current slice has no pull-request write port, so failed results cannot mutate an existing PR through this module.

## Risks / Trade-offs

- [A workspace-write worker can modify any file in its assigned worktree before returning invalid output] → Isolate the path and branch per run, pass no additional writable directories, persist failure, and never promote the result to a PR in this slice.
- [Git worktree creation succeeds but process launch fails] → Keep the worktree and durable failed execution for diagnosis; make replay a later recovery concern rather than deleting evidence.
- [Issue checkbox prose cannot identify a repository-specific route automatically] → The pre-worker matrix names the stable public behavior seam and proof method; the implementer refines exact commands in its structured result without changing the criterion.
- [Vendored skills change over time] → Record content hashes in every invocation and persisted execution.
- [CLI flags evolve] → Confine command construction to `CodexCliWorker` and cover it with a fake-process contract test.

## Migration Plan

1. Add idempotent SQLite tables for implementation executions; existing inbox, run, claim, and checkpoint rows remain valid.
2. Configure repository root/context, worktree root, vendored skill root, and Codex executable outside secrets.
3. Deploy the extended application; newly claimed issues create worktrees and worker executions, while previously claimed rows remain readable without retroactive launch.
4. Roll back by stopping the extended runtime and using the previous code; new tables and worktrees are inert and can be inspected or removed manually.

## Open Questions

None for this slice. Retry/resume semantics, PR promotion, reviewers, and cleanup policy belong to later issues.
