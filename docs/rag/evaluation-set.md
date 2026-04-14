# DanielsVault Local RAG Evaluation Set v0

## Zweck

Dieses Dokument definiert ein erstes Evaluation-Set fuer das lokale DanielsVault-RAG.

Die Fragen basieren nicht nur auf expliziten Nutzerfragen aus vergangenen Sessions, sondern auch auf:

- agentischen Wissensfragen, die waehrend der Bearbeitung tatsaechlich gestellt wurden
- Rueckfragen, die fuer eine schnellere oder robustere Loesung hilfreich gewesen waeren
- zukunftsorientierten Folgefragen fuer kommende RAG-Slices

Damit testet das Set nicht nur "Kann das System eine Nutzerfrage beantworten?", sondern auch:

1. findet das RAG die richtige fachliche Startbasis?
2. unterstuetzt es Agenten bei Kontextaufbau und Scope-Klaerung?
3. hilft es dabei, unnoetige Cross-Domain-Suche zu vermeiden?

## Quellenbasis

Ausgewertete Verlaufsquellen in dieser Iteration:

- Codex Prompt-Historie in `/Users/dh/.codex/.codex-global-state.json`
- ausgewaehlte Codex-Session-Artefakte unter `/Users/dh/.codex/sessions/`
- ausgewaehlte Claude-Session-Logs unter `/Users/dh/.claude/projects/`
- Copilot-CLI-Metadaten unter `/Users/dh/Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli/copilotcli.session.metadata.json`
- ausgewaehlte Copilot-Chat-Sessions unter `/Users/dh/Library/Application Support/Code/User/workspaceStorage/`

Beobachtete agentische Evidenz, die fuer dieses Eval-Set wichtig war:

- Claude hat bei Spec-Delivery-Aufgaben aktiv `spec-change-delivery.md`, `doc-workflow.md`, `spec-closeout`, `check-build-watcher` und `spec-change-delivery`-Skill-Dateien gelesen oder gesucht.
- Copilot hat bei Nebenkosten- und Planungsaufgaben wiederholt Specs gelesen, DoR/DoD gesucht, Repo-Grenzen geprueft und vorhandene Code-/Testartefakte gegen Specs gespiegelt.
- Copilot- und Codex-Sessions zeigen mehrere Faelle, in denen die eigentlich nuetzliche Frage nicht nur "wie loese ich das", sondern "welche Datei ist hier die normative Quelle" oder "welche Domain ist ueberhaupt in scope" war.

Hinweise:

- sensible historische Prompts wurden paraphrasiert
- das Set fokussiert nur Fragen, die sich an reale DanielsVault-Dateien oder stabile Projektartefakte anbinden lassen
- Ziel ist Retrieval-Evaluation, nicht vollstaendige Rekonstruktion jeder Unterhaltung

## Frageklassen

Jeder Eintrag hat:

- eine `id`
- einen `bucket`
- eine Herkunft wie `codex`, `claude`, `copilot` oder `synthetic-follow-up`
- eine konkrete Frage
- erwartete Primaerquellen
- ein minimales Acceptance Target fuer Retrieval

Verwendete Buckets:

- `historical-user`: echte, explizit gestellte Nutzerfragen
- `historical-agent`: Fragen, die der Agent waehrend der Bearbeitung faktisch an die Wissensbasis gestellt hat
- `counterfactual-helpful`: Rueckfragen, die fuer Scope, Verifikation oder Quellenklarheit hilfreich gewesen waeren
- `future`: sinnvolle Folgefragen fuer kommende RAG-Slices

Eine maschinenlesbare Erstfassung liegt parallel in:

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl`

## Historical User Questions

### U01

- Bucket: `historical-user`
- Herkunft: `codex`
- Frage: Was ist RAG, und macht es Sinn, so etwas fuer DanielsVault lokal aufzubauen?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/AGENTS.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md`
- Acceptance Target:
  - mindestens 2 Treffer aus Root + shared-ai-docs
  - Antwort erwaehnt lokale Wissensschicht und Domain-Grenzen

### U02

- Bucket: `historical-user`
- Herkunft: `codex`
- Frage: Wie soll das DanielsVault-Local-RAG fachlich und technisch abgegrenzt werden?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`
- Acceptance Target:
  - beide RAG-Artefakte sollten getroffen werden
  - Antwort nennt In-Scope, Out-of-Scope und erste bounded slices

### U03

- Bucket: `historical-user`
- Herkunft: `codex`
- Frage: Wie synchronisiere ich eigene Agent-Skills zwischen privatem Mac und Windows-Arbeitslaptop?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/index.md`
- Acceptance Target:
  - Hybrid-Skill-Sync-Doku muss Top-Treffer sein
  - Antwort nennt Git-Repo als Source-of-Truth und Runtime-Symlinks/Junctions

