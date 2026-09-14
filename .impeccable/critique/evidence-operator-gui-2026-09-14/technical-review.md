# Assessment B — technischer UX-Befund

Ziel: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs-operator-issue-03/microsoft-agent-framework-work-package-pilot/src/Wpcp.Api/wwwroot/operator`. Methode: isolierter Subagent `/root/ux_technical_evidence`; A-Befunde nicht gesehen. Detectorbefunde bis zum Parent-Signal nach Abschluss A zurückgehalten.

## Detector

Exakt ein Aufruf: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.codex/skills/impeccable/scripts/impeccable detect --json <absolutes Zielverzeichnis>`. Exit 2 (Befunde), vollständiges JSON: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/detector.json`.

**44 Meldungen: 40 warning, 4 advisory. 7 Regeln.** Es sind Meldungen zu Mustern/Elementen, keine 44 unabhängigen Usability-Defekte. 40 Meldungen liegen auf `index.html`, vier auf `operator.css`; kein JS-Dateibefund. Der Detector nennt für alle HTML-Befunde `line: 0` (keine auflösbare Quellzeile). Keine Quellzeile dafür erfinden.

| Regel | Anzahl | Detector-Ort |
|---|---:|---|
| undersized-ui-text | 24 | index.html:0 |
| tiny-text | 6 | index.html:0 |
| wide-tracking | 4 | index.html:0 |
| extreme-negative-tracking | 1 | index.html:0 |
| kicker-above-heading | 1 | index.html:0 |
| numbered-section-labels | 4 advisory | index.html:0 |
| side-tab | 4 | operator.css:628, 651, 654, 675 |

Einordnung / Fehlalarme:

- Die starke Größenhäufung ist im Browser bestätigt: Status, Repository/Issue, Zeitangaben, technische Disclosures und Kicker häufig 9–10 px; Mobil-Brand sogar 7 px. Relevant ist vor allem Funktions- und Kontexttext, nicht die Markenzeile. `tiny-text` überlappt teilweise dieselben typografischen Entscheidungen wie `undersized-ui-text`; nicht additiv als Einzelprobleme bewerten. Keine absolute WCAG-Schriftgrößen-Untergrenze behaupten.
- **4 `wide-tracking` sind Kontext-Fehlalarme:** Es handelt sich um kurze großgeschriebene Kicker/Meta-Labels, nicht laufenden Fließtext. Die Regel selbst reserviert weites Tracking für solche Labels. Die kleinen Schriftgrößen bleiben ein separater Befund.
- `extreme-negative-tracking` trifft das Wordmark (`-0.05em`), nicht Lesetext. Im Screenshot erkennbare Marke; kein belastbarer funktionaler Defekt daraus.
- `side-tab` ist kein automatischer UX-Fehler: die Borders kennzeichnen ausgewählten Versuch, Ergebnis, Fehler und Ergebniszusammenfassung. Die Bedeutung wird zusätzlich durch Text/State kommuniziert. Allenfalls visuelle Redundanz; kein pauschales Entfernen empfehlen.
- `numbered-section-labels` und `kicker-above-heading` sind Gestaltungsheuristiken. 01 Zugang und 01 Aufnahme sind alternative Zustände; der Quellscan zählt beide. Ziffern nicht als vier gleichzeitig sichtbare Schritte interpretieren.

## Browserbelege

Aktuelle Assets wurden unverändert direkt aus dem Worktree ausgeliefert, Daten stammen aus `openspec/changes/add-agent-framework-operator-gui/evidence/issue-03-readable/live-workflow.json` und den beiden `live-artifact-*.json`. Der Lauf ist `c8c55cd0-91bf-40f3-b685-f56b3e174a7e`. Die Submission wurde aus dem originalen `ImplementationRunStarted.payload.note` rekonstruiert und mit der aufgezeichneten runId verknüpft; Execution aus dem abschließenden State-Ereignis. Keine echten Agenten, Issues oder Credentials verwendet.

Eigener neuer Chrome-Tab: 823720564, temporäre lokale URL `http://127.0.0.1:5097/operator/`, Dummy-Eingabe `preview-only`. Alle POSTs vom Replayserver abgewiesen. Seitentitel und fixe Fußleiste kennzeichneten die Aufzeichnungswiedergabe. Native CUA-Screenshots/Interaktionen; read-only DOM-Messung. Eine fixe Replayleiste am unteren Rand gehört nicht zum Produkt und beeinflusst dessen normalen Dokumentfluss nicht.

