# Human-approved evolution of Agent Definition Repositories

Die Agent Evolution Loop darf Änderungen an einem vollständigen Agent Definition Repository analysieren, vorschlagen und als versionierte Repository-Änderungen ausarbeiten. Dazu gehören Prompts, Skills, Tools, Agent Policies, Integrationen und Zugriffe zu Ticket-System, Wiki und anderen Arbeitsmitteln sowie unterstützender Code innerhalb der Agent Definition. Keine solche Änderung darf sich selbst freigeben: Sie benötigt Agent Definition Approval durch einen zweiten Menschen über geschützten Branch und Pull oder Merge Request im jeweiligen GitHub-, GitLab- oder Azure-DevOps-Repository, bevor die Work Package Control Plane sie verwenden darf. Diese Grenze erlaubt eine umfassende kontinuierliche Verbesserung aus realen Implementierungsläufen, ohne der Agent Evolution Loop die Kontrolle über ihre eigene Governance zu übertragen.

## Consequences

- Jede vorgeschlagene Änderung besitzt eine nachvollziehbare Herkunft aus Run History, Evaluation oder einem erkannten Prozessmuster.
- Die Agent Evolution Loop kann die Änderung selbst implementieren, einen Pull oder Merge Request vorbereiten und ihre Evaluation liefern, bleibt aber vom externen menschlichen Vier-Augen-Gate getrennt.
- Aktive und historische Agentenaufrufe müssen auf eine konkrete Revision ihres Agent Definition Repository zurückführbar bleiben.
- Nach menschlicher Freigabe darf die Work Package Control Plane die neue Revision auch in einem bereits aktiven Implementierungslauf für nachfolgende Agentenaufrufe verwenden; eine bereits laufende Agentenoperation wird nicht rückwirkend verändert.
