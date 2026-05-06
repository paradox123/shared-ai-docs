**Date:** 2026-05-04  
**Status:** 🟠 Plan  
**Scope:** Konsolidierte v2-Master-Spec fuer den Free-Entry-Flow der Mittelstand KI-Startbahn: Nutzerpfad, Survey, LLM-Aktivierung, lokale KI-Arbeitsumgebung, RAG/ROI, Report, Sicherheits- und Runtime-Vertraege.

---

## 1. Zweck

Diese Master Spec konsolidiert die bisherigen Free-Entry-Specs und das fuehrende Dokument:

`/Users/dh/Documents/DanielsVault/ki-fuer-kmu/v2/docs/APPLICATION-FLOW.md`

Sie ersetzt die alte Steuerungslogik als fachlich fuehrendes Zielbild. Alte Specs bleiben als Detailquellen erhalten, duerfen aber nach fachlicher Freigabe dieser Master Spec nicht mehr direkt als Implementierungsquelle genutzt werden, wenn sie der hier beschriebenen Reihenfolge widersprechen.

Ziel ist ein vertrauenswuerdiger Free Entry, der einen Interessenten lokal durch Profil, Betrieb, Survey, KI-Zugang, signiertes Content-Bundle, Arbeitsumgebung, Dokumentenlage, ROI-Bewertung und naechsten Schritt fuehrt, ohne Zahlungsdaten im Script abzufragen, ohne Anbieter-Subscription weiterzugeben, ohne dein IP breit oeffentlich zu publizieren und ohne produktive Kundensysteme zu veraendern.

## 2. Fuehrende Reihenfolge

Der Nutzerpfad ist verbindlich:

1. Interessent oeffnet Einstiegsseite.
2. Interessent startet den lokalen Assistenten.
3. Assistent fragt User-Profil und Betriebstyp ab.
4. Assistent prueft nur, ob ein bestehender kunden-eigener LLM-Zugang bereit ist; kein Zahlungsdialog, kein Accountsetup.
5. Wenn kein LLM bereit ist: Einsteiger-Survey als fester Default.
6. Wenn LLM bereit ist: lokale KI-Arbeitsumgebung vorbereiten, Profil/Betrieb mit LLM interpretieren, passenden Fragepfad waehlen.
7. Survey laeuft im Browser: bevorzugt ueber Survey-Delivery-Service, alternativ lokal als Fallback.
8. Regulatorik-/KRITIS-Fragen erscheinen nur im relevanten Survey-Pfad; nicht relevante Pfade fragen sie nicht.
9. Survey endet; Antworten werden als kanonisches Artefakt lokal uebernommen.
10. Erst wenn `survey/answers.json` lokal importiert und geprueft ist, gelten die Antworten als strukturiert vorliegend.
11. Wenn noch kein LLM bereit ist: Empfehlung und Aktivierung eines passenden Zugangs.
12. Nach lokaler LLM-Konfiguration: Readiness-Test mit einfachem nicht-kundenspezifischem Prompt.
13. Erst bei erfolgreichem Test: `provider_ready=true`.
14. Danach signiertes Free-Entry-Bundle oder freigegebenen Managed-AI-Updatekanal pruefen, falls die Arbeitsumgebung noch nicht bereit ist.
15. Danach lokale KI-Arbeitsumgebung aus Bundle-Manifest vorbereiten, falls noch nicht vorhanden.
16. Optional: ROI-Agent schlaegt wenige Zusatzfragen im Survey-Schema vor; Anwendung stellt sie im passenden Sprachstil.
17. Dokumentationslage auswerten.
18. Nur mit aktivem LLM und Freigabe: Dokumente lesen, extrahieren, normalisieren und fuer RAG vorbereiten.
19. Wenn keine Dokumentation vorhanden ist: Survey-Antworten und Annahmen bilden die ROI-Grundlage.
20. ROI-Agent wertet Antworten, Dokumente, Annahmen und Erfahrungswerte aus.
21. Report zeigt Chancen, Risiken, ROI-Bandbreite, Annahmen und naechsten Schritt.
22. Nutzer kann dich kontaktieren/beauftragen, Workshop buchen, Pilot starten oder mit der lokalen KI-Plattform selbst weiterarbeiten.

## 3. Non-Goals

- Keine Kreditkarten- oder Zahlungsdatenerfassung im Download-Script, Starter, Wizard oder lokalen Agenten.
- Keine Weitergabe deiner Provider-Subscription oder deiner API-Keys an Interessenten.
- Keine automatische Provider-Account-Erstellung im Namen des Nutzers.
- Keine produktiven Aenderungen an Kundensystemen im Free Entry.
- Keine RAG-/Dokumentenaufbereitung ohne aktiven LLM-Zugang und Freigabe.
- Kein Agent, der den kompletten Survey frei als Chat fuehrt.
- Keine stille Installation beliebiger Obsidian-Community-Plugins.
- Kein Managed Gateway im Free Entry ohne bezahlten, budgetierten Pilotvertrag.
- Keine Klartext-Tokens in Manifesten, Logs, Reports, Registrierungsdaten oder Download-Scripten.
- Keine breite Veroeffentlichung deiner gepflegten Skill-/Kontext-/Agenten-Repositories als Nebenwirkung des Free Entry.

## 4. Nutzer- und UX-Anforderungen

### V2-FR-001 Einsteigerverstaendlicher Start

- Der interaktive Standardpfad laeuft im Browser-Wizard; CLI bleibt Fallback fuer Support und Automation.
- Die Anwendung fragt zuerst User-Profil und Betriebstyp in verstaendlicher Sprache.
- Jeder Schritt zeigt, ob er `read-only`, `dry-run`, `setup` oder `LLM-Modellnutzung` ist.
- Fehlermeldungen nennen Problem, Auswirkung und naechsten sinnvollen Schritt.

### V2-FR-002 Profil- und Betriebstyp-Routing

- User-Profil bestimmt Sprache und Erklaertiefe.
- Betriebstyp bestimmt, welche Fragepfade fachlich sinnvoll sind.
- Typische nicht regulierte Betriebe wie Fitnessstudio, Handwerk oder Agentur erhalten keine direkte KRITIS-Frage im Standardpfad.
- Energieversorgung, gesundheitsnahe Organisationen, oeffentliche Verwaltung und unklare Mischformen koennen in strengere Pfade wechseln.
- Dies ist keine Rechtsbewertung; bei Unsicherheit fragt die Anwendung nach oder wechselt vorsichtig in einen strengeren Pfad.

### V2-FR-003 Entry, Download und Registrierung

