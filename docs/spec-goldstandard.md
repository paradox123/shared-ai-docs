# Spec Goldstandard

Diese Referenz definiert, wann eine Spec im shared-ai-docs DocWorkflow als Goldstandard-Kandidat oder Goldstandard-Referenz gilt.

Der Goldstandard bewertet die Qualitaet der Spec als Arbeits- und Lieferartefakt. Er bewertet nicht das Produkt, das Fachkonzept oder den kommerziellen Inhalt einer Spec.

## Scope Guard

Diese Referenz ist bewusst eng geschnitten:

1. Sie definiert Spec-Qualitaet, nicht Produktqualitaet.
2. Sie startet keine SpecOps-Backfills.
3. Sie migriert keine alten Specs pauschal.
4. Sie misst bereits akzeptierte Legacy-Specs nicht nachtraeglich.
5. Sie erhebt Referenzen nur einzeln und explizit.
6. Sie entscheidet zuerst den Standard; Skill- und Doc-Anpassungen folgen nur gezielt, wenn der Standard stabil ist.

## Grundsatz

Eine Spec ist goldstandardfaehig, wenn ein kompetenter Implementer oder Reviewer ohne Rueckfrage versteht:

1. welches Ziel erreicht werden soll,
2. welche Grenzen gelten,
3. welche Entscheidungen eingefroren sind,
4. welche normativen Vertraege gelten,
5. welche positiven, negativen und blockierenden Faelle relevant sind,
6. wie die Arbeit verifiziert wird,
7. welche Abhaengigkeiten und Write-Sets gelten,
8. welche Evidence fuer Done oder Accepted erforderlich ist.

Goldstandard bedeutet nicht maximale Laenge. Goldstandard bedeutet synchronisierte Review-Flaeche, klare Scope-Disziplin, beweisbare Lieferreife und nachvollziehbare Traceability.

## Klassifizierung Im Dokument

Die Goldstandard-Klassifizierung muss in der Spec selbst sichtbar sein, damit spaetere Bearbeitung nachvollziehbar bleibt. Sie gehoert in die `Review Control Surface`.

```md
## Review Control Surface

- Spec-Variante:
- Goldstandard Status:
- Ziel:
- In Scope:
- Out of Scope:
- Wichtigste Test-/Harness-Cases:
- Wichtigste Verification Commands:
- Offene Entscheidungen:
- Readiness Status:
```

Erlaubte `Goldstandard Status`-Werte:

- `none`: normale Spec ohne Referenzanspruch.
- `candidate`: Spec wird als moegliche Goldstandard-Referenz bewertet oder gehardent.
- `reference`: Spec ist fuer ihre Variante als Goldstandard-Referenz erhoben.

Dieser Status ist getrennt vom Workflow-`Status` im Header (`🟡 Spec`, `🟠 Plan`, `🔵 Implemented`, `🟢 Accepted`).

## Entscheidungsstand

Folgende Entscheidungen sind fuer diesen Goldstandard gesetzt:

1. Es gibt keinen One-Size-Fits-All-Goldstandard. Goldstandard-Referenzen werden pro Spec-Variante gefuehrt.
2. `Goldstandard Status` ist im Dokument sichtbar, damit spaetere Bearbeitung nachvollziehen kann, warum eine Spec als Kandidat oder Referenz behandelt wird.
3. Die ausfuehrliche Definition lebt in dieser Datei; `docs/doc-workflow.md` bleibt die knappe kanonische Gate-Quelle und verweist hierher.
4. Bereits akzeptierte Specs werden nicht nachtraeglich an dieser Referenz gemessen. Sie bleiben als umgesetzte Historie erhalten.

## Mindestbestandteile Fuer Alle Specs

Jede neue oder aktiv bearbeitete Spec braucht mindestens:

1. Header mit `Date`, `Status` und `Scope`.
2. `Review Control Surface` mit Spec-Variante und Goldstandard Status.
3. Ziel, In Scope und Out of Scope.
4. Fuehrende Quellen, Parent/Master Coverage oder eine andere explizite Source of Truth.
5. Offene Entscheidungen als `[MISSING ...]`, `[DECISION ...]` oder `[REVIEW ...]` Marker.
6. Acceptance Criteria oder ein klares Done-Signal.
7. Verification-/Review-Evidence passend zur Spec-Variante.
8. Append-only History und `SessionId`.

