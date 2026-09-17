# Wiederaufnehmbare Wiki-Pflege mit unabhaengiger Fachquellen-Indexpflege

Status: ready-for-agent
Date: 2026-09-17
Issue source: Local Markdown
Origin: Nutzerauftrag zur Diagnose der haengenden QMD-Automation und Pflegeinterview vom 17.09.2026; bestaetigte Optionen 1 und 1.
Owning change: [operate-contextual-llm-wiki](../../openspec/changes/operate-contextual-llm-wiki/proposal.md)
Decision: [ADR 0016](../../docs/adr/0016-decouple-source-index-freshness-from-wiki-compilation.md)

## Problem Statement

Die taegliche Pflege wirkt ueber Stunden festgefahren. Die Codex-Session wartet wiederholt auf denselben stillen Helper, ohne erkennbaren Fortschritt oder begrenzten Diagnoseausstieg. Damit ist fuer Daniel weder ersichtlich, ob Wissen erfolgreich aufgebaut wird, noch wann die Suche neue Dokumente beruecksichtigt.

Die Untersuchung zeigte einen fast fuenfstuendigen Lauf mit 1.986 bereitgestellten Fachquellen und 1.983 als neu vorgemerkten Quellen. Wechselnde Codex-Unterprozesse waren weiterhin in der Konzeptextraktion. Eine echte Endlosschleife im Compiler oder serienweise Providerfehler wurden damit nicht bewiesen; belegt sind fehlende Beobachtbarkeit und eine unbegrenzte aeussere Warteschleife.

Die Verarbeitung erkennt Aenderungen bereits ueber Hashes und besitzt einen No-op-Pfad. Der gemeinsame Erstimport wurde jedoch noch nicht abgeschlossen. Erfolgreiche Einzel-Extraktionen werden waehrend der langen Phase nicht dauerhaft fuer einen spaeteren Lauf gesichert. Eine Aenderung irgendeiner Quelle waehrend der Generierung kann die gesamte Veroeffentlichung verhindern; temporaere Arbeit wird anschliessend entfernt. Historische Versuche wurden wegen solcher Quellenabweichungen abgebrochen. Jeder neue Anlauf muss dadurch erhebliche Arbeit erneut leisten.

Die Fachquellen-Indexpflege liegt hinter der Wiki-Kompilierung und wird durch deren ausstehenden Abschluss ebenfalls aufgehalten. Daniel braucht aktuelle Originale in der Suche und eine schrittweise, nachvollziehbare Wiki-Nachpflege, die auch bei Unterbrechungen vorankommt.

## Solution

Der vorhandene taegliche Job aktualisiert die Suchdaten aktueller Fachquellen unabhaengig davon, ob die Wiki-Aufbereitung abgeschlossen werden kann. WikiQuery bleibt der gemeinsame Zugang: Es liefert entweder verifizierte aktuelle Wiki-Aussagen oder gekennzeichnete, gepruefte Originalquellen. Ein erfolgreicher Suchindexlauf wird nicht als erfolgreiche Wiki-Kompilierung ausgegeben.

Neue und geaenderte Fachquellen erhalten Vorrang vor dem Erstimport-Rueckstand und sollen spaetestens am naechsten Tag im Wiki verarbeitet sein. Der Erstimport darf mehrere Tage dauern. Arbeit wird in begrenzten, wiederaufnehmbaren Einheiten ausgefuehrt; bereits erfolgreiche und weiterhin gueltige Modellarbeit bleibt ueber Prozessneustarts erhalten. Das Aktualitaetsziel darf bei Ausfaellen nicht still relativiert werden: Fristverletzungen und Ursachen werden sichtbar.

Fortschritt, Fehler und Restarbeit werden waehrend des Laufs dauerhaft erfasst. Ein kontrolliertes Laufende sichert den Stand und gibt die Steuerung zurueck. Gemeinsame Providerfehler stoppen weitere abhaengige Modellauftraege. Fachquellen, gemeinsamer Pflegeumfang, WikiQuery-Zugang sowie bestehender Zeitplan, Modell, Projekt und Benachrichtigungseinstellungen bleiben erhalten.

## User Stories

