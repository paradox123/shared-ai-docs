**Date:** 2026-05-05  
**Status:** 🟢 Accepted  
**Scope:** Minimaler vertikaler Architektur-Spike fuer .NET-Starter, Survey-Handoff, Dummy-Bundle, Provider-Stub und Harness.

---

## 1. Ziel

S1 beweist den kleinsten lauffaehigen Free-Entry-v2-Kontrollfluss mit echten Schnittstellen, echten Artefaktnamen und deterministischer Harness. Der Spike ersetzt den quarantined Node/OpenSpec-Legacy-Prototyp nicht fachlich vollstaendig, sondern setzt die neue technische Tragschicht fuer S2-S7.

Der Spike ist erfolgreich, wenn ein isolierter Lauf nachweisbar:

1. einen .NET-Starter/Runner ausfuehrt,
2. Survey-Antworten ueber einen Stub-Handoff oder lokalen Fallback nach `survey/answers.json` importiert,
3. ein Dummy-Free-Entry-Bundle prueft,
4. Provider-Readiness als Stub dokumentiert,
5. eine lokale Workbench-/Vault-Struktur anlegt,
6. ein maschinenlesbares Run-Manifest schreibt,
7. Blockerfaelle deterministisch stoppt,
8. keine Host-Secrets in Logs, Reports oder Manifesten ausgibt.

## 2. In Scope

- Moderner .NET-Starter/Wizard/Runner-Durchstich gemaess ADR-002.
- Survey-Delivery-Service-Stub und lokaler Fallback gemaess ADR-003.
- Automatischer Import von `survey/answers.json` und `survey/import-manifest.json`.
- Dummy-Free-Entry-Bundle mit Manifest, Hash-/Signatur-Stub, erwarteten Dateien und Readiness-Status gemaess ADR-001.
- Provider-Readiness-Stub mit `provider_ready=true/false` und `activation_status`.
- Lokale Workbench-/Vault-Stub-Struktur mit Ergebnisordnern.
- Run-Manifest gemaess Master-Spec `V2-FR-061`, soweit fuer den Spike sinnvoll belegbar.
- Agent-Konfigurations-Stub gemaess Master-Spec `V2-FR-062`, nur im Modus `preflight_only`.
- Szenariobasierte Harness mit mindestens den S1-Case-Dateien aus Abschnitt 10.
- Minimaler Docker-Harness, der die S1-Cases in einem nackten Container mit injizierten YAML/JSON-Testdaten ausfuehrt.
- Secret-Redaction fuer Harness-Logs, Run-Manifest und Fehlertexte.
- .NET-10-Verifikation ohne neues lokales `global.json`; die Commands muessen den vorhandenen Vault-Parent-`global.json` bewusst umgehen.

## 3. Out of Scope

- Vollstaendige Survey-v2-Inhalte.
- Echte Provider-Guides.
- Echte LLM-Modellaufrufe.
- Vollstaendige RAG-/ROI-Runtime.
- Produktives Packaging, Signing oder Notarisierung.
- Echte kryptografische Signaturvalidierung. S1 nutzt einen deterministischen Signatur-Stub.
- Echte Server-Retention-Implementierung. S1 dokumentiert Retention nur im Import-Manifest.
- Git/GitHub-Zugang, private Repo-Credentials oder Managed-AI-Updatekanal.
- Obsidian-Community-Plugin-Installation. S1 legt hoechstens ein Plugin-Baseline-Protokoll als Stub an.
- Produktive Kundensystem-Scans, Dateisystem-Inventarisierung ausserhalb des Harness-Workspace oder Dokumentenverarbeitung.

## 4. Fuehrende Quellen

S1 wird nur aus diesen Quellen umgesetzt:

1. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
2. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/APPLICATION-FLOW.md`
3. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md`
4. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/adr/001-repo-access-and-ip-protection.md`
5. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/adr/002-starter-wizard-runner-technology-stack.md`
6. `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/adr/003-survey-delivery-and-answer-handoff.md`

Der alte technische Prototyp unter `_legacy/v1-node-prototype` darf nur als historische Detailquelle fuer Testideen und Artefaktbeispiele gelesen werden. Er darf keine V2-Projektstruktur, keine V2-Runtime und keine V2-Defaults vorgeben.

## 5. Master-Spec-Abdeckung

