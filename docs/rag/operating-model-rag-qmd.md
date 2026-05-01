# Operating Model: rag Default, qmd Optional

## Entscheid in einem Satz

Fuer DanielsVault ist `rag` die verbindliche Standardruntime fuer agentisches Retrieval; `qmd` ist ein optionaler Zusatz fuer Discovery-orientierte Markdown-Suche.

## Warum dieser Zuschnitt

1. Die akzeptierte RAG-Abnahme basiert auf dem `rag`-CLI-Contract, nicht auf globalem `qmd`.
2. `rag` liefert die benoetigten Workflow-Capabilities (`research-for-review`, `spec-closeout`) inkl. Eval-/Gate-Pfade.
3. `qmd` kann Recall und Ranked Discovery bei offenen Suchfragen verbessern, ist aber kein Betriebs-Blocker.

## Standardpfad (immer zuerst)

```bash
cd /Users/dh/Documents/DanielsVault/_shared/danielsvault-rag
export PATH="$PWD/.venv/bin:$PATH"
rag --version
rag runtime health
rag runtime smoke
```

## Optionaler qmd-Zusatz

Wenn du zusaetzliche Discovery-Faehigkeiten willst, kannst du `qmd` global installieren:

```bash
npm install -g @tobilu/qmd
qmd status
```

Wichtig: Fehlendes `qmd` ist kein Fehler fuer den Standardbetrieb, solange `rag` laeuft.

## Wann welches Tool

| Frage-/Aufgabentyp | Primar | Optional |
|---|---|---|
| Spec-nahe agentische Retrieval-Workflows | `rag workflow ...` | - |
| Strukturierte Fakten mit Filter (`record_type`, `setting_name`, IDs) | `rag retrieve structured` | - |
| Eval/Gates und reproduzierbare Runtime-Nachweise | `rag eval ...`, `rag runtime ...` | - |
| Breite Discovery in Markdown mit Query-Expansion/Reranking | - | `qmd query ...` |

## Empfohlener Agent-Flow

1. Runtime-Preflight auf `rag` ausfuehren.
2. Fachfrage ueber `rag retrieve ...` oder `rag workflow ...` bedienen.
3. Nur falls Discovery zu duenn ist: zusaetzlich `qmd` fuer breitere Kandidatensuche einsetzen.
4. Finale agentische Antwort weiterhin mit `rag`-Quellenpfaden absichern.

## Verifikation

Core-Gates (muessen immer gruen sein):

```bash
command -v rag
rag --version
rag runtime health
rag runtime smoke
```

Optionaler Add-on-Gate fuer `qmd` (nur bei installiertem Discovery-Zusatz):

```bash
command -v qmd
qmd --version
qmd status
```

Interpretation:

1. Wenn `qmd` nicht installiert ist, bleibt der Standardbetrieb trotzdem valide, solange Core-Gates gruen sind.
2. Wenn `qmd` installiert wird, sollten alle drei Add-on-Checks gruen sein.

## Session-Stabilitaet

Um `rag` in neuen Shell-Sessions sofort verfuegbar zu haben:

```bash
echo 'export PATH="/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/.venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Troubleshooting

1. `qmd: command not found`:
   - Kein Blocker. Mit `rag` normal weiterarbeiten.
2. `rag: command not found`:
   - In den Runtime-Ordner wechseln und `PATH` wie oben setzen.
3. `rag runtime smoke` nicht gruen:
   - Erst Runtime reparieren; `qmd` behebt keinen `rag`-Runtime-Fehler.
