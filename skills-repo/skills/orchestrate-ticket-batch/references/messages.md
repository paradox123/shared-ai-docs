# Messages and handoff contracts

Compose readable messages from these templates; replace every bracketed field before sending. Omit optional fields that do not exist. Use actual original user instructions as authorization evidence, never fabricate quotations or call a coordinator message a direct user message.

## First worker assignment

```text
[$implement]([resolved absolute implement SKILL.md path]) Implementiere [ticket URL] vollständig. Benutze OpenSpec gemäß Implement-Skill und Repository-Policy; dokumentiere bei Verzicht die konkrete Begründung.

Dies ist die dedizierte Umsetzung für [ticket] im sequenziellen Batch [batch scope]. Der Nutzer hat diesen Batch mit dem Workflow Implementierung → kritische Verifikation → Abnahme → Commit/Push/Merge beauftragt. Quelle: [original user request/task ID and faithful scope]. Diese Herkunft dokumentiert den Auftrag; tatsächliche Tool-Berechtigungen bleiben maßgeblich.

Prüfe Git-Root, Branch/detached state, Status, vorhandene Vorarbeiten und aktuellen Remote-Zielstand. Repository [root], Zielbranch [target], letzter bestätigter Remote-Stand [SHA]. Verwende [resolved environment: isolierter Worktree oder ausdrücklich gewählter Checkout] und [confirmed branch instruction, respecting any explicit user branch; otherwise a new codex/ branch]. Bewahre fremde Änderungen.

Lies AGENTS.md, README, Ticket einschließlich relevanter Kommentare sowie zugehörige PRD/ADRs. Falls vorhanden: [prototype reference] ist ausschließlich visuelle Inspiration; daraus keine neuen Anforderungen, Zustände oder Pflichtschritte ableiten und keine Demo-Logik übernehmen.

Wende den genannten Implement-Skill an. Er entscheidet über aktiven OpenSpec-Change, repo-lokalen propose/apply-Workflow oder CLI-Fallback. Prüfe Verhalten durch öffentliche Schnittstellen mit TDD soweit sinnvoll, relevante Backend-/Frontend-Checks und abschließend code-review. Nutze isolierte synthetische Daten für Nachweise.

Liefere zunächst ein abnahmebereites Ergebnis: echte Screenshots der laufenden Anwendung oder verständliche Darstellungen tatsächlich gemessener Ergebnisse, absolute Artefaktpfade, Soll/Ist-Zuordnung zu Akzeptanzkriterien, Test-/Reviewbefunde, Grenzen und Identität des geprüften Standes (Commit oder Manifest). Eine bloße Liste grüner Tests genügt nicht.

Noch nicht committen, pushen, mergen, das Ticket schließen oder OpenSpec archivieren. Warte auf die separate kritische Verifikation und danach auf „Akzeptiert“ durch [coordinator task ID]. Der Batchauftrag umfasst die anschließende Lieferung; die Abnahme bestimmt deren Zeitpunkt. Melde technische Freigabeablehnungen mit ihrer tatsächlichen Ursache.

Falls die eigene echte threadId im Sessionkontext oder CODEX_THREAD_ID verfügbar ist und send_message_to_thread zulässig ist, melde einmal Issue, ID, hostId, Worktree und Branch an [coordinator ID]. Rate keine ID und durchsuche keine fremden Sitzungen. Ist die Rückmeldung unmöglich, erwähne das kurz und arbeite weiter; die Orchestrierung übernimmt die Zuordnung. Starte keine weiteren Ticket-Tasks.
```

## Separate critical verification

```text
Prüfe jetzt gesondert und kritisch, ob die Implementierung und bisherige Verifikation sämtliche Akzeptanzkriterien von [ticket] tatsächlich abdecken. Prüfe auch relevante Gegenbeispiele und Grenzen. Leite erforderliche Ergänzungen selbst aus Ticket und Repository-Vorgaben ab und behebe gefundene Lücken.

Zeige das Ergebnis mit tatsächlichen Screenshots der laufenden Umsetzung oder lesbaren, gemessenen Soll/Ist-Ergebnissen. Liefere absolute Pfade, relevante Test-/Reviewbefunde, Prüfgrenzen und die Identität des final geprüften Standes. Erneuere betroffene Nachweise nach Änderungen. Noch kein Commit/Push/Merge, Ticketabschluss oder OpenSpec-Archivieren.
```

## Repair

```text
Noch nicht akzeptiert. Für [criterion] zeigt [inspected artifact/measurement] folgendes Problem: [observed outcome or missing proof]. Erwartet ist [ticket-grounded outcome]. Diagnostiziere die Ursache selbst, korrigiere beziehungsweise ergänze die Verifikation und liefere neue Nachweise für den resultierenden Stand. Die übrigen akzeptanzrelevanten Eigenschaften müssen erhalten bleiben. Noch keine Lieferung.
```

## Acceptance and delivery

```text
Akzeptiert für [ticket], geprüfter Stand [SHA/manifest], anhand [actually inspected evidence]. Akzeptierte Grenzen: [material limitations].

Führe die vom Nutzer beauftragte Lieferung aus: OpenSpec gegebenenfalls schließen/archivieren und validieren, auf [confirmed branch] committen, nach [verified remote] pushen und nach [target] mergen. Beachte erforderliche Checks und Branch Protection; kein Force-Push oder Bypass. Verifiziere nach Konfliktauflösung/Änderungen erneut; wesentliche Änderungen brauchen eine neue Abnahme.

Bestätige PR, Head, Merge-Commit, Remote-Ziel und Ticket-Schließung. Weise nach, dass die akzeptierten Inhalte auf dem Remote-Ziel enthalten sind. Aktualisiere einen sauberen Haupt-Checkout nur per Fast-forward und bewahre fremde Änderungen. Erhalte die Nachweisartefakte. Starte selbst keine nächste Ticket-Session. Falls automatische Freigabeprüfung blockiert, liefere ihre genaue Begründung und den konkreten noch ausstehenden Schritt.
```

## Heartbeat

Keep the schedule in the automation fields. Render the real absolute paths and task ID below, not this template literally. Store changing ticket state in the ledger rather than copying the entire lifecycle into automation.toml.

```text
Setze den autorisierten Ticket-Batch in dieser Orchestrierungsaufgabe [ID] fort. Lade [absolute orchestrate-ticket-batch/SKILL.md] und lies zuerst den aktuellen kompakten Zustand aus [absolute ledger path]. Batchumfang: [frozen ticket IDs], Repository: [root], Ziel: [target].

Gleiche aktuelle Phase und eventuell ausstehende Tool-Aktionen mit der bekannten Umsetzung und gegebenenfalls dem Remote-Tracker ab, bevor du mutierst. Nutze bestätigte IDs direkt. Bei fehlender ID folge der begrenzten Metadaten-Wiederherstellung des Skills. Keine doppelten Tasks oder Prompts; keine Produktimplementierung hier.

Verarbeite einen erkannten Abschluss bis zum nächsten möglichen Schritt im selben Lauf. Bei unverändertem oder nicht handlungsrelevantem Stand bleibe still; melde nur wesentliche Fortschritte, Abschluss, Fehler oder nötige Nutzereingaben. Speichere Phase, Cursor und nächste Aktion vor Laufende. Nach vollständiger verifizierter Lieferung des eingefrorenen Batches pausiere nur diese Automation.
```
