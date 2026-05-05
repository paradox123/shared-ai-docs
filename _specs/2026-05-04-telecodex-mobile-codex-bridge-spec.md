**Date:** 2026-05-04  
**Status:** 🟡 Spec
**Scope:** Sichere Pilot-Einfuehrung von TeleCodex als Telegram-basierte mobile Fernsteuerung fuer lokale Codex-Sessions auf dem MacBook.

---

# TeleCodex Mobile Codex Bridge Spec

## 1. Kontext

Der Nutzer moechte unterwegs vom Samsung/Android-Handy aus lokale Codex-Arbeit sehen und steuern:

- bestehende Codex-Sessions vom MacBook finden,
- eine bestehende Session fortsetzen,
- neue Sessions starten,
- Audio-/Sprachinput aufnehmen und an Codex geben,
- Ergebnisse und Status unterwegs nachvollziehen,
- bei Bedarf zur lokalen CLI/Desktop-Arbeit zurueckwechseln.

Ein kompletter Eigenbau aus mobiler Web-App, Audio-Pipeline, Session-Bridge und sicherem Remote-Zugang waere moeglich, aber fuer den ersten Schritt zu aufwendig und sicherheitskritisch. Das GitHub-Projekt `benedict2310/telecodex` liefert bereits einen grossen Teil dieses Use Cases als Telegram-Bridge fuer Codex.

## 2. Quellenbasis

Gepruefte Quelle:

- Repository: `https://github.com/benedict2310/telecodex`
- Lokal inspizierter Commit: `fd2a241`
- Relevante Komponenten:
  - `README.md`: Feature- und Betriebsbeschreibung.
  - `src/codex-session.ts`: Nutzung von `@openai/codex-sdk`, Start/Resume von Threads, Streaming von Agent-/Tool-Events.
  - `src/codex-state.ts`: Lesen lokaler Codex-Threads aus `~/.codex/state_*.sqlite`.
  - `src/config.ts`: Telegram-Allowlist, Sandbox-/Approval-Konfiguration, Workspace-Ermittlung.
  - `src/bot.ts`: Telegram-Kommandos `/sessions`, `/attach`, `/new`, `/handback`, Voice/Bild/Datei-Handler.
  - `docker-compose.yml`: Containerbetrieb mit Mount von `~/.codex` und `./workspace`.

Lokale Befunde:

- `npm ci && npm test` war erfolgreich: 203 Tests gruen.
- `npm audit --omit=dev --json` meldet keine Produktions-Vulnerabilities.
- `npm audit --json` meldet transitive Dev-/Tooling-Vulnerabilities; diese sind vor dauerhaftem Betrieb zu bewerten oder zu beheben.

## 3. Zielbild

TeleCodex wird als schmaler Pilot auf dem MacBook betrieben. Telegram dient als mobile Oberflaeche, nicht als vollwertiger Ersatz fuer die lokale Codex Desktop App oder CLI.

Der Pilot beantwortet:

1. Ist TeleCodex praktisch genug fuer mobile Codex-Inputs?
2. Koennen bestehende lokale Sessions verlaesslich gefunden und fortgesetzt werden?
3. Ist Voice-Input per Telegram brauchbar genug?
4. Laesst sich das Sicherheitsprofil so eng halten, dass der Nutzen den Zusatzangriffspfad rechtfertigt?

## 4. Grundsatzentscheidungen

### 4.1 Reuse statt Eigenbau

TeleCodex wird im Pilot gegenueber einer eigenen PWA bevorzugt, weil es bereits liefert:

- Telegram-Mobile-UI,
- Voice-Transcription,
- Session-Browser,
- Attach/Resume bestehender Codex-Threads,
- Streaming-Ausgaben,
- Handback zur CLI,
- Telegram-User-Allowlist.

### 4.2 Kein oeffentlicher MacBook-Webzugang

