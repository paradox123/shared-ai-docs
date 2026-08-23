from __future__ import annotations

import subprocess
import sys

from github_issue_pilot.implementation import Worktree
from github_issue_pilot.verification import CommandDeterministicVerifier


def _committed_worktree(tmp_path) -> tuple[Worktree, str]:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.email", "pilot@example.invalid"], cwd=repository, check=True)
    subprocess.run(["git", "config", "user.name", "Pilot Test"], cwd=repository, check=True)
    tracked = repository / "feature.txt"
    tracked.write_text("committed\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.txt"], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "Initial"], cwd=repository, check=True)
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return Worktree(repository, "main", "main"), head_sha


def test_deterministic_verifier_binds_passing_command_to_clean_committed_head(tmp_path) -> None:
    worktree, head_sha = _committed_worktree(tmp_path)
    command = f'{sys.executable} -c "print(\'business behavior passed\')"'

    result = CommandDeterministicVerifier().verify(
        worktree,
        command=command,
        head_sha=head_sha,
    )

    assert result.as_dict() == {
        "command": command,
        "head_sha": head_sha,
        "passed": True,
        "exit_code": 0,
        "observed": "business behavior passed",
    }


def test_deterministic_verifier_rejects_wrong_head_without_running_command(tmp_path) -> None:
    worktree, _ = _committed_worktree(tmp_path)
    marker = worktree.path / "must-not-run"
    command = f'{sys.executable} -c "open(\'{marker}\', \'w\').write(\'ran\')"'

    result = CommandDeterministicVerifier().verify(
        worktree,
        command=command,
        head_sha="0" * 40,
    )

    assert result.passed is False
    assert result.exit_code == -1
    assert result.observed == "worktree_head_mismatch"
    assert not marker.exists()


def test_deterministic_verifier_fails_when_command_mutates_committed_source(tmp_path) -> None:
    worktree, head_sha = _committed_worktree(tmp_path)
    tracked = worktree.path / "feature.txt"
    command = f'{sys.executable} -c "open(\'{tracked}\', \'w\').write(\'mutated\')"'

    result = CommandDeterministicVerifier().verify(
        worktree,
        command=command,
        head_sha=head_sha,
    )

    assert result.passed is False
    assert result.exit_code == 0
    assert result.observed == "verification_mutated_worktree"