- Fuehrende Reihenfolge.
- V2-FR-003 Entry, Download und Registrierung.
- V2-FR-010a Survey-Handoff.
- V2-FR-020/021 Aktivierungsstatus und Readiness.
- V2-FR-030 Vault und Arbeitsraum.
- V2-FR-031a Bundle-Manifest und Readiness.
- V2-FR-060/061 Artefaktstruktur und Run-Manifest.
- V2-FR-062 Agent-Konfiguration.
- V2-FR-063 Exit-Codes.
- V2-NFR-001 Sicherheit.
- Docker- und Test-Harness als S1-Startpunkt fuer S7.

## 6. Decision Freeze Pack

| Entscheidung | S1-Freeze |
|---|---|
| Starter-/Runner-Stack | .NET 10, lokale V2-Codebasis unter `v2`, kein Node/Shell als Kundenstarter, kein neues `v2/global.json` als Pflichtartefakt. |
| Wizard-UX im Spike | Minimaler lokaler Browser-/HTTP- oder CLI-faehiger Durchstich ist erlaubt; die Kunden-UX wird noch nicht finalisiert. |
| Survey-Modi | `server_rendered`, `local_fallback`, `preloaded_answers` als Harness-Modi. |
| Survey-Handoff | S1 nutzt Stub-Handoff mit kurzlebigem Test-Token oder lokalen Fallback; Zielartefakte sind bereits normativ. |
| Content-Zugang | Signiertes Free-Entry-Bundle als Zielmodell; S1 nutzt Dummy-Bundle mit Hash und Signatur-Stub. |
| Provider | Kein echter Provider. Nur Stub-Modi `none`, `stub_success`, `stub_failure`. |
| RAG/ROI | Blockiert oder `preflight_only`; keine ROI-Behauptung. |
| Secrets | Harness setzt Test-Secrets und prueft, dass sie nicht in Artefakten erscheinen. |
| Docker-Harness | Pflicht fuer S1 als minimaler nackter Containerlauf; kein voller Compose-/Multi-Service-/S7-Ausbau. |
| Exit-Code-Semantik | S1 nutzt Master-Spec-Codes, ergaenzt aber keine neue globale Exit-Code-Liste. |

## 7. Soll-Projektstruktur

Die Umsetzung soll eine neue V2-Codebasis anlegen. Namensdetails duerfen im Scope Contract angepasst werden, solange die Verantwortungsgrenzen erhalten bleiben.

```text
v2/
  FreeEntryV2.sln
  src/
    FreeEntry.App/
      FreeEntry.App.csproj
    FreeEntry.Core/
      FreeEntry.Core.csproj
    FreeEntry.SurveyStub/
      FreeEntry.SurveyStub.csproj
  tests/
    FreeEntry.Tests/
      FreeEntry.Tests.csproj
    harness/
      Dockerfile
      cases/
        001-success-local-fallback.yaml
        002-success-server-handoff.yaml
        003-provider-missing-preflight-only.yaml
        004-invalid-bundle-blocks.yaml
        005-invalid-survey-handoff-blocks.yaml
        006-secret-redaction.yaml
      fixtures/
        bundles/
        survey/
        secrets/
  scripts/
    run-harness.sh
  docs/
    FREE-ENTRY-V2-SLICE-PLAN.md
```

Rollen:

- `FreeEntry.App`: Starter/Runner-Entry-Point fuer Harness und spaeteren lokalen Assistenten.
- `FreeEntry.Core`: Artefakt-, Manifest-, Bundle-, Provider-Stub-, Redaction- und Handoff-Logik.
- `FreeEntry.SurveyStub`: minimaler Survey-Delivery-Service-Stub fuer `server_rendered` und Handoff-Export.
- `FreeEntry.Tests`: schnelle Unit-/Integrationstests fuer Core-Vertraege.
- `tests/harness`: szenariobasierte End-to-End-Verifikation ueber echte Prozesslaeufe.
- `tests/harness/Dockerfile`: nackte Containerumgebung fuer S1-Harness-Cases mit .NET 10 SDK, Testfixtures und ohne Host-Home-/Host-Secret-Abhaengigkeit.

### 7.1 Scope Contract fuer Delivery

S1 wird im Implementierungsmodus OpenSpec umgesetzt. Der aktive Change ist `openspec/changes/free-entry-v2-s1-vertical-spike`.

Der Scope Contract fuer die Umsetzung ist:

- In scope: die Projektstruktur aus Abschnitt 7, die Artefaktvertraege aus Abschnitt 8, die Kontrollfluss- und Harness-Cases aus Abschnitt 9 und 10, sowie die Verification Commands aus Abschnitt 12.
- Out of scope: echte Survey-v2-Inhalte, echte Provider, echte LLM-/ROI-/RAG-Runtime, produktives Bundle-Signing, produktiver Survey-Service, Git/GitHub-Zugang und S7-Vollmatrix.
- Akzeptanzziel: alle sechs S1-Harness-Cases laufen lokal und im Docker-Harness mit den erwarteten Artefakten, Exit-Codes und Secret-Leak-Assertions.
- Verification: Abschnitt 12 ist der normative Command-Vertrag. Abweichende Scriptnamen oder Projektpfade muessen vor Umsetzung in dieser Spec geaendert werden.
- Strukturentscheidung: die Ziel-Projektstruktur aus Abschnitt 7 ist bestaetigt. Namensdetails duerfen nur angepasst werden, wenn die Verantwortungsgrenzen der drei Projekte `App`, `Core` und `SurveyStub` erhalten bleiben.

## 8. Runtime- und Artefaktvertrag

Jeder S1-Lauf schreibt ausschliesslich in einen explizit uebergebenen Workspace, zum Beispiel:

```text
<workspace>/
  .kickstart/
    site_id
    session_tracking_id
  ai-bootcamp-runs/
    <timestamp>__<tenant_label>/
      run-manifest.json
      logs/
        harness.log
        runner.log
      survey/
        answers.json
        import-manifest.json
      workbench/
        vault/
          README.md
          _system/
            bundle-readiness.json
            plugin-baseline-stub.json
      agent/
        agent-config.json
    latest
```

Wenn die Harness mehrere Cases in einem Lauf ausfuehrt, muss sie unterhalb des uebergebenen Workspace pro Case einen eigenen isolierten Unterworkspace verwenden, zum Beispiel `<workspace>/<case-id>/`. `ai-bootcamp-runs/latest` wird nur innerhalb dieses Case-Workspaces ausgewertet. Der gemeinsame Harness-Summary darf im Root des uebergebenen Workspace liegen.

### 8.1 `survey/answers.json`

S1 muss mindestens diese Felder schreiben:

```json
{
  "schema_version": "free-entry-survey-answers.v1",
  "survey_version": "s1-spike",
  "survey_profile": "A",
  "business_type": "fitnessstudio",
  "render_mode": "local_fallback",
  "completed_at_utc": "2026-05-05T00:00:00Z",
  "answers": {},
  "process_candidates": [],
  "document_intake": {
    "has_process_documentation": false,
    "document_paths": []
  },
  "consents": {
    "server_processing": false,
    "document_processing": false
  }
}
```

Die Inhalte duerfen im Spike minimal sein. Wichtig ist das stabile Schema, nicht die fachliche Vollstaendigkeit des Surveys.

### 8.2 `survey/import-manifest.json`

S1 muss mindestens diese Felder schreiben:

```json
{
  "survey_session_id": "s1-local-session",
  "handoff_id": "s1-handoff",
  "source": "local_fallback",
  "imported_at_utc": "2026-05-05T00:00:00Z",
  "answers_sha256": "<sha256>",
  "server_signature": "stub-valid",
  "import_status": "imported",
  "retention_policy": "local_only",
  "server_delete_status": "not_applicable"
}
```

Bei fehlerhaftem Handoff darf `answers.json` nicht als erfolgreich importiertes Artefakt gelten. Das Run-Manifest muss den Blocker dokumentieren.

### 8.3 `run-manifest.json`

S1 muss mindestens diese Master-Spec-Felder belegen:

- `run_id`
- `session_tracking_id`
- `site_id`
- `tenant_key`
- `tenant_label`
- `user_role`
- `tech_experience_level`
- `segment_branch`
- `segment_company_size`
- `execution_mode`
- `activation_status`
- `provider_ready`
- `access_mode_resolved`
- `access_mode_source`
- `started_at_utc`
- `finished_at_utc`
- `first_run_key`
- `dedupe_group_id`
- `is_first_run`
- `registration_mode`
- `registration_status`
- `survey_render_mode`
- `survey_version`
- `survey_session_id`
- `survey_import_status`
- `survey_answers_path`
- `survey_answers_sha256`
- `survey_data_residency`
- `bundle_readiness_status`
- `bundle_id`
- `bundle_version`
- `bundle_sha256`
- `workbench_status`
- `exit_code`
- `blockers`