Der Pilot oeffnet keinen Webserver-Port am MacBook fuer das Internet. TeleCodex nutzt Telegram-Polling. Damit muss das MacBook ausgehend Telegram erreichen, aber nicht eingehend aus dem Internet erreichbar sein.

### 4.3 Native-first fuer bestehende lokale Sessions

Der erste Pilot laeuft bevorzugt nativ auf dem MacBook, nicht in Docker. Grund: Docker mountet im Standard nur `./workspace` als `/workspace`. Bestehende Codex-Threads mit Arbeitsverzeichnissen unter `/Users/dh/...` lassen sich nativ einfacher und naeher am echten Arbeitsfluss fortsetzen.

Docker bleibt ein spaeterer Haertungs-/Isolationspfad, erfordert dann aber bewusst gemappte Workspaces.

### 4.4 Sicherer Default

Der Pilot startet mit:

```env
CODEX_SANDBOX_MODE=read-only
CODEX_APPROVAL_POLICY=never
ENABLE_UNSAFE_LAUNCH_PROFILES=false
TOOL_VERBOSITY=summary
ENABLE_TELEGRAM_LOGIN=false
SHOW_TURN_TOKEN_USAGE=false
ENABLE_TELEGRAM_REACTIONS=false
```

`read-only / never` ist der Pilot-Default: Codex darf ohne weitere Rueckfrage nur innerhalb der Read-only-Sandbox arbeiten. `workspace-write` darf erst nach expliziter Freigabe fuer definierte Repositories/Profile genutzt werden und benoetigt vorher einen eigenen Check, ob Approval-Flows in TeleCodex praktisch handhabbar sind. `danger-full-access` ist im Pilot ausgeschlossen.

## 5. In Scope

- Einen dedizierten Telegram Bot fuer den privaten Pilot einrichten.
- Zugriff auf exakt erlaubte Telegram User IDs begrenzen.
- TeleCodex lokal auf dem MacBook installieren und starten.
- Bestehende lokale Codex-Sessions ueber `/sessions` anzeigen.
- Eine bestehende Session per `/attach <thread-id>` oder Session-Auswahl verbinden.
- Mobile Textnachrichten an die aktive Session senden.
- Telegram-Voice-Nachrichten transkribieren und als Prompt weitergeben.
- Neue Threads aus Telegram starten, standardmaessig read-only.
- `/handback` nutzen, um zur lokalen CLI mit `codex resume <id>` zurueckzukehren.
- Einen minimalen Betriebs-/Rollbackpfad dokumentieren.

## 6. Out of Scope

- Eigene Mobile-App oder PWA.
- Eigene Audioaufnahme-/Transkriptionspipeline ausserhalb TeleCodex.
- Oeffentlicher Webzugang auf das MacBook.
- Telegram-Gruppenbetrieb mit mehreren Personen im Erstrelease.
- Dauerhafter Betrieb als unbeaufsichtigter Produktionsdienst.
- `danger-full-access` aus Telegram.
- Automatisches Pushen, Deployen oder Ausfuehren destruktiver Operationen aus Telegram.
- Weitergabe von OpenAI-/Codex-Secrets in Telegram-Nachrichten.

## 7. Bedrohungsmodell und Sicherheitsannahmen

### 7.1 Schutzobjekte

- Lokale Repositories und Arbeitskopien.
- Codex-Auth-State unter `~/.codex`.
- API-Keys und andere Secrets im Shell-/Projektkontext.
- Inhalte aus Codex-Sessions, inklusive Code, Dokumentation und Tool-Ausgaben.
- Telegram Bot Token.

### 7.2 Vertrauensgrenzen

- Telegram ist Transport- und UI-Schicht, aber kein geheimer Tresor.
- Der Bot Token ist ein Hochrisiko-Secret.
- Die Allowlist schuetzt nur, wenn Telegram-Konto, Bot Token und lokale Host-Umgebung nicht kompromittiert sind.
- Codex bleibt der aktive Agent mit Shell-/Dateiwerkzeugzugriff gemaess Sandbox/Approval-Konfiguration.

