"""Read-only Azure and local provenance observation for the managed pilot gate."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from pathlib import Path


PILOT_SOURCE_PATHS = (
    "ManagedDurabilityProbe/ManagedDurabilityProbe.csproj",
    "ManagedDurabilityProbe/Program.cs",
    "ManagedDurabilityProbe/Probe.cs",
    "ManagedDurabilityProbe/packages.lock.json",
    "azure_observation.py",
    "evidence.py",
    "global.json",
    "isolation.py",
    "managed-gate-config.schema.json",
    "managed-gate-evidence.schema.json",
    "managed_gate.py",
    "process_controller.py",
    "protected-boundaries.json",
    "schema_validation.py",
    "tests/fixtures/fake_worker.py",
    "tests/test_managed_gate_cli.py",
)


def _command(*arguments: str, cwd: Path) -> str:
    for attempt in range(2):
        try:
            return subprocess.run(
                arguments,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            ).stdout.strip()
        except subprocess.TimeoutExpired:
            if attempt == 1:
                raise
    raise AssertionError("unreachable")


def _json_command(*arguments: str, cwd: Path) -> object:
    return json.loads(_command(*arguments, "--output", "json", cwd=cwd))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pilot_source_sha256(pilot_root: Path) -> str:
    digest = hashlib.sha256()
    for relative in PILOT_SOURCE_PATHS:
        path = pilot_root / relative
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _rid(dotnet_info: str) -> str:
    for line in dotnet_info.splitlines():
        if line.strip().startswith("RID:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("dotnet RID unavailable")


def _access_token_object_id(token: str) -> str:
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    object_id = claims.get("oid")
    if not isinstance(object_id, str) or not object_id:
        raise ValueError("signed-in user object ID unavailable")
    return object_id


def observe(config: dict[str, object], pilot_root: Path) -> dict[str, object]:
    azure_value = config.get("azure")
    provenance_value = config.get("provenance")
    if not isinstance(azure_value, dict) or not isinstance(provenance_value, dict):
        raise ValueError("azure and provenance configuration are required")
    azure = azure_value
    provenance = provenance_value
    subscription_id = str(azure["subscriptionId"])
    resource_group = str(azure["resourceGroup"])
    scheduler_name = str(azure["schedulerName"])
    task_hub_name = str(azure["taskHubName"])
    budget_name = str(azure["budgetName"])

    account = _json_command(
        "az", "account", "show", "--subscription", subscription_id, cwd=pilot_root
    )
    subscription = _json_command(
        "az",
        "rest",
        "--method",
        "get",
        "--url",
        f"https://management.azure.com/subscriptions/{subscription_id}?api-version=2022-12-01",
        cwd=pilot_root,
    )
    scheduler = _json_command(
        "az",
        "durabletask",
        "scheduler",
        "show",
        "--resource-group",
        resource_group,
        "--name",
        scheduler_name,
        "--subscription",
        subscription_id,
        cwd=pilot_root,
    )
    task_hub = _json_command(
        "az",
        "durabletask",
        "taskhub",
        "show",
        "--resource-group",
        resource_group,
        "--scheduler-name",
        scheduler_name,
        "--name",
        task_hub_name,
        "--subscription",
        subscription_id,
        cwd=pilot_root,
    )
    budget = _json_command(
        "az",
        "consumption",
        "budget",
        "show-with-rg",
        "--resource-group",
        resource_group,
        "--budget-name",
        budget_name,
        "--subscription",
        subscription_id,
        cwd=pilot_root,
    )
    access_token = _command(
        "az",
        "account",
        "get-access-token",
        "--tenant",
        str(azure["tenantId"]),
        "--query",
        "accessToken",
        "--output",
        "tsv",
        cwd=pilot_root,
    )
    user_object_id = _access_token_object_id(access_token)
    role_names = _json_command(
        "az",
        "role",
        "assignment",
        "list",
        "--assignee-object-id",
        user_object_id,
        "--scope",
        str(task_hub["id"]),
        "--role",
        "Durable Task Data Contributor",
        "--subscription",
        subscription_id,
        "--query",
        "[].roleDefinitionName",
        cwd=pilot_root,
    )

    lock_path = pilot_root / str(provenance["packageLockPath"])
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    dependencies = lock["dependencies"]["net10.0"]
    notifications = budget.get("notifications") or {}
    thresholds = sorted(
        value["threshold"]
        for value in notifications.values()
        if isinstance(value, dict) and value.get("enabled") is True
    )
    repository_root = pilot_root.parent
    return {
        "schemaVersion": "maf-managed-dts-observation/v1",
        "subscription": {
            "id": account["id"],
            "tenantId": account["tenantId"],
            "quotaId": subscription["subscriptionPolicies"]["quotaId"],
            "spendingLimit": subscription["subscriptionPolicies"]["spendingLimit"],
        },
        "scheduler": {
            "resourceGroup": scheduler["resourceGroup"],
            "name": scheduler["name"],
            "endpoint": scheduler["properties"]["endpoint"],
            "sku": scheduler["properties"]["sku"]["name"],
            "state": scheduler["properties"]["provisioningState"],
            "publicNetworkAccess": scheduler["properties"].get("publicNetworkAccess"),
            "ipAllowlist": scheduler["properties"].get("ipAllowlist", []),
        },
        "taskHub": {
            "name": task_hub["name"],
            "state": task_hub["properties"]["provisioningState"],
            "id": task_hub["id"],
        },
        "budget": {
            "name": budget["name"],
            "amount": budget["amount"],
            "timeGrain": budget["timeGrain"],
            "notificationThresholds": thresholds,
        },
        "role": (
            "Durable Task Data Contributor"
            if "Durable Task Data Contributor" in role_names
            else None
        ),
        "principal": {
            "objectId": user_object_id,
            "type": account["user"]["type"],
            "authenticationSource": "AzureCLI",
        },
        "provenance": {
            "sourceRevision": _command(
                "git", "rev-parse", "HEAD", cwd=repository_root
            ),
            "dotnetSdk": _command("dotnet", "--version", cwd=pilot_root),
            "rid": _rid(_command("dotnet", "--info", cwd=pilot_root)),
            "packageLockSha256": _sha256(lock_path),
            "pilotSourceSha256": _pilot_source_sha256(pilot_root),
            "packages": {
                "azureIdentity": dependencies["Azure.Identity"]["resolved"],
                "agentFrameworkDurableTask": dependencies[
                    "Microsoft.Agents.AI.DurableTask"
                ]["resolved"],
                "agentFrameworkWorkflows": dependencies[
                    "Microsoft.Agents.AI.Workflows"
                ]["resolved"],
                "durableTaskClientAzureManaged": dependencies[
                    "Microsoft.DurableTask.Client.AzureManaged"
                ]["resolved"],
                "durableTaskWorkerAzureManaged": dependencies[
                    "Microsoft.DurableTask.Worker.AzureManaged"
                ]["resolved"],
            },
        },
    }
