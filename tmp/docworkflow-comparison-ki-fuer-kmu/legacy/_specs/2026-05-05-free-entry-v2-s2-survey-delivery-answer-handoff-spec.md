**Date:** 2026-05-05  
**Status:** 🟢 Accepted  
**Scope:** Survey-Delivery-Service, lokaler Fallback, kanonisches Antwortartefakt, Handoff-Token, Import und Retention.

---

## 1. Ziel

S2 macht den Survey-Handoff produktionsnah: server-rendered online, lokal fallbackfaehig und mit automatisch lokal importierten Antwortartefakten.

## 2. In Scope

- Survey-Session-Start.
- Server-gerendertes Survey-HTML.
- Lokaler Survey-Fallback.
- Kurzlebiges Handoff-Token.
- Integritaets-/Versions-/Vollstaendigkeitspruefung.
- Lokaler Import von `survey/answers.json` und `survey/import-manifest.json`.
- Retention- und Delete-Status im Import-Manifest.

## 3. Out of Scope

- Finaler Wortlaut aller Survey-Fragen.
- ROI-Agent.
- Provider-Aktivierungsguides.
- Content-Bundle-Installation.

## 4. Master-Spec-Abdeckung

- V2-FR-010 Survey-Definition.
- V2-FR-010a Survey-Delivery-Service und Antwortdaten-Uebergabe.
- V2-FR-060 Artefaktstruktur.
- V2-FR-061 Run-Manifest.
- V2-NFR-001 Sicherheit.

## 5. Akzeptanz

- Online-Modus und lokaler Fallback erzeugen dasselbe kanonische Antwortschema.
- Bei Hash-/Signatur-/Versionsfehler startet kein ROI/RAG-Folgeschritt.
- Nutzer muss keine JSON-Datei manuell herunterladen.
- Import-Manifest dokumentiert Datenresidenz, Retention und Server-Delete-Status.

## 6. Normativer S2-Vertrag

S2 ersetzt den S1-SurveyStub-Vertrag durch einen produktionsnahen API-/Artefaktvertrag, bleibt aber kompatibel zu den bereits erzeugten lokalen Zielartefakten.

### 6.1 Komponenten

- `FreeEntry.App` oder lokale Wizard-Huelle startet eine Survey-Session und fuehrt den Nutzer zum Survey.
- Survey-Delivery-Service rendert freigegebenes Survey-HTML fuer die gewaehlte Survey-Version.
- `FreeEntry.Core` importiert das Antwortartefakt in den lokalen Run-Workspace.
- Lokaler Fallback erzeugt dasselbe Antwortartefakt ohne Server.

### 6.2 Survey-Delivery-API

Der produktionsnahe Service muss mindestens diese HTTP-Oberflaeche bereitstellen:

- `GET /health` gibt `200` mit `{"status":"ok"}` zurueck.
- `POST /sessions` nimmt `site_id`, `survey_profile`, `business_type`, `survey_version`, optional `resume_token` und optional `consents` entgegen.
- `POST /sessions` gibt `survey_session_id`, `handoff_id`, `handoff_token`, `render_mode="server_rendered"`, `survey_url`, `survey_version`, `survey_definition_id`, `survey_definition_sha256` und `expires_at_utc` zurueck.
- `GET /survey-definitions/{survey_definition_id}` liefert die aktive Survey-Definition gemaess Abschnitt 6.4.
- `GET /sessions/{survey_session_id}/html` liefert server-gerendertes HTML fuer die freigegebene Survey-Version oder leitet auf `survey_url`.
- `POST /sessions/{survey_session_id}/answers` nimmt ein oder mehrere Antwortobjekte gemaess Abschnitt 6.5 entgegen und speichert sie als temporaeren Session-Zwischenstand.
- `POST /sessions/{survey_session_id}/complete` validiert Pflichtfelder, Fragebezug und Antworttypen, friert die Session fuer den Export ein und gibt `survey_session_id`, `handoff_id`, `handoff_ready=true`, `answers_sha256` und `expires_at_utc` zurueck.
- `GET /handoffs/{handoff_id}/answers` nimmt `Authorization: Bearer <handoff_token>` an und gibt ein Antwortpaket gemaess Abschnitt 6.5 zurueck.
- `POST /handoffs/{handoff_id}/import-confirmations` nimmt `answers_sha256`, `imported_at_utc`, `local_run_id` und `survey_import_status` entgegen und gibt den aktuellen `server_delete_status` zurueck.

