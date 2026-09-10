# Microsoft Agent Framework managed durability pilot

This sibling probe proves the operator-approved Azure DTS exception without
changing the historical OSS gate result. It starts one durable Agent Framework
workflow, kills worker one inside the second activity, and requires worker two
to finish the same run with exactly-once committed effects.

The checked-in configuration contains Azure resource identities but no secret.
Authentication uses the developer's Azure CLI identity through
`Authentication=DefaultAzure`.

Run the reproducible checks from this directory:

```bash
dotnet restore --locked-mode ManagedDurabilityProbe/ManagedDurabilityProbe.csproj
dotnet build --no-restore ManagedDurabilityProbe/ManagedDurabilityProbe.csproj
python3 -m unittest tests/test_managed_gate_cli.py -v
python3 managed_gate.py evaluate \
  --config managed-gate-config.json \
  --boundaries protected-boundaries.json \
  --evidence-root evidence
```

The gate writes a unique directory containing `decision.json` and `report.md`.
A passing decision is named `go-managed-pilot`; it is not an OSS qualification.

## Observable-run control-plane slice

`Wpcp.Api`, `Wpcp.Worker`, and `Wpcp.OperatorCli` implement Ticket 02's
separate, local control-plane foundation. PostgreSQL owns the command inbox,
canonical `ImplementationRun` history, and rebuildable read projection. Worker
and API process records are supplemental evidence: Agent Framework and Durable
Task IDs never replace the product-owned run/event history.

Run its isolated black-box proof from this directory (Docker is required for a
disposable `postgres:17-alpine` instance):

```bash
dotnet restore --locked-mode Wpcp.WorkPackageControlPlane.sln
dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore
python3 -m unittest tests/test_control_plane_black_box.py -v
```

The test starts the API and three separate Operator CLI processes, restarts the
API, and invokes two independent worker processes. It reads state only through
the public HTTP/CLI surfaces and removes its uniquely named database container
on completion.

This is a loopback-only synthetic-provider harness, not production repository
authentication. Its API requires a fresh `WPCP_FIXTURE_ACCESS_TOKEN` supplied
outside command payloads; the test generates one in memory and never persists
or prints it. For a manual local invocation, export a new high-entropy value in
the API and Operator CLI environments. The checked-in fixture provides only
synthetic issues and permissions; Ticket 03 remains responsible for real
repository-derived authorization and the Control Lease.
