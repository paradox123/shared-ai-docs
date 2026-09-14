# Ticket 02 — two-axis review

Baseline: `a77418a82e7746918853f339ae566c5ac0090735`, the accepted Ticket 01
checkout. Initial implementation: `2cb7451`; corrections: `565d326`.
Both reviewers independently inspected `git diff a77418a...565d326` without
editing files or duplicating the full regression. Scope is the supplied
[Ticket 02](../../../.scratch/agent-framework-operator-gui/issues/02-eingereichtes-issue-als-hintergrundaktivitaet-starten.md)
and its explicit scenarios in the active OpenSpec change. Later ticket features
are excluded.

## Standards

Initial findings:

- **P2, documented contract:** Extracting the legacy disposable fixture into
  `prepare_disposable_issue` removed indentation inside the generated
  `GreetingTests` class. Its generated Python failed to compile, breaking the
  existing native implementation proof described in the pilot README and the
  retained CLI/local-agent route in ADR 0014.
- **P3, judgment call — possible Repeated Switches:** Independent Python and
  analysis flags selected workflow/resource/executor names in several places and
  admitted contradictory mode combinations.

Final reviewer report at `565d326`: **no unresolved Standards findings**.
The fixture's original indentation is restored. Independent literal extraction
and compilation pass; the real native implementation fixture also passes.
`AgentSessionMode` now selects one metadata mapping, and an entry guard rejects
incompatible Python/mode combinations. All callsites are consistent. The
remaining validation branches implement distinct result contracts and do not
warrant another refactoring finding. Recovery changes have corresponding
OpenSpec, documentation and focused HTTP/Chrome evidence.

## Spec

Initial findings:

- **P1:** An HTTP timeout finalized the analysis as failed, so a subsequently
  completed adapter receipt never supplied its real session or observations to
  central history. An isolated public HTTP probe reproduced `failed/timeout`,
  null session and zero observations after replacement, despite a completed
  external session. This violated the retained-observation/recovery scenario.
- **P2:** The malformed generated legacy fixture also violated Ticket 02's
  requirement to preserve existing CLI/Run/Dossier contracts.

Final reviewer report at `565d326`: **both findings resolved; no additional
actionable Spec findings**. Timeout and uncertain transport retain a running
attempt and a durable `reconciling` disposition. Preparation is committed before
PUT, covering a worker killed before it can record a timeout. Replacements reuse
the same operation/assignment, and the GUI displays reconciliation while polling.
Public tests cover both late receipts and connection refusal after worker death.
The legacy fixture is restored and verified. Analysis completion remains distinct
from implementation completion, and authorization/immutable-input boundaries
remain intact.

Initial totals: Standards 2 (worst P2); Spec 2 (worst P1). Final unresolved totals:
Standards 0; Spec 0. Regression and live acceptance results are recorded separately
in [issue-02-evidence.md](issue-02-evidence.md).
