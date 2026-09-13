## Context

Daniel hat Karpathys Konzept und Atomicstratas Implementierung gewählt. Grundlage ist Commit `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb`; die [Schnittstellenprüfung](../../../../docs/rag/2026-09-12-atomicstrata-integrationsschnittstellen.md) dokumentiert den tatsächlichen Stand. Die bestehenden Markdown-Repos sind externe, weitergepflegte Fachquellen. Das Wiki ist eine zusätzliche lokale Schicht im Obsidian-Vault und kein eigenes Git-Repo. Das [QMD-Betriebsmodell](../../../../docs/rag/operating-model-rag-qmd.md) verlangt eine einzige persistierte Retrieval-Engine.

Atomicstrata verarbeitet echte Dateien unter seinem Quellenroot, keine Symlink-Sammlung externer Repos. Sein SDK bietet Compile ohne Embeddings; die verbleibende Indexerzeugung schreibt eine Markdown-Inhaltsübersicht. Native Query-/Save- und Remove-/Refresh-Abläufe haben hingegen eigene Retrieval-/Embedding-Effekte, die für die Integration nicht unverändert nutzbar sind. Gespeicherte Query-Seiten werden von der Freshness-Prüfung nicht wie Konzeptseiten behandelt. Ein installierbarer Upstream ist damit die Compilerbasis, noch nicht die fertige Kontextintegration.

## Goals / Non-Goals

**Goals:**

- Echte gemeinsame Synthese und Wiederverwendung aus mehreren externen Markdown-Repos.
- Nachvollziehbare Korrektur und Entzug entlang Quelle–Konzept–gespeicherte Antwort.
- Git-freie lokale Wiki-Ausgabe, Obsidian-Einstieg und QMD-basierter Agent-Zugriff.
- Kleine nachvollziehbare Adapter um vorhandene Compilerfunktionen und öffentliche End-to-End-Verifikation.

**Non-Goals:**

- Neuer Compiler, alternatives Wiki-Produkt, allgemeine Ontologie oder neue Suchplattform.
- Automatische Veränderung der Fachrepos, Umzug bestehender Clones oder Umschaltung heutiger Automationen.
- Neues Obsidian-Plugin, eigener Viewer, Pflicht-MCP-Transport oder automatische Dateiwächter.

## Decisions

### 1. Ein öffentliches Integrationsmodul

Die verwaltete Oberfläche ist eine lokale CLI über einem TypeScript-Modul. Ihre logischen Operationen sind Setup, Reconcile/Maintain, Status, Query/Save und Lint. Diese Namen beschreiben den neuen Adaptervertrag, keine behaupteten Upstream-Kommandos. Agenten können die CLI direkt aufrufen; dadurch gibt es zunächst eine gemeinsame Testschnittstelle für Quellenabgleich, Compiler, Quellenabhängigkeiten und Retrieval.

Das Modul ruft öffentliche SDK-Funktionen für Ingest, Source-Operationen, Compile und lesende Operationen auf. Es nutzt den echten Upstream und pinnt die Abhängigkeit. Ein Source-Code-Checkout darf seinerseits versioniert sein; der erzeugte Wiki-Bereich wird dadurch nicht zum eigenen Git-Repo. Eine passende Node-Runtime (Upstream verlangt mindestens Node 24) wird lokal isoliert bereitgestellt. Der Provider bleibt konfigurierbar; vorhandene Codex-/Claude-Zugänge können nach tatsächlichem Preflight genutzt werden.

Alternative: native CLI-Kommandos unverändert verketten. Verworfen als alleinige Lösung, weil Refresh/Remove/Query zusätzliche Embeddings erzeugen können und die Query-Abhängigkeiten fehlen. Es bleibt möglich, einen schmalen Upstream-Hook zu ergänzen und darüber weitere native Abläufe wiederzuverwenden.

### 2. Gerichteter Quellenadapter

`Meetings` und `Projects` sind ausdrücklich verpflichtende initiale Inhaltszonen des Vault-Roots. Ihre Markdown-Dateien werden rekursiv eingelesen; eine gesonderte Auswahl einzelner Meetings ist nicht erforderlich. Die private Projektzone wird im privaten Kontext ebenfalls aufgenommen. Fehlende eigene Git-Wurzeln oder gemischte Themen rechtfertigen keinen Ausschluss dieser Ordner.