1. As a knowledge user, I want newly indexed original sources to be discoverable before wiki generation finishes, so that a long initial import does not block access to current information.
2. As a knowledge user, I want WikiQuery to remain my single entry point, so that I do not need to choose between competing search workflows.
3. As a knowledge user, I want original-source fallback to be explicit, so that I can distinguish retrieved evidence from completed wiki synthesis.
4. As a knowledge user, I want stale dependent wiki statements excluded, so that old conclusions are not presented as current knowledge.
5. As a knowledge user, I want navigable original references and freshness checks, so that I can verify the evidence behind an answer.
6. As a knowledge user, I want explicit task and source boundaries respected during fallback, so that independent indexing does not broaden my query scope.
7. As the operator, I want new and changed sources processed in the wiki by the next day, so that ongoing work remains useful during the initial import.
8. As the operator, I want ongoing updates prioritized over the initial backlog, so that a large existing corpus does not delay daily changes.
9. As the operator, I want the initial import to progress across multiple days, so that it does not require one uninterrupted long session.
10. As the operator, I want unchanged initial-backlog sources to retain their identity across runs, so that they are not repeatedly misclassified as new daily updates.
11. As the operator, I want changes to an unprocessed backlog source to receive ongoing-update priority, so that active work receives the same freshness treatment as established sources.
12. As the operator, I want successful unchanged extraction work reused after restart, so that an interruption does not waste completed model requests.
13. As the operator, I want cached work invalidated when its evidence or generation contract changes, so that resumption does not reuse incompatible results.
14. As the operator, I want a source edit during processing to invalidate only work whose independence cannot be proven, so that unrelated verified progress survives.
15. As a knowledge user, I want concepts supported by multiple repositories to preserve their full verified dependencies, so that smaller work units do not distort shared conclusions.
16. As the operator, I want confirmed removals distinguished from incomplete scans, so that unavailable folders do not silently erase knowledge.
17. As the operator, I want bounded maintenance runs with a durable remaining-work report, so that a session returns control instead of waiting indefinitely.
18. As the operator, I want progress visible while work is running, so that I can distinguish activity, successful processing, failures and stalled work.
19. As the operator, I want shared provider failures to stop new dependent requests, so that the queue does not repeatedly consume time on a broken prerequisite.
20. As the operator, I want isolated failures to preserve independent valid work, so that one problematic source does not block the entire corpus.
21. As the operator, I want concurrent maintenance attempts to respect the existing ownership locks, so that source and wiki indexing cannot overlap unsafely.
22. As the operator, I want source-index freshness, daily-update completion and initial-import completion reported separately, so that partial progress cannot look like full success.
23. As the operator, I want missed freshness targets and their pending sources visible, so that outages or overload do not remain hidden behind a successful index report.
24. As the operator, I want unchanged completed work to require no new model calls, so that ordinary maintenance remains small.
25. As the operator, I want preserved generated knowledge and source authority during rollout, so that improving maintenance does not lose valid existing work or modify original documents.
26. As the operator, I want the saved automation prompt to use bounded observation and the durable report, so that it cannot fall back into the diagnosed polling loop.
27. As the operator, I want an actual scheduled execution verified after activation, so that a successful isolated test is not mistaken for productive completion.

## Implementation Decisions

Die Produktentscheidungen sind durch das Pflegeinterview und ADR 0016 festgelegt. Die folgenden technischen Festlegungen sind begruendete Umsetzungsannahmen; konkrete Parameter werden bei der Lieferung gemessen und festgelegt, ohne weitere Produktinterviews.