### U04

- Bucket: `historical-user`
- Herkunft: `codex`
- Frage: Wie passt `vercel-labs/skills` in das lokale Hybrid-Skill-Modell mit `~/.agents/skills`?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md`
- Acceptance Target:
  - Antwort trennt klar Source-of-Truth, Runtime-Pfad und Vendor-/Import-Rolle

### U05

- Bucket: `historical-user`
- Herkunft: `codex`
- Frage: Wie sind Codex CLI, Claude Code und GitHub Copilot an das lokale LiteLLM-Gateway angebunden?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/agent-and-extension-configuration.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/litellm-api-gateway.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/api-gateway/index.md`
- Acceptance Target:
  - Agent-/Extension-Konfiguration unter den Top-Treffern
  - Antwort unterscheidet direkte Clients von indirekten oder experimentellen Integrationen

### U06

- Bucket: `historical-user`
- Herkunft: `copilot`
- Frage: Welche Unterlagen und offenen Schritte sind fuer die MKK-/ELR-Foerderung der energetischen Sanierung relevant?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/private/Energetische Sanierung/Förderung/README.md`
  - `/Users/dh/Documents/DanielsVault/private/Energetische Sanierung/00-Dashboard.md`
  - `/Users/dh/Documents/DanielsVault/private/Energetische Sanierung/Finanzierung/README.md`
- Acceptance Target:
  - mindestens 2 Treffer aus `private/Energetische Sanierung/`
  - Antwort nennt Eigentumsbestaetigung, Finanzierungsnachweis, Bilder/Erlaeuterung und Status/offene Punkte

### U07

- Bucket: `historical-user`
- Herkunft: `copilot`
- Frage: Welche Belege und Messwerte muessen fuer die Nebenkostenabrechnung 2025 extrahiert und validiert werden?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025MesswerteReviewedArtifactsTests.cs`
- Acceptance Target:
  - Messwerte-Spec muss getroffen werden
  - Antwort nennt ista, Belege, Zaehlerpruefung und Tibber-Kontext

### U08

- Bucket: `historical-user`
- Herkunft: `copilot`
- Frage: Welche Spec beschreibt Zahlungshinweis und Vorauszahlungsempfehlung fuer die PDF-Einzelabrechnung?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-10 Nebenkostenabrechnung PDF Zahlungshinweis und Vorauszahlungsempfehlung.md`
- Acceptance Target:
  - exakte Spec-Datei unter den Top-Treffern
  - Antwort benennt Zahlungshinweis und Empfehlung zur kuenftigen Vorauszahlung als Fokus

### U09

- Bucket: `historical-user`
- Herkunft: `codex`
- Frage: Wo liegt die korrigierte 2025er-Abrechnung fuer NE3/Koenig, und welche Vorauszahlungswerte wurden dort gesetzt?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output/final-pdf-ne3-vorauszahlung-korrektur-2026-04-12_2008/mp-ne3/einzelabrechnung.json`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output/final-pdf-ne3-vorauszahlung-korrektur-2026-04-12_2008/mp-ne3/einzelabrechnung.html`
- Acceptance Target:
  - NE3-Artefaktpfad wird gefunden
  - Antwort nennt 150 EUR monatlich und 1800 EUR gesamt als gesetzte Vorauszahlungen

### U10

- Bucket: `historical-user`
- Herkunft: `claude`
- Frage: Welche NCG-Dokumente beschreiben Service-Abhaengigkeiten und die Migration zu Hetzner-Dev?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/Service-Dependency-Graph.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/Completed/2026-02-22 Migration to Hetzner-Dev.md`
- Acceptance Target:
  - beide NCG-Dokumente sollten unter den Treffern liegen
  - Antwort trennt Architektur-/Abhaengigkeitswissen von der Migrations-Spec

## Historical Agent Questions

### A01