Die [initiale Repo-Liste](../../../../.scratch/contextual-llm-wiki/input-repositories.md) definiert die acht bestätigten Wurzeln und ihre Startfilter. Sie wird als lokale Startkonfiguration ausgeliefert, statt die Repo-Auswahl erst dem Implementierungsagenten zu überlassen. Vault-Zonen ohne eigene Git-Wurzel behalten die Identität `vault-root`; der gemeinsame zweite Shared-AI-Checkout und erzeugte Test-Repos werden ausgeschlossen. Der private Umfang ist separat registriert. Eine Inventur vor dem ersten Compile zeigt die konkrete Auswahl und ihre Ausschlüsse.

Kontextkonfiguration und lokaler Laufzustand werden getrennt. Die Konfiguration enthält Kontext-ID, stabile Repo-ID, Clone-Pfad, Markdown-Filter und Scope. Der Laufzustand enthält je Fachquelle Originalpfad, Hash des tatsächlichen Arbeitsbaum-Inhalts, beobachteten Commit als Zusatzinformation und Compiler-Quellen-ID. Uncommitted Markdown-Korrekturen werden deshalb nicht durch einen unveränderten Git-HEAD übersehen.

Ausgewählte Markdown-Dateien werden als echte, zeilenerhaltende Eingaben gespiegelt; Identitäten verwenden Repo und relativen Pfad statt blossen Dateinamen. Ein vollständiger Scan liefert ein Änderungsset. Ein Scannerfehler liefert keinen leeren Kontext. Ein nachweislich fehlender Clone oder ausdrückliche Abwahl bewirkt Kontextentzug. Explizit konfigurierte neue Clones werden beim nächsten Aufruf aufgenommen; die Integration durchsucht nicht ohne Scope sämtliche Repos.

Spiegel und Laufmetadaten werden aus der aktiven Wiki-QMD-Collection ausgeschlossen. Citations bekommen einen Weg zurück zur Originalquelle, damit der interne Spiegel nicht zur menschlichen Hauptablage wird. Weder Symlinks auf fremde Schreibbereiche noch Umzüge von Fachrepos sind erforderlich.

### 3. Abhängigkeiten als Ergänzung des Compilerzustands

Konzeptabhängigkeiten werden aus dem vorhandenen Source-Ownership und den Zitaten übernommen. Für jede gespeicherte Antwort werden die tatsächlich verwendeten Page-IDs/Versionen und alle transitiven Quellenstände festgehalten. Bereits die Evidenzübergabe muss die IDs liefern; ausschliesslich die fertige Antwort nach Quellenlinks abzusuchen reicht nicht.

Wenn nicht zuverlässig unterschieden werden kann, welche der übergebenen Quellen eine Antwort tatsächlich trägt, gilt die ganze übergebene Evidenzmenge als Abhängigkeit. Das kann zusätzliche Prüfungen auslösen, verhindert aber unbegründete Aktualitätszusagen. Dieser begrenzte Dependency-Graph dient der Pflege, nicht als neue Such- oder Wissensdatenbank. Ein Claim pro atomarer Aussage ist nicht erforderlich; betroffene Passagen werden soweit vorhanden aus Zitaten angezeigt, die sichere Invalidierung erfolgt auf Seitenebene.

Unbekannte Abhängigkeiten sind sichtbarer Prüfbedarf. Sie werden weder als leere Menge noch als dauerhaft frischer Inhalt behandelt. Normale Query-Antworten werden nur auf Save-Anforderung gespeichert. Der im Original vorgesehene Dialog kann somit weiter Wissen erzeugen, ohne die Quellennachpflege zu umgehen.

### 4. Veröffentlichte Seiten und Nachpflege

Der verwaltete Arbeitsbereich unterscheidet Compiler-/Stagingzustand, aktive Wiki-Seiten und lokalen Sicherungszustand. Physische Unterverzeichnisse werden bei Umsetzung bestimmt. Als lokaler Standard eignet sich ein im Vault bereits aus Versionierung ausgeschlossener Shared-Bereich; dies muss vor Einrichtung am tatsächlichen Vault-Git geprüft werden. Es wird keine neue Wiki-Git-Wurzel initialisiert.