### 7.3 Pflicht-Guardrails

1. Nur dedizierter Bot fuer diesen Pilot.
2. Nur private Chat-Nutzung im Erstrelease.
3. `TELEGRAM_ALLOWED_USER_IDS` enthaelt ausschliesslich die eigene User ID.
4. Kein `CODEX_API_KEY` in Telegram schreiben.
5. Bot Token nur lokal in `.env`, nicht in Repos.
6. `ENABLE_TELEGRAM_LOGIN=false`, wenn Codex bereits lokal authentifiziert ist.
7. Start mit `read-only / never`.
8. `ENABLE_UNSAFE_LAUNCH_PROFILES=false`.
9. Keine vertraulichen Kundendaten oder produktiven Secrets per Telegram-Voice/Text senden.
10. Bei Verlust/Diebstahl des Handys oder Telegram-Kontoverdacht: Bot Token sofort rotieren und TeleCodex stoppen.

## 8. Funktionale Anforderungen

### FR-001 Installation und Start

TeleCodex MUSS aus einem lokal geklonten Repository auf dem MacBook startbar sein. Der Start MUSS fehlschlagen, wenn `TELEGRAM_BOT_TOKEN` oder `TELEGRAM_ALLOWED_USER_IDS` fehlen.

### FR-002 Authentifizierter Telegram-Zugriff

Nur Telegram-Nutzer in `TELEGRAM_ALLOWED_USER_IDS` duerfen Kommandos und Nachrichten verarbeiten lassen. Nicht erlaubte Nutzer erhalten keine Session- oder Workspace-Informationen.

### FR-003 Session-Browser

Der Bot MUSS mit `/sessions` lokale Codex-Threads aus `~/.codex/state_*.sqlite` anzeigen koennen. Die Anzeige MUSS mindestens Thread-Titel, Workspace und relative Aktualitaet oder gleichwertige Orientierung enthalten.

### FR-004 Session-Attach

Der Bot MUSS eine bestehende lokale Codex-Session per Auswahl oder `/attach <thread-id>` an den aktuellen Telegram-Kontext binden koennen. Unbekannte Thread-IDs MUESSEN abgelehnt werden.

### FR-005 Mobile Prompt-Eingabe

Textnachrichten ohne Slash-Kommando MUESSEN an die aktive Codex-Session weitergeleitet werden. Wenn noch keine aktive Session existiert, DARF TeleCodex eine neue Session mit sicherem Default-Profil erstellen.

### FR-006 Voice-Eingabe

Voice- oder Audio-Nachrichten MUESSEN transkribiert und erst danach an Codex weitergegeben werden. Leere oder fehlgeschlagene Transkripte MUESSEN sichtbar abgelehnt werden, ohne Codex zu starten.

### FR-007 Handoff zur CLI

`/handback` MUSS einen direkt ausfuehrbaren `codex resume <thread-id>`-Befehl mit korrektem Arbeitsverzeichnis liefern.

### FR-008 Launch-Profile

Der Pilot MUSS mindestens ein `read-only / never`-Profil anbieten. Schreibende Profile duerfen nur nach expliziter Entscheidung aktiviert werden. `danger-full-access` MUSS im Pilot deaktiviert bleiben.

### FR-009 Tool-Sichtbarkeit

Tool-Ausgaben MUESSEN standardmaessig zusammengefasst werden. Vollstaendige Tool-Outputs duerfen nur fuer gezielte Debug-Sessions aktiviert werden, weil Telegram sonst zu viele lokale Details transportiert.

### FR-010 Betriebsstopp

Es MUSS einen einfachen Stopp- und Token-Rotationspfad geben. Nach Stop darf TeleCodex keine weiteren Telegram-Updates verarbeiten.

## 9. Nicht-funktionale Anforderungen