1. **Bestehende Komponenten weiterentwickeln.** Der Wartungshelper, die verwaltete Wiki-Pflege, Compiler-Integration, QMD-Anbindung und der bestehende WikiQuery-Zugang tragen den Ablauf. Die vorhandene hashbasierte Aenderungserkennung bleibt erhalten. Kein zweiter Retrieval-Dienst und kein zusaetzlicher Scheduler werden eingefuehrt.
2. **Pflegefolge entkoppeln.** Fachquellen-Indexpflege darf vor dem Abschluss der Modellarbeit fertig werden. Ungepruefte oder veraltete generierte Wiki-Seiten duerfen durch einen globalen Indexlauf nicht wieder als aktuelle Evidenz erreichbar werden. Aktualitaetspruefung bei der Query bleibt verpflichtend. QMD-Schreiboperationen bleiben serialisiert; Unabhaengigkeit bedeutet keine parallelen Schreiber derselben Datenbank.
3. **Eingangsinventar und Prioritaet dauerhaft unterscheiden.** Ein persistiertes Ausgangsinventar identifiziert den Erstimport-Rueckstand. Spaeter neu erkannte oder geaenderte Quellen gehoeren zur laufenden Nachpflege, auch wenn ihre vorherige Fassung noch im Rueckstand lag. Wiederholung eines Scans setzt das Alter offener Arbeit nicht zurueck. Bestaetigte Entfernungen behalten ihre bestehenden Abhaengigkeits- und Sperrregeln.
4. **Aktualitaet separat messen.** Das Ziel bleibt die Verarbeitung spaetestens am naechsten Tag in der lokalen Zeitzone Europe/Berlin. Der Bericht unterscheidet beobachtete Quellenstaende, Aktualisierungsbedarf, Verarbeitung und Fristverletzung. Eine unbekannte Aenderungszeit wird nicht erfunden. Ausfallzeiten und zu hoher Durchsatzbedarf bleiben erklaerte Zielverletzungen, keine automatische Verlaengerung der Frist.
5. **Wiederverwendbare Modellarbeit sichern.** Jede erfolgreich validierte Extraktion wird dauerhaft gesichert, bevor sie als wiederaufnehmbarer Fortschritt zaehlt. Gueltigkeit umfasst Quellenidentitaet und Inhalt sowie relevante Modell-, Prompt-, Schema- und Compilerparameter; weiterer Modellkontext muss ebenfalls erfasst werden. Unvollstaendige oder inkompatible Eintraege werden nicht wiederverwendet. Ein Cachetreffer macht eine Quelle noch nicht zu veroeffentlichtem Wiki-Wissen.
6. **Arbeitseinheiten an Abhaengigkeiten ausrichten.** Begrenzte Pakete dienen der Ausfuehrung, nicht einer kuenstlichen Trennung des gemeinsamen Wissens. Quellenuebergreifende Konzepte und gespeicherte Antworten werden gegen alle benoetigten Quellenversionen geprueft. Bei unbekannten Abhaengigkeiten wird die betreffende Veroeffentlichung zurueckgestellt; unabhaengige Extraktionsarbeit und aktuelle Originalsuche koennen dennoch erhalten bleiben.
7. **Aenderungen gezielt nachziehen.** Vor Wiederverwendung und Veroeffentlichung werden relevante Quellenstaende geprueft. Drift entwertet betroffene Ergebnisse und deren Abhaengigkeiten. Ein nicht betroffener erfolgreicher Extraktionsschritt bleibt verwendbar. Eine alte Antwort darf nicht durch neue Metadaten scheinbar aktuell werden.
8. **Begrenztes Laufende.** Die Ausfuehrung bekommt ein explizites Zeit- beziehungsweise Arbeitsbudget und eine endliche Beendigungsfrist. Bei Budgetende werden keine neuen Modellauftraege begonnen, vorhandene Unterprozesse innerhalb der Frist abgeschlossen oder gezielt beendet, Fortschritt gesichert und Sperren kontrolliert freigegeben. Ein nachfolgender Prozess setzt anhand dauerhaften Zustands fort. Paketgroesse und Parallelitaet muessen gemeinsam genutzte Konzepte und Tagesprioritaet beruecksichtigen; die vorgeschlagenen 25–50 Quellen und 20–30 Minuten sind keine zugesagten Produktwerte.
9. **Fehler klassifizieren.** Ein gemeinsamer Authentifizierungs-, Provider-, Speicher- oder Indexfehler stoppt die jeweils davon abhaengige Arbeit. Er wird nicht fuer jede weitere Quelle als isolierter Fehler wiederholt. Begrenzte Quellenfehler halten ihre Fehlerursache und Restarbeit fest. Unvollstaendige Scans bestaetigen keine Entfernungen. Sichere unabhaengige Suchindexpflege ist weiterhin erlaubt.
10. **Beobachtbarer Prozessvertrag.** Neben eindeutiger Laufidentitaet und Artefaktverweis werden Phase, laufende Arbeit, erfolgreiche und fehlgeschlagene Einheiten, wiederverwendete Ergebnisse, Restbestand und letzter Fortschritt dauerhaft lesbar. Fortschritt darf nicht ausschliesslich von der Rueckkehr des Compileraufrufs abhaengen. Fortschrittsdaten enthalten keine Zugangsdaten und keine unnoetigen Dokumentinhalte. Die bestehende strukturierte CLI-Endausgabe bleibt fuer ihre Aufrufer parsebar.
11. **Getrennte Ergebnisdimensionen.** Der Abschlussbericht unterscheidet Fachquellen-Indexpflege, laufende Wiki-Nachpflege und Erstimport-Rueckstand. Ein planmaessig begrenzter Lauf mit Restarbeit ist wiederaufnehmbar, aber kein vollstaendiger Erfolg. Der bestehende Vertrag fuer vollstaendigen Erfolg verlangt weiterhin Exit 0, ein explizit erfolgreiches Ergebnis und keine offene angeforderte Arbeit. Die genaue Kodierung eines budgetbedingt unvollstaendigen Laufs wird mit Parsern und Tests abgestimmt; bisherige Verbraucher duerfen ihn nicht als Vollerfolg interpretieren. Der vollstaendige Pflegezeitpunkt wird nicht durch Indexerfolg oder Teilverarbeitung vorgezogen.
12. **Automationsvertrag anpassen.** Der Agent startet einen eigenen Lauf einmal, liest den bekannten Fortschrittsort und beobachtet nur begrenzt. Fehlender Fortschritt fuehrt nach einer definierten Grenze zu einer begrenzten Diagnose und einem sichtbaren Ergebnis. Weder neues Starten zur Ausgabewiedergewinnung noch endloses Warten auf einen fehlenden Abschlussbericht ist erlaubt. Der Prompt, die Wartungsreferenz und die Betriebsanleitung muessen diesen Vertrag uebereinstimmend beschreiben.
13. **Bestand und Aktivierung erhalten.** Vorhandener Zustand wird kompatibel uebernommen oder kontrolliert migriert. Wiederverwendbare, gueltige Ergebnisse duerfen nicht durch einen pauschalen Reset verloren gehen. Eine spaetere Aktivierung erfolgt ohne konkurrierenden Pflegeprozess. Diese Spec-Veroeffentlichung startet oder beendet keinen Produktionslauf und veraendert die Live-Automation nicht.

