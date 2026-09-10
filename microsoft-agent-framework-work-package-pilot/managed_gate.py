"""Public CLI for the managed DTS durability pilot gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from azure_observation import observe
from evidence import create_evidence_directory, write_evidence
from isolation import capture_boundaries, path_failures
from process_controller import run_probe
from schema_validation import validate


def load_json(path: str) -> dict[str, object]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected object in {path}")
    return value


def as_object(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def digest(value: dict[str, object]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_probe_environment(
    config: dict[str, object], pilot_root: Path
) -> tuple[dict[str, str], list[str]]:
    azure = as_object(config.get("azure"))
    configured_path = azure.get("connectionEnvFile")
    if configured_path is None:
        return {}, []
    if not isinstance(configured_path, str) or not configured_path:
        return {}, ["security.connection-environment-path-invalid"]
    path = (pilot_root / configured_path).resolve()
    if not path.is_file():
        return {}, ["security.connection-environment-file-missing"]

    environment: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, value = line.partition("=")
        if not separator or not name:
            return {}, ["security.connection-environment-file-invalid"]
        lowered = name.lower()
        if name != "DURABLE_TASK_SCHEDULER_CONNECTION_STRING" and any(
            marker in lowered for marker in ("secret", "password", "token", "key")
        ):
            return {}, [f"security.credential-in-environment-file:{name}"]
        if name == "DURABLE_TASK_SCHEDULER_CONNECTION_STRING":
            environment[name] = value

    actual = environment.get("DURABLE_TASK_SCHEDULER_CONNECTION_STRING")
    expected = (
        f"Endpoint={azure.get('endpoint')};"
        f"TaskHub={azure.get('taskHubName')};Authentication=DefaultAzure"
    )
    if actual != expected:
        return {}, ["security.connection-string-target-mismatch"]
    return environment, []


def preflight_failures(
    config: dict[str, object], observation: dict[str, object]
) -> list[str]:
    failures: list[str] = []
    if observation.get("schemaVersion") != "maf-managed-dts-observation/v1":
        failures.append("observation.schema-version-mismatch")
    if config.get("schemaVersion") != "maf-managed-dts-gate/v1":
        failures.append("config.schema-version-mismatch")
    approval = as_object(config.get("operatorApproval"))
    if approval.get("accepted") is not True:
        failures.append("approval.operator-not-accepted")
    if approval.get("scope") != "isolated-agent-framework-pilot":
        failures.append("approval.scope-mismatch")

    azure = as_object(config.get("azure"))
    for name in azure:
        lowered = name.lower()
        if any(marker in lowered for marker in ("secret", "password", "token", "key", "connectionstring")):
            failures.append(f"security.stored-credential-field:{name}")
    if azure.get("authentication") != "DefaultAzure":
        failures.append("security.authentication-not-default-azure")

    subscription = as_object(observation.get("subscription"))
    scheduler = as_object(observation.get("scheduler"))
    task_hub = as_object(observation.get("taskHub"))
    budget = as_object(observation.get("budget"))
    principal = as_object(observation.get("principal"))
    comparisons = (
        (azure.get("subscriptionId"), subscription.get("id"), "subscription-id"),
        (azure.get("tenantId"), subscription.get("tenantId"), "tenant-id"),
        (azure.get("resourceGroup"), scheduler.get("resourceGroup"), "resource-group"),
        (azure.get("schedulerName"), scheduler.get("name"), "scheduler-name"),
        (azure.get("endpoint"), scheduler.get("endpoint"), "scheduler-endpoint"),
        (azure.get("taskHubName"), task_hub.get("name"), "task-hub-name"),
        (
            azure.get("developerPrincipalObjectId"),
            principal.get("objectId"),
            "developer-principal-object-id",
        ),
    )
    for expected, actual, label in comparisons:
        if expected != actual:
            failures.append(f"azure.{label}-mismatch")
    if scheduler.get("sku") != "Consumption":
        failures.append("azure.scheduler-sku-not-consumption")
    if scheduler.get("state") != "Succeeded":
        failures.append("azure.scheduler-not-ready")
    if task_hub.get("state") != "Succeeded":
        failures.append("azure.task-hub-not-ready")
    if scheduler.get("publicNetworkAccess") != "Enabled":
        failures.append("azure.public-network-not-enabled")
    if scheduler.get("ipAllowlist") != azure.get("ipAllowlist"):
        failures.append("azure.ip-allowlist-mismatch")
    if principal.get("type") != "user" or principal.get("authenticationSource") != "AzureCLI":
        failures.append("azure.developer-identity-not-azure-cli-user")
    if subscription.get("spendingLimit") != "On":
        failures.append("azure.spending-limit-not-active")
    if not budget:
        failures.append("azure.budget-unavailable")
    else:
        if budget.get("name") != azure.get("budgetName"):
            failures.append("azure.budget-name-mismatch")
        if budget.get("timeGrain") != "Monthly":
            failures.append("azure.budget-not-monthly")
        amount = budget.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            failures.append("azure.budget-amount-invalid")
        elif amount != azure.get("budgetAmount"):
            failures.append("azure.budget-amount-mismatch")
        thresholds = budget.get("notificationThresholds")
        if not isinstance(thresholds, list) or not {50, 80, 100}.issubset(set(thresholds)):
            failures.append("azure.budget-notifications-incomplete")
    if observation.get("role") != "Durable Task Data Contributor":
        failures.append("azure.data-contributor-role-missing")

    packages = as_object(config.get("packages"))
    probe_config = as_object(config.get("probe"))
    if probe_config.get("command") != [
        "dotnet", "run", "--no-build", "--project", "ManagedDurabilityProbe", "--"
    ]:
        failures.append("probe.production-command-mismatch")
    expected_packages = {
        "azureIdentity": "1.17.1",
        "agentFrameworkDurableTask": "1.16.0-preview.260730.1",
        "agentFrameworkWorkflows": "1.16.0",
        "durableTask": "1.18.0",
    }
    labels = {
        "azureIdentity": "azure-identity",
        "agentFrameworkDurableTask": "agent-framework-durable-task",
        "agentFrameworkWorkflows": "agent-framework-workflows",
        "durableTask": "durable-task",
    }
    for name, expected in expected_packages.items():
        if packages.get(name) != expected:
            failures.append(f"provenance.{labels[name]}-version-mismatch")
    expected_provenance = as_object(config.get("provenance"))
    observed_provenance = as_object(observation.get("provenance"))
    provenance_comparisons = (
        ("sourceRevision", "source-revision"),
        ("dotnetSdk", "dotnet-sdk"),
        ("rid", "rid"),
        ("packageLockSha256", "package-lock"),
        ("pilotSourceSha256", "pilot-source"),
    )
    for field, label in provenance_comparisons:
        if expected_provenance.get(field) != observed_provenance.get(field):
            failures.append(f"provenance.{label}-mismatch")
    observed_packages = as_object(observed_provenance.get("packages"))
    observed_package_names = {
        "azureIdentity": "azureIdentity",
        "agentFrameworkDurableTask": "agentFrameworkDurableTask",
        "agentFrameworkWorkflows": "agentFrameworkWorkflows",
        "durableTaskClientAzureManaged": "durableTask",
        "durableTaskWorkerAzureManaged": "durableTask",
    }
    for observed_name, config_name in observed_package_names.items():
        if observed_packages.get(observed_name) != packages.get(config_name):
            failures.append(f"provenance.{observed_name}-mismatch")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--config", required=True)
    evaluate_parser.add_argument("--boundaries", required=True)
    evaluate_parser.add_argument("--evidence-root", required=True)
    observe_parser = subparsers.add_parser("observe")
    observe_parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    config = load_json(args.config)
    pilot_root = Path(__file__).resolve().parent
    if args.command == "observe":
        print(json.dumps(observe(config, pilot_root), indent=2, sort_keys=True))
        return 0
    config_schema = load_json(str(pilot_root / "managed-gate-config.schema.json"))
    config_schema_failures = validate(config, config_schema)
    failures = [f"config.schema:{failure}" for failure in config_schema_failures]
    observation: dict[str, object] = {}
    if not failures:
        try:
            observation = observe(config, pilot_root)
        except (
            AttributeError,
            IndexError,
            OSError,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            subprocess.SubprocessError,
        ) as exc:
            failures.append(f"observation.failed:{type(exc).__name__}")
    failures.extend(preflight_failures(config, observation))
    boundaries = load_json(args.boundaries)
    expected_boundaries_digest = as_object(config.get("provenance")).get(
        "protectedBoundariesSha256"
    )
    if digest(boundaries) != expected_boundaries_digest:
        failures.append("boundaries.inventory-digest-mismatch")
    evidence_root = Path(args.evidence_root).resolve()
    state_root = evidence_root.parent / "state"
    repository_root = pilot_root.parent
    unsafe_path_failures = path_failures(
        boundaries, repository_root, pilot_root, evidence_root, state_root
    )
    failures.extend(unsafe_path_failures)
    before, before_boundary_failures = capture_boundaries(boundaries, repository_root)
    failures.extend(before_boundary_failures)
    probe: dict[str, object] = {"started": False}
    if not failures:
        environment, environment_failures = load_probe_environment(config, pilot_root)
        failures.extend(environment_failures)
    if not failures:
        try:
            probe, probe_failures = run_probe(
                config,
                pilot_root,
                state_root,
                environment,
            )
            failures.extend(probe_failures)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            probe = {"started": False}
            failures.append(f"probe.failed:{type(exc).__name__}")
    after, after_boundary_failures = capture_boundaries(boundaries, repository_root)
    failures.extend(after_boundary_failures)
    changed = sorted(name for name, value in before.items() if after.get(name) != value)
    failures.extend(f"boundary.changed:{name}" for name in changed)
    result = {
        "schemaVersion": "maf-managed-dts-evidence/v1",
        "decision": "go-managed-pilot" if not failures else "no-go-managed-pilot",
        "failures": failures,
        "configDigest": digest(config),
        "observationDigest": digest(observation),
        "operatorApproval": as_object(config.get("operatorApproval")),
        "approvedAzure": {
            name: value
            for name, value in as_object(config.get("azure")).items()
            if name != "connectionEnvFile"
        },
        "observation": observation,
        "probe": probe,
        "boundaries": {
            "before": before,
            "after": after,
            "changed": changed,
            "unchanged": not changed
            and not before_boundary_failures
            and not after_boundary_failures,
        },
    }
    evidence_schema = load_json(str(pilot_root / "managed-gate-evidence.schema.json"))
    evidence_schema_failures = validate(result, evidence_schema)
    if evidence_schema_failures:
        result["failures"].extend(
            f"evidence.schema:{failure}" for failure in evidence_schema_failures
        )
        result["decision"] = "no-go-managed-pilot"
    unsafe_evidence_root = any(
        failure.startswith("isolation.evidence-") for failure in unsafe_path_failures
    )
    if not unsafe_evidence_root:
        try:
            evidence_directory = create_evidence_directory(evidence_root)
            result["evidenceDirectory"] = str(evidence_directory)
            write_evidence(evidence_directory, result)
        except OSError as exc:
            result["failures"].append(f"evidence.write-failed:{type(exc).__name__}")
            result["decision"] = "no-go-managed-pilot"
            result.pop("evidenceDirectory", None)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["decision"] == "go-managed-pilot" else 2


if __name__ == "__main__":
    raise SystemExit(main())