### Wichtigste bestätigte Befunde

1. **[P1] Beobachtung ist tief unter Aufnahme und vollständigem Analysetext verborgen.** Bei 1440×1000 beginnt `#workflow` bei y=3019 px, gesamte Seite 4751 px. Bei 390×844 beginnt es bei y=5363,7 px, Gesamthöhe 7860 px. Das entspricht über sechs mobilen Viewports bis zur eigentlichen Run-/Sessionnavigation. Die Übersicht zeigt währenddessen nur „Gestartet“. Das ist ein direkt gemessener Weg zum Beobachtungsziel, kein bloßes Stilurteil. Eine Auswahl-/Run-Ansicht sollte Workflow und Ergebnis in den ersten Bildschirm bringen; lange Quelle/13 Erkenntnisse nachgeordnet aufklappen.
2. **[P2] Kleine Funktionsschrift und ein knapp unterschrittener Textkontrast.** `.row-source` und die Zeitangabe in `.row-bottom` sind 10 px (`operator.css:315`, `:320`). Im ausgewählten Eintrag beträgt `#62756a` auf `#eef4e9` **4,39:1**, knapp unter 4,5:1 für normalen Text. Andere geprüfte Kombinationen bestehen: derselbe Muted-Ton auf Weiß 4,92:1; Ergebnis-Kicker auf `#f2f7eb` 4,51:1; Ergebnistext 10,91:1; grüner Status 6,78:1; grüne Aktion auf Weiß 7,63:1. Kein pauschaler Kontrastfehler für die gesamte Oberfläche.
3. **[P2] Mobile Schrittübersicht schneidet den ausgewählten Agentenschritt an.** Bei 390 px ist der Graph 308 px breit, Inhalt 406 px; `scrollLeft=0`. Der ausgewählte zweite Schritt beginnt bei x=271 px und ist im Screenshot rechts abgeschnitten. Die Seite selbst hat keinen horizontalen Überlauf (390/390); das Problem ist der eigene horizontale Graph ohne sichtbaren Schritt-/Scrollhinweis und ohne automatisches Sichtbarmachen der Auswahl. CSS `operator.css:678`. Inline-Hinweis „Wähle links“ passt außerdem nicht zur mobilen Anordnung oberhalb des Inspektors.
4. **[P2] Tastaturfokus verschwindet nach Schrittauswahl.** `Gesamten Run zeigen` → Tab fokussiert den ersten Versuch sichtbar; Enter wählt ihn korrekt aus, setzt den Fokus durch das Neurendern aber auf BODY. Erst ein weiteres Tab fokussiert den neu erzeugten ersten Versuch. Ursache in `workflow-view.js:38` (`graph.replaceChildren`) und `:86` (`select` rendert Graph neu). Nicht als vollständige Keyboard-Blockade bewerten: Auswahl funktioniert, Fokus sollte jedoch am gewählten Knoten bleiben oder gezielt in den Inspektor wechseln.
5. **[P2] Kleine Ziele erschweren mobile Detailbedienung.** Gemessene Höhen: „Run und Agentensession“ / Herkunft 15 px; Auftrag/Anweisung/Werkzeug-Disclosure 16,5 px; „Session und Herkunft“ 19,5 px; Erkenntnisse 21,6 px. Abmelden, Runbutton, „Gesamten Run zeigen“ und Artefaktbutton 32,5 px; Refresh 31,2×32,5 px; Filter 36,5 px. Primäre Aufnahme/Starten sind 46 px hoch, Versuche 91,5 px. 44 px ist hier ein Komfortziel; ohne vollständige Prüfung der Abstands-Ausnahmen keine pauschale WCAG-2.5.8-Verletzung behaupten.

### Was technisch funktioniert

