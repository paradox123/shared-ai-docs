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

For the original admission-only path, the control context is the completed
admission attempt and an explicit null head. The later slices below add sessions,
attempts, live commands, transfer and forced takeover. Worker evidence has `kind: service`;
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

## Recoverable external fake Codex attempt (Ticket 04)

The worker now has an explicit fake-agent execution mode. A typed Agent Framework
`FakeCodexAttemptV1` graph runs deterministic preparation followed by a regular
executor calling the external `AgentSessionAdapter/v1` HTTP boundary. Neither
executor is a model agent. The fake service owns an independent SQLite session
receipt; PostgreSQL owns the product attempt, redacted response, ordered history
and processing decision.

Run the full isolated process proof, including real SIGKILL boundaries:

```bash
python3 -m unittest tests.test_fake_codex_attempt -v
```

For a manual local run, first start the controlled external service (choose a
free loopback port and a disposable receipt file):

```bash
python3 tests/fake_codex_provider.py --port 5091 --database /tmp/wpcp-fake-session.sqlite
```

With an admitted run and `WPCP_CONNECTION_STRING` set for its pilot database:

```bash
dotnet src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll \
  --fixture tests/Wpcp.BlackBox.Tests/fixtures/synthetic-provider-redaction-fixture.json \
  --run-id <run-id> --worker-id worker-one \
  --fake-agent-origin http://127.0.0.1:5091 --reject-blocked true

dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 attempt \
  --run-id <run-id> --attempt-id <attempt-id>
```

Use `run` to find the `fake-codex` activity and its attempt. The authenticated
`GET /api/v1/runs/{runId}/attempts/{attemptId}` returns that attempt, admission
provenance and its canonical events. `session.originalResult` and
`AgentResultObserved` retain the redacted blocked observation; configured
`--reject-blocked true` creates a separate `AgentResultRejected` referencing it.
The attempt then reports `semantic-rejection` while the external session remains
`blocked`. Both the selected attempt and full run include `openInCodex` with
`mode: unsupported`, `sameSession: false`, `appTaskVisible: false`, no URL and
reason `fake-adapter-has-no-codex-app-session`. No Codex app task or fork is created.

`--pause-at after-session-start`, `after-session-mapping`, or
`after-result-observed` emits a JSON boundary marker and waits for the process to
be killed. Launch a replacement worker against the **same database, run, fake
origin and reject policy**, omitting the pause option. It adopts the saved
operation/session or uses the captured response; concurrent deliveries serialize.
Adapter origin and reject policy are bound to the original assignment, and a
conflicting redelivery is rejected before it contacts another provider. This
mode does not provide an implicit fresh retry. Keep the fake receipt file until
recovery verification finishes.

The fake service's `--scenario` can reproduce `process-failure` (a child exits
17), `timeout`, `transport-failure`, `contract-incompatible`, `schema-failure`,
`malformed-json`, and `infrastructure-failure`. `--agent-timeout-ms` configures the
worker timeout (default 10000; use 500 for the controlled two-second timeout).
Process, timeout, transport, contract, schema and infrastructure failures, plus
`blocked` and `semantic-rejection`, remain distinct in public diagnostics;
malformed JSON maps to `schema-failure`.
An unavailable database produces an `infrastructure-failure` worker response,
without pretending to have appended history to that database. A worker exit of
zero means the delivery and its diagnostic outcome were persisted, including a
controlled failure; inspect the attempt state for the agent outcome.

This proof uses explicit local graph redelivery, independent API/CLI/worker and
fake-provider processes, and real disposable PostgreSQL. It does not wire this
new graph into automatic managed DTS dispatch, prove real Codex capabilities,
or exercise live repository writes. The existing managed durability gate and
LangGraph pilot remain separate. See the
[Ticket 04 evidence](../openspec/changes/archive/2026-09-11-recover-fake-codex-attempt/implementation-evidence.md).

## Human Request continuation in the controlled Codex session (Ticket 06)

A blocked or semantic-rejected fake attempt now exposes a redacted
`session.humanRequest` through `run` and `attempt`. It identifies the selected
attempt and session, current phase, expected head, problem, evidence, permitted
actions, and the current control context. It is durable product state: API or
worker replacement does not require the original process, receipt file, or
database-table access to inspect it.

Read the target and its current fences first. Use fresh `control` values from
`run` for every control command, because an accepted decision changes the run
version.

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 attempt \
  --run-id <run-id> --attempt-id <attempt-id>

dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 claim --run-id <run-id> \
  --target-attempt-id <attempt-id> --expected-run-version <version> \
  --expected-head-sha null --lease-epoch <epoch>
```

The current Control Lease holder can make exactly one of these continuation
decisions for an open request. Each requires the request and command UUIDs plus
the same current target/version/head/epoch fences as `claim`:

| Decision | Result |
| --- | --- |
| `resume` | Uses the selected, original session ID. |
| `fork` | Creates a distinct session with `lineage.parentSessionId` and `lineage.origin: "fork"`. |
| `fresh-retry` | Creates a distinct session with no parent or imported conversation. It is different from Ticket 05 repository-effect `retry`. |

For example, substitute `fork` or `fresh-retry` only when that is the intended
operator choice:

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 resume --run-id <run-id> \
  --target-attempt-id <attempt-id> --expected-run-version <version> \
  --expected-head-sha <head-or-null> --lease-epoch <epoch> \
  --request-id <human-request-uuid> --command-id <new-command-uuid>
```

Repeating the exact command ID returns its durable logical outcome; reusing it
with a different decision is rejected. Read the run again after completion to
see the original and continuation attempts, lineage, correlated operation, and
canonical events.

Read the redacted durable adapter receipt independently with the same command
identity:

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 continuation --run-id <run-id> \
  --command-id <continuation-command-uuid>
```

`open` resolves only the explicitly selected attempt/session and needs a
read-authorized caller, request ID, and command ID; it does not claim the lease
or change phase, head, effects, or session identity.

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 open --run-id <run-id> \
  --attempt-id <attempt-id> --request-id <human-request-uuid> \
  --command-id <new-command-uuid>
```

Treat `session.openInCodex` as a capability disclosure, not a promise that this
pilot has started a real Codex App task:

| Capability mode | Operator result |
| --- | --- |
| `same-session` | The controlled adapter opens only that saved session. |
| `handoff-confirmation-required` | `open` reports the limitation and creates nothing. The lease holder may later submit the separately fenced `handoff` decision, which creates one lineage-marked child session. |
| `unsupported` | The reason is shown; there is no hidden fallback, fork, or new run. |

After a selected same-session open, interactive `write` is a control action,
not a read action. It requires fresh provider authorization, the current Control
Lease, current fences, request/command IDs, and `--message`; its redacted
message/tool/result observations are appended to the same run history.

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 write --run-id <run-id> \
  --target-attempt-id <attempt-id> --expected-run-version <version> \
  --expected-head-sha <head-or-null> --lease-epoch <epoch> \
  --request-id <human-request-uuid> --command-id <new-command-uuid> \
  --message "<operator instruction>"