## Varianten

### Parent/Master Spec

Eine Parent/Master Spec ist die fuehrende Scope- und Anforderungsquelle fuer mehrere Child Specs oder Delivery Slices.

Verpflichtend:

- stabiler Ziel- oder Nutzerpfad,
- Non-Goals,
- Requirement-IDs oder stabile Requirement-Zeilen,
- Traceability zu Quellen,
- Coverage Matrix oder Child-Coverage-Plan,
- Child Readiness Matrix oder Hardening Queue,
- Empfehlung fuer naechste Slices,
- Closeout-Sync-Regeln fuer akzeptierte Children.

Kontextabhaengig:

- Parallel Work Control Surface, wenn mehrere Child Specs oder Implementierungen parallel laufen koennen,
- Backlog-/Re-entry-Liste fuer bewusst deferierten Scope,
- Orchestrator-Output als eigenes Delivery Orchestration Pack.

### Implementation-Ready Child Spec

Eine implementation-ready Child Spec beschreibt genau eine umsetzbare Delivery-Scheibe.

Verpflichtend:

- Parent/Master Coverage,
- Parent Scope Conformance,
- Decision Freeze Pack,
- Normative Contract,
- konkrete Acceptance Criteria,
- Harness-/Verification-Cases inklusive relevanter Negativ-, Fehler-, Fallback- und Secret-/Redaction-Cases,
- Verification Commands mit Execution Context, Preflight, Gate Verification, Erfolgskriterien, Runtime-Readiness und Anti-Loop-Regel,
- Dependencies and Write-Set,
- Definition of Ready fuer Umsetzung,
- Definition of Done / Closeout Evidence,
- Closeout Sync Targets.

Kontextabhaengig:

- Canonical Examples oder Fixture-Pfade,
- Parallel Work Control Surface fuer spec/doc hardening oder implementation,
- OpenSpec Scope Contract.

### Contract-Heavy Spec

Eine contract-heavy Spec definiert ein Manifest, Schema, API, Statusmodell, Signatur-/Hashmodell, Migration, Entitlement, Fallback, Report, Artifact-Format oder eine andere downstream-relevante Struktur.

Verpflichtend:

- normative Felder und erlaubte Werte,
- Statuswerte inklusive Failure- und Blocked-States,
- Identity, Context, Provenance und Version nur dort, wo downstream Interpretation sie braucht,
- Hash-/Signatur-/Canonical-Serialization-Regeln, wenn Integritaet relevant ist,
- Fallback- und Compatibility-Regeln,
- Security-/Redaction-Regeln,
- Canonical Examples, Fixture-Dateien oder eine begruendete Hybrid-Entscheidung,
- Tests, die beweisen, dass ungueltige, inkompatible oder unsichere Artefakte blockieren.

Kontextabhaengig:

- eingebettete Minimalbeispiele fuer kurze normative Vertraege,
- referenzierte Fixture-Dateien fuer grosse oder ausfuehrbare Beispiele,
- Migration-/Lineage-Regeln fuer langlebige Artefakte.

### Vertical Spike Spec

Eine vertical spike Spec beweist einen kleinsten lauffaehigen Durchstich ueber mehrere Systemgrenzen.

Verpflichtend:

- fuehrende Quellen und klare Nicht-Quellen,
- kleinster beweisbarer End-to-End-Pfad,
- echte Artefaktnamen und Schnittstellen, auch wenn Implementierungen noch Stub-Charakter haben,
- explizite Out-of-Scope-Grenzen gegen Vollausbau,
- Blockerpfade,
- Harness-Cases fuer lokalen und, wenn relevant, Container-/Runtime-Pfad,
- DoR/DoD mit konkreter Evidence.

Kontextabhaengig:

- Stub-Vertraege,
- technische Projektstruktur,
- Nachfolge-Slice-Hinweise, ohne sie in den Spike-Scope zu ziehen.

### Output/Report/Data-Artifact Spec

Eine output/report/data-artifact Spec definiert ein erzeugtes Dokument, Report, Datenpaket, Export oder maschinenlesbares Ergebnis.

