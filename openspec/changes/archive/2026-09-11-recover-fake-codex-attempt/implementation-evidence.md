# Ticket 04 implementation evidence

Verified on 2026-09-11 against the working tree. Change: `recover-fake-codex-attempt`.

## Direct behavior evidence

The public test seam is `tests/test_fake_codex_attempt.py` in
`microsoft-agent-framework-work-package-pilot/`. The suite builds the actual .NET
API, CLI and worker; starts real disposable PostgreSQL; launches an external fake
provider process with independently durable SQLite receipts; and authenticates
separate Operator requests through the existing controlled GitHub boundary.
Product state is read solely through HTTP/CLI. No test reads product tables or
framework internals to infer business success.

| Acceptance criterion | Executed evidence |
| --- | --- |
| Stable external session/activity/attempt; deterministic work stays outside model agents | `test_external_attempt_has_ordered_redacted_transcript`: real typed MAF graph, one fake activity/attempt/session, operation key equals attempt ID |
| Numbered messages, tool calls/results, artifacts, controlled failure, redaction and causal order | Same test verifies source positions 1–5, source types, stable session/attempt IDs, predecessor event IDs and redaction metadata; raw canary absent in HTTP and worker output |
| Worker death without duplicate session/activity | `test_replacement_adopts_one_session_before_and_after_mapping`: SIGKILL at two boundaries, two concurrent replacement deliveries, external session count remains one, original event prefix unchanged and exactly one preparation/session/result event |
| Original blocked observation survives downstream rejection | `test_blocked_original_survives_downstream_rejection_and_capture_crash`: SIGKILL after capture, replacement preserves original result and session; one separate rejection references the original event; attempt is semantic-rejection, session is blocked |
| Publicly distinct failures | `test_failure_categories_are_public_and_preserve_originals`: process exit 17, real delayed HTTP timeout, disconnected transport, contract v99, invalid result schema, malformed JSON, provider 503; terminal redelivery leaves attempt unchanged |
| Storage infrastructure failure is explicit | `test_unavailable_store_is_infrastructure_failure_without_fabricated_history`: unavailable PostgreSQL endpoint gives exit 2 with infrastructure category, existing run remains admitted and no external session starts |
| Attempt selection and honest opening capability | `test_attempt_selection_is_authorized_and_open_capability_is_truthful`: second read-authorized Operator selects attempt by HTTP and CLI after API restart, reads original/rejection/history and unsupported same-session capability; unauthorized/bot access denied and unknown attempt is 404 |
| Recovery fails closed on inconsistent input | `test_inconsistent_adapter_correlation_and_transcript_fail_closed`: wrong operation key, sequence gap, conflicting replay, null event retain response and become schema failure |
| Adapter assignment cannot silently change | `test_redelivery_cannot_change_durable_adapter_assignment`: another origin is rejected with agent-assignment-conflict and is never called |

## Red → green observations

- Original lifecycle-only worker left state `admitted` instead of `blocked`.
- Recovery and capture tests initially failed because the requested pause boundary
  was never reached; after implementation, actual SIGKILL/replacement passed.
- Failure matrix initially mislabeled process exit and timeout as blocked, ignored
  incompatible contracts, and surfaced transport/parser exceptions. It now retains
  redacted response first and publishes the individual category.
- Attempt-detail route initially returned 404; implemented HTTP and CLI now agree.
- Missing infrastructure category, a null event causing an uncaught exception, and
  assignment conflict causing an uncaught framework wrapper each had a failing
  public process check before their fixes.

## Validation

From the pilot directory:

```text
dotnet restore --locked-mode Wpcp.WorkPackageControlPlane.sln
  succeeded
python3 -m unittest discover -s tests -v
  Ran 42 tests in 30.452s — OK
```

The test harness builds the solution with `--no-restore`; the standalone build
also passed with zero warnings/errors. From the repository root:

```text
openspec validate recover-fake-codex-attempt --strict
  Change 'recover-fake-codex-attempt' is valid
git diff --check
  passed
```

The final simplification pass consolidated fake worker option parsing with the
existing parser, extracted the reusable process harness instead of suppressing
inherited tests dynamically, and preserved framework error identity across its
reflection wrapper. All 42 tests passed after this pass. The storage helper uses
short row-locked transactions for correlated history/projection writes; its
separate session lock serializes worker delivery without holding the human
control row lock across HTTP calls.

## Scope and limitations

- The graph runs via pinned Agent Framework Workflows 1.16.0. This bounded slice
  explicitly re-delivers the local graph on worker replacement; it does not add
  automatic DTS scheduling of the new graph. The existing managed DTS probe was
  regression-tested through its local gate tests, not rerun against Azure here.
- No real Codex process, app-task visibility, same-session opening, fork/resume,
  live provider mutation or real three-human integration is claimed. The fake
  explicitly reports opening as unsupported. Later tickets own these behaviors.
- The local fake's idempotent operation receipt proves the controlled external
  success/local commit gap. Other effects and providers need their own
  reconciliation contracts (Ticket 05).
- Redaction covers configured controlled canaries, including decoded JSON string
  values. The external synthetic provider intentionally owns the original test
  input; only redacted copies enter product storage/history.
- Work began on top of uncommitted Ticket 03 and unrelated documentation/skill
  changes. They were preserved; unrelated work was not included in this change.
  The user accepted the implementation and its direct proof on 2026-09-11.


## Acceptance and archive

Accepted by the user on 2026-09-11 after the recorded proof: 8/8 black-box tests,
136 sanitized public observations, and three confirmed SIGKILL exits. Evidence
and source hashes were checked again before closeout. The proof artifacts are in
`.scratch/distributed-codex-work-package-control-plane/evidence/ticket-04-proof-2026-09-11/`.

The pre-archive DRY/SOLID/KISS pass inspected the current diff and adjacent
executor/storage/spec code; no further behavior-preserving refactoring was
needed. The subsequent full regression passed: 42 tests in 38.940 seconds.

Standard `openspec archive -y recover-fake-codex-attempt` created the canonical
`recoverable-fake-codex-attempt` spec with four requirements and archived this
spec-driven change. All artifacts and all six tasks were complete. Ticket 04
remains resolved with explicit user acceptance. README and issue links now point
to this archive. Work is on `main`; no feature-branch merge is required.
