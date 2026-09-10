"""Public CLI for Microsoft Agent Framework OSS durability Gate 0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence import create_evidence_directory, write_evidence
from isolation import capture_boundaries, namespace_failures, path_failures
from probe_runner import run_probe
from provenance import json_digest, observe_environment
from schema_validation import validate as validate_schema


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _floating(value: object) -> bool:
    return (
        not isinstance(value, str)
        or not value.strip()
        or value.casefold() in {"latest", "main", "master", "head", "*"}
        or "*" in value
    )


def semantic_failures(manifest: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if manifest.get("schemaVersion") != "maf-oss-gate-manifest/v1":
        failures.append("manifest.schema-version-invalid")
    forbidden = {
        value.casefold()
        for value in manifest.get("forbiddenComponents", [])
        if isinstance(value, str)
    }
    components = manifest.get("components")
    components = components if isinstance(components, list) else []
    if not components:
        failures.append("manifest.components-missing")
    names: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            continue
        name = component.get("name")
        display = name if isinstance(name, str) else "<unnamed>"
        if isinstance(name, str):
            folded = name.casefold()
            if folded in names:
                failures.append(f"manifest.component-duplicate:{name}")
            names.add(folded)
            if folded in forbidden:
                failures.append(f"dependency.forbidden:{name}")
        if _floating(component.get("version")):
            failures.append(f"manifest.component-version-not-pinned:{display}")
        if not isinstance(component.get("licence"), dict) or not component.get(
            "licence"
        ):
            failures.append(f"manifest.component-licence-missing:{display}")
        if not isinstance(component.get("unavoidableServiceCost"), dict):
            failures.append(f"manifest.component-cost-missing:{display}")
    backend = manifest.get("backend")
    if not isinstance(backend, dict):
        return failures + ["manifest.backend-missing"]
    if _floating(backend.get("revision")):
        failures.append("manifest.backend-revision-not-pinned")
    if backend.get("type") != "production":
        failures.append(f"backend.{backend.get('type', 'type-missing')}")
    for field, failure in (
        ("productionCapable", "backend.not-production-capable"),
        ("selfManaged", "backend.not-self-managed"),
        ("openSource", "backend.not-open-source"),
        ("compatibleWithTuple", "backend.incompatible-with-tuple"),
    ):
        if backend.get(field) is not True:
            failures.append(failure)
    if not backend.get("compatibilityEvidence"):
        failures.append("manifest.backend-compatibility-evidence-missing")
    if not backend.get("storageDependencies"):
        failures.append("manifest.backend-storage-dependencies-missing")
    if not isinstance(backend.get("licence"), dict) or not backend.get("licence"):
        failures.append("manifest.backend-licence-missing")
    cost = backend.get("unavoidableServiceCost")
    if not isinstance(cost, dict):
        failures.append("manifest.backend-cost-missing")
    elif (
        cost.get("amount") != 0
        or cost.get("amountStatus") != "zero"
        or cost.get("period") != "none"
    ):
        failures.append("backend.unavoidable-service-cost")
    return failures


def provenance_failures(
    manifest: dict[str, object], recorded: dict[str, object], live: dict[str, object]
) -> list[str]:
    failures: list[str] = []
    if recorded.get("schemaVersion") != "maf-oss-gate-observed/v1":
        failures.append("provenance.schema-version-invalid")
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
    dimensions = (
        (source.get("revision"), "sourceRevision", "source-revision"),
        (source.get("gateSourceDigest"), "gateSourceDigest", "gate-source-digest"),
        (source.get("dirtyStateDigest"), "dirtyStateDigest", "dirty-state-digest"),
        (runtime.get("dotnetSdk"), "dotnetSdk", "dotnet-sdk"),
        (runtime.get("rid"), "rid", "rid"),
        (configuration.get("version"), "configurationVersion", "configuration-version"),
        (configuration.get("contractVersion"), "contractVersion", "contract-version"),
        (package_lock.get("sha256"), "packageLockSha256", "package-lock-sha256"),
        (
            component_inventory.get("sha256"),
            "componentInventorySha256",
            "component-inventory-sha256",
        ),
    )
    for expected, field, label in dimensions:
        if expected != recorded.get(field) or expected != live.get(field):
            failures.append(f"provenance.{label}-mismatch")
    return failures


def _deduplicate(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def evaluate_command(
    args: argparse.Namespace, gate_root: Path, repository_root: Path
) -> int:
    manifest = load_json(args.manifest)
    recorded = load_json(args.observed)
    boundaries = load_json(args.boundaries)
    schema = load_json(gate_root / "manifest.schema.json")
    live, observation_failures = observe_environment(
        manifest, gate_root, repository_root
    )
    before, before_failures = capture_boundaries(boundaries, repository_root)
    failures = [
        f"manifest.schema:{failure}" for failure in validate_schema(manifest, schema)
    ]
    failures += semantic_failures(manifest)
    component_inventory = manifest.get("componentInventory")
    inventory_path = (
        component_inventory.get("path")
        if isinstance(component_inventory, dict)
        else None
    )
    try:
        inventory_components = (
            json.loads((gate_root / inventory_path).read_text(encoding="utf-8"))
            if isinstance(inventory_path, str)
            else None
        )
    except (OSError, json.JSONDecodeError, TypeError):
        inventory_components = None
    if inventory_components != manifest.get("components"):
        failures.append("manifest.component-inventory-mismatch")
    failures += observation_failures
    failures += provenance_failures(manifest, recorded, live)
    failures += before_failures
    failures += path_failures(
        manifest, boundaries, repository_root, gate_root, args.evidence_root
    )
    failures += namespace_failures(manifest)
    probe: dict[str, object] = {"started": False}
    if not failures:
        probe, probe_failures = run_probe(manifest, gate_root)
        failures += probe_failures
    result: dict[str, object] = {
        "decision": "go" if not failures else "no-go",
        "failures": _deduplicate(failures),
        "probe": probe,
        "manifestDigest": json_digest(manifest),
        "recordedObservedDigest": json_digest(recorded),
        "observedDigest": json_digest(live),
        "manifest": manifest,
        "recordedProvenance": recorded,
        "provenance": live,
        "backend": manifest.get("backend"),
        "boundaries": {},
    }
    unsafe_evidence = any(
        failure.startswith("isolation.evidence-") for failure in result["failures"]
    )
    evidence_dir: Path | None = None
    if not unsafe_evidence:
        try:
            evidence_dir = create_evidence_directory(args.evidence_root)
            result["evidenceDirectory"] = str(evidence_dir)
            write_evidence(evidence_dir, result)
        except OSError as exc:
            result["failures"] = _deduplicate(
                list(result["failures"])
                + [f"evidence.write-failed:{type(exc).__name__}"]
            )
            result["decision"] = "no-go"
            result.pop("evidenceDirectory", None)
            evidence_dir = None
    after, after_failures = capture_boundaries(boundaries, repository_root)
    result["failures"] = _deduplicate(list(result["failures"]) + after_failures)
    for name in sorted(set(before) | set(after)):
        unchanged = before.get(name) == after.get(name)
        result["boundaries"][name] = {
            "before": before.get(name),
            "after": after.get(name),
            "unchanged": unchanged,
        }
        if not unchanged:
            result["failures"].append(f"boundary.changed:{name}")
    result["failures"] = _deduplicate(result["failures"])
    result["decision"] = "go" if not result["failures"] else "no-go"
    if evidence_dir is not None:
        try:
            write_evidence(evidence_dir, result)
        except OSError as exc:
            result["failures"] = _deduplicate(
                list(result["failures"])
                + [f"evidence.write-failed:{type(exc).__name__}"]
            )
            result["decision"] = "no-go"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["decision"] == "go" else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--manifest", type=Path, required=True)
    evaluate_parser.add_argument("--observed", type=Path, required=True)
    evaluate_parser.add_argument("--boundaries", type=Path, required=True)
    evaluate_parser.add_argument("--evidence-root", type=Path, required=True)
    observe_parser = subparsers.add_parser("observe")
    observe_parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    gate_root = Path(__file__).resolve().parent
    repository_root = gate_root.parent
    if args.command == "observe":
        observed, failures = observe_environment(
            load_json(args.manifest), gate_root, repository_root
        )
        print(json.dumps({"observed": observed, "failures": failures}, sort_keys=True))
        return 0 if not failures else 2
    return evaluate_command(args, gate_root, repository_root)


if __name__ == "__main__":
    raise SystemExit(main())
