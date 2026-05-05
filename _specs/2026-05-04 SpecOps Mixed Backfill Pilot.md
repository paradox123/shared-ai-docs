**Date:** 2026-05-04
**Status:** 🔵 Implemented
**Scope:** Zweiter SpecOps-MVP-Slice fuer einen gemischten Backfill aus Nebenkosten-Umbrella, Nebenkosten-Slice und CheckBuild-Spec

---

## Kontext

Der erste SpecOps-Slice `2026-05-04 SpecOps RAG Project Board Pilot.md` hat die lokale Obsidian-Struktur unter `_shared/SpecOps/` aufgebaut. Die Review-Erkenntnis war: Die technische Struktur funktioniert, aber die Uebersicht bleibt zu leer, solange nur RAG erfasst ist.

Dieser Child-Slice nutzt den im Dashboard angelegten Backlog-Eintrag `mixed-backfill-pilot`, um SpecOps selbst zu testen:

1. Kann SpecOps mehrere Projekte sichtbar machen?
2. Koennen verschiedene Spec-Formate einheitlich als Entity Notes dargestellt werden?
3. Werden rekonstruierte, explizite und konfliktbehaftete Metadaten sichtbar statt versteckt?

## Ziel

Ein gemischter Backfill erfasst genau drei reale Specs:

1. eine Nebenkosten-Umbrella-Spec,
2. eine Nebenkosten-Slice-Spec,
3. eine CheckBuild-artige Spec.

Danach soll das Dashboard erstmals zeigen, dass SpecOps nicht nur ein RAG-Board ist, sondern eine projektuebergreifende Control Plane werden kann.

## In Scope

1. Drei neue `type: spec` Entity Notes unter `_shared/SpecOps/Entities/specs/`.
2. Ein gemischtes Backfill-Dashboard unter `_shared/SpecOps/Dashboards/`.
3. Projektboards fuer `Nebenkostenabrechnung` und `NCG / CheckBuild`.
4. Aktualisierung des Backlog-Items `mixed-backfill-pilot`.
5. Aktualisierung der Child-Spec mit Implementation Evidence nach Verifikation.

## Out of Scope

1. Kein Voll-Backfill aller Nebenkosten- oder CheckBuild-Specs.
2. Keine Release-Entity-Notes.
3. Keine automatisierte Metadatenextraktion.
4. Keine Aenderung an Fachcode, Skills, CheckBuild-Logik oder Nebenkosten-Artefakten.
5. Kein finaler Entscheid, ob Projektboards spaeter manuell oder templategeneriert entstehen.

## Decision Freeze Pack

### Betroffene Quellen

| Rolle | Quelle | Rekonstruktionsgrund |
|-------|--------|----------------------|
| Nebenkosten Umbrella | `_specs/Completed/2026-03-14 Nebenkostenabrechnung Pipeline.md` | Autoritative Neustart-Spec, Completed-Pfad, produktuebergreifender Scope. |
| Nebenkosten Slice | `_specs/Completed/2026-04-10 Nebenkostenabrechnung 2025 BE2 Heiznebenkosten Sonderverteilung Korrektur-Slice.md` | Explizit accepted/closed, klare Zielartefakte und Verification Commands. |
| CheckBuild | `_specs/Completed/2026-03-03 CheckBuild Skill.md` | Iterative Spec mit spaeteren Implementierungs- und Retro-Abschnitten, guter Konfliktfall fuer Metadatenqualitaet. |

### Datenmodell-Entscheidungen

1. Completed-Pfad darf `status: accepted` nahelegen, wenn kein staerkerer Gegenbeleg existiert.
2. Explizite Closeout-Aussagen schlagen Pfad-Inferenz.
3. Widerspruechliche Statussignale fuehren zu `metadata_quality: conflict`.
4. Unscharf rekonstruierte Felder duerfen gesetzt werden, muessen aber `metadata_quality: inferred` tragen.
5. Die drei Entities duerfen absolute lokale `source`-Pfade verwenden, weil SpecOps aktuell local-first im DanielsVault arbeitet.

### Abnahmekriterien

Go:

1. Die drei neuen Spec-Entities existieren.
2. `Nebenkostenabrechnung` hat mindestens zwei echte Spec-Entities.
3. `NCG / CheckBuild` hat mindestens eine echte Spec-Entity.
4. Das Dashboard enthaelt eine Mixed-Backfill-Sicht.
5. Jede neue Spec-Entity hat `type`, `id`, `title`, `project`, `status`, `source`, `metadata_quality`.
6. Mindestens eine Entity demonstriert `metadata_quality: inferred`.
7. Mindestens eine Entity demonstriert `metadata_quality: conflict`.
8. Das Backlog-Item `mixed-backfill-pilot` ist nicht mehr nur `ready_for_spec`, sondern mit dieser Child-Spec verbunden.

No-Go:

1. Der Backfill erzeugt nur Text in der Spec, aber keine sichtbaren Entity Notes.
2. Unklare Felder werden als sicher dargestellt.
3. Der Dashboard-Zuwachs bleibt auf RAG beschraenkt.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Pflichtchecks:

1. `test -f _shared/SpecOps/Entities/specs/nebenkostenabrechnung-pipeline-2026-03-14.md`
2. `test -f _shared/SpecOps/Entities/specs/nebenkostenabrechnung-be2-heiznebenkosten-sonderverteilung-2026-04-10.md`
3. `test -f _shared/SpecOps/Entities/specs/checkbuild-skill-2026-03-03.md`
4. `test -f _shared/SpecOps/Dashboards/mixed-backfill.md`
5. `test -f _shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md`
6. `test -f _shared/SpecOps/Dashboards/projects/ncg-checkbuild.md`
7. `rg -n 'metadata_quality: inferred|metadata_quality: conflict|mixed-backfill-pilot|Nebenkostenabrechnung|NCG / CheckBuild' _shared/SpecOps`
8. `rg -n 'Mixed Backfill|Dashboards/mixed-backfill' _shared/SpecOps/Dashboard.md _shared/SpecOps/Dashboards/mixed-backfill.md`

## Backlog Handling

Dieser Slice ist selbst ein Test fuer Backlog-Pflege:

1. Vor Umsetzung steht `mixed-backfill-pilot` auf `ready_for_spec`.
2. Nach Erstellung dieser Child-Spec wird der Backlog-Eintrag mit `promoted_to` auf diese Spec verlinkt.
3. Nach Umsetzung wird der Backlog-Eintrag auf `done` gesetzt, sofern die Verifikation erfolgreich ist.

## Implementation Evidence

Target runtime: lokaler DanielsVault unter `/Users/dh/Documents/DanielsVault`.

| Check | Status | Evidence |
|-------|--------|----------|
| Nebenkosten umbrella entity exists | ran-target | `test -f _shared/SpecOps/Entities/specs/nebenkostenabrechnung-pipeline-2026-03-14.md` returned exit code `0`. |
| Nebenkosten slice entity exists | ran-target | `test -f _shared/SpecOps/Entities/specs/nebenkostenabrechnung-be2-heiznebenkosten-sonderverteilung-2026-04-10.md` returned exit code `0`. |
| CheckBuild entity exists | ran-target | `test -f _shared/SpecOps/Entities/specs/checkbuild-skill-2026-03-03.md` returned exit code `0`. |
| Mixed Backfill dashboard exists | ran-target | `test -f _shared/SpecOps/Dashboards/mixed-backfill.md` returned exit code `0`. |
| Nebenkosten project board exists | ran-target | `test -f _shared/SpecOps/Dashboards/projects/nebenkostenabrechnung.md` returned exit code `0`. |
| NCG / CheckBuild project board exists | ran-target | `test -f _shared/SpecOps/Dashboards/projects/ncg-checkbuild.md` returned exit code `0`. |
| Required markers are visible | ran-target | `rg -n 'metadata_quality: inferred\|metadata_quality: conflict\|mixed-backfill-pilot\|Nebenkostenabrechnung\|NCG / CheckBuild' _shared/SpecOps` found the expected markers. |
| Dashboard links Mixed Backfill | ran-target | `rg -n 'Mixed Backfill\|Dashboards/mixed-backfill' _shared/SpecOps/Dashboard.md _shared/SpecOps/Dashboards/mixed-backfill.md` found the dashboard section and embed. |
| Project spec coverage | ran-target | `Nebenkostenabrechnung` has two spec entities; `NCG / CheckBuild` has one spec entity; total spec entity count is five. |
| Source files exist | ran-target | All three source specs exist; the BE2 final PDF output directory and CheckBuild watcher skill file also exist. |

Metadata-quality observations:

1. `nebenkostenabrechnung-pipeline-2026-03-14` uses `metadata_quality: inferred` because `status: accepted` is reconstructed from the Completed path and umbrella status text.
2. `nebenkostenabrechnung-be2-heiznebenkosten-sonderverteilung-2026-04-10` uses `metadata_quality: explicit` because the source says accepted and closed on 2026-04-10.
3. `checkbuild-skill-2026-03-03` uses `metadata_quality: conflict` because the header still says initial requirements while later sections document implementation and retro.

Verdict: READY for Obsidian review.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-04 | User | Mixed Backfill Pilot als naechsten SpecOps-Slice freigegeben. |
| 2026-05-04 | Codex | Child-Spec fuer Nebenkosten-Umbrella, Nebenkosten-Slice und CheckBuild-Spec erstellt. |
| 2026-05-04 | Codex | Mixed Backfill Entities, Dashboards, Projektboards und Backlog-Verknuepfung umgesetzt und verifiziert. |

SessionId: codex-desktop-current-thread
