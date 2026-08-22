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

For Cloudflare relay operation, configure the independent second-hop secret instead of the GitHub webhook secret:

```bash
unset GITHUB_WEBHOOK_SECRET
export PILOT_INTERNAL_WEBHOOK_SECRET="..."
uv run github-issue-pilot
```

Exactly one of `GITHUB_WEBHOOK_SECRET` and `PILOT_INTERNAL_WEBHOOK_SECRET` must be set. Relay signatures bind `X-GitHub-Delivery`, `X-GitHub-Event`, and the unchanged raw body. The two hop secrets must be different and must not be committed or logged.

The receiver listens on `127.0.0.1:8788` by default. It exposes:

- `POST /webhooks/github`
- `GET /workflows/{owner}/{repository}/issues/{issue_number}`

The GitHub token needs read/write issue access because the workflow reads issue labels and blockers and adds `agent-running`. Do not commit the database, webhook secret, or token.

Cloudflare Queue, retry, DLQ, and named Tunnel setup is documented in `../cloudflare-github-webhook-relay/README.md`.

## Verify

```bash
uv run pytest
```
