# SpecOps

SpecOps ist der Arbeitsname fuer die lokale Control Plane ueber Specs, Artefakte, Releases, Environments und AI-Learnings im DanielsVault.

## Einstieg

1. [MVP Architecture](./mvp-architecture.md)
   - visuelles Zielbild mit Systemkontext, Datenmodell, Flow, Board-Modell und Release-/Environment-Matrix.
2. [Parent-Spec](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-05-04%20SpecOps%20Control%20Plane%20MVP%20Obsidian%20Dataview%20Mermaid.md)
   - Scope, Non-Goals, Decision Freeze Pack, Statusachsen, offene Entscheidungen und vorgeschlagene Child-Specs.

## MVP-Prinzip

Der MVP bleibt local-first:

1. Markdown-Specs bleiben narrative Quelle.
2. Strukturierte Markdown-Entity-Notes mit Frontmatter machen Status und Beziehungen maschinenlesbar.
3. Obsidian Dataview erzeugt Portfolio-Map, projektlokale Boards und Tabellen.
4. Mermaid erzeugt Architektur- und Ablaufdiagramme.
5. Ein SpecOps-Backlog haelt Folgethemen sichtbar, auch wenn die ausloesende Spec bereits accepted ist.
6. ADRs und andere Projektdokumente werden als `type: document` verknuepft, aber nicht als Specs behandelt.
7. Skills, Custom Agents und RAG-Evals werden spaeter ueber Learning-Items angebunden.

## Dashboard

Das Obsidian-Dashboard ist im MVP eine normale Markdown-Datei im Vault. Es enthaelt Dataview-Abfragen, Mermaid-Diagramme und Links zu den Detail-Entity-Notes.

Entscheidung:

1. Der user-facing SpecOps-Bereich liegt unter `_shared/SpecOps/`.
2. Das Dashboard liegt unter `_shared/SpecOps/Dashboard.md`.
3. Taxonomie, Beziehungstypen, Statusdefinitionen und Feldreferenz liegen unter `_shared/SpecOps/Reference/`.
4. Diese Struktur soll spaeter als portabler Baustein fuer Kundenvaults funktionieren.
5. Dataview ist installiert und wird fuer den MVP verwendet.

## Entschieden

1. Release-Records starten im MVP als Feld `releases`; eigene Release-Entity-Notes kommen spaeter.
2. Nach dem RAG-Pilot folgt ein kleines gemischtes Backfill-Set aus Nebenkosten-Umbrella, Nebenkosten-Slice und CheckBuild-Spec.
3. Die vorgeschlagene Taxonomie und Beziehungstypen werden fuer den MVP uebernommen und nach dem Backfill bei Bedarf korrigiert.

## Empfohlener erster Slice

Start mit einem **RAG Project Board Pilot**:

1. minimales Entity-Note-Schema,
2. drei bis fuenf RAG-nahe Entity Notes,
3. Portfolio-Map,
4. DanielsVault-RAG-Board,
5. SpecOps-Backlog-View,
6. Missing-Metadata-View.

Dieser Slice prueft das Modell sichtbar, ohne historischen Voll-Backfill oder Skill-Automatisierung vorauszusetzen.
