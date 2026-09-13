# Karpathys LLM-Wiki: Konzeptprüfung

Stand: 12.09.2026. Primärquelle ist Andrej Karpathys Gist **LLM Wiki**, ausschließlich der Autorentext; Kommentare und Implementierungen wurden nicht als Konzeptvorgaben verwendet.

## Aussagen des Originals

- **Dauerhafte Synthese:** Ein verlinktes Markdown-Wiki zwischen Mensch und Quellen bewahrt erarbeitetes Wissen. Das LLM pflegt es; der Mensch kuratiert Quellen, fragt und steuert. Obsidian dient zum Lesen und Erkunden. [The core idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#the-core-idea)
- **Schreibgrenze:** Raw-Quellen sind unveränderlich für das Wiki-LLM: Es liest, verändert sie aber nicht. Das LLM schreibt Wiki-Seiten, auch aufgrund des Gesprächs. Menschen schreiben laut Einleitung nie oder selten selbst; das ist kein technisches Bearbeitungsverbot. Ein gemeinsam weiterentwickeltes Schema regelt Struktur und Abläufe. [Architecture](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#architecture), [The core idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#the-core-idea)
- **Nachpflege:** Ingest verarbeitet auf Anstoß Quellen und aktualisiert betroffene Seiten. Weniger beaufsichtigte Stapelverarbeitung ist möglich. Query beantwortet Fragen; geeignete Antworten können ins Wiki zurückfließen. Periodisch angefordertes Lint sucht unter anderem Widersprüche und veraltete Aussagen. Ein unbeaufsichtigter Dateiwächter und vollständige Abhängigkeitsfortschreibung bei jeder Quellenänderung sind nicht vorgeschrieben oder garantiert. [Operations](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#operations)
- **Umsetzungsfreiheit:** Git wird genannt; der abschließende Hinweis beschreibt das Muster ausdrücklich als abstrakt, optional und modular. Dynamischer Umfang nach geklonten Repos und Löschfolgen sind nicht festgelegt. [Tips and tricks](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#tips-and-tricks), [Note](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#note)

## Daniels zusätzliche Vorgaben

Die bestehenden, außerhalb der Wiki-Pflege veränderlichen Markdown-Repos bleiben Input im Obsidian-Vault. Das Wiki hat kein eigenes Git-Repo; sein Kontext folgt den eingebundenen Repos. Bei entfallendem Input verschwinden abhängige Erkenntnisse und können später neu entstehen. Das Wiki ist erster Einstieg für Mensch und Agent; Quellenänderungen sollen betroffene gemeinsame Aussagen erkennbar machen.

Diese Vorgaben ergänzen das Original. Ihre Umsetzung und Überprüfbarkeit sind bei der noch offenen Repository-Auswahl zu prüfen; insbesondere liefert das Konzept allein keinen Nachweis vollständiger Änderungsfolgen-Erkennung. Siehe [Konzeptstand](2026-09-11-kontextabhaengiges-llm-wiki.md).