- Login mit Dummy-Wert ließ sich per Tab/Enter öffnen. Sichtbarer Fokus am Versuch: `2px solid rgb(53,124,82)`, Offset 4 px (Desktopbild).
- Nativer Inhalte-Filter schaltet 5 lesbare Karten der gewählten Session auf **18 originale Sessionereignisse** um; alle 18 technischen Details vorhanden, initial geschlossen. Wechsel zurück auf Sessionverlauf ergibt wieder fünf Karten. „22 von 22“ bezeichnet den Run, nicht die Filtermenge.
- `requirements-analysis.json` öffnet lesbare Zusammenfassung, „Erkenntnisse · 13“ und geschlossenes „Originalinhalt“. Fokus wechselt zum `artifact-content`-Container. Kein horizontaler Dokumentüberlauf bei 390 px.
- Statusnamen und Texte ergänzen Farben. Labels und native Buttons/Disclosures sind im Accessibility Tree benannt. Keine beobachtete allgemeine Click-only-Blockade.
- Keine vom Browserlog gelieferten JavaScript-Errors/Warnings bei der begrenzten Prüfung. Das ersetzt keine Runtime-/Performanceprüfung.

## Grenzen / Run Notes für Parent

- README, relevante aktive OpenSpec-Scenario „Understand the observed work without decoding protocol data“, Evidence und Browser-Testseam gelesen. Keine Produktdateien geändert, daher kein neuer OpenSpec-Change.
- Worktree hatte vor Beginn nur untracked `.scratch/agent-framework-operator-gui/proof-20260914/`; nicht verändert.
- `impeccable context` war vom Parent ausgeführt; nicht wiederholt. Slug/Snapshot/Trend gehören zur Parent-Orchestrierung. `.impeccable/critique/ignore.md` war im Worktree nicht vorhanden.
- Browser-Overlay **nicht verfügbar**: dokumentiertes CUA `playwright.evaluate` ist read-only. Keine mutable Injection angeboten; kein Titel-/Script-Injektionsversuch über eine unzulässige Umgehung, kein Detector-Live-Server gestartet, keine Overlay-Existenz behaupten. Ersatzsignal sind einmaliger CLI-Scan, natives Rendering und read-only Computed-Style-/Geometriemessung. Replay-Fußleiste ist kein Detectoroverlay.
- Vorhandener fremder dotnet-Dienst auf 5090 lieferte für `/operator/` HTTP 404, blieb unangetastet.
- Replay-SSE liefert nur lokale Keepalives. „Live verbunden“ ist damit keine neue Live-Backend-Verifikation. Auth-/Revocation-/Reconnect-/Latency-/echte Fehler-/Multi-User-Semantik und Screenreader/200%-Zoom wurden nicht neu geprüft; dafür nur vorhandene Evidence lesen, keine neue Aussage behaupten.
- Ein temporärer Replayfehler bei Artefaktpfaden (ursprünglich SHA statt Artifact-ID im Dateinamen) wurde im Helfer korrigiert; erneutes Öffnen funktionierte. Dieser Fehler gehört nicht zum Produkt. Zwei Server-PIDs: 33471 (vor Korrektur) und 39285 (danach), beide per SIGTERM gestoppt und Nichtvorhandensein geprüft. Stopmethode war `kill <PID>`. A und Parent hatten vorher den Replay angesehen.
- Chrome-Tab geschlossen, temporäres 1440×1000-/390×844-Override zurückgesetzt. Previewprogramm, PID-Datei und Serverlog werden entfernt; Messwerte, Screenshots, Detector-JSON und dieser Bericht bleiben als Reviewbelege für Parent erhalten.
- Keine Testsuite gestartet. Eine einzige gebündelte Inspektionsrunde Desktop/Mobil; keine UI-Korrektur-/Polierrunde.

## Dateien

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/detector.json` — ungekürzte 44 Meldungen
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/desktop-metrics.json`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/mobile-metrics.json`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/desktop-workflow-focus.png`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/mobile-workflow-focus.png`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/.impeccable/critique/evidence-operator-gui-2026-09-14/mobile-artifact.png`
- Aktuelle echte Referenzbilder bleiben unter `openspec/changes/add-agent-framework-operator-gui/evidence/issue-03-readable/live-workflow-desktop.png` und `live-workflow-mobile.png`.

## Vollständige kompakte Detector-Liste