### 8.4 Dummy-Bundle-Fixture und Readiness

S1 nutzt kein produktives Bundle-Format, aber ein deterministisches Dummy-Bundle mit einem stabilen Fixture-Vertrag.

Gueltige Bundle-Fixtures liegen unter `v2/tests/harness/fixtures/bundles/<fixture-id>/` und enthalten mindestens:

```text
<fixture-id>/
  manifest.json
  content/
    README.md
```

`manifest.json` enthaelt mindestens:

```json
{
  "bundle_id": "free-entry-s1-dummy",
  "version": "s1.0.0",
  "channel": "free-entry",
  "created_at_utc": "2026-05-05T00:00:00Z",
  "sha256": "<sha256-of-content-tree>",
  "signature": "stub-valid",
  "signature_mode": "s1-deterministic-stub",
  "expected_files": [
    {
      "path": "content/README.md",
      "sha256": "<sha256>",
      "install_target": "workbench/vault/README.md"
    }
  ],
  "compatibility": {
    "starter": "free-entry-v2-s1",
    "spec": "2026-05-05-free-entry-v2-s1"
  },
  "conflict_policy": "overwrite_stub_workspace_only"
}
```

Der Signatur-Stub ist absichtlich klein: nur `signature="stub-valid"` mit `signature_mode="s1-deterministic-stub"` gilt als gueltig. Alle anderen Werte blockieren als ungueltiges Bundle.

S1-Readiness-Statuswerte fuer `bundle_readiness_status` sind:

- `ready`
- `blocked_invalid_bundle`
- `blocked_incompatible_bundle`
- `blocked_missing_expected_file`

Die Harness muss fuer `004-invalid-bundle-blocks.yaml` mindestens einen Hash-Mismatch oder eine fehlende erwartete Datei ausloesen. Beide Fehler muessen mit Exit `30`, `workbench_status=blocked` und einem redigierten Blocker im `run-manifest.json` enden. Ein fehlerhaftes Bundle darf keine erfolgreiche Workbench-/Vault-Installation melden.

### 8.5 `agent/agent-config.json`

S1 erzeugt nur einen Preflight-Stub:

```json
{
  "run_id": "s1-run",
  "site_id": "s1-site",
  "dry_run": true,
  "agent_mode": "preflight_only",
  "llm_mode": "not_configured",
  "activation_status": "no_ai_runtime_yet",
  "provider_ready": false,
  "rag_enabled": false,
  "rag_status": "disabled_no_docs",
  "rag_sources_path": null,
  "preprocessing_required_count": 0,
  "unsupported_format_count": 0,
  "qualification_gate_result": "not_evaluated_in_s1"
}
```

Die Beispielwerte sind Platzhalter. Zur Laufzeit muessen `run_id`, `site_id`, `activation_status`, `provider_ready` und `llm_mode` konsistent zum jeweiligen `run-manifest.json` sein.

Bei `provider_mode=stub_success` darf `provider_ready=true`, `activation_status=customer_owned_provider` und `llm_mode=provider_test` gesetzt werden, aber `agent_mode` bleibt in S1 `preflight_only`.

### 8.6 SurveyStub-Handoff-Vertrag

`FreeEntry.SurveyStub` ist in S1 nur ein lokaler Test-Double fuer Harness-Laeufe. Er ist kein produktiver Survey-Delivery-Service und keine S2-API-Festlegung.

Der Stub muss fuer `server_rendered` mindestens diese HTTP-Oberflaeche bereitstellen:

- `GET /health` gibt `200` mit `{"status":"ok"}` zurueck.
- `POST /sessions` nimmt `survey_profile`, `business_type` und optional `scenario` entgegen und gibt `survey_session_id`, `handoff_id`, `handoff_token`, `render_mode="server_rendered"` und `expires_at_utc` zurueck.
- `GET /handoffs/{handoff_id}/answers` nimmt den Handoff-Token per `Authorization: Bearer <token>` an und gibt ein Antwortpaket mit `answers`, `answers_sha256`, `server_signature`, `survey_version`, `survey_session_id`, `handoff_id`, `retention_policy` und `server_delete_status` zurueck.

Das minimale Antwortpaket des Stub muss in dieselbe `survey/answers.json`-Struktur aus Abschnitt 8.1 importierbar sein. `server_signature="stub-valid"` gilt als gueltiger Integritaetsnachweis. Der Runner muss `answers_sha256`, `server_signature`, `survey_version` und `handoff_id` pruefen, bevor `survey_import_status=imported` gesetzt wird.