- Die Einstiegsseite stellt versionierte Download-Artefakte fuer macOS und Windows bereit.
- Download-Metadaten enthalten mindestens `version`, `sha256` und `updated_at_utc`.
- Der Browser-Wizard ist die primaere interaktive UX; CLI bleibt Support-/Automation-Fallback.
- Der Starter prueft vor Ausfuehrung Schreibrechte, benoetigte lokale Runtime, Integritaet des Payloads und optional Register-Erreichbarkeit.
- Bei Hash-Mismatch stoppt der Starter vor Runner-Start mit Exit `20`.
- Der Starter nutzt einen stabilen lokalen Arbeitsbereich, zum Beispiel `.kickstart`, und wiederverwendet eine vorhandene `site_id`.
- Registrierung ist best-effort. Wenn Register nicht erreichbar ist, laeuft der lokale Flow mit `registration_status=offline_fallback` weiter.
- Register-Payload enthaelt keine Secrets und keine Hardware-Fingerprints.
- Server-Komponenten wie Landing, Register und Survey-Delivery-Service laufen reproduzierbar ueber Docker Compose.
- Kein nativer MSI/PKG-GUI-Installer und kein OS-Daemon sind Teil dieses v2-Free-Entry-Plans.

### V2-NFR-UX-001 Bedienbarkeit und Messbarkeit

- Wizard-Screens sollen eine Frage oder eine kleine zusammenhaengende Fragegruppe zeigen.
- Jeder Screen hat Fortschritt, klare Hilfe und eine kurze Erklaerung, warum die Information benoetigt wird.
- Fachbegriffe werden fuer Profil `A` vermieden oder direkt erklaert.
- Abbrueche werden mit `screen_id`, `reason_code` und Zeitstempel erfasst, ohne personenbezogene Zusatzdaten zu sammeln.
- Der verkürzte Wizard-Smoke (`dry_run + smoke_token + manifest echo`) bleibt als technischer E2E-Test erhalten, ersetzt aber keine vollstaendige Survey- und Kontrollfluss-Harness.

## 5. Survey

### V2-FR-010 Survey-Definition

- Der Survey wird von der Anwendung programmatisch im Browser gefuehrt.
- Die Survey-Inhalte werden in drei fachlichen Varianten gepflegt.
- Im bevorzugten Online-Modus rendert ein Survey-Delivery-Service die Survey-Seiten als HTML aus der jeweils freigegebenen Survey-Version.
- Im lokalen Fallback-Modus duerfen gepinnte Survey-Definitionen oder statische lokale Survey-Seiten aus Package oder Content-Bundle genutzt werden.
- Wenn maschinenlesbare lokale Definitionen genutzt werden, heissen die Dateien normativ:
  - `survey-v2-a-einsteiger.json`
  - `survey-v2-b-anwender.json`
  - `survey-v2-c-technisch.json`
- Die drei Varianten heissen:
  - `A` Einsteiger: einfache Sprache, Beispiele, keine unerklaerten Fachbegriffe.
  - `B` Anwender: normale Sprache mit kurzen Erklaerungen.
  - `C` Technisch versiert: kompakter, optionale technische Vertiefungen.
- Alle Varianten erfassen denselben fachlichen Pflichtkern.
- Der vorhandene Katalog `03-product/survey-v1-final.md` ist Inhaltsquelle, muss aber in neue Reihenfolge und maschinenlesbare Definition migriert werden.
- Survey-HTML, Survey-Version, Render-Modus (`server_rendered` oder `local_fallback`) und Datenverarbeitungsstatus muessen nachvollziehbar protokolliert werden.

### V2-FR-010a Survey-Delivery-Service und Antwortdaten-Uebergabe

ADR `v2/docs/adr/003-survey-delivery-and-answer-handoff.md` entscheidet den Hybridpfad:

- Online: Survey-Delivery-Service rendert HTML, speichert Antworten nur als temporaeren Session-Zwischenstand und erzeugt nach Abschluss ein kanonisches Antwortartefakt.
- Lokal: .NET-Starter oder lokale Wizard-Huelle uebernimmt das Antwortartefakt automatisch in die lokale KI-Arbeitsumgebung.
- Fallback: lokale Survey-Definition oder lokale Survey-Seiten erzeugen dasselbe kanonische Antwortartefakt ohne Server.

Der Nutzer darf nicht manuell mit einer JSON-Datei arbeiten muessen. Die UI zeigt stattdessen einen verstaendlichen Status wie "Ihre Antworten wurden lokal in die Arbeitsumgebung uebernommen."

Normativer Handoff-Vertrag:

- Der Server erzeugt nach Survey-Abschluss ein kanonisches Antwortartefakt.
- Der .NET-Starter ruft dieses Artefakt mit einem kurzlebigen Handoff-Token ab.
- Der .NET-Starter prueft Integritaet, Survey-Version, Schema-Version und Vollstaendigkeit.
- Bei erfolgreicher Pruefung schreibt der .NET-Starter lokal `survey/answers.json` und `survey/import-manifest.json`.
- Erst danach duerfen LLM-Aktivierung, Repo-/Content-Setup, RAG, ROI-Agent und Report mit den Survey-Antworten fortfahren.

Retention- und Datenschutzregeln:

- Serverseitige Survey-Antworten sind im Free Entry temporaere Session-Daten.
- Speicherdauer, Einwilligung und Loeschlogik muessen fuer den Nutzer verstaendlich erklaert werden.
- Nach erfolgreicher lokaler Uebernahme muss der Server den temporaeren Antwortstand loeschen oder nach dokumentierter Einwilligung minimal weiterhalten.
- Der Server darf keine Provider-Secrets, lokalen Host-Secrets oder Dokumentinhalte als Teil des Survey-Handoffs erhalten.

Fehlerfaelle:

- Wenn der Server nicht erreichbar ist, muss lokaler Fallback oder spaeter fortsetzen angeboten werden.
- Wenn Export, Download, Hash-/Signaturpruefung oder lokaler Import fehlschlaegt, wird kein `survey_import_status=imported` gesetzt.
- Bei fehlendem lokalen `survey/answers.json` duerfen RAG/ROI nicht starten.

### V2-FR-011 Survey-Inhalte

Der Survey muss mindestens erfassen:

- Betrieb, Ansprechpartner, Entscheidungsverantwortung.
- User-Profil und Betriebstyp.
- Branche, Groesse, Hauptleistungen, wichtigste Systeme.
- Ziele, Engpaesse, 1 bis 3 priorisierte Prozesse.
- Dokumentationslage und Dokumentpfade, falls vorhanden.
- Freigabe zur Dokumentaufbereitung, falls Dokumentation vorhanden ist.
- Daten-/Security-Hinweise in nutzerverstaendlicher Form.
- ROI-Mindestdaten pro priorisiertem Prozess oder begruendete Annahmen.
- Entscheidungsweg und gewuenschter naechster Schritt.

### V2-FR-012 Agent-Zusatzfragen

- Der ROI-Agent darf den Survey nicht frei "durchchatten".
- Nach Survey-Ende darf der ROI-Agent wenige Zusatzfragen vorschlagen, wenn ROI-Mindestdaten fehlen.
- Diese Zusatzfragen muessen in das Survey-Schema uebersetzt werden.
- Die Anwendung stellt sie im Browser und im Stil der gewaehlten Nutzerstufe.
- Einsteigerfragen muessen einfach bleiben und duerfen keine unrealistischen API-, KPI- oder technischen Detailfragen erzwingen.

