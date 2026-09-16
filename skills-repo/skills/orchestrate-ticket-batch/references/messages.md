# Messages and handoff contracts

Compose readable messages from these templates; replace every bracketed field before sending. Omit optional fields that do not exist. Use actual original user instructions as authorization evidence, never fabricate quotations or call a coordinator message a direct user message.

## First worker assignment

```text
[$implement]([resolved absolute implement SKILL.md path]) Implementiere [ticket URL] vollständig. Benutze OpenSpec gemäß Implement-Skill und Repository-Policy; dokumentiere bei Verzicht die konkrete Begründung.

Dies ist die dedizierte Umsetzung für [ticket] im Ticket-Batch [batch scope]. Der Nutzer hat diesen Batch mit dem Workflow Implementierung → kritische Verifikation → Abnahme → Commit/Push/Merge beauftragt. Quelle: [original user request/task ID and faithful scope]. Diese Herkunft dokumentiert den Auftrag; tatsächliche Tool-Berechtigungen bleiben maßgeblich.

Prüfe Git-Root, Branch/detached state, Status, vorhandene Vorarbeiten und aktuellen Remote-Zielstand. Repository [root], Zielbranch [target], letzter bestätigter Remote-Stand [SHA]. Arbeite ausschließlich im für diese Aufgabe eingerichteten isolierten Worktree. Prüfe den von Codex eingerichteten Branch; falls der Worktree detached ist oder noch keinen eigenen Arbeitsbranch besitzt, lege darin einen eindeutigen codex/-Arbeitsbranch für dieses Ticket vom verifizierten Zielstand an. Arbeite niemals direkt auf dem Zielbranch. Melde den tatsächlichen Worktree-Pfad und Arbeitsbranch zur Registrierung; die Orchestrierung bestätigt anschließend die Zuordnung. Verifiziere vor Änderungen den Ausgangspunkt gegen den frisch abgerufenen Remote-Zielbranch; melde den bestätigten Basis-SHA. Bewahre fremde Änderungen. Verwende separate Ports, synthetische Datenbanken und Ausgabepfade für veränderliche Testressourcen. Melde neu entdeckte Überschneidungen mit anderen Tickets sofort an die Orchestrierung und koordiniere eine sichere Pause, bevor kollidierende Arbeit fortgesetzt wird.

Lies AGENTS.md, README, Ticket einschließlich relevanter Kommentare sowie zugehörige PRD/ADRs. Falls vorhanden: [prototype reference] ist ausschließlich visuelle Inspiration; daraus keine neuen Anforderungen, Zustände oder Pflichtschritte ableiten und keine Demo-Logik übernehmen.

Wende den genannten Implement-Skill an. Er entscheidet über aktiven OpenSpec-Change, repo-lokalen propose/apply-Workflow oder CLI-Fallback. Prüfe Verhalten durch öffentliche Schnittstellen mit TDD soweit sinnvoll, relevante Backend-/Frontend-Checks und abschließend code-review. Nutze isolierte synthetische Daten für Nachweise.

Liefere zunächst ein abnahmebereites Ergebnis: echte Screenshots der laufenden Anwendung oder verständliche Darstellungen tatsächlich gemessener Ergebnisse, absolute Artefaktpfade, Soll/Ist-Zuordnung zu Akzeptanzkriterien, Test-/Reviewbefunde, Grenzen und Identität des geprüften Standes (Commit oder Manifest). Eine bloße Liste grüner Tests genügt nicht.

Noch nicht committen, pushen, mergen, das Ticket schließen oder OpenSpec archivieren. Warte auf die separate kritische Verifikation und danach auf die Vorbereitung im exklusiven Integrationsslot durch [coordinator task ID]. Eine fachliche Abnahme erlaubt noch keinen Merge. Der Merge erhält anschließend eine gesonderte Freigabe für den konkreten PR-Head und den geprüften Zielstand. Melde technische Freigabeablehnungen mit ihrer tatsächlichen Ursache.

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

## Acceptance and integration preparation

Send only after reserving the integration slot. Accepted workers waiting for the slot stay idle and may not merge.

```text
Akzeptiert für [ticket], geprüfter Stand [SHA/manifest], anhand [actually inspected evidence]. Akzeptierte Grenzen: [material limitations]. Du hältst jetzt den Integrationsslot für [target]. Bereite die Lieferung vor; noch nicht mergen oder das Ticket schließen.

