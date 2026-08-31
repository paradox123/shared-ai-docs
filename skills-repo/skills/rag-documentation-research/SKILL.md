---
name: rag-documentation-research
description: QMD-first documentation research for DanielsVault. Use when users ask to find, research, search, or narrow documentation sources before planning or implementation, or when a requested plan, decision template, review, or other grounded artifact requires synthesizing several DanielsVault documents from one supplied starting path. This skill owns retrieval and source verification, not downstream artifact authoring. Use targeted rg only when QMD is unavailable or for final literal verification.
---

# QMD Documentation Research

Use QMD as the single DanielsVault indexing and ranked-retrieval engine. Use this either for a standalone source-finding request or as the bounded retrieval phase of a larger deliverable. In the latter case, build the evidence bundle here and then continue the parent task; do not replace the requested artifact with a source list. The skill keeps its legacy name so existing prompts continue to trigger it; it does not use the historical `.rag/store` indexes.

## Automation Session Guard

When this skill supports a session-review automation, follow that automation's state bootstrap before QMD preflight or documentation retrieval. Search only the repositories, services, or identifiers implicated by the bounded session evidence.

## Preflight

Run one coverage check:

```bash
qmd status
qmd collection list
```

If `qmd status` exits non-zero, treat QMD as unavailable for the remainder of the task. State the blocker once and use targeted `rg`; do not repeat QMD initialization through multiple commands.

## Collection Routing

Prefer the narrowest collection set that covers the question:

- Shared AI workflows, skills, prompts, and OpenSpec: `shared-ai-docs`
- SpecOps entities and dashboards: `shared-specops`
- NCG repository Markdown: `ncg-docs`
- KI repository Markdown: `ki-fuer-kmu-docs`
- Probare CRM repository Markdown: `probare-crm-docs`
- Meeting Assistant repository Markdown: `meeting-assistant-docs`
- QMD-excluded repository Markdown when relevant: `meeting-assistant-agents`, `shared-ai-codex`, `shared-ai-github`, `shared-ai-vendor`, `shared-ai-vendor-council-github`, `shared-ai-vendor-mattpocock-agents`, `ki-fuer-kmu-agents`, `ki-fuer-kmu-codex`, `ki-fuer-kmu-github`, `ncg-agents`
- Meeting and project context: `vault-meetings`, `vault-projects`
- RAG/QMD compatibility workspace and its OpenSpec: `danielsvault-rag`
- Private knowledge: `private`, only when the user or task explicitly selects private scope
- Standalone notes: `sparkle`

Do not query the private collection as part of a generic broad search.
Repository collections cover complete repository roots, including Markdown outside `docs` and `adr`. Add the matching supplementary collection when the question concerns `.agents`, `.codex`, `.github`, or tracked vendor skills, because QMD intentionally excludes hidden directories and directories named `vendor` during parent-root traversal.

## Retrieval Flow

For exact identifiers, filenames, environment variables, route fragments, or titles, start lexically:

```bash
qmd search "<exact term>" -c <collection> -n 20 --json
```

For natural-language questions where document vocabulary is unknown, use ranked hybrid retrieval:

```bash
qmd query "<specific question>" -c <collection> -n 7 --json
```

For questions spanning a known set of domains, repeat `-c` only for those collections. Do not search every collection by default.

Use this bounded sequence:

1. Run one QMD search or query against the narrowest relevant collection set.
2. Project at most seven results: `file`, `title`, `snippet`, `score`, and `docid`.
3. Resolve the selected `qmd://<collection>/<path>` source through `qmd get` or the collection root shown by `qmd collection show <collection>`.
4. Open only the selected on-disk sections and verify claims against source text.
5. If exact QMD search misses an obvious literal, run targeted `rg -n -F` in the implicated documentation root.

Do not treat a QMD snippet as final evidence until the source document and relevant section are opened.

## Compatibility Workflows

The local `rag` command at `~/Documents/DanielsVault/_shared/danielsvault-rag` is a QMD-backed compatibility interface for callers that require the historical `hits[]`, `facts[]`, `research-for-review`, or `spec-closeout` JSON envelopes. It does not own an index.

Prefer native QMD for ordinary research. Use compatibility commands only when their stable envelope is useful:

```bash
rag workflow research-for-review --scope <scope> --query "<question>" --top-k 7 --format json
rag workflow spec-closeout --scope <scope> --change "<change>" --top-k 7 --format json
```

## Local Runtime Transfer Mode

Read [runtime-transfer.md](references/runtime-transfer.md) only when the user asks to move, package, reinstall, or explain the DanielsVault retrieval setup.

## Output Or Handoff Contract

For a standalone research request, return the following. When supporting a downstream artifact, retain the same fields as the internal evidence handoff and then continue the parent workflow:

1. Prioritized source paths.
2. Section or heading when available.
3. A short why-relevant rationale.
4. The collection and retrieval method used (`qmd search`, `qmd query`, compatibility workflow, or `rg` fallback).
5. Gaps, stale paths, or low-confidence findings.

## Guardrails

- Keep private retrieval explicitly scoped.
- Do not claim runtime or system validation from documentation retrieval alone.
- Do not mutate QMD collections or embeddings during ordinary research.
- Do not inspect or repair historical `.rag/store` files; collection/index maintenance belongs to the daily QMD automation or an explicit maintenance task.
- If documentation conflicts with code or OpenSpec, report the conflict instead of silently choosing one.