```

Run the Ticket 06 black-box proof with the Ticket 04 suite:

```bash
python3 -m unittest tests.test_fake_codex_attempt -v
```

It uses disposable PostgreSQL, separate API/CLI/worker/fake-provider processes,
and public HTTP/CLI read-back only. It proves restart-stable Human Requests;
Resume/Fork/Fresh Retry lineage; truthful open/handoff behavior; lease/fence and
duplicate-write rejection; and adoption of continuation/write success gaps
without a duplicate provider session or interaction.

## Repository base and effect recovery (Ticket 05)

A repository-managed delivery adds exact-base preflight and a durable repository
owner around the fake Agent Framework graph. Its controlled effects are a local
run branch, an external provider run marker, and the fake session. The public run
projection includes `repositoryExecution`: base evidence, active ownership,
stable operation IDs, receipts, queued recovery and concrete human decisions.

Run the isolated proof:

```bash
python3 -m unittest tests.test_repository_reconciliation -v
```

The worker accepts `--repository-plan <json-file>` with this structure (use actual
absolute paths and a real 40-character SHA from your disposable fixture):

```json
{
  "repository": {"repositoryId": "repo-1", "fullName": "pilot/fixture", "providerRepositoryId": 9001},
  "localPath": "/absolute/path/to/disposable/checkout",
  "remoteName": "origin",
  "baseBranch": "main",
  "providerOrigin": "http://127.0.0.1:5092",
  "agentOrigin": "http://127.0.0.1:5091",
  "expectedBaseSha": "<40-character-commit-sha>",
  "predecessorIssueNumber": null
}
```

Plan configuration is pinned to the admitted repository; changing its path,
branch, remote name or provider origins fails closed. Once registered, that
repository requires managed delivery and cannot bypass preflight through the
standalone `--fake-agent-origin` mode. The controlled repository provider in
`tests/repository_provider_fixture.py` reads a separate bare Git repository and
stores provider receipts independently. Its predecessor-completed fixture signal
stands for merged and closed; no merge is performed by the worker.

`retry`, `reconcile` and `retire` use the same required fence options as `claim`:
`--run-id`, `--target-attempt-id`, `--expected-run-version`, `--expected-head-sha`
and `--lease-epoch`. They require the current holder's fresh contributor access.
`adopt` additionally requires `--operation-id` and `--receipt-id` from a publicly
observed `adoptable` effect. Routes are `POST /api/v1/runs/{runId}/control/{action}`.
Read fresh fences with `run` after every accepted decision.

Commands persist a visible recovery request; deliver the same worker/run/plan to
process it. Reconcile reads existing effects without creating missing ones; Adopt
rereads the selected receipt and checks the immutable intent. Retry continues
missing work with the same IDs; it is not a fresh conversation retry. Only before
any effect intent exists may Retry refresh the recorded expected SHA from the
provider. Synchronize the local Git base explicitly; the worker never resets it.
A changed base after effect intent blocks new work while Reconcile/Retire can
still settle the old effects. Conflicting or ambiguous receipts require correction
of the external evidence and another reconciliation, not a forced adoption.

Retire settles existing effects and retains history, then ends active attempts,
clears the human lease and releases repository ownership. Uncertain effects keep
the run blocked and owned. A normal settled fake `blocked` result is also terminal
for this bounded slice and releases ownership; it does not qualify the result for
publication. An in-flight worker must stop before recovery commands are accepted.

Fault boundaries `after-git-effect`, `after-provider-effect`, `after-session-start`,
`after-session-mapping` and `after-result-observed` emit a marker and wait for an
external process kill. Restart with the same plan and without `--pause-at`.
The API, CLI, worker, PostgreSQL and providers remain separate processes; explicit
local delivery does not claim automatic DTS dispatch or live repository writes.
See the [Ticket 05 proof](../openspec/changes/archive/2026-09-11-reconcile-repository-effects/implementation-evidence.md).

An already-started standalone session cannot be promoted into a managed run:
its original base was not verified. First registration racing with an active
standalone delivery returns `repository-registration-busy`; stop that delivery
before registering. A settled recovery can finish after the provider advances:
it validates existing receipts against their historical intent and processes the
session read-only. Current-head equality is still mandatory before missing work.

For machine-readable proof snapshots, set `WPCP_PROOF_DIR` when running the
repository test module. It writes public state transitions, receipts, canonical
history, external operation counts and killed-worker exit codes without database
access or provider credentials. Additional crash hooks `after-reconciled-effect`
and `after-session-receipt` prove idempotent local receipt processing/finalization.

## Targeted active operations (Ticket 07)

The live adapter path adds `queue`, `interrupt` and `cancel` to the Operator CLI
and `POST /api/v1/runs/{runId}/agent-commands/{mode}` to the API. Select a concrete
`attemptId` from `run` or `attempt` read-back. `attempt.liveOperation` shows the
session, current operation/process, fence epoch and ordered command inbox.
The API rejects an omitted target; the CLI requires `--target-attempt-id`.
Unlike the admission control context's suggested latest target, live commands
can select any active attempt belonging to the run.

Each command requires `--command-id` (UUID), `--target-attempt-id`,
`--expected-run-version`, `--expected-head-sha` (explicit `null` when absent) and
`--lease-epoch`, plus these mode-specific options:

| Command | Additional options | Behavior |
| --- | --- | --- |
| `queue` | `--message` | Execute serially after the current operation in acceptance order. |
| `interrupt` | `--message`, `--reason` | Advance the operation fence, stop/reconcile the old process, execute this command next, then retain the previous FIFO order. |
| `cancel` | `--reason`, `--scope operation` | Stop the current operation; previously accepted queued commands remain eligible. |
| `cancel` | `--reason`, `--scope attempt` | Stop the chosen attempt and visibly reject its pending commands; no automatic retry. |

Use the latest version/head/lease from public read-back for each new decision.
Repeating the same command ID and redacted intent returns its persisted status;
substituting another target, message, mode, reason or scope conflicts. A second
interrupt/cancel during an outstanding stop conflicts. Admission, stop intent,
reconciliation and agent replies share the same Run History and command/operation
identities. Human stop decisions do not create repair rounds. An attempt's
completion timestamp is set only when its stop is confirmed.

The bounded local worker pass is independent of the accepting API or original
worker. It adopts durable receipts on every invocation. For an admitted,
unregistered disposable run, start the external controlled adapter and prepare
an activity (all commands below run from this directory):

```bash
python3 tests/live_codex_provider.py --port 5092 --database /tmp/wpcp-live-demo.sqlite
```

In another terminal with `WPCP_CONNECTION_STRING` set, run:

```bash
dotnet src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll \
  --fixture tests/Wpcp.BlackBox.Tests/fixtures/synthetic-provider-redaction-fixture.json \
  --run-id <run-id> --worker-id live-worker \
  --fake-agent-origin http://127.0.0.1:5092 --live-activity-key planning
