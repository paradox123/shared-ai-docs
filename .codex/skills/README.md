# Repository-lokale UX/UI-Skills

Diese Skills sind auf Wunsch vom 14.09.2026 direkt in diesem Repository unter
`.codex/skills` installiert. Sie gehören nicht zur gemeinsamen/globalen Sammlung
unter `skills-repo`. Die vorhandenen OpenSpec-Skills bleiben daneben bestehen.

| Skill | Version | Zweck |
| --- | --- | --- |
| [Impeccable](impeccable/SKILL.md) | 4.3.1 | UX/UI-Entwurf, Informationshierarchie, Texte, Designkritik und Überarbeitung |
| [Vercel Web Design Guidelines](web-design-guidelines/SKILL.md) | 1.0.0 | Prüfung von UI-Code gegen Vercels aktuelle Web Interface Guidelines |

## Verwendung in Codex

Ab dem nächsten Turn sind die Skills im Repository verfügbar. Beispiele:

```text
$impeccable critique die Operator-Ansicht
$impeccable clarify die Statusmeldungen
$impeccable distill die Run-Details
$web-design-guidelines prüfe die Operator-Oberfläche
```

Impeccable enthält die Referenzen, Helferskripte und Codex-Agentdefinitionen in
seinem eigenen Skill-Ordner. Der Einstieg löst Helferpfade relativ zu diesem
Ordner auf; sein tatsächlicher Pfad hier ist:

```sh
.codex/skills/impeccable/scripts/impeccable context --target microsoft-agent-framework-work-package-pilot/src/Wpcp.Api/wwwroot/operator/index.html
```

Der Launcher nutzt die Engine-Version aus `impeccable/scripts/VERSION`
(bei Installation 0.1.5). Er lädt bei Bedarf das passende, per SHA-256 geprüfte
Binary in den normalen Laufzeitcache `~/.impeccable/bin`. Dieser Cache enthält
keine global installierten Skills. Der dokumentierte Upstream-Mechanismus
unterstützt alternativ `IMPECCABLE_HOME` oder `IMPECCABLE_BIN`.

Automatische Impeccable-Hooks wurden nicht eingerichtet. Der Skill kann manuell
aufgerufen werden und fordert bei UI-Änderungen den passenden Detektorlauf an.
Die Installation erzeugt keine Produkt-/Designvorgaben in `PRODUCT.md` oder
`DESIGN.md`; vorhandene Anforderungen bleiben maßgeblich.

Vercels Skill lädt bei jeder Prüfung die aktuelle
[Regelquelle](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md).
Der Skill ist gepinnt, die Regeln werden entsprechend seinem Upstream-Vertrag
aktuell abgerufen.

## Herkunft und Updates

[sources.lock.json](sources.lock.json) enthält Repository, Commit, Quellpfad,
Version und SHA-256 jedes importierten Dokuments/Skripts. Die Skill-Dateien sind
unveränderte Upstream-Kopien. Impeccables `LICENSE` und `NOTICE.md` stammen aus
demselben Commit. Vercel nennt MIT in seinem Repository-README; der gepinnte Baum
enthält keine separate Root-Lizenzdatei.

Bei Updates den neuen Stand zuerst außerhalb der aktiven Skill-Ordner vorbereiten,
mit dem gepinnten Stand vergleichen und Referenzen sowie Helfer prüfen. Danach
gezielt die beiden lokalen Ordner und ihre Lockeinträge aktualisieren. Lokale
Änderungen nicht überschreiben. Den globalen Skill-Sync nicht verwenden und
keine globale CLI-Installation ausführen.

## Installationsprüfung vom 14.09.2026

- Beide Skill-Namen und YAML-Einstiege erfolgreich gelesen.
- Alle direkt aus den SKILL-Dateien verlinkten lokalen Referenzen vorhanden.
- 58 Impeccable-Dateien und die Vercel-SKILL-Datei stimmen bytegenau mit den
  dokumentierten Upstream-Commits überein; ausführbare Dateirechte erhalten.
- `engine-probe` meldet `impeccable-engine 0.1.5`.
- Kontextauflösung erkennt dieses Repository und verwendet den Helferpfad
  `.codex/skills/impeccable/scripts/impeccable`.
- Der mechanische Detektor wurde auf `operator.css` ausgeführt und lieferte
  gültiges JSON (`[]`). Das ist ein Funktionstest des Helfers, keine UI-Abnahme.
- Vercels Regelquelle erfolgreich abgerufen (7.760 Bytes).
- `skills-repo` und globale Skill-Links unverändert.

Dies belegt die lokale Installation und die grundlegende Nutzbarkeit der Helfer.
Eine vollständige Design-, Accessibility- oder Browser-Abnahme der Anwendung
ist nicht Bestandteil dieser Installation.
