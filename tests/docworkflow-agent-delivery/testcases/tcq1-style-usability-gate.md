# TCQ1 Style and Usability Gate

## Ziel

Pruefen, dass DWT-S4 Reporting-Artefakte stale oder unsynchronisierte Child-Spec-, Child-Index- und Handoff-Daten als maschinenlesbaren Style-Fehler melden.

## Input

- Fixture: `tests/docworkflow-agent-delivery/reporting/fixtures/style-stale-handoff-pointer/style-fixture.json`
- Runner: `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh style`

## Erwartung

- `child_spec`, `child_index_row` und `persisted_handoff` muessen dieselbe Child ID, denselben Hardening Verdict, denselben Target Repository Pfad und denselben Handoff Pointer enthalten.
- Eine Abweichung im Handoff Pointer erzeugt `stale_handoff_or_index_pointer`.
- Der Fixture-Status ist `fail`, waehrend der Harness insgesamt `PASS` meldet, weil die negative Assertion erwartet ist.
- Der Evidence-Output `dwt-s4-r4-style.json` enthaelt die konkrete abweichende Eigenschaft.

## Grenzen

Der Test startet keine Agenten und liest keine Runtime-Repositories. Er prueft nur den Reporting-/Style-Vertrag.
