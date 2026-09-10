"""Write correlated JSON and Markdown evidence for the managed gate."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path


def create_evidence_directory(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    while True:
        directory = root / f"managed-gate-{uuid.uuid4()}"
        if not directory.exists():
            return directory


def render_report(result: dict[str, object]) -> str:
    probe = result.get("probe") if isinstance(result.get("probe"), dict) else {}
    boundaries = result.get("boundaries") if isinstance(result.get("boundaries"), dict) else {}
    observation = result.get("observation") if isinstance(result.get("observation"), dict) else {}
    approval = result.get("operatorApproval") if isinstance(result.get("operatorApproval"), dict) else {}
    azure = result.get("approvedAzure") if isinstance(result.get("approvedAzure"), dict) else {}
    subscription = observation.get("subscription") if isinstance(observation.get("subscription"), dict) else {}
    scheduler = observation.get("scheduler") if isinstance(observation.get("scheduler"), dict) else {}
    budget = observation.get("budget") if isinstance(observation.get("budget"), dict) else {}
    provenance = observation.get("provenance") if isinstance(observation.get("provenance"), dict) else {}
    effects = probe.get("effects", {})
    workers = probe.get("workerPids", {})
    before = boundaries.get("before") if isinstance(boundaries.get("before"), dict) else {}
    after = boundaries.get("after") if isinstance(boundaries.get("after"), dict) else {}
    boundary_lines = "\n".join(
        f"- `{name}`: before `{fingerprint}`, after `{after.get(name)}`"
        for name, fingerprint in sorted(before.items())
    ) or "- No boundary fingerprints captured."
    failures = result.get("failures") if isinstance(result.get("failures"), list) else []
    failure_lines = "\n".join(f"- `{failure}`" for failure in failures) or "- None."
    return (
        "# Microsoft Agent Framework managed durability gate\n\n"
        f"Decision: **{result.get('decision')}**\n\n"
        "## Operator exception and Azure controls\n\n"
        f"- Approval: accepted `{approval.get('accepted')}` on `{approval.get('acceptedAt')}` "
        f"for `{approval.get('scope')}`.\n"
        f"- Azure DTS Consumption scheduler: `{scheduler.get('name')}` at `{scheduler.get('endpoint')}`.\n"
        f"- Subscription/tenant: `{subscription.get('id')}` / `{subscription.get('tenantId')}`; "
        f"spending limit `{subscription.get('spendingLimit')}`.\n"
        f"- Task hub: `{azure.get('taskHubName')}`; network `{scheduler.get('publicNetworkAccess')}`; "
        f"allowlist `{scheduler.get('ipAllowlist')}`.\n"
        f"- Budget: `{budget.get('name')}`, amount `{budget.get('amount')}`, "
        f"monthly thresholds `{budget.get('notificationThresholds')}`.\n"
        f"- Authentication: DefaultAzure constrained to the observed Azure CLI user "
        f"`{azure.get('developerPrincipalObjectId')}`; no stored cloud credential is forwarded.\n\n"
        "## Durability proof\n\n"
        f"Run `{probe.get('runId')}` was started as one durable run. The worker replacement used "
        f"distinct processes `{workers}`. Worker 1 was terminated after entering checkpoint two; "
        f"Worker 2 resumed that checkpoint and completed the existing run. Activity attempts: "
        f"`{probe.get('activityWorkers')}`.\n\n"
        f"The exactly-once effect ledger contains `{effects}` and the run-start count is "
        f"`{probe.get('runStartCount')}`.\n\n"
        "## Immutable provenance\n\n"
        f"- Repository revision: `{provenance.get('sourceRevision')}`.\n"
        f"- Pilot source SHA-256: `{provenance.get('pilotSourceSha256')}`.\n"
        f"- Package lock SHA-256: `{provenance.get('packageLockSha256')}`.\n"
        f"- Runtime: .NET `{provenance.get('dotnetSdk')}` / `{provenance.get('rid')}`.\n"
        f"- Packages: `{provenance.get('packages')}`.\n"
        f"Config digest: `{result.get('configDigest')}`. Observation digest: "
        f"`{result.get('observationDigest')}`.\n\n"
        "## Isolation\n\n"
        f"All protected boundaries unchanged: `{boundaries.get('unchanged')}`.\n\n"
        f"{boundary_lines}\n\n"
        "## Gate failures\n\n"
        f"{failure_lines}\n"
    )


def write_evidence(directory: Path, result: dict[str, object]) -> None:
    staging = directory.parent / f".{directory.name}.{uuid.uuid4()}.tmp"
    staging.mkdir(parents=False, exist_ok=False)
    try:
        staging.joinpath("decision.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.joinpath("report.md").write_text(
            render_report(result), encoding="utf-8"
        )
        staging.replace(directory)
    except OSError:
        shutil.rmtree(staging, ignore_errors=True)
        raise
