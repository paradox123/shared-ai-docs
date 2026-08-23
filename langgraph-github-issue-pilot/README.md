# LangGraph GitHub Issue Pilot

This package implements the local repository control plane: it accepts authenticated direct or Cloudflare-relayed GitHub deliveries, persists them in SQLite, evaluates the complete authorized and unblocked backlog through a versioned repository adapter, serializes one persistent LangGraph implementation run per repository, and exposes durable workflow state. Claimed issues become bounded evidence-aware assignments executed by Codex CLI in isolated Git worktrees; a successful implementation is promoted only when criterion-level behavioral evidence qualifies, then committed, pushed, and projected as one draft pull request. That exact draft head is reviewed by three fresh, independent, read-only requirements, code-quality, and architecture workers. Actionable failed-axis findings return only to the same writing implementer for at most three committed, deterministically verified, fully re-reviewed repair rounds before verification or explicit human handoff.

The only live adapter is `probare-crm`. Repository-specific label names, accepted webhook events, provenance and parent/PRD relationships, issue dependencies, human-merge state, and GitHub label projections are contained behind `RepositoryAdapter` version `1`. The workflow core does not branch on a repository name. A second adapter is used only by the behavior contract tests.

## Run locally

Install the locked environment:

```bash
uv sync
```

Provide secrets and repository configuration outside the repository, then start the loopback receiver:

```bash
export PILOT_DATABASE_PATH="$PWD/pilot.db"
export PILOT_ALLOWED_REPOSITORIES="OWNER/probare-crm"
export GITHUB_WEBHOOK_SECRET="..."
export GITHUB_TOKEN="..."
export DANIEL_GITHUB_LOGIN="YOUR_GITHUB_LOGIN"
export PILOT_REPOSITORY_ROOT="/path/to/probare-crm"
export PILOT_WORKTREE_ROOT="/path/to/pilot-worktrees"
export PILOT_REPOSITORY_CONTEXT_PATH="$PILOT_REPOSITORY_ROOT/AGENTS.md"
export PILOT_PUBLIC_OBSERVATION_SURFACE="HTTP API and browser behavior"
export PILOT_VERIFICATION_COMMAND="uv run pytest"
export PILOT_SKILL_ROOT="$PWD/../skills-repo/vendor/mattpocock/.agents/skills"
uv run github-issue-pilot
```

For Cloudflare relay operation, configure the independent second-hop secret instead of the GitHub webhook secret:

```bash
unset GITHUB_WEBHOOK_SECRET
export PILOT_INTERNAL_WEBHOOK_SECRET="..."
uv run github-issue-pilot
```

Exactly one of `GITHUB_WEBHOOK_SECRET` and `PILOT_INTERNAL_WEBHOOK_SECRET` must be set. Relay signatures bind `X-GitHub-Delivery`, `X-GitHub-Event`, and the unchanged raw body. The two hop secrets must be different and must not be committed or logged.

The implementation pilot currently accepts exactly one configured repository. `PILOT_WORKTREE_ROOT` must be disjoint from `PILOT_REPOSITORY_ROOT`. The context file is the only configured repository guidance copied into the worker assignment; secrets, webhook payloads, and previous Codex sessions are not included.

Optional runtime settings are:

- `PILOT_BASE_REF` (default `main`)
- `PILOT_CODEX_EXECUTABLE` (default `codex`)
- `PILOT_CODEX_TIMEOUT_SECONDS` (default `3600`)
- `PILOT_GIT_EXECUTABLE` (default `git`)
- `PILOT_HOST`, `PILOT_PORT`, and `PILOT_MAX_REQUEST_BYTES`

