# Ticket 10: real runtime gate, stopped candidate

Status: **partial implementation; no-go; not ready for acceptance or archive**.
The missing native Codex lease boundary prevents the actual disposable issue
execution and interactive acceptance. No product repository was connected.

## Observed outcome

On 2026-09-12 the pinned real `codex-cli 0.153.4` ran behind the sibling worker.
The authenticated Operator read-back retained the same report after an API
replacement and worker replay:

- Run: `9b80e075-ff0b-4320-9753-755d63326c81`
- Attempt: `71922d73-d5d5-4e1e-9f53-4f6aee274bb8`
- StartFresh / Read / Resume session: `01a096ab-4f7a-7931-ace5-a9c59c95cc52`
- Fork: `01a096ab-67c9-76c3-b697-c305c5cb08ad`, with the original session as parent
- Final run state: `capability-unavailable`
- Gate reason: `native-client-lease-fencing-unverified`

The [public proof](evidence/real-runtime-public-proof.json) contains the full
Operator attempt, report and canonical events. It was obtained through HTTP/CLI,
not by reading the control-plane database. Its temporary filesystem paths are
historical evidence; the probe repositories and Codex homes were disposed.

## Requirement acceptance matrix

| Issue criterion | Expected behavior | Observed result and evidence | Status |
| --- | --- | --- | --- |
| Disposable repository only | No irreversible remote effect | The gate creates its own Git repository with empty templates and no global Git config; public `repository.remoteCount` is zero. Only owned local file/network canaries are used. | Proven for the executed probe; issue implementation remains unstarted. |
| Prerequisites before issue work | Pin runtime/contract, inspect methods/dependencies/tools/sandbox/session capability; stop on missing prerequisites | Binary, CLI version, generated stable protocol and canonical schema are checked. Drift and a missing Python interpreter produce public terminal failures. Sandbox checks run before the endpoint model turn. | Admission gate proven; native interaction prerequisite fails. |
| Complete canonical schema and separate endpoint projection | Preserve canonical conditions while sending an accepted endpoint schema | Canonical SHA-256 `457e7331f32ee67465787dc50b4c796a6d4f697d9a82c581f929eb5ca5f73c62` matches the original worker-result-v3 fixture. The real model completes the projected output-schema turn; exact synthetic output matches and complete validation passes. A completion with empty evidence is independently rejected locally. | Proven. |
| Real session operation matrix | Execute StartFresh, Read, Resume, Fork, Interrupt/Stop and safe Open with identities | The first five operations pass with explicit IDs in `capabilities`; the owned runtime group stops. Empty, unmaterialized sessions reject Resume/Fork; the successful proof first completes a synthetic turn. | Partial: safe native Open is not executed. |
| Same-session Open or confirmed handoff | Resolve the exact background session; no silent fork | The real thread reports `canAcceptDirectInput: true`. No supported native-client lease check has been verified. The Operator exposes no URL and no automatic handoff. The conformance Fork above is a protocol test, not a native-app handoff. | Blocked. |
| Interactive observations with lease/fencing | Native inputs/tools/results return to the same run and reject stale/non-holder writes | No native app writer was opened. Existing controlled-adapter lease tests remain green, but they cannot establish real-app fencing. | Not verified. |
| Crash before session mapping | Adopt exact existing receipt or end unsafe; never silently start twice | The real adapter is SIGKILLed after `thread/start` returns and before mapping. Public gate read-back exposes dispatching; replay returns `session-start-uncertain` with `newSessionStarted: false`. Separate normal replay retains the original complete report and session. | Proven unsafe branch; no claim of independent session adoption. |
| Process ownership, timeout and late output | Correlate process state with attempt/session and prevent stale state mutation | Public report has owning gate PID, supervisor group, runtime PID, times, timeout child PID and exit 124. An owned local command cannot print its post-timeout output. Crash cleanup checks that no live process remains in the group. | Process portion proven. Real issue output fencing into head/business state remains unverified. |
| Missing stable semantics stop visibly | No unsafe fallback and no change to LangGraph | Gate and worker retain a terminal no-go, with `issueWorkStarted: false`. There is no go override, native opening URL, implicit handoff or issue execution path in this gate. | Proven. |

## What the blocker means