```

A second activity key creates a separately targeted attempt; repeating a key
adopts the original assignment. Replacement processing needs only the persisted
run and database, with no adapter-origin or original-worker argument:

```bash
dotnet src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll \
  --fixture tests/Wpcp.BlackBox.Tests/fixtures/synthetic-provider-redaction-fixture.json \
  --run-id <run-id> --worker-id replacement --deliver-active true
```

Invoke this pass after command acceptance or external operation completion. It
stops at a still-running operation and processes other attempts independently.
An unavailable adapter or rejected receipt stays pending with a diagnostic in
Run History. This ticket uses explicit local worker passes; it does not install
an automatic polling service or DTS orchestration.

The controlled provider's `POST /operations/{operationKey}/complete` with `{}`
finishes its real child process and exposes a deterministic agent answer.
Its durable stop tombstone also blocks delayed starts. The adapter contract
requires immutable attempt/session/command/operation identities, fence epoch,
message, process ID, terminal response and explicit effect reconciliation.
The live fixture is incapable of repository writes (`effectScope: none`);
nonempty or conflicting effects block further delivery. Live runs cannot gain
later repository provenance or overlap repository registration. Real Codex
process control and reconciliation of live Git/GitHub writes remain Ticket 10.
The existing Ticket 04/06 blocked-session and Human Request paths remain separate.

Run the process proof and optionally export sanitized public HTTP evidence:

```bash
python3 -m unittest tests.test_active_agent_control -v
```

Set `WPCP_ACTIVE_PROOF_DIR` to an output directory to export each test's Operator
projection and canonical history. Tests cover API SIGKILL before response read,
worker SIGKILL around start/stop/dispatch/response, concurrent replacement,
stop-before-start, late output, parallel isolation, redaction and authorization.
See the [acceptance overview](../openspec/changes/archive/2026-09-12-control-active-agent-operations/implementation-evidence.md).


## Atomic Control Transfer and Forced Takeover (Ticket 08)

An observing contributor can request control, and the current holder can approve
or reject the identified request. Read-only repository users remain observers.
Use the same fresh `control` attempt/version/head/epoch fences as `claim`:

| CLI / HTTP control action | Additional arguments | Result |
| --- | --- | --- |
| `request-transfer` | `--request-id <new-uuid> --reason <text>` | One pending request; holder and epoch remain unchanged. |
| `approve-transfer` | `--request-id <pending-uuid> --reason <text>` | Recheck recipient permission, then atomically change holder and increment epoch. |
| `reject-transfer` | `--request-id <pending-uuid> --reason <text>` | Close that request and retain the holder. |
| `force-takeover` | `--reason <text>` | Another contributor takes control without approval or an administrator role. |

All routes use `POST /api/v1/runs/{runId}/control/{action}`. For example, a
contributor explicitly taking responsibility uses its own `WPCP_PROVIDER_TOKEN`:

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 force-takeover --run-id <run-id> \
  --target-attempt-id <attempt-id> --expected-run-version <version> \
  --expected-head-sha <head-or-null> --lease-epoch <epoch> \
  --reason "Continue while the previous holder is unavailable"
```

`run` exposes `control.transferRequest`, its requester, original holder/epoch,
reason and state. `authorization` includes `canRequestTransfer`,
`canDecideTransfer` and `canForceTakeover`. Only one request can be pending;
closed request IDs cannot be reused. Release, revocation and takeover supersede
pending requests. Duplicate/stale requests return a conflict with current state;
read fresh fences before submitting a new decision.