The implementer runs non-interactively with the packaged node policy (`gpt-5.6-terra`, `xhigh`, `workspace-write`), a run-owned `codex/run-<run-id>` branch, issue-type skill hashes, and the packaged worker-result v2 JSON Schema. Invalid or failed results remain attached to the run as failures and are not promoted to a pull request. Repair assignments use separate versioned contracts, the same worker port, skills, worktree, and branch, plus a hard per-initial-review limit of three numbered rounds. Rounds one and two use Terra unless an allowed material or structured escalation applies; round three records `final_repair_round` and uses `gpt-5.6-sol`, `xhigh`, with the same bounded implementer write root.

After draft publication, three separate `codex exec` processes review the same immutable head with `gpt-5.6-terra`, `xhigh`, and `read-only`. Requirements and code quality use the separate spec and standards axes of `code-review`; architecture uses `codebase-design` and `domain-modeling`. Every schema-valid verdict retains its invocation ID, reviewed SHA, rationale, concrete findings, policy, and skill hashes. Requirements cannot be `not_applicable`. Invalid, missing, or stale-head output still fails closed. A schema-valid `fail` with actionable findings starts the bounded repair loop: each completed repair must create a new pushed head, update the existing draft PR, run `PILOT_VERIFICATION_COMMAND` on that exact clean commit, and execute all three reviews again even when the deterministic check fails. Only a passing deterministic check plus all applicable fresh reviews add `verified` and `awaiting-review` and remove `agent-running`.

Repair assignments authorize small reversible implementation and presentation details within existing guidance. Warnings, consent, domain actions, security meaning, and other semantic behavior remain product decisions. Genuine product/scope questions, missing access, unavoidable manual evidence, or non-agentic conflicts can stop repair. After three unsuccessful rounds, a structured missing-or-contradictory-requirements classification projects `needs-info`; other unresolved conflicts project `ready-for-human`. The existing draft PR retains the ordered attempts and open findings, loses `agent-running`, and is never merged, deployed, or released by the pilot.

Publication requires exactly one passing evidence item per acceptance criterion. REST items require request, relevant response, and business read-back; UI items require executed interaction and a decisive screenshot reference; recovery and idempotency require restart/repetition plus public read-back; negative gates require rejection plus proof that the forbidden side effect is absent; background work requires the eventually observable business result. Builds, process/container starts, healthchecks, naked status codes, enqueue success, static starting screenshots, and log claims are rejected as sole evidence. Correlated logs remain supplemental.

Before publication, worker evidence and diagnostics redact the configured GitHub/webhook secrets plus recognizable tokens, authorization values, credential fields, and email addresses. The outgoing diff is scanned for the same material and fails closed rather than rewriting source. The Git adapter uses the worktree's `origin`, creates `Implement issue #<number>` only when the worker left uncommitted changes, pushes the explicit run branch, and supplies the observed head SHA to the PR renderer. A branch with no implementation commit is not published.

The receiver listens on `127.0.0.1:8788` by default. It exposes:

- `POST /webhooks/github`
- `GET /workflows/{owner}/{repository}/issues/{issue_number}`

On startup, before the receiver accepts new deliveries, it scans the same SQLite database for non-terminal runs and reconciles their existing LangGraph thread and durable phase records. Claim, implementation, publication, review, repair, and human-feedback continuation reuse the run-owned worktree, branch, pull request, current head, batch, round, and invocation identities. A completed transition is read from its durable record instead of being executed again; an operation interrupted without a valid result is retried only under the same durable identity and bounded write context. A valid existing Git worktree for the deterministic run path is adopted after restart rather than replaced.

Before that ordinary crash recovery, startup evaluates a durable local `last_alive_at` against a stable operating-system boot identity. The production resolver derives an opaque boot-session ID from macOS `kern.boottime` (and supports the Linux kernel boot ID for development). The first-ever recorded start establishes liveness and does not guess an offline interval. On the first process start of each later boot, an interval of exactly 24 hours or more starts one durable current-state reconciliation; a shorter interval records `not_required`. Process restarts in the same boot reuse that evaluation. If reconciliation was interrupted, the restart resumes its existing `running` boot record instead of allocating another run.

