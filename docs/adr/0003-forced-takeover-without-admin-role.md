# Forced Takeover without an administrator role

Jeder Mensch, der auf einen Implementierungslauf zugreifen und grundsätzlich dessen Steuerung übernehmen darf, kann einen Forced Takeover auslösen, wenn ein normaler Control Transfer nicht praktikabel ist. Die Zustimmung des bisherigen Inhabers und eine gesonderte Administratorrolle sind dafür nicht erforderlich. Die Control Plane überträgt die Control Lease atomar, entzieht dem bisherigen Inhaber sofort mutierende Rechte und zeichnet mindestens bisherigen und neuen Inhaber, Zeitpunkt, betroffenen Implementierungslauf und die erzwungene Art der Übergabe in der Run History auf. Diese Entscheidung hält den Entwicklungsprozess bei Abwesenheit oder Ausfall des bisherigen Inhabers verfügbar und vermeidet für den Prototyp ein zusätzliches privilegiertes Rollenmodell; der Preis ist, dass Missbrauch und auffällige Übernahmemuster nachträglich über Audit und Agent Evolution Loop erkannt werden müssen.

## Consequences

- Ein Forced Takeover ändert weder Workflow-Phase noch Agentensession und darf keine laufende Wirkung doppelt auslösen.
- Bereits ausgestellte Steuerungstokens oder offene mutierende Requests des bisherigen Inhabers werden ab der atomaren Übernahme ungültig.
- Der bisherige Inhaber bleibt, sofern weiterhin zugriffsberechtigt, als lesender Beobachter verbunden und sieht den Forced Takeover.
- Forced Takeovers werden als eigenes auswertbares Signal an die Agent Evolution Loop projiziert.
