## Why

Das gemeldete Finding zeigt ein Governance-Risiko zwischen Parent- und Child-Specs: Metrik- und Gate-Aussagen duerfen nicht missverstaendlich sein, insbesondere fuer `source_precision` versus verbindliche Phase-1-Blocking-KPIs. Ohne klare Harmonisierung drohen inkonsistente Implementierungs- und Abnahmeentscheidungen.

## What Changes

- Parent-Spec-Verifikationsabschnitt wird explizit als Child-gesteuerter Gate-Contract praezisiert.
- Child-Spec 04 bekommt eine explizite Klarstellung zu optionalen Monitoring-Metriken (inkl. `source_precision`) ohne Blocking-Wirkung.
- OpenSpec-Evidence fuer Marker-Check, Contract-Alignment und Re-Review wird erzeugt.
- Build-Monitoring-Evidenz wird ueber `check-build-watcher` erfasst.

## Capabilities

### New Capabilities
- `rag-metric-gate-alignment`: Sicherstellung eines konsistenten Metrik- und Gate-Vertrags zwischen Parent-RAG-Spec und Child-Spec 04.

### Modified Capabilities
- None.

## Impact

- Betroffene Dateien liegen in `_specs/` und OpenSpec-Change-Artefakten.
- Keine Runtime- oder API-Implementierungsaenderung.
- Reduziertes Rework-Risiko in spaeteren Implementierungsruns.
