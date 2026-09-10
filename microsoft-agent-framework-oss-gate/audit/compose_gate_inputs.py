"""Compose the committed gate manifest and locally observed provenance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from provenance import command, dirty_state_digest, sha256, source_digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    repository_root = root.parent
    lock_path = root / "audit" / "packages.lock.json"
    components_path = root / "audit" / "components.json"
    revision = command("git", "rev-parse", "HEAD", cwd=repository_root)
    repository = command("git", "remote", "get-url", "origin", cwd=repository_root)
    dotnet_sdk = command("dotnet", "--version", cwd=root)
    dotnet_info = command("dotnet", "--info", cwd=root)
    rid = next(
        line.split(":", 1)[1].strip()
        for line in dotnet_info.splitlines()
        if line.strip().startswith("RID:")
    )
    lock_digest = sha256(lock_path)
    gate_source_digest = source_digest(root)
    gate_dirty_state_digest = dirty_state_digest(root, repository_root)
    components = json.loads(components_path.read_text(encoding="utf-8"))
    configuration = json.loads((root / "gate-config.json").read_text(encoding="utf-8"))

    manifest = {
        "schemaVersion": "maf-oss-gate-manifest/v1",
        "source": {
            "repository": repository,
            "revision": revision,
            "gateSourceDigest": gate_source_digest,
            "dirtyStateDigest": gate_dirty_state_digest,
        },
        "runtime": {"dotnetSdk": dotnet_sdk, "rid": rid},
        "configuration": {"path": "gate-config.json", **configuration},
        "packageLock": {"path": "audit/packages.lock.json", "sha256": lock_digest},
        "componentInventory": {
            "path": "audit/components.json",
            "sha256": sha256(components_path),
        },
        "components": components,
        "backend": {
            "name": "Azure Durable Task Scheduler",
            "type": "managed-service",
            "repository": "https://learn.microsoft.com/en-us/azure/durable-task/common/choose-orchestration-framework",
            "revision": "documentation-2026-05-05",
            "protocol": "Durable Task Scheduler gRPC via Microsoft.DurableTask.*.AzureManaged 1.18.0",
            "productionCapable": True,
            "selfManaged": False,
            "openSource": False,
            "compatibleWithTuple": True,
            "compatibilityEvidence": [
                "https://learn.microsoft.com/en-us/azure/durable-task/common/choose-orchestration-framework",
                "https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions",
                "https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Microsoft.Agents.AI.DurableTask.csproj",
                "https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/samples/DurableWorkflows/ConsoleApps/01_SequentialWorkflow/Program.cs",
            ],
            "licence": {
                "spdx": "LicenseRef-Proprietary-Azure-Managed-Service",
                "source": "https://azure.microsoft.com/en-us/support/legal/",
            },
            "unavoidableServiceCost": {
                "amount": None,
                "amountStatus": "variable-paid",
                "currency": "EUR",
                "period": "operation",
                "source": "https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler-billing",
            },
            "storageDependencies": [
                "Microsoft-operated Azure Durable Task Scheduler resource",
                "Azure subscription",
            ],
        },
        "forbiddenComponents": ["Temporal", "paid-managed-workflow-service"],
        "probe": {
            "command": ["python3", "audit/probe-must-not-start.py"],
            "workerProcessNames": ["maf-oss-gate-worker-1", "maf-oss-gate-worker-2"],
            "ports": [19080, 19082],
            "statePaths": [".gate-state"],
            "expectedEffects": ["before-worker-stop", "after-worker-stop"],
        },
    }
    observed = {
        "schemaVersion": "maf-oss-gate-observed/v1",
        "sourceRevision": revision,
        "gateSourceDigest": gate_source_digest,
        "dirtyStateDigest": gate_dirty_state_digest,
        "dotnetSdk": dotnet_sdk,
        "rid": rid,
        "configurationVersion": configuration["version"],
        "contractVersion": configuration["contractVersion"],
        "packageLockSha256": lock_digest,
        "componentInventorySha256": sha256(components_path),
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "observed.json").write_text(
        json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"components": len(components), "gateSourceDigest": gate_source_digest},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