## 6. LLM-Zugang und Provider-Aktivierung

### V2-FR-020 Aktivierungsstatus

Normative Statuswerte:

- `no_ai_runtime_yet`: Vorbereitung vorhanden, keine echte Modellnutzung.
- `guided_low_budget_api_setup`: Kunde richtet eigenen Free-/Trial-/Low-Budget-Zugang beim offiziellen Provider gefuehrt ein.
- `assisted_customer_setup`: Einrichtung erfolgt in Termin oder Supportpfad.
- `customer_owned_provider`: Kunde besitzt Provider-Account, Billing und API-Key.
- `managed_gateway_paid_pilot`: budgetierter Gateway-Zugang nur im bezahlten Pilot mit Vertrag/Freigabe.

### V2-FR-021 Readiness

Ein LLM gilt erst als bereit, wenn:

- Zugangsweg und Aktivierungsstatus dokumentiert sind.
- Key oder Gateway-Token nicht in Logs, Reports, Registrierung oder Ergebnisdateien erscheint.
- OS-Keychain/Credential Manager bevorzugt genutzt wird; explizite Env-Variablen oder projektlokale `.env` sind bewusste Fallbacks.
- Ein technischer Readiness-Test das Modell oder den Gateway erreicht.
- Der Readiness-Test einen einfachen, nicht-kundenspezifischen Prompt sendet und eine verwertbare Antwort erhaelt.
- Erst danach wird `provider_ready=true` gesetzt.

### V2-FR-022 Provider-Guardrails

- Free Entry darf ohne Provider-Zwang starten.
- Echte Prozessanalyse, Dokumenteninterpretation, RAG-Aufbereitung und ROI-Berechnung duerfen erst mit aktivem LLM laufen.
- Bei fehlendem oder fehlerhaftem LLM-Zugang entsteht ein Vorbereitungsreport mit Status `roi_blocked_provider_required` oder aequivalent.
- Managed Gateway ist im Free Entry blockiert und nur als bezahlter, budgetierter Pilot erlaubt.
- Provider-Empfehlung erfolgt nach Survey-Ende, weil dann Betrieb, Prozesse und Dokumentationslage bekannt sind.

### V2-FR-023 Provider-/Modell-Empfehlungsmatrix

Die konkrete Empfehlung muss nach Survey-Ende deterministisch aus Profil, Prozessanzahl, Dokumentationslage, erwarteter Modellnutzung, technischer Vorerfahrung und Wunsch nach Selbststaendigkeit abgeleitet werden.

Vorschlag fuer die erste Matrix:

| Fall | Empfehlung | Begruendung |
|---|---|---|
| Einsteiger, 1 bis 2 einfache Prozesse, keine oder wenig Dokumentation | `guided_low_budget_api_setup` mit OpenAI API als bevorzugtem Startpfad | Ein API-Key plus kleiner Budgetrahmen ist erklaerbar, testbar und fuer ROI-Smoke meist ausreichend. |
| Anwender, 1 bis 3 Prozesse, gemischte Dokumentation | OpenAI API oder Anthropic API, je nach Dokument-/Textlast und verfuegbarer Anleitung | Beide Pfade bleiben customer-owned; Auswahl erfolgt ueber gepflegte Provider-Guides. |
| Technisch versiert, vorhandener Firmenprovider oder vorhandene API-Governance | `customer_owned_provider` | Kunde nutzt eigenes Konto, eigenes Billing, eigenen Key und vorhandene Governance. |
| Nutzer will Einrichtung nicht selbst machen | `assisted_customer_setup` | Kein Script-Zahlungsdialog; Einrichtung erfolgt im Support-/Terminpfad. |
| Umfang, Datenschutz, Budget oder Dokumentenmenge passen nicht mehr zu Self-Service | `managed_gateway_paid_pilot` oder bezahlter Pilot | Nur mit Vertrag, Budgetlimit, Laufzeit und klarer Leistungsgrenze. |
| Kein geeigneter LLM-Zugang wird aktiviert | `no_ai_runtime_yet` | Vorbereitungsreport statt ROI-Behauptung. |

Die Matrix ist nicht im Code zu verstecken. Sie muss als versionierte Konfigurations-/Content-Datei gepflegt werden, zum Beispiel `config/provider-recommendation-matrix.v1.yaml`.

### V2-FR-024 Provider-Aktivierungsguides

Da beim Einrichten des ersten LLM-Zugangs oft noch kein LLM verfuegbar ist, darf die Assistenz an dieser Stelle nicht dynamisch per LLM aus dem Internet erzeugt werden. Stattdessen braucht jeder freigegebene Provider einen gepflegten Aktivierungsguide. Ein Developer Quickstart reicht fuer Einsteiger nicht aus; offizielle Quickstarts sind Quellenanker, aber nicht die eigentliche Nutzerfuehrung.

Ein Provider-Guide muss mindestens enthalten:

- `provider_id`
- `display_name`
- `target_user_profiles` (`A`, `B`, `C`)
- `recommended_for`
- `not_recommended_for`
- `official_signup_url`
- `official_api_key_docs_url`
- `official_billing_docs_url`
- Schrittfolge fuer Account/Billing/API-Key in drei Sprachvarianten.
- UI-Schritte im Stil "Klicken Sie auf ...", "Waehlen Sie ...", "Kopieren Sie ...", jeweils mit erwarteter Seite oder sichtbarem UI-Text.
- Hinweise, was nicht im Script eingegeben werden darf.
- Screenshot-/Bildreferenzen optional, mit `last_verified_at`.
- `last_verified_at`
- `owner`
- `review_interval_days`
- Fallback, wenn die Provider-Oberflaeche anders aussieht.

Die Guides muessen regelmaessig gepflegt werden, weil Provider-Oberflaechen, Preise, Modellnamen und Billing-Flows sich aendern koennen. Screenshots sind erlaubt, aber nicht die einzige Wahrheit; jeder Screenshot braucht Quelle, Datum und betroffenen Schritt.

Die Anwendung stellt diese Guides ueber einen Menuepunkt wie `KI-Zugang einrichten` bereit. Der Guide ist lokaler Content, kein LLM-Chat. Der Nutzer wird auf offizielle Provider-Seiten gefuehrt; Account, Billing und API-Key bleiben beim Nutzer.

Startvorschlag fuer Guide-Artefakte:

| Provider | Guide-Datei | Offizielle Anker |
|---|---|---|
| OpenAI API | `provider-guides/openai-api.v1.yaml` | Quickstart, API-Key, Billing/Usage/Pricing |
| Anthropic API | `provider-guides/anthropic-api.v1.yaml` | Console, API-Key, Quickstart, Billing/Usage/Pricing |
| Assisted Setup | `provider-guides/assisted-setup.v1.yaml` | Termin-/Supportpfad, keine API-Key-Eingabe im Script |
| Paid Pilot / Managed Gateway | `provider-guides/managed-gateway-paid-pilot.v1.yaml` | Vertrags-/Angebotspfad, Budgetlimit, Laufzeit, Gateway-Token erst nach Freigabe |