Verpflichtend:

- Output-Zweck und Zielnutzer,
- Schema oder Struktur,
- required und optional fields,
- Provenance, Identity, Version und Status, wenn das Artefakt spaeter gelesen oder weiterverarbeitet wird,
- akzeptierte leere, partielle, blocked und failed Outputs,
- Redaction-/Privacy-Regeln,
- Beispieloutput oder Fixture,
- Verification, dass der Output nicht durch Ueberspringen des intendierten Flows erzeugt werden kann.

Kontextabhaengig:

- visuelle Acceptance fuer gerenderte Reports,
- Exportformate,
- Retention-/Deletion-Evidence.

## Verpflichtend Vs. Kontextabhaengig

Verpflichtend ist alles, was ohne weitere Entscheidung fuer die konkrete Spec-Variante gebraucht wird, damit Scope, Umsetzung und Review nicht auseinanderlaufen.

Kontextabhaengig ist alles, was nur bei bestimmten Risiken oder Artefakten noetig ist, zum Beispiel:

- Parallel Work Control Surface nur bei paralleler Arbeit.
- Canonical Serialization nur bei Hash, Signatur oder stabiler byte-genauer Pruefung.
- Runtime-Readiness nur bei Services, Containern oder asynchronen Starts.
- Provenance-Felder nur, wenn ein downstream Flow die Herkunft spaeter interpretieren muss.
- Closeout Evidence nur, wenn ein Change implementiert oder akzeptiert wurde.

## Disqualifizierende Anti-Patterns

Eine Spec ist nicht goldstandardfaehig, wenn eines dieser Muster blockierend bleibt:

1. Scope ist zu breit fuer eine realistische Delivery und hat keine Parent/Child-Zerlegung.
2. Review Control Surface fehlt, ist stale oder widerspricht dem Body.
3. Acceptance kann erfuellt werden, ohne den intendierten Kontrollfluss auszufuehren.
4. Verification Commands sind generisch, nicht ausfuehrbar, ohne Erfolgskriterien oder ohne notwendige Runtime-Readiness.
5. Contract-heavy Spec hat weder Canonical Examples noch Fixture-Pfade noch eine begruendete Hybrid-Entscheidung.
6. Parent Scope wird stillschweigend verengt, widersprochen oder fallen gelassen.
7. Negative, Fallback-, Secret-/Redaction- oder Failure-Cases fehlen trotz erkennbarem Risiko.
8. `[MISSING ...]`, `[DECISION ...]` oder blockierende `[REVIEW ...]` Marker werden als Aufgaben versteckt statt sichtbar gehalten.
9. Parallelisierung wird behauptet, ohne Write-Sets, Shared-File-Regeln, Dependencies, Integration Owner und Merge-/Sync-Reihenfolge.
10. Die Spec mischt Produktbewertung, Backfill, Runtime-Implementation und Workflow-Methodik so, dass keine saubere Review- oder Delivery-Grenze bleibt.

## Erhebung Zur Goldstandard-Referenz

Eine bestehende Spec wird nur explizit und einzeln zur Goldstandard-Referenz erhoben. Es gibt keine pauschale Migration alter Specs.

Prozess:

1. Spec-Variante festlegen.
2. `Goldstandard Status: candidate` in der Review Control Surface setzen.
3. Gegen Mindestbestandteile und variantenbezogene Pflichtteile pruefen.
4. Fehlende Kontrollflaechen und sicher inferierbare Struktur ergaenzen, ohne neue Produkt-, Scope-, Architektur-, Security-, Legal- oder Data-Contract-Entscheidungen zu erfinden.
5. Review Control Surface mit Detailbody synchronisieren.
6. `doc-review-autoresolve`-Stil anwenden: autonome Inkonsistenzen bereinigen, echte Entscheidungen offen markieren.
7. Bei stabilem Ergebnis `Goldstandard Status: reference` setzen und in der History begruenden.

Referenzstatus darf nicht gesetzt werden, wenn blockierende Marker, Parent-Conformance-Widersprueche oder nicht belegte Verification-/Evidence-Ansprueche verbleiben.

## Kandidatenreferenzen

