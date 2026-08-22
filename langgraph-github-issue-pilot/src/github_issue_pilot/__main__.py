from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

from github_issue_pilot.app import create_app
from github_issue_pilot.github import (
    ConfiguredRepositoryAdapter,
    GitHubHttpAdapter,
    RepositorySettings,
)

PROBARE_CRM_EVENTS = frozenset(
    {
        ("issues", "opened"),
        ("issues", "edited"),
        ("issues", "labeled"),
        ("issues", "unlabeled"),
        ("issues", "reopened"),
        ("issues", "closed"),
        ("pull_request", "opened"),
        ("pull_request", "synchronize"),
        ("pull_request", "closed"),
        ("pull_request_review", "submitted"),
        ("pull_request_review", "dismissed"),
        ("pull_request_review_comment", "created"),
        ("pull_request_review_comment", "edited"),
        ("issue_comment", "created"),
        ("issue_comment", "edited"),
    }
)


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is missing: {name}")
    return value


def main() -> None:
    repositories = {
        repository.strip()
        for repository in _required_environment("PILOT_ALLOWED_REPOSITORIES").split(",")
        if repository.strip()
    }
    if len(repositories) != 1:
        raise RuntimeError("the pilot requires exactly one configured probare-crm repository")
    repository = next(iter(repositories))
    if repository.rsplit("/", maxsplit=1)[-1] != "probare-crm":
        raise RuntimeError("the only live pilot repository must be named probare-crm")
    github = GitHubHttpAdapter(
        _required_environment("GITHUB_TOKEN"),
        human_login=_required_environment("DANIEL_GITHUB_LOGIN"),
    )
    adapter = ConfiguredRepositoryAdapter(
        github,
        RepositorySettings(
            repository=repository,
            allowed_event_actions=PROBARE_CRM_EVENTS,
        ),
    )
    app = create_app(
        database_path=Path(_required_environment("PILOT_DATABASE_PATH")),
        webhook_secret=_required_environment("GITHUB_WEBHOOK_SECRET").encode(),
        repository_adapters={repository: adapter},
        clock=lambda: datetime.now(UTC),
        max_request_bytes=int(os.environ.get("PILOT_MAX_REQUEST_BYTES", "1048576")),
    )
    try:
        uvicorn.run(
            app,
            host=os.environ.get("PILOT_HOST", "127.0.0.1"),
            port=int(os.environ.get("PILOT_PORT", "8788")),
        )
    finally:
        github.close()


if __name__ == "__main__":
    main()