- Bucket: `historical-agent`
- Herkunft: `claude`
- Frage: Welche Workflow- und Skill-Dokumente sind fuer Spec-Delivery normativ, bevor ein Prompt oder eine Umsetzung angepasst wird?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_prompts/spec-change-delivery.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-change-delivery/SKILL.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/check-build-watcher/SKILL.md`
- Acceptance Target:
  - mindestens 2 normative Workflow-Dokumente unter den Top-Treffern
  - Antwort trennt Prompt-Text, Workflow-Gates und Skill-Verhalten

### A02

- Bucket: `historical-agent`
- Herkunft: `copilot`, `claude`
- Frage: Welche Shared Gates fuer DoR, DoD und Decision Freeze gelten fuer diese Spec oder diesen Change?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_prompts/spec-change-delivery.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-change-delivery/SKILL.md`
- Acceptance Target:
  - `doc-workflow.md` muss unter den Top-Treffern sein
  - Antwort nennt DoR/DoD als gemeinsame Gates und nicht nur freie To-do-Listen

### A03

- Bucket: `historical-agent`
- Herkunft: `claude`
- Frage: Welche offenen `[MISSING]`, `[DECISION]` oder `[BLOCKED]` Marker stehen aktuell in der betroffenen Spec?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`
- Acceptance Target:
  - die konkrete Spec-Datei ist Top-Treffer
  - Antwort nennt Marker mit ihrem Thema, nicht nur eine Ja/Nein-Aussage

### A04

- Bucket: `historical-agent`
- Herkunft: `claude`
- Frage: Welche Skill- oder Prompt-Dateien referenzieren `OpenSpec` oder `spec-change-delivery`, bevor ich daran etwas aendere?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_prompts/spec-change-delivery.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-change-delivery/SKILL.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-closeout/SKILL.md`
- Acceptance Target:
  - Antwort findet die relevanten Skill-/Prompt-Dateien
  - Antwort unterscheidet Implementierung, Delivery und Closeout

### A05

- Bucket: `historical-agent`
- Herkunft: `copilot`
- Frage: Welche Tests und reviewed artifacts decken Nebenkosten-2025-Importe bereits ab, bevor ich neue Anforderungen formuliere oder Code aendere?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025MesswerteReviewedArtifactsTests.cs`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025TibberReviewedArtifactsTests.cs`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025RestkostenReviewedArtifactsTests.cs`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
- Acceptance Target:
  - mindestens ein Testartefakt und eine Spec werden gemeinsam getroffen
  - Antwort benennt vorhandene Testabdeckung statt blind neue Aufgaben abzuleiten

### A06

- Bucket: `historical-agent`
- Herkunft: `copilot`
- Frage: Welcher Git-Root und welches Repo sind fuer diese Aenderung in scope, und welche angrenzenden Repos sollen nicht mitveraendert werden?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/AGENTS.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_plans/2026-03-25 Nebenkostenabrechnung Applikation Implementierungsplan.md`
- Acceptance Target:
  - `VAULT_AGENT_STRUCTURE.md` muss getroffen werden
  - Antwort benennt Git-Roots und aendert nicht implizit die Domain-Grenzen

### A07

- Bucket: `historical-agent`
- Herkunft: `copilot`
- Frage: Welche Service-Abhaengigkeiten und SettingKeys sind fuer die Docker-BaseUrl-Fix-Spec bereits dokumentiert?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/Completed/2026-03-02 Docker BaseUrl Fix - Test-Driven Iterative.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/Service-Dependency-Graph.md`
- Acceptance Target:
  - die Docker-BaseUrl-Fix-Spec wird gefunden
  - Antwort nennt Dependency-Matrix oder SettingKey-Kontext

## Counterfactual Helpful Questions

### C01

- Bucket: `counterfactual-helpful`
- Herkunft: `synthetic-from-sessions`
- Frage: Welche Datei ist fuer dieses Thema die normative Spec, und welche Dateien sind nur `Failed`, `Completed` oder historische Ableitungen?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Failed/2026-03-14 Nebenkostenabrechnung Pipeline.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/Completed/2026-04-09 Nebenkostenabrechnung 2025 Messwerte Review-Slice.md`
- Acceptance Target:
  - Antwort unterscheidet normative Quelle von historischem Material
  - `Failed` und `Completed` werden nicht stillschweigend als aktuelle Norm behandelt

### C02

- Bucket: `counterfactual-helpful`
- Herkunft: `synthetic-from-sessions`
- Frage: Welche Verifikationskommandos oder Testnachweise muessen am Ende gruen sein, bevor der Change als fertig gilt?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_prompts/spec-change-delivery.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`
- Acceptance Target:
  - Antwort nennt explizite Verification Commands oder Nachweisformen
  - Ergebnis ist pruefbar und nicht nur narrativ

### C03

- Bucket: `counterfactual-helpful`
- Herkunft: `synthetic-from-sessions`
- Frage: Welche bestehenden Output-Artefakte oder Testdaten belegen den Zielzustand bereits, bevor ich neu implementiere oder neu rechne?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output/final-pdf-ne3-vorauszahlung-korrektur-2026-04-12_2008/mp-ne3/einzelabrechnung.json`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025MesswerteReviewedArtifactsTests.cs`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025TibberReviewedArtifactsTests.cs`
- Acceptance Target:
  - Antwort findet konkrete Artefakte mit Pfadbezug
  - Antwort benutzt vorhandene Evidenz statt rein hypothetischer Beschreibung

