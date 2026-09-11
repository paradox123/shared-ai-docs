# Ticket 05 – kompakter Funktionsnachweis

Geprüfter Stand: `c4147a4` auf `main`. **59/59 Tests grün**, Build ohne Warnungen/Fehler. Standards- und Spec-Review: **0 offene Findings**.

| Effekt | Echter Worker-Abbruch | Externer Effektzähler nach Recovery | Ergebnis |
|---|---|---:|---|
| Git | `SIGKILL` / `-9` | **1** | `adopted` · [Receipt](test_git_success_gap_adopts_the_existing_ref_once.json) |
| Provider | `SIGKILL` / `-9` | **1** | `adopted` · [Receipt](test_provider_success_gap_adopts_one_independent_receipt.json) |
| Session | `SIGKILL` / `-9` | **1** | `adopted` · [Receipt](test_session_success_gap_and_concurrent_replacement_keep_one_session.json) |

**Stale Base:** Provider `55bf92abacb3`, lokal `7c13abd988c3` → `local-base-stale`, keine Effekte/Session. Nach Synchronisierung stimmen erwartete, lokale und Provider-SHA exakt überein; erst dann startet die Session. [SHA-Verlauf](test_stale_local_base_blocks_before_any_agent_start.json)

**Operator:** Reconcile → API-Neustart → Adopt → Retry geprüft; Retire beendet aktive Versuche, löst die Lease und gibt das Repository frei. Konflikte und veraltete Commands werden abgewiesen. [Operator-Verlauf](test_operator_reconcile_adopt_retry_survive_api_restart.json) · [Retire-Verlauf](test_retire_settles_existing_effects_releases_owner_and_fences_late_worker.json)

[Gesamtes Testprotokoll](test-output.txt) · [Maschinenlesbare Zusammenfassung](summary.json) · [Review](../../../../openspec/changes/archive/2026-09-11-reconcile-repository-effects/review.md)

Grenze: echtes Git/PostgreSQL und getrennte Prozesse; kontrollierter Provider und Fake-Codex. Keine Behauptung über Live-GitHub-Schreibzugriffe oder automatischen DTS-Dispatch.