Rufe den aktuellen Stand von [remote]/[target] ab und integriere ihn ohne Force-Push. Führe erforderliche Tests, Checks und relevante Prüfung des kombinierten Verhaltens aus. Erneuere betroffene Nachweise nach Änderungen. Schließe/archiviere OpenSpec soweit erforderlich und validiere es. Committe auf [owned branch], pushe nach [verified remote] und bereite den PR mit exakt [target] als Basis vor. Beachte Branch Protection; kein Bypass.

Liefere PR, finalen Head-SHA, geprüften Ziel-SHA, Differenzen gegenüber dem abgenommenen Stand und aktualisierte Nachweise. Wesentliche Änderungen benötigen erneute Abnahme. Bewahre Artefakte und Worktree. Warte auf die gesonderte Merge-Freigabe und starte keine andere Ticket-Aufgabe. Melde Freigabeablehnungen mit ihrer tatsächlichen Ursache.
```

## Final merge grant

Send only after reviewing the prepared candidate and rechecking current remote target/head and checks.

```text
Die finale Lieferung für [ticket] ist freigegeben: PR [URL], Head [exact SHA], Ziel [remote]/[target], geprüfter Zielstand [exact SHA]. Die ursprüngliche Nutzerautorisierung ist [actual provenance]; diese Nachricht ist die koordinierende Qualitäts- und Zeitpunktfreigabe innerhalb dieses Auftrags.

Prüfe unmittelbar vor dem Merge PR-Basis, Head, Zielstand und erforderliche Checks erneut. Falls Head oder Zielstand abweichen, nicht mergen: melde den neuen Stand für erneute Verifikation/Abnahme. Merge sonst den konkreten PR nach [target], ohne Force-Push oder Bypass. Keine zeitlich offene Auto-Merge-Freigabe für spätere ungeprüfte Stände.

Bestätige den tatsächlichen Remote-Merge und die enthaltenen akzeptierten Inhalte auch bei Squash/Rebase. Falls externe Änderungen dazwischenkamen, verifiziere das relevante kombinierte Verhalten am entstandenen Zielstand. Schließe [ticket] nach gesichertem Ergebnis ausdrücklich, falls automatisches Schließen bei diesem Zielbranch ausbleibt. Liefere PR, Head, Merge-SHA, endgültigen Zielstand, Ticketstatus und Artefaktpfade.

Beende danach deine Arbeit und bestätige, dass keine Prozesse mehr in deinen Worktree schreiben. Entferne den Worktree nicht selbst; die Orchestrierung sichert Nachweise und räumt anschließend auf. Starte keine nächste Ticket-Aufgabe. Bei technischer Freigabeablehnung nenne Operation und genaue Begründung; umgehe die Ablehnung nicht.
```

## Heartbeat

Keep the schedule in the automation fields. Render the real absolute paths and task ID below, not this template literally. Store changing ticket state in the ledger rather than copying the entire lifecycle into automation.toml.

```text
Setze den autorisierten Ticket-Batch in dieser Orchestrierungsaufgabe [ID] fort. Lade [absolute orchestrate-ticket-batch/SKILL.md] und lies zuerst den aktuellen kompakten Zustand aus [absolute ledger path]. Batchumfang: [frozen ticket IDs], Repository: [root], Ziel: [target].

Gleiche die Phasen aller Tickets, belegte Slots (Limit [recorded concurrency]), den exklusiven Integrationsslot und ausstehende Tool-Aktionen mit den bekannten Umsetzungen, Worktrees und dem Remote-Tracker ab, bevor du mutierst. Nutze bestätigte IDs direkt. Bei fehlender ID folge der begrenzten Metadaten-Wiederherstellung des Skills. Keine doppelten Tasks oder Prompts; keine Produktimplementierung hier.

Verarbeite erkannte Abschlüsse bis zum nächsten möglichen Schritt im selben Lauf und fülle freie Slots mit unabhängigen, nicht blockierten Tickets. Ein Blocker hält nur betroffene Tickets zurück. Prüfe pro Ticket auch die noch offene Nachweissicherung und Bereinigung. Bei unverändertem oder nicht handlungsrelevantem Stand bleibe still; melde nur wesentliche Fortschritte, Abschluss, Fehler oder nötige Nutzereingaben. Speichere pro Ticket Phase, Cursor und nächste Aktion sowie Integrations- und Bereinigungsstand vor Laufende. Nach vollständiger verifizierter Lieferung und Bereinigung des eingefrorenen Batches pausiere nur diese Automation.
```
