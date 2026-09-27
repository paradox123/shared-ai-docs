# Gemeinsames Vault-Wiki mit wiederaufnehmbarer Pflege

Status: accepted
Date: 2026-09-25
Issue source: Local Markdown
Origin: Daniels Bestaetigung der vier Kernanforderungen nach Pruefung der bisherigen Anforderungsherkunft.

## Problem Statement

Daniel will die ausgewaehlten Markdown-Repositories seines Obsidian-Vaults als eine zusammenhaengende Wissensbasis nutzen. Dazu gehoeren auch persoenliche Inhalte, Meetings und Projects. Der bisherige Pflegeprozess fuer den realen Quellenbestand dauert sehr lange. Bei einem Abbruch koennen bereits abgeschlossene Modellantworten der Seitengenerierung verloren gehen und beim naechsten Aufruf erneut Kosten und Laufzeit verursachen. Zusaetzliche Betriebsziele aus frueheren Gespraechen haben das eigentliche Vorhaben unnoetig kompliziert gemacht.

## Solution

Der bestehende Atomicstrata-Compiler liest alle ausdruecklich ausgewaehlten Markdown-Quellen als einen gemeinsamen Bestand und bildet daraus repo-uebergreifende Konzepte. Die Originaldateien bleiben erhalten und sind von den abgeleiteten Aussagen aus erreichbar. Die erzeugten Artikel stehen als Markdown im Vault und werden in einer gemeinsamen QMD-Collection gefunden. Ein wiederholbarer Pflegeaufruf verarbeitet neue, geaenderte und bestaetigt entfernte Quellen. Bei einem Abbruch verwendet der naechste Lauf weiterhin gueltige, bereits abgeschlossene Modellarbeit sowohl aus der Extraktion als auch aus der Seitengenerierung erneut.

Die vorhandene Integration wird auf diese vier Ziele geprueft und nur dort geaendert, wo ein nachgewiesener Abstand besteht. Bisherige Zusatzfunktionen duerfen bestehen bleiben, sind aber keine unabhaengigen Abnahmekriterien dieses Auftrags.

## User Stories

1. As the Vault owner, I want to select Markdown repositories explicitly, so that only my intended source set feeds the wiki.
2. As the Vault owner, I want the selected `private` repository included, so that personal and professional knowledge can be connected in one wiki.
3. As the Vault owner, I want Markdown under Meetings and Projects included, so that those notes contribute to the same wiki.
4. As the Vault owner, I want every selected source to retain its repository and path identity, so that equal filenames from different repositories remain distinguishable.
5. As the Vault owner, I want original source files left unchanged, so that the compiler cannot silently rewrite my working documents.
6. As a wiki reader, I want a concept page to combine relevant evidence from different repositories, so that I can understand a relationship that is missing from any single document.
7. As a wiki reader, I want a generated claim to point to its original sources, so that I can check the evidence in the Vault.
8. As a wiki reader, I want generated Markdown articles in the Vault, so that I can browse the shared wiki in Obsidian.
9. As a search user, I want those articles in one QMD collection, so that the common wiki is searchable through the existing index.
10. As the operator, I want to rerun one documented maintenance command after a source change, so that the wiki reflects additions, edits, and confirmed removals.
11. As the operator, I want an unchanged completed run to avoid repeating model work, so that normal maintenance stays incremental.
12. As the operator, I want completed extraction responses to survive a process stop, so that a restart does not repeat the same valid requests.
13. As the operator, I want completed page-generation responses to survive a process stop, so that a restart of a large compile does not start that expensive phase again.
14. As the operator, I want resumed results checked against their source and generation contract, so that changed or incomplete work is recomputed instead of published as current.
15. As the operator, I want a failed or interrupted run to report remaining work honestly, so that partial progress is not mistaken for a finished wiki.

## Implementation Decisions

