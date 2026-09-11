# Ticket 03 implementation evidence

Verified on 2026-09-10 against the working tree based on
`ac5166e5667de4895667cc4c415e9c0094755d69` using .NET SDK `10.0.203`.
This is public-surface behavior evidence for the isolated Microsoft pilot.

## Executed checks

From `microsoft-agent-framework-work-package-pilot/`:

```text
dotnet restore --locked-mode Wpcp.WorkPackageControlPlane.sln
  All projects are up-to-date for restore.
dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore
  Build succeeded. 0 warnings, 0 errors.
python3 -m unittest discover -s tests -v
  Ran 34 tests in 9.573s — OK
```

From the repository root:

```text
openspec validate enforce-repository-control-lease --strict
  Change 'enforce-repository-control-lease' is valid
git diff --check
  Passed
```

The final suite includes nine public control-plane tests and 25 existing managed
pilot gate/controller tests. The nine public tests start real API/CLI/worker
processes and disposable PostgreSQL; only the external GitHub HTTP service is
controlled test infrastructure. Tests read behavior through HTTP/CLI, never
through application table inspection or edits. The test database, API processes,
provider server and temporary fixture directory are cleaned up afterward.

## Acceptance mapping

| Ticket criterion | Public behavior verified |
| --- | --- |
| Reader observes, cannot mutate | Reader reads projection/history/audit; admission, claim and release are denied. Spoofing a contributor in the payload does not elevate access. |
| Exactly one contributor controls | Two API processes race different contributors against one run; statuses are exactly 200 and 409, with one claim event. The non-holder cannot release. |
| Lease belongs to the human | Claiming CLI exits, API is replaced, another CLI uses a different token for the same provider ID; holder, epoch and claimed time remain unchanged and that human can release. |
| All fences checked | Incorrect and omitted target, version, head and epoch values are independently rejected. Returned current state matches readback and history remains at positions 1 and 2. |
| Rejections have no requested effect | Denied requests preserve lease/run history; sanitized security audit is separate. Non-readers receive no current run state. Provider errors never relinquish the lease. |
| Provider rights are current | Read-triggered and mutation-triggered downgrade revoke the holder; full access removal denies readback; regrant cannot reuse the old decision and requires a fresh claim. |
| Human/service identities remain distinct | Admission and claim history have the same human provider subject; bot rejection audit and worker evidence carry service identities. Tokens and harness capability do not appear in public output. |
| Repository remains pinned | Changing the configured/provider numeric repository ID after admission cannot retarget an existing run or disclose its correlation through repeated admission. |
| Ticket 02 remains intact | Original admission idempotency, conflicting command reuse, separate clients, API/worker replacement, timing axes, canonical positions, provenance and controlled-canary redaction pass. |

## TDD and review

Behavioral failures were observed before each implementation slice: payload
impersonation returned 201, absent control routes returned 404, stale release
fences executed the action, revocation left the holder intact, CLI claim was
unsupported, admission history lacked human identity, and changed repository
configuration exposed an old run (including via admission conflict).
Each regression now passes through the public API/CLI surface.

The final DRY/SOLID/KISS review kept provider evaluation behind
`IRepositoryAuthorization`, consolidated run decisions under one database lock,
kept audit separate from canonical business events, removed unused client actor
transport, avoided reading projections before authorization, and simplified the
provider HTTP request lifetime. The complete suite was rerun afterward.

## Verification limits and operating boundaries

- No live GitHub credentials or three real human accounts were used. Live provider
  integration remains Ticket 14; this ticket proves the adapter against a controlled
  HTTP provider with real surrounding application processes and storage.
- No Azure request, GitHub write, deployment or existing pilot database migration
  was performed. The current head is explicitly null and the current context is
  the completed admission attempt; later tickets create writer attempts/heads.
- Permission revocation is recognized on an identified holder's next request.
  Unidentifiable expired/revoked credentials deny access without guessing ownership;
  credentials are not retained for background revalidation. Provider changes after
  an authorization response cannot be atomic with PostgreSQL; the next request
  revalidates again. Ambiguous errors deny access without transferring the lease.
- Fixture-only historical rows without a pinned binding fail closed. No repository
  mapping is inferred from a changed configuration.
- Service identities reported by GitHub are rejected for human control. A service
  using a human-owned credential is indistinguishable from that human to this
  adapter; clients must keep human and worker credentials separate.
- Unrelated concurrent changes in CONTEXT.md, RAG documentation and shared skills
  were preserved; verification targeted this pilot and this OpenSpec change.

## Verified source fingerprints

SHA-256 fingerprints identify the files tested in this working tree:

- `8e4ecfba38109245f8bc0726b77e2d3317815942791fae01c4c2730533fc7eaa` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Api/Program.cs`
- `7817a4624166adccb434a9845c10632119a573ff01af9b498c80d5613b3ede2d` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Api/GitHubRepositoryAuthorization.cs`
- `b11469c5723b38be2c97e4507a2b6d4c3faf89f1a5932946274c208c5a6c9a5f` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Domain/RepositoryAuthorization.cs`
- `575c2c1cc9567d788ea9e171d117f2eae64dd02d21cab7eccc7a1088f2de1ae4` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Domain/RunControl.cs`
- `d9da4a6daf9a8ddaf12f8dd90cef548c6321822291f9f67be8f4a102bc1cf14b` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Domain/ImplementationRunContracts.cs`
- `212f3124c36f0d1e661de9ff7136fb223409a34173911a18c8718c5e4736d9b7` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Domain/SyntheticProviderFixture.cs`
- `4a16713cc81d62a4cb7da7e51c567e8da7ae87ba75edc44bbf1206b4aa81c239` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Storage.Postgres/PostgresRunControl.cs`
- `becf3c6248dbc5a6112c1f868c95b897b078568b744ae358085083201ae14f29` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.Storage.Postgres/PostgresImplementationRunStore.cs`
- `7e194f17ecc8f74543e04b8110c6cb11ed6d0fe4af5451678cd86341edb3e62e` — `microsoft-agent-framework-work-package-pilot/src/Wpcp.OperatorCli/Program.cs`
- `1cd9378aa06dea713d5d16a76c5edb9cf73021c069fa1057fe805d476b61bfa4` — `microsoft-agent-framework-work-package-pilot/tests/test_control_plane_black_box.py`
- `39efc34ebd4c2d96c4c8a90c5d9e713af96b38d9dd6cfe01db9d2d6f4248c91a` — `microsoft-agent-framework-work-package-pilot/tests/github_provider_fixture.py`
- `e2fc9959b59b138664cfb4adb5adc2048cca1d8a36b1812d79b53fb356b94b4a` — `microsoft-agent-framework-work-package-pilot/tests/Wpcp.BlackBox.Tests/fixtures/synthetic-provider-redaction-fixture.json`

## Accepted and archived (2026-09-11)

The user accepted the freshly captured public HTTP/CLI proof and explicitly
requested archive, commit and push. The standard OpenSpec archive command
synchronized both canonical specs and archived the complete six-task change.
The final pre-archive DRY/SOLID/KISS inspection required no further code changes;
all 12 recorded implementation fingerprints still match. The build again had
zero warnings/errors and all 34 tests passed (10.360s).

- [Accepted execution log](../../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-03-2026-09-11/proof.log)
- [Original HTTP/CLI responses](../../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-03-2026-09-11/http-cli-responses.jsonl)
- [Reproducible proof script](../../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-03-2026-09-11/prove.py)
