# TC2: Single Child Slice Delivery & Next Child Handoff

## Ziel

Pruefen, dass eine Delivery-Session genau einen implementation-ready Child umsetzt, aus einem frischen Handoff startet, nur in einem Temp-Repo arbeitet und den naechsten Child nicht automatisch freigibt.

## Fixture Setup

- Source Fixture: S3-Child, Child Index und S3-Handoff aus `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs`.
- Test Fixture: Temp-Kopie unter `/tmp/docworkflow-agent-delivery.*`.
- Temp-Normalisierung: Das kopierte S3-Handoff erhaelt `Target Repository / Working Directory: <fixture>/target-repo` und absolute Verification-Pfade werden auf diese Temp-Kopie umgebogen.
- Negative Fixture: Ein stale S3-Handoff ohne Target Repository wird unter `<fixture>/negative/stale-handoffs/` erzeugt.

## Workflow Action

Agentischer Dry-Run:

1. `spec-change-delivery` liest Child Index, Handoff, Child Spec und Parent Spec.
2. Der S3-Hardening-Verdict wird validiert.
3. Allowed Write-Set und Target Repository werden vor jedem Runtime-Edit geprueft.
4. Implementation laeuft nur in `<fixture>/target-repo`.
5. Verification laeuft vollstaendig, falls Runtime-Fixture vorhanden ist.
6. `spec-closeout` synchronisiert Parent Coverage, Child Index, Backlog/Re-entry, Evidence, OpenSpec-Status und naechstes Handoff.
7. S4 wird nur als naechster Hardening-Kandidat behandelt, solange S4 nicht implementation-ready ist.

Automatisierter Harness-Anteil:

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh tc2
```

## Assertions

| Assertion | Automatisierung | Erwartung |
|---|---:|---|
| S3 Delivery-Gate prueft Child Index/Handoff/Verdict. | ja | S3 besteht den Readiness-Gate nur in der normalisierten Temp-Kopie. |
| Runtime-Implementation nutzt nur Temp-Repo. | ja | Handoff Target Repository liegt unter `<fixture>/target-repo`; kopierte Handoff-Commands enthalten keine Original-Repo-Pfade. |
| Allowed Write-Set ist enforceable. | ja | Write-Set nennt konkrete Pfade/Globs und keine unsicheren Begriffe wie `TBD`, `likely`, `etc`. |
| Lokale und Docker-/Harness-Gates sind verpflichtend dokumentiert. | ja | Handoff/Child Spec nennen `dotnet`, lokalen Harness, Docker build/run und Secret-Assertions. |
| Stale Handoff blockiert. | ja | Negative Fixture ohne Target Repository faellt durch den Gate. |
| Fehlendes Target Repository blockiert. | ja | Validator/Fallback meldet stale/missing Target Repository als Fehler. |
| S4 wird nicht automatisch implementiert. | ja | S4 bleibt `NEEDS HARDENING`; `spec-change-delivery` wird nicht als Next Action freigegeben. |
| Vollstaendige Runtime Verification laeuft. | Dry-Run | Ohne echte Temp-Repo-Implementation bleiben Commands geplant, nicht als `ran-target` gewertet. |
| `spec-closeout` synchronisiert Parent/Index/Evidence/Handoff. | Dry-Run | Contract ist dokumentiert; echte Sync-Pruefung braucht eine ausgefuehrte S3-Delivery. |

## Evidence

Der Harness schreibt `evidence/tc2-contract-checks.txt` in die Temp-Fixture.

## Cleanup

Ohne `--keep` loescht der Harness die Temp-Fixture beim Exit.