Der Ablauf ist: vollständige Quelleninventur → Änderungs-/Entzugsmenge → betroffene Abhängigkeitsmenge → betroffene aktive Seiten ungültig setzen/bei Entzug aus der aktiven Sicht nehmen → Quellenstand abgleichen → echte Compiler-Nachpflege → gespeicherte Antworten prüfen → vollständige Seiten samt Abhängigkeiten veröffentlichen → QMD synchronisieren → vollständigen Erfolg melden.

Bei Quellenkorrekturen verhindert die Agent-Schnittstelle eine unqualifizierte Ausgabe ungeprüfter Seiten. Obsidian zeigt den letzten Pflegezeitpunkt und offene Prüfungen. Ohne laufenden Watcher ist vor dem nächsten Pflegeaufruf keine Echtzeitaktualität garantiert. Bei Kontextentzug werden betroffene aktive Dateien entfernt beziehungsweise vorübergehend ausserhalb des aktiven Wiki-Baums gehalten. Gemischte Konzepte entstehen neu aus verbleibenden Quellen, gespeicherte Antworten mit verlorenen benötigten Inputs werden zurückgezogen. Ein Frontmatter-Orphan-Flag genügt nicht.

Der Agent-Zugriff prüft dazu die relevanten Originalquellen gegen die gespeicherten Abhängigkeiten, nicht nur den zuletzt synchronisierten Spiegel. Erkennt er vor der nächsten Pflege eine Abweichung, meldet er Prüfbedarf oder verwendet aktuelle Originale; er startet nicht zwingend eine Modellkompilierung für jede Frage.

Ein Lauf sperrt konkurrierende Schreiber desselben Kontexts und hält begonnenen/bestätigten Quellstand sowie offene Seiten-/Indexarbeit fest. Vor Veröffentlichung wird der Inputstand erneut abgeglichen. Fehler dürfen keinen neueren Hash als erfolgreich geprüft bestätigen. QMD-Ausfälle lassen den Lauf unvollständig; managed Agent-Abfragen filtern zusätzlich gegen das aktive Seitenregister. Erzwungene Konsistenz aller Rohdateisystem-Leser mitten im Lauf ist keine zugesagte atomare Datenbanktransaktion.

### 5. QMD und Query/Save

SDK-Compile verwendet `embeddings: false`. Die erzeugte Markdown-Indexseite bleibt erhalten: Sie erfüllt Karpathys Navigation und ist kein zweiter maschineller Retrieval-Index. Der tatsächliche problematische Pfad ist native Query/Save beziehungsweise Remove mit Embedding-Aktualisierung.

Für diese Operationen soll bevorzugt eine kleine injectable Retrieval-/Save-Grenze an Atomicstrata ergänzt werden: QMD liefert aktive, kontextgeprüfte Evidenz und stabile Seitenreferenzen; Speichern übernimmt das Abhängigkeitsregister ohne Compiler-Embeddings. Der Upstream hat diesen Hook am gepinnten Stand noch nicht. Als alternative Ausführung kann der vorhandene Agent QMD-Evidenz verarbeiten und seinen Entwurf über die Integrations-Save-Operation einreichen. Beide Varianten müssen denselben Kontext-/Abhängigkeitsvertrag durchsetzen; ein zweiter nachgebauter Recherchecompiler ist ausgeschlossen. Die Wahl des kleineren Eingriffs wird in der ersten technischen Slice dokumentiert und ist keine neue Produktentscheidung.

Compile selbst darf weiterhin alle wirklich neuen/ausstehenden Quellen verarbeiten. Für gezielte Nachpflege werden vorhandene betroffene Compiler-Quellen markiert beziehungsweise über einen nötigen SDK-Refresh-Hook verarbeitet; die CLI-only-Refresh-Logik wird nicht blind unter Umgehung der Indexregeln aufgerufen. Quellenentzug erfordert zusätzliche aktive Seitenbereinigung, weil SDK-Orphan-Markierung allein Obsidian-Dateien nicht entfernt.

Die Wiki-Collection und ihre Ausschlüsse werden explizit in die bestehende QMD-Konfiguration eingebunden. Ein fremder Collection-Konflikt blockiert die Einrichtung statt stilles Repointing. Entfernte aktive Dateien müssen aus den echten QMD-Ergebnissen verschwinden; ein Quellenregister-Flag ersetzt diesen Nachweis nicht. Änderungen an der zuständigen QMD-Konfiguration bleiben dort nachvollziehbar, während Integrationscode im Shared-AI-Repo liegt.

