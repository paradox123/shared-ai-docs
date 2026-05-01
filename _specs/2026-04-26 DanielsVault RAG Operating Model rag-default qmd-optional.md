**Date:** 2026-04-26  
**Status:** 🔵 Implemented
**Scope:** Betriebsmodell fuer DanielsVault-Retrieval mit `rag` als Standardruntime und `qmd` als optionalem Discovery-Zusatz

---

## Kontext

In einzelnen Sessions entstand Widerspruch zwischen "RAG ist abgeschlossen" und "qmd ist nicht installiert".

Die Parent-/Child-RAG-Specs wurden auf einen stabilen `rag`-CLI-Contract abgenommen; `qmd` ist als moeglicher Backend-/Search-Zusatz zulaessig, aber nicht Pflicht fuer den Phase-1-Betrieb.

## Ziel

1. Betriebsentscheid fuer den Alltag explizit und auffindbar machen.
2. Session-Start ohne Mehrdeutigkeit (`rag` default, `qmd` optional) dokumentieren.
3. Nutzer und Agenten auf einen gemeinsamen, reproduzierbaren Ablauf fuer Retrieval fuehren.

## Non-Goals

1. Keine Aenderung am bestehenden Phase-1-CLI-Contract des `rag`-Runtimes.
2. Kein Zwang, `qmd` global zu installieren.
3. Keine Anpassung der gemeinsamen Workflow-Gates in `docs/doc-workflow.md`.

## Decision Freeze Pack

### Zielbild und Scope

DanielsVault-Retrieval nutzt im Standardbetrieb die bestehende `rag`-Runtime. `qmd` wird als optionales Discovery-Werkzeug dokumentiert, ohne den `rag`-Contract zu ersetzen.

### Betroffene Repositories

1. `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
2. `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag` (nur als referenzierte Runtime, keine Codeaenderung in diesem Change)

### Secret-/Config-Contract

Keine neuen Secrets. Optionaler Shell-PATH-Hinweis fuer lokale Session-Stabilitaet.

### Datenmigration/Fallback

Kein Datenmigrationsbedarf. Fallback bei fehlendem `qmd`: Betrieb laeuft vollstaendig ueber `rag`.

### Sicherheits-/Exposure-Entscheidungen

Keine neuen Exposures; rein lokale CLI- und Dokumentationsaenderung.

### Abnahmekriterien (Go/No-Go)

Go:
1. Betriebsmodell ist in `docs/rag/` dokumentiert.
2. RAG-Doku-Einstiegspunkte verlinken auf das Betriebsmodell.
3. Doku macht klar: `qmd`-Fehlen blockiert den `rag`-Betrieb nicht.
4. Optionaler `qmd`-Add-on-Gate ist als separater Verifikationspfad dokumentiert.

No-Go:
1. Betriebsentscheidung bleibt implizit oder widerspruechlich.
2. Startanleitung priorisiert weiterhin unklare Toolwahl.

### Nachweisformat

1. Markdown-Artefakte in `docs/rag/` und `_specs/`.
2. Verifikationskommandos mit Exit-Code `0` fuer `rag`-Runtime-Preflight.

## Umsetzung

1. Neue Betriebsdoku: `docs/rag/operating-model-rag-qmd.md`.
2. Neue Spezifikation fuer den Change unter `_specs/`.
3. Link-Integration in:
   - `docs/rag/README.md`
   - `docs/rag/index.md`

## Verifikationskommandos

Core-Gates (verpflichtend):

1. `command -v rag`
2. `rag --version`
3. `rag runtime health`
4. `rag runtime smoke`
5. `test -f /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/operating-model-rag-qmd.md`
6. `rg -n "Operating Model: rag Default, qmd Optional" /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/README.md /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/index.md`

Optionaler Add-on-Gate (`qmd`, nur wenn Discovery-Zusatz gewuenscht):

7. `command -v qmd`
8. `qmd --version`
9. `qmd status`

Bewertung:

1. Core-Gates muessen fuer DoD gruen sein.
2. `qmd`-Gate darf als `not-installed` dokumentiert sein, ohne den Change zu blockieren.
3. Wenn `qmd` installiert wird, muessen auch die Add-on-Checks gruen sein.

## Definition-of-Done Bezug

Dieser Change folgt den gemeinsamen Gates in `docs/doc-workflow.md`:

1. Scope/Non-Goals/Decision Freeze sind explizit dokumentiert.
2. Verifikationskommandos sind vorab definiert und nach Umsetzung ausfuehrbar.
3. Artefakte sind synchron (Spec + Doku + Indexseiten).

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-26 | User | Entscheidung angefragt, `rag` als Standard und `qmd` optional verbindlich zu dokumentieren. |
| 2026-04-26 | Codex | Spec erstellt, Operating Model dokumentiert, RAG-Indexseiten verlinkt und Status auf `🔵 Implemented` gesetzt. |
| 2026-04-26 | User + Codex | Explizite `qmd`-Verifikationen als optionaler Add-on-Gate ergaenzt und Gate-Bewertung praezisiert. |
| 2026-04-26 | Codex | Scope Contract im Direct-Mode fuer die Delivery-Ausfuehrung fixiert und Status auf `🟠 Plan` gesetzt. |
| 2026-04-26 | Codex | Vollstaendige Verifikationsstrecke inkl. `qmd`-Gate und `check-build-watcher` ausgefuehrt, Evidence-Datei erzeugt und Status auf `🔵 Implemented` gesetzt. |

SessionId: codex-desktop-current-thread
