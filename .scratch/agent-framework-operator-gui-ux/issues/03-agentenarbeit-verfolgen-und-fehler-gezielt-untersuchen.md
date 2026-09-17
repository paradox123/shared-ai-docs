# 03: Agentenarbeit verfolgen und Fehler gezielt untersuchen

**What to build:** Ein Mensch wählt einen beobachteten Schritt aus, versteht die zugehörige Agentenarbeit anhand lesbarer Nachrichten und Werkzeugergebnisse und gelangt von einem gemeldeten Fehler direkt zum betroffenen Versuch und dessen vorhandenen Belegen.

**Blocked by:** UX-[01: Gemeinsame Run-Ansicht mit verlässlichem Status](01-gemeinsame-run-ansicht-mit-verlaesslichem-status.md).

**Status:** ready-for-agent

**Kontext:** UX-03; [Spezifikation und Designreferenz](../spec.md). UX-02 und UX-04 sind keine Blocker.

- [ ] Die Verlaufansicht bietet benannte Schritte mit dem beobachteten Zustand. Die Auswahl öffnet die zugeordneten Aufträge, beobachtbaren Nachrichten und Werkzeugergebnisse mit verfügbaren Dauer- und Fehlerangaben. Ein Aufnahmeschritt ohne Agentensession zeigt seine tatsächlichen gespeicherten Angaben und behauptet keine Agentenarbeit.
- [ ] Die normale Ansicht priorisiert lesbare Arbeitsergebnisse. „Alle Ereignisse“ und der Zugang zur gesamten Run History erhalten sämtliche gespeicherten Beobachtungen einschließlich ihrer Originaldetails und Zuordnung zu Aktivität, Versuch und Session. Filtern oder Aufklappen verliert keine Inhalte und umgeht keine bestehenden Zugriffs- oder Redaktionsregeln.
- [ ] Ein Fehlerhinweis bietet einen direkten Zugang zum passenden Versuch und seinen vorhandenen Beobachtungen. Falls keine Session oder kein weiterer Beleg existiert, nennt die Ansicht diese Grenze und zeigt den gespeicherten Fehler. Der Zugang startet weder eine neue Diagnose noch eine Wiederholung der Ausführung.
- [ ] Schrittauswahl, technische Aufklappbereiche und Tastaturfokus bleiben beim Anwählen und bei Live-Aktualisierungen erhalten, solange das ausgewählte Element noch existiert. Der mobile Verlauf stellt die auswählbaren Schritte vollständig innerhalb der verfügbaren Breite dar; ausgewählte Schritte werden nicht abgeschnitten.
- [ ] Nachladen, Live-Wiederaufnahme und erneutes Öffnen erhalten bestätigte Ereignispositionen, Reihenfolge und stabile Identitäten ohne doppelte Anzeige. Fehlende Inhalte und noch nicht abgeglichene Zustände bleiben sichtbar; ein Darstellungsfilter wird nicht als Nachweis vollständiger History ausgegeben.
- [ ] Reproduzierbare Checks belegen zunächst den Fokusverlust, den abgeschnittenen mobilen Schritt und den fehlenden Fehlerzugang. Verhaltenstests und Browsernachweise prüfen Schrittauswahl per Tastatur, eintreffende Ereignisse, Filterwechsel und den Fehlerzugang bei einem gespeicherten Run. Sichtbare Inhalte werden mit öffentlichen History-Antworten verglichen; Desktop und 390-Pixel-Mobilansicht sind Bestandteil der Abnahme.
