# Lokale Planungsfälle A–G

Alle Aktionen unten sind **geplante Koordinatoraktionen**, keine ausgeführten Task-, Messaging-, Automations-, Git- oder Netzwerkoperationen. Grundlage sind ausschließlich die Fallangaben und der gelesene [Orchestrierungs-Skill](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/orchestrate-ticket-batch/SKILL.md) samt Referenzen. Dateien wurden ausschließlich in `/tmp/orchestrator-events-scenario-output` erstellt; kein Repository wurde verändert.

Gemeinsam gilt: Ziel bleibt `release/audit`; Ticket- und Unteragentenlimits werden getrennt geführt. Vor einer Aktion werden Receipt, gerechtfertigter Phasenwechsel und ticketbezogene Pending-Action in einem revisionsgeprüften Checkpoint gespeichert, danach der beobachtete Ausgang. Bereits registrierte Worker werden weiterverwendet. Ein Turnende gibt keine Reservierungen frei. Nicht genannte Voraussetzungen werden nicht als erfüllt behandelt.

## A — Neues Ready, unzureichende fachliche Nachweise

1. `implement-1/seq1` ist mechanisch `new`. Zuordnung/Phase und das Ergebnis `/tmp/fixture/11.md` für Manifest A prüfen. Der nach Turnende zugestellte Callback belegt hier einen nutzbaren Callback-Wake; diese Evidenz im Fortsetzungsmodus festhalten.
2. Zwei grüne Tests ohne Soll/Ist-Zuordnung genügen nicht zur fachlichen Annahme. Noch keinen `change-accepted`-Auftrag erteilen. Konkrete Nachweislücke protokollieren: betroffene Akzeptanzkriterien mit tatsächlich gemessenem erwartetem/beobachtetem Verhalten, Artefaktpfaden und Grenzen belegen. Keine unbekannten Kriterien oder Ergebnisse erfinden.
3. Receipt und begrenzten Nachbesserungsauftrag an denselben Worker gemeinsam checkpointen, für die neue Anweisung eine neue Request-ID vergeben, Auftrag einmal senden und Ausgang speichern. Manifest A als Bezugsstand nennen; keine pauschale Wiederholung aller Tests verlangen. Ein Nachweisdefizit beweist noch keinen Codefehler.
4. Andere schon handlungsrelevante Ereignisse bearbeiten. Kein weiterer Ticketstart bei belegten Slots und keine Empfangsbestätigungsnachricht ohne Sachauftrag.

**Turnende:** Ja, nachdem der Nachbesserungsauftrag samt Ausgang verarbeitet ist und nur Warten bleibt. Der nachgewiesene Callback-Wake erlaubt dies; keine zusätzliche 60-Sekunden-Schleife und kein erfundener Automationsbedarf.

**Regeln:** `worker-events.md`, „Choose a usable continuation mode“ und „Coordinator consumption“; Skill „Verification and acceptance“; `messages.md`, Erstauftrag/Reparatur.

## B — Altes Ereignis, ungeklärter Abschlussauftrag

1. Gegen die aktuelle Zuordnung `complete-2` ist `implement-1/seq2` **stale**, obwohl es zugleich eine Wiederholung des historischen Receipts ist. Das alte Receipt bleibt Historie; für `complete-2` besteht dadurch kein neues Receipt. Nicht rückstufen, bestätigen oder den Abschlussauftrag aufgrund dieses Events erneut senden.
2. Die offene Pending-Action hat Vorrang: gezielt den betroffenen Zielworker und seine jüngsten Nachrichten zum Versand von `complete-2` lesen. Ein toolseitiger Laufstatus allein beweist keine Zustellung des konkreten Auftrags.
3. Bei belegter Zustellung den Ausgang verbuchen und den bestehenden Abschlussauftrag weiterverfolgen. Nur bei hinreichend geklärtem Nichtversand und weiterhin passendem Zustand einen begrenzten erneuten Versand mit **derselben** Request-ID `complete-2` erwägen. Solange der Ausgang unbekannt bleibt, Pending-Action und Reservierungen erhalten; keinen abhängigen Phasenfortschritt oder blinden Retry.