Server-gerendertes HTML darf intern klassische Form-Posts nutzen, muss aber semantisch denselben Antwortvertrag wie `POST /sessions/{survey_session_id}/answers` erfuellen. Die Harness darf den Browserpfad durch direkte API-Submission ersetzen, wenn sie trotzdem Session-Start, Health, Complete, Handoff-Abruf, Import und Artefaktvalidierung ausfuehrt.

Nicht normativ fuer S2 sind Authentifizierung jenseits des kurzlebigen Handoff-Tokens, CRM-/Lead-Persistenz, finale UI-Texte und finaler fachlicher Wortlaut aller Survey-Fragen.

### 6.3 Token- und Session-Regeln

- Handoff-Tokens sind kurzlebig, nur fuer genau einen `handoff_id` gueltig und duerfen nicht in Logs, Reports oder Manifeste geschrieben werden.
- Abgelaufene oder falsche Tokens enden mit `401` oder einem aequivalent maschinenlesbaren Fehler.
- Handoff-Abruf vor erfolgreichem `POST /sessions/{survey_session_id}/complete` endet mit `409` oder einem aequivalent maschinenlesbaren Fehler `handoff_not_ready`.
- Der Service darf Survey-Antworten nur als temporaeren Session-Zwischenstand halten, bis lokaler Import bestaetigt oder Retention abgelaufen ist.
- Der lokale Fallback darf kein Handoff-Token simulieren muessen; er muss aber `source="local_fallback"` und einen aequivalenten Integritaetsnachweis im Import-Manifest schreiben.

### 6.4 Survey-Definition-Vertrag

S2 definiert nicht den finalen fachlichen Fragenkatalog; dieser bleibt S5. S2 muss aber eine stabile technische Survey-Definition bereitstellen, damit Antwortartefakte reproduzierbar validiert werden koennen.

Normative S2-Baseline:

- Maschinenlesbare lokale Definitionen nutzen die Dateinamen aus der Hauptspec:
  - `survey-v2-a-einsteiger.json`
  - `survey-v2-b-anwender.json`
  - `survey-v2-c-technisch.json`
- Fuer S2-Harness-Cases liegen gepinnte technische Fixture-Definitionen unter `v2/tests/harness/fixtures/survey-definitions/`.
- Die Fixture-Definitionen duerfen kurze Test-Fragetexte verwenden, muessen aber stabile `question_id`, `question_revision`, `question_path`, `answer_type`, Pflichtfeld- und Validierungsregeln enthalten.
- Lokaler Fallback laedt dieselbe aktive Definition wie der Online-Pfad aus Package, Content-Bundle oder Harness-Fixture. Unterschiedliche Online-/Fallback-Fragenschemata sind fuer denselben `survey_definition_id` nicht erlaubt.

Eine Survey-Definition enthaelt mindestens:

- `survey_definition_id`
- `schema_version`
- `survey_version`
- `survey_profile`
- `definition_source`: `server_release`, `package_pinned`, `content_bundle` oder `harness_fixture`
- `questions[]` mit `question_id`, `question_revision`, `question_path`, `prompt`, `answer_type`, `required_when`, optional `allowed_values` und optional `validation`
- optionale `routing_rules`

`survey_definition_sha256` ist der SHA-256-Hash der kanonischen Survey-Definition gemaess Abschnitt 6.5. Ein Import darf nur erfolgreich sein, wenn `survey_definition_id` und `survey_definition_sha256` aus Session, Antwortpaket, lokalem Artefakt und Import-Manifest uebereinstimmen.

### 6.5 Antwortartefakt und Integritaet

Das serverseitige Antwortpaket enthaelt mindestens:

- `answers`
- `answers_sha256`
- `integrity_proof` oder `server_signature`
- `schema_version`
- `survey_version`
- `survey_definition_id`
- `survey_definition_sha256`
- `survey_session_id`
- `handoff_id`
- `source="survey_delivery_service"`
- `retention_policy`
- `server_delete_status`