## Testing Decisions

**Primaere Testgrenze:** Der oeffentliche Wartungshelper wird als Prozess gegen temporaere Fachrepos, echten verwalteten Wiki-Code, den integrierten Compiler und eine isolierte QMD-Datenbank ausgefuehrt. Ergebnispruefung erfolgt ueber dauerhafte Laufberichte und die oeffentliche WikiQuery-Schnittstelle. Ein kontrollierter Modellprovider liefert deterministische Antworten, Fehler und begrenzt gehaltene Aufrufe. Externe Modell- und Embeddingantworten duerfen kontrolliert werden; Aenderungserkennung, Wiederaufnahme, Publikation und Retrieval werden nicht durch Attrappen ersetzt.

Diese Testgrenze ist eine Umsetzungsannahme auf Basis der vorhandenen oeffentlichen Schnittstellen; sie wurde zur Rueckmeldung gestellt und wird mangels abweichender Vorgabe verwendet. Die Codex-Automation erhaelt zusaetzlich eine Konfigurations- und spaetere Betriebspruefung, ohne ihre agentische Ausfuehrung fuer jeden Regressionstest vorauszusetzen.

Ein guter Test behauptet externes Verhalten: die Quelle ist auffindbar, eine alte Aussage fehlt, ein Neustart loest keinen zweiten identischen erfolgreichen Modellauftrag aus, ein Prozess endet innerhalb einer Grenze und Restarbeit bleibt rekonstruierbar. Er spiegelt keine private Datenstruktur und zaehlt keine internen Methodenaufrufe. Fuer Wiederverwendung werden beobachtbare Provideranfragen fuer kontrollierte Quellen ausgewertet; fuer Suchbarkeit genuegt weder Exit 0 noch die Existenz einer Indexdatei.