A qualifying reconciliation reads current ready or otherwise authorized open issues and the current pull request for the persisted active run through the repository adapter. A valid human-merged active PR is processed before ready backlog work. Missing readiness and merge facts become deterministic synthetic deliveries in the ordinary SQLite inbox and go through the same workflow dispatcher as webhooks. The inbox stores transport receipts separately from semantic command identities, so a synthetic command and a delayed Cloudflare Queue delivery for the same issue-ready or exact-head merge fact produce one workflow effect in either order. A late real delivery is still persisted and receives `already_accepted`; reusing its `X-GitHub-Delivery` with different content remains a conflict.

After startup completes, there is no reconciliation timer and no periodic GitHub polling. A local heartbeat updates only SQLite once per minute and again on graceful shutdown so a later boot can measure the last durable proof of life. Workflow read-back includes the latest boot reconciliation ID, threshold outcome, status, prior/current liveness timestamps, measured offline seconds, and discovered/accepted/deduplicated command counts. These records exclude webhook and GitHub bodies, feedback, tokens, email addresses, and arbitrary external exception text.

Recovery never activates a run whose human-merge completion is terminal. A published run with no incomplete machine transition remains waiting for new human feedback or merge activity and does not start a worker, review, push, or label projection merely because the process restarted.

Exactly one repository must be configured and its name must be `probare-crm`. The GitHub token needs read/write issue and pull-request access because the adapter reads the complete issue backlog, parent/PRD provenance, dependencies, issue timelines, human merge state, and current PR head; idempotently projects workflow labels; and creates or updates one draft pull request for the run branch. Do not commit the database, webhook secret, login, or token.

Candidates are ordered by issue number. `ready-for-agent` is the only start authorization and applies to every issue type. Without that label, only a Daniel-authored issue, a linked Daniel-authored PRD, or a Daniel-rooted parent chain can inherit authorization. Every blocker requires both a human-merged implementation pull request and a closed blocker issue. A queued successor starts only after the active run satisfies the same two completion facts.

Workflow read-back includes the durable assignment, planned evidence, worktree identity, policy selection, skill provenance, access profile, redacted JSONL diagnostics, the validated result or redacted failure, `draft_pull_request`, `review`, `repair`, `human_feedback`, and `recovery`. A published draft record includes its PR identity, branch, current exact head SHA, complete redacted evidence package, canonical body, and timestamps. The review record exposes the latest three independent assignments/verdicts and their policy/routing provenance, aggregation reason, reviewed head, projected labels, and timestamps across restart. The repair record preserves the initial review identity, limit/count, ordered assignments and invocations, policies, skills, access profiles, results, diagnostics, committed heads, deterministic checks, linked review batches, open findings, terminal state, and label projection. Recovery exposes only generated event ID, phase, stable operation key, bounded outcome code, and timestamp. It never stores webhook bodies, assignments, feedback copies, source payloads, arbitrary exception text, tokens, credentials, authorization values, or email addresses. An insufficient evidence package or non-actionable blocked review instead exposes a stable reason without forbidden success effects.

Cloudflare Queue, retry, DLQ, and named Tunnel setup is documented in `../cloudflare-github-webhook-relay/README.md`.

## Verify

```bash
uv run pytest
uvx ruff check .
uv lock --check
```

The suite drives sufficient and deliberately insufficient evidence packages plus blocked, successful, stale-head, repaired, three-round-exhausted, `needs-info`, `ready-for-human`, and restart-safe batches through the signed HTTP interface with real SQLite and LangGraph persistence. Subprocess system cases forcibly terminate the process after durable claim, implementation, publication, review, repair, and feedback boundaries, then reconstruct a new application process on the same files and prove via HTTP read-back and controlled boundary counts that only missing work continues. Separate boundary contracts use real temporary Git repositories, fake Codex executables, an exact-head deterministic command verifier, and a controlled GitHub HTTP transport.