`survey/answers.json` enthaelt mindestens:

- `schema_version`
- `survey_version`
- `survey_definition_id`
- `survey_definition_sha256`
- `survey_profile`
- `business_type`
- `render_mode`
- `completed_at_utc`
- `answers`
- `process_candidates`
- `document_intake`
- `consents`

`answers` ist normativ eine Liste strukturierter Antwortobjekte, keine lose Map ohne Fragebezug. Jedes Antwortobjekt enthaelt mindestens:

- `question_id`: stabiler maschinenlesbarer Fragen-Identifier aus der aktiven Survey-Definition.
- `question_revision`: Revision der Frage innerhalb der Survey-Definition, falls die Frage bei gleicher fachlicher Bedeutung textlich angepasst wird.
- `question_path`: logischer Pfad, zum Beispiel `profile.business_type` oder `roi.monthly_hours`.
- `question_prompt_snapshot`: der dem Nutzer angezeigte Fragetext oder eine kanonische Kurzfassung zum Zeitpunkt der Beantwortung.
- `answer_type`: zum Beispiel `single_choice`, `multi_choice`, `number`, `text`, `boolean`, `consent`.
- `answer_value`: normalisierter Antwortwert.
- `answered_at_utc`.
- `required`: ob die Frage fuer diesen Pfad Pflichtfrage war.

`survey_definition_sha256` hasht die kanonische Survey-Definition inklusive Frage-IDs, Fragetexten, Antworttypen, Routing- und Pflichtfeldregeln. Der Import darf nur erfolgreich sein, wenn jede Antwort auf eine bekannte Frage der aktiven Survey-Definition verweist und Antworttyp sowie Pflichtfeldregeln passen.

Kanonische Hash-/Integritaetsregeln:

- Kanonisches JSON nutzt UTF-8 ohne BOM, lexikografisch sortierte Objekt-Properties, stabile Array-Reihenfolge, keine irrelevanten Whitespaces, ISO-8601-UTC-Zeitstempel und kulturinvariante Zahlenformatierung.
- `answers_sha256` ist der lowercase-hex SHA-256 ueber das kanonische JSON des vollstaendigen `survey/answers.json`-Objekts.
- `survey_definition_sha256` ist der lowercase-hex SHA-256 ueber das kanonische JSON der aktiven Survey-Definition.
- Der Integritaetsnachweis signiert oder belegt mindestens diesen kanonischen Payload: `schema_version`, `survey_version`, `survey_definition_id`, `survey_definition_sha256`, `survey_session_id`, `handoff_id`, `source`, `answers_sha256`, `retention_policy`.
- S2-Harness-Fixtures duerfen einen deterministischen Testnachweis wie `integrity_proof="s2-fixture-valid"` verwenden, muessen aber dieselbe Payload-Bindung und dieselben Negativfaelle pruefen. Produktive Signatur-/Key-Infrastruktur bleibt ausserhalb von S2.

`survey/import-manifest.json` enthaelt mindestens:

- `survey_session_id`
- `handoff_id`
- `source`
- `imported_at_utc`
- `answers_sha256`
- `survey_definition_sha256`
- `integrity_proof` oder `server_signature`
- `survey_import_status`
- `retention_policy`
- `server_delete_status`
- `data_residency`
- `answer_question_refs_validated`

Status-Namensentscheidung:

- `survey_import_status` ist ab S2 der normative Feldname in `survey/import-manifest.json` und im Run-Manifest.
- ADR-003s `import_status` gilt fuer S2 als historischer Alias. Implementierungen duerfen ihn beim Einlesen akzeptieren, muessen aber neu geschriebene Artefakte mit `survey_import_status` erzeugen.
- Run-Manifest und Import-Manifest muessen denselben Statuswert tragen, wenn ein Survey-Import versucht wurde.

Fuer `source="local_fallback"` gelten diese ID-Regeln:

- `survey_session_id` ist eine lokale synthetische ID im Format `local-session-<run_id>`.
- `handoff_id` ist eine lokale synthetische ID im Format `local-handoff-<run_id>`.
- `server_delete_status` ist `not_applicable_local_fallback`.
- Handoff-Token-Felder duerfen im lokalen Fallback nicht geschrieben werden.

