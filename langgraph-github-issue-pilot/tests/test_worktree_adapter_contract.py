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
    origin = tmp_path / "origin.git"
    sibling = tmp_path / "sibling-worktree"
    worktree_root = tmp_path / "worker-worktrees"
    daniels_checkout.mkdir()
    git("init", "-b", "main", cwd=daniels_checkout)
    git("config", "user.name", "Contract Test", cwd=daniels_checkout)
    git("config", "user.email", "contract@example.invalid", cwd=daniels_checkout)
    (daniels_checkout / "marker.txt").write_text("main checkout\n", encoding="utf-8")
    git("add", "marker.txt", cwd=daniels_checkout)
    git("commit", "-m", "initial", cwd=daniels_checkout)
    git("init", "--bare", origin)
    git("remote", "add", "origin", origin, cwd=daniels_checkout)
    git("push", "-u", "origin", "main", cwd=daniels_checkout)
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
    assert created.base_ref == git("rev-parse", "main", cwd=daniels_checkout)
    assert git("branch", "--show-current", cwd=created.path) == "codex/run-run-001"
    assert (created.path / "marker.txt").read_text(encoding="utf-8") == "main checkout\n"
    assert (daniels_checkout / "marker.txt").read_text(encoding="utf-8") == "main checkout\n"
    assert (sibling / "marker.txt").read_text(encoding="utf-8") == "sibling change\n"


def test_git_adapter_fetches_and_pins_the_remote_base_when_local_main_is_stale(tmp_path) -> None:
    origin = tmp_path / "origin.git"
    upstream = tmp_path / "upstream"
    daniels_checkout = tmp_path / "daniels-checkout"
    worktree_root = tmp_path / "worker-worktrees"
    git("init", "--bare", origin)
    upstream.mkdir()
    git("init", "-b", "main", cwd=upstream)
    git("config", "user.name", "Contract Test", cwd=upstream)
    git("config", "user.email", "contract@example.invalid", cwd=upstream)
    (upstream / "marker.txt").write_text("base A\n", encoding="utf-8")
    git("add", "marker.txt", cwd=upstream)
    git("commit", "-m", "base A", cwd=upstream)
    git("remote", "add", "origin", origin, cwd=upstream)
    git("push", "-u", "origin", "main", cwd=upstream)
    git("--git-dir", origin, "symbolic-ref", "HEAD", "refs/heads/main")
    git("clone", origin, daniels_checkout)
    stale_sha = git("rev-parse", "HEAD", cwd=daniels_checkout)

    (upstream / "marker.txt").write_text("base B\n", encoding="utf-8")
    git("add", "marker.txt", cwd=upstream)
    git("commit", "-m", "base B", cwd=upstream)
    git("push", "origin", "main", cwd=upstream)
    remote_sha = git("rev-parse", "HEAD", cwd=upstream)
    assert git("rev-parse", "main", cwd=daniels_checkout) == stale_sha
    assert remote_sha != stale_sha

    created = GitWorktreeAdapter(worktree_root).create(
        run_id="run-002",
        repository="daniel/probare-crm",
        repository_root=daniels_checkout,
        base_ref="main",
    )

    assert git("rev-parse", "HEAD", cwd=created.path) == remote_sha
    assert (created.path / "marker.txt").read_text(encoding="utf-8") == "base B\n"
    assert created.base_ref == remote_sha
    assert git("rev-parse", "main", cwd=daniels_checkout) == stale_sha


def test_git_adapter_adopts_the_same_run_owned_worktree_after_restart(tmp_path) -> None:
    repository = tmp_path / "daniels-checkout"
    origin = tmp_path / "origin.git"
    repository.mkdir()
    git("init", "-b", "main", cwd=repository)
    git("config", "user.name", "Contract Test", cwd=repository)
    git("config", "user.email", "contract@example.invalid", cwd=repository)
    (repository / "marker.txt").write_text("main checkout\n", encoding="utf-8")
    git("add", "marker.txt", cwd=repository)
    git("commit", "-m", "initial", cwd=repository)
    git("init", "--bare", origin)
    git("remote", "add", "origin", origin, cwd=repository)
    git("push", "-u", "origin", "main", cwd=repository)
    adapter = GitWorktreeAdapter(tmp_path / "worker-worktrees")

    first = adapter.create(
        run_id="run-001",
        repository="daniel/probare-crm",
        repository_root=repository,
        base_ref="main",
    )
    (repository / "later.txt").write_text("remote advanced\n", encoding="utf-8")
    git("add", "later.txt", cwd=repository)
    git("commit", "-m", "advance remote", cwd=repository)
    git("push", "origin", "main", cwd=repository)
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
