---
status: accepted
date: 2026-09-19
---

# Drei getrennte Refactoring-Prüfungen im gemeinsamen Abschluss

Der gemeinsame technische Abschluss für NCG-Backend, ki-fuer-kmu und probare-crm enthält nach erfolgreicher kritischer Anforderungsverifikation drei sequenzielle Refactoring-Prüfungen: DRY → SOLID → KISS, jeweils mit einem eigenen Prüfagenten. Lücken in der Anforderungsumsetzung werden vor dem ersten Strukturreview behoben. Befunde werden vor der nächsten Prüfung bearbeitet und betroffene Tests erneut ausgeführt; die bisher strengste Prüfmethode bleibt damit erhalten und wird für probare-crm erweitert.

Daniel hat diese Variante am 2026-09-19 ausdrücklich gewählt. Die Einsparung soll aus weniger wiederholten Abschlussrunden und kompakteren Aufträgen entstehen; die drei Perspektiven werden nicht zu einem einzigen Prüfauftrag zusammengelegt. Der gemeinsame Ablauf gilt für inhaltliche technische Änderungen an Code, Anforderungen, wirksamer Konfiguration oder verbindlichen Arbeitsregeln, einschließlich Skills und AGENTS.md. Reine redaktionelle Korrekturen erhalten passende Dokumentprüfungen. Diese Anwendungsgrenze wurde ebenfalls ausdrücklich bestätigt und wird zentral gepflegt.

Der gemeinsame Ablauf gilt sowohl bei direkter Umsetzung als auch bei orchestrierter Arbeit. Am 2026-09-20 hat Daniel den Auslöser festgelegt: Direkte Implementierungsarbeit wartet nach Umsetzung und ersten Tests auf eine fachliche Abnahme wie „akzeptiert“ oder „Change accepted“, bevor die vollständigen Abschlussprüfungen beginnen. Bei vollständig delegierten Aufträgen erteilt der autorisierte Koordinator denselben Abschlussauftrag ohne zusätzliche menschliche Freigabe. Laufende Tests und Refactoring im Entwicklungszyklus bleiben Teil der Implementierung.

Die fachliche Abnahme startet die technische Prüfung und bestätigt deren Ergebnis nicht vorab. Gültige Nachweise desselben Standes werden wiederverwendet; nachfolgende Änderungen öffnen die betroffenen Prüfungen wieder. Lieferautorisierung und Zielvorgaben ergeben sich aus dem tatsächlichen Auftrag. „Unabhängig“ beschreibt die Trennung von Implementierung und Prüfung, keine weitere Prüfart.

Auf Daniels anschließenden Vorschlag wird code-review die zentrale Definition für DRY → SOLID → KISS, Repository-Standards und Nachprüfung. AGENTS.md und die Abschluss-/Orchestrierungs-Einstiege verweisen auf diesen Skill, statt seine Methode zu wiederholen. Der Accepted-Einstieg steuert kritische Anforderungsverifikation → code-review → autorisierten Abschluss. Der bisherige Spec-Abgleich geht in der vorgelagerten Anforderungsverifikation auf; eine zusätzliche pauschale Standards-/Spec-Runde entfällt im Zielentwurf. [Design und Begriffsklärung](../../openspec/changes/add-sequential-ticket-orchestration-skill/completion-contract-design.md) dokumentieren die Zuständigkeiten und den Migrationsumfang; die Migration ist lokal umgesetzt, ihre vollständige technische Abschlussprüfung wartet auf kontextbezogene Abnahme.
