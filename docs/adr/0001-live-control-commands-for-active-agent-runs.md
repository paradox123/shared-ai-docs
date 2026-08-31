# Live Control Commands for active agent runs

Menschen dürfen eine aktive Workflow-Aktivität auch außerhalb expliziter Fehler-, Pausen- oder Freigabepunkte beeinflussen. Ein Control Command wird an den zentralen Implementierungslauf und einen expliziten Activity Attempt gesendet; dessen Command Router löst daraus die zuständige Codex-Session auf. Bei genau einem geeigneten aktiven Versuch darf der Operator Client dieses Ziel vorauswählen, persistiert wird aber immer dessen stabile Identität. Der Command wählt ausdrücklich zwischen zwei Zustellungsmodi: `interrupt`, wodurch die laufende Agentenoperation beendet und der Command als Nächstes bearbeitet wird, oder `queue`, wodurch die Operation zunächst abgeschlossen und der Command anschließend in stabiler Reihenfolge bearbeitet wird. Beide Modi bleiben derselben Aktivität und Run History zugeordnet und werden mit Benutzer-, Session-, Aktivitäts- und Head-Identität korreliert. Diese Form entspricht dem vertrauten Codex-Interaktionsmodell, erlaubt eine frühe fachliche Korrektur und vermeidet zugleich eine nichtdeterministische Vermischung paralleler Prompts.

## Consequences

- Die Control Plane muss Workflow-Aktivitäten adressieren, deren aktuelle Agentensession auflösen, aktive Agentenoperationen abbrechen und geordnete Commands dauerhaft puffern können.
- Ein Interrupt darf nicht als fachlicher Fehler oder zusätzlicher Behebungsversuch gezählt werden; bereits eingetretene externe Wirkungen müssen vor der Fortsetzung abgeglichen werden.
- Nur der Mensch mit gültiger Control Lease darf Control Commands senden. Andere verbundene Menschen beobachten dieselbe Run History nur lesend.
- Bei mehreren parallelen Aktivitäten muss der Mensch einen konkreten Activity Attempt wählen; der Router darf kein Ziel aus zeitlicher Nähe oder einer globalen „aktuellen Aktivität“ erraten.