### 6. Abnahme und Wiederherstellung

Die Tests verwenden zwei kleine Git-Quellrepos und die echte Integrations-CLI. Ein kontrollierter Modellprovider erlaubt deterministische Nachpflege- und Fehlerfälle, mindestens ein echter Providerlauf zeigt fachliche Synthese. Echte QMD-Ergebnisse und eine Obsidian-Sichtprüfung ergänzen diese Grenze; ein Mock-UI oder Scheincompiler kann sie nicht ersetzen. Das Muster separater Prozessclients aus den vorhandenen Control-Plane-Black-Box-Tests dient als Vorbild.

Lokale Sicherungen liegen ausserhalb des aktiven Wissens-/Suchbereichs. Sie enthalten Wiki und Abhängigkeiten, nicht nur rekonstruierbare Quellenkopien. Ein Restore muss zuerst den aktuellen Repo-Kontext abgleichen und darf entzogene Antworten nicht aktivieren. Eine Rückkehr von Quellen ist von einem Restore alter Antworten zu unterscheiden; neue LLM-Ausgaben müssen nicht textidentisch sein.

## Risks / Trade-offs

- [Quellenadapter verdoppelt Quelldateien lokal] → Kopien klar als Betriebsinput kennzeichnen, aus Wiki-Retrieval ausschliessen und Originalbelege erhalten.
- [Gepinnter Upstream besitzt noch keinen öffentlichen QMD-/Save-Hook] → Technisch schmalen Patch oder bestehenden Agent-plus-Save-Pfad verwenden; Upstream-Diff und Kompatibilität nachweisen.
- [Konservative Antwortabhängigkeiten ziehen mehr Seiten zurück] → Korrektheit priorisieren, Umfang der verwendeten Evidenz klein halten und Mehrarbeit offen im Laufbericht zeigen.
- [LLM prüft eine korrigierte Aussage falsch] → Deterministische Datenflusschecks durch konkrete fachliche Vorher-/Nachher-Abnahme mit echtem Provider ergänzen; kein Wahrheitsgarantieversprechen.
- [QMD/Obsidian sind keine gemeinsame transaktionale Datenbank] → Entzug und Publishing geordnet durchführen, Restarbeit sichtbar halten, Erfolg erst nach überprüfter Suchsynchronisation melden.
- [Quellen ändern sich während der Pflege] → Erfasste Hashes vor Veröffentlichung vergleichen und neuere Arbeit pending lassen.

## Migration Plan

1. Isolierten Testkontext mit dem gepinnten Compiler einrichten, Quellen-/Index-Schreibgrenzen beweisen.
2. Adapter und Abhängigkeiten in kleinen TDD-Slices entwickeln; zuerst vollständige Quelle–Synthese–Korrektur-Kette.
3. QMD/Query/Save sowie Entzug/Wiederaufnahme durch dieselbe Oberfläche prüfen.
4. Mit ausgewählten realen Fachquellen im bestehenden Vault und echtem Provider abnehmen; Obsidian-Evidence erfassen.
5. Betriebsdokumentation und lokale Sicherung/Wiederherstellung prüfen. Bestehende Quellenautomationen weiterlaufen lassen.

Rollback entfernt oder deaktiviert nur den neuen Wiki-Einstieg, die neue Integration und ihre eigene QMD-Sicht. Originalquellen und fremde Collections bleiben unverändert. Ein Stand mit unvollständiger Nachpflege wird nicht als aktuelle Wiederherstellung veröffentlicht.

## Open Questions

Keine neue Produktentscheidung blockiert die Spec. Konkrete CLI-Namen, Speicherformat, Standardausgabepfad und die kleinste öffentliche QMD-/Save-Erweiterung sind Umsetzungsauswahl innerhalb des beschriebenen Vertrags. Runtime/Provider, Quellen-/Antwortnachpflege und QMD-Entzug sind in der [ausgeführten Abnahme](../../../../contextual-llm-wiki/evidence/acceptance.md) belegt. Auch die Obsidian-Sichtprüfung ist nach manuellem Entsperren über den tatsächlichen Klickweg abgeschlossen und mit drei echten Screenshots belegt.
