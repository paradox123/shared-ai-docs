# LangGraph GitHub Issue Pilot

This package implements the first local pilot slice: accept an authenticated GitHub issue delivery, persist it in SQLite, claim one eligible issue as a persistent LangGraph run, and expose the resulting workflow state.

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
uv run github-issue-pilot
```

The receiver listens on `127.0.0.1:8788` by default. It exposes:

- `POST /webhooks/github`
- `GET /workflows/{owner}/{repository}/issues/{issue_number}`

The GitHub token needs read/write issue access because the workflow reads issue labels and blockers and adds `agent-running`. Do not commit the database, webhook secret, or token.

## Verify

```bash
uv run pytest
```
