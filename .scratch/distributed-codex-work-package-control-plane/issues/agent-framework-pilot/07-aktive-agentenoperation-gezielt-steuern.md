# 07: Eine aktive Agentenoperation gezielt steuern

**What to build:** Der aktuelle Lease-Inhaber kann einen konkreten laufenden Activity Attempt beobachten und mit `interrupt`, `queue` oder Cancel beeinflussen, ohne Commands zu verlieren, doppelt zuzustellen oder einen falschen Parallelversuch zu treffen.

**Blocked by:** 06: Eine Human Request beantworten und die Session in Codex fortsetzen

**Status:** ready-for-agent

- [ ] Bei mehreren aktiven Attempts verlangt der Operator eine explizite Zielauswahl; ein mehrdeutiges Kommando wird abgelehnt.
- [ ] `queue` bewahrt mehrere Commands in sichtbarer Annahmereihenfolge und stellt sie nach Abschluss der aktiven Operation zu.
- [ ] `interrupt` stoppt und fenced die adressierte Operation kontrolliert, reconciled vorhandene Wirkungen und stellt genau einen angenommenen Command als Nächstes zu.
- [ ] Cancel beendet ausschließlich den gewählten Scope mit dokumentiertem Grund und ohne automatischen Retry.
- [ ] Ein menschlich ausgelöster Interrupt oder Cancel verbraucht keine fachliche Repair-Runde.
- [ ] API-/Workerabbruch zwischen Annahme, Zustellung, Prozessstopp und Antwort verliert, verdoppelt oder vertauscht keinen Command.
- [ ] Verspätete Ausgabe eines gefenceten Prozesses kann History ergänzen, aber weder Head noch kanonischen Zustand verändern.
- [ ] Der Operator zeigt Zustellmodus, Queue-Position, Prozessstatus, Fence-Epoche und anschließende Agentenantwort in derselben Run History.

## Session lesson

Die neue Steuerung darf weder an den ursprünglichen Workerprozess noch an eine separate Codex-Task gebunden sein. Sie adressiert immer den fachlichen Attempt.
