"""Protected-boundary and gate-owned resource checks."""

from __future__ import annotations

import hashlib
import os
import socket
import subprocess
from pathlib import Path

from provenance import sha256


def _filesystem_fingerprint(path: Path) -> str:
    if not path.exists() and not path.is_symlink():
        return "missing"
    digest = hashlib.sha256()
    paths = [path] if path.is_file() or path.is_symlink() else sorted(path.rglob("*"))
    for candidate in paths:
        relative = (
            candidate.name
            if candidate == path
            else candidate.relative_to(path).as_posix()
        )
        digest.update(relative.encode())
        if candidate.is_symlink():
            digest.update(b"symlink\0" + os.readlink(candidate).encode())
        elif candidate.is_file():
            digest.update(b"file\0" + sha256(candidate).encode())
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
            "git",
            "-C",
            str(repository),
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            scope_arg,
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
            digest.update(sha256(candidate).encode())
        else:
            digest.update(b"missing\0")
    return digest.hexdigest()


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
        name, raw_path, mode = entry["name"], entry.get("path"), entry.get("mode")
        if not isinstance(raw_path, str):
            failures.append(f"boundaries.path-invalid:{name}")
            continue
        path = expand_path(raw_path, repository_root)
        try:
            if mode == "git-path":
                fingerprints[name] = _git_fingerprint(repository_root, path)
            elif mode == "git-repository":
                fingerprints[name] = (
                    _git_fingerprint(path) if path.exists() else "missing"
                )
            elif mode == "metadata-and-content-hash":
                fingerprints[name] = _filesystem_fingerprint(path)
            else:
                failures.append(f"boundaries.mode-invalid:{name}")
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            failures.append(f"boundaries.capture-failed:{name}:{type(exc).__name__}")
    return fingerprints, failures


def _overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def path_failures(
    manifest: dict[str, object],
    boundaries: dict[str, object],
    repository_root: Path,
    gate_root: Path,
    evidence_root: Path,
) -> list[str]:
    failures: list[str] = []
    resolved_evidence = evidence_root.resolve()
    if resolved_evidence != gate_root and gate_root not in resolved_evidence.parents:
        failures.append("isolation.evidence-root-outside-gate-root")
    probe = manifest.get("probe")
    state_paths = probe.get("statePaths") if isinstance(probe, dict) else None
    if not isinstance(state_paths, list) or not state_paths:
        return ["manifest.probe-state-paths-missing"]
    resources: list[tuple[str, Path]] = [("evidence", resolved_evidence)]
    for index, raw_state in enumerate(state_paths):
        if not isinstance(raw_state, str):
            failures.append("manifest.probe-state-path-invalid")
            continue
        state_path = Path(raw_state)
        state_path = (
            (gate_root / state_path).resolve()
            if not state_path.is_absolute()
            else state_path.resolve()
        )
        resources.append(("state", state_path))
        if state_path != gate_root and gate_root not in state_path.parents:
            failures.append(f"isolation.state-path-outside-gate-root:{index}")
    entries = boundaries.get("boundaries")
    if not isinstance(entries, list):
        return failures
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("name"), str)
            or not isinstance(entry.get("path"), str)
        ):
            continue
        name = entry["name"]
        boundary_path = expand_path(entry["path"], repository_root).resolve()
        for kind, resource_path in resources:
            if _overlaps(resource_path, boundary_path):
                failures.append(f"isolation.{kind}-path-overlap:{name}")
    return failures


def namespace_failures(manifest: dict[str, object]) -> list[str]:
    probe = manifest.get("probe")
    probe = probe if isinstance(probe, dict) else {}
    failures: list[str] = []
    try:
        process_list = subprocess.run(
            ["ps", "-axo", "command="], check=True, capture_output=True, text=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return ["isolation.process-namespace-unavailable"]
    for name in probe.get("workerProcessNames", []):
        if isinstance(name, str) and name in process_list:
            failures.append(f"isolation.process-name-in-use:{name}")
    for port in probe.get("ports", []):
        if not isinstance(port, int):
            continue
        with socket.socket() as candidate:
            try:
                candidate.bind(("127.0.0.1", port))
            except OSError:
                failures.append(f"isolation.port-in-use:{port}")
    return failures