Die folgenden Specs sind als Lern- und Referenzkandidaten geeignet. Die Bewertung bezieht sich nur auf Spec-Qualitaet, nicht auf Produktinhalt.

| Kandidat | Geeignete Variante | Referenzstaerke | Fehlende Schritte vor `reference` |
|---|---|---|---|
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s1-vertical-architecture-spike-spec.md` | `vertical spike Spec` | Fuehrungsquellen, Scope-Grenze, Decision Freeze Pack, Artefaktvertrag, Harness, Preflight/Gate Verification und DoD/Evidence. | Review Control Surface mit Spec-Variante/Goldstandard Status, Parent Scope Conformance, Dependencies/Write-Set. |
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md` | `contract-heavy Spec` und `output/report/data-artifact Spec` | API-, Token-, Status-, Integritaets- und Artefaktvertrag mit Fehlerfaellen, Docker-Gate und Closeout Evidence. | Review Control Surface, Decision Freeze Pack als eigener Abschnitt, Parent Scope Conformance, Canonical Examples/Fixtures-Entscheidung. |
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md` | `contract-heavy Spec` | Manifestvertrag, kanonische Beispiele, Pflicht-Cases, Negative Cases, Secret-Assertions und harte Verification Commands. | Implementation-/Closeout-Evidence nach Umsetzung, Review Control Surface, Decision Freeze Pack, Parent Scope Conformance, Dependencies/Write-Set. |
| `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md` | `Parent/Master Spec` | Stabile Reihenfolge, Requirement-IDs, Non-Goals, Traceability, offene Punkte und naechste Slice-Empfehlung. | Review Control Surface, Child Coverage Matrix, Child Readiness Matrix, Hardening Queue, optional Parallel Work Control Surface oder Verweis darauf. |

## Legacy-Regel

Bereits akzeptierte Legacy-Specs werden nicht nachtraeglich am Goldstandard gemessen. Sie bleiben als historische, umgesetzte Artefakte gueltig, wie sie akzeptiert wurden.

Goldstandard-Regeln gelten fuer:

1. neue Specs,
2. aktive Spec-Kandidaten,
3. Specs, die explizit fuer eine Referenz-Erhebung geoeffnet werden,
4. Child Specs, die implementation-ready gemacht werden sollen.

## Minimaltemplate

```md
**Date:** YYYY-MM-DD
**Status:** 🟡 Spec
**Scope:** <one-line scope>

---

## Review Control Surface

- Spec-Variante:
- Goldstandard Status: none
- Ziel:
- In Scope:
- Out of Scope:
- Wichtigste Test-/Harness-Cases:
- Wichtigste Verification Commands:
- Offene Entscheidungen:
- Readiness Status:

## Goal

## In Scope

## Out of Scope

## Sources / Parent Coverage

## Decision Freeze Pack

## Normative Contract

## Acceptance / Harness Cases

## Verification Commands

## Definition of Ready

## Definition of Done / Closeout Evidence

## Dependencies and Write-Set

## History

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | User/Codex | Initial spec created. |

SessionId: <stable-id>
```

Omitted sections must be intentionally irrelevant for the selected Spec-Variante or replaced by a variant-specific equivalent.

## Mini-Retro

- Was wurde entschieden? Goldstandard wird variantenbezogen definiert; der Status wird im Dokument sichtbar getragen; akzeptierte Legacy-Specs werden nicht nachtraeglich bewertet.
- Was wurde geaendert? Diese Referenz ergaenzt Scope Guard, Entscheidungsstand, Varianten, Mindestbestandteile, Anti-Patterns, Erhebungsprozess, Kandidaten und Legacy-Regel.
- Was bleibt offen? Ob spaeter einzelne Skills direkt auf diese Datei verweisen oder nur ueber `doc-workflow.md`.
- Welche Evidenz/Verification fehlt? Noch kein praktischer Erhebungs-Run an einer Kandidaten-Spec.
- Welche Skill-/Workflow-Reibung ist aufgefallen? Bestehende starke Specs entstanden vor der heutigen Review-Control-Surface-Pflicht; fuer Referenz-Erhebung reichen gezielte Patches statt Altbestand-Migration.
- Session-/Kontextzustand: weiterarbeiten in dieser Session ist moeglich.
