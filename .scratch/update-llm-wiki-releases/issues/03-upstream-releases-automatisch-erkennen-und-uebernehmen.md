# 03: Upstream-Releases automatisch erkennen und übernehmen

**What to build:** Neue veröffentlichte LLM-Wiki-Releases werden regelmäßig erkannt, reproduzierbar geprüft und bei Erfolg automatisch auf dem Mac aktiviert. Der gesamte Ablauf benötigt im Erfolgsfall keine Vorlage an den Betreiber; gescheiterte Übernahmen bleiben nachvollziehbar sichtbar.

**Blocked by:** 02 — Geprüften Wiki-Stand auf dem Mac aktivieren.

**Status:** ready-for-agent

- [ ] Ein regelmäßig ausgeführter, dokumentierter und reproduzierbar einrichtbarer Updatecheck verfolgt reguläre veröffentlichte Releases des bestätigten Upstream-Projekts und ordnet sie ihrem exakten Commit zu. Der Zeitplan und der tatsächlich aktive Stand sind erkennbar.
- [ ] Neue Hauptbranch-Commits, bloße Tags, Release-Entwürfe und einzelne Library-Releases lösen kein Update aus. Vorabversionen werden standardmäßig ausgeschlossen. Ohne neues geeignetes Release endet der Check ohne Versionsänderung.
- [ ] Ein neues Release durchläuft Kandidateninstallation, Build, alle erforderlichen Integrationstests und lokale Aktivierung. Der geprüfte Release-Commit bleibt über die gesamte Kette identisch; fehlende, ausstehende oder fehlgeschlagene Pflichtprüfungen blockieren die Übernahme.
- [ ] Falls Renovate eingesetzt wird, aktualisiert es ausschließlich unsere Referenz auf das veröffentlichte Wiki-Release. Es führt keine eigenständigen Updates interner Compiler-Abhängigkeiten und keine Änderungen im Upstream-Repository aus. Etwaige Integrations-PRs werden nach erfolgreichen Pflichtprüfungen automatisch gemergt, auch ohne gesonderte menschliche Freigabe bei einem Major-Release.
- [ ] Ein Integrations-Merge wird erst nach tatsächlich verifizierter Aktivierung als erfolgreiche Mac-Aktualisierung gemeldet. Nach Unterbrechung kann der Ablauf nachvollziehbar fortsetzen, ohne den bisherigen funktionsfähigen Stand zu verlieren.
- [ ] Ein fehlgeschlagener Updateversuch meldet Release, fehlgeschrittene Prüfung und weiterhin aktiven Stand über einen im Zielbetrieb verifizierten Benachrichtigungsweg. Erfolgreiche unveränderte Checks benötigen keine menschliche Bearbeitung.
- [ ] Der automatische Auslöser wird im tatsächlichen Laufzeitkontext nachgewiesen. Ein kontrollierter Releasewechsel, ein unveränderter Check und ein gescheiterter Kandidat belegen die vollständige Kette; kontrollierte Szenarien werden nicht als bereits beobachtetes neues Upstream-Release ausgegeben.
- [ ] Die bestehende Wissenspflegeautomation bleibt unverändert; unabhängige Node-, QMD- und Wrapper-Updates sowie die offenen Wiki-Migrationsarbeiten werden nicht in diesen Ablauf aufgenommen.
