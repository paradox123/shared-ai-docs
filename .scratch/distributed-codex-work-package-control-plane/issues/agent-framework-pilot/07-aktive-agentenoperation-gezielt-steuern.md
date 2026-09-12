# 07: Eine aktive Agentenoperation gezielt steuern

**What to build:** Der aktuelle Lease-Inhaber kann einen konkreten laufenden Activity Attempt beobachten und mit `interrupt`, `queue` oder Cancel beeinflussen, ohne Commands zu verlieren, doppelt zuzustellen oder einen falschen Parallelversuch zu treffen.

**Blocked by:** 06: Eine Human Request beantworten und die Session in Codex fortsetzen

**Status:** resolved

- [x] Bei mehreren aktiven Attempts verlangt der Operator eine explizite Zielauswahl; ein mehrdeutiges Kommando wird abgelehnt.
- [x] `queue` bewahrt mehrere Commands in sichtbarer Annahmereihenfolge und stellt sie nach Abschluss der aktiven Operation zu.
- [x] `interrupt` stoppt und fenced die adressierte Operation kontrolliert, reconciled vorhandene Wirkungen und stellt genau einen angenommenen Command als Nächstes zu.
- [x] Cancel beendet ausschließlich den gewählten Scope mit dokumentiertem Grund und ohne automatischen Retry.
- [x] Ein menschlich ausgelöster Interrupt oder Cancel verbraucht keine fachliche Repair-Runde.
- [x] API-/Workerabbruch zwischen Annahme, Zustellung, Prozessstopp und Antwort verliert, verdoppelt oder vertauscht keinen Command.
- [x] Verspätete Ausgabe eines gefenceten Prozesses kann History ergänzen, aber weder Head noch kanonischen Zustand verändern.
- [x] Der Operator zeigt Zustellmodus, Queue-Position, Prozessstatus, Fence-Epoche und anschließende Agentenantwort in derselben Run History.

## Session lesson

Die neue Steuerung darf weder an den ursprünglichen Workerprozess noch an eine separate Codex-Task gebunden sein. Sie adressiert immer den fachlichen Attempt.


## Implementation and acceptance — 2026-09-12

Implemented through OpenSpec change
[`control-active-agent-operations`](../../../../openspec/changes/archive/2026-09-12-control-active-agent-operations/proposal.md).
The [acceptance overview](../../../../openspec/changes/archive/2026-09-12-control-active-agent-operations/implementation-evidence.md)
links each criterion to observed HTTP/CLI results and sanitized Run History.

The local proof covers parallel attempts, FIFO commands, interrupt/cancel,
actual process termination, API/worker SIGKILL, concurrent replacement,
stop-before-start, fenced late output, redaction and repository isolation.
Processing uses explicit replacement-worker passes and persisted attempt/session
identities, never a separate Codex task or the original worker's identity.

Scope of acceptance: the controlled live adapter has no repository write
capability. Successful reconciliation proves process stop and an empty
repository-effect set; nonempty/conflicting effects block delivery visibly.
Real Codex and live Git/GitHub effects remain the subsequent integration tickets.
Accepted by the user on 2026-09-12. The OpenSpec change is archived and its six requirements are synchronized to the [canonical specification](../../../../openspec/specs/active-agent-operation-control/spec.md).
