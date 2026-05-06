**Date:** 2026-05-05  
**Status:** 🟡 Spec  
**Scope:** Signiertes Free-Entry-Bundle, Bundle-Manifest, Readiness, lokaler Vault-Import und spaeterer Managed-AI-Updatekanal.

---

## 1. Ziel

S3 baut den v2-Default fuer Content-Zugang: kein GitHub-Zwang fuer Einsteiger, sondern signierte Bundles mit spaeterem Managed-AI-Kanal.

## 2. In Scope

- Bundle-Manifestformat fuer `free-entry`, `paid-pilot`, `managed-ai` und Test-/Demo-Inhalte.
- Hash, Signatur, erwartete Dateien und Kompatibilitaet.
- Installationsziele im lokalen Vault/Workbench.
- Konfliktpolitik fuer lokale Kundenaenderungen.
- Managed-AI-Updatekanal als spaeterer Freigabepfad.
- Optionaler Git/GitHub-Pfad nur als technischer Spaeterpfad.

## 3. Out of Scope

- Provider-API-Keys oder Repo-Tokens im Manifest.
- Oeffentliche Veroeffentlichung geschuetzter IP.
- Vollstaendiger Managed-Service-Betrieb.

## 4. Master-Spec-Abdeckung

| Master-Spec-Bereich | S3-Abdeckung | Grenze |
|---|---|---|
| V2-FR-030 Vault und Arbeitsraum | Teilabdeckung: Vault-/Workbench-Content-Import, Installationsmanifest, Content-Versionsprotokoll und Plugin-Baseline-Protokoll. | Lokale Provider-Konfiguration, Ergebnisordner fuer Survey/Dokumente/RAG/ROI/Report und lokaler Agent bleiben bei S4/S6/S7. |
| V2-FR-031 Content-Bundle und optionale Repo-Quellen | Vollabdeckung fuer Bundle-Manifest, Content-Sets, Installation, optionalen oeffentlichen Git-Testpfad und spaetere technische Repo-Pfade. | Produktive private Repo-Credentials bleiben out of scope. |
| V2-FR-031a Bundle-Manifest und Readiness | Vollabdeckung fuer Hash, Signatur, erwartete Dateien, Kompatibilitaet, Entitlement, Channel und Blockerstatus. | Produktive Signatur-Infrastruktur kann durch deterministische Harness-Signaturen simuliert werden. |
| V2-FR-031b Managed-AI-Kanal und Git/GitHub-Spaeterpfad | Vollabdeckung fuer Update-Metadaten, Tenant-/Entitlement-Pruefung, Konfliktstatus und Git/GitHub als optionalen Spaeterpfad. | Vollstaendiger Managed-Service-Betrieb bleibt out of scope. |
| V2-FR-032 Obsidian-Plugin-Baseline | Vollabdeckung fuer Baseline-Manifest, Pflicht-/Empfohlen-/Optional-Status, `latest_approved`, Zweck, Trust-Entscheidung, Fallback und Vault-Setup-Protokoll. | Stille Plugin-Installation bleibt verboten. |

## 5. Fachlicher Vertrag

### 5.1 Bundle-Manifest

S3 konkretisiert das produktive Bundle-Manifest aus der Master-Spec. Das Manifest muss Free-Entry-, Paid-Pilot-, Managed-AI- und oeffentliche Test-/Demo-Inhalte beschreiben koennen, ohne mehrere konkurrierende Content-Zugangsmodelle einzufuehren.

Ein S3-Manifest enthaelt mindestens:

