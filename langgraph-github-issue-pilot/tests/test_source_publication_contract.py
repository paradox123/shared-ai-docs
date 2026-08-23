from __future__ import annotations

import subprocess

import pytest

from github_issue_pilot.implementation import GitWorktreeAdapter, Worktree
from github_issue_pilot.publication import GitSourceControl, SourcePublicationError


def git(*args: object, cwd=None) -> str:
    completed = subprocess.run(
        ["git", *(str(arg) for arg in args)],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def publication_worktree(tmp_path) -> tuple[Worktree, object]:
    remote = tmp_path / "remote.git"
    checkout = tmp_path / "checkout"
    git("init", "--bare", remote)
    checkout.mkdir()
    git("init", "-b", "main", cwd=checkout)
    git("config", "user.name", "Contract Test", cwd=checkout)
    git("config", "user.email", "contract@example.invalid", cwd=checkout)
    (checkout / "marker.txt").write_text("main\n", encoding="utf-8")
    git("add", "marker.txt", cwd=checkout)
    git("commit", "-m", "initial", cwd=checkout)
    git("remote", "add", "origin", remote, cwd=checkout)
    git("push", "-u", "origin", "main", cwd=checkout)
    worktree = GitWorktreeAdapter(tmp_path / "worktrees").create(
        run_id="run-001",
        repository="daniel/probare-crm",
        repository_root=checkout,
        base_ref="main",
    )
    git("config", "user.name", "Pilot Agent", cwd=worktree.path)
    git("config", "user.email", "pilot@example.invalid", cwd=worktree.path)
    return worktree, remote


def test_source_control_commits_and_pushes_the_explicit_run_branch(tmp_path) -> None:
    worktree, remote = publication_worktree(tmp_path)
    (worktree.path / "feature.txt").write_text("implemented\n", encoding="utf-8")

    published = GitSourceControl().publish(worktree, issue_number=41)

    assert published.branch == "codex/run-run-001"
    assert published.head_sha == git("rev-parse", "HEAD", cwd=worktree.path)
    assert len(published.head_sha) == 40
    assert git("status", "--porcelain", cwd=worktree.path) == ""
    assert git("log", "-1", "--pretty=%s", cwd=worktree.path) == "Implement issue #41"
    assert git("--git-dir", remote, "rev-parse", "refs/heads/codex/run-run-001") == (
        published.head_sha
    )


def test_source_control_pushes_an_already_committed_implementation_without_extra_commit(
    tmp_path,
) -> None:
    worktree, remote = publication_worktree(tmp_path)
    (worktree.path / "feature.txt").write_text("implemented\n", encoding="utf-8")
    git("add", "feature.txt", cwd=worktree.path)
    git("commit", "-m", "Worker implementation", cwd=worktree.path)
    worker_head = git("rev-parse", "HEAD", cwd=worktree.path)

    published = GitSourceControl().publish(worktree, issue_number=41)

    assert published.head_sha == worker_head
    assert git("rev-list", "--count", "main..HEAD", cwd=worktree.path) == "1"
    assert git("--git-dir", remote, "rev-parse", "refs/heads/codex/run-run-001") == worker_head


def test_source_control_rejects_sensitive_diff_before_commit_or_push(tmp_path) -> None:
    worktree, remote = publication_worktree(tmp_path)
    base_head = git("rev-parse", "HEAD", cwd=worktree.path)
    (worktree.path / "leak.txt").write_text(
        "Authorization: Bearer ghp_12345678901234567890\n",
        encoding="utf-8",
    )

    with pytest.raises(SourcePublicationError, match="sensitive_diff"):
        GitSourceControl().publish(worktree, issue_number=41)

    assert git("rev-parse", "HEAD", cwd=worktree.path) == base_head
    assert subprocess.run(
        ["git", "--git-dir", str(remote), "show-ref", "--verify", "--quiet", "refs/heads/codex/run-run-001"],
        check=False,
    ).returncode == 1
