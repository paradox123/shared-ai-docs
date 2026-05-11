# DocWorkflow Agent Delivery Test Suite

Diese Testsuite prueft den shared-ai-docs Agent Delivery Workflow fuer Parent-/Child-Spec-Delivery. Sie ist absichtlich klein und contract-orientiert: sie soll Workflow-Gates reproduzierbar machen, ohne KI-fuer-KMU-Originaldateien oder Legacy-Specs zu migrieren.

## Struktur

| Pfad | Zweck |
|---|---|
| `testcases/tc1-parent-first-orchestration-child-hardening.md` | Testcase 1 als lesbarer Harness-Vertrag. |
| `testcases/tc2-single-child-delivery-next-handoff.md` | Testcase 2 als lesbarer Harness-Vertrag. |
| `l1/fixtures/` | Kleine synthetische DWT-S1-Fixtures fuer deterministische L1-Vertragschecks. |
| `l2/parent-first/fixtures/` | DWT-S2 Parent-first Output Bundles fuer positive, negative, blocked, style and telemetry checks. |
| `l2/parent-first/validators/` | Deterministic Node validator for DWT-S2 parent-first orchestration bundles. |
| `l2/single-child-closeout/fixtures/` | DWT-S3 Single-child Delivery/Closeout Output Bundles fuer current handoff, stale handoff, isolation, closeout, DWT-S5-block, blocked-agent and style/telemetry checks. |
| `l2/single-child-closeout/validators/` | Deterministic Node validator for DWT-S3 delivery kickoff, closeout sync and next-child gate bundles. |
| `l3/runtime-temp-repo/fixtures/` | DWT-S5 synthetic runtime repo plus positive, negative, blocked, closeout and reporting fixtures. |
| `l3/runtime-temp-repo/validators/` | Deterministic Node validator for DWT-S5 temp-repo materialization, runtime gates, blocked-runtime honesty and closeout sync. |
| `scripts/run-mock-e2e-checks.sh` | Fuehrt den mock-only Standard-E2E-Gate fuer grosse und kleine Agent-Delivery-Flows aus. |
| `scripts/run-contract-checks.sh` | Kompatibilitaetskommando; `all` delegiert mock-only auf den Standard-E2E-Gate, TC1/TC2 sind legacy und explicit-fixture-only. |
| `scripts/run-l1-contract-checks.sh` | Fuehrt DWT-S1 L1A-L1F gegen synthetische Fixtures aus und schreibt `evidence/l1-summary.json`. |
| `scripts/run-l2-parent-orchestration-checks.sh` | Fuehrt DWT-S2 L2A-L2F gegen Parent-first Output Bundles aus und schreibt `evidence/dwt-s2-l2-summary.json`. |
| `scripts/run-l2-single-child-closeout-checks.sh` | Fuehrt DWT-S3 L2A-L2F gegen Single-child Delivery/Closeout Bundles aus und schreibt `evidence/dwt-s3-l2-summary.json`. |
| `scripts/run-l3-runtime-temp-repo-checks.sh` | Fuehrt DWT-S5 L3A-L3F gegen ein synthetisches Temp-Repo aus und schreibt `evidence/dwt-s5-l3-summary.json`. |
| `scripts/run-reporting-contract-checks.sh` | Fuehrt DWT-S4 Summary-, Telemetry-, Style- und Efficiency-Contract-Checks aus und schreibt `evidence/dwt-s4-reporting-summary.json`. |
| `reporting/fixtures/` | DWT-S4 positive, negative, warning, blocked and retained-baseline reporting fixtures. |
| `reporting/validators/` | Deterministic Node validator for DWT-S4 reporting fixtures. |
| `e2e/fixtures/control-session-boundary/` | ADV-CAS-S4 control-session boundary fixtures for observed-only behavior and direct-write/session-role false positives. |
| `e2e/validators/control-boundary-summary.js` | Deterministic validator for `docworkflow-agent-delivery-control-boundary-summary.v1` fixture replay. |
| `e2e/fixtures/visible-app-session-closeout/` | ADV-CAS-S5 visible Codex-App closeout archive fixtures for archived, already archived, headless, queued, retained and failure cases. |
| `e2e/validators/visible-session-closeout-summary.js` | Thin Node wrapper around `ArchiveVisibleCodexAppSession.cs` for S5 closeout archive fixture replay. |