Provider-Guides sind Teil der gepflegten Content-Baseline und muessen mindestens bei jeder Release-Vorbereitung auf Aktualitaet geprueft werden.

Ein Einsteiger-Guide muss mindestens diese Abschnitte haben:

1. Was wird eingerichtet?
2. Was kostet es ungefaehr und wer bezahlt?
3. Was wird nicht im Script eingegeben?
4. Offizielle Seite oeffnen.
5. Konto erstellen oder einloggen.
6. Billing/Usage-Limit setzen.
7. API-Key erzeugen.
8. API-Key lokal im Assistenten hinterlegen.
9. Readiness-Test starten.
10. Was tun, wenn ein Schritt anders aussieht?

Die Guide-Texte muessen in drei Varianten gepflegt werden:

- `A` Einsteiger: Klickpfad, einfache Sprache, Screenshots bevorzugt.
- `B` Anwender: Klickpfad plus kurze technische Einordnung.
- `C` Technisch: kompakte Schritte, direkte Links, Sicherheits- und Scope-Hinweise.

### V2-FR-024a Visualisierung der Aktivierungsguides

Die Provider-Guides muessen ohne vorhandenes LLM funktionieren. Deshalb rendert die lokale Anwendung sie als lokalen Browser-Wizard oder lokale Hilfeseite aus gepflegtem Content, nicht als dynamische Chat-Antwort.

Ein visueller Guide muss mindestens unterstuetzen:

- Schritt-fuer-Schritt-Seiten mit einem klaren aktuellen Schritt.
- Screenshot-Assets pro kritischem Provider-Schritt, wenn die Provider-Oberflaeche fuer Einsteiger sonst zu schwer erklaerbar ist.
- Hervorgehobene Zielbereiche im Screenshot, zum Beispiel rote Rahmen oder Callouts fuer "hier klicken".
- Erwarteten sichtbaren UI-Text, damit der Nutzer erkennt, ob er auf der richtigen Seite ist.
- Eine "Schritt erledigt"-Bestaetigung pro Guide-Schritt.
- Einen Fallback-Abschnitt "Wenn es anders aussieht", mit offizieller Hilfeseite und Assisted-Setup-Option.
- `last_verified_at`, `source_url`, `screenshot_captured_at` und `review_interval_days` fuer jeden Screenshot-gebundenen Schritt.

Empfohlenes Content-Layout:

- `provider-guides/<provider-id>.v1.yaml` fuer Metadaten, Schritte, Profile, offizielle Links und Validierungsregeln.
- `provider-guides/content/<provider-id>/<profile>.md` fuer laengere erklaerende Texte je Nutzerprofil.
- `provider-guides/assets/<provider-id>/...` fuer Screenshots und Callout-Bilder.

Der Nutzer gibt Zahlungsdaten nur auf offiziellen Provider-Seiten ein, nie im lokalen Script. API-Keys werden nach Erzeugung lokal im Assistenten hinterlegt und anschliessend mit dem Readiness-Test geprueft.

## 7. Lokale KI-Arbeitsumgebung

### V2-FR-030 Vault und Arbeitsraum

Die lokale KI-Arbeitsumgebung gehoert dem Interessenten und bleibt auch ohne Folgeauftrag nutzbar.

Sie umfasst:

- lokalen Projekt-/Arbeitsordner.
- lokalen Obsidian Vault als Arbeits- und Wissensraum.
- lokale Provider-Konfiguration ohne Secret-Leakage.
- Ergebnisordner fuer Survey, Dokumente, RAG-Vorbereitung, ROI und Report.
- Versionsprotokoll der verwendeten Repos, Skills, Subagents, Context-Repos und Plugin-Baseline.
- lokalen Agenten, der diese Bausteine nutzen kann.

### V2-FR-031 Content-Bundle und optionale Repo-Quellen

ADR-001 ist fuehrend: Der v2-Default ist ein signiertes Free-Entry-Bundle mit spaeterem Managed-AI-Updatekanal. Es gibt keine hardcodierten Pflicht-Repositories im Code und keinen GitHub-Zwang fuer Einsteiger.

Das Content-Bundle:

- enthaelt freigegebene Startinhalte fuer Shared AI Docs, Skills, Subagents, Kontextpakete, Provider-Guides und Hilfsinhalte.
- enthaelt keine produktiven Secrets, keine Zahlungsdaten und keine eingebetteten Repository-Tokens.
- wird versioniert, signiert und mit Hash, Channel, Entitlement/Freigabe, Kompatibilitaet und erwarteten Dateien beschrieben.
- wird in den lokalen Obsidian Vault uebernommen, ohne lokale Kundenaenderungen still zu ueberschreiben.
- ist der Ausgangspunkt fuer den spaeteren Managed-AI-Updatekanal.

Optionale Arbeitsbereiche wie RAG-/RACK-Vorbereitung, n8n-Kontext, Automationspakete oder Dokumentenaufbereitung werden nur angelegt, wenn Survey-Antworten, Dokumentationslage oder Umsetzungspfad sie benoetigen.

Das Testrepo `https://github.com/paradox123/ai-test-repo.git` wird als oeffentlicher Testfall in die Harness aufgenommen. Es prueft Repo-Mechanik und erwartete Artefakte, ist aber kein Muster fuer die geschuetzte IP-Baseline.

### V2-FR-031a Bundle-Manifest und Readiness

Das Bundle-Manifest muss mindestens enthalten:

- `bundle_id`.
- `version`.
- `channel`, zum Beispiel `free-entry`, `paid-pilot`, `managed-ai`.
- `created_at`.
- `expires_at` oder explizit `no_expiry`.
- `sha256`.
- `signature`.
- `entitlement_ref` oder Freischaltstatus.
- `expected_files`.
- `compatibility`, mindestens Starter-/Spec-Version.
- `install_targets`, mindestens Vault-Unterordner.
- `conflict_policy`.

Die Anwendung muss:

- Hash, Signatur, erwartete Dateien und Kompatibilitaet pruefen.
- Bundle- und Installationsstatus im lokalen Laufmanifest dokumentieren.
- jeden Fehler secret-redacted und kundenverstaendlich loggen.
- bei fehlendem oder ungueltigem Bundle klar mit Exit `30` oder einem blockierten Arbeitsumgebungsstatus enden.
- keinen halb fertigen Vault als Erfolg melden.

### V2-FR-031b Managed-AI-Kanal und Git/GitHub-Spaeterpfad

Der Managed-AI-Kanal nutzt denselben Content-Mechanismus als Updatepfad. Nach Beauftragung, Pilot oder Managed-Service-Freigabe kann die bestehende lokale Arbeitsumgebung auf einen freigegebenen Updatekanal umgestellt werden.

Der Managed-AI-Kanal muss:

- Mandant/Freigabe, Channel, Bundle-Kompatibilitaet und Signatur pruefen.
- neue oder aktualisierte Skills, Subagents, Guides, Kontexte und Migrationshinweise als signierte Updates bereitstellen.
- lokale Kundenaenderungen erkennen und Konflikte sichtbar machen.
- Update-Regeln fuer manuelle, freigegebene oder managed-only Updates dokumentieren.

