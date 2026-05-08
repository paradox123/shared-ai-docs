# TC1: Parent-First Orchestration & Child Hardening

## Ziel

Pruefen, dass ein grosser Parent-/Master-Spec-Start nicht direkt als Single-Session-Implementation behandelt wird. Der Workflow muss ueber `spec-orchestrator` und `child-spec-hardening` zu einem operationalen Child Index, Handoffs und einer Implementation-Readiness-Matrix fuehren.

## Fixture Setup

- Source Fixture: `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs`
- Test Fixture: Temp-Kopie unter `/tmp/docworkflow-agent-delivery.*`
- Originaldateien: read-only Quelle, keine Aenderung erlaubt.
- Runtime-Ziel: nur Temp-Repo-Stubs unter `<fixture>/target-repo`.

## Workflow Action

Agentischer Dry-Run:

1. Parent Spec lesen.
2. Spec Sizing Gate anwenden.
3. `spec-orchestrator` als naechsten Modus bestimmen.
4. Child Schnitt, Child Index, Coverage Matrix, Dependencies und Hardening Queue erzeugen oder validieren.
5. `child-spec-hardening` fuer hardenbare Children in Dependency-Reihenfolge anwenden.
6. Implementation-Readiness-Matrix ausgeben.

Automatisierter Harness-Anteil:

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh tc1
```

DWT-S1 ergaenzt dazu eine deterministic-only L1-Schicht:

```sh
tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh all
```

Diese L1-Schicht beweist nur maschinenpruefbare Vertragsregeln fuer Fixtures,
Provenance, Readiness-Blocker und S0-Limitation-Isolation. Sie ist kein
agentischer Orchestration-Dry-Run und keine L2-Ausfuehrung.

DWT-S2 ergaenzt die L2 Parent-first Output-Bundle-Schicht:

```sh
tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh all
```

Diese L2-Schicht prueft positive, negative, blocked, style and telemetry
Output-Bundles. Fallback-Artefaktmodus darf deterministische Contract Evidence
liefern, aber keine akzeptierte Agent-Proof ohne `agent_execution_status:
ran-target`.

## Assertions

| Assertion | Automatisierung | Erwartung |
|---|---:|---|
| Spec Sizing Gate ist kanonisch dokumentiert. | ja | `docs/doc-workflow.md` enthaelt `Spec Sizing Gate` und Parent/Child-Routing. |
| `spec-orchestrator` erzwingt operationalen Child Index. | ja | Skill-Contract nennt exakte Child-Index-Spalten und Handoff-Regeln. |
| Child Index hat exakte Mindestspalten. | ja | Header entspricht dem operationalen Contract. |
| Child IDs sind stabil. | ja | Rows fuer `S0` bis `S7` existieren. |
| S3 gilt nur mit hartem Verdict und Handoff als ready. | ja | `S3` besteht den Readiness-Gate in der Temp-Kopie. |
| S4-S7 werden nicht automatisch implementierbar. | ja | Rows bleiben `NEEDS HARDENING`, `NEEDS USER DECISION` oder blockiert. |
| Kein plausible Schnitt reicht fuer Readiness. | ja | nicht-ready Children haben kein implementation-allowing Verdict und keinen Delivery-Next-Action. |
| High-risk Verification Commands haben Rehearsal/Preflight/Blocking Contract. | teilweise | Contract prueft Preflight-/Docker-/Anti-Loop-Regeln; echte Rehearsal-Ausfuehrung bleibt Dry-Run. |
| Persistierte Handoffs und Child Index sind konsistent. | ja fuer S3 | S3-Index zeigt auf persistiertes Handoff; Child/Verdict/Write-Set/Target Repo stimmen. |
| Coverage Matrix ist semantisch vollstaendig. | Dry-Run | Agent muss Coverage gegen Parent-Anforderungen bewerten. |
| Parent-only L1-Start ist frei von Child-Artefakten. | ja in DWT-S1 | `DWT-S1-L1A` besteht nur ohne Child Index, Child Specs und Handoffs im Start-State. |
| Generierte Child-Control-Artefakte haben Provenance. | ja in DWT-S1 | `DWT-S1-L1B` verlangt Source-ID/Hash und Output-Pfad. |
| Thin Child und fehlendes High-risk-Rehearsal blockieren Readiness. | ja in DWT-S1 | `DWT-S1-L1C`/`DWT-S1-L1D` melden erwartete Blocker statt Delivery-Freigabe. |
| Hidden Normalization und S0-Agent-Abhaengigkeiten bleiben verboten. | ja in DWT-S1 | `DWT-S1-L1E` scheitert erwartungsgemaess; `DWT-S1-L1F` bleibt ohne Promptfoo/Codex/Auth/npm. |
| Oversized Parent wird nicht direkt implementiert. | ja in DWT-S2 | `DWT-S2-L2A` blockiert Direct-Implementation-, Docker-, Deployment-, Credential- und Original-Repo-Aktionen. |
| Parent-first Output erzeugt Child Control Surface. | ja in DWT-S2 | `DWT-S2-L2B` verlangt Child Specs, exakten Child Index, Coverage Matrix, Dependencies und Hardening Queue. |
| Thin Child kann nicht implementation-ready werden. | ja in DWT-S2 | `DWT-S2-L2C` erkennt fehlenden Handoff, konkrete Write-Set- und Validator-Evidence. |
| Genau ein Leading Next Child State ist gueltig. | ja in DWT-S2 | `DWT-S2-L2D` erlaubt `implementation_ready` nur mit Handoff und Validator Evidence. |
| Blocked Agent Path wird nicht als Pass akzeptiert. | ja in DWT-S2 | `DWT-S2-L2E` bleibt `blocked`, wenn Promptfoo/Codex nicht als `ran-target` lief. |
| L2 Output folgt Summary-/Telemetry-/Style-Vertrag. | ja in DWT-S2 | `DWT-S2-L2F` prueft DWT-S4-kompatible Felder und haelt DWT-S3/DWT-S5 blockiert/geplant. |

## Evidence

Der L0-Harness schreibt `evidence/tc1-contract-checks.txt` in die Temp-Fixture.
Der DWT-S1-L1-Harness schreibt `evidence/l1-summary.json` in seinen isolierten
L1-Run-Ordner.
Der DWT-S2-L2-Harness schreibt `evidence/dwt-s2-l2-summary.json` in seinen
isolierten L2-Run-Ordner.

## Cleanup

Ohne `--keep` loescht der Harness die Temp-Fixture beim Exit.