**Turnende:** Nicht allein wegen des alten Events. Zunächst die begrenzte Reconciliation durchführen. Anschließend nur bei nutzbarer dokumentierter Hintergrundfortsetzung beenden; andernfalls aktiver Warte-Fallback. „Gleicher Worker“ beweist nicht automatisch die Übernahme des in A ausdrücklich gegebenen Wake-Nachweises, da die Fälle unabhängig sind. Aus den angegebenen Fakten ist ein sofortiges sicheres Turnende daher nicht belegt.

**Regeln:** `worker-events.md`, Verbrauchsschritte 1–2/5; `recovery-and-state.md`, ungewisser Versand; `local-helpers.md`, `stale` und neue Requests.

## C — Keine erlaubte Hintergrundfortsetzung

1. Messaging-Verfügbarkeit belegt keinen Wake eines ruhenden Koordinators. Automationen sind ausdrücklich verboten; keinen Heartbeat anlegen und keine automatische Wiederaufnahme nach Turnende versprechen.
2. Den Modus „begrenztes aktives Warten“ einmal dokumentieren. Nach dem gegebenen unveränderten 60-Sekunden-Ergebnis neueste Cursor im laufenden Kontext behalten und den nächsten begrenzten `wait_threads` mit bestätigten IDs, Hosts und diesen Cursorn ausführen.
3. Keine Detailreads, zusätzlichen Worker-Nachrichten oder Shell-Checkpoints pro unverändertem Timeout. Cursor mit dem nächsten ohnehin erforderlichen Checkpoint sichern. Bei echter Änderung daraus resultierende Arbeit bearbeiten.
4. Zwei aktive Worker beweisen für sich weder einen freien Ticket-Slot noch die Zulässigkeit eines weiteren Starts: auch wartende/in Prüfung befindliche Tickets zählen. Vor weiterem Warten bekannte Slot-/Abhängigkeitsdaten auswerten; nur einen nachweislich freien Slot mit nachweislich unabhängigem Ticket füllen. Diese Belege sind hier nicht angegeben.

**Turnende:** Nein. Der verlangte autonome Fortgang hat ohne erlaubte/nachgewiesene Hintergrundfortsetzung den ausdrücklich vorgesehenen aktiven Warte-Fallback. Ein Timeout ist kein Abschluss.

**Regeln:** `worker-events.md`, „No usable background continuation“; `parallel-delivery.md`, Slotzählung/Zulässigkeit.

## D — Unveränderter Recovery-Wake

1. Der autorisierte bestehende Recovery-Heartbeat ist ein nutzbarer Fortsetzungsweg trotz unbekanntem Callback-Wake. Den Wake-Nachweis weiterhin als unbekannt führen.
2. Nach der bereits erfolgten einmaligen kompakten Beobachtung keine Detailreads, Meldungen, zusätzlichen Helferaufrufe oder weitere Warteschleife beginnen. Keine freien Slots und keine Pending-Actions bedeuten hier keine weitere handlungsrelevante Arbeit.
3. Neue Cursor/Zeitstempel gebündelt im abschließenden revisionsgeprüften Checkpoint sichern; Phasen und Reservierungen unverändert lassen.

**Turnende:** Ja, still. Der vorhandene Recovery-Heartbeat bleibt aktiv. Kein neuer Heartbeat und keine Änderung seiner Definition nötig.

**Regeln:** `worker-events.md`, einzelner Recovery-Pass; `recovery-and-state.md`, unveränderte Zustände; `messages.md`, Recovery-Heartbeat-Abschlusscheckpoint.

## E — Zielbranch bewegt, zweiter Kandidat wartet