Git/GitHub ist kein Free-Entry-Default. Git/GitHub bleibt ein optionaler technischer Betriebs- oder Migrationspfad fuer spaetere Kundenbeziehungen, technische Nutzer oder Organisationen. Dieser Pfad braucht dann ein eigenes Credential-Modell, zum Beispiel `https_token`, `ssh_agent` oder `github_app`, und darf Tokens nur ueber Secret-Referenzen wie Keychain/Credential Manager verwenden.

### V2-FR-032 Obsidian-Plugin-Baseline

Community-Plugins sind ausfuehrbarer Code. Sie werden nicht still installiert, sondern als freigegebene Baseline mit Zweck, Version, Trust-Entscheidung und Fallback dokumentiert.

Baseline:

| Status | Plugins |
|---|---|
| Pflicht | `dataview` |
| Empfohlen | `metadata-menu`, `templater-obsidian`, `obsidian-tasks-plugin`, `obsidian-git`, `obsidian-linter` |
| Optional | `obsidian-kanban`, `obsidian-excalidraw-plugin`, `obsidian-charts`, `table-editor-obsidian` |

Versionierungsregel: Die Baseline nutzt keine fest gepinnte Version in dieser Master Spec. Fuer Neuinstallationen gilt `latest_approved` aus der freigegebenen Plugin-Baseline. Die tatsaechlich installierte Version wird im Laufmanifest oder Vault-Setup-Protokoll dokumentiert.

## 8. Dokumente, RAG und Quellenstatus

### V2-FR-040 Dokumentationslage

- Dokumente werden erst nach Survey-Ende verarbeitet.
- Dokumente werden nur verarbeitet, wenn LLM bereit ist und Freigabe vorliegt.
- Bei fehlender Prozessdokumentation nutzt der ROI-Agent Survey-Antworten, Erfahrungswerte und sichtbar markierte Annahmen.
- Bei verweigerter Dokumentfreigabe bleibt RAG aus.

### V2-FR-041 RAG-Status

RAG-Status muss mindestens unterscheiden:

- `disabled_no_docs`
- `disabled_no_approval`
- `prepared`
- `preprocessing_required`
- `unsupported_sources_present`

Bild-/Scan-lastige Quellen duerfen den Lauf nicht hart abbrechen, wenn ein Aufbereitungsagent fehlt. Sie werden als `preprocessing_required` markiert. Nicht unterstuetzte Formate werden als `unsupported_format` oder aequivalent berichtet.

## 9. ROI-Agent und Report

### V2-FR-050 ROI-Agent

- Der ROI-Agent benoetigt aktiven LLM-Zugang.
- Er darf Erfahrungswerte und Annahmen nicht als harte Source-Code-Konstanten verstecken.
- Annahmen muessen im Report sichtbar sein.
- Bewertet werden mindestens 1 und maximal 3 Prozesse.
- Der Agent beruecksichtigt Survey-Antworten, Dokumente, RAG-Status, Erfahrungswerte und Annahmen.

### V2-FR-051 ROI-Modell

Das bestehende ROI-Modell bleibt erhalten:

- Zeitersparnis ueber heutige Minuten, kuenftige Minuten, Wochenvolumen und Automatisierungsanteil.
- Monatsnutzen aus Zeitnutzen plus Qualitaetsnutzen.
- Netto-Nutzen nach laufenden Kosten.
- Initialinvestition aus Umsetzungskosten plus Enablement-/Change-Aufwand.
- Payback in Monaten.
- Bandbreiten konservativ, realistisch, optimistisch.
- Empfehlungen `jetzt`, `spaeter`, `verwerfen`.
- Prozesse ohne positiven Payback duerfen nicht als Top-1 empfohlen werden.

### V2-FR-052 Report

Der Report enthaelt:

- 1-Seiten-Zusammenfassung.
- 1 bis 3 Prozesskandidaten.
- ROI-Bandbreite je Kandidat.
- sichtbare Annahmen und Datenqualitaet.
- Risiken und Grenzen.
- Aktivierungsstatus und Provider-/LLM-Empfehlung, falls relevant.
- RAG-/Dokumentenstatus, falls relevant.
- klaren naechsten Schritt: Kontakt, Beratungstermin, Workshop, bezahlter Pilot, Umsetzung beauftragen oder selbst weiterarbeiten.

### V2-FR-053 Kundenverstaendliche Aktivierungs- und Vorbereitungsreport-Hinweise

Alle Aktivierungs- und Vorbereitungsreport-Texte muessen in drei Varianten gepflegt werden:

- `A` Einsteiger.
- `B` Anwender.
- `C` Technisch versiert.

Startvorschlag fuer `no_ai_runtime_yet`:

| Profil | Textvorschlag |
|---|---|
| A Einsteiger | "Wir haben Ihre Antworten gespeichert und die naechsten Schritte vorbereitet. Fuer eine echte Einschaetzung mit ROI brauchen wir jetzt einen KI-Zugang, der Ihnen gehoert. Ohne diesen Zugang kann der Assistent noch keine belastbare Nutzenrechnung erstellen." |
| B Anwender | "Der Survey ist abgeschlossen und die Arbeitsbasis ist vorbereitet. Fuer Dokumentauswertung, Annahmenbildung und ROI-Berechnung fehlt noch ein aktivierter LLM-Zugang. Sie koennen einen eigenen API-Zugang einrichten, Assisted Setup waehlen oder einen Pilot anfragen." |
| C Technisch | "Survey-Artefakte liegen vor, `provider_ready=false`. RAG/ROI bleiben blockiert, bis ein customer-owned Provider oder ein freigegebener Paid-Pilot-Gateway den Readiness-Test besteht. Secrets werden nicht in Logs oder Reports persistiert." |

Startvorschlag fuer erfolgreiche Aktivierung:

| Profil | Textvorschlag |
|---|---|
| A Einsteiger | "Der KI-Zugang funktioniert. Jetzt kann der Assistent Ihre Antworten und freigegebene Unterlagen auswerten und eine erste Nutzenrechnung fuer bis zu drei Prozesse erstellen." |
| B Anwender | "Der LLM-Readiness-Test war erfolgreich. Die lokale KI-Arbeitsumgebung wird vorbereitet, danach starten Zusatzfragen, Dokumentaufbereitung und ROI-Auswertung, soweit sie freigegeben sind." |
| C Technisch | "`provider_ready=true`. Workbench und Bundle-Manifest werden vorbereitet; anschliessend laufen optionale Survey-Nachfragen, RAG-Preprocessing und ROI-Agent im freigegebenen Scope." |

## 10. Technologie-Stack-Entscheidung

### V2-DEC-TECH-001 Starter-, Wizard- und Runner-Stack

ADR `v2/docs/adr/002-starter-wizard-runner-technology-stack.md` entscheidet den .NET-Weg fuer Starter, lokale Wizard-Huelle und Runner-Orchestrierung.

