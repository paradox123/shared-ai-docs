from __future__ import annotations

import subprocess

from github_issue_pilot.implementation import GitWorktreeAdapter


def git(*args: object, cwd=None) -> str:
    completed = subprocess.run(
        ["git", *(str(arg) for arg in args)],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_git_adapter_creates_a_run_owned_branch_without_changing_other_worktrees(tmp_path) -> None:
    daniels_checkout = tmp_path / "daniels-checkout"
    sibling = tmp_path / "sibling-worktree"
    worktree_root = tmp_path / "worker-worktrees"
    daniels_checkout.mkdir()
    git("init", "-b", "main", cwd=daniels_checkout)
    git("config", "user.name", "Contract Test", cwd=daniels_checkout)
    git("config", "user.email", "contract@example.invalid", cwd=daniels_checkout)
    (daniels_checkout / "marker.txt").write_text("main checkout\n", encoding="utf-8")
    git("add", "marker.txt", cwd=daniels_checkout)
    git("commit", "-m", "initial", cwd=daniels_checkout)
    git("worktree", "add", "-b", "codex/sibling", sibling, "main", cwd=daniels_checkout)
    (sibling / "marker.txt").write_text("sibling change\n", encoding="utf-8")

    created = GitWorktreeAdapter(worktree_root).create(
        run_id="run-001",
        repository="daniel/probare-crm",
        repository_root=daniels_checkout,
        base_ref="main",
    )

    assert created.path == worktree_root / "daniel-probare-crm" / "run-001"
    assert created.branch == "codex/run-run-001"
    assert created.base_ref == "main"
    assert git("branch", "--show-current", cwd=created.path) == "codex/run-run-001"
    assert (created.path / "marker.txt").read_text(encoding="utf-8") == "main checkout\n"
    assert (daniels_checkout / "marker.txt").read_text(encoding="utf-8") == "main checkout\n"
    assert (sibling / "marker.txt").read_text(encoding="utf-8") == "sibling change\n"


def test_git_adapter_adopts_the_same_run_owned_worktree_after_restart(tmp_path) -> None:
    repository = tmp_path / "daniels-checkout"
    repository.mkdir()
    git("init", "-b", "main", cwd=repository)
    git("config", "user.name", "Contract Test", cwd=repository)
    git("config", "user.email", "contract@example.invalid", cwd=repository)
    (repository / "marker.txt").write_text("main checkout\n", encoding="utf-8")
    git("add", "marker.txt", cwd=repository)
    git("commit", "-m", "initial", cwd=repository)
    adapter = GitWorktreeAdapter(tmp_path / "worker-worktrees")

    first = adapter.create(
        run_id="run-001",
        repository="daniel/probare-crm",
        repository_root=repository,
        base_ref="main",
    )
    recovered = adapter.create(
        run_id="run-001",
        repository="daniel/probare-crm",
        repository_root=repository,
        base_ref="main",
    )

    assert recovered == first
    assert git("worktree", "list", "--porcelain", cwd=repository).count(
        f"worktree {first.path}"
    ) == 1
