"""Fingerprint protected paths before and after the isolated managed probe."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _filesystem_fingerprint(path: Path) -> str:
    if not path.exists() and not path.is_symlink():
        return "missing"
    digest = hashlib.sha256()
    paths = [path] if path.is_file() or path.is_symlink() else sorted(path.rglob("*"))
    for candidate in paths:
        relative = candidate.name if candidate == path else candidate.relative_to(path).as_posix()
        digest.update(relative.encode())
        if candidate.is_symlink():
            digest.update(b"symlink\0" + os.readlink(candidate).encode())
        elif candidate.is_file():
            digest.update(b"file\0" + _file_sha256(candidate).encode())
        elif candidate.is_dir():
            digest.update(b"directory\0")
    return digest.hexdigest()


def _git_fingerprint(repository: Path, scope: Path | None = None) -> str:
    scope_arg = "." if scope is None else scope.relative_to(repository).as_posix()
    head = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    listed = subprocess.run(
        [
            "git", "-C", str(repository), "ls-files", "-z", "--cached", "--others",
            "--exclude-standard", "--", scope_arg,
        ],
        check=True,
        capture_output=True,
    ).stdout
    digest = hashlib.sha256(head.encode())
    for raw_name in sorted(name for name in listed.split(b"\0") if name):
        candidate = repository / raw_name.decode(errors="surrogateescape")
        digest.update(raw_name)
        if candidate.is_symlink():
            digest.update(b"symlink\0" + os.readlink(candidate).encode())
        elif candidate.is_file():
            digest.update(_file_sha256(candidate).encode())
        else:
            digest.update(b"missing\0")
    return digest.hexdigest()


def _github_fingerprint(repository: Path) -> str:
    remote = subprocess.run(
        ["git", "-C", str(repository), "remote", "get-url", "origin"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    repository_data = json.loads(
        subprocess.run(
            [
                "gh", "repo", "view", remote, "--json",
                "nameWithOwner,defaultBranchRef,isPrivate,url,visibility",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    )
    name_with_owner = repository_data["nameWithOwner"]
    rulesets = json.loads(
        subprocess.run(
            ["gh", "api", f"repos/{name_with_owner}/rulesets?includes_parents=true"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    )
    payload = json.dumps(
        {"remote": remote, "repository": repository_data, "rulesets": rulesets},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def expand_path(raw_path: str, repository_root: Path) -> Path:
    return Path(
        raw_path.replace("$REPO_ROOT", str(repository_root)).replace(
            "$USER_HOME", str(Path.home())
        )
    )


def capture_boundaries(
    boundaries: dict[str, object], repository_root: Path
) -> tuple[dict[str, str], list[str]]:
    fingerprints: dict[str, str] = {}
    failures: list[str] = []
    entries = boundaries.get("boundaries")
    if not isinstance(entries, list):
        return fingerprints, ["boundaries.invalid"]
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            failures.append("boundaries.entry-invalid")
            continue
        name = str(entry["name"])
        raw_path = entry.get("path")
        mode = entry.get("mode")
        if not isinstance(raw_path, str):
            failures.append(f"boundaries.path-invalid:{name}")
            continue
        path = expand_path(raw_path, repository_root)
        try:
            if mode == "git-path":
                fingerprints[name] = _git_fingerprint(repository_root, path)
            elif mode == "git-repository":
                fingerprints[name] = _git_fingerprint(path) if path.exists() else "missing"
            elif mode == "github-repository":
                fingerprints[name] = _github_fingerprint(path)
            elif mode == "metadata-and-content-hash":
                fingerprints[name] = _filesystem_fingerprint(path)
            else:
                failures.append(f"boundaries.mode-invalid:{name}")
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            failures.append(f"boundaries.capture-failed:{name}:{type(exc).__name__}")
    return fingerprints, failures


def path_failures(
    boundaries: dict[str, object],
    repository_root: Path,
    pilot_root: Path,
    evidence_root: Path,
    state_root: Path,
) -> list[str]:
    resources = {
        "evidence": evidence_root.resolve(),
        "state": state_root.resolve(),
    }
    failures: list[str] = []
    for kind, path in resources.items():
        if path != pilot_root and pilot_root not in path.parents:
            failures.append(f"isolation.{kind}-root-outside-pilot")
    entries = boundaries.get("boundaries")
    if not isinstance(entries, list):
        return failures + ["boundaries.invalid"]
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name, raw_path = entry.get("name"), entry.get("path")
        if not isinstance(name, str) or not isinstance(raw_path, str):
            continue
        if entry.get("mode") == "github-repository":
            continue
        boundary_path = expand_path(raw_path, repository_root).resolve()
        for kind, path in resources.items():
            if path == boundary_path or path in boundary_path.parents or boundary_path in path.parents:
                failures.append(f"isolation.{kind}-path-overlap:{name}")
    return failures