- `bundle_id`
- `version`
- `channel`: `free-entry`, `paid-pilot`, `managed-ai` oder `public-demo`
- `created_at_utc`
- `expires_at_utc` oder `no_expiry`
- `content_sets`: freigegebene Inhaltsgruppen mit stabiler `content_set_id`, `category`, `channel_scope`, `required_for_channel` und `items`
- `sha256`: Hash des kanonischen Bundle-Inhalts
- `signature`: Signatur ueber Manifest und Inhalt
- `signature_mode`: reale Signaturpruefung oder fuer Harness-Fixtures ein expliziter deterministischer Stub
- `tenant_ref`: pseudonyme oder technische Mandantenreferenz, kein Klarname und kein Secret; bei `tenant_scope=public` optional
- `tenant_scope`: `public`, `registered_free_entry`, `paid_pilot` oder `managed_ai_customer`
- `entitlement_ref`, ausser wenn `entitlement_status=not_required`
- `entitlement_type`: `public_demo`, `free_entry`, `paid_pilot`, `managed_ai`
- `entitlement_status`: `not_required`, `valid`, `missing`, `expired`, `tenant_mismatch` oder `channel_not_allowed`
- `entitlement_expires_at_utc` oder `no_expiry`
- `allowed_channels`: erlaubte Zielkanaele fuer diese Freigabe
- `compatibility`: mindestens Starter-/Spec-Version und erlaubte Zielkanaele
- `expected_files`: Pfad, Hash, Installationsziel, `content_set_id`, `content_item_id`, `source_kind`, `source_version`, `revision`, optional `previous_revision` und optional `migration_id` pro erwarteter Datei
- `install_targets`: erlaubte Vault-/Workbench-Zielbereiche
- `conflict_policy`: `fail_on_local_change`, `preserve_local_change`, `manual_review_required` oder ein dokumentierter Harness-Stub
- `managed_update`: Metadaten fuer spaetere Updatefaehigkeit, falls der Channel `managed-ai` ist
- `plugin_baseline`: freigegebene Obsidian-Plugin-Baseline nach Abschnitt 5.5

Ein `content_sets[*].items[*]`-Eintrag enthaelt mindestens:

- `content_item_id`: stabile logische ID, die ueber Datei-Umbenennungen hinweg erhalten bleibt
- `content_set_id`
- `source_kind`: `shared_ai_doc`, `skill`, `subagent`, `context_package`, `provider_guide`, `helper_content`, `plugin_baseline`, `migration_note`, `public_demo` oder `test_fixture`
- `source_version`
- `revision`
- optional `previous_revision`
- optional `migration_id`
- `path`
- `install_target`
- `sha256`

Ein gueltiges Free-Entry-Bundle muss mindestens diese Content-Sets enthalten und im Harness mit echten erwarteten Dateien belegen:

| Content-Set | Mindestinhalt |
|---|---|
| `shared-ai-docs` | Einstieg, Arbeitsweise und Nutzungshinweise fuer die lokale KI-Arbeitsumgebung. |
| `skills` | Mindestens ein freigegebener Skill fuer ROI-/Spec-/Kontextarbeit. |
| `subagents` | Mindestens ein freigegebener Agent-/Subagent-Kontext. |
| `context-packages` | Mindestens ein Kontextpaket fuer die Free-Entry-Arbeitsbasis. |
| `provider-guides` | Mindestens ein gepflegter Provider-Guide oder Assisted-Setup-Guide als lokaler Content. |
| `helper-content` | Hilfsinhalte fuer Vault-Navigation, naechste Schritte oder Reportvorbereitung. |
| `plugin-baseline` | Plugin-Baseline-Protokoll nach Abschnitt 5.5. |

Das Manifest darf keine produktiven Secrets, Provider-API-Keys, Zahlungsdaten oder eingebetteten Repo-Tokens enthalten. Secret-Referenzen duerfen nur als nicht aufloesbare Referenzen wie `keychain_ref`, `credential_manager_ref` oder `entitlement_ref` erscheinen.

### 5.1.1 Kanonische Manifest-Beispiele

Diese Beispiele sind der Mindestvertrag fuer Fixture- und Implementierungsdesign. Vollstaendige Dateien duerfen mehr Felder enthalten, aber die Channel-spezifischen Pflichtfelder und Content-Sets duerfen nicht fehlen.

Free Entry:

```yaml
bundle_id: free-entry-starter
version: 3.0.0
channel: free-entry
tenant_ref: free-entry-registration-001
tenant_scope: registered_free_entry
entitlement_ref: entitlement-free-entry-001
entitlement_type: free_entry
entitlement_status: valid
allowed_channels: [free-entry]
content_sets:
  - content_set_id: shared-ai-docs
    category: shared_ai_doc
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: shared-ai-docs.start-here
        source_kind: shared_ai_doc
        source_version: 3.0.0
        revision: 1
        path: content/shared-ai-docs/start-here.md
        install_target: vault/Shared AI Docs/start-here.md
        sha256: "<sha256>"
  - content_set_id: skills
    category: skill
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: skills.roi-prep
        source_kind: skill
        source_version: 3.0.0
        revision: 1
        path: content/skills/roi-prep/SKILL.md
        install_target: vault/Skills/roi-prep/SKILL.md
        sha256: "<sha256>"
  - content_set_id: subagents
    category: subagent
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: subagents.free-entry-coach
        source_kind: subagent
        source_version: 3.0.0
        revision: 1
        path: content/subagents/free-entry-coach.md
        install_target: vault/Subagents/free-entry-coach.md
        sha256: "<sha256>"
  - content_set_id: context-packages
    category: context_package
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: context.kmu-start
        source_kind: context_package
        source_version: 3.0.0
        revision: 1
        path: content/context/kmu-start.md
        install_target: vault/Context/kmu-start.md
        sha256: "<sha256>"
  - content_set_id: provider-guides
    category: provider_guide
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: provider-guides.assisted-setup
        source_kind: provider_guide
        source_version: 3.0.0
        revision: 1
        path: provider-guides/assisted-setup.v1.yaml
        install_target: vault/Provider Guides/assisted-setup.v1.yaml
        sha256: "<sha256>"
  - content_set_id: helper-content
    category: helper_content
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: helper.next-steps
        source_kind: helper_content
        source_version: 3.0.0
        revision: 1
        path: content/helper/next-steps.md
        install_target: vault/Start/next-steps.md
        sha256: "<sha256>"
  - content_set_id: plugin-baseline
    category: plugin_baseline
    channel_scope: [free-entry]
    required_for_channel: true
    items:
      - content_item_id: plugin-baseline.free-entry
        source_kind: plugin_baseline
        source_version: 3.0.0
        revision: 1
        path: content/plugin-baseline/obsidian-plugin-baseline.v1.yaml
        install_target: vault/.setup/obsidian-plugin-baseline.v1.yaml
        sha256: "<sha256>"
```

Paid Pilot:

```yaml
bundle_id: paid-pilot-starter
version: 3.0.0
channel: paid-pilot
tenant_ref: paid-pilot-tenant-001
tenant_scope: paid_pilot
entitlement_ref: entitlement-paid-pilot-001
entitlement_type: paid_pilot
entitlement_status: valid
allowed_channels: [free-entry, paid-pilot]
content_sets:
  - content_set_id: shared-ai-docs
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: shared-ai-docs.start-here, source_kind: shared_ai_doc, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: skills
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: skills.pilot-kickoff, source_kind: skill, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: subagents
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: subagents.pilot-coach, source_kind: subagent, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: context-packages
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: context.pilot-start, source_kind: context_package, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: provider-guides
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: provider-guides.managed-gateway-paid-pilot, source_kind: provider_guide, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: helper-content
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: helper.pilot-next-steps, source_kind: helper_content, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: plugin-baseline
    channel_scope: [free-entry, paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: plugin-baseline.free-entry, source_kind: plugin_baseline, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
  - content_set_id: pilot-migration-notes
    channel_scope: [paid-pilot]
    required_for_channel: true
    items: [{ content_item_id: migration-notes.pilot-start, source_kind: migration_note, source_version: 3.0.0, revision: 1, sha256: "<sha256>" }]
```

Managed AI:

```yaml
bundle_id: managed-ai-update
version: 3.1.0
channel: managed-ai
tenant_ref: tenant-test-001
tenant_scope: managed_ai_customer
entitlement_ref: entitlement-managed-ai-001
entitlement_type: managed_ai
entitlement_status: valid
entitlement_expires_at_utc: 2026-12-31T23:59:59Z
allowed_channels: [managed-ai]
managed_update:
  update_id: managed-ai-2026-05
  update_policy: manual_approval_required
  conflict_policy: manual_review_required
content_sets:
  - content_set_id: skills
    channel_scope: [managed-ai]
    required_for_channel: true
    items: [{ content_item_id: skills.roi-prep, source_kind: skill, source_version: 3.1.0, revision: 2, previous_revision: 1, migration_id: managed-ai-2026-05, sha256: "<sha256>" }]
  - content_set_id: subagents
    channel_scope: [managed-ai]
    required_for_channel: true
    items: [{ content_item_id: subagents.free-entry-coach, source_kind: subagent, source_version: 3.1.0, revision: 2, previous_revision: 1, migration_id: managed-ai-2026-05, sha256: "<sha256>" }]
  - content_set_id: context-packages
    channel_scope: [managed-ai]
    required_for_channel: true
    items: [{ content_item_id: context.kmu-start, source_kind: context_package, source_version: 3.1.0, revision: 2, previous_revision: 1, migration_id: managed-ai-2026-05, sha256: "<sha256>" }]
  - content_set_id: provider-guides
    channel_scope: [managed-ai]
    required_for_channel: true
    items: [{ content_item_id: provider-guides.openai-api, source_kind: provider_guide, source_version: 3.1.0, revision: 2, previous_revision: 1, migration_id: managed-ai-2026-05, sha256: "<sha256>" }]
  - content_set_id: migration-notes
    channel_scope: [managed-ai]
    required_for_channel: true
    items: [{ content_item_id: migration-notes.managed-ai-2026-05, source_kind: migration_note, source_version: 3.1.0, revision: 1, migration_id: managed-ai-2026-05, sha256: "<sha256>" }]
  - content_set_id: plugin-baseline
    channel_scope: [managed-ai]
    required_for_channel: true
    items: [{ content_item_id: plugin-baseline.free-entry, source_kind: plugin_baseline, source_version: 3.1.0, revision: 2, previous_revision: 1, migration_id: managed-ai-2026-05, sha256: "<sha256>" }]
```

Public Demo:

```yaml
bundle_id: public-demo-content
version: 3.0.0
channel: public-demo
tenant_scope: public
entitlement_type: public_demo
entitlement_status: not_required
allowed_channels: [public-demo]
content_sets:
  - content_set_id: public-demo
    category: public_demo
    channel_scope: [public-demo]
    required_for_channel: true
    items:
      - content_item_id: public-demo.ai-test-repo
        source_kind: public_demo
        source_version: 3.0.0
        revision: 1
        path: content/public-demo/ai-test-repo.md
        install_target: vault/Public Demo/ai-test-repo.md
        sha256: "<sha256>"
```

### 5.2 Bundle-Readiness und Installation

Die Anwendung muss Hash, Signatur, erwartete Dateien, Channel, Entitlement/Freigabe, Kompatibilitaet und Installationsziele pruefen, bevor Inhalte in Vault oder Workbench uebernommen werden.

Ein gueltiges Free-Entry-Bundle muss:

- `bundle_readiness_status=ready` setzen.
- `workbench_status=ready` oder einen gleichwertigen vorbereiteten Status setzen.
- installierte Dateien mit Quelle, Ziel, Hash und Content-Set in einem Installationsmanifest dokumentieren.
- lokale Kundenaenderungen gemaess `conflict_policy` behandeln.
- keine Dateien ausserhalb des explizit uebergebenen Workspaces/Vault-Ziels schreiben.

Ein ungueltiges Bundle muss:

- mit Exit `30` oder `bundle_readiness_status=blocked_invalid_bundle` blockieren.
- `workbench_status=blocked` setzen.
- keinen teilweise installierten Vault als Erfolg melden.
- den Fehler kundenverstaendlich und secret-redacted dokumentieren.

### 5.3 Managed-AI-Updatekanal

Der Managed-AI-Kanal nutzt denselben Bundle-Mechanismus als freigegebenen Updatepfad. Er darf erst aktiv werden, wenn Mandant/Freigabe, Channel, Bundle-Kompatibilitaet und Signatur erfolgreich geprueft wurden.

Ein Managed-AI-Update muss:

- neue oder aktualisierte Skills, Subagents, Guides, Kontexte und Migrationshinweise als signierte Content-Sets beschreiben.
- `tenant_ref`, `tenant_scope`, `entitlement_type`, `entitlement_status`, `entitlement_expires_at_utc` oder `no_expiry` und `allowed_channels` pruefen.
- bei falschem Mandanten, fehlender Freigabe, abgelaufener Freigabe oder nicht erlaubtem Channel blockieren.
- lokale Kundenaenderungen erkennen und Konflikte sichtbar machen.
- `update_status=ready`, `blocked_entitlement_missing`, `blocked_entitlement_expired`, `blocked_tenant_mismatch`, `blocked_channel_not_allowed`, `blocked_incompatible_bundle`, `blocked_invalid_signature` oder `conflict_manual_review_required` dokumentieren.
- Update-Regeln fuer manuelle, freigegebene oder managed-only Updates im Manifest oder im Installationsmanifest nachvollziehbar machen.