### 6.6 Statuswerte

Normative `survey_import_status`-Werte:

- `imported`
- `blocked_integrity_failed`
- `blocked_version_incompatible`
- `blocked_incomplete_answers`
- `blocked_unknown_question`
- `blocked_answer_schema_invalid`
- `blocked_token_expired`
- `blocked_export_unavailable`
- `blocked_local_write_failed`
- `paused_server_unavailable`
- `local_fallback_imported`

Normative `server_delete_status`-Werte:

- `not_applicable_local_fallback`
- `pending_import_confirmation`
- `delete_confirmed`
- `delete_failed_retryable`
- `retained_with_consent`
- `retention_expired`
- `unknown`

Fehlerhafte Handoffs, inkompatible Versionen und unvollstaendige Pflichtantworten duerfen weder `survey_import_status=imported` noch `local_fallback_imported` setzen.

## 7. Kontrollfluss und Fehlerfaelle

### 7.1 Online-Erfolg

1. Starter erzeugt oder nutzt lokale `site_id`.
2. Starter ruft `POST /sessions` auf.
3. Starter oder Browser laedt die aktive Survey-Definition beziehungsweise server-gerendertes HTML.
4. Nutzer beantwortet server-gerenderten Survey; die Antworten werden ueber `POST /sessions/{survey_session_id}/answers` oder aequivalente HTML-Form-Posts in der Server-Session gespeichert.
5. Survey-Abschluss ruft `POST /sessions/{survey_session_id}/complete` auf.
6. Starter ruft Antwortpaket per Handoff-Token ab.
7. Starter prueft Hash, Integritaetsnachweis, Schema-Version, Survey-Version, Survey-Definition, Fragebezug, Antworttypen und Vollstaendigkeit.
8. Starter schreibt `survey/answers.json` und `survey/import-manifest.json`.
9. Starter bestaetigt lokalen Import.
10. Folgepfade duerfen erst nach erfolgreichem Import starten.

### 7.2 Lokaler Fallback

Der lokale Fallback wird genutzt, wenn der Server nicht erreichbar ist, Safe-Test/Offline explizit gewuenscht ist oder die Harness den lokalen Pfad prueft. Er muss dieselbe `survey/answers.json`-Struktur und ein Import-Manifest mit `survey_import_status=local_fallback_imported` erzeugen.

### 7.3 Blockerfaelle

- Server nicht erreichbar: lokaler Fallback anbieten oder Lauf mit `survey_import_status=paused_server_unavailable` pausieren.
- Handoff-Token abgelaufen: neuen Export anfordern oder Session wieder aufnehmen; kein Folgepfad.
- Hash/Signatur/Integritaetsnachweis ungueltig: Exit `20`, `survey_import_status=blocked_integrity_failed`, kein ROI/RAG.
- Inkompatible Schema- oder Survey-Version: Exit `20`, `survey_import_status=blocked_version_incompatible`, kein ROI/RAG.
- Pflichtantworten unvollstaendig: Exit `20`, `survey_import_status=blocked_incomplete_answers`, kein ROI/RAG.
- Antwort referenziert keine bekannte Frage der aktiven Survey-Definition: Exit `20`, `survey_import_status=blocked_unknown_question`, kein ROI/RAG.
- Antworttyp passt nicht zur Frage oder verletzt definierte Antwortregeln: Exit `20`, `survey_import_status=blocked_answer_schema_invalid`, kein ROI/RAG.
- Lokales Schreiben fehlgeschlagen: klarer Nutzerhinweis zu Speicherort/Berechtigung, kein erfolgreicher Importstatus.
- Server-Loeschbestaetigung fehlt: lokaler Import bleibt gueltig, `server_delete_status=unknown` oder `delete_failed_retryable` wird sichtbar dokumentiert.

## 8. Harness- und Verification-Cases

S2 muss die S1-Harness erweitern, nicht ersetzen. Die S2-Harness muss lokal und im Docker-Container laufen. Fuer `server_rendered`-Cases startet die Docker-Harness den Survey-Delivery-Service im Container, uebergibt die im Case definierten Survey-Antworten an die Service-Session und validiert danach Handoff, lokalen Import und Artefakte.

