# Shared AI Workflow Context

Gemeinsame Begriffe fuer agentenbasierte Entwicklungs- und Dokumentationsworkflows im DanielsVault.

## Language

**Automatische Implementierung**:
Ein agentischer Arbeitslauf, der aus einem freigegebenen Issue einen verifizierten Pull Request erzeugt. Merge und Deployment gehoeren nicht zur automatischen Implementierung und bleiben menschliche Entscheidungen.
_Avoid_: Vollautonome Auslieferung, autonomes Deployment

**Implementierungsfreigabe**:
Die Einstufung eines Issues als `ready-for-agent`. Sie autorisiert den automatischen Implementierungslauf ohne weitere Startfreigabe und darf durch einen Menschen oder durch einen Agenten erfolgen, wenn das Issue nachweisbar aus einem menschlich angestossenen Arbeitsmandat abgeleitet wurde.
_Avoid_: `implementation-authorized`, doppelte Startfreigabe

**Arbeitsmandat**:
Ein von einem Menschen angestossenes Issue, PRD oder vergleichbares Requirements-Artefakt, dessen Scope von Agenten verfeinert, in Issues zerlegt und innerhalb dieser Grenzen implementiert werden darf. Abgeleitete Issues erben die Autorisierung ueber bestehende Parent-/Child- oder PRD-Verlinkungen; eigenstaendige, vom Menschen angestossene Issues sind ihr eigenes Arbeitsmandat.
_Avoid_: Blankovollmacht, unbegrenzter Agentenauftrag

**Implementierungswarteschlange**:
Die pro Repository seriell geordnete Menge freigegebener Issues, deren dokumentierte Abhaengigkeiten bereits abgeschlossen sind. Ein Folge-Issue wird erst nach Merge des vorgelagerten Pull Requests und Schliessung des blockierenden Issues gestartet.
_Avoid_: Parallele Issue-Bearbeitung, gestapelte Pull Requests

**Review-Schleife**:
Der wiederaufnehmbare Teil eines Implementierungslaufs, in dem Requirements-, Code- und Architekturpruefung Findings erzeugen und der Implementierungsagent diese bis zur erneuten Verifikation bearbeitet. Nach dem Pull Request koennen menschliche Aenderungswuensche dieselbe Schleife erneut starten; der Merge bleibt menschlich.
_Avoid_: Einmalige Selbstkontrolle, automatischer Merge

**Reviewfreigabe**:
Der gemeinsame Gate-Zustand, in dem Requirements-, Code- und Architekturreview jeweils bestanden oder begruendet nicht anwendbar sind. Ein Fehler auf einer Achse kann nicht durch den Erfolg einer anderen Achse kompensiert werden; das Requirements Review ist immer anwendbar.
_Avoid_: Mehrheitsentscheidung, gemitteltes Review-Ergebnis

**Behebungsrunde**:
Ein vollstaendiger Durchlauf aus Findings-Bearbeitung, deterministischer Verifikation und erneuter Requirements-, Code- und Architekturpruefung. Pro Review- oder menschlichem Feedback-Batch sind hoechstens drei automatische Behebungsrunden erlaubt.
_Avoid_: Endlosschleife, unbegrenztes Self-Review

**Produktentscheidung**:
Eine Entscheidung, die fachliches Verhalten, Akzeptanzkriterien, Domaenenregeln, Datenlebenszyklus, Sicherheits- oder Datenschutzgrenzen oder irreversible externe Wirkungen veraendert. Rein interne, reversible Implementierungs- und Darstellungsdetails sind keine Produktentscheidungen.
_Avoid_: Geschmacksfrage, beliebiges UI-Detail, interne Codeentscheidung

**Interventionsanfrage**:
Ein gezielter, beantwortbarer Hilferuf aus einem ansonsten automatischen Implementierungslauf, wenn dieser ohne menschliche Entscheidung oder Behebung nicht sicher fortfahren kann. Die Antwort setzt denselben Arbeitslauf fort und ist weder eine Workflow-Neukonfiguration noch ein neuer Implementierungsauftrag.
_Avoid_: Manueller Neustart, Workflow-Override, dauerhafte Worker-Steuerung, allgemeiner Fortschrittsstatus

**Control Command**:
Eine vom steuernden Menschen initiierte Nachricht an die aktive Aktivitaet eines Implementierungslaufs. Die Control Plane routet sie zur zustaendigen Agentensession; sie wird entweder nach Abbruch der laufenden Operation als Naechstes bearbeitet oder bis zu deren Abschluss geordnet eingereiht.
_Avoid_: Steuerungseingabe, Interventionsanfrage, unkorrelierter Chat-Prompt

**Operator Client**:
Eine menschliche Lese- und Steuerungsoberflaeche, die sich an einen zentralen Implementierungslauf anhaengt und dessen Run History darstellt. Sie ist selbst keine Agentensession und besitzt weder den Worker noch dessen Modellkontext.
_Avoid_: Operator-Client, Supervisor-Agent, menschliche Agentensession

**Run History**:
Die dauerhaft geordnete, vollstaendig beobachtbare Ausfuehrung aller Aktivitaeten, Agentensessions, Werkzeugwirkungen und menschlichen Entscheidungen eines Implementierungslaufs. Sie ist weder ein Modellkontext noch eine einzelne Session-Historie.
_Avoid_: Laufhistorie, Agenten-Memory, gemeinsamer Chat

