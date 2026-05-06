# Spec Goldstandard Candidates

Diese Datei sammelt konkrete Kandidaten fuer Goldstandard-Referenzen. Die Bewertung bezieht sich nur auf Spec-Qualitaet, nicht auf Produktinhalt.

Kandidaten werden hier einzeln gepflegt, damit `docs/spec-goldstandard.md` produktneutral bleibt.

| Kandidat | Geeignete Variante | Referenzstaerke | Fehlende Schritte vor `reference` |
|---|---|---|---|
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md` | `vertical spike Spec` | Fuehrungsquellen, Scope-Grenze, Decision Freeze Pack, Artefaktvertrag, Harness, Preflight/Gate Verification und DoD/Evidence. | Review Control Surface mit Spec-Variante/Goldstandard Status, Parent Scope Conformance, Dependencies/Write-Set. |
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md` | `contract-heavy Spec` und `output/report/data-artifact Spec` | API-, Token-, Status-, Integritaets- und Artefaktvertrag mit Fehlerfaellen, Docker-Gate und Closeout Evidence. | Review Control Surface, Decision Freeze Pack als eigener Abschnitt, Parent Scope Conformance, Canonical Examples/Fixtures-Entscheidung. |
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md` | `contract-heavy Spec` | Manifestvertrag, kanonische Beispiele, Pflicht-Cases, Negative Cases, Secret-Assertions und harte Verification Commands. | Implementation-/Closeout-Evidence nach Umsetzung, Review Control Surface, Decision Freeze Pack, Parent Scope Conformance, Dependencies/Write-Set. |
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md` | `Parent/Master Spec` | Stabile Reihenfolge, Requirement-IDs, Non-Goals, Traceability, offene Punkte und naechste Slice-Empfehlung. | Review Control Surface, Child Coverage Matrix, Child Readiness Matrix, Hardening Queue, optional Parallel Work Control Surface oder Verweis darauf. |

## Pflege-Regeln

1. Kandidaten werden nur explizit und einzeln aufgenommen.
2. Aufnahme in diese Liste setzt keinen `Goldstandard Status: reference`.
3. Referenzstatus bleibt an den Prozess in `docs/spec-goldstandard.md` gebunden.
4. Produkt- oder Projektnamen in dieser Datei sind Beispiele und keine globalen Workflow-Vorgaben.