Lokale Kundenaenderungen duerfen nicht still ueberschrieben werden. Bei Konflikt muss der Lauf blockieren oder einen manuellen Review-Status erzeugen; ein Auto-Merge ist fuer S3 kein Default.

### 5.4 Optionaler Git/GitHub-Spaeterpfad

Git/GitHub bleibt kein Free-Entry-Default. Der optionale technische Spaeterpfad darf nur ueber ein eigenes Repo-/Credential-Modell aktiviert werden und muss in S3 testbar bleiben, ohne echte Tokens zu verwenden.

Der oeffentliche Testpfad nutzt `https://github.com/paradox123/ai-test-repo.git` als Harness-Fixture fuer Repo-Mechanik und erwartete Artefakte. Private oder geschuetzte Repo-Faelle muessen mit Fake-/Test-Secrets laufen und bei fehlender Freigabe mit Exit `30` oder `40` blockieren, ohne Token-Leak.

### 5.5 Obsidian-Plugin-Baseline

Community-Plugins sind ausfuehrbarer Code und duerfen nicht still installiert werden. S3 liefert deshalb nur eine freigegebene Plugin-Baseline und ein Vault-Setup-Protokoll. Die Anwendung darf daraus Empfehlungen, Warnungen und nachvollziehbare Setup-Schritte erzeugen; eine Installation braucht explizite Nutzerbestaetigung oder Assisted Setup.

`plugin_baseline` enthaelt mindestens:

- `baseline_id`
- `baseline_version`
- `status_groups`: `required`, `recommended`, `optional`
- `plugins`
- `default_install_mode`: `recommend_only` oder `explicit_user_approval_required`
- `vault_setup_log_target`

Jeder Plugin-Eintrag enthaelt mindestens:

- `plugin_id`
- `baseline_status`: `required`, `recommended` oder `optional`
- `latest_approved`
- `purpose`
- `trust_decision`
- `fallback`
- `install_mode`
- `installed_version`: zur Laufzeit im Vault-Setup-Protokoll, nicht zwingend im Bundle-Manifest

Pflicht-Baseline:

| Status | Plugin | Vertrag |
|---|---|---|
| Pflicht | `dataview` | `latest_approved`, Zweck, Trust-Entscheidung, Fallback und spaeter installierte Version werden dokumentiert. |
| Empfohlen | `metadata-menu`, `templater-obsidian`, `obsidian-tasks-plugin`, `obsidian-git`, `obsidian-linter` | Werden empfohlen oder als nicht aktiviert protokolliert; keine stille Installation. |
| Optional | `obsidian-kanban`, `obsidian-excalidraw-plugin`, `obsidian-charts`, `table-editor-obsidian` | Nur sichtbar als optionale Erweiterung mit Zweck und Fallback. |

Das Vault-Setup-Protokoll dokumentiert mindestens `baseline_id`, `baseline_version`, jeden `plugin_id`, `baseline_status`, `latest_approved`, `install_mode`, `installed_version` oder `not_installed`, `trust_decision`, `fallback` und `user_action_required`.

### 5.6 Security und Redaction

S3 muss dieselben Secret-Leak-Assertions lokal und im Docker-Harness bestehen. Die Assertions pruefen mindestens:

- Harness-Logs
- `run-manifest.json`
- Bundle-Manifest und Installationsmanifest
- Managed-AI-Update-Metadaten
- Vault-/Workbench-Zieldateien
- Reports
- Harness-Summaries

Die Harness injiziert fuer S3 mindestens `S3_TEST_SECRET_VALUE`, `S3_TEST_ENTITLEMENT_TOKEN` und `S3_TEST_GIT_TOKEN` als verbotene Testwerte. Diese Werte duerfen in keinem erzeugten Artefakt, Log, Report oder Summary erscheinen.

## 6. Harness- und Verification-Cases

S3 muss die bestehende S1/S2-Harness erweitern, nicht ersetzen. Die S3-Cases muessen lokal und im Docker-Container laufen. Das Docker-Gate ist verpflichtend und muss dieselben Bundle-, Artefakt-, Konflikt- und Secret-Leak-Assertions ausfuehren wie der lokale Harness-Lauf.

