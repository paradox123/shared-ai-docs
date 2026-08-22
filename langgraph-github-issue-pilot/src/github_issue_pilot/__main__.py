from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

from github_issue_pilot.app import create_app
from github_issue_pilot.github import GitHubHttpAdapter


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
    github = GitHubHttpAdapter(_required_environment("GITHUB_TOKEN"))
    github_webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").strip()
    internal_webhook_secret = os.environ.get("PILOT_INTERNAL_WEBHOOK_SECRET", "").strip()
    try:
        app = create_app(
            database_path=Path(_required_environment("PILOT_DATABASE_PATH")),
            webhook_secret=github_webhook_secret.encode() if github_webhook_secret else None,
            internal_webhook_secret=internal_webhook_secret.encode() if internal_webhook_secret else None,
            allowed_repositories=repositories,
            github=github,
            clock=lambda: datetime.now(UTC),
            max_request_bytes=int(os.environ.get("PILOT_MAX_REQUEST_BYTES", "1048576")),
        )
        uvicorn.run(
            app,
            host=os.environ.get("PILOT_HOST", "127.0.0.1"),
            port=int(os.environ.get("PILOT_PORT", "8788")),
        )
    finally:
        github.close()


if __name__ == "__main__":
    main()