## Schnellstart

```sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
```

Kompatibilitaetsname fuer den mock-only Standard-Gate:

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep
```

Der lokale Mock-E2E-Basispfad nutzt nur source-controlled Mockdaten unter `tests/docworkflow-agent-delivery/mock-data/**` und isolierte Evidence-Ordner unter `tests/docworkflow-agent-delivery/e2e/evidence/**`. `run-contract-checks.sh all --keep` bleibt ein mock-only Kompatibilitaetsname fuer denselben Standard-Gate; TC1/TC2 Legacy-Selectoren sind explicit-fixture-only und nicht der aktuelle Agent-Delivery-E2E-Erfolgsnachweis. `setup-fixture.sh` ist kein No-Argument-Standardpfad und darf nur mit expliziter Fixture-Quelle ausserhalb des Standard-Mock-E2E-Basispfads verwendet werden.

Akzeptierte Mock-E2E-Evidence:

| Slice | Bedeutung | Evidence |
|---|---|---|
| `MD-E2E-1` | Mock fixture family, Manifeste und Forbidden-Real-Fixture-Validator akzeptiert. | `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures/implementation-evidence.md` |
| `MD-E2E-2` | Local Mock Session Runner fuer `large`, `small` und `all` akzeptiert. | `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner/implementation-evidence.md`; `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/aggregate-summary.json` |
| `MD-E2E-3` | `run-mock-e2e-checks.sh all --keep` als fuehrender Standard-Gate und `run-contract-checks.sh all --keep` als mock-only Shim akzeptiert. | `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/implementation-evidence.md`; `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-3-mock-all/aggregate-summary.json`; `tests/docworkflow-agent-delivery/e2e/evidence/20260509T082132Z-all/aggregate-summary.json` |

KI-fuer-KMU und andere reale Produkt-Repositories sind nur historische/read-only oder verbotene Real-Fixture-Kontexte. Sie sind keine Standard-Fixture, kein Fallback, keine Kompatibilitaetsquelle und kein Target Workspace fuer den Mock-E2E-Gate. Ein spaeterer Live-Agent-/Codex-Session-Pfad gehoert zu `MD-E2E-5` und darf den lokalen Mock-E2E-Basispfad nicht ersetzen.

DWT-S1 L1 deterministic-only checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all
```

DWT-S4 reporting contract checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all
```

DWT-S2 L2 parent-first orchestration checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all
```

DWT-S3 L2 single-child delivery and closeout checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all
```

DWT-S5 L3 runtime temp-repo checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh all
```

ADV-CAS-S4 control-session boundary fixture checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh control-boundary
node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary
```

ADV-CAS-S3 / `MD-E2E-5` live visible Codex-App session gate:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

This command is an opt-in live gate and does not replace `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`. It writes `visible-session-summary.json` under the retained run directory and exits non-zero with `overall_workflow_status: "not_ready"` when the live visible-session, S4, S5, or output evidence is incomplete. A passing live run must retain `visible-session-summary.json`, parent plus five child visible-session evidence records, S4 control-boundary status, S5 archive/no-thread evidence and final output proof for exact `1\n2\n3\n4\n5\n`.

ADV-CAS-S5 visible Codex-App closeout archive checks:

```sh
dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate
dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout
```

Optional mit behaltenem L1-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all --keep
```

Optional mit behaltenem DWT-S2 L2-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all --keep
```

Optional mit behaltenem DWT-S3 L2-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all --keep
```

Optional mit behaltenem DWT-S4 Reporting-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all --keep
```

Optional mit behaltenem DWT-S5 L3-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh all --keep
```

Optional mit behaltenem Mock-E2E-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep
```

## Automatisierungsgrenzen

Automatisierbar:

- exakte Child-Index-Mindestspalten,
- Child-/Handoff-Konsistenz,
- implementation-allowing Hardening Verdict fuer S3,
- Blockade fuer nicht implementation-ready Children,
- konkrete Allowed Write-Sets,
- stale/missing Target Repository im Handoff,
- Temp-Repo-Gate fuer Delivery-Starts,
- Vorhandensein lokaler und Docker-/Harness-Gates im Vertrag,
- L1-Fixture-Provenance, Child-Readiness-Regressionen, Hidden-Normalization-Fehler und S0-Limitation-Isolation.
- DWT-S2 Parent-only Startzustand, generated Child Control Surface, Direct-Implementation-Blocker, Thin-Child-Readiness-Blocker, exactly-one leading Next Child State und blocked-agent Ehrlichkeit.
- DWT-S3 current-handoff Delivery-Kickoff, stale Handoff Blocker, Temp-Workspace-Isolation, synthetic Closeout Sync, DWT-S5 Blockade, blocked-agent Ehrlichkeit und DWT-S4-kompatible Summary/Telemetry.
- DWT-S4 Summary-v1-Felder, Legacy-Kompatibilitaet fuer die retained DWT-S1 Summary, Telemetry-Verbote, Style-/Handoff-Sync, Efficiency-Warnungen und Downstream-Release-Blockaden.
- DWT-S5 synthetic Temp-Repo-Materialisierung, current-handoff Delivery-Kickoff, local runtime gate, container/harness gate, forbidden-target/secret Blocker, Closeout-Sync und DWT-S4-kompatible Summary/Telemetry.
- ADV-CAS-S4 Control-Session Boundary fuer observed-only Control-Verhalten, verbotene direkte Orchestration-/Hardening-/Delivery-/Closeout-/Output-Writes, ununterscheidbare Session-Rollen und Mock-Runner-Substitute.

Agentischer Dry-Run:

- echte Ausfuehrung von `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery` und `spec-closeout`,
- semantische Bewertung der Parent-Coverage-Matrix,
- vollstaendige Runtime-Implementation und lokale/Docker-Harness-Verifikation,
- OpenSpec-Archivierung und Parent-/Index-/Evidence-Sync nach echter Delivery.

Die Dry-Run-Teile sind trotzdem als explizite Assertions im Testfall dokumentiert. Sie werden erst voll automatisierbar, wenn ein Agent-Runner oder ein maschinenlesbares Orchestration-Pack als stabiler Output existiert.

## DWT-S1 L1 Boundary

`run-l1-contract-checks.sh` ist bewusst deterministic-only. Der Runner kopiert synthetische Fixtures in einen isolierten Temp-Ordner, prueft Parent-only Cleanliness, generierte Child-Control-Provenance, Thin-Child-Readiness-Blocks, fehlende High-risk-Rehearsals, Hidden Normalization und S0-Limitation-Isolation. Er ruft keine Agenten, Promptfoo, Inspect AI, Codex, Docker, npm Registry oder Runtime-Repos auf.

Negative Fixtures gelten nur dann als erfolgreich geprueft, wenn der erwartete Blocker sichtbar wird. Deshalb kann `test_results` fuer einzelne L1-Cases bewusst `blocked` oder `fail` enthalten, waehrend der Runner insgesamt `RESULT: PASS` meldet.

## DWT-S4 Reporting Boundary

`run-reporting-contract-checks.sh` ist reporting-only. Der Runner liest die retained DWT-S1 Summary als externe Legacy-Baseline und prueft neue source-controlled Fixtures unter `reporting/fixtures/`. Er ruft keine Agenten, Promptfoo, Codex, Docker, npm Registry oder Runtime-Repos auf.

Die DWT-S4 Summary verwendet `schema_id: docworkflow-agent-delivery-summary.v1`. Negative Fixtures gelten als erfolgreich geprueft, wenn die erwartete Failure-Klasse sichtbar wird, z. B. `invalid_evidence_truth`, `forbidden_runtime_command` oder `stale_handoff_or_index_pointer`. Warning- und Blocked-Fixtures bleiben maschinenlesbare Ergebnisstatus, waehrend `harness_case_results` zeigt, ob die erwartete Contract-Assertion bestanden hat.

## DWT-S2 L2 Boundary

`run-l2-parent-orchestration-checks.sh` prueft Output-Bundles fuer Parent-first Orchestration. Fuer `all` und `agent` startet der Runner zusaetzlich den Promptfoo/Codex SDK Provider gegen den parent-only Fixture-Workspace und schreibt `promptfoo-eval.json`, `promptfoo-eval.txt` und `dwt-s2-agent-proof.json` in den Evidence-Ordner. Wenn `CODEX_HOME_OVERRIDE` nicht gesetzt ist und `~/.codex/auth.json` existiert, wird dieses lokale Codex-Home als Auth-Quelle verwendet; alternativ koennen `OPENAI_API_KEY` oder `CODEX_API_KEY` durch die Umgebung bereitgestellt werden. Negative Fixtures gelten als erfolgreich geprueft, wenn der erwartete Blocker sichtbar wird.

Eine akzeptierte L2-Agent-Proof braucht weiterhin `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target` und `overall_agent_proof_status: pass`. Der Selector `fallback` bleibt deterministic-only und kann keine akzeptierte Agent-Proof erzeugen.

## DWT-S3 L2 Boundary

`run-l2-single-child-closeout-checks.sh` prueft Output-Bundles fuer genau eine DWT-S3 Delivery- und Closeout-Session. Der Runner materialisiert source-controlled Fixture Bundles in einen isolierten Temp-Ordner, validiert retained DWT-S2 `ran-target` predecessor evidence, prueft den aktuellen DWT-S3 Handoff, blockiert stale oder out-of-workspace Kickoffs, validiert synthetic Closeout Sync und beweist, dass DWT-S5 nach DWT-S3 Closeout weiter `blocked_by_dependency` bleibt.

Der Selector `all` laeuft deterministic/fallback, solange `DWT_S3_ENABLE_AGENT=1` nicht gesetzt ist. Das ist absichtlich nicht als akzeptierte Agent-Proof markiert: die Summary meldet `runner_mode: fallback-artifact`, `agent_execution_status: blocked_runtime` und `overall_agent_proof_status: blocked`. Eine akzeptierte DWT-S3 Agent-Proof braucht weiterhin `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target` und `overall_agent_proof_status: pass`; der `agent` Selector kann diese Proof versuchen, wenn Codex/Promptfoo Auth und Runtime provisioniert sind.

## DWT-S5 L3 Boundary

`run-l3-runtime-temp-repo-checks.sh` materialisiert ein source-controlled synthetic runtime repo unter `<run-dir>/target-repos/dwt-s5-synthetic-runtime-repo/`. Der Runner validiert retained DWT-S3 `ran-target` predecessor evidence, den aktuellen DWT-S5 Handoff, ein konkretes Allowed Write-Set, lokale Runtime-Evidence, container/harness Evidence, forbidden-target/secret Blocker und Closeout-Sync fuer `DWT-PR3`, `DWT-PR4` und `DWT-PR5`.

Der Selector `preflight` prueft retained Evidence, Fixture-Integritaet und Temp-Repo-Provenance ohne Runtime-Gates. Der Selector `all` laeuft deterministic/fallback, solange `DWT_S5_ENABLE_AGENT=1` nicht gesetzt ist. In diesem Zustand meldet die Summary `runner_mode: fallback-artifact`, `agent_execution_status: blocked_runtime` und `overall_runtime_proof_status: blocked`, auch wenn lokale Runtime und container/harness Fixture erfolgreich liefen. Eine akzeptierte DWT-S5 Runtime-Proof braucht weiterhin `runner_mode: promptfoo-codex`, `agent_execution_status: ran-target`, `overall_runtime_proof_status: pass` sowie lokale Runtime- und container/harness Evidence aus dem generated synthetic temp repo.

Retained DWT-S5 target evidence from the accepted Promptfoo/Codex path is stored under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-ran-target/`. Retained fallback/blocker rehearsal evidence is stored separately under `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-blocked-runtime/`.
