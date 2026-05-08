# TC2: Single Child Slice Delivery & Next Child Handoff

## Ziel

Pruefen, dass eine Delivery-Session genau einen implementation-ready Child umsetzt, aus einem frischen Handoff startet, nur in einem Temp-Repo arbeitet und den naechsten Child nicht automatisch freigibt.

## Fixture Setup

- Source Fixtures: DWT-S3 Output Bundles unter `tests/docworkflow-agent-delivery/l2/single-child-closeout/fixtures/`.
- DWT-S5 Runtime Fixtures: synthetisches Repo und L3 Kontrollfixtures unter `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/fixtures/`.
- Test Fixture: isolierte Temp-Kopie unter `/tmp/docworkflow-agent-delivery-l2-single-child-closeout.*`.
- Temp-Normalisierung: `__RUN_DIR__` wird beim Validatorlauf auf den isolierten Run-Ordner abgebildet; Original-Repos bleiben read-only.
- Negative Fixtures: stale DWT-S3 Handoff, out-of-workspace write attempt und DWT-S5 auto-release attempt.

## Workflow Action

Agentischer Dry-Run:

1. `spec-change-delivery` liest Child Index, Handoff, Child Spec und Parent Spec.
2. Der S3-Hardening-Verdict wird validiert.
3. Allowed Write-Set und Target Repository werden vor jedem Runtime-Edit geprueft.
4. Implementation laeuft nur in `<fixture>/target-repo`.
5. Verification laeuft vollstaendig, falls Runtime-Fixture vorhanden ist.
6. `spec-closeout` synchronisiert Parent Coverage, Child Index, Backlog/Re-entry, Evidence, OpenSpec-Status und naechstes Handoff.
7. DWT-S5 bleibt blocked, bis DWT-S5 einen eigenen Child Spec, Handoff und Validatornachweis hat.

Automatisierter Harness-Anteil:

```sh
tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh tc2
tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh all
tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh preflight
tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh all
```

## Assertions

| Assertion | Automatisierung | Erwartung |
|---|---:|---|
| S3 Delivery-Gate prueft Child Index/Handoff/Verdict. | ja | S3 besteht den Readiness-Gate nur in der normalisierten Temp-Kopie. |
| Runtime-/Edit-artiger Output nutzt nur Temp-Workspace oder Artifact Bundle. | ja | Handoff Target Repository liegt unter dem isolierten Run-Ordner; Original-Repo-Pfade sind als Write Targets verboten. |
| Allowed Write-Set ist enforceable. | ja | Write-Set nennt konkrete Pfade/Globs und keine unsicheren Begriffe wie `TBD`, `likely`, `etc`. |
| Docker, Deployment und Credential Copy sind verboten. | ja | Telemetry und Kickoff/Closeout Bundles duerfen keine forbidden command classes als erlaubte Aktion enthalten. |
| Stale Handoff blockiert. | ja | Negative Fixture ohne Target Repository faellt durch den Gate. |
| Fehlendes Target Repository blockiert. | ja | Validator/Fallback meldet stale/missing Target Repository als Fehler. |
| DWT-S5 wird nicht automatisch implementiert. | ja | DWT-S5 bleibt `blocked_by_dependency`; `spec-change-delivery` wird nicht als Next Action freigegeben. |
| Blocked Agent Path bleibt ehrlich. | ja | Fallback Artifact Mode kann Deterministik beweisen, meldet aber `overall_agent_proof_status: blocked`. |
| `spec-closeout` synchronisiert Parent/Index/Evidence/Handoff. | ja | Synthetic Closeout Fixture bewahrt Parent Coverage, Evidence Links und OpenSpec Ledger State. |
| DWT-S5 arbeitet nur in generated synthetic temp repos. | ja | L3A materialisiert `target-repos/dwt-s5-synthetic-runtime-repo/` aus source-controlled Fixtures und validiert Source-/Target-Provenance. |
| DWT-S5 lokale Runtime bleibt im Temp-Repo. | ja | L3C fuehrt die lokale Gate-Command im generated temp repo aus und schreibt cwd/exit status als Evidence. |
| DWT-S5 container/harness Proof bleibt ehrlich. | ja | L3D akzeptiert pass nur mit target harness evidence oder meldet `blocked_runtime`; blocked runtime darf nicht als accepted L3 pass erscheinen. |

## Evidence

Der L0 Harness schreibt `evidence/tc2-contract-checks.txt` in die Temp-Fixture. Der DWT-S3 L2 Harness schreibt `evidence/dwt-s3-l2-summary.json` plus per-case Assertion JSON in den isolierten Run-Ordner. Der DWT-S5 L3 Harness schreibt `evidence/dwt-s5-l3-summary.json`, `agent-run-manifest.json`, runtime gate logs und per-case Assertion JSON in den isolierten Run-Ordner; retained blocked-runtime evidence liegt unter `tests/docworkflow-agent-delivery/l3/runtime-temp-repo/evidence/2026-05-08-blocked-runtime/`.

## Cleanup

Ohne `--keep` loescht der Harness die Temp-Fixture beim Exit.
