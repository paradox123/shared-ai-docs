# Derive Operator access from repository permissions

Die Work Package Control Plane verwaltet keine eigene Mitglieder- oder Zugriffsliste fuer Implementierungslaeufe. Jeder Implementierungslauf ist eindeutig einem Repository zugeordnet. Der Operator Client authentifiziert einen Menschen ueber den zugehoerigen GitHub-, GitLab- oder Azure-DevOps-Provider; die Control Plane leitet dessen erlaubte Aktionen aus den aktuell wirksamen Berechtigungen auf diesem Repository ab. Provideradapter normalisieren die unterschiedlichen Berechtigungsmodelle in einen kleinen fachlichen Vertrag: Repository-Lesezugriff erlaubt Beobachtung, Schreib- oder Contributor-Zugriff erlaubt grundsaetzlich mutierende Operator-Aktionen. Deren Ausfuehrung erfordert zusaetzlich die Control Lease.

Eine lokale, kurzlebige Anwendungssession, Permission Cache und Auditdaten bleiben technische Bestandteile der Control Plane. Sie sind jedoch keine zweite Autoritaet fuer Mitgliedschaft. Mutierende Aktionen werden gegen eine hinreichend aktuelle Providerberechtigung und zusaetzlich gegen die Control Lease geprueft. Menschliche Provideridentitaeten und technische Service-Identitaeten der Agenten bleiben getrennt.

## Consequences

- Der Repository Provider bleibt die einzige Stelle, an der Teammitgliedschaft und Repositoryzugriff verwaltet werden.
- Die Control Plane braucht Authentifizierungsadapter, eine providerneutrale Action Policy, kurze Cache- oder Revalidierungsregeln und Audit; sie braucht kein eigenes Rollen- oder ACL-Management.
- Die Mindestberechtigung ist fachlich festgelegt: effektiver Repository-Lesezugriff fuer Beobachtung und effektiver Schreib- oder Contributor-Zugriff fuer Claim, Control Transfer, Forced Takeover und Control Commands. Provideradapter bilden ihre konkreten Rollen und Permissions auf diese beiden Stufen ab.
- Entzogene Providerrechte muessen ohne manuelles Entfernen aus einer zweiten Benutzerliste wirksam werden. Sicherheitskritische Mutationen duerfen nicht allein auf einer langlebigen, veralteten Sessionentscheidung beruhen.
- Der Operator Client stellt nur die gemaess Repository Authorization erlaubten Aktionen dar. Eine sichtbare Texteingabe erzeugt einen Control Command an den bestehenden Implementierungslauf und keine neue Agentensession.
- GitHub, GitLab und Azure DevOps bleiben austauschbare Autoritaeten hinter demselben fachlichen Vertrag, obwohl ihre effektiven Berechtigungen unterschiedlich ermittelt werden.

## Provider evidence

- GitHub stellt die effektive Repositoryberechtigung eines Benutzers nach Beruecksichtigung von Repository-, Team-, Organisations- und Enterprise-Zuweisungen bereit.
- GitLab kann Projektmitglieder einschliesslich geerbter und eingeladener Mitgliedschaften mit dem hoechsten wirksamen `access_level` liefern.
- Azure DevOps stellt Repositoryberechtigungen ueber Security Namespaces, ACLs und die Auswertung wirksamer Permissions bereit; `Deny`, Vererbung und Gruppenmitgliedschaften muessen dabei durch den Provideradapter beruecksichtigt werden.
