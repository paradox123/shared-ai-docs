## Why

Daniels bestehende Markdown-Repos sollen als Fachquellen erhalten bleiben, während gemeinsame Erkenntnisse über Fragen und Sessions hinweg nutzbar werden. Atomicstratas LLM-Wiki-Compiler ist als Implementierung gewählt; die fehlende Anbindung externer Repo-Kontexte und die Nachpflege auch gespeicherter Gesprächssynthesen müssen ergänzt werden.

## What Changes

- Atomicstrata am geprüften Commit `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` als Compilerbasis integrieren und dessen Karpathy-Abläufe weiterverwenden.
- Einen gerichteten Abgleich externer Markdown-Fachquellen in einen gemeinsamen lokalen Compiler-Arbeitsbereich einführen; Originalrepos bleiben an ihrem Ort und werden vom Wiki-Prozess nicht geschrieben.
- Die acht vorhandenen regulären DanielsVault-Repo-Wurzeln mit konkreten Clone-Pfaden und Markdown-Filtern initial registrieren; private Quellen getrennt und weitere Checkouts/Test-Repos ausgeschlossen halten.
- Die Vault-Ordner Meetings und Projects einschliesslich ihrer fachlichen Markdown-Unterordner ausdrücklich als initiale Quellen aufnehmen.
- Quellenstände, Originalverweise und direkte sowie indirekte Abhängigkeiten auch für gespeicherte Gesprächssynthesen führen.
- Nach Quellenkorrektur betroffene Seiten gezielt prüfen; nach Kontextentzug abhängige Inhalte aus dem aktiven Wiki und dessen Suche entfernen, bei Rückkehr neu aufbauen.
- Das Wiki als Markdown-Einstieg für Mensch in Obsidian und Agent über eine gemeinsame öffentliche Integrationsschnittstelle bereitstellen. Das generierte Wiki hat kein eigenes Git-Repo.
- QMD als einzige persistierte Retrieval-Engine erhalten; Compilerindexierung und Retrieval entsprechend anbinden, statt still einen zweiten Suchindex einzuführen.
- Wiederholbare, beobachtbare Pflege auf expliziten Aufruf und eine Abnahme über echte Compileraufrufe, generierte Dateien, QMD und Obsidian definieren.

## Capabilities

### New Capabilities

- `contextual-llm-wiki`: Kontextspezifische, aus externen Repos abgeleitete Wiki-Schicht mit Quellenabgleich, inkrementeller Synthese, vollständiger Nachpflege der verwalteten Seitentypen, QMD-Zugriff und sichtbarem Betriebszustand.

### Modified Capabilities

Keine bestehenden OpenSpec-Capabilities werden verändert. Das dokumentierte QMD-Single-Engine-Modell bleibt eine Integrationsvorgabe; historische SpecOps-Audits sind keine neue Wiki-Runtime.

## Impact

- Neuer lokaler Integrationscode und zugehörige Agent-/Betriebsanweisungen in shared-ai-docs; versionierte Compilerabhängigkeit, bei Bedarf eine kleine nachvollziehbare Upstream-Erweiterung für Retrieval-/Save-Hooks. Die Markdown-Inhaltsübersicht des Compilers bleibt erhalten.
- Nicht versionierter Wiki-Arbeitsbereich im vorhandenen Obsidian-Vault; Quellenkopien und Betriebsmetadaten werden von aktiven Wiki-Seiten getrennt.
- Explizite QMD-Collection-Anbindung über die bestehende DanielsVault-QMD-Konfiguration. Anpassungen im zuständigen QMD-Repo müssen getrennt nachvollziehbar bleiben; fremde Collections werden nicht pauschal verändert.
- Node-Runtime und konfigurierbarer Modellprovider müssen zum gepinnten Upstream passen. Kein neuer Cloud-Dienst, kein Obsidian-Plugin und keine automatische Umstellung laufender Automationen.
- Die lokale Tracker-Spec beschreibt den Umsetzungsauftrag; dieses Change-Paket hält dessen normative Verhaltensanforderungen und Umsetzungsschritte fest. Auswahlentscheidung ist keine bereits bestandene Laufzeitabnahme.
