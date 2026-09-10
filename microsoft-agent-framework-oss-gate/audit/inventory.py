"""Build a deterministic component inventory from a NuGet lock file."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

DIRECT_KINDS = {
    "Microsoft.Agents.AI.DurableTask": "workflow",
    "Microsoft.Agents.AI.Workflows": "framework",
    "Microsoft.DurableTask.Client": "client",
    "Microsoft.DurableTask.Client.AzureManaged": "client",
    "Microsoft.DurableTask.Worker": "worker",
    "Microsoft.DurableTask.Worker.AzureManaged": "worker",
}


def global_packages_root() -> Path:
    configured = os.environ.get("NUGET_PACKAGES")
    if configured:
        return Path(configured)
    output = subprocess.run(
        ["dotnet", "nuget", "locals", "global-packages", "--list"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _, path = output.split(": ", 1)
    return Path(path)


def nuspec_metadata(
    package_root: Path,
    name: str,
    version: str,
    overrides: dict[str, dict[str, str]],
) -> tuple[str, str, str | None]:
    package_dir = package_root / name.casefold() / version.casefold()
    nuspecs = list(package_dir.glob("*.nuspec"))
    if len(nuspecs) != 1:
        raise ValueError(
            f"expected one nuspec for {name} {version}, found {len(nuspecs)}"
        )
    root = ET.parse(nuspecs[0]).getroot()
    metadata = next(
        element for element in root.iter() if element.tag.endswith("metadata")
    )
    licence = next(
        (element for element in metadata if element.tag.endswith("license")), None
    )
    override = overrides.get(f"{name}/{version}")
    if (
        licence is not None
        and licence.attrib.get("type") == "expression"
        and licence.text
    ):
        licence_expression = licence.text.strip()
        licence_source = f"https://www.nuget.org/packages/{name}/{version}"
    elif override and override.get("spdx") and override.get("source"):
        licence_expression = override["spdx"]
        licence_source = override["source"]
    else:
        raise ValueError(
            f"{name} {version} has no SPDX licence expression or audited override"
        )
    repository = next(
        (element for element in metadata if element.tag.endswith("repository")), None
    )
    revision = repository.attrib.get("commit") if repository is not None else None
    return licence_expression, licence_source, revision


def build_inventory(
    lock_path: Path, overrides: dict[str, dict[str, str]]
) -> list[dict[str, object]]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    dependencies = lock.get("dependencies")
    if not isinstance(dependencies, dict) or len(dependencies) != 1:
        raise ValueError("lock file must contain exactly one target framework")
    packages = next(iter(dependencies.values()))
    if not isinstance(packages, dict):
        raise TypeError("target framework dependency graph is invalid")
    package_root = global_packages_root()
    inventory: list[dict[str, object]] = []
    for name in sorted(packages, key=str.casefold):
        details = packages[name]
        if not isinstance(details, dict):
            raise TypeError(f"invalid lock entry for {name}")
        version = details.get("resolved")
        content_hash = details.get("contentHash")
        if not isinstance(version, str) or not isinstance(content_hash, str):
            raise TypeError(f"unresolved package entry for {name}")
        licence, licence_source, revision = nuspec_metadata(
            package_root, name, version, overrides
        )
        package_url = f"https://www.nuget.org/packages/{name}/{version}"
        component: dict[str, object] = {
            "name": name,
            "kind": DIRECT_KINDS.get(name, "transitive"),
            "version": version,
            "contentHash": content_hash,
            "source": package_url,
            "licence": {"spdx": licence, "source": licence_source},
            "unavoidableServiceCost": {
                "amount": 0,
                "amountStatus": "zero",
                "currency": "EUR",
                "period": "none",
                "source": package_url,
            },
        }
        if revision:
            component["repositoryRevision"] = revision
        inventory.append(component)
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--licence-overrides",
        type=Path,
        default=Path(__file__).with_name("licence-overrides.json"),
    )
    args = parser.parse_args()
    overrides = json.loads(args.licence_overrides.read_text(encoding="utf-8"))
    inventory = build_inventory(args.lock, overrides)
    args.output.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"components": len(inventory), "output": str(args.output)}, sort_keys=True
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
