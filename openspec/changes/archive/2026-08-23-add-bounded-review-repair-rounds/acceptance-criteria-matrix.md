# Acceptance Criteria Matrix

| Issue-05-Kriterium | Direkter Seam | Erwartete Beobachtung | Geplante Verifikation |
|---|---|---|---|
| Strukturierte Aggregation aller fehlgeschlagenen Achsen nur an den Implementer | Kontrollierter Repair-Worker-Port plus Workflow-GET | Eine versionierte Assignment enthält jede Fail-Achse mit Ort/Beschreibung; derselbe Worker und Worktree schreiben, Reviewer bleiben read-only | Contract-Test und erfolgreicher signed-HTTP Repair-Fall |
| Vollständige Neuverifikation jedes Repair-Heads | Git-/Verifier-/Reviewer-Grenzen plus Workflow-GET | Neuer Commit/Head, deterministischer Check und drei frische Reviews sind exakt an denselben SHA gebunden | Signed-HTTP Repair-Erfolg und Deterministic-Fail-Fall |
| Höchstens drei automatische Runden | Kontrollierter Worker und persistierter Repair-Read-Back | Genau drei nummerierte Versuche und keine vierte Invocation nach weiterem Fail | Signed-HTTP Systemtest mit dauerhaft failenden Reviewern |
| Begrenzte Sol-Eskalation | Paketierter Policy-Contract und Worker-Invocation | Terra regulär; Sol nur material/structured/finale Runde, stets `xhigh` und im Implementer-Write-Root | Parametrisierte Policy- und Worker-Contract-Tests |
| `needs-info` nach fehlenden/widersprüchlichen Anforderungen | Workflow-GET, bestehender Draft-PR und GitHub-Labelprojektion | Drei Versuche/Findings bleiben; ausschließlich `needs-info` wird terminal projiziert | Signed-HTTP Restart-Systemtest |
| `ready-for-human` für nicht agentisch lösbare Konflikte | Workflow-GET, bestehender Draft-PR und GitHub-Labelprojektion | Drei Versuche/Findings bleiben; ausschließlich `ready-for-human` wird terminal projiziert | Signed-HTTP Restart-Systemtest |
| Reversible Details autonom, semantische UI-Fragen Produktentscheidung | Repair-Assignment/Result-Schema und Codex-Prompt | Entscheidungsgrenzen sind explizit; semantischer Block erzeugt strukturierte Unterbrechung | Repair-Contract-/Adapter-Test |
| Persistierter Lauf, PR und GitHub-Projektion | Signiertes POST, öffentliches GET, reales SQLite/LangGraph, kontrollierte Grenzen | Repair-Historie und Terminal-/Verified-Zustand überleben App-Rekonstruktion ohne doppelte Effekte | Erfolgs- und beide Handoff-Systemtests |
