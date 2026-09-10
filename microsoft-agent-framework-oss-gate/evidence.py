"""Correlated machine-readable and human-readable Gate 0 evidence."""

from __future__ import annotations

import json
import uuid
from pathlib import Path


def render_report(result: dict[str, object]) -> str:
    provenance = (
        result.get("provenance") if isinstance(result.get("provenance"), dict) else {}
    )
    manifest = (
        result.get("manifest") if isinstance(result.get("manifest"), dict) else {}
    )
    source = manifest.get("source") if isinstance(manifest.get("source"), dict) else {}
    runtime = (
        manifest.get("runtime") if isinstance(manifest.get("runtime"), dict) else {}
    )
    configuration = (
        manifest.get("configuration")
        if isinstance(manifest.get("configuration"), dict)
        else {}
    )
    package_lock = (
        manifest.get("packageLock")
        if isinstance(manifest.get("packageLock"), dict)
        else {}
    )
    component_inventory = (
        manifest.get("componentInventory")
        if isinstance(manifest.get("componentInventory"), dict)
        else {}
    )
    backend = (
        manifest.get("backend") if isinstance(manifest.get("backend"), dict) else {}
    )
    probe = result.get("probe") if isinstance(result.get("probe"), dict) else {}
    failures = result.get("failures", [])
    failure_lines = "\n".join(f"- `{failure}`" for failure in failures) or "- None"
    boundary_lines = (
        "\n".join(
            f"- `{name}`: {'unchanged' if detail['unchanged'] else 'CHANGED'}"
            for name, detail in result.get("boundaries", {}).items()
        )
        or "- None configured"
    )
    return (
        "# Microsoft Agent Framework OSS durability Gate 0\n\n"
        f"Decision: **{result['decision']}**\n\n"
        "## Correlated provenance\n\n"
        f"- Source revision: `{source.get('revision')}` (live `{provenance.get('sourceRevision')}`)\n"
        f"- Gate source digest: `{source.get('gateSourceDigest')}`\n"
        f"- Dirty-state digest: `{source.get('dirtyStateDigest')}`\n"
        f"- Package lock SHA-256: `{package_lock.get('sha256')}`\n"
        f"- Component inventory SHA-256: `{component_inventory.get('sha256')}`\n"
        f"- Runtime: .NET `{runtime.get('dotnetSdk')}`, RID `{runtime.get('rid')}`\n"
        f"- Configuration / contract: `{configuration.get('version')}` / `{configuration.get('contractVersion')}`\n"
        f"- Backend revision / protocol: `{backend.get('revision')}` / `{backend.get('protocol')}`\n"
        f"- Manifest SHA-256: `{result['manifestDigest']}`\n"
        f"- Live observation SHA-256: `{result['observedDigest']}`\n\n"
        "## Worker replacement\n\n"
        f"- Orchestration: `{probe.get('orchestrationId')}`\n"
        f"- Workers / PIDs: `{probe.get('workerPids', {})}`\n"
        f"- Checkpoints: `{probe.get('checkpoints', [])}`\n"
        f"- Effects: `{probe.get('effects', {})}`\n\n"
        "## Failures\n\n"
        f"{failure_lines}\n\n"
        "## Protected boundaries\n\n"
        f"{boundary_lines}\n"
    )


def create_evidence_directory(evidence_root: Path) -> Path:
    evidence_dir = evidence_root / f"gate-{uuid.uuid4()}"
    evidence_dir.mkdir(parents=True, exist_ok=False)
    return evidence_dir


def write_evidence(evidence_dir: Path, result: dict[str, object]) -> None:
    (evidence_dir / "decision.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence_dir / "report.md").write_text(render_report(result), encoding="utf-8")