### 8.1 Harness-Eingabevertrag

Jeder S2-Case enthaelt mindestens:

- `survey.mode`: `server_rendered` oder `local_fallback`.
- `survey.profile`, `survey.business_type`, `survey.version`.
- `survey.definition_file` oder `survey.definition_id`: aktive Survey-Definition, gegen die Antworten validiert werden.
- `survey.definition_sha256`: erwarteter Hash der aktiven Survey-Definition.
- `survey.questions`: fuer den Case relevante Frage-IDs, Revisionen, Pfade, Antworttypen und Pflichtfeldregeln aus der aktiven Survey-Definition.
- `survey.answers`: strukturierte Testantworten mit `question_id`, `answer_type` und `answer_value`, die der Harness entweder an den Survey-Delivery-Service uebergibt oder im lokalen Fallback direkt in dasselbe kanonische Schema transformiert.
- `survey.expected_required_fields`: Pflichtfelder, deren Vollstaendigkeit vor Import-Erfolg geprueft wird.
- `survey.handoff`: optionales Fehlerprofil wie `valid`, `invalid_hash`, `invalid_signature`, `incompatible_version`, `expired_token`, `export_unavailable`.
- `expected_artifacts`: mindestens `survey/answers.json`, `survey/import-manifest.json` und relevante Run-Manifest-Felder.
- `forbidden_values`: Handoff-Tokens, Test-Secrets und andere Werte, die in keinem Artefakt/Log/Summary erscheinen duerfen.

Die Harness darf einen Case nicht dadurch bestehen lassen, dass sie ein fertiges `answers.json` direkt in den Workspace legt. Im Online-Pfad muss sie den Servicepfad ausfuehren: Session starten, Survey-Definition abrufen oder pinnen, Survey-Antworten an den Service uebergeben, Session abschliessen, Handoff abrufen, lokal importieren und danach gegen die erwarteten Artefakte pruefen.

Die Harness muss fuer jedes Antwortobjekt validieren, dass `question_id` in der aktiven Survey-Definition existiert, `question_revision` und `question_path` zur Definition passen, `answer_type` erlaubt ist und `answer_value` die Frage-Regeln erfuellt. Mindestens ein positiver Case muss im Artefakt beweisen, dass die Antwort nicht nur gespeichert, sondern der konkreten Frage zugeordnet wurde.

### 8.2 Pflicht-Cases

Mindestens diese Cases muessen lokal und im Docker-Gate laufen:

| Case | Zweck | Erwartung |
|---|---|---|
| `s2-001-online-handoff-success.yaml` | Survey-Delivery-Service erzeugt produktionsnahes Antwortpaket. | Exit `0`, `render_mode=server_rendered`, `survey_import_status=imported`, Import-Confirmation gesendet. |
| `s2-002-local-fallback-equivalence.yaml` | Lokaler Fallback erzeugt dasselbe kanonische Schema. | Exit `0`, `survey_import_status=local_fallback_imported`, `server_delete_status=not_applicable_local_fallback`. |
| `s2-003-invalid-integrity-blocks.yaml` | Hash oder Integritaetsnachweis passt nicht. | Exit `20`, kein erfolgreicher `answers.json`-Import, kein ROI/RAG. |
| `s2-004-version-incompatible-blocks.yaml` | Schema-, Survey- oder Survey-Definition-Version inkompatibel. | Exit `20`, `survey_import_status=blocked_version_incompatible`. |
| `s2-005-token-expired-blocks.yaml` | Handoff-Token abgelaufen oder falsch. | Exit `20`, `survey_import_status=blocked_token_expired`. |
| `s2-006-server-unavailable-fallback.yaml` | Service nicht erreichbar. | Lokaler Fallback oder pausierter Lauf, kein stiller Datenverlust. |
| `s2-007-retention-delete-status.yaml` | Import-Confirmation und Delete-Status werden dokumentiert. | Import-Manifest enthaelt `retention_policy`, `server_delete_status` und `data_residency`. |
| `s2-008-token-redaction.yaml` | Token/Secrets tauchen in Artefakten nicht auf. | Keine Handoff-Tokens in Logs, Reports, Manifests oder Harness-Summaries. |
| `s2-009-question-answer-link.yaml` | Antworten sind konkreten Fragen der Survey-Definition zugeordnet. | Exit `0`, jedes Antwortobjekt enthaelt `question_id`, `question_revision`, `question_path`, `question_prompt_snapshot`, `answer_type`, `answer_value`; Manifest setzt `answer_question_refs_validated=true`. |
| `s2-010-unknown-question-blocks.yaml` | Antwort referenziert eine nicht existierende Frage. | Exit `20`, `survey_import_status=blocked_unknown_question`, kein ROI/RAG. |
| `s2-011-answer-type-mismatch-blocks.yaml` | Antworttyp passt nicht zur Frage. | Exit `20`, `survey_import_status=blocked_answer_schema_invalid`, kein ROI/RAG. |
| `s2-012-canonical-hash-mismatch-blocks.yaml` | Service und Importer sehen unterschiedliche kanonische Antwort- oder Definition-Hashes. | Exit `20`, `survey_import_status=blocked_integrity_failed`, kein ROI/RAG. |

