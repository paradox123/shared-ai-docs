# Release-Ticket 02: lokale Aktivierung mit Rückfall

Stand: 13.09.2026. Zielbranch `codex/update-llm-wiki-releases`, isolierter Worktree `../shared-ai-docs-update-llm-wiki-releases`. Review-Basis `1cf3892a8641bc02510a349e64f27cbd5aa02388`; erste Implementierung `1f68c57926b0c0b91782d86e374428e8449d2139`. Unabhängige Änderungen und die produktive Pflege im ursprünglichen Checkout bleiben außerhalb dieses Auftrags.

## Vertrag und Nachweis

`wiki update --candidate PATH` ist der öffentliche Übernahmeaufruf. Er benötigt alle erfolgreichen Pflichtprüfungen und einen unveränderten vollständigen Runtime-Baum. Dateien einschließlich installierter Abhängigkeiten und Node, ausführbare Rechte und Symlink-Ziele sind gebunden; externe Runtime-Symlinks werden abgewiesen. Leere Verzeichnisse sowie Git-Verwaltungsdaten und Python-Bytecode-Caches gehören nicht zur ausführbaren Inhaltsidentität. Der Compiler-Commit wird zusätzlich durch die tatsächlich gestartete Runtime mit Git geprüft. Berichte ohne vollständige Bindung erfordern erneute Qualifikation.

Die Übernahme kopiert den Kandidaten in eine getrennte Runtime, prüft die Kopie, schaltet die Auswahl vorläufig um und bestätigt die tatsächlich geladene Identität. Der öffentliche CLI-Funktionsnachweis übernimmt künstliche Wissensseiten und eine gespeicherte Antwort der vorherigen Runtime. Query prüft Originalherkunft; No-op-Pflege erhält Texte und Zustand bytegleich. Eine kontrollierte Quellenkorrektur wird mit dem bisherigen Compilerzustand weitergepflegt und erreicht die gespeicherte Antwort. Erst danach wird die Auswahl endgültig.

| Anforderung | Beobachtetes Verhalten | Beleg |
| --- | --- | --- |
| Nur geprüfte unveränderte Kandidaten | Fehlende/ausstehende Prüfungen blockieren auch bei gesetztem Eignungsflag. Änderungen an Wrapper, Build, beiden Dependency-Bäumen oder Node werden abgewiesen; der aktive Snapshot bleibt erhalten. Auch der Installer selbst weist explizite Kandidatenziele innerhalb aktiver/aufbewahrter Snapshots ab. | Öffentliche `test_release_update.py`-Prozesstests; vollständige Runtime-Prüfinventare im Kandidaten |
| Übernahme ohne neue Freigabe | Der öffentliche Aufruf führt Kopie, Umschaltung und Funktionsprüfung ohne weiteren Bedienerschritt aus. | Aktivierungsbericht und Prozess-Exit |
| Tatsächlich aktive Identität und Funktion | Status meldet ausgewählten Wrapper, eigenen Node und exakten Compiler-Commit; die Funktionsprüfung liest frühere gespeicherte Erkenntnisse mit aktueller Herkunft. | `release-status`, `probe.identity`, `probe.originals` |
| Wissen und Zustand erhalten | No-op-Pflege lässt frühere Fixture-Seiten und Zustand bytegleich; Quellenkorrektur wird in gespeicherte Antwort übernommen. Produktionskonfiguration wird nie an die Aktivierung übergeben. | `savedKnowledgePreserved`, `updatedKnowledgeVerified` |
| Fehler und Rückfall | Ein gezielter QMD-Transportfehler tritt erst beim Funktionsaufruf der neuen Runtime auf; Update liefert Exit 1 und wieder den vorherigen aktiven Einstieg. Vorläufige Auswahl nach Abbruch wird vor normaler Nutzung zurückgesetzt. | Fehlerprobe und Wiederherstellungstest |
| No-op und Serialisierung | Zweiter unveränderter Kandidatenaufruf behält Auswahlbytes und Runtime-Pfad. Ein laufender Wiki-Aufruf sperrt ein konkurrierendes Update sichtbar als busy. | No-op-/Sperrtests |

## TDD und Grenzen

Beobachtete Rot→Grün-Slices: ungeprüfter Kandidat statt unbekannter Operation; tatsächliche Aktivierung statt fehlender Übernahme; Busy-Schutz statt überlappender Updates; Wiederherstellung einer unterbrochenen vorläufigen Auswahl; Installations-No-op statt erneuter Aktivierung; Nachpflege früheren Compilerzustands statt ausschließlich frischem Fixture/No-op. Der zunächst zu kurze Qualifikations-Testtimeout wurde als Harnessfehler behandelt, nicht als Verhaltens-Rot; folgende Qualifikations-Prozesse erhalten eine eigene Prozessgruppe und ausreichendes Zeitbudget.

GitHub/Git/npm, Compiler, Node und QMD sind real. Der Modellprovider antwortet deterministisch auf künstliche, begrenzte Quellen. Keine Produktivmigration, kein Vollimport und kein Schedulerlauf werden behauptet. Ein inkompatibler Datenvertrag wird abgewiesen; eine künftig notwendige Produktivmigration benötigt zuerst eine gesicherte, rücksetzbare Implementierung. Die Aktivierung ist je Installation/Checkout lokal. Der Scheduler verwendet weiterhin seinen bestehenden Produktionseinstieg; der Feature-Worktree kann unabhängig aktiviert werden.

