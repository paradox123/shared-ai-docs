# Ticket 10: real Codex issue and same-session continuation

Status: **accepted by the user and closed, 2026-09-13**.

The Microsoft Agent Framework worker starts the pinned real Codex runtime in its
own disposable repository. The human opens that exact session in the official
native Codex TUI, completes the bounded issue, and retains observations in the
same PostgreSQL Run History. The earlier missing integration has been implemented;
it was not a requirement gap or a proven platform limitation.

## Acceptance evidence

| Requirement | Observed behavior | Evidence |
| --- | --- | --- |
| Disposable work, no remote effects | The adapter creates its own local Git repository, commits a synthetic baseline with no remote, and fixes `greeting.py`. Original supplied tests must remain unchanged and pass independently. | [Actual issue result, commands and history](evidence/native/real-issue.json) |
| Prerequisites before issue work | Executable SHA/version, stable protocol digest, complete canonical contract, exact dependencies, trusted tool hook, sandbox writes/network denial and timeout are checked. The separate endpoint-schema turn must validate completely before native issue input is admitted. | Initial real-attempt events in [run history](evidence/native/real-issue.json); [runtime operation proof](evidence/hook-followup/real-runtime-public-proof.json) |
| Full output contract | Endpoint-only projection preserves the byte-identical canonical schema. Worker validation checks the complete result; the actual issue returns valid `completed` output including red/green evidence. | [Canonical tests](../../../../microsoft-agent-framework-work-package-pilot/tests/test_codex_contract.py), [completed result](evidence/native/real-issue.json) |
| StartFresh, Read, Resume, Fork | Background start and native read use the same ID. Public Operator Resume keeps it; Fork creates a different ID with the original parent. Replaying a command preserves its receipt. | [Resume](evidence/native/native-resume.json), [Fork](evidence/native/native-fork.json) |
| Interrupt / Stop | Native interruption reaches the real turn and returns its correlated interrupted terminal event. Runtime loss stops the owned Codex process; timeout/group cleanup are separately exercised. | [Native interrupt](evidence/native/native-interrupt.json), [replacement](evidence/native/native-replacement.json), [process probes](evidence/hook-followup/real-runtime-public-proof.json) |
| Exact native opening | The official pinned TUI displays the background conversation and sends the actual implementation prompt through the same session. `appTaskVisible:false` accurately describes absence from the desktop sidebar. No session is silently forked. | [Native terminal recording](evidence/native/native-issue-tui.txt), [real issue session ID](evidence/native/real-issue.json) |
| Every write checks current authority | Native prompts, PreToolUse checks and MCP command execution call the existing authenticated, serialized Operator write boundary. Read-only native sandbox and gateway method filtering prevent direct command/configuration bypass. | [Native tests](evidence/native-tests.txt), [takeover proof](evidence/native/native-takeover.json) |
| Revocation and late observations | Permission withdrawal prevents the requested file write. Late events retain run/attempt/session identity as `NativeObservationQuarantined`, with `qualifiesResult:false`. A private durable outbox retries delivery after interruptions. | [Revocation and late terminal result](evidence/native/native-revocation.json); [outbox recovery](evidence/native/native-outbox-recovery.json) |
| Recovery without duplicate start | Exact completed receipts replay; replacement opens the same stored session. An uncertain session-start intent ends unsafe without dispatching a second start. | [Real adapter replacement](evidence/native/native-replacement.json), [SIGKILL gap proof](evidence/hook-followup/real-runtime-public-proof.json) |
| Visible failure on unsupported capabilities | Runtime/contract drift and unavailable required capabilities fail before issue work. The standalone diagnostic gate retains its original no-go because it deliberately has no interactive gateway. | [Gate tests](evidence/real-runtime-tests.txt), [historical gate assessment](preflight-history.md) |

The issue's canonical `completed` result is an observation of the human
continuation. It does not automatically approve a PR, advance repository Head,
or resolve the original Human Request. Those remain explicit workflow actions;
Ticket 10 does not claim a published PR or completion of later pilot tickets.

