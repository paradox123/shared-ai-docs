# Free Entry v2 Slice Plan

Datum: 2026-05-04

Status: Plan

Quelle:

- Fuehrend: `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
- Nutzerpfad: `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/APPLICATION-FLOW.md`
- Entscheidungen: `v2/docs/adr/001-repo-access-and-ip-protection.md`, `v2/docs/adr/002-starter-wizard-runner-technology-stack.md`, `v2/docs/adr/003-survey-delivery-and-answer-handoff.md`

## Zweck

Dieser Plan zerlegt die v2-Master-Spec in umsetzbare Slices, ohne den Gesamtscope zu verlieren. Er ist kein Ersatz fuer die Master-Spec. Er ist die Kontrollschicht zwischen Master-Spec und einzelnen `spec-change-delivery`-Umsetzungen.

Ein Slice darf nur umgesetzt oder geschlossen werden, wenn seine Traceability zur Master-Spec sichtbar ist und die Coverage-Matrix aktualisiert wurde.

## Scope-Schutzregeln

1. Keine Anforderung verschwindet beim Schneiden in Slices. Alles aus der Master-Spec bleibt in der Coverage-Matrix sichtbar.
2. Ein Slice darf Scope bewusst verschieben, aber nicht still streichen. Verschobener Scope bleibt als `[PENDING]` oder `[BLOCKED]` sichtbar.
3. Jeder Slice braucht einen klaren Done-Nachweis: Artefakt, Test, Review oder lauffaehiger Spike.
4. Der vertikale Spike darf Funktionen stubben, muss aber die echten Schnittstellen, Artefaktnamen und Kontrollflussgrenzen beweisen.
5. Alte Specs duerfen nach Freeze nur noch Detailquellen sein. Bei Widerspruch gewinnt die v2-Master-Spec.
6. ADR-Entscheidungen duerfen nicht in Slices neu verhandelt werden. Neue Zweifel werden als neue ADR oder ADR-Revision sichtbar gemacht.
7. Harness-Faelle muessen jeden fuer den jeweiligen Slice beanspruchten Kontrollfluss-Pfad mindestens einmal abdecken, bevor dieser Slice als implementierungsnah gilt.

## Slice-Zuschnitt

| Slice | Ziel | Abhaengigkeiten | Done-Signal |
|---|---|---|---|
| S0 Spec Freeze Pack | Alte Specs als Detailquellen sichern und Widerspruch zur Master-Spec entschärfen. | Master-Spec, Application Flow, ADR-001/002/003 | Erledigt in `v2/docs/S0-REPO-FREEZE-LEGACY-QUARANTINE.md` und `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s0-repo-freeze-legacy-quarantine-spec.md`. |
| S1 Vertikaler Architektur-Spike | Minimaler Durchstich durch .NET-Starter, Survey-Server, lokale Antwortuebernahme, Dummy-Bundle, Provider-Stub und Harness. | S0 empfohlen; ADR-001/002/003 entschieden | Accepted: lokaler und Docker-Harness-Lauf erzeugen `survey/answers.json`, `survey/import-manifest.json`, Bundle-Readiness-Status und Run-Manifest in isolierter Umgebung. |
| S2 Survey Delivery und Answer Handoff | Server-gerenderter Survey, lokaler Fallback, Antwortartefakt, Handoff-Token, Retention. | ADR-003, Spike-Erkenntnisse | Accepted: API-/Artefaktvertrag ist implementiert; lokale und Docker-Harness beweisen 12/12 S2-Cases. |
| S3 Content Bundle und Managed-AI-Kanal | Free-Entry-Bundle, Bundle-Manifest, Signatur/Hash, Updatekanal, optionaler Git/GitHub-Spaeterpfad. | ADR-001, Spike-Erkenntnisse | Bundle kann installiert/geprueft werden; ungueltiges Bundle blockiert sauber; Updatekanal ist spezifiziert oder stubbar. |
| S4 Provider Activation Guides | Provider-Matrix, kundengerechte Schritt-fuer-Schritt-Guides, Visualisierungskonzept, Readiness-Test. | Survey-Antworten, Provider-Guardrails | Mindestens ein Free/Trial- und ein API-Pfad sind als Guide-Artefakt mit Readiness-Vertrag beschrieben. |
| S5 Survey v2 Inhalte | Drei Survey-Varianten, Pflichtkern, bedingter Regulatorikblock, agentische Zusatzfragen im Survey-Stil. | S2, Application Flow | Survey-Katalog ist server-renderbar und lokal fallbackfaehig; KRITIS erscheint nur im relevanten Pfad. |
| S6 ROI/RAG Runtime | Dokumentenlage, RAG-Status, Quellenstatus, ROI-Agent, Report. | S2, S3, S4, S5 | ROI-Report entsteht nur mit `provider_ready=true`; RAG bleibt ohne LLM/Freigabe blockiert. |
| S7 Docker/Safe Harness Ausbau | Szenariobasierte Harness fuer alle Kontrollfluss-Pfade, Artefakte, Exit-Codes und Secret-Leaks. | S1 als Start; erweitert mit S2-S6 | Jeder fuehrende Pfad hat mindestens einen Case mit erwarteten Artefakten und Negativfall. |

## Coverage-Matrix

| Master-Spec-Bereich | Slice-Abdeckung | Status | Nicht-verlieren-Hinweis |
|---|---|---|---|
| Fuehrende Reihenfolge | S0, S1, S7 | [PARTIAL S1] | S1-Harness beweist Survey vor Bundle/Workbench/Agent-Config; volle Kontrollflussmatrix bleibt S7. |
| Non-Goals und Sicherheitsgrenzen | S0, S1, S3, S4, S7 | [PARTIAL S1] | S1-Harness prueft keine Secrets in Logs/Manifesten/Summaries und keine echten Provider/LLM. |
| V2-FR-001 Einsteigerverstaendlicher Start | S1, S4, S5 | [PARTIAL S1] | S1 liefert technischen Starter-/Runner-Durchstich; finale Texte/UX bleiben S4/S5. |
| V2-FR-002 Profil- und Betriebstyp-Routing | S1, S5, S7 | [PARTIAL S1] | S1 uebernimmt Profil/Betriebstyp aus Cases; echtes Routing bleibt S5/S7. |
| V2-FR-003 Entry, Download und Registrierung | S1, S3 | [PARTIAL S1] | S1 nutzt Stub-Registrierung und Dummy-Bundle; produktiver Download/Bundlescope bleibt S3. |
| V2-NFR-UX-001 Bedienbarkeit und Messbarkeit | S1, S4, S7 | [PARTIAL S1] | S1 misst Case-Erfolg/Exit-Codes maschinenlesbar; UX-Metriken bleiben spaeter. |
| V2-FR-010 Survey-Definition | S2, S5 | [PARTIAL S2] | S2 liefert technische Fixture-Definitionen und Hash-Vertrag; finaler fachlicher Fragenkatalog bleibt S5. |
| V2-FR-010a Survey-Delivery-Service und Antwortdaten-Uebergabe | S1, S2, S7 | [DONE S2] | S2 implementiert Session-Start, Definition-Load, Answer-Submit, Complete, Handoff, Import-Confirmation, Retention und lokale Fallback-Artefakte. |
| V2-FR-011 Survey-Inhalte | S5 | [PENDING] | Prozessdoku ja/nein, Taetigkeiten, ROI-Kandidaten nicht verlieren. |
| V2-FR-012 Agent-Zusatzfragen | S5, S6 | [PENDING] | Agent fragt nicht frei, sondern im Survey-Stil und begrenzt. |
| V2-FR-020 Aktivierungsstatus | S1, S4, S7 | [PARTIAL S1] | S1 manifestiert `activation_status` fuer Provider-Stub-Pfade; echte Guides bleiben S4. |
| V2-FR-021 Readiness | S1, S4, S7 | [PARTIAL S1] | S1 manifestiert `provider_ready` als Stub; echter LLM-Test bleibt S4. |
| V2-FR-022 Provider-Guardrails | S4, S7 | [PENDING] | Keine Zahlungsdaten im Script, keine Accountanlage im Namen des Nutzers. |
| V2-FR-023 Provider-/Modell-Empfehlungsmatrix | S4 | [PENDING] | Empfehlung erst nach Survey-Ende konkretisieren. |
| V2-FR-024 Provider-Aktivierungsguides | S4 | [PENDING] | Einsteiger brauchen Menuefuehrung, nicht nur Developer-Links. |
| V2-FR-024a Visualisierung der Aktivierungsguides | S4 | [PENDING] | Screenshots/rote Markierungen/Schrittbilder als Content-Artefakte pruefen. |
| V2-FR-030 Vault und Arbeitsraum | S1, S3, S7 | [PARTIAL S1] | S1 erzeugt Workbench-/Vault-Stub; echter Vault-/Shared-Content bleibt S3/S7. |
| V2-FR-031 Content-Bundle und optionale Repo-Quellen | S1, S3, S7 | [PARTIAL S1] | S1 prueft Dummy-Bundle; produktives Bundle-/Update-Modell bleibt S3. |
| V2-FR-031a Bundle-Manifest und Readiness | S1, S3, S7 | [PARTIAL S1] | S1 prueft Hash, Signatur-Stub und erwartete Dateien; echte Signatur bleibt S3. |
| V2-FR-031b Managed-AI-Kanal und Git/GitHub-Spaeterpfad | S3, S7 | [PENDING] | Wiederkehrender Umsatzpfad bleibt Teil des Zielbilds. |
| V2-FR-032 Obsidian-Plugin-Baseline | S3, S7 | [PENDING] | Pflicht/empfohlen/optional und Plugin-Trust nicht verlieren. |
| V2-FR-040 Dokumentationslage | S5, S6, S7 | [PENDING] | Doku-Pfade aus Survey erst nach Survey-Ende verarbeiten. |
| V2-FR-041 RAG-Status | S6, S7 | [PENDING] | RAG nur mit LLM und Freigabe. |
| V2-FR-050 ROI-Agent | S6, S7 | [PENDING] | ROI zwingend LLM-gestuetzt, nicht hart codiert. |
| V2-FR-051 ROI-Modell | S6, S7 | [PENDING] | Annahmen, Bandbreiten und Quellenstatus sichtbar. |
| V2-FR-052 Report | S6, S7 | [PENDING] | Chancen, Risiken, ROI, Annahmen, naechster Schritt. |
| V2-FR-053 Report-Hinweise | S4, S6 | [PENDING] | Drei Sprachprofile. |
| V2-DEC-TECH-001 .NET Starter/Wizard/Runner | S1 | [DONE S1] | .NET-10-Solution mit `FreeEntry.App`, `FreeEntry.Core`, `FreeEntry.SurveyStub` und Tests liegt unter `v2/`. |
| V2-FR-060 Artefaktstruktur | S1, S2, S3, S6, S7 | [PARTIAL S2] | S2 stabilisiert `survey/answers.json` und `survey/import-manifest.json`; Bundle-/ROI-/RAG-Artefakte bleiben S3/S6/S7. |
| V2-FR-061 Run-Manifest | S1, S2, S7 | [PARTIAL S2] | S2 synchronisiert `survey_import_status` zwischen Import-Manifest und Run-Manifest; volle S7-Feld-/Pfadmatrix bleibt spaeter. |
| V2-FR-062 Agent-Konfiguration | S1, S3, S6, S7 | [PARTIAL S1] | S1 erzeugt `agent/agent-config.json` mit `agent_mode=preflight_only`. |
| V2-FR-063 Exit-Codes | S1, S7 | [PARTIAL S1] | S1 prueft Exit `0`, `20`, `30`; volle Exit-Code-Matrix bleibt S7. |
| V2-NFR-001 Sicherheit | S1, S2, S3, S4, S7 | [PARTIAL S2] | S2 prueft Handoff-Token-/Secret-Redaction fuer lokale und Docker-Harness-Summaries und Artefakte. |
| Docker- und Test-Harness | S1, S2, S7 | [PARTIAL S2] | S2-Docker-Harness baut Image und fuehrt alle 12 S2-Cases mit Survey-Service-, Artefakt- und Secret-Assertions aus; Vollmatrix bleibt S7. |
| Traceability und alte Specs | S0 | [DONE] | Alte Details sind als historische Quellen gesichert; alte Reihenfolgen sind mit Superseded-/Migrationshinweisen neutralisiert. |

## Iteration 1

### Scope Pressure Check

Der Gesamtscope ist zu gross fuer eine direkte Implementierung. Das Risiko liegt nicht nur in der Menge, sondern darin, dass Survey, Provider, Bundle, Vault, RAG/ROI und Harness fachlich voneinander abhaengen. Deshalb wird nicht in isolierte Feature-Bloecke zerlegt, sondern zuerst ein vertikaler Spike geplant, der die Schnittstellen beweist.

### Aktionen

- [DONE] ADR-001, ADR-002 und ADR-003 sind entschieden und bilden feste Architekturgrenzen.
- [DONE] Die v2-Master-Spec ist fachlich fuehrend und enthaelt die konsolidierten Scope-Bloecke.
- [DONE] S0 Spec Freeze Pack durchgefuehrt: alte Specs mit Superseded-Hinweis versehen, verbleibende Konflikte gelistet, Legacy-Code quarantined und fachliche Ordner als Quellenstatus markiert.
- [DONE] Child Specs fuer S0-S7 unter `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs` angelegt.
- [DONE] S1 Vertikalen Architektur-Spike umgesetzt: kleinster lauffaehiger Pfad durch .NET-Starter, Survey-Handoff, Bundle-Dummy, Provider-Stub und Harness.
- [DONE] Fuer S1 konkrete Verification Cases definieren: lokaler Fallback, Server-Handoff, fehlender Provider, ungueltiges Bundle, Survey-Handoff-Fehler, Secret-Leak-Check, jeweils lokal und im Docker-Minimalharness.
- [DONE] Nach S1 die Coverage-Matrix aktualisiert: S1-belegte Bereiche sind als `[DONE S1]` oder `[PARTIAL S1]` markiert, spaeterer Scope bleibt sichtbar.
- [DONE] S2 Survey Delivery und Answer Handoff umgesetzt und akzeptiert: 12 lokale und 12 Docker-Harness-Cases pruefen Survey-Service, Fragebezug, Handoff, Retention, Redaction und Blocker.

### Offene Punkte

- [MISSING SPEC non-blocking: Konkretes Bundle-Manifest-Beispiel fuer Free Entry, Paid Pilot und Managed AI.]
- [MISSING SPEC non-blocking: Provider-Guides mit aktueller visueller Nutzerfuehrung.]
- [MISSING SPEC non-blocking: Finaler Wortlaut der Report-Hinweise fuer A/B/C.]

### S1 Spike-Erfolgskriterien

Der Spike ist erfolgreich, wenn ein isolierter Testlauf mindestens diese Artefakte erzeugt oder absichtlich blockiert:

- `survey/answers.json`.
- `survey/import-manifest.json`.
- lokaler Vault-/Workbench-Ordner.
- Bundle-Readiness-Status.
- Provider-Readiness-Status, im Spike als Stub erlaubt.
- Run-Manifest mit Exit-Code und Blockerstatus.
- Harness-Log ohne Host-Secrets.

Der Spike ist nicht erfolgreich, wenn er nur eine UI oder nur einen Containerstart zeigt, aber keine Datenuebergabe, keine Artefakte und keine Blockerlogik beweist.

## History

| Date | Iteration | Author | Delta |
|---|---:|---|---|
| 2026-05-04 | 1 | Codex | Initialen Slice-Plan mit Scope-Schutzregeln, Slice-Zuschnitt und Coverage-Matrix aus der v2-Master-Spec erstellt. |
| 2026-05-05 | 2 | Codex | S0 Repo Freeze als erledigt markiert und Child Specs fuer S0-S7 als naechste Spezifikationsschicht ergaenzt. |
| 2026-05-05 | 3 | Codex | S1-Slice-Plan an die konkretisierte S1-Spec angepasst: Docker-Minimalharness, definierte Verification Cases, slice-bezogene Harness-Abdeckung und `preflight_only` Agent-Config-Stub nachgezogen. |
| 2026-05-05 | 4 | Codex | S1-Implementierung abgeschlossen und Coverage-Matrix mit `[DONE S1]`/`[PARTIAL S1]` gegen lokale und Docker-Harness-Evidence aktualisiert. |
| 2026-05-05 | 5 | Codex | S1 nach akzeptiertem OpenSpec-Closeout als Accepted markiert; OpenSpec-Archiv `2026-05-05-free-entry-v2-s1-vertical-spike` ist kanonische Abschluss-Evidence. |
| 2026-05-05 | 6 | User/Codex | S2 nach akzeptiertem OpenSpec-Closeout als Accepted markiert; Survey-Handoff-Coverage auf `[DONE S2]`/`[PARTIAL S2]` aktualisiert. |