Die bisherige Node-/JSON-/Script-Umsetzung bleibt Prototyp-/Legacy-Stand und darf nicht als v2-Kundenstarter verfestigt werden. Shell-/Script-Pfade bleiben hoechstens fuer Entwicklung, Support oder Testautomation zulaessig.

Der Zielzuschnitt:

- moderner .NET-Starter fuer macOS/Windows.
- lokale Wizard-Huelle fuer Vertrauen, Setup, Systempruefungen, Provider-Guides und Fallbacks.
- server-gerenderter Survey als bevorzugter Online-Modus.
- lokaler Survey-Fallback fuer Safe-Test, Offline, Demo und sensible Pfade.
- dateibasierte Content- und Manifest-Verarbeitung fuer Bundles, Guides, Reports und Vault-Artefakte.
- Keychain/Credential-Manager-Abstraktion fuer Secrets.

Der Survey muss nicht zwingend als im Download-Package gebuendelte JSON gerendert werden. Im Online-Modus darf der Server aktuelle Survey-HTML-Seiten aus der freigegebenen Survey-Version ausliefern. Dadurch koennen Fragen, Hilfetexte, Routing und Provider-Hinweise aktualisiert werden, ohne das Kunden-Package neu zu bauen.

Der lokale Fallback bleibt verpflichtend fuer:

- Safe-Test-Harness.
- Offline-/Demo-Laeufe.
- kontrollierte Reproduzierbarkeit.
- sensible Pfade, in denen Survey-Antworten nicht serverseitig verarbeitet werden sollen.

Offene Umsetzungsfragen fuer den .NET-Spike:

| Kriterium | Zu klaeren |
|---|---|
| Einsteiger-UX | Wie wenig technische Vorinstallation braucht der Interessent? |
| Runtime-Abhaengigkeit | Node, .NET, Shell, Browser und Git: was muss vorhanden sein, was kann gebundelt werden? |
| macOS/Windows | Wie gut funktionieren Download, Start, Signierung/Notarisierung, Quarantaene und Updates? |
| Lokaler Wizard | Wie stabil laesst sich der Browser-Wizard lokal starten, mit Server-Survey verbinden und bei Bedarf lokal fallbacken? |
| Server-Survey | Wie werden Survey-Session, Survey-Version, Fortschritt, Export und Datenschutzstatus abgebildet? |
| Dateibasierter Content | lokale Survey-Fallbacks, Provider-Guides, Content-Manifeste, Reports und Vault-Dateien muessen robust gelesen/geschrieben werden. |
| Secret-Handling | Keychain/Credential Manager, Env-Fallbacks, Secret-Redaction und Repo-/Provider-Credentials. |
| Content-Zugang | signierte Bundles, spaeterer Managed-AI-Kanal, Git-Spezialpfade, Konflikte und Testbarkeit. |
| Docker-/Harness-Faehigkeit | Szenariobasierte Tests mit Server-Stub, Stub-LLM, Test-Bundles, Testdokumenten und Artefakt-Assertions. |
| Agent-/LLM-Anbindung | Readiness-Test, Provider-Abstraktion, spaetere Agent-Runtime und RAG/ROI-Integration. |
| Wartbarkeit | Wie leicht kann die Loesung von dir gepflegt, debuggt und an Kundenumgebungen angepasst werden? |

## 11. Runtime-, Artefakt- und Sicherheitsvertrag

### V2-FR-060 Artefaktstruktur

Jeder Lauf erzeugt nachvollziehbare Artefakte unter `ai-bootcamp-runs`.

Sollstruktur:

- `ai-bootcamp-runs/<timestamp>__<tenant_label>/run-manifest.json`
- `logs/`
- `survey/`
- `survey/answers.json`
- `survey/import-manifest.json`
- `inventory/`
- `process-docs/`
- `roi/`
- `rag/` nur wenn aktiviert
- `agent/agent-config.json` wenn Agent-Konfiguration erzeugt wird
- `ai-bootcamp-runs/latest` als Zeiger auf letzten erfolgreichen Lauf

### V2-FR-061 Run-Manifest

Mindestfelder:

- `run_id`
- `session_tracking_id`
- optional `customer_id`
- `site_id`
- `tenant_key`
- `tenant_label`
- `user_role`
- `tech_experience_level`
- `segment_branch`
- `segment_company_size`
- `execution_mode`
- `activation_status`
- `provider_ready`
- `access_mode_resolved`
- `access_mode_source`
- `started_at_utc`
- `finished_at_utc`
- `first_run_key`
- `dedupe_group_id`
- `is_first_run`
- `registration_mode`
- `registration_status`
- `survey_render_mode`
- `survey_version`
- `survey_session_id`
- `survey_import_status`
- `survey_answers_path`
- `survey_answers_sha256`
- `survey_data_residency`
- optional `registration_id`
- optional `e2e_smoke_echo`

### V2-FR-062 Agent-Konfiguration

`ai-bootcamp-runs/latest/agent/agent-config.json` enthaelt mindestens:

- `run_id`
- `site_id`
- `dry_run`
- `agent_mode` (`preflight_only` oder `roi_agent`)
- `llm_mode` (`not_configured`, `provider_test` oder `provider`)
- `activation_status`
- `provider_ready`
- `rag_enabled`
- `rag_status`
- `rag_sources_path`
- `preprocessing_required_count`
- `unsupported_format_count`
- `qualification_gate_result`

### V2-FR-063 Exit-Codes

- `0`: Erfolg.
- `10`: Qualification Gate nicht erfuellt.
- `11`: KRITIS/regulatorischer Stop.
- `20`: Konfigurations-/Eingabefehler.
- `30`: Secrets/Auth/Provider-Credentials nicht verfuegbar.
- `40`: Repo-Klon/Sync fehlgeschlagen.
- `50`: Inventar-Fehler im freigegebenen Scope.
- `60`: ROI-Berechnung wegen fehlender Mindestdaten nicht vollstaendig.
- `99`: Unerwarteter interner Fehler.

### V2-NFR-001 Sicherheit

- Default ist dry-run.
- Keine produktiven Keys im Defaultpfad.
- Read-only-Inventarisierung nur innerhalb explizit freigegebenem Scope.
- Keine normalen Host-Secrets in Docker-/Safe-Test-Harness.
- Keine Hardware-Fingerprints.
- Registrierung nutzt minimale technische Daten.
- Logs, Reports und Fehlertexte muessen Secret-Redaction anwenden.
- Keine stillen Seiteneffekte ausserhalb definierter Arbeitsverzeichnisse.

## 12. Docker- und Test-Harness

Die v2-Umsetzung braucht eine Docker-basierte Safe-Test-Harness, die die Anwendung nicht nur startet, sondern alle Kontrollfluss-Pfade mit Eingaben, erwarteten Artefakten und Assertions prueft.

Die Harness muss Testszenarien als Dateien aufnehmen koennen, zum Beispiel unter `tests/harness/cases/*.yaml`. Ein Case enthaelt mindestens:

- Survey-Antworten oder Verweis auf Survey-Antwortdatei.
- Survey-Modus (`server_rendered`, `local_fallback`, `preloaded_answers`).
- Optional Survey-Server-Stub-Antworten und Handoff-Token-Verhalten.
- Provider-/LLM-Modus (`none`, `stub_success`, `stub_failure`, optional `real_provider_explicit`).
- Bundle-Manifest oder Manifest-Override; optional Repo-Manifest fuer technische Testpfade.
- Vorbefuellte Testdateien im Container, inklusive Dokumente, Bilder, Markdown oder leere Pfade.
- Erwartete Exit-Codes.
- Erwartete Manifest-Felder.
- Erwartete Dateien/Ordner.
- Erwartete Report-Abschnitte.
- Secret-Leak-Assertions.
- Optional erwartete ROI-/RAG-/Agent-Antworten.

Die Harness muss mindestens diese Faelle pruefen:

- Kein Provider: Einsteiger-Survey, Vorbereitungsmodus, keine ROI-Behauptung.
- Provider von Beginn an: LLM-Routing, Arbeitsumgebung, Survey, ROI-Smoke.
- Kein Provider bis Survey-Ende, dann erfolgreiche Aktivierung: Readiness-Test, Arbeitsumgebung, optionale Zusatzfragen, ROI-Smoke.
- Kein Provider bis Ende: Vorbereitungsreport mit blockiertem ROI.
- KRITIS-/Regulatorik-Stop: kein nutzbarer Agent-Endzustand.
- RAG vorbereitet mit Freigabe.
- RAG deaktiviert ohne Dokumentation oder ohne Freigabe.
- Secret-Isolation: keine normalen Host-Env-Secrets.
- Free-Entry-Bundle gueltig: Signatur, Hash und erwartete Dateien werden geprueft und in den Vault uebernommen.
- Free-Entry-Bundle ungueltig: falscher Hash, fehlende Signatur oder fehlende erwartete Dateien fuehren zu klarem Blockerstatus ohne Erfolgsmeldung.
- Managed-AI-Updatekanal: freigegebene Update-Metadaten werden erkannt; lokale Kundenaenderungen werden nicht still ueberschrieben.
- Optionaler Git-Testpfad: `https://github.com/paradox123/ai-test-repo.git` wird als oeffentlicher Testfall in den erwarteten Vault-Unterordner geklont.
- Optionaler Git-Auth-Fehler: privater/geschuetzter Repo-Fall scheitert mit Exit `30` oder `40`, ohne Token-Leak.
- Optionaler Git-Konflikt: divergierter Stand erzeugt klaren Konfliktstatus, kein Auto-Merge.
- Survey-Antworten aus Datei: Container erhaelt fertige Antworten und muss erwartete Artefakte/Reports erzeugen.
- Dokumente im Testcontainer: PDF/DOCX/MD/TXT/Bild-Testdateien fuehren zu erwarteten RAG-/Preprocessing-Statuswerten.
- ROI-Zusatzfragen: Agent-Stub fordert fehlende ROI-Daten an; Anwendung rendert sie im Survey-Stil und speichert Antworten strukturiert.
- Report-Textvarianten: Vorbereitungs- und Aktivierungshinweise erscheinen passend zu Profil `A`, `B`, `C`.
- Obsidian-Vault-Setup: Vault-Struktur, Plugin-Baseline-Protokoll und Repo-Zielpfade werden erzeugt.
- Provider-Guide-Auswahl: Matrix waehlt erwarteten Guide und blockiert dynamische LLM-Erklaerung, solange kein LLM bereit ist.
- Survey-Server-Handoff erfolgreich: Server-Stub erzeugt Antwortartefakt, .NET-Starter importiert `survey/answers.json`, Manifest enthaelt `survey_import_status=imported`.
- Survey-Server-Handoff Hash/Signatur ungueltig: Import stoppt, kein ROI/RAG, klarer Fehlerstatus.
- Survey-Server nicht erreichbar: lokaler Fallback oder pausierter Lauf, kein stiller Datenverlust.
- Survey-Retention: Import-Manifest dokumentiert `retention_policy` und `server_delete_status`.

## 13. Traceability

| Quelle | Uebernommene Inhalte | Status in dieser Master Spec |
|---|---|---|
| `v2/docs/APPLICATION-FLOW.md` | fuehrender Nutzerpfad, LLM-Konfigurationsblock, Vault/Workbench, Survey-Grenze, Kontaktpfad | fuehrend uebernommen |
| `2026-04-22-free-entry-onboarding-spec.md` | Artefaktstruktur, Manifest, Exit-Codes, Secret-Handling, Register-Minimum, Repo-Klon-Vertraege | uebernommen, alte Reihenfolge ersetzt |
| `2026-05-01-01-onboarding-runner-core-spec.md` | Runner-Orchestrierung, Idempotenz, Step-Status, Dry-Run, Logs, Exit-Codes | uebernommen |
| `2026-05-01-02-entry-services-browser-register-spec.md` | Landing, Browser-Wizard, Register-Backend, Docker, Wizard-Smoke | uebernommen |
| `2026-05-01-03-discovery-compliance-survey-spec.md` | A/B/C-Sprachvarianten, Pflichtkern, Stop-Verhalten, read-only Scope | Inhalte uebernommen, alte KRITIS-Reihenfolge ersetzt |
| `2026-05-01-04-artifact-pipeline-roi-rag-spec.md` | Repo-Klon/Sync, ROI-Guardrails, RAG-Preprocessing, Quellenstatus | uebernommen und um LLM-Pflicht erweitert |
| `2026-05-04-05-distribution-and-installer-spec.md` | macOS/Windows-Starter, SHA256, `.kickstart`, best-effort Register, Bootstrap-Preflight | uebernommen |
| `2026-05-04-06-agent-runtime-and-rag-service-spec.md` | Agent-Konfig, Agent-Modi, RAG-Status, Docker-Harness, LLM-Pflicht fuer ROI | uebernommen, Prozessdialog auf Survey-zuerst korrigiert |
| `2026-05-04-07-provider-access-and-commercial-activation-spec.md` | Aktivierungsstatus, keine Zahlungsdaten, customer-owned Provider, Assisted Setup, Paid Pilot | uebernommen, Aktivierung auf zweiten Punkt nach Survey geschaerft |
| `v2/docs/adr/001-repo-access-and-ip-protection.md` | signiertes Free-Entry-Bundle als Default, spaeterer Managed-AI-Updatekanal, Git/GitHub nur als optionaler technischer Spaeterpfad | fuehrend fuer Content-Zugang |
| `v2/docs/adr/003-survey-delivery-and-answer-handoff.md` | Survey-Delivery-Service, server-rendered HTML, temporaerer Antwortspeicher, lokaler JSON-Import, Retention | fuehrend fuer Survey-Handoff |
| `v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md` | Scope-Schutzregeln, Slice-Zuschnitt, Coverage-Matrix und erster vertikaler Architektur-Spike | fuehrend fuer Umsetzungszerlegung |
| `03-product/survey-v1-final.md` | Survey-Feldkatalog, drei Erfahrungsstufen, RAG-Intake, ROI-Mindestdaten | Inhaltsquelle, Reihenfolge muss migriert werden |
| `03-product/roi-modell.md` | ROI-Formeln, Bandbreiten, Guardrails, Report-Mindestqualitaet | uebernommen |
| `03-product/bootstrap-requirements-spec.md` | Self-Serve Script, Setup, Survey, Inventar, ROI, Register, Docker, GO/NO-GO-Testfaelle | Inhalte uebernommen, Subscription-first und KRITIS-first ersetzt |
| `01-offering/free-entry-startpfad.md` / `01-offering/angebot.md` | kundenverstaendlicher Free-Entry-Nutzen, Assisted-Begriff, ROI-Erklaerung, Track-B-Hinweis | Marketing-/Angebotsdoku muss nach v2-Flow aktualisiert werden |
| `_legacy/v1-node-prototype/config/repo-manifest.v1.yaml` | Repo-Manifest als vorhandener flexibler Mechanismus | optionaler technischer Spaeterpfad; v2-Default ist Bundle-Manifest nach ADR-001 |