Vorhandene Vorbilder sind die Tests zur inkrementellen Lebensdauer und zum No-op, zu Quellenabweichungen und konkurrierenden Schreibern, sowie zur Teilfehlerfortsetzung ueber den echten Wartungshelper. Der bestehende prozessuebergreifende Test ersetzt globale Retrieval-Kommandos teilweise durch eine Attrappe; diese allein reicht fuer den neuen Nachweis der Originalquellensuche nicht aus.

| Abnahme | Beobachtbares Ergebnis |
| --- | --- |
| Neue Originalquelle, blockierte Wiki-Generierung | Nach begrenzt beendetem Pflegeversuch findet WikiQuery den aktuellen Originalinhalt mit gueltigem Verweis und gekennzeichnetem Fallback. |
| Geaenderte Quelle mit alter Wiki-Aussage | Die alte Aussage wird nicht als aktuell geliefert, obwohl die Originalquelle bereits indexiert ist. |
| Erstimport plus neue Tagesaenderung | Ein kleines Folgepaket verarbeitet die Tagesaenderung vorrangig; unveraenderter Rueckstand wird nicht erneut als neue Tagesarbeit eingestuft. |
| Geaenderte noch offene Erstimportquelle | Die neue Fassung erhaelt Tagesprioritaet; keine fertige Synthese beruft sich auf die veraltete Fassung. |
| Kontrolliertes Budgetende und neuer Prozess | Bericht meldet Restarbeit und getrennten Indexstatus; unveraenderte erfolgreiche Extraktionen werden nicht erneut beim Provider angefordert. |
| Prozessabbruch nach gesichertem Fortschritt | Ein frischer Prozess verwertet die vollstaendig gesicherten Einheiten; unvollstaendige Eintraege bleiben unverwendet. |
| Quellen-, Prompt- oder Modellvertragsaenderung | Betroffene Zwischenergebnisse werden neu berechnet; unveraenderte kompatible Ergebnisse bleiben verwendbar. |
| Quellenabweichung waehrend Generierung | Betroffene Veroeffentlichung bleibt gesperrt; belegbar unabhaengige erfolgreiche Arbeit ueberlebt. |
| Gemeinsames Konzept ueber zwei Repos | Endgueltige Synthese und gespeicherte Antworten enthalten nur gepruefte Abhaengigkeiten; Paketgrenzen unterschlagen keine benoetigte Evidenz. |
| Gemeinsamer Providerfehler bei gefuellter Queue | Neue abhaengige Anfragen stoppen nach erkannter gemeinsamer Stoerung; bereits laufende Arbeit wird begrenzt abgewickelt und der Fehler sichtbar. |
| Isolierter Quellenfehler | Unabhaengige gueltige Arbeit bleibt nutzbar, betroffene Aussagen und Restarbeit bleiben klar ausgewiesen. |
| Fehlende Quelle versus unvollstaendiger Scan | Bestaetigte Entfernung zieht abhaengige Aussagen zurueck; Scanfehler verursacht keine Massenentfernung. |
| QMD-Fehler und Wiederaufnahme | Indexfrische wird nicht behauptet; gesicherte kompatible Modellarbeit geht fuer die Wiederaufnahme nicht verloren. |
| Zweiter gleichzeitiger Aufruf | Kein ueberlappender Schreiber; vorhandene Laufzustandsdaten bleiben intakt und Besitzkonflikt ist sichtbar. |
| Tagesfrist ueberschritten | Kontrollierte Zeit zeigt die offene Aenderung und die verpasste Frist; ein erneuter Scan setzt ihre Historie nicht zurueck. |
| Unveraenderter abgeschlossener Folgelauf | Keine neuen Modellaufrufe, konsistenter No-op und weiterhin nutzbarer Index. |
| Explizite Abfragebegrenzung | Quellen-Fallback respektiert dieselben Grenzen wie Wiki-Evidenz. |
| Automationsdefinition nach Aktivierung | Zeitplan, Modell, Projekt, Benachrichtigung und Pflegeumfang bleiben erhalten; Prompt und Referenzen enthalten endliche Beobachtungs- und Ausstiegsregeln. |