- **NFR-001 Minimaler Angriffspfad:** Kein eingehender Port am MacBook fuer den Pilot.
- **NFR-002 Least Privilege:** Startprofil ist read-only; Schreibzugriff ist explizit.
- **NFR-003 Secret-Hygiene:** `.env` bleibt lokal und wird nicht versioniert.
- **NFR-004 Nachvollziehbarkeit:** Startkonfiguration und aktive Profile sind dokumentiert.
- **NFR-005 Reversibilitaet:** Pilot kann ohne Aenderung an bestehenden Repositories entfernt werden.
- **NFR-006 Datenminimierung:** Telegram erhaelt nur den Inhalt, den der Nutzer aktiv sendet oder den Codex als Antwort/Tool-Zusammenfassung ausgibt.
- **NFR-007 Update-Bewusstsein:** TeleCodex ist Fremdcode; Updates werden vor Uebernahme kurz geprueft.

## 10. Abnahmekriterien

Der Pilot gilt als bereit fuer eine erste Nutzung, wenn:

1. TeleCodex lokal installiert ist und Tests gruen sind.
2. Produktion-Abhaengigkeiten laut `npm audit --omit=dev` keine High/Critical Findings haben.
3. `.env` enthaelt einen dedizierten Bot Token und exakt erlaubte Telegram User IDs.
4. Default-Profil ist `read-only / never`.
5. Unsafe Launch Profiles sind deaktiviert.
6. `/auth` zeigt eine nutzbare Codex-Authentifizierung.
7. `/sessions` listet lokale Codex-Threads.
8. Eine bestehende Session kann attached werden.
9. Eine Textnachricht erreicht die attached Session.
10. Eine Voice-Nachricht wird transkribiert und erreicht die attached Session.
11. `/handback` liefert einen plausiblen lokalen `codex resume`-Befehl.
12. Unautorisierte Telegram User ID wird abgelehnt.
13. Stop/Restart und Bot-Token-Rotation sind einmal trocken dokumentiert.

## 11. Testfaelle

### 11.1 Lokale Qualitaet

- `TC-LQ-01`: `npm ci && npm test` ist gruen.
- `TC-LQ-02`: `npm audit --omit=dev --audit-level=high` ist gruen.
- `TC-LQ-03`: Dev-Audit-Findings sind dokumentiert oder behoben.

### 11.2 Zugriff und Auth

- `TC-AUTH-01`: fehlender `TELEGRAM_BOT_TOKEN` verhindert Start.
- `TC-AUTH-02`: fehlende `TELEGRAM_ALLOWED_USER_IDS` verhindert Start.
- `TC-AUTH-03`: erlaubte eigene User ID kann `/start` und `/sessions` nutzen.
- `TC-AUTH-04`: nicht erlaubte User ID erhaelt keine Sessiondaten.

### 11.3 Session-Flow

- `TC-SESS-01`: `/sessions` zeigt mindestens eine bestehende lokale Codex-Session.
- `TC-SESS-02`: `/attach <id>` bindet eine existierende Session.
- `TC-SESS-03`: `/attach <ungueltig>` wird abgelehnt.
- `TC-SESS-04`: `/new` startet einen neuen Thread im sicheren Default-Profil.
- `TC-SESS-05`: `/handback` liefert `cd '<workspace>' && codex resume '<id>'`.

### 11.4 Mobile Eingabe

- `TC-MOB-01`: Textprompt wird an die aktive Session gesendet.
- `TC-MOB-02`: Voice Message erzeugt sichtbares Transkript und wird danach gesendet.
- `TC-MOB-03`: leeres Transkript startet keinen Codex-Turn.
- `TC-MOB-04`: Bild mit Caption wird als Bildinput an Codex weitergegeben.

### 11.5 Sicherheitsprofile

- `TC-SEC-01`: `/launch_profiles` zeigt kein Full-Access-Profil.
- `TC-SEC-02`: Default-Profil ist `read-only / never`.
- `TC-SEC-03`: Schreibendes Profil ist im Pilot nicht aktiv.
- `TC-SEC-04`: Tool-Ausgaben sind im Modus `summary`.
- `TC-SEC-05`: `.env` ist nicht versioniert und enthaelt keine versehentlich committeten Secrets.

