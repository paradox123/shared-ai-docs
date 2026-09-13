> Evidence des echten Providerlaufs. Der Antworttext ist unverändert; relative Seitenlinks wurden für diese Kopie auf die lokale aktive Ausgabe aufgelöst.

# QMD: Welche gemeinsame Architekturentscheidung beschreiben das Betriebsmodell und die Runtime-Dokumentation, welche Rollen bleiben getrennt und welche Grenzen gelten?

Beide Dokumentationen beschreiben dieselbe Architekturentscheidung: **QMD übernimmt allein die persistierte Indexierung, Embeddings und das Retrieval für DanielsVault.** `rag` bleibt als Kompatibilitäts- und Workflow-Adapter erhalten, ohne eigenen Chunk-, Datensatz- oder `.rag/store`-Speicher. Die Runtime-Dokumentation ergänzt, dass QMD seinen lokalen Standarddatenort verwendet. [concepts/qmd-als-einzige-persistierte-retrieval-engine; concepts/qmd-als-zentrale-wissensabruf-engine]

Die Rollen bleiben getrennt:

- **QMD:** `qmd update` pflegt den lexikalischen Index, `qmd embed` erzeugt Embeddings, `qmd search` und `qmd query` liefern gerankte Treffer. Agenten nutzen QMD gewöhnlich direkt. [concepts/qmd-als-einzige-persistierte-retrieval-engine; concepts/direkter-wissensabruf-mit-qmd]
- **`rag`:** erhält bestehende CLI-, JSON- und Workflow-Verträge. Bei strukturierten Abfragen wählt QMD Quelldokumente aus; anschließend werden Fakten transient daraus extrahiert. **Gezieltes `rg`** übernimmt laut Betriebsmodell die exakte Fallback-Suche. [concepts/qmd-gestützte-rag-kompatibilitätsschicht]
- **Manifest, Helper und Automation:** `qmd-collections.json` definiert Collections, Pfade und Scopes; der Synchronisationshelper gleicht sie ab; die tägliche Automation übernimmt die Indexpflege. [concepts/manifestbasierte-verwaltung-von-qmd-sammlungen]

Dabei gelten folgende Grenzen:

- **Datenschutz und Abdeckung:** `private` ist nur über einen expliziten Private-Scope erreichbar und aus `all` ausgeschlossen. Verschachtelte Git-Repositories werden jeweils ab ihrem Root mit `**/*.md` erfasst; getrennte Vault-Collections verhindern Doppelindexierung. Zusatz-Collections erfassen sonst übersprungenes versioniertes Markdown, etwa in versteckten Verzeichnissen und `vendor`. [concepts/repository-gerechte-markdown-indexierung; concepts/manifestbasierte-verwaltung-von-qmd-sammlungen]
- **Konfigurationsänderungen:** Fehlende Collections werden kontrolliert ergänzt. Abweichende Pfade oder Patterns werden nicht automatisch umgebogen; Konflikte blockieren und verlangen bewusste Korrektur. Die Runtime beschreibt für die Einrichtung zuerst eine lesende Prüfung und erst danach `--apply`. [concepts/deklarative-collection-verwaltung; concepts/manifestbasierte-verwaltung-von-qmd-sammlungen]
- **Betrieb:** Das Betriebsmodell präzisiert die Erfolgsbedingungen: konfliktfreier Abgleich → erfolgreiches `qmd update` → `qmd embed` → Statusdokumentation. Fehlendes Runtime-Binary, Collection-Konflikte oder Berechtigungsfehler führen zum Abbruch; Projekt-Repositories werden nicht editiert. [concepts/tägliche-qmd-wartung-mit-fail-closed-verhalten]

Die vorliegende Evidenz zeigt keinen Architekturwiderspruch. Die Dokumente unterscheiden sich im Detailgrad: Transiente Faktenextraktion, `rg`-Fallback und ausdrückliches Fail-closed-Verhalten stammen aus dem Betriebsmodell; lokalen Indexort und Einrichtungsprüfung konkretisiert die Runtime-Dokumentation. [concepts/qmd-gestützte-rag-kompatibilitätsschicht; concepts/tägliche-qmd-wartung-mit-fail-closed-verhalten; concepts/qmd-als-zentrale-wissensabruf-engine]

## Verwendete Evidenz

- [concepts/qmd-als-einzige-persistierte-retrieval-engine](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/qmd-als-einzige-persistierte-retrieval-engine.md) @ 172ecda7fb70a03881443f3ac15ccfe8c57cef85439f03ed3b7467bda8e3606d
- [concepts/direktes-qmd-retrieval-mit-exakter-fallback-suche](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/direktes-qmd-retrieval-mit-exakter-fallback-suche.md) @ 834385b2d1cfc9c236f0e5c6f172d7c6a6c124b7d94ee5e63cbd2a15449e9723
- [concepts/qmd-gestützte-rag-kompatibilitätsschicht](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/qmd-gest%C3%BCtzte-rag-kompatibilit%C3%A4tsschicht.md) @ b74e7957e447b393416bd243bdcc885242d1b24d9e933e9b1624a01bd7811c9e
- [concepts/tägliche-qmd-wartung-mit-fail-closed-verhalten](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/t%C3%A4gliche-qmd-wartung-mit-fail-closed-verhalten.md) @ 4e2a1d73b2d66ba793f9fbcbf6e346d6f85106afa46d8c1e56017ec78fdcd229
- [concepts/repository-gerechte-markdown-indexierung](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/repository-gerechte-markdown-indexierung.md) @ 385422104a69dee1709dd5041b7d9f75243b197302d92657b6b46b6f492b92a5
- [concepts/deklarative-collection-verwaltung](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/deklarative-collection-verwaltung.md) @ 1022e19d8e7d41d3618bc0e22caba5ff389acca035c4ed17304e39033c41362e
- [concepts/qmd-als-zentrale-wissensabruf-engine](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/qmd-als-zentrale-wissensabruf-engine.md) @ f24eed0514cbd6f750b4f655d7531bb70399392ebc04f744927b541e477fc705
- [concepts/direkter-wissensabruf-mit-qmd](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/direkter-wissensabruf-mit-qmd.md) @ e41cb24f1d37570ba99c65572dc921308db4a43ddae051915aea703cb096920f
- [concepts/manifestbasierte-verwaltung-von-qmd-sammlungen](/Users/dh/Documents/DanielsVault/_shared/contextual-llm-wiki/acceptance-general/wiki/concepts/manifestbasierte-verwaltung-von-qmd-sammlungen.md) @ a4b5fab87eacccbeffb7d16e91f21e3af0ec5b49e8673ca1ab18fc9fcd8c2598

## Originalquellen

- [shared-ai-docs/docs/rag/operating-model-rag-qmd.md](obsidian://open?path=%2FUsers%2Fdh%2FDocuments%2FDanielsVault%2F_shared%2Fshared-ai-docs%2Fdocs%2Frag%2Foperating-model-rag-qmd.md) — SHA-256 e711ebd10e6b3f4596bcbb888af730043b2d1ba620e5d0e2ad3fa4025d5a8207
- [vault-root/_shared/danielsvault-rag/README.md](obsidian://open?path=%2FUsers%2Fdh%2FDocuments%2FDanielsVault%2F_shared%2Fdanielsvault-rag%2FREADME.md) — SHA-256 6b1baaed1f5856b93741c25e5619fef8cb5f3402d70728134b3deff16d60209f
