from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass
from typing import Protocol

from github_issue_pilot.implementation import Worktree


@dataclass(frozen=True)
class DeterministicVerification:
    command: str
    head_sha: str
    passed: bool
    exit_code: int
    observed: str

    def as_dict(self) -> dict[str, object]:
        return {
            "command": self.command,
            "head_sha": self.head_sha,
            "passed": self.passed,
            "exit_code": self.exit_code,
            "observed": self.observed,
        }


class DeterministicVerifierPort(Protocol):
    def verify(
        self,
        worktree: Worktree,
        *,
        command: str,
        head_sha: str,
    ) -> DeterministicVerification: ...


class CommandDeterministicVerifier:
    def __init__(self, *, timeout_seconds: float = 3600, git_executable: str = "git") -> None:
        self._timeout_seconds = timeout_seconds
        self._git_executable = git_executable

    def verify(
        self,
        worktree: Worktree,
        *,
        command: str,
        head_sha: str,
    ) -> DeterministicVerification:
        if not command.strip():
            raise ValueError("verification command must not be empty")
        if re.fullmatch(r"[0-9a-f]{40}", head_sha) is None:
            raise ValueError("verification head must be a full commit SHA")
        current_head = self._git(worktree, "rev-parse", "HEAD")
        if current_head != head_sha:
            return DeterministicVerification(
                command=command,
                head_sha=head_sha,
                passed=False,
                exit_code=-1,
                observed="worktree_head_mismatch",
            )
        if self._git(worktree, "status", "--porcelain"):
            return DeterministicVerification(
                command=command,
                head_sha=head_sha,
                passed=False,
                exit_code=-1,
                observed="worktree_not_clean",
            )
        try:
            completed = subprocess.run(
                shlex.split(command),
                cwd=worktree.path,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
            )
            exit_code = completed.returncode
            observed = "\n".join(
                part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
            )[-4000:] or f"exit_code={exit_code}"
        except subprocess.TimeoutExpired:
            exit_code = -1
            observed = "verification_timed_out"
        except OSError:
            exit_code = -1
            observed = "verification_command_failed_to_start"
        if self._git(worktree, "rev-parse", "HEAD") != head_sha:
            return DeterministicVerification(
                command=command,
                head_sha=head_sha,
                passed=False,
                exit_code=exit_code,
                observed="verification_changed_head",
            )
        if self._git(worktree, "status", "--porcelain"):
            return DeterministicVerification(
                command=command,
                head_sha=head_sha,
                passed=False,
                exit_code=exit_code,
                observed="verification_mutated_worktree",
            )
        return DeterministicVerification(
            command=command,
            head_sha=head_sha,
            passed=exit_code == 0,
            exit_code=exit_code,
            observed=observed,
        )

    def _git(self, worktree: Worktree, *args: str) -> str:
        return subprocess.run(
            [self._git_executable, "-C", str(worktree.path), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
