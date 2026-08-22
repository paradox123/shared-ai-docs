# LangGraph GitHub Issue Pilot

This package implements the local repository control plane: it accepts authenticated GitHub deliveries, persists them in SQLite, evaluates the complete authorized and unblocked backlog through a versioned repository adapter, serializes one persistent LangGraph implementation run per repository, and exposes durable workflow state.

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
uv run github-issue-pilot
```

The receiver listens on `127.0.0.1:8788` by default. It exposes:

- `POST /webhooks/github`
- `GET /workflows/{owner}/{repository}/issues/{issue_number}`

Exactly one repository must be configured and its name must be `probare-crm`. The GitHub token needs read/write issue access and pull-request read access because the adapter reads the complete issue backlog, parent/PRD provenance, dependencies, issue timelines, and human merge state, and idempotently adds `ready-for-agent` or `agent-running`. Do not commit the database, webhook secret, login, or token.

Candidates are ordered by issue number. `ready-for-agent` is the only start authorization and applies to every issue type. Without that label, only a Daniel-authored issue, a linked Daniel-authored PRD, or a Daniel-rooted parent chain can inherit authorization. Every blocker requires both a human-merged implementation pull request and a closed blocker issue. A queued successor starts only after the active run satisfies the same two completion facts.

## Verify

```bash
uv run pytest
```
