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

**Darstellungsdetail**:
Eine reversible visuelle oder textliche Ausgestaltung innerhalb bestehender Anforderungen, Domaenensprache, Barrierefreiheitsregeln und des vorhandenen Designsystems. Ein Detail, das fachliche Bedeutung, Gefahrenstufe, Einwilligung oder Aktionssemantik traegt, ist kein blosses Darstellungsdetail.
_Avoid_: Produktentscheidung, wenn keine fachliche Wirkung vorliegt

**Verifizierter Pull Request**:
Ein Pull Request, dessen aktueller Head-Commit die erforderlichen deterministischen Checks und die Reviewfreigabe bestanden hat. Jeder neue Commit macht die Verifikation ungueltig, bis Checks und Reviews erneut bestanden sind.
_Avoid_: Einmal verifizierter Branch, veraltete Reviewfreigabe

**Verhaltensnachweis**:
Ein reproduzierbarer Beleg, dass ein konkretes Akzeptanzkriterium ueber die direkteste oeffentliche Schnittstelle das erwartete fachliche Ergebnis erzeugt. Erfolgreicher Start, fehlende Fehlermeldungen, ein Health-Status oder ein HTTP-200 ohne pruefbaren fachlichen Inhalt sind lediglich Betriebsnachweise.
_Avoid_: Startnachweis, Health-Check als Feature-Evidence, "keine Fehler gesehen"