### 6.1 Harness-Eingabevertrag

Jeder S3-Case enthaelt mindestens:

- `bundle.fixture_id` oder `bundle.manifest_override`
- `bundle.channel`
- `bundle.expected_sha256` oder ein definiertes Fehlerprofil
- `bundle.signature_mode`
- `bundle.expected_files`
- `bundle.install_targets`
- `bundle.conflict_policy`
- `bundle.required_content_sets`
- `bundle.expected_content_items`: mit `content_item_id`, `content_set_id`, `source_kind`, `source_version`, `revision`, optional `previous_revision` und optional `migration_id`
- `managed_ai`: Update-Metadaten oder `not_applicable`
- `entitlement`: erwarteter Mandant, Freigabe, erlaubte Channels und Fehlerprofil
- `plugin_baseline`: erwartete Baseline, Plugin-IDs, Statusgruppen und Vault-Setup-Protokollfelder
- `repo_path`: optionaler Git-Testpfad oder `not_applicable`
- `preexisting_workspace_files`: lokale Kundenaenderungen fuer Konfliktfaelle
- `expected_exit_code`
- `expected_manifest_fields`
- `expected_artifacts`
- `forbidden_values`: Test-Secrets, Entitlement-Tokens, Git-Tokens und andere Werte, die nie in Artefakten/Logs/Summaries erscheinen duerfen

Die Harness darf einen S3-Case nicht dadurch bestehen lassen, dass sie die erwarteten Ergebnisartefakte direkt in den Workspace legt. Sie muss den normalen Bundle-Readiness-, Installations- oder Updatepfad ausfuehren und danach gegen die erwarteten Artefakte pruefen.

### 6.2 Pflicht-Cases

Mindestens diese Cases muessen lokal und im Docker-Gate laufen:

| Case | Zweck | Erwartung |
|---|---|---|
| `s3-001-valid-free-entry-bundle.yaml` | Gueltiges Free-Entry-Bundle wird geprueft und installiert. | Exit `0`, `bundle_readiness_status=ready`, erwartete Dateien im Vault, Installationsmanifest mit Hashes. |
| `s3-002-invalid-signature-blocks.yaml` | Signatur oder Signaturmodus ist ungueltig. | Exit `30`, `bundle_readiness_status=blocked_invalid_bundle`, kein erfolgreicher Workbench-Status. |
| `s3-003-missing-expected-file-blocks.yaml` | Erwartete Datei fehlt oder Hash passt nicht. | Exit `30`, `bundle_readiness_status=blocked_missing_expected_file`, keine Erfolgsmeldung. |
| `s3-004-managed-ai-update-metadata.yaml` | Freigegebener Managed-AI-Updatekanal wird erkannt. | Exit `0`, `update_status=ready`, Update-Metadaten, Channel und Kompatibilitaet dokumentiert. |
| `s3-005-managed-ai-local-conflict.yaml` | Lokale Kundenaenderung kollidiert mit Update. | Exit `30`, `update_status=conflict_manual_review_required`, kein stilles Ueberschreiben. |
| `s3-006-public-git-test-path.yaml` | Optionaler oeffentlicher Git-Testpfad bleibt technischer Spaeterpfad. | Exit `0`, oeffentliches Testrepo im erwarteten Zielpfad, Git nicht als Free-Entry-Default markiert. |
| `s3-007-git-auth-secret-redaction.yaml` | Geschuetzter Git-Pfad nutzt nur Fake-/Test-Secret und blockiert ohne Leak. | Exit `30` oder `40`, kein Token in Logs, Manifesten, Reports oder Summaries. |
| `s3-008-secret-redaction.yaml` | Bundle-, Entitlement- und Git-Test-Secrets erscheinen nirgends. | Alle verbotenen Werte fehlen in Logs, Manifesten, Vault-Zielen, Reports und Harness-Summaries. |
| `s3-009-managed-ai-tenant-mismatch-blocks.yaml` | Signiertes Managed-AI-Update gehoert zu falschem Mandanten. | Exit `30`, `update_status=blocked_tenant_mismatch`, keine Update-Installation. |
| `s3-010-managed-ai-entitlement-missing-blocks.yaml` | Managed-AI-Freigabe fehlt, ist abgelaufen oder erlaubt den Channel nicht. | Exit `30`, passender `blocked_entitlement_*`- oder `blocked_channel_not_allowed`-Status, keine Update-Installation. |
| `s3-011-plugin-baseline-protocol.yaml` | Plugin-Baseline wird als freigegebene Baseline protokolliert. | Exit `0`, Vault-Setup-Protokoll enthaelt `dataview`, empfohlene/optionale Plugin-IDs, `latest_approved`, Trust-Entscheidung, Fallback und keine stille Installation. |
| `s3-012-content-item-lineage.yaml` | Content-Items bleiben ueber Updates stabil referenzierbar. | Exit `0`, Installationsmanifest enthaelt pro Datei `content_item_id`, `content_set_id`, `source_kind`, `source_version`, `revision` und bei Updates `previous_revision` oder `migration_id`. |

