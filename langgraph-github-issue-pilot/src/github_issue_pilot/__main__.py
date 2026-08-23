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
from github_issue_pilot.implementation import (
    CodexCliWorker,
    GitWorktreeAdapter,
    ImplementationServices,
    RepositoryContext,
)
from github_issue_pilot.publication import GitSourceControl
from github_issue_pilot.review import CodexCliReviewWorker
from github_issue_pilot.verification import CommandDeterministicVerifier

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


def _implementation_services(repositories: set[str]) -> ImplementationServices:
    if len(repositories) != 1:
        raise RuntimeError("the implementation pilot requires exactly one configured repository")
    repository = next(iter(repositories))
    repository_root = Path(_required_environment("PILOT_REPOSITORY_ROOT")).expanduser().resolve()
    worktree_root = Path(_required_environment("PILOT_WORKTREE_ROOT")).expanduser().resolve()
    if repository_root.is_relative_to(worktree_root) or worktree_root.is_relative_to(repository_root):
        raise RuntimeError("PILOT_WORKTREE_ROOT and PILOT_REPOSITORY_ROOT must be disjoint")
    context_path = Path(_required_environment("PILOT_REPOSITORY_CONTEXT_PATH")).expanduser()
    instructions = context_path.read_text(encoding="utf-8").strip()
    if not instructions:
        raise RuntimeError("PILOT_REPOSITORY_CONTEXT_PATH is empty")
    sensitive_values = tuple(
        value
        for name in (
            "GITHUB_TOKEN",
            "GITHUB_WEBHOOK_SECRET",
            "PILOT_INTERNAL_WEBHOOK_SECRET",
        )
        if (value := os.environ.get(name, "").strip())
    )
    skill_root = Path(_required_environment("PILOT_SKILL_ROOT")).expanduser().resolve()
    codex_executable = os.environ.get("PILOT_CODEX_EXECUTABLE", "codex")
    codex_timeout = float(os.environ.get("PILOT_CODEX_TIMEOUT_SECONDS", "3600"))
    return ImplementationServices(
        repository_roots={repository: repository_root},
        repository_contexts={
            repository: RepositoryContext(
                base_ref=os.environ.get("PILOT_BASE_REF", "main").strip() or "main",
                instructions=instructions,
                public_observation_surface=_required_environment(
                    "PILOT_PUBLIC_OBSERVATION_SURFACE"
                ),
                verification_command=_required_environment("PILOT_VERIFICATION_COMMAND"),
            )
        },
        skill_root=skill_root,
        worktrees=GitWorktreeAdapter(worktree_root),
        worker=CodexCliWorker(
            executable=codex_executable,
            timeout_seconds=codex_timeout,
        ),
        source_control=GitSourceControl(
            git_executable=os.environ.get("PILOT_GIT_EXECUTABLE", "git"),
        ),
        reviewer=CodexCliReviewWorker(
            skill_root=skill_root,
            executable=codex_executable,
            timeout_seconds=codex_timeout,
        ),
        verifier=CommandDeterministicVerifier(
            timeout_seconds=codex_timeout,
            git_executable=os.environ.get("PILOT_GIT_EXECUTABLE", "git"),
        ),
        sensitive_values=sensitive_values,
    )


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
            base_ref=os.environ.get("PILOT_BASE_REF", "main").strip() or "main",
            allowed_event_actions=PROBARE_CRM_EVENTS,
        ),
    )
    github_webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "").strip()
    internal_webhook_secret = os.environ.get("PILOT_INTERNAL_WEBHOOK_SECRET", "").strip()
    try:
        app = create_app(
            database_path=Path(_required_environment("PILOT_DATABASE_PATH")),
            webhook_secret=github_webhook_secret.encode() if github_webhook_secret else None,
            internal_webhook_secret=internal_webhook_secret.encode() if internal_webhook_secret else None,
            repository_adapters={repository: adapter},
            clock=lambda: datetime.now(UTC),
            max_request_bytes=int(os.environ.get("PILOT_MAX_REQUEST_BYTES", "1048576")),
            implementation=_implementation_services(repositories),
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