## 12. Verifikationskommandos

### 12.1 Ausfuehrungskontext

- Working Directory fuer Code-Checks: lokaler TeleCodex-Clone.
- Shell: macOS `zsh` oder `bash`.
- Node.js: 22+.
- Keine rekursiven Verify-Loops.
- Live-Telegram-Checks benoetigen einen dedizierten Test-Bot und die eigene Telegram User ID.

### 12.2 Risk-based Preflight

```bash
npm ci
npm test
npm audit --omit=dev --audit-level=high
```

Erfolg:

- Exit-Code `0` fuer alle drei Kommandos.
- Dev-Audit-Findings sind separat bewertet, falls `npm audit --json` Findings meldet.

### 12.3 Konfigurationspruefung

```bash
test -f .env
rg -q '^TELEGRAM_BOT_TOKEN=.+$' .env
rg -q '^TELEGRAM_ALLOWED_USER_IDS=[0-9,]+$' .env
rg -q '^CODEX_SANDBOX_MODE=read-only$' .env
rg -q '^CODEX_APPROVAL_POLICY=never$' .env
rg -q '^ENABLE_UNSAFE_LAUNCH_PROFILES=false$' .env
rg -q '^ENABLE_TELEGRAM_LOGIN=false$' .env
```

Erfolg:

- Alle Checks liefern Exit-Code `0`.

### 12.4 Live-Smoke

```bash
npm run dev
```

Manuelle Telegram-Smokes:

1. `/start`
2. `/auth`
3. `/sessions`
4. Session auswaehlen oder `/attach <thread-id>`
5. kurze Textnachricht senden
6. kurze Voice Message senden
7. `/handback`
8. Prozess mit `Ctrl-C` stoppen

Erfolg:

- Bot antwortet nur der erlaubten User ID.
- Sessionliste und Attach funktionieren.
- Text und Voice landen in der erwarteten Codex-Session.
- `/handback` liefert einen plausiblen lokalen Resume-Befehl.
- Stop beendet Polling ohne Neustartschleife.

## 13. Offene Punkte

### Blocking vor Pilotstart

Keine offenen blocking Punkte, sofern der Pilot mit `read-only / never` startet.

### Non-blocking

- [DECISION non-blocking: Ob spaeter ein separates `workspace-write`-Profil fuer ausgewaehlte Repositories erlaubt wird.]
- [DECISION non-blocking: Ob TeleCodex-Approval-Flows fuer `workspace-write / on-request` praktisch genug sind oder ob Schreibprofile lokal bestaetigt werden muessen.]
- [DECISION non-blocking: Ob TeleCodex spaeter in Docker laufen soll; dafuer braucht es ein bewusstes Workspace-Mounting fuer `/Users/dh/...`.]
- [MISSING non-blocking: Endgueltiger Ort des lokalen TeleCodex-Clones.]
- [MISSING non-blocking: Gewaehlter Name des dedizierten Telegram Bots.]

## 14. Review-Checkliste

Diese Spec ist nur bereit fuer Pilotplanung, wenn der Review bestaetigt:

1. Der Scope ist ein Pilot, kein Produktionsbetrieb.
2. Die Security-Defaults sind eng genug.
3. Es gibt keine implizite Freigabe fuer `danger-full-access`.
4. Telegram wird nicht als Secret-Kanal behandelt.
5. Native-vs-Docker ist bewusst entschieden.
6. Akzeptanzkriterien sind testbar.

## 15. History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-04 | Codex | Initiale Spec fuer TeleCodex als mobile Telegram-Bridge fuer lokale Codex-Sessions erstellt. |
| 2026-05-04 | Codex | Review-Findings eingearbeitet: Pilot-Default auf `read-only / never` korrigiert und Config-Pruefung auf secret-schonende `rg -q` Checks umgestellt. |

SessionId: codex-telecodex-mobile-bridge-2026-05-04
