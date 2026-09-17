# Backstage als Operator-Oberfläche des Agent-Framework-Piloten

Stand: 2026-09-13. Recherche und Architektur-Empfehlung; keine Implementierungsentscheidung oder geprüfte Paketkompatibilität.

**Empfehlung:** Backstage ist ein geeigneter Kandidat für das gemeinsame Entwicklerportal und den darin eingebetteten Operator Client. Für den Piloten ohne bekanntes bestehendes Backstage-Deployment empfehle ich zunächst eine eigenständige React-Oberfläche mit React Flow und klarer API-Grenze. React Flow allein rechtfertigt die zusätzliche Plattform nicht. Backstage wird attraktiv, sobald Repository-Katalog, Ownership, Dokumentation und weitere Entwicklerwerkzeuge einen eigenständigen gemeinsamen Portalbedarf bilden. Dies ist eine Abwägung der nachfolgend belegten Fähigkeiten und Betriebspflichten.

## Was sich gut einbetten lässt

Die aktuelle Backstage-Frontend-Architektur kapselt Seiten, Navigation, APIs und Katalog-Erweiterungen in Plugins. `createFrontendPlugin` und `PageBlueprint` können reguläre React-Komponenten als eigene, auch umfangreiche Anwendungsseiten laden. React Flow stellt eine React-Komponente für Knoten und Kanten bereit; eigene Knoten sind ebenfalls React-Komponenten. **Schlussfolgerung:** Ein „Agent Operations“-Plugin mit React-Flow-Ansicht ist architektonisch plausibel. React-, Paket-, CSS- und Layout-Kompatibilität der konkret ausgewählten Versionen muss ein Integrationsversuch noch belegen. [Frontend-Plugins](https://backstage.io/docs/frontend-system/architecture/plugins/), [Plugin-Bau](https://backstage.io/docs/frontend-system/building-plugins/index/), [React Flow](https://reactflow.dev/learn), [Custom Nodes](https://reactflow.dev/learn/customization/custom-nodes).

Der Software Catalog verwaltet Software-Metadaten und Ownership aus versionierten Metadaten und ordnet integrierte Werkzeuge um diese Einträge an. Backstage bietet außerdem Authentifizierungsprovider sowie ein Permission-Framework für Ressourcen und Aktionen; eigene Plugins müssen dessen Prüfungen integrieren. **Möglicher Nutzen für den Piloten:** Einstieg über ein Repository beziehungsweise dessen Software-Komponente, verknüpfte Runs und Dokumentation sowie gemeinsame Anmeldung und Navigation. [Catalog](https://backstage.io/docs/features/software-catalog/), [Auth](https://backstage.io/docs/auth/), [Permissions](https://backstage.io/docs/permissions/overview/), [Plugin-Integration](https://backstage.io/docs/permissions/plugin-authors/01-setup/).

## Verantwortungsgrenze für diesen Piloten

Der [vereinbarte GUI-Entwurf](../../openspec/changes/add-agent-framework-operator-gui/design.md) verlangt unabhängige Hintergrundausführung, persistierte Run History, vollständige Operator-Aktionen und einen separaten Workstation Client. Die [Control-Lease-Spezifikation](../../openspec/specs/repository-control-lease/spec.md) setzt aktuelle Repository-Provider-Berechtigungen als alleinige Operator-Autorität sowie menschliche Identität, Lease und atomare Versions-/Head-Prüfungen voraus.

**Architektur-Empfehlung:**

- Backstage mit eigenem Plugin übernimmt Einstieg, Darstellung und Eingabe. React Flow visualisiert Mandat, abgeleitete Issues, Aktivitäten und Attempts; ein Detailbereich zeigt die zugehörige beobachtbare Historie.
- Die bestehende .NET-Control-Plane bleibt maßgeblich für Ausführung, Zustand, History, Autorisierung, Interventionsbefehle und Freigaben. Das Plugin konsumiert deren öffentliche Schnittstellen. Eine Backstage-Anmeldung oder Portalrolle erteilt für sich keine Run-Berechtigung; die Integration muss die erforderliche Provider-Identität erhalten. Keine zweite Run-ACL und keine direkte Datenbankmutation.
- Der Workstation Client bleibt für adressierte lokale Agentenöffnung und Rückübertragung der lokalen Beobachtungen zuständig.

Diese Aufteilung folgt dem lokalen Vertrag. Backstage dokumentiert ausdrücklich Plugins, die separate Dienste per API nutzen; ein Umzug des .NET-Dienstes in Backstage ist daher keine Voraussetzung. React Flow dokumentiert Graph-Interaktion und Darstellung, keine Erfüllung der hier verlangten dauerhaften Workflow-Ausführung: Laufzeit, Wiederaufnahme und History müssen weiterhin durch den Piloten geliefert werden. [Backstage-Architektur](https://backstage.io/docs/overview/architecture-overview/), [React Flow](https://reactflow.dev/learn).

Backstage Notifications können mit Signals Echtzeitmeldungen anzeigen. **Abgrenzung:** Das belegt noch keine automatische lokale Codex-Öffnung bei geschlossenem Browser, Offline-Zustellung oder deduplizierte Handover-Bestätigung gemäß dem lokalen GUI-Entwurf. Diese Integration bleibt gesondert zu liefern. [Notifications](https://backstage.io/docs/notifications/).

## Aufwand und Entscheidungskriterium

Backstage ist eine individuell weiterzuentwickelnde Anwendung auf Bibliotheksbasis. Updates betreffen zusammengehörige Pakete; Änderungen am erzeugten App-Template werden nicht automatisch übernommen. Die typische Architektur umfasst Frontend, Backend und Plugin-Datenbanken; PostgreSQL ist die bevorzugte Produktionsdatenbank. Deployment ist mit oder ohne Docker möglich, Kubernetes ist keine Voraussetzung. [Updates](https://backstage.io/docs/getting-started/keeping-backstage-updated/), [Architektur](https://backstage.io/docs/overview/architecture-overview/), [Deployment](https://backstage.io/docs/deployment/).

**Folgerung:** Bei vorhandenem Portal oder verbindlichem Portalziel ist ein Backstage-Plugin sinnvoll. Für den isolierten Nachweis des vollständigen Operator-Verhaltens erhöht eine erstmalige Plattform-Einführung den Umfang. Die erste Oberfläche sollte deshalb austauschbare React-Komponenten und einen getrennten API-Client verwenden; ein späterer Backstage-Adapter bleibt damit ein realistischer, noch zu prüfender Integrationsweg. Falls Backstage sofort gewählt wird, sollte ein begrenzter Versuch zuerst Graph, authentifizierten History-Zugriff, Ereignis-Reconnect und eine API-seitig abgesicherte Intervention nachweisen.

## Quellennachweise

Die Links an den Aussagen verweisen auf offizielle Backstage-/React-Flow-Dokumentation beziehungsweise die verbindlichen lokalen Entwürfe und Spezifikationen. Recherche per Dokumentenabgleich; keine Installation, Laufzeitprüfung oder Versionsmatrix wurde durchgeführt.