## 9. Verification Commands

Execution Context:

- Working directory: `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`.
- Shell: `zsh` auf macOS fuer lokale Entwicklung.
- Runtime target: .NET 10 SDK.
- SDK-Auswahl: Wie in S1 laufen `dotnet`-Commands aus `/tmp`, damit der Vault-Parent-`global.json` die SDK-Auswahl nicht verfaelscht.
- Runtime-Readiness: Survey-Delivery-Service-Checks nutzen Poll/Retry auf `GET /health`.
- Scope-Guard-Baseline: aktueller Git-Working-Tree vor S2-Implementierungsbeginn; vorhandene S1-Artefakte und unrelatierte lokale Aenderungen werden nicht zurueckgesetzt.
- Anti-Loop-Regel: Die Commands verifizieren Implementierung und Artefakte, nicht rekursiv die Verification selbst.
- Docker-Gate: Der Survey-Delivery-Service laeuft fuer `server_rendered`-Cases innerhalb des Harness-Containers. Die Harness wartet per Poll/Retry auf dessen `GET /health`, bevor sie Antworten uebergibt oder Handoff-Assertions ausfuehrt.

Preflight:

```bash
cd /tmp
dotnet --version
dotnet --list-sdks | rg '^10\.'
docker version
dotnet restore /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln
```

Gate Verification:

```bash
cd /tmp
dotnet build /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln --configuration Release --no-restore
dotnet test /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln --configuration Release --no-build
/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/scripts/run-harness.sh --case s2 --workspace /Users/dh/Documents/DanielsVault/ki-fuer-kmu/.safe-test/s2
docker build -f /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/tests/harness/Dockerfile -t free-entry-v2-s2-harness /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2
docker run --rm \
  -e S2_TEST_HANDOFF_TOKEN=S2_TEST_HANDOFF_TOKEN \
  -e S2_TEST_SECRET_VALUE=S2_TEST_SECRET_VALUE \
  -v /Users/dh/Documents/DanielsVault/ki-fuer-kmu/.safe-test/s2-docker:/work/out \
  free-entry-v2-s2-harness \
  /app/scripts/run-harness.sh --case s2 --workspace /work/out
```

Erfolg:

- Build, Tests, lokale Harness und Docker-Harness enden mit Exit `0`.
- Lokale Harness und Docker-Harness erzeugen je eine `harness-summary.json`.
- Die Docker-Harness weist pro `server_rendered`-Case nach, dass der Survey-Delivery-Service im Container gestartet wurde, `GET /health` erfolgreich war, die Survey-Definition geladen wurde, die Case-Antworten ueber den Servicepfad mit Fragebezug in `survey/answers.json` gelandet sind und die Session per Complete abgeschlossen wurde.
- Jeder S2-Case enthaelt im Summary mindestens `case_id`, `ran`, `exit_code`, `expected_exit_code`, `passed`, `survey_service_started`, `survey_definition_loaded`, `survey_answers_submitted`, `survey_session_completed`, `handoff_validated`, `answer_question_refs_validated`, `artifact_paths`.
- Secret-/Token-Leak-Assertions pruefen mindestens `logs/`, `run-manifest.json`, `survey/import-manifest.json`, `survey/answers.json`, alle Reports und alle Harness-Summaries.

