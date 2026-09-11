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

## Repository authorization and exclusive control (Ticket 03)

The API remains a loopback-only pilot with synthetic **issues**. Authorization
now uses the caller's GitHub credential on every request; fixture actor IDs and
local membership lists no longer grant access. `IRepositoryAuthorization` is the
provider-neutral boundary. GitHub `/user` supplies the immutable human ID and
`/repos/{owner}/{repo}` supplies effective `pull`/`push` permissions. Bot and
installation credentials cannot authorize human control. A provider outage,
malformed response, or mismatched repository ID denies access.

Each repository in the issue fixture needs `repositoryId`, `fullName` and
`providerRepositoryId` (GitHub's numeric ID). The binding is persisted at
admission and cannot silently change when configuration changes. Existing
fixture-only records without a binding fail closed with
`repository-binding-required`; use a fresh disposable pilot database rather
than inventing an authorization binding for historical data. No live database
was migrated for this ticket.

Supply `WPCP_FIXTURE_ACCESS_TOKEN` in both the API and CLI environments as before.
In the CLI environment, also supply `WPCP_PROVIDER_TOKEN` with that human's
GitHub user credential. The credential needs access to the configured repository;
GitHub's authenticated repository response must include effective permissions.
Tokens are never command arguments, persisted records, or output. The deprecated
`--actor-id` option is accepted and ignored for older clients. Production GitHub
requests use `https://api.github.com/`; the test harness alone sets
`WPCP_GITHUB_TEST_ORIGIN` to its controlled loopback server. Redirects are disabled.

Read a run and use the returned `control` values when making a decision:

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 run --run-id <run-id>

dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 claim --run-id <run-id> \
  --target-attempt-id <attempt-id> --expected-run-version <version> \
  --expected-head-sha null --lease-epoch <epoch>
```

`release` uses the same options and requires the current holder. `audit --run-id
<run-id>` reads sanitized authorization/control decisions; `events` reads
canonical history. Run projections expose `authorization.canClaim` and
`authorization.canRelease`. The API routes are:

- `POST /api/v1/runs/{runId}/control/claim`
- `POST /api/v1/runs/{runId}/control/release`
- `GET /api/v1/runs/{runId}/audit`

Claim/release compare target attempt, run version, explicit head SHA, lease epoch,
and freshly evaluated permission while holding a PostgreSQL row lock. Conflict
responses include the current decision for authorized readers; other callers
receive permission status without run content. Rejections append only security
audit, never the requested action. A recognized holder permission revocation is
a separate `ControlLeaseRevoked` security transition that advances version/epoch.
Regrant requires a new claim. Disconnect and token rotation for the same human
leave the lease intact; no token is retained for background permission checks.
An invalid token denies the request without guessing its owner or releasing a lease.

The control context is currently the completed admission attempt and an explicit
null head. Creating writer heads/attempts, live agent commands, transfer and forced
takeover belong to subsequent tickets. Worker evidence has `kind: service`;
human admission/control/audit records carry `kind: human`, provider and subject ID.
This separates identities asserted by the provider; it cannot detect automation
using a human's own credential.

Run the full isolated regression suite:

```bash
python3 -m unittest discover -s tests -v
```

The proof uses separate API, CLI and worker processes, real disposable PostgreSQL,
and a controlled external GitHub HTTP boundary. It tests the real GitHub adapter,
including permission revocation and provider errors, without live credentials or
provider writes. Three real human accounts and live GitHub integration remain
Ticket 14. See the [implementation evidence](../openspec/changes/archive/2026-09-11-enforce-repository-control-lease/implementation-evidence.md).