## Implementation boundary

`codex_adapter.py` owns one run, repository and isolated Codex home, protected by
an exclusive local process lock. Its stdio app-server is inaccessible to native
clients directly. `codex_open.py` checks the pinned binary and selected attempt,
then launches the official remote TUI through `codex_native_gateway.py`.

Only text prompts reach `turn/start`; UI sandbox/model/tool overrides do not
change the managed runtime. Native file execution is available through the
controlled `wpcp.execute` MCP tool. Each execution runs inside the existing
PostgreSQL-serialized authorization/lease/version/head/epoch/attempt check and
uses the real Codex sandbox with only the disposable repository writable and
network denied. A trusted PreToolUse hook checks authorization before each tool.

Interactive receipts use the existing redaction and Run History mechanisms.
Adapter service credentials are scoped to an exact origin; provider credentials
are held in memory and are not persisted in the observation outbox. The outbox
contains private runtime evidence and must not be committed. Recovery delivers
uncertain observations only as non-qualifying quarantine evidence.

## Validation and scope

The native acceptance suite uses separate API, worker, adapter, real Codex TUI,
real app-server and disposable PostgreSQL processes. Repository authorization is
tested through the existing controlled GitHub provider, including live changes
to its permission response. No claim of three real human accounts or production
GitHub integration is made; that remains Ticket 14.

The acceptance surface is the official native Codex **TUI**, not the desktop
sidebar. The capability reports that distinction. No private desktop database,
private IPC or fabricated app link is used. This satisfies same-session access;
the existing explicit Handoff requirement remains intact when direct opening is
unavailable.

Temporary paths in evidence are historical; test repositories and credentials
are disposed by the test harness. The LangGraph application is unchanged.
The [historical preflight record](preflight-history.md) documents the initial
no-go and its correction; it is no longer the status of the full real adapter.

## Final checks

- [Full opt-in regression](evidence/completed-regression.txt): **143/143 passed**, including the real runtime, native TUI, existing repository/control/recovery tests and 10,015-event dossier restore. No live tests were skipped.
- [Focused native recovery checks](evidence/native-recovery-tests.txt): **3/3 passed**, adding the simultaneous API/adapter crash case and strengthening actual hook-denial and bypass assertions. **144 distinct tests** are covered across both runs.
- [Locked restore and build](evidence/completed-build.txt): success, zero warnings and zero errors.
- `openspec validate prove-real-codex-runtime --strict` and scoped `git diff --check`: passed.
- [Machine-readable verification summary](evidence/completed-validation.json) records the actual issue IDs, red/green command exit codes and validation facts.

The maintenance review checked the shared workflow's existing fake path, real
canonical-validation branch, serialized control delivery and event redaction.
HTTP session transport is shared; canonical validation, owned process RPC,
native authorization and MCP execution retain distinct responsibilities. The
review corrected idle-reader events incorrectly advancing the writer's fence,
retained disconnected writers' observations, and added durable outage recovery.
All final source changes are covered by the runs above. Existing unrelated
wiki/RAG changes were preserved. The user accepted the result and requested the standard OpenSpec archive, commit and push on 2026-09-13.

## Accepted closeout — 2026-09-13

The user accepted Ticket 10 and authorized archive, commit and push. The standard
`openspec archive` path synchronized four requirements into the canonical
`real-codex-runtime-gate` specification and moved this complete `spec-driven`
change here. All eight tasks were complete; no incomplete-work exception was
needed. Ticket 10 remains `resolved`, with the user's acceptance recorded.

The pre-archive maintenance pass rechecked duplication, responsibilities and
complexity in the worker, RPC connection and native gateway. It found no further
refactoring necessary for this accepted change. Runtime behavior is unchanged
from the 144-test acceptance run; closeout adjusts documentation and spec paths.

Post-archive checks passed: 46/46 repository-wide strict OpenSpec validations,
two canonical-contract checks, complete archive-link verification, and both
working-tree and staged diff checks. The active change directory is absent.