## 14. Offene Punkte

1. [MISSING non-blocking: Konkrete Bundle-Manifest-Beispiele fuer Free-Entry-, Paid-Pilot- und Managed-AI-Inhalte sowie oeffentliche Test-/Demo-Inhalte.]
2. [MISSING non-blocking: Git-/GitHub-Migrationsvertrag fuer spaetere technische Kundenpfade nach Managed-Service-Freigabe.]
3. [DONE by S2 child spec: Survey-Delivery-Service-API fuer Session-Start, Antwort-Submission, Handoff-Export, Retention-Status und lokale Importbestaetigung ist in `_specs/2026-05-05-free-entry-v2-s2-survey-delivery-answer-handoff-spec.md` implementiert und akzeptiert.]
4. [MISSING non-blocking: Provider-Guides mit aktuellen Screenshots, offiziellen Links, `last_verified_at` und Review-Intervall.]
5. [MISSING non-blocking: Finaler Wortlaut aller Aktivierungs- und Vorbereitungsreport-Hinweise ueber die Startvorschlaege hinaus.]

## 15. Plan-Readiness dieser Master Spec

Diese Master Spec ist als Planungsgrundlage bereit fuer Umsetzungsspezifikationen, wenn:

1. Die fuehrende Reihenfolge nicht mehr mit alten Specs kollidiert.
2. Die alten Specs als `Superseded` markiert oder eindeutig auf diese Master Spec verwiesen wurden. Status 2026-05-05: erledigt durch `v2/docs/S0-REPO-FREEZE-LEGACY-QUARANTINE.md`.
3. Die Survey-Doku oder ein neues Survey-Artefakt die neue Reihenfolge server-renderbar und lokal fallbackfaehig abbildet.
4. Der .NET-Spike den entschiedenen Starter-/Wizard-/Runner-Zuschnitt technisch bestaetigt hat.
5. Der Survey-Handoff `survey/answers.json` und `survey/import-manifest.json` reproduzierbar lokal erzeugt.
6. Das Bundle-Manifest Free-Entry-, Paid-Pilot- und Managed-AI-Inhalte sowie oeffentliche Test-/Demo-Inhalte flexibel abbildet.
7. Die Docker-Harness die Kontrollfluss-Pfade mit szenariobasierten Inputs und erwarteten Artefakten prueft.

## 16. Empfohlener naechster Schritt

Nach fachlicher Freigabe dieser Master Spec:

1. Slice-Plan `v2/docs/FREE-ENTRY-V2-SLICE-PLAN.md` als Scope-Kontrollschicht verwenden.
2. S0 Spec Freeze Pack ist abgeschlossen: alte Specs sind superseded, Legacy ist quarantined und Child Specs liegen unter `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_specs`.
3. S1 vertikaler Architektur-Spike und S2 Survey Delivery / Answer Handoff sind akzeptiert.
4. Naechster Umsetzungsschritt: S3 Content Bundle und Managed-AI-Kanal umsetzen, damit der Dummy-Bundle-Pfad durch einen verifizierbaren Bundle-/Manifest-/Installationsvertrag ersetzt wird.

| Date | Author | Change |
|------|--------|--------|
| 2026-05-04 | Codex | Konsolidierte v2-Master-Spec aus Application Flow, Parent-Spec, Agent/RAG-Spec, Provider-Spec, Survey-Katalog und ROI-Modell erstellt. |
| 2026-05-04 | User/Codex | Master-Spec als Planungsgrundlage geschaerft: flexible Repo-Manifeste statt Pflichtrepos, drei Survey-JSONs, erweitertes Docker-Szenario-Harness, Provider-Matrix, Plugin-IDs und Textvarianten. |
| 2026-05-04 | User/Codex | Status von Accepted auf Plan korrigiert und Repo-Auth sowie einsteigergeeignete Provider-Guides konkretisiert. |
| 2026-05-04 | User/Codex | Geschuetzte Repo-Zugaenge als Default, visueller Provider-Guide-Wizard und Technologie-Stack-Evaluierung vor weiteren Runtime-Implementierungen ergaenzt. |
| 2026-05-04 | User/Codex | Zwei ADRs fuer Repo-/Content-Zugang und Starter-/Wizard-/Runner-Technologie als Entscheidungsgrundlage ergaenzt. |
| 2026-05-04 | User/Codex | ADR-002 entschieden: .NET-Starter/Wizard/Runner mit server-gerendertem Survey und lokalem Survey-Fallback in Master Spec nachgezogen. |
| 2026-05-04 | User/Codex | ADR-003 fuer Survey-Delivery-Service und automatische lokale Antwortdaten-Uebergabe erstellt und Master Spec um kanonische Survey-Artefakte ergaenzt. |
| 2026-05-04 | User/Codex | ADR-001 als entschieden nachgezogen: signiertes Free-Entry-Bundle als Default, Managed-AI-Updatekanal und Git/GitHub nur als optionaler Spaeterpfad. |
| 2026-05-04 | User/Codex | Slice-Plan als Scope-Kontrollschicht ergaenzt, damit die v2-Master-Spec beim Aufteilen in Umsetzungsslices vollstaendig abgedeckt bleibt. |
| 2026-05-05 | User/Codex | S0 Repo Freeze nachgezogen: alte Specs superseded, Legacy quarantined, fachliche Ordner als Quellen markiert und Child Specs fuer S0-S7 erstellt. |
| 2026-05-05 | Codex | S2 Survey-Delivery-Service-API als durch Child Spec konkretisiert markiert. |
| 2026-05-05 | User/Codex | S2 Survey Delivery und Answer Handoff akzeptiert; Master-Spec-Status fuer Survey-Handoff auf done gesetzt und S3 als naechsten Umsetzungsschritt markiert. |

SessionId: codex-free-entry-v2-master-spec-2026-05-04
