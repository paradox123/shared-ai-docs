---
status: accepted
date: 2026-09-15
---

# Vorhandene Agentenplattformen für die Nutzung zusammensetzen

Daniel möchte komplexe Prozesse mit Agenten und Menschen auf vorhandenen Plattformen ausführen. Der Auftrag ist die Auswahl, Architektur, Konfiguration und Integration geeigneter Produkte. Die Entwicklung und dauerhafte Pflege einer eigenen Agent Control Plane ist ausdrücklich kein Ziel.

Diese Entscheidung ersetzt die in [ADR 0014](0014-evolve-control-plane-backend-with-versioned-workflows.md) vorgesehene Weiterentwicklung des Piloten zum eigenen produktiven Backend. Die bisherige Microsoft-Agent-Framework-Präferenz beschreibt den Pilotversuch; sie bindet die Auswahl der künftig genutzten Plattform nicht. Bestehende Nachweise bleiben erhalten und werden nicht als Begründung für weiteren Plattformbau verwendet.

## Konsequenzen

- Das nächste Architekturartefakt beschreibt vorhandene Produkte, ihre Zuständigkeiten und Schnittstellen, benötigte Konfiguration, Betrieb und einen konkreten durchgängigen Beispielprozess. Auch eine einzelne geeignete Plattform ist eine vollständige Lösung; zusätzliche Komponenten brauchen einen konkreten Nutzen.
- Anforderungen werden als gewünschte Arbeitsergebnisse bewertet. Andere Produktbegriffe, Zustandsmodelle oder Übergabekonzepte sind akzeptable Lösungswege, wenn sie den fachlichen Zweck erfüllen. Implementierungsdetails des Piloten werden nicht automatisch zu Auswahlkriterien.
- Vorhandene Integrationen und Erweiterungspunkte haben Vorrang. Falls eine kleine Anbindung erforderlich ist, bleibt sie auf die Verbindung bestehender Produkte beschränkt. Eine eigene allgemeine Workflow-Laufzeit, Aufgabenverwaltung, Governance-Plattform oder Operator-Oberfläche gehört nicht zum Auftrag.
- Eine Lücke führt zur Prüfung einer anderen Kombination, eines anderen Standardablaufs oder einer bewussten fachlichen Einschränkung. Sie eröffnet nicht automatisch erneut die Option einer eigenen Plattform.
- Pilotcode, offene Ausbau-Tickets und frühere Architekturentscheidungen dienen als Referenz für Anforderungen, Nachweise und Erfahrungen. Ein bestehender `ready-for-agent`-Status allein ist nach dieser Richtungsentscheidung kein Auftrag, den Plattformausbau fortzusetzen. Ticketstatus und technische Abnahmehistorie bleiben zur Nachvollziehbarkeit erhalten.
- Diese Entscheidung wählt noch keinen Anbieter, löst keinen Kauf aus und ändert keinen laufenden Dienst. Konkrete Änderungen an Daten, Integrationen und Betriebsumgebung folgen aus der später ausgewählten Nutzungsarchitektur.

Maßgeblich sind die [Produktvision](../agent-control-plane/product-vision.md) und der [Plattformvergleich](../research/agent-control-plane-platform-comparison-2026-09-15.md). Erfolg wird an nutzbaren Prozessen, geringem Integrations- und Pflegeaufwand sowie nachvollziehbaren Ergebnissen gemessen.