The installed public protocol provides session operations and notifications.
Those are not a verified authorization callback for native desktop/TUI inputs.
A directly writable native session could accept a message without the Operator
checking repository access and the current run lease first. Merely importing its
events afterward cannot satisfy the requirement to reject unauthorized writes
before they happen. Opening it anyway, or silently substituting a fork, would
violate the requested behavior.

This is an **unverified mandatory integration capability**, not a claim that all
possible future Codex integrations are impossible. The next implementation needs
a supported native opening/handoff surface with enforceable pre-write ownership
and complete event return. Only then may tasks 2.3 and 2.4 proceed. The current
gate does not implement a general real `AgentSessionAdapter/v1` or execute issues.
The next section updates this initial assessment with a verified input hook;
the original stop must not be interpreted as a proven platform limitation.

## Follow-up 2026-09-13: trusted prompt hook

The Microsoft Agent Framework pilot now probes an actual `UserPromptSubmit`
hook, discovered with `hooks/list` and trusted for the exact reviewed command
hash through the public `thread/start.config` surface. Its files live only in
the disposable Codex home. No personal hook trust, global configuration or
native application database is changed.

Expected behavior: the synthetic denial prompt causes one blocked hook and a
completed turn under the original session, with no agent output. Observed:
the real runtime passes this test. The report preserves the session/turn IDs,
`hookStatus: blocked`, `turnStatus: completed`, and
`leaseIntegrationVerified: false` in `capabilities.promptHook`.

The [13 targeted tests](evidence/hook-followup-tests.txt) pass, including the
real endpoint, session operations, crash cleanup and public Operator tests.
The public proof is separately refreshed in
[the follow-up report](evidence/hook-followup/real-runtime-public-proof.json).

This corrects the earlier reasoning: `canAcceptDirectInput: true` does not mean
there is no pre-input hook. The documented hook exists and works in the pinned
runtime when its exact hash is trusted. The first exploratory invocation's
CLI trust-bypass flag did not make the hook run in app-server mode; an explicit
per-session trust configuration did. See the official
[hook contract](https://learn.chatgpt.com/docs/hooks) and
[configuration schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json).

The hook currently rejects only a fixed synthetic prompt; it is not the actual
authorization/lease bridge. Native opening, live contributor checks, tool
fencing and full event return remain implementation work in task 2.3. The
actual issue execution in task 2.4 remains unstarted. There is no user decision
or demonstrated platform impossibility blocking continued implementation.

## Validation and limits

- [Broad regression](evidence/regression-tests.txt): 130 discovered tests, 125
  passed and five explicitly opted-out live tests. This also retains Ticket 09's
  10,015-event / 12 MB restore proof and zero raw canary matches across 35 surfaces.
- [Final targeted checks](evidence/real-runtime-tests.txt): all 12 tests passed,
  including all five real opt-in cases and two tests added after broad discovery.
  Together the two runs cover 132 distinct tests. The final checks include the
  missing-interpreter failure and supervisor cleanup correction.
- Locked .NET restore and build pass with zero warnings/errors; see the
  [validation summary](evidence/validation-summary.json). Strict OpenSpec
  validation and the narrow diff check pass; unrelated
  pre-existing LLM-wiki changes were not edited.
- API, worker, CLI, disposable PostgreSQL and Codex are separate real processes.
  GitHub authorization is the existing controlled provider, and delivery is
  explicitly local. No new managed DTS dispatch or real multi-human identity
  claim is made.
- Only whitelisted synthetic protocol observations are written into the gate
  report. Raw upstream errors and private model reasoning are not exported.
  Native interactive redaction/return is unverified with native interaction.
- The model probe produces a synthetic blocked result, not a completed coding
  issue. The full canonical schema was not sent as a negative live test; the
  projection's acceptance and complete local rejection behavior were tested.

## Maintenance review

The code review pass kept three responsibilities separate: canonical contract
validation/projection, owned RPC process supervision, and deterministic gate
orchestration. The .NET worker uses existing redacted report storage and attempt
read-back rather than introducing another product history or database. State-root
and interpreter changes are fenced with the immutable assignment so recovery
cannot silently move to a fresh receipt directory. No existing fake session is
promoted to a real runtime attempt. No new abstraction for native UI control was
added before that boundary is actually supported.

The authoritative runtime contract is generated from the SHA-pinned binary.
The [official App Server documentation](https://learn.chatgpt.com/docs/app-server)
provided protocol orientation; all capability claims above come from the executed
pinned process, not documentation alone.
