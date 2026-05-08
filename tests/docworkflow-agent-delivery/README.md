# DocWorkflow Agent Delivery Test Suite

Diese Testsuite prueft den shared-ai-docs Agent Delivery Workflow fuer Parent-/Child-Spec-Delivery. Sie ist absichtlich klein und contract-orientiert: sie soll Workflow-Gates reproduzierbar machen, ohne KI-fuer-KMU-Originaldateien oder Legacy-Specs zu migrieren.

## Struktur

| Pfad | Zweck |
|---|---|
| `testcases/tc1-parent-first-orchestration-child-hardening.md` | Testcase 1 als lesbarer Harness-Vertrag. |
| `testcases/tc2-single-child-delivery-next-handoff.md` | Testcase 2 als lesbarer Harness-Vertrag. |
| `l1/fixtures/` | Kleine synthetische DWT-S1-Fixtures fuer deterministische L1-Vertragschecks. |
| `scripts/setup-fixture.sh` | Kopiert reale KI-fuer-KMU-Spec-Fixtures in einen Temp-Ordner und normalisiert nur diese Kopie. |
| `scripts/run-contract-checks.sh` | Fuehrt automatisierbare Contract-Checks fuer TC1/TC2 aus und schreibt Evidence in die Temp-Fixture. |
| `scripts/run-l1-contract-checks.sh` | Fuehrt DWT-S1 L1A-L1F gegen synthetische Fixtures aus und schreibt `evidence/l1-summary.json`. |
| `scripts/run-reporting-contract-checks.sh` | Fuehrt DWT-S4 Summary-, Telemetry-, Style- und Efficiency-Contract-Checks aus und schreibt `evidence/dwt-s4-reporting-summary.json`. |
| `reporting/fixtures/` | DWT-S4 positive, negative, warning, blocked and retained-baseline reporting fixtures. |
| `reporting/validators/` | Deterministic Node validator for DWT-S4 reporting fixtures. |

## Schnellstart

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all
```

DWT-S1 L1 deterministic-only checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all
```

DWT-S4 reporting contract checks:

```sh
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all
```

Optional mit behaltenem L1-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all --keep
```

Optional mit behaltenem DWT-S4 Reporting-Evidence-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh all --keep
```

Optional mit behaltenem Temp-Ordner:

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep
```

Optional mit expliziter Fixture:

```sh
fixture_dir="$(tests/docworkflow-agent-delivery/scripts/setup-fixture.sh | sed -n 's/^FIXTURE_DIR=//p')"
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --fixture "$fixture_dir"
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
- DWT-S4 Summary-v1-Felder, Legacy-Kompatibilitaet fuer die retained DWT-S1 Summary, Telemetry-Verbote, Style-/Handoff-Sync, Efficiency-Warnungen und Downstream-Release-Blockaden.

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