**Control Lease**:
Das exklusive, sichtbar beanspruchte Recht genau eines Menschen, mutierende Kommandos an einen gesamten Implementierungslauf einschliesslich aller parallelen Aktivitaeten zu senden. Sie ist an die menschliche Identitaet und nicht an eine einzelne Clientverbindung gebunden; ein Verbindungsabbruch gibt sie nicht automatisch frei. Andere verbundene Menschen bleiben lesende Beobachter, bis die Control Lease freigegeben, uebertragen, per Forced Takeover uebernommen oder durch Entzug der erforderlichen Repository Authorization ungueltig wird.
_Avoid_: Steuerungshoheit, gleichzeitige Co-Steuerung, impliziter Session-Besitz

**Control Transfer**:
Der atomare Wechsel der Control Lease fuer einen gesamten Implementierungslauf, nachdem ein lesender Beobachter die Uebernahme angefragt und der aktuelle Inhaber sie bewilligt hat. Anfrage und Bewilligung bleiben in der Run History sichtbar.
_Avoid_: Steuerungsuebergabe, stille Uebernahme, Aktivitaetswechsel

**Forced Takeover**:
Der atomare Wechsel der Control Lease ohne Bewilligung des bisherigen Inhabers. Jeder fuer den Implementierungslauf zugriffsberechtigte Mensch darf ihn ausloesen; der erzwungene Verantwortungswechsel bleibt ausdruecklich in der Run History sichtbar.
_Avoid_: Force-Uebernahme, Administrator-Override, stille Lease-Uebernahme

**Agent Definition Repository**:
Das versionierte GitHub-Repository eines Agenten oder einer Agentenrolle mit deren Prompts, Skills, Tools, Policies, Integrationen und Zugriffen. Es definiert die verfuegbaren Agentenfaehigkeiten, orchestriert aber keine Implementierungslaeufe.
_Avoid_: Agent Platform, Einzelprompt, lokale Codex-Konfiguration

**Work Package Control Plane**:
Das zentrale System, das Implementierungslaeufe, Aktivitaeten, Agentensessions, Run History und menschliche Steuerung orchestriert. Es verwendet versionierte Agent Definition Repositories, besitzt aber deren Prompts, Skills und Tools nicht.
_Avoid_: Workflow Platform, Agent Platform, Agent Definition Repository

**Agent Evolution Loop**:
Die wiederkehrende Auswertung abgeschlossener und unterbrochener Implementierungslaeufe, die menschlich freizugebende Aenderungen an Agent Definition Repositories ableiten und ausarbeiten darf. Interventionsanfragen, Control Commands und Forced Takeovers sind dafuer eigene auswertbare Signale.
_Avoid_: Platform Learning Loop, Entwicklungs-Lernschleife, stille Selbstmodifikation

**Agent Definition Approval**:
Die durch geschuetzte Branches und ein menschliches Vier-Augen-Review im jeweiligen GitHub-, GitLab- oder Azure-DevOps-Repository qualifizierte Aenderung einer Agent Definition. Die Work Package Control Plane konsumiert nur das Ergebnis und besitzt keinen eigenen Approval-Prozess dafuer.
_Avoid_: Control-Plane-Freigabe, Agenten-Selbstfreigabe, unreviewter Direkt-Push

**Repository Authorization**:
Die providerneutrale Ableitung erlaubter Operator-Aktionen aus den aktuell wirksamen Berechtigungen einer menschlichen Identitaet auf dem Repository, dem ein Implementierungslauf zugeordnet ist. Repository-Lesezugriff erlaubt die Beobachtung; Schreib- oder Contributor-Zugriff erlaubt grundsaetzlich mutierende Operator-Aktionen, die zusaetzlich eine gueltige Control Lease erfordern. Die Work Package Control Plane authentifiziert den Menschen ueber GitHub, GitLab oder Azure DevOps, verwaltet aber keine eigene Mitglieder- oder Zugriffsliste.
_Avoid_: Control-Plane-Mitgliederverwaltung, duplizierte Repository-ACL, dauerhaft synchronisierte Benutzerrolle

**Darstellungsdetail**:
Eine reversible visuelle oder textliche Ausgestaltung innerhalb bestehender Anforderungen, Domaenensprache, Barrierefreiheitsregeln und des vorhandenen Designsystems. Ein Detail, das fachliche Bedeutung, Gefahrenstufe, Einwilligung oder Aktionssemantik traegt, ist kein blosses Darstellungsdetail.
_Avoid_: Produktentscheidung, wenn keine fachliche Wirkung vorliegt

**Verifizierter Pull Request**:
Ein Pull Request, dessen aktueller Head-Commit die erforderlichen deterministischen Checks und die Reviewfreigabe bestanden hat. Jeder neue Commit macht die Verifikation ungueltig, bis Checks und Reviews erneut bestanden sind.
_Avoid_: Einmal verifizierter Branch, veraltete Reviewfreigabe

**Verhaltensnachweis**:
Ein reproduzierbarer Beleg, dass ein konkretes Akzeptanzkriterium ueber die direkteste oeffentliche Schnittstelle das erwartete fachliche Ergebnis erzeugt. Erfolgreicher Start, fehlende Fehlermeldungen, ein Health-Status oder ein HTTP-200 ohne pruefbaren fachlichen Inhalt sind lediglich Betriebsnachweise.
_Avoid_: Startnachweis, Health-Check als Feature-Evidence, "keine Fehler gesehen"