Wenn S2 statt Single-Container-Harness eine Compose-/Multi-Service-Harness einfuehrt, muss diese Spec vor Umsetzung die konkrete Compose-Kommandoform ersetzen oder ergaenzen; ein Docker-Gate bleibt verpflichtend.

## 10. Definition of Ready fuer Umsetzung

- Scope ist auf Survey-Delivery-Service, lokalen Fallback, kanonisches Antwortartefakt, Handoff-Import und Retention begrenzt.
- Non-Goals sind in Abschnitt 3 festgelegt.
- Decision Freeze Pack: Option C aus ADR-003 ist gesetzt; .NET-Starter bleibt lokale Importinstanz; manuelles JSON bleibt ausgeschlossen; serverseitige Antworten bleiben temporaere Session-Daten.
- Referenz-Baseline: Master-Spec `V2-FR-010`, `V2-FR-010a`, `V2-FR-060`, `V2-FR-061`, `V2-NFR-001`, ADR-003 und S1-Handoff-Vertrag.
- Abnahmeszenarien sind in Abschnitt 8 definiert.
- Verifikationskommandos sind in Abschnitt 9 definiert.
- Offene Risiken: finale Survey-Fragentexte liegen in S5; finale Datenschutz-/Einwilligungstexte muessen vor produktiver Nutzung rechtlich/fachlich freigegeben werden, blockieren aber den technischen S2-Vertrag nicht.

## 11. Closeout Evidence

Akzeptiert am 2026-05-05 nach erneutem Verification-Replay:

- .NET 10 Preflight, Docker Preflight und Restore erfolgreich.
- Release-Build erfolgreich mit 0 Warnungen und 0 Fehlern.
- Release-Tests erfolgreich: 6/6 Tests bestanden.
- Lokale S2-Harness erfolgreich: 12/12 Cases bestanden, Summary unter `.safe-test/s2-closeout/harness-summary.json`.
- Docker-S2-Harness erfolgreich: 12/12 Cases bestanden, Summary unter `.safe-test/s2-docker-closeout/harness-summary.json`.
- OpenSpec-Change `free-entry-v2-s2-survey-handoff` validiert, in `openspec/specs/free-entry-v2-s2/spec.md` synchronisiert und nach `openspec/changes/archive/2026-05-05-free-entry-v2-s2-survey-handoff/` archiviert.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S2 Child Spec aus ADR-003 und Master-Spec abgeleitet. |
| 2026-05-05 | Codex | Review-Findings autonom aufgeloest: S2 API-/Artefaktvertrag, Fehlerstatus, Retention, Harness-Cases und DoR ergaenzt. |
| 2026-05-05 | Codex | Docker-Gate fuer Survey-Delivery-Service im Harness-Container und Survey-Antwort-Eingabevertrag ergaenzt. |
| 2026-05-05 | Codex | Frage-Antwort-Zuordnung ueber `question_id`, Survey-Definition-Hash, Antwortobjektstruktur und Harness-Blockerfaelle ergaenzt. |
| 2026-05-05 | Codex | Auto-Resolve-Findings behoben: Submit-/Complete-API, Survey-Definition-Baseline, kanonische Hash-Regeln, lokale Fallback-IDs und Import-Status-Alias festgelegt. |
| 2026-05-05 | Codex | Status auf Plan gesetzt: OpenSpec-Scope-Contract fuer S2 Survey Delivery und Handoff fixiert. |
| 2026-05-05 | Codex | S2 implementiert und verifiziert: lokale und Docker-Harness bestehen mit Survey-Delivery-Service, Fragebezug, Handoff-Import, Retention und Redaction. |
| 2026-05-05 | User/Codex | Change akzeptiert und S2 nach Closeout-Replay als Accepted geschlossen; OpenSpec-Archiv ist kanonische Abschluss-Evidence. |

SessionId: codex-free-entry-v2-s2-survey-handoff-2026-05-05