1. Bericht `preparation-3/seq1` mit Zuordnung und Ergebnis prüfen; aus einer Sequenznummer allein ohne Receipt-Historie nicht ungeprüft `new` ableiten. Der vorbereitete Head A wurde nur gegen T1 geprüft; T2 macht eine Merge-Freigabe auf dieser Evidenz unzulässig.
2. Worker11 behält den Integrationsslot. Soweit das Ereignis regulär konsumierbar ist, Receipt und neue konkrete Pending-Action gemeinsam checkpointen: neuer Vorbereitungs-/Revalidierungsauftrag mit neuer Request-ID an Worker11 für `release/audit` auf T2. Relevantes kombiniertes Verhalten und betroffene Nachweise erneut prüfen lassen; finalen Head, getestetes Target und Änderungen gegenüber A verlangen.
3. Bei wesentlichen Kandidatenänderungen erneute fachliche/technische Annahme der betroffenen Änderungen; Dokumentationsbuchungen ausdrücklich zuordnen. Erst nach aktuellen PR-Basis-/Head-/Check-/Target-Prüfungen eine spezifische Merge-Freigabe für genau diesen Kandidaten und Zielstand erteilen. Erneute Target-Bewegung verlangt erneut Revalidierung.
4. Worker12 bleibt `awaiting-integration`. Die Worker-Nachricht „bitte beide mergen“ ist keine Nutzerautorisierung und hebt weder die Integrationsserialisierung noch die Kandidaten-/Target-Bindung auf. Keine pauschale Doppelfreigabe, keine Slotfreigabe zugunsten Worker12 während der normalen Revalidierung.

**Turnende:** Jetzt noch nicht: den konkreten Revalidierungsauftrag verarbeiten. Danach nur bei dokumentiert nutzbarem Callback-/Recovery-Weg, wenn ausschließlich Warten verbleibt. Dieser Weg ist in E nicht angegeben; daher kein unbedingtes Turnende behaupten. Ohne solchen Weg gilt bei autonomem Fortgang aktives begrenztes Warten.

**Regeln:** `parallel-delivery.md`, „One integration reservation per target“; `worker-events.md`, Event ist keine neue Nutzerautorisierung; Skill „Verification and acceptance“.

## F — Wiederholte Fehler, ausgeschöpfte Prüferkapazität

1. Allowances `1 + 1 + 1 = 3` sind vollständig reserviert. Worker11 keine drei zusätzlichen Prüfer gewähren. Sein bestehendes Kontingent erlaubt sequenzielle Prüfungen; verschachtelte Agenten zählen mit. Ein neuer Review-Typ schafft kein neues Kontingent.
2. Vor einer dritten gleichartigen Korrekturrunde oder weiterem Helferneubau einen begrenzten Methodenwechsel verlangen: brauchbaren Stand sichern, wiederkehrende falsche Zuordnung und betroffene Kriterien/Inhalte benennen, Ursache/ungeeignete Annahme prüfen und eine explizite Restarbeitsliste mit begrenzten Paketen, Ergebnisverträgen und repräsentativen vollständigen Fällen vorlegen. Bestehende deterministische Helfer wiederverwenden, sofern geeignet.
3. Auftrag mit neuer Request-ID und konkretem Nachweisdelta checkpointen und an denselben Worker senden. Keine vorweggenommene Fehlerursache behaupten. Pflichtprüfungen innerhalb der Kapazität sequenziell durchführen oder warten lassen; nicht streichen.
4. Umverteilung nur nach bestätigter Freigabe und Ruhe beim bisherigen Kontingentinhaber. Kein Nachweis dafür liegt vor. Keine zusätzliche Nutzerfreigabe für einen innerhalb bestehender Autorisierung möglichen Methodenwechsel erfinden; eine echte Umfangs-/Berechtigungserweiterung wäre gesondert zu klären.
5. Korrekturrunden, Helferwachstum und Allowances dokumentieren. Tokenzähler als nicht verfügbar markieren; keine Transkriptsuche, erfundenen Schwellen/Budgets oder Abbruch wegen vermuteten Verbrauchs.

