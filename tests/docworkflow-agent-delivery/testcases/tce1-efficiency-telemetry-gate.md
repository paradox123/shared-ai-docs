# TCE1 Efficiency and Telemetry Gate

## Ziel

Pruefen, dass DWT-S4 Telemetry-Manifeste verbotene Runtime-Command-Klassen failen und gerechtfertigte breite Reads als `warn` statt `pass` ausweisen.

## Inputs

- Negative Fixture: `tests/docworkflow-agent-delivery/reporting/fixtures/telemetry-forbidden-runtime-command/agent-run-manifest.json`
- Warning Fixture: `tests/docworkflow-agent-delivery/reporting/fixtures/efficiency-justified-broad-read-warn/agent-run-manifest.json`
- Runner: `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh telemetry` und `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh efficiency`

## Erwartung

- Command-Klassen `docker`, `runtime-build`, `runtime-test`, `credential-copy`, `ki-fuer-kmu-write` und `deployment` sind fuer reporting-only Runs verboten.
- Das Forbidden-Runtime-Fixture erzeugt den erwarteten Fixture-Status `fail` mit `forbidden_runtime_command`.
- Das Broad-Read-Fixture bleibt innerhalb des Budgets, enthaelt eine Justification und erzeugt `warn`.
- Unbegruendete oder versteckte Drift darf nicht als `pass` erscheinen.

## Grenzen

Der Test bewertet Command-Telemetry, nicht Runtime-Implementation. Er fuehrt keine Docker-, Build-, Auth- oder Deployment-Kommandos aus.