## Reale Mac-Abnahme

Der für die Fehler-/Erfolgs-/No-op-Abnahme aus `c6b69ba` vorbereitete Kandidat verwendet das reguläre GitHub-Release **v1.3.0**, Release-ID **386878086**, Commit **34ca1df97b3e60a6700048c48c7cf70c92a9bfdb**. Build, Typecheck, **59 Upstream-Tests**, **29 Integrationstests** und abschließende Inhaltsbindung bestanden. Vollständiger Runtime-Hash: `b5b556529fa786641dc1b1b7f2ec73a39875c87d4c07e902f9e6deaffd187249`.

`python3 test/accept-activation.py --candidate .runtime/release-02-reviewed --protected-config <bestehende-common.json> --scheduler <bestehende-automation.toml>` ruft den öffentlichen Einstieg einer separaten Mac-Installation auf. Die [maschinenlesbare Abnahme](release-activation-02-results.json) enthält Qualifikation, Fehlerbericht, Aktivierung, tatsächlichen Status und No-op sowie Vorher-/Nachher-Prüfsummen. Vollständige lokale Artefakte bleiben unter den dort genannten `.runtime/`-Pfaden erhalten.

Beobachtete Reihenfolge: **failed → activated → noop**. Der Fehler entsteht gezielt erst in der QMD-Prozessgrenze der neuen Runtime; der vorherige Einstieg ist danach wieder aktiv. Die erfolgreiche Aktivierung weist erhaltene Seiten/Synthese, unveränderten Zustand beim No-op und erfolgreiche Aktualisierung der gespeicherten Antwort nach Quellenkorrektur aus. `release-status` stimmt mit dem tatsächlich ausgewählten Snapshot und dessen eigener Node-Binary überein. Die Wiederholung lässt den Auswahlzustand bytegleich.

Die drei geschützten Pfade — produktive `common.json`, deren vollständiges Wiki-Ausgabeverzeichnis einschließlich Zustand sowie die bestehende Schedulerdefinition — sind vor und nach allen drei Aufrufen hashgleich. Keine produktive Konfiguration wird an einen Update- oder Probeprozess übergeben.

## Review und Abschlussprüfung

Das [zweiachsige Review](release-activation-02-review.md) fand keine Standards-Verstöße und eine fehlende Identitätsangabe nach Abbruchwiederherstellung. Diese wurde Rot→Grün korrigiert und unabhängig nachgeprüft; keine Findings bleiben offen. Der Refactoring-Pass teilte die Runtime-Identitätsprüfung zwischen Status/Preflight und führte Fixture-Aufbau sowie kontrollierte Fehlertransporte in gemeinsamen Testhelfern zusammen. Die funktionalen Grenzen blieben erhalten.

Die vollständige Abschlussprüfung bestand: Typecheck, **61 CLI-Tests**, **59 Upstream-Tests**, **acht Wartungshelfer-Tests** und **21 Installer-/Aktivierungstests** (einschließlich des nachträglich ergänzten Installationsschutzes). [Vollständiges Protokoll](release-activation-02-verification.txt). Python-Syntax, `git diff --check` und `openspec validate operate-contextual-llm-wiki --strict` sind ebenfalls grün.

Die Fachtests verwenden den öffentlich qualifizierten Kandidaten aus der unabhängigen Abnahme; zusätzliche Qualifikation nach `2ae80c5` umfasst auch den endgültigen Installationsschutz. Der abschließende Einstieg im Feature-Worktree wurde aus diesem vollständigen Stand aktiviert und anschließend als No-op erneut aufgerufen.

## Tatsächlich aktiver Feature-Worktree

Der nach `2ae80c5` vollständig neu qualifizierte Kandidat `.runtime/release-02-delivery` bestand erneut Build, Typecheck, 59 Upstream- und 29 Integrationstests sowie Integrität. Sein Runtime-Hash lautet `7dd7bce47325240afef183e0c5442917a6c482a5a0c94ad6b0d67a9b6a01a9d8`. Der öffentliche `wiki`-Einstieg des Feature-Worktrees verwendet jetzt `.runtime/releases/16b85b9331034b73880395b5182f03e4/wrapper` mit eigener Node-Kopie. `wiki release-status` meldet v1.3.0 und den oben genannten exakten Compiler-Commit. Der nachfolgende identische Update-Aufruf meldet `noop` und dieselbe aktive Identität.

Die Ergebnisdatei enthält diesen Nachweis separat unter `deliveryQualification`, `worktreeActivation`, `worktreeStatus` und `worktreeNoop`. Eine erneute Prüfsumme nach der tatsächlichen Worktree-Aktivierung bestätigt die unveränderten produktiven Daten, Konfiguration und Schedulerdefinition (`worktreeProtectedUnchanged: true`).

Ticket 02 ist implementiert und verifiziert. Der Betriebs-Change bleibt wegen Release-Erkennung aus Ticket 03 und weiterer, hier ausgeklammerter Wissenspflegeaufgaben offen; er wird nicht archiviert.