The API revalidates both the approving holder and the requested recipient.
GitHub's collaborator permission endpoint supplies current effective permission;
the stored login is only a lookup hint, and the returned immutable numeric ID
must match the requester. Missing access, renamed/replaced identity, malformed
provider responses and provider failures fail closed. The approving credential
needs repository Metadata read permission for this endpoint, as documented in
[GitHub's permission API](https://docs.github.com/en/rest/collaborators/collaborators#get-repository-permissions-for-a-user).
No requester token or separate membership list is persisted.

Ownership changes preserve the running attempt, session, phase, head and already
accepted effects. Old credentials (including a new token for the same former
holder), stale HTTP requests and writes from the former holder's opened window
cannot obtain mutating rights. A new holder can write the same opened session
using current fences. `ControlLeaseTransferred` and
`ControlLeaseForcedTakenOver` expose previous/new identities, event timestamp,
run identity, redacted reason and voluntary/forced mode in `events`.

Pending session writes receive a durable adapter tombstone by operation key.
The controlled adapter's `POST /control-operations/{operationKey}/fence` accepts
`sourceSessionId` and `action` and returns `AgentSessionAdapter/v1`, those exact
identities, `state: fenced|applied`, and an existing `receipt` if already applied.
The tombstone and adapter write serialize in the adapter's durable store; it
rejects delayed writes even if the original API died before receiving its reply.
Dispatch re-reads the durable command while holding the run lock, so restart
cannot deliver a fenced command. Pending live queue entries become visibly
rejected with `control-lease-changed`; the current autonomous operation continues.

A change of responsibility must not orphan an already accepted continuation or
recovery decision. The API returns these explicit 409 conflicts when settlement
must finish first:

- `control-continuation-pending`: complete/recover the accepted continuation,
  then read fresh state and retry.
- `control-recovery-pending`: deliver the existing repository recovery request
  through the worker, then retry with fresh state.
- `control-active-delivery-pending`: a promoted live command has not yet recorded
  its process receipt; run replacement delivery to settle its existing identity.
- `control-effects-reconciled`: an external write already existed and was just
  adopted; read its receipt/current fences and repeat the ownership decision.
- `control-fencing-unavailable`: the adapter cannot prove a safe fence or receipt;
  restore that capability before retrying. Ownership remains unchanged.

These paths use bounded local process delivery. They do not claim real Codex App
process control or live GitHub-account verification; those remain Tickets 10/14.
Stop old API/worker binaries before upgrading the additive schema. Mixed-version
writers must not share the upgraded database. The local tests migrate disposable
databases only.

Run the public proof and optionally retain sanitized observations:

```bash
WPCP_TRANSFER_PROOF_DIR=/tmp/wpcp-transfer-proof \
  python3 -m unittest tests.test_control_transfer -v
python3 -m unittest tests.test_repository_reconciliation -v
```

See the [acceptance evidence](../openspec/changes/archive/2026-09-12-transfer-run-control-atomically/implementation-evidence.md).

## Reconnect and portable Run Dossier (Ticket 09)

The Operator API serves bounded canonical history and an authenticated SSE tail.
Run identity, event IDs and committed positions survive client/API/worker replacement,
including a failed run. Set `WPCP_ARTIFACT_ROOT` to the same dedicated absolute
directory in the API and worker environments before capturing artifact content.
Use a separate empty directory and database for historical restore.

| Public read | Result |
| --- | --- |
| `GET /api/v1/runs/{runId}/events?after=N&limit=250` | Events strictly after N; default 250, maximum 1000. |
| `GET /api/v1/runs/{runId}/events/stream` | SSE replay and tail, with `Last-Event-ID: N` or `?after=N`. |
| `GET /api/v1/runs/{runId}/artifacts` | Manifest, current availability and the artifact prerequisite `qualificationEligible`. |
| `GET /api/v1/runs/{runId}/artifacts/{artifactId}` | Verified bytes, SHA-256 and redaction-policy headers; HTTP 410 with metadata for unavailable evidence. |
| `GET /api/v1/runs/{runId}/checksums` | SHA-256 of the canonical current history and projection, plus artifact status. |
| `GET /api/v1/runs/{runId}/export` | Portable ZIP dossier of one consistent history/projection snapshot. |

Every read requires the existing fixture capability and current human repository
authorization. SSE revalidates on each page/poll and ends with `access-revoked`
when access fails. Writes await stream backpressure; idle tails emit keepalives.

Persist a page's `nextAfter` only after consuming its events. `lastPosition` is
the snapshot high-water mark and may be ahead of that delivered cursor. Continue
from `nextAfter` while `hasMore` is true. SSE uses the same event positions in its
`id` field. Reconnecting from an older, unacknowledged cursor deliberately replays
those events, so clients should process/checkpoint by stable event identity. A
future or negative cursor is rejected. Completion of the agent operation is not
required to read its committed history.

The CLI reads a page with `events --run-id <runId> --after <N>` and downloads a
dossier without replacing an existing output file:

```bash
dotnet src/Wpcp.OperatorCli/bin/Debug/net10.0/Wpcp.OperatorCli.dll \
  --base-url http://127.0.0.1:5080 export --run-id <run-id> --output run-dossier.zip
```

Artifacts use an inline adapter envelope with `mediaType` and `contentBase64`.
Content is decoded and redacted before any durable write. URI-only source events
retain their descriptor and add an explicit `external-artifact-unavailable` entry. UTF-8 text, JSON and
JSONL preserve sanitized content; opaque binary content containing a configured
UTF-8/UTF-16 canary is withheld. Invalid text/JSON/base64 is explicitly unavailable.
SHA-256 names bind the published bytes. Atomic create-only files precede database
references, making replay idempotent. A crash may leave unreferenced sanitized
bytes. Referenced files are verified on read and export; missing/corrupt files
block the artifact prerequisite for future qualification. Head qualification and
reviews remain the later qualification ticket's responsibility.

Observations over 16 KiB are exposed as artifact references in canonical event
envelopes and projections. Fake-session recovery uses its checksum-verified
sanitized original adapter response. Active-operation responses and continuation
receipts share the same artifact boundary. Controlled adapter responses are bounded
at 64 MiB; the local dossier importer accepts at most 256 MiB of expanded ZIP data.
These are pilot limits, not an unbounded streaming blob service. Redaction matches
configured canaries; production secret/PII discovery and retention require their
own policy. Keep policy versions distinct when changing the configured inventory.

The versioned `wpcp-run-dossier/v1` ZIP contains `manifest.json`, `history.json`,
`projection.json`, and `artifacts/<sha256>`. Its manifest carries core-file hashes,
artifact availability and policy metadata, admission provenance, adapter contracts,
execution runtime observations, exporter runtime, and framework/Durable Task
correlations. JSON canonicalization v1 orders object keys ordinally and preserves
array order. Use the declared file hashes for comparison; ZIP timestamps can vary.
Projection hashes describe the export snapshot, including its process observations.

For local restore, stop any worker intended for the destination, configure a fresh
pilot database through `WPCP_CONNECTION_STRING` and a separate `WPCP_ARTIFACT_ROOT`,
then run this local service command before starting/reading through the new API:

```bash
dotnet src/Wpcp.Worker/bin/Debug/net10.0/Wpcp.Worker.dll \
  --restore-dossier run-dossier.zip \
  --fixture tests/Wpcp.BlackBox.Tests/fixtures/synthetic-provider-redaction-fixture.json
```

Use a fixture whose redaction policy covers the dossier's canary inventory. Restore
validates core checksums, contiguous identities, artifact references and current
redaction policy before publication. It rejects existing run IDs. Missing or corrupt
artifact bytes are retained as explicit unavailable entries. Restored runs expose
the same public history/projection/artifact checksums and current repository access
checks, with `authorization.historical: true` and disabled control. They are
historical views: worker execution, session opening and lease revival are unavailable.
The public manifest remains the authority for current artifact availability when
immutable historical references describe their original capture status.

Run the isolated process proof:

```bash
python3 -m unittest tests.test_run_dossier -v
```

It uses independent API/CLI/worker processes, controlled provider HTTP boundaries,
two disposable PostgreSQL containers and separate artifact roots. The large case
injects a pre-commit crash, stops a worker at source event 5000, kills the API,
reconnects another reader, and compares more than 10,000 events through SSE/pages
and a fresh restore. It also scans the disposable databases, artifacts, worker logs,
export and client payloads for every configured canary category. API log providers
remain disabled. Real provider identities, live Codex and managed DTS dispatch are
covered by their separate pilot tickets.
