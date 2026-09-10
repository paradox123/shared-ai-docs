"""Deterministic hashing and live environment observation for Gate 0."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

SOURCE_FILES = (
    ".gitignore",
    "README.md",
    "gate.py",
    "evidence.py",
    "gate-config.json",
    "isolation.py",
    "probe_runner.py",
    "provenance.py",
    "schema_validation.py",
    "global.json",
    "manifest.schema.json",
    "protected-boundaries.json",
    "audit/Audit.csproj",
    "audit/Program.cs",
    "audit/components.json",
    "audit/compose_gate_inputs.py",
    "audit/inventory.py",
    "audit/licence-overrides.json",
    "audit/packages.lock.json",
    "audit/probe-must-not-start.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def source_digest(gate_root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SOURCE_FILES:
        digest.update(relative.encode())
        digest.update(sha256(gate_root / relative).encode())
    return digest.hexdigest()


def command(*arguments: str, cwd: Path) -> str:
    return subprocess.run(
        arguments, cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def dirty_state_digest(gate_root: Path, repository_root: Path) -> str:
    """Hash working-file state relative to HEAD without depending on the index."""
    digest = hashlib.sha256()
    for relative in SOURCE_FILES:
        repo_relative = (gate_root / relative).relative_to(repository_root).as_posix()
        working_digest = sha256(gate_root / relative)
        committed = subprocess.run(
            ["git", "-C", str(repository_root), "show", f"HEAD:{repo_relative}"],
            check=False,
            capture_output=True,
        )
        if committed.returncode:
            state = "untracked"
        else:
            state = (
                "clean"
                if hashlib.sha256(committed.stdout).hexdigest() == working_digest
                else "modified"
            )
        digest.update(f"{relative}\0{state}\0{working_digest}\n".encode())
    return digest.hexdigest()


def observe_environment(
    manifest: dict[str, object], gate_root: Path, repository_root: Path
) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    package_lock = manifest.get("packageLock")
    lock_relative = package_lock.get("path") if isinstance(package_lock, dict) else None
    component_inventory = manifest.get("componentInventory")
    inventory_relative = (
        component_inventory.get("path")
        if isinstance(component_inventory, dict)
        else None
    )
    try:
        revision = command("git", "rev-parse", "HEAD", cwd=repository_root)
    except (OSError, subprocess.CalledProcessError):
        revision = ""
        failures.append("observation.source-revision-unavailable")
    try:
        dotnet_sdk = command("dotnet", "--version", cwd=gate_root)
        dotnet_info = command("dotnet", "--info", cwd=gate_root)
        rid = next(
            line.split(":", 1)[1].strip()
            for line in dotnet_info.splitlines()
            if line.strip().startswith("RID:")
        )
    except (OSError, subprocess.CalledProcessError, StopIteration):
        dotnet_sdk, rid = "", ""
        failures.append("observation.runtime-unavailable")
    try:
        lock_digest = (
            sha256((gate_root / lock_relative).resolve())
            if isinstance(lock_relative, str) and lock_relative
            else ""
        )
        if not lock_digest:
            failures.append("observation.package-lock-unavailable")
    except OSError:
        lock_digest = ""
        failures.append("observation.package-lock-unavailable")
    try:
        inventory_digest = (
            sha256((gate_root / inventory_relative).resolve())
            if isinstance(inventory_relative, str) and inventory_relative
            else ""
        )
        if not inventory_digest:
            failures.append("observation.component-inventory-unavailable")
    except OSError:
        inventory_digest = ""
        failures.append("observation.component-inventory-unavailable")
    try:
        gate_digest = source_digest(gate_root)
        dirty_digest = dirty_state_digest(gate_root, repository_root)
    except (OSError, subprocess.CalledProcessError, ValueError):
        gate_digest, dirty_digest = "", ""
        failures.append("observation.gate-source-unavailable")
    configuration = manifest.get("configuration")
    configuration = configuration if isinstance(configuration, dict) else {}
    configuration_path = configuration.get("path")
    try:
        live_configuration = (
            json.loads((gate_root / configuration_path).read_text(encoding="utf-8"))
            if isinstance(configuration_path, str)
            else {}
        )
    except (OSError, json.JSONDecodeError):
        live_configuration = {}
        failures.append("observation.configuration-unavailable")
    return {
        "schemaVersion": "maf-oss-gate-observed/v1",
        "sourceRevision": revision,
        "gateSourceDigest": gate_digest,
        "dirtyStateDigest": dirty_digest,
        "dotnetSdk": dotnet_sdk,
        "rid": rid,
        "configurationVersion": live_configuration.get("version"),
        "contractVersion": live_configuration.get("contractVersion"),
        "packageLockSha256": lock_digest,
        "componentInventorySha256": inventory_digest,
    }, failures