Der Stub muss deterministische Fehler-Szenarien fuer die Harness unterstuetzen:

- `invalid_hash`: Antwortinhalt und `answers_sha256` passen nicht zusammen.
- `invalid_signature`: `server_signature` ist nicht `stub-valid`.
- `incompatible_version`: `survey_version` ist nicht `s1-spike`.
- `expired_token`: Handoff-Abruf endet mit `401` oder aequivalentem Stub-Fehler.

Jedes dieser Szenarien muss im Runner mit Exit `20`, `survey_import_status=blocked_integrity_failed`, keinem erfolgreichen `answers.json`-Import und keinem ROI-/RAG-Folgepfad enden. Wenn der HTTP-Service gestartet wird, wartet die Harness per Poll/Retry auf `GET /health`.

## 9. Kontrollfluss

### 9.1 Erfolgreicher Minimalpfad ohne Provider

1. Runner startet mit Harness-Case und isoliertem Workspace.
2. `.kickstart/site_id` und `.kickstart/session_tracking_id` werden erstellt oder wiederverwendet.
3. User-Profil/Betriebstyp werden aus dem Case gelesen.
4. Provider-Modus `none` setzt `activation_status=no_ai_runtime_yet` und `provider_ready=false`.
5. Survey laeuft als `local_fallback` oder `preloaded_answers`.
6. `survey/answers.json` und `survey/import-manifest.json` werden geschrieben.
7. Dummy-Bundle wird geprueft und installiert.
8. Workbench-/Vault-Stub wird angelegt.
9. `agent-config.json` wird als `preflight_only` geschrieben.
10. `run-manifest.json` meldet Erfolg fuer Vorbereitung, aber ROI/RAG blockiert wegen fehlendem Provider.
11. Exit-Code ist `0`, solange alle S1-Preflight-Artefakte erfolgreich erzeugt wurden und kein S1-Blocker vorliegt.

### 9.2 Erfolgreicher Pfad mit Provider-Stub

Wie 9.1, aber `provider_mode=stub_success` setzt:

- `activation_status=customer_owned_provider`
- `provider_ready=true`
- `llm_mode=provider_test`

S1 darf keinen echten ROI-Agenten starten. Das Run-Manifest muss sichtbar machen, dass ROI/RAG in spaeteren Slices liegen.

### 9.3 Blockerpfade

- Ungueltiges Bundle blockiert mit Exit `30` und `bundle_readiness_status=blocked_invalid_bundle`.
- Ungueltiger Survey-Handoff blockiert mit Exit `20` und `survey_import_status=blocked_integrity_failed`.
- Provider-Stub-Fehler blockiert nicht den ganzen Free-Entry-Preflight, solange der Case den Vorbereitungsmodus erwartet. Dann gilt `provider_ready=false` und `activation_status=no_ai_runtime_yet`.
- Unerwartete interne Fehler enden mit Exit `99`.

## 10. Docker- und Harness-Cases

Die S1-Harness muss lokal und im Docker-Container laufen. Der Docker-Pfad ist Teil der S1-Akzeptanz, weil der Spike beweisen soll, dass der Free-Entry-Runner in einer nackten Umgebung mit injizierten Testdaten reproduzierbar arbeitet.

Der Container-Harness:

- startet aus einem minimalen .NET-10-SDK-Image oder aequivalentem lokalen Build-Image,
- bekommt Cases und Fixtures als YAML/JSON/Testdateien,
- nutzt einen explizit gemounteten Output-Workspace,
- darf nicht auf Host-Home, Host-Keychain, echte Provider-Secrets oder lokale Daniel-Konfiguration zugreifen,
- setzt nur explizite Test-Secrets fuer Redaction-Assertions,
- schreibt alle Artefakte unter den gemounteten Harness-Workspace,
- erzeugt dieselbe `harness-summary.json` wie der lokale Harness.

Die S1-Harness muss mindestens diese Cases enthalten:

| Case | Zweck | Erwartung |
|---|---|---|
| `001-success-local-fallback.yaml` | Lokaler Survey-Fallback ohne Provider. | Exit `0`, Survey-Artefakte, Bundle ok, Workbench ok, `provider_ready=false`. |
| `002-success-server-handoff.yaml` | Survey-Server-Stub erzeugt Handoff. | Exit `0`, `render_mode=server_rendered`, Import-Manifest mit Handoff-ID. |
| `003-provider-missing-preflight-only.yaml` | Kein Provider bis Ende. | Exit `0`, Vorbereitungsstatus, keine ROI-Behauptung, `agent_mode=preflight_only`. |
| `004-invalid-bundle-blocks.yaml` | Falscher Hash oder fehlende erwartete Datei. | Exit `30`, kein Erfolg fuer Workbench, kein halb fertiger Erfolg. |
| `005-invalid-survey-handoff-blocks.yaml` | Hash-/Signatur-/Versionsfehler im Survey-Handoff. | Exit `20`, kein ROI/RAG, `survey_import_status=blocked_integrity_failed`. |
| `006-secret-redaction.yaml` | Test-Secrets im Environment und in Fixture-Eingaben. | Exit `0`, Secret-Werte erscheinen in keinem Log, Report oder Manifest. |

Empfohlenes Case-Schema:

```yaml
id: 001-success-local-fallback
workspace_mode: isolated_temp
survey:
  mode: local_fallback
  profile: A
  business_type: fitnessstudio
provider:
  mode: none
bundle:
  fixture: valid-free-entry-s1
expected:
  exit_code: 0
  files:
    - survey/answers.json
    - survey/import-manifest.json
    - run-manifest.json
    - agent/agent-config.json
  manifest:
    provider_ready: false
    survey_import_status: imported
    bundle_readiness_status: ready
  secret_leaks:
    forbidden_values:
      - S1_TEST_SECRET_VALUE
```

## 11. Akzeptanzkriterien

S1 ist akzeptiert, wenn alle Kriterien erfuellt sind:

- `survey/answers.json`
- `survey/import-manifest.json`
- lokaler Workbench-/Vault-Ordner als Stub
- Bundle-Readiness-Status
- Provider-Readiness-Status
- Run-Manifest mit Exit-Code und Blockerstatus
- `agent/agent-config.json` im Modus `preflight_only`
- Harness-Log ohne Host-Secrets

Zusaetzlich:

1. Alle sechs S1-Harness-Cases laufen deterministisch lokal und im Docker-Harness.
2. `latest` zeigt innerhalb jedes Case-Workspaces auf den letzten erfolgreichen Lauf dieses Cases oder ist eindeutig als Symlink-/Pointer-Mechanismus dokumentiert.
3. Ein fehlerhaftes Bundle wird nicht als teilweise erfolgreicher Workbench-Setup gemeldet.
4. Ein fehlerhafter Survey-Handoff startet keinen Folgepfad.
5. Der Spike nutzt keine Dateien aus `_legacy/v1-node-prototype` zur Laufzeit.
6. Alle erzeugten Artefakte liegen unter dem expliziten Workspace und nicht verstreut im Repo oder Host-Home.
7. Die V2-Slice-Plan-Coverage kann nach erfolgreicher Umsetzung fuer S1 aktualisiert werden.

## 12. Verification Commands

### 12.1 Execution Context

- Working directory: `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`
- Shell: `zsh` auf macOS fuer lokale Entwicklung.
- Runtime target: .NET 10 SDK.
- SDK-Auswahl: Wegen des vorhandenen Vault-Parent-`global.json` duerfen `dotnet`-Commands nicht aus dem Repo-Root laufen, wenn sie .NET 10 nachweisen sollen. Sie laufen aus einem SDK-neutralen Arbeitsverzeichnis ausserhalb des Vaults und referenzieren die Solution per absolutem Pfad.
- Docker ist fuer S1 verpflichtend als minimaler Harness-Container. Docker Compose, Multi-Service-Orchestrierung und vollstaendige S7-Pfadabdeckung bleiben out of scope.
- Scope-Guard-Baseline: aktueller Git-Working-Tree nach dem S1-Implementierungsdiff. Die Verification darf nicht verlangen, dass der Branch historisch kurzlebig ist.
- Runtime-Readiness: Wenn `FreeEntry.SurveyStub` als HTTP-Service gestartet wird, muss die Harness per Poll/Retry auf einen Health-Endpunkt warten, bevor Handoff-Assertions laufen.
- Anti-Loop-Regel: Diese Commands verifizieren Implementierung und Artefakte. Es werden keine zusaetzlichen Commands eingefuehrt, die nur die Verification selbst verifizieren.

### 12.2 Risk-Based Preflight

Diese Commands sind vor dem Scaffolding auszufuehren:

```bash
cd /tmp
dotnet --version
dotnet --list-sdks | rg '^10\.'
docker version
```

Erfolg:

- `dotnet --version` zeigt eine 10.0.x SDK-Version.
- `dotnet --list-sdks` enthaelt mindestens ein 10.x SDK.
- `docker version` endet mit Exit `0` und bestaetigt, dass der Docker-Daemon erreichbar ist.

Nach dem Scaffolding ist dieser Preflight zu ergaenzen:

```bash
cd /tmp
dotnet restore /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln
```

Erfolg:

- `dotnet restore` endet mit Exit `0`.
- Der unmittelbar vorher aus `/tmp` gepruefte SDK-Kontext bleibt .NET 10.
- Restore zeigt keinen `NETSDK1045`- oder vergleichbaren Fehler, der auf ein zu altes SDK hindeutet.

### 12.3 Gate Verification

Nach Implementierung muessen diese Commands laufen:

```bash
cd /tmp
dotnet restore /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln
dotnet build /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln --configuration Release --no-restore
dotnet test /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln --configuration Release --no-build
/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/scripts/run-harness.sh --case all --workspace /Users/dh/Documents/DanielsVault/ki-fuer-kmu/.safe-test/s1
docker build -f /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/tests/harness/Dockerfile -t free-entry-v2-s1-harness /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2
docker run --rm \
  -e S1_TEST_SECRET_VALUE=S1_TEST_SECRET_VALUE \
  -v /Users/dh/Documents/DanielsVault/ki-fuer-kmu/.safe-test/s1-docker:/work/out \
  free-entry-v2-s1-harness \
  /app/scripts/run-harness.sh --case all --workspace /work/out
```

Erfolg:

- Restore, Build und Tests enden mit Exit `0`.
- Die lokale Harness und die Docker-Harness fuehren alle Cases aus Abschnitt 10 aus.
- Die lokale Harness erzeugt einen maschinenlesbaren Ergebnisbericht, zum Beispiel `.safe-test/s1/harness-summary.json`.
- Die Docker-Harness erzeugt einen eigenen maschinenlesbaren Ergebnisbericht, zum Beispiel `.safe-test/s1-docker/harness-summary.json`.
- Der Ergebnisbericht enthaelt pro Case `ran`, `exit_code`, `expected_exit_code`, `passed` und Artefaktpfade.
- Jeder Case nutzt einen eigenen Unterworkspace unter `.safe-test/s1/<case-id>/`; `latest` wird nur innerhalb dieses Case-Workspaces bewertet.
- Der Docker-Lauf nutzt eigene Unterworkspaces unter `.safe-test/s1-docker/<case-id>/` und besteht dieselben Case-, Artefakt- und Secret-Leak-Assertions wie der lokale Harness.
- Secret-Leak-Assertions pruefen mindestens `logs/`, `run-manifest.json`, `survey/import-manifest.json`, `survey/answers.json`, `agent/agent-config.json` und alle Harness-Summaries.

Falls die konkrete Implementierung die Script-Schnittstelle anders benennt, muss der Scope Contract vor Umsetzung die alternative Kommandoform festhalten und diese Spec entsprechend aktualisieren.

## 13. Definition of Ready fuer Umsetzung

S1 ist bereit fuer `spec-change-delivery`, wenn:

1. diese Spec keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker enthaelt,
2. der Scope Contract die Ziel-Projektstruktur aus Abschnitt 7 bestaetigt oder begruendet anpasst,
3. die sechs Harness-Cases aus Abschnitt 10 als Mindestumfang erhalten bleiben,
4. der Implementierungsmodus `direct` oder OpenSpec explizit gewaehlt ist,
5. die Verification Commands aus Abschnitt 12 im Scope Contract uebernommen oder bewusst angepasst werden.

## 14. Definition of Done

S1 ist done, wenn:

1. alle Gate Verification Commands aus Abschnitt 12.3 erfolgreich ausgefuehrt wurden,
2. alle Akzeptanzkriterien aus Abschnitt 11 mit Artefaktpfaden belegt sind,
3. keine Secrets in Logs, Manifesten oder Reports gefunden wurden,
4. der Slice-Plan `v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md` fuer S1-Coverage aktualisiert wurde,
5. diese Spec durch den Delivery-Run auf `🔵 Implemented` gesetzt wurde,
6. offene Erkenntnisse fuer S2-S7 als Follow-up notiert wurden, ohne sie in S1 mitzuerledigen.