1. Continue using the selected Atomicstrata compiler and the existing shared Wiki integration. Do not build a second compiler or a separate wiki per repository.
2. Use the configured source inventory as the inclusion boundary. `private` denotes a subject area, not a separate access mode. Meetings and Projects are part of the selected common input.
3. Preserve original-source identity, version, and navigable citation in generated knowledge. Publishing a partial or stale page as a completed current article is invalid.
4. Keep generated Markdown in the Vault and register its active article set in the existing QMD collection. Do not make a new retrieval database a precondition for this work.
5. Keep the public maintenance invocation as the operational entry point. A successful no-change repeat must avoid model calls. A changed input must lead to the affected wiki knowledge being reconsidered.
6. Durable model work is reusable only when the exact relevant source versions, prompt/model/compiler contract and required evidence still match. Save an individually completed, validated response before relying on it as restartable progress. A process interruption must not require a whole page-generation batch to finish first.
7. A cache hit is intermediate work, not proof of completed publication. The usual provenance, source-drift, publication, and QMD checks still decide when a page is current.
8. The existing uncommitted page-response-resumption fix is a separate worktree. Integrate or adapt it deliberately after reviewing the changed requirements; this spec does not assume it is already deployed.
9. Previous decisions about next-day deadlines, fairness between backlog and daily changes, mandatory source-summary publication, independent original-source indexing, and a particular query fallback are not acceptance requirements here. Retain a useful existing behavior when it does not obstruct the four goals; remove or simplify it only with evidence of cost or conflict.

## Testing Decisions

The primary test seam is the public maintenance command with temporary selected repositories, the real pinned compiler, generated Vault Markdown, and an isolated real QMD database. Only external model responses are controlled for deterministic tests. This is the highest existing seam and matches the prior shared-wiki and restart tests.

A good test observes source files, generated articles, original citations, QMD search results, provider requests, and the maintenance result. It does not assert private cache layout or internal helper call counts. In particular:

1. Two selected repositories, including a personal source and a project or meeting source, produce one relevant concept article citing both originals; the originals remain byte-identical.
2. The article is present in the Vault output and found through the shared QMD collection.
3. An unchanged second maintenance call makes no new model requests.
4. After a controlled stop during page generation, a fresh process reuses completed responses and finishes with correct provenance and QMD visibility.
5. If a source or generation contract changes between calls, affected saved work is not reused; unrelated valid work remains available.
6. A partial run reports outstanding work and never exposes an incomplete page as current.

The existing end-to-end shared-wiki tests and extraction restart tests provide prior art. The page-response test must reproduce the observed loss before the fix and pass afterward. A later controlled run on a representative Vault subset checks scale and integration without using the live long-running writer as a test fixture.

## Out of Scope

- A fixed daily completion deadline or a throughput guarantee for the initial corpus.
- A required policy for ordering daily changes against the initial backlog.
- A second wiki, a separate private wiki, or a new persistent retrieval engine.
- Replacing Atomicstrata with a custom synthesis implementation.
- Automatic scheduling, automation notification policy, or redesign of WikiQuery unless a failing core scenario requires a specific adjustment.
- General cleanup of working source repositories or changes to original Markdown.

## Further Notes

The common source inventory, repo-crossing synthesis, Vault publication, and QMD registration already have implementation and acceptance evidence. Extraction resumption is present. The concrete observed gap is durable resumption of individual page-generation responses before the full compile completes. The pending isolated fix has passing tests but is not yet committed or activated. Reassess these statements against the target branch and production state before claiming completion.

This specification replaces the broader maintenance interview as the product acceptance boundary for this effort. It does not erase historical documentation or automatically disable existing behavior.

## Acceptance — 2026-09-27

The scoped requirements are accepted. The existing shared source selection, cross-repository synthesis, citations, Vault Markdown, QMD visibility and no-op behavior are covered by the earlier linked Ticket 01/02 evidence and existing public-interface tests. The added restart requirements are covered by the public-helper regression test and the production run receipts in [page-response evidence](../../contextual-llm-wiki/evidence/page-response-resumption-2026-09-25.md): 322 valid page responses were saved in a bounded production run and all 322 were reused by a fresh production process; a changed source is covered by the test's invalidation case. Both production invocations honestly retained pending work and returned non-success.

This accepts this tracker spec's scope. The broader `operate-contextual-llm-wiki` OpenSpec remains active for its independent full-import, later scheduler and upstream-release work.
