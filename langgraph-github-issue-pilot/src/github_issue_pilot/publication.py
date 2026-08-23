from __future__ import annotations

import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from github_issue_pilot.evidence import contains_sensitive_text

if TYPE_CHECKING:
    from github_issue_pilot.implementation import Worktree


class SourcePublicationError(RuntimeError):
    pass


@dataclass(frozen=True)
class PublishedHead:
    branch: str
    head_sha: str


class SourceControlPort(Protocol):
    def publish(
        self,
        worktree: Worktree,
        *,
        issue_number: int,
        sensitive_values: Sequence[str] = (),
    ) -> PublishedHead: ...


class GitSourceControl:
    def __init__(self, *, git_executable: str = "git", remote: str = "origin") -> None:
        self._git_executable = git_executable
        self._remote = remote

    def publish(
        self,
        worktree: Worktree,
        *,
        issue_number: int,
        sensitive_values: Sequence[str] = (),
    ) -> PublishedHead:
        if issue_number <= 0:
            raise ValueError("issue number must be positive")
        if re.fullmatch(r"codex/[A-Za-z0-9._-]+", worktree.branch) is None:
            raise SourcePublicationError("unsafe_branch")
        try:
            current_branch = self._git(worktree, "branch", "--show-current")
            if current_branch != worktree.branch:
                raise SourcePublicationError("worktree_branch_mismatch")
            self._git(worktree, "add", "--all")
            outgoing_diff = "\n".join(
                (
                    self._git(
                        worktree,
                        "diff",
                        "--no-ext-diff",
                        "--binary",
                        f"{worktree.base_ref}...HEAD",
                    ),
                    self._git(worktree, "diff", "--cached", "--no-ext-diff", "--binary"),
                )
            )
            if contains_sensitive_text(outgoing_diff, sensitive_values):
                raise SourcePublicationError("sensitive_diff")

            staged_names = self._git(worktree, "diff", "--cached", "--name-only")
            if staged_names:
                self._git(worktree, "commit", "-m", f"Implement issue #{issue_number}")
            ahead_count = int(
                self._git(worktree, "rev-list", "--count", f"{worktree.base_ref}..HEAD")
            )
            if ahead_count < 1:
                raise SourcePublicationError("no_implementation_commit")
            head_sha = self._git(worktree, "rev-parse", "HEAD")
            if re.fullmatch(r"[0-9a-f]{40}", head_sha) is None:
                raise SourcePublicationError("invalid_head")
            self._git(
                worktree,
                "push",
                self._remote,
                f"HEAD:refs/heads/{worktree.branch}",
            )
            return PublishedHead(branch=worktree.branch, head_sha=head_sha)
        except SourcePublicationError:
            raise
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            raise SourcePublicationError("git_operation_failed") from exc

    def _git(self, worktree: Worktree, *args: str) -> str:
        return subprocess.run(
            [self._git_executable, "-C", str(worktree.path), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