Die nachfolgenden Werte sind unveränderte Regel-/Orts-/Snippet-Angaben aus dem einzigen Detectoraufruf.

1. `extreme-negative-tracking` · `index.html:0` · warning · letter-spacing: -0.05em — "work packageDANIELSVAULT"

2. `undersized-ui-text` · `index.html:0` · warning · 7px functional text "DANIELSVAULT" (below 11px floor)

3. `tiny-text` · `index.html:0` · warning · 8px body text

4. `undersized-ui-text` · `index.html:0` · warning · 8px functional text "WORK PACKAGE CONTROL PLANE" (below 11px floor)

5. `wide-tracking` · `index.html:0` · warning · letter-spacing: 0.20em on body text

6. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Nicht verbunden" (below 11px floor)

7. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "01 / ZUGANG" (below 11px floor)

8. `tiny-text` · `index.html:0` · warning · 11px body text

9. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "01 / AUFNAHME" (below 11px floor)

10. `tiny-text` · `index.html:0` · warning · 11px body text

11. `undersized-ui-text` · `index.html:0` · warning · 9px functional text "02 / ÜBERSICHT" (below 11px floor)

12. `undersized-ui-text` · `index.html:0` · warning · 9px functional text "03 / BEOBACHTUNG" (below 11px floor)

13. `undersized-ui-text` · `index.html:0` · warning · 8px functional text "GITHUB ALS QUELLE" (below 10px floor)

14. `wide-tracking` · `index.html:0` · warning · letter-spacing: 0.15em on body text

15. `undersized-ui-text` · `index.html:0` · warning · 8px functional text "Inhalt · Herkunft · gespeicherte Fassung" (below 10px floor)

16. `tiny-text` · `index.html:0` · warning · 8px body text

17. `undersized-ui-text` · `index.html:0` · warning · 8px functional text "GESPEICHERTE ANFORDERUNGEN" (below 11px floor)

18. `wide-tracking` · `index.html:0` · warning · letter-spacing: 0.20em on body text

19. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "● Aufgenommen" (below 11px floor)

20. `tiny-text` · `index.html:0` · warning · 10px body text

21. `wide-tracking` · `index.html:0` · warning · letter-spacing: 0.16em on body text

22. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Run-ID" (below 11px floor)

23. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Aktivität" (below 11px floor)

24. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Versuch" (below 11px floor)

25. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Session" (below 11px floor)

26. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Zielrepository" (below 11px floor)

27. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Quelle · GitHub" (below 11px floor)

28. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Aufgenommen am" (below 11px floor)

29. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Quellfassung vom" (below 11px floor)

30. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Anforderungs-ID" (below 11px floor)

31. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "GitHub Issue-ID" (below 11px floor)

32. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Aufgenommen durch" (below 11px floor)

33. `tiny-text` · `index.html:0` · warning · 10px body text

34. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "SHA-256 der gespeicherten Fassung" (below 11px floor)

35. `undersized-ui-text` · `index.html:0` · warning · 10px functional text "Redaktionsregel" (below 11px floor)

36. `kicker-above-heading` · `index.html:0` · warning · kicker "WORK PACKAGE CONTROL PLANE" above h1 "Anforderungen"

37. `numbered-section-labels` · `index.html:0` · advisory · tiny numbered label "01 / ZUGANG" beside h2 "Mit GitHub verbinden" (4 on page)

38. `numbered-section-labels` · `index.html:0` · advisory · tiny numbered label "01 / AUFNAHME" beside h2 "Anforderungen aufnehmen" (4 on page)

39. `numbered-section-labels` · `index.html:0` · advisory · tiny numbered label "02 / ÜBERSICHT" beside h2 "Gespeicherte Anforderungen 0" (4 on page)

40. `numbered-section-labels` · `index.html:0` · advisory · tiny numbered label "03 / BEOBACHTUNG" beside h2 "Workflow und Sessionverlauf" (4 on page)

41. `side-tab` · `operator.css:628` · warning · border-left:3px solid #89a78f

42. `side-tab` · `operator.css:651` · warning · border-left:3px solid var(--green)

43. `side-tab` · `operator.css:654` · warning · border-left:3px solid #a35b32

44. `side-tab` · `operator.css:675` · warning · border-left:3px solid var(--green)