Ein S3-Gate darf die Pflicht-Cases nicht als Erfolg werten, wenn sie nur geskippt wurden. `not_applicable` ist nur als Feldwert fuer Case-Dimensionen erlaubt, die fuer diesen konkret gelaufenen Case irrelevant sind; es darf nie einen S3-Pflicht-Case, den Docker-Lauf oder die Assertions ersetzen.

## 7. Verification Commands

Execution Context:

- Working directory: `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`.
- Shell: `zsh` auf macOS fuer lokale Entwicklung.
- Runtime target: .NET 10 SDK.
- SDK-Auswahl: Wie in S1/S2 laufen `dotnet`-Commands aus `/tmp`, damit der Vault-Parent-`global.json` die SDK-Auswahl nicht verfaelscht.
- Docker-Gate: Der vorhandene Harness-Container unter `v2/tests/harness/Dockerfile` ist verpflichtend. S3 darf nicht nur lokal, nur mit Unit Tests oder nur durch statische Dokumentpruefung verifiziert werden.
- Scope-Guard-Baseline: aktueller Git-Working-Tree vor S3-Implementierungsbeginn; vorhandene S1/S2-Artefakte und unrelatierte lokale Aenderungen werden nicht zurueckgesetzt.
- Runtime-Readiness: Falls S3 spaeter einen lokalen Service fuer Bundle-Download, Update-Metadaten oder Repo-Proxy startet, muss die Harness per Poll/Retry auf einen Health-Endpunkt oder ein deterministisches Bereitschaftssignal warten, bevor Assertions laufen.
- Anti-Loop-Regel: Die Commands verifizieren Implementierung und Artefakte, nicht rekursiv die Verification selbst.

Preflight:

```bash
cd /tmp
dotnet --version
dotnet --list-sdks | rg '^10\.'
docker version
dotnet restore /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln
```

Erfolg:

- `dotnet --version` zeigt eine 10.0.x SDK-Version.
- `dotnet --list-sdks` enthaelt mindestens ein 10.x SDK.
- `docker version` endet mit Exit `0` und bestaetigt, dass der Docker-Daemon erreichbar ist.
- `dotnet restore` endet mit Exit `0`.

Gate Verification:

```bash
cd /tmp
dotnet build /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln --configuration Release --no-restore
dotnet test /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/FreeEntryV2.sln --configuration Release --no-build
/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/scripts/run-harness.sh --case s3 --workspace /Users/dh/Documents/DanielsVault/ki-fuer-kmu/.safe-test/s3
docker build -f /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/tests/harness/Dockerfile -t free-entry-v2-s3-harness /Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2
docker run --rm \
  -e S3_TEST_SECRET_VALUE=S3_TEST_SECRET_VALUE \
  -e S3_TEST_ENTITLEMENT_TOKEN=S3_TEST_ENTITLEMENT_TOKEN \
  -e S3_TEST_GIT_TOKEN=S3_TEST_GIT_TOKEN \
  -v /Users/dh/Documents/DanielsVault/ki-fuer-kmu/.safe-test/s3-docker:/work/out \
  free-entry-v2-s3-harness \
  /app/scripts/run-harness.sh --case s3 --workspace /work/out
```

Erfolg:

- Build, Tests, lokale Harness und Docker-Harness enden mit Exit `0`.
- Lokale Harness und Docker-Harness erzeugen je eine `harness-summary.json`.
- Die lokale Harness fuehrt alle S3-Pflicht-Cases aus Abschnitt 6.2 aus und setzt pro Case `ran=true`, `passed=true`, `exit_code`, `expected_exit_code` und Artefaktpfade.
- Die Docker-Harness fuehrt alle S3-Pflicht-Cases aus Abschnitt 6.2 in eigenen Unterworkspaces unter `.safe-test/s3-docker/<case-id>/` aus.
- Der Docker-Lauf besteht dieselben Bundle-, Installations-, Konflikt-, Optional-Git- und Secret-Leak-Assertions wie der lokale Harness-Lauf.
- Kein Pflicht-Case wird als bestanden gewertet, wenn er nicht tatsaechlich gelaufen ist.
- Gueltige Bundle-Cases beweisen die erforderlichen Content-Sets und Content-Item-Lineage-Felder, nicht nur beliebige Dateien.
- Managed-AI-Cases beweisen Tenant-/Entitlement-/Channel-Blocker.
- Plugin-Baseline-Cases beweisen `latest_approved`, Zweck, Trust-Entscheidung, Fallback, Vault-Setup-Protokoll und keine stille Installation.
- Secret-Leak-Assertions pruefen mindestens `logs/`, `run-manifest.json`, Bundle-Manifest, Installationsmanifest, Managed-AI-Update-Metadaten, Vault-/Workbench-Zieldateien, Reports und alle Harness-Summaries.

Wenn S3 statt Single-Container-Harness eine Compose-/Multi-Service-Harness einfuehrt, muss diese Spec vor Umsetzung die konkrete Kommandoform ersetzen oder ergaenzen; ein Docker-Gate bleibt verpflichtend.

## 8. Akzeptanz

- Gueltiges Bundle wird nachvollziehbar installiert.
- Ungueltiges Bundle fuehrt zu Blockerstatus, nicht zu halb fertigem Erfolg.
- Gueltige Free-Entry-Bundles enthalten die in Abschnitt 5.1 geforderten Mindest-Content-Sets mit stabilen Content-Item-IDs und Version-Lineage.
- Managed-AI-Update-Metadaten werden erkannt und bei lokaler Kundenaenderung nicht still uebernommen.
- Managed-AI-Updates blockieren bei falschem Mandanten, fehlender/abgelaufener Freigabe oder nicht erlaubtem Channel.
- Plugin-Baseline wird mit `latest_approved`, Zweck, Trust-Entscheidung, Fallback und Vault-Setup-Protokoll dokumentiert; Plugins werden nicht still installiert.
- Secrets erscheinen nicht in Manifest, Logs, Vault-Zieldateien, Reports oder Harness-Summaries.
- Git/GitHub bleibt optional und nicht Einsteiger-Default.
- Alle S3-Pflicht-Cases laufen lokal und im Docker-Harness mit denselben erwarteten Artefakten, Exit-Codes und Secret-Leak-Assertions.

## 9. Definition of Ready fuer Umsetzung

S3 ist bereit fuer `spec-change-delivery`, wenn:

- Scope und Non-Goals in den Abschnitten 2 und 3 unveraendert gelten.
- Der fachliche Vertrag aus Abschnitt 5 als Scope Contract uebernommen oder bewusst angepasst wurde.
- Alle Harness-Pflicht-Cases aus Abschnitt 6.2 als Case-Dateien oder im Scope Contract konkretisiert sind.
- Die Verification Commands aus Abschnitt 7 im Scope Contract uebernommen oder vor Umsetzung bewusst angepasst wurden.
- Keine Umsetzung ohne Docker-Gate geplant ist.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | Codex | S3 Child Spec aus ADR-001 und Master-Spec abgeleitet. |
| 2026-05-06 | Codex | Review-Findings aufgeloest: S3-Harness-Cases, verpflichtendes lokales und Docker-Gate, Secret-Redaction-Scope und Managed-AI-Konfliktvertrag ergaenzt. |
| 2026-05-06 | Codex | Parent-Scope-Findings aufgeloest: Plugin-Baseline, Mindest-Content-Sets, Tenant-/Entitlement-Vertrag, Content-Item-Lineage und kanonische Manifest-Beispiele ergaenzt. |

SessionId: codex-free-entry-v2-s3-content-bundle-2026-05-05
