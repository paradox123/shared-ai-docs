# CheckBuild User Guide (Developer-Armed Auto Triage)

## 1) Ziel

Dieser Guide beschreibt den gewünschten Ablauf:

1. Du arbeitest wie gewohnt lokal (Code ändern, commit, push).
2. Du sagst lokal **"watch my next build"** (bzw. führst den entsprechenden Arm-Befehl aus).
3. Falls der beobachtete Build/`check-build-remote` einen Incident zeigt, läuft automatisch:
   - `pull -> analyze -> plan`
4. **Fix / commit / push** entscheidest du weiterhin manuell.

Wichtig: Die automatische Plan-Erstellung ist **dateibasiert** und nicht von einer bestimmten Copilot-Session abhängig.

---

## 2) Komponenten im Hintergrund

## A. GitLab Pipeline (CI)
- Führt Build/Deploy/`check-build-remote` aus.
- Erzeugt bei Incident ein Artifact-Bundle (`incident/...`).
- Ist nur für Beobachtung + Evidence zuständig, nicht für automatische Codeänderungen.

## B. Lokaler Watcher-Job
- Läuft im Hintergrund (z. B. launchd oder eigener Hintergrundprozess).
- Liest den lokalen Arm-Status ("nächsten Build beobachten").
- Pollt GitLab und prüft das beobachtete Pipeline-Ergebnis.
- Triggert bei Incident automatisch:
  1) `check-build.local.pull.cs`
  2) `check-build.local.analyze.cs`
  3) `check-build.local.plan.cs`

## C. Lokale File-Based Tools (.NET 10)
- `check-build.local.pull.cs`: lädt Artifact
- `check-build.local.analyze.cs`: erstellt Diagnose
- `check-build.local.plan.cs`: erstellt Plan-Dateien

## D. Lokaler State
- `~/.ncg/check-build/local-state.json`
- Enthält u. a. Arm-Status, bereits verarbeitete Pipeline/Job-IDs und Trigger-Metadaten.

## E. Plan-Artefakte
- `analysis/incident-triage.md` / `incident-triage.json` (kompakte Incident-Zusammenfassung)
- `analysis/fix-plan.md` / `fix-plan.json` (eigentlicher Implementation Plan)
- `analysis/implementation-plan.md` / `implementation-plan.json` (kompatibler Alias)
- Optional: `analysis/run-meta.json` (pipeline/job/run, triggerReason, generatedAt, optional copilotSessionId)

---

## 3) Developer Workflow (praktisch)

## Schritt 1: Build-Beobachtung "scharf schalten"
Beispiel (geplantes Interface):

```bash
dotnet run tests/check-build.local.watch.cs -- --arm-next-build
```

Hinweis: Ohne `--branch` nutzt der Watcher automatisch den aktuellen Git-Branch.

Optional commit-spezifisch:

```bash
dotnet run tests/check-build.local.watch.cs -- --arm-next-build --branch <target-branch> --commit <sha>
```

## Schritt 2: Normal entwickeln
- In Rider committen/pushen wie gewohnt.
- Konsole kann weiter normal genutzt werden (Watcher läuft im Hintergrund).

## Schritt 3: Auto-Triage (nur bei Incident)
Wenn der beobachtete Run fehlschlägt/Incident markiert ist:
- Watcher zieht Artifact,
- erstellt Diagnose,
- erstellt Plan-Dateien,
- meldet Ergebnis (Konsole + optional Desktop Notification).

## Schritt 4: Manuelle Entscheidung
Du öffnest den erzeugten Plan und entscheidest:
- Fix umsetzen oder nicht,
- commit/push,
- nächste Pipeline als Verifikation.

---

## 4) Session-Handling (wichtig)

- Der Watcher braucht **keine dauerhafte Copilot-Session**, um Plan-Dateien zu erzeugen.
- Plan-Dateien sind die primäre Wahrheit für den nächsten Schritt.
- Falls eine Copilot-Session-Weiterführung gewünscht ist:
  - optional Session-ID in Metadaten speichern,
  - später `/resume <sessionId>` nutzen,
  - oder neue Session starten und direkt mit den Artefakt-Dateien weiterarbeiten.

Kurz: Session ist optionaler Komfort, nicht technische Abhängigkeit.

---

## 5) Was ist bereits umgesetzt / was noch nicht?

## Bereits umgesetzt und getestet
- Incident-Erzeugung in `check-build-remote`
- Artifact-Download (`pull`)
- Diagnose (`analyze`)
- Plan-Ausgabe (`plan`) als dateibasierter Output

## Noch umzusetzen (gemäß Iteration 7)
- Watcher mit Arm-Mechanismus (`watch my next build`)
- automatische Trigger-Logik auf genau den beobachteten Build
- erweiterter echter Implementation-Plan (`implementation-plan.md/json`)
- optionales `run-meta.json` mit Session-Link-Metadaten

---

## 6) Troubleshooting

- **Kein Auto-Start nach Pipeline:** Watcher läuft nicht oder Build war nicht armed.
- **Auth-Fehler:** `GITLAB_PAT` fehlt/ungültig.
- **Doppelte Verarbeitung:** dedupe in `local-state.json` prüfen.
- **Plan zu allgemein:** auf `implementation-plan.*` umstellen (Iteration 7 Ziel).