**Turnende:** Nicht vor der begrenzten Methoden-/Nachweisentscheidung und Verarbeitung des Folgeauftrags. Danach ausschließlich nach dem dokumentierten Fortsetzungsmodus; da dieser in F fehlt, kein automatisches Turnende ableiten. Das Kapazitätslimit ist kein Grund, ungelöste lokale Arbeit als extern blockiert oder erledigt zu markieren.

**Regeln:** `efficient-execution.md`, „Early evidence and controlled expansion“, „Repair and consumption signals“; `parallel-delivery.md`, Reservierungsfreigabe.

## G — Sequenzkollision, danach Lücke

1. `repair-4/seq1` mit Manifest B kollidiert mit dem konsumierten `seq1`/A: gleiche Ereignisidentität, anderer Payload. Mechanisch **blocked: sequence reused with different content**. Es ist weder ein harmloses Duplikat noch ein neuer Bericht. Receipt A unverändert erhalten; den abweichenden Bericht zur Klärung bewahren.
2. Genau Worker11, seine unveränderlichen Ereignis-/Ergebnisdateien und die relevante Request-Historie fokussiert lesen. Korrekturen erfordern eine neue Sequenz; keine stille Mutation des alten Receipts akzeptieren. Nicht aus dem fehlenden zweiten Ledger-Schreiber auf eine gültige Ereignisfolge schließen.
3. Solange Receipt A/seq1 die belegte Basis bleibt, ist das nachfolgende `seq3`/C ebenfalls **blocked: event sequence gap**. Fehlendes `seq2` gezielt wiederherzustellen versuchen. Da es laut Fall nicht vorhanden ist, alternativ eine aus verifizierter Worker-Historie ausdrücklich begründete Receipt-Basis rekonstruieren; erst danach das spätere Ereignis inhaltlich bewerten. Eine solche Historienverifikation ist nicht als Fakt gegeben und darf nicht fingiert werden.
4. Ohne hinreichende Klärung Receipt und abhängige Aktion unverändert halten, Protokollproblem und konkreten Recovery-Bedarf speichern. Kein blindes Überschreiben mit B oder C, keine zweite Workerinstanz. Auch bei nur einem Ledger-Schreiber revisionsgeprüfte atomare Checkpoints verwenden.

**Turnende:** Nicht vor der fokussierten Reconciliation. Bleibt sie erfolglos, abhängigen Fortschritt stoppen und nur mit einem tatsächlich nutzbaren dokumentierten Fortsetzungsweg zurück in den Wartezustand gehen; sonst aktiver Warte-Fallback bei autonomem Auftrag. Die Fallangaben liefern weder eine gültige neue Receipt-Basis noch einen Hintergrund-Wake und rechtfertigen deshalb kein bedingungsloses Turnende.

**Regeln:** `worker-events.md`, Ereignisidentität/Unveränderlichkeit und Verbrauchsschritt 3; `local-helpers.md`, Konflikt/Lücke; `recovery-and-state.md`, revisionsgeprüfte Checkpoints.

## Mechanische Gegenprüfung

Der lokale, rein lesende `batch_state.py classify-event` wurde ausschließlich mit synthetischen JSON-Eingaben im Ausgabeverzeichnis ausgeführt:

| Fall | Helper-Ergebnis | Exitcode |
| --- | --- | --- |
| A | `new` | 0 |
| B, aktueller Request `complete-2` | `stale` | 0 |
| G, seq1/B gegen seq1/A | `blocked`, conflicting payload | 2 |
| G, seq3/C gegen seq1/A | `blocked`, sequence gap | 2 |

B wurde ohne aktuelles `--previous` klassifiziert: das frühere `implement-1`-Receipt gehört in die Historie, nicht als Receipt zum neuen Request `complete-2`. Die Ergebnisdateien `*-classification.json` enthalten die unveränderte Helferausgabe. Phasen-/Pfadfelder der synthetischen Eingaben dienen nur der gültigen Hülle; sie sind keine zusätzlich ermittelten Fallbelege. Der Helper überprüft keine echte Datei, Senderidentität, Fachlichkeit oder Berechtigung.
