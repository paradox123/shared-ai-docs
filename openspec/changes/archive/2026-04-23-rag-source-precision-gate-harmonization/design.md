## Context

Die RAG-Spec-Landschaft ist in Parent + Child-Specs 01..05 aufgeteilt. Das Finding adressiert einen moeglichen Interpretationskonflikt bei Eval-Metriken (`source_precision` vs. Blocking-KPIs). Die eigentliche Runtime ist fuer diesen Change nicht Gegenstand.

## Goals / Non-Goals

**Goals:**
- Eindeutiger, widerspruchsfreier Metrikvertrag zwischen Parent und Child-04.
- Klare Trennung zwischen Blocking-Gates und optionalem Monitoring.
- Nachvollziehbare OpenSpec-Evidence inkl. Re-Review.

**Non-Goals:**
- Implementierung oder Validierung der RAG-Runtime/CLI.
- Aenderung der fachlichen KPI-Schwellenwerte in Child-04.
- Scope-Ausweitung auf andere Child-Specs ausser notwendige Konsistenzreferenzen.

## Decisions

1. Parent bleibt Governance-/Routing-Ebene, Child-04 bleibt KPI-Gate-Quelle.
2. `source_precision` wird explizit als optionales Monitoring behandelt, nicht als Blocking-Gate.
3. Verifikation fuer diesen Change erfolgt als Dokument-/Contract-Verification (rg/assertions) statt Runtime-RAG-Ausfuehrung.

## Risks / Trade-offs

- [Risiko] Reviewer lesen nur Parent und uebersehen Child-04-Details. -> Mitigation: explizite Parent-Referenz auf Child-Gate-Quelle und optionale Metrikregel.
- [Risiko] Runtime-DoD-Vorlagen werden falsch auf Spec-only-Change uebertragen. -> Mitigation: Scope Contract und Evidence trennen klar Spec-Contract-Change von Runtime-Implementierung.

## Migration Plan

1. OpenSpec-Change-Artefakte vervollstaendigen.
2. Parent/Child-04 minimal patchen.
3. Marker-/Contract-Verification und check-build-watcher ausfuehren.
4. Acceptance Matrix + Evidence finalisieren.

## Open Questions

- Keine blockierenden Open Questions fuer diesen bounded Spec-Change.