## 15. Risiken und Guardrails

| Risiko | Guardrail |
|---|---|
| Spike wird zur halben Produktimplementierung. | S1 bleibt bei Stubs fuer Survey-Inhalte, Provider, ROI/RAG, Bundle-Signatur und UI. |
| Legacy-Code schleicht sich als V2-Basis ein. | `_legacy/v1-node-prototype` darf nicht zur Laufzeit referenziert werden. |
| Harness prueft nur Container-/Prozessstart. | Harness muss Artefakte, Manifestfelder, Exit-Codes und Secret-Leaks pruefen. |
| Docker-Scope wird zu S7. | S1 baut nur einen nackten Harness-Container fuer die sechs S1-Cases; Compose, echte Provider, RAG/ROI, Managed-Updates und volle Kontrollflussmatrix bleiben S7 bzw. spaetere Slices. |
| Vault-Parent-`global.json` beeinflusst Builds. | Verification-Commands laufen aus `/tmp` und referenzieren die Solution per absolutem Pfad; S1 legt kein neues `v2/global.json` als Pflichtartefakt an. |
| `provider_ready=true` wird mit echtem Provider verwechselt. | S1 markiert Provider nur als Stub und startet keinen echten ROI/RAG-Pfad. |
| Halb fertige Workbench wird als Erfolg gemeldet. | Bundle-/Handoff-Blocker verhindern Erfolgsmeldung und setzen klare Statuswerte. |
| Host-Secrets laufen in Testartefakte. | Harness isoliert Workspace und nutzt explizite Test-Secrets fuer Redaction-Assertions. |

## 16. Follow-up nach S1

Nach erfolgreichem S1-Spike werden diese naechsten Specs konkretisiert oder umgesetzt:

- S2: Survey-Delivery-Service und Answer-Handoff als echter API-/Retention-Vertrag.
- S3: Content-Bundle, Manifest, Signatur, Installations- und Konfliktpolitik.
- S4: Provider-Aktivierungsguides und echte Readiness-Tests.
- S5: Survey-v2-Inhalte und Routing.
- S6: ROI/RAG-Runtime und Report.
- S7: Vollstaendige Docker-/Safe-Harness fuer alle fuehrenden Kontrollfluss-Pfade.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S1 Child Spec aus Master-Spec, Slice Plan und ADRs abgeleitet. |
| 2026-05-05 | Codex | S1 Spec zu einer umsetzungsreifen Spike-Spec mit Projektstruktur, Artefaktvertrag, Harness-Cases und Verification Commands ausgearbeitet. |
| 2026-05-05 | User/Codex | Runtime-Ziel von .NET 8 auf .NET 10 aktualisiert, da .NET 10 lokal installiert ist und fuer die neue V2-Codebasis genutzt werden soll. |
| 2026-05-05 | User/Codex | Review-Findings autonom aufgeloest: `global.json`-Pflicht entfernt, .NET-10-Verification neutralisiert, Agent-Config-Felder vervollstaendigt und Harness-Workspaces pro Case isoliert. |
| 2026-05-05 | User/Codex | Docker-Harness als verpflichtenden S1-Minimalscope nachgezogen: nackter Containerlauf mit injizierten YAML/JSON-Fixtures und denselben Artefakt-/Secret-Assertions wie lokal. |
| 2026-05-05 | User/Codex | Review-Findings autonom aufgeloest: Scope Contract auf `direct` festgelegt, Dummy-Bundle-Fixture-Vertrag und SurveyStub-Handoff-Vertrag fuer S1 gepinnt. |
| 2026-05-05 | User/Codex | Delivery-Status auf Plan gesetzt und Implementierungsmodus gemaess Nutzerauftrag auf OpenSpec-Change `free-entry-v2-s1-vertical-spike` umgestellt. |
| 2026-05-05 | User/Codex | S1 implementiert: .NET-10-Solution, Core Runner, SurveyStub, Harness-Cases, Docker-Harness und OpenSpec-Evidence mit gruenen Gate-Commands geliefert. |
| 2026-05-05 | User/Codex | Change akzeptiert und geschlossen: OpenSpec-Change als `2026-05-05-free-entry-v2-s1-vertical-spike` archiviert, Verifikation erneut gruen replayed und Spec auf Accepted gesetzt. |

SessionId: codex-free-entry-v2-s1-architecture-spike-2026-05-05
