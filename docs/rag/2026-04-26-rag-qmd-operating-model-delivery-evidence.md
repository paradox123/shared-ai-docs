# Delivery Evidence: RAG Operating Model (`rag` default, `qmd` optional)

**Date:** 2026-04-26  
**Mode:** `direct` (kein OpenSpec-Change)

## Scope Summary

Implementierter Change:
1. Betriebsmodell-Doku fuer `rag` als Standard und `qmd` als optionalen Add-on-Gate.
2. Link-Integration in RAG-Indexseiten.
3. Vollstaendige Verifikation der in der Spec gelisteten Commands.
4. Zusatznachweis fuer `check-build-watcher` im NCG-Backend.

Nicht implementiert:
1. Keine Runtime-Codeaenderungen in `danielsvault-rag`.
2. Keine weiteren Refactorings ausserhalb des dokumentierten Changes.

## Verification Checklist (Spec Commands)

Status-Legende: `planned`, `ran-target`, `ran-rehearsal`, `failed`, `blocked`

| # | Command | Status | Exit | Evidence (Kurz) |
|---|---|---|---|---|
| 1 | `command -v rag` | `ran-target` | `0` | `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/.venv/bin/rag` |
| 2 | `rag --version` | `ran-target` | `0` | `rag 0.1.0` |
| 3 | `rag runtime health` | `ran-target` | `0` | JSON `status: ok` |
| 4 | `rag runtime smoke` | `ran-target` | `0` | JSON `status: ok`, `semantic_hits: 3`, `facts: 3` |
| 5 | `test -f /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/operating-model-rag-qmd.md` | `ran-target` | `0` | Datei vorhanden (`ok`) |
| 6 | `rg -n "Operating Model: rag Default, qmd Optional" ...README.md ...index.md` | `ran-target` | `0` | Treffer in beiden Dateien |
| 7 | `command -v qmd` | `ran-target` | `0` | `/opt/homebrew/bin/qmd` |
| 8 | `qmd --version` | `ran-target` | `0` | `qmd 2.1.0 (125c041acb)` |
| 9 | `qmd status` | `ran-target` | `0` | QMD Status ausgegeben; aktuell keine Collections indexiert |

## Additional Required Verification (User Request)

| Check | Status | Exit | Evidence (Kurz) |
|---|---|---|---|
| `cd /Users/dh/Documents/Dev/NCG/ncg-backend/backend/sources && dotnet run tests/check-build.local.watch.cs -- --show-state` | `ran-target` | `0` | Watcher-JSON mit `isArmed: true`, `branch: develop`, `projectId: 4` |

Hinweis:
Watcher-/Build-Status ist Pipeline-Health-Evidenz, keine fachliche Endpoint-/Businessflow-Validierung.

## Acceptance Coverage

1. Betriebsmodell ist dokumentiert: `pass`
2. RAG-Doku-Einstiegspunkte verlinken auf Betriebsmodell: `pass`
3. `qmd`-Gate explizit verifiziert: `pass`
4. Runtime-Validierung (`rag` health/smoke): `pass`

## Changed Artifacts

1. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-26 DanielsVault RAG Operating Model rag-default qmd-optional.md`
2. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/operating-model-rag-qmd.md`
3. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/README.md`
4. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/index.md`
5. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/2026-04-26-rag-qmd-operating-model-delivery-evidence.md`