### C04

- Bucket: `counterfactual-helpful`
- Herkunft: `synthetic-from-sessions`
- Frage: Welche Domain soll zuerst durchsucht werden, und welche Domains sollten fuer diese Aufgabe explizit ausgeschlossen bleiben?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/AGENTS.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md`
- Acceptance Target:
  - Antwort nennt eine priorisierte Start-Domain
  - Antwort vermeidet ungerichtete Vollsuche ueber alle Git-Roots

## Future Questions

### F01

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Welche Dateien und Dateitypen sollte Slice A des DanielsVault-RAG initial indexieren, und welche sollten explizit ignoriert werden?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`

### F02

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Welche Git-Roots und Domains muessen im Retriever als Filter oder Facetten auftauchen?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/AGENTS.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`

### F03

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Wie sollte das minimale Chunk-Metadaten-Schema fuer DanielsVault aussehen?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`

### F04

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Welche Eval-Fragen pruefen am besten, ob `_shared`, `private` und `ncg` im Retrieval sauber getrennt bleiben?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.md`

### F05

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Welche Dokumente sollte ein Agent bei Skill-Sync-Fragen zuerst laden, bevor er breite Repo-Suchen startet?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/index.md`

### F06

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Welche Dokumente und Tests sollte ein Agent fuer Nebenkosten-2025-Messwerte und Importe priorisieren?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025MesswerteReviewedArtifactsTests.cs`
  - `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Import.Tests/Year2025TibberReviewedArtifactsTests.cs`

### F07

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Welche minimalen Retrieval-Metriken und Ergebnisformen sollte das DanielsVault-RAG in Phase 1 reporten?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`

### F08

- Bucket: `future`
- Herkunft: `synthetic-follow-up`
- Frage: Wie sollte ein spaeteres RAG mit privaten und geteilten Inhalten umgehen, ohne Domain-Grenzen zu verwischen?
- Erwartete Primaerquellen:
  - `/Users/dh/Documents/DanielsVault/VAULT_AGENT_STRUCTURE.md`
  - `/Users/dh/Documents/DanielsVault/AGENTS.md`
  - `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13 DanielsVault Local RAG Wissensplattform.md`

## Einsatzempfehlung

Empfohlene erste Auswertung:

1. `historical-user` als klassisches Gold-Set fuer Nutzerfragen verwenden
2. `historical-agent` als Gold-Set fuer agentischen Kontextaufbau verwenden
3. `counterfactual-helpful` nutzen, um bessere Routing- und Scope-Checks zu evaluieren
4. `future` erst aktivieren, sobald Slice A und Slice C weiter konkretisiert sind

Pro Frage sollte mindestens gespeichert werden:

- Top-5 Retrieval-Kandidaten
- traf die richtige Domain?
- traf die richtige Datei?
- war die Quelle hinreichend praezise?
- wurde unnoetige Cross-Domain-Mischung vermieden?

## Verifikationskommandos

```bash
test -f /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.md
test -f /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
path = Path("/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.v0.jsonl")
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
assert rows, "no rows"
counts = Counter(r["bucket"] for r in rows)
for bucket in ["historical-user", "historical-agent", "counterfactual-helpful", "future"]:
    assert counts[bucket] > 0, f"missing bucket: {bucket}"
for row in rows:
    for expected in row.get("expected_paths", []):
        assert Path(expected).exists(), f"missing path for {row['id']}: {expected}"
print(f"rows={len(rows)} counts={dict(counts)}")
PY
rg -n '^### U|^### A|^### C|^### F' /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.md
```

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-14 | 0 | User | Wunsch nach Evaluation-Set aus echten DanielsVault-Fragen und sinnvollen Folgefragen |
| 2026-04-14 | 1 | Codex | Erste historische Auswertung aus Codex-, Claude- und Copilot-Sessions plus v0-Eval-Set erstellt |
| 2026-04-14 | 2 | Codex | Eval-Set um agentische Wissensfragen und hilfreiche Gegenfragen erweitert |

Session: `codex-desktop-2026-04-14`