Verhalten wird zuerst isoliert mit Rot→Gruen-Slices verifiziert. Jeder Fehler- oder Abbruchtest besitzt eine kurze harte Testfrist und raeumt ausschliesslich eigene Prozesse auf. Es werden keine Produktionshelfer zur Reproduktion gestartet und keine laufenden fremden Handles gepollt. Erst nach isolierter Verifikation folgt eine kontrollierte produktive Abnahme; ein spaeterer tatsaechlicher Schedulerlauf sowie der endgueltige Erstimport-Abschluss werden separat nachgewiesen. Vor Umsetzung und Aktivierung sind die konkreten Grenzen samt Messgrundlage zu dokumentieren.

## Out of Scope

- Ein taeglicher erzwungener Vollimport oder das Zuruecksetzen des bestehenden Wissensbestands.
- Reduzierter Quellenumfang, ein separates Privat-Wiki oder geaenderte Zugriffsregeln.
- Ein neuer Suchzugang neben WikiQuery, ein zweiter Retrieval-Speicher oder eine neue Antwortplattform.
- Zusaetzliche Scheduler, Watcher oder automatische Pflege durch Query oder Merge.
- Unabhaengige Modellwechsel, Dependency-Upgrades und die separate Upstream-Release-Automation.
- Reparaturen an macOS-TCC, Anmeldung, Installation oder sonstigen Fachautomationen waehrend eines Tageslaufs.
- Eine Garantie rechtzeitiger Verarbeitung trotz ausgeschaltetem Mac, nicht verfuegbarem Provider oder beliebig hohem Aenderungsvolumen; solche Faelle verletzen sichtbar das Ziel.
- Veroeffentlichung ungepruefter Teilsynthesen, Aenderung von Originalquellen oder Behauptung eines abgeschlossenen Erstimports durch einen erfolgreichen Suchindexlauf.
- Sofortige Codeumsetzung, Ticketzerlegung, Commit, Push oder Aenderung laufender Produktionsprozesse im Rahmen dieser Spec-Erstellung.

## Further Notes

Diese Spec ist die lokale Tracker-Veroeffentlichung des bestaetigten Betriebs-Deltas und erhaelt direkt `ready-for-agent`; eine weitere Triage ist nicht erforderlich. Sie ersetzt nicht die archivierten Implementierungsnachweise. Der bestehende OpenSpec-Change bleibt Eigentuemer der Anforderungen; spaetere Implementierungstickets sollen diese Spec und die jeweils relevanten kanonischen Regeln referenzieren.

Restliche technische Risiken sind das Verdraengen des Erstimports durch dauernden Aenderungsnachschub, sehr grosse gemeinsame Konzepte, unbekannte Abhaengigkeiten, kompatible Migration des alten Zustands und eine sichere Trennung von Original- und Wiki-Indexpflege innerhalb desselben QMD-Speichers. Die Umsetzung muss dabei Fortschritt fuer den Rueckstand ermoeglichen, ohne die zugesagte Tagesprioritaet still aufzugeben. Ein Cache ist abgeleitete Modellarbeit, keine neue fachliche Autoritaet und kein zusaetzlicher Suchspeicher.

Referenzen fuer die Umsetzung:

- [Glossar](../../CONTEXT.md) und [ADR 0010](../../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md).
- [ADR 0016](../../docs/adr/0016-decouple-source-index-freshness-from-wiki-compilation.md), [Betriebsdesign](../../openspec/changes/operate-contextual-llm-wiki/design.md), [Requirement-Delta](../../openspec/changes/operate-contextual-llm-wiki/specs/contextual-wiki-operations/spec.md) und [offene Betriebsschritte](../../openspec/changes/operate-contextual-llm-wiki/tasks.md).
- [Kanonischer Teilfehlervertrag](../../openspec/specs/contextual-wiki-operations/spec.md) und [Wiki-Vertrag](../../openspec/specs/contextual-llm-wiki/spec.md).
- [Bestehende Lebensdauertests](../../contextual-llm-wiki/test/lifecycle.test.ts), [Wiederaufnahmetests](../../contextual-llm-wiki/test/recovery.test.ts), [Prozesstest fuer begrenzte Fehler](../../contextual-llm-wiki/test/bounded-failures.test.ts) und [Testumgebung](../../contextual-llm-wiki/test/support.ts).
- [Untersuchte Ausgangssession](codex://threads/01a0adcb-8603-75a2-b6e4-f8060e4dffb9). Die Diagnose hat deren Helper nicht erneut gestartet oder auf dessen Abschluss gewartet.
