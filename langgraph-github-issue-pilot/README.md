# LangGraph GitHub Issue Pilot

This package implements the local repository control plane: it accepts authenticated direct or Cloudflare-relayed GitHub deliveries, persists them in SQLite, evaluates the complete authorized and unblocked backlog through a versioned repository adapter, serializes one persistent LangGraph implementation run per repository, and exposes durable workflow state. Claimed issues become bounded evidence-aware assignments executed by Codex CLI in isolated Git worktrees.

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
- `PILOT_HOST`, `PILOT_PORT`, and `PILOT_MAX_REQUEST_BYTES`

The implementer runs non-interactively with the packaged node policy (`gpt-5.6-terra`, `xhigh`, `workspace-write`), a run-owned `codex/run-<run-id>` branch, issue-type skill hashes, and the packaged worker-result JSON Schema. Invalid or failed results remain attached to the run as failures and are not promoted to a pull request.

The receiver listens on `127.0.0.1:8788` by default. It exposes:

- `POST /webhooks/github`
- `GET /workflows/{owner}/{repository}/issues/{issue_number}`

Exactly one repository must be configured and its name must be `probare-crm`. The GitHub token needs read/write issue access and pull-request read access because the adapter reads the complete issue backlog, parent/PRD provenance, dependencies, issue timelines, and human merge state, and idempotently adds `ready-for-agent` or `agent-running`. Do not commit the database, webhook secret, login, or token.

Candidates are ordered by issue number. `ready-for-agent` is the only start authorization and applies to every issue type. Without that label, only a Daniel-authored issue, a linked Daniel-authored PRD, or a Daniel-rooted parent chain can inherit authorization. Every blocker requires both a human-merged implementation pull request and a closed blocker issue. A queued successor starts only after the active run satisfies the same two completion facts.

Workflow read-back includes the durable assignment, planned evidence, worktree identity, policy selection, skill provenance, access profile, JSONL diagnostics, and the validated result or redacted failure.

Cloudflare Queue, retry, DLQ, and named Tunnel setup is documented in `../cloudflare-github-webhook-relay/README.md`.

## Verify

```bash
uv run pytest
uvx ruff check .
uv lock --check
```

The suite drives orchestration through the signed HTTP interface with real SQLite and LangGraph persistence. Separate boundary contracts use a real temporary Git repository and a fake Codex executable.
