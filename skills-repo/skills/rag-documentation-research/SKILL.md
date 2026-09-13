---
name: rag-documentation-research
description: Research DanielsVault knowledge through managed WikiQuery, verify its original-source references, and hand off grounded evidence for planning or implementation. Use for finding or synthesizing vault documentation; ordinary research does not maintain the index or save answers.
---

# DanielsVault Documentation Research

Start knowledge-context searches through the common wiki's managed WikiQuery. QMD is its internal persisted retrieval engine. This skill owns source discovery and verification; after gathering evidence, continue the user's requested artifact or implementation.

## Entry and source verification

Honor repository startup requirements and the task's explicit boundaries. Already named primary documents may be opened directly. Inside session-review automations, read the required automation/session state before knowledge retrieval.

Use the existing local installation:

```bash
WIKI_HOME=/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki
"$WIKI_HOME/wiki" query --config "$WIKI_HOME/.local/common.json" \
  --question '<specific question>'
```

For an explicitly repository-limited task, append `--repo <id>` (repeat for multiple allowed repos). Registered identities are `vault-root`, `meeting-assistant`, `shared-ai-docs`, `ki-fuer-kmu`, `ncg-docs`, `private`, `probare-crm`, and `sparkle`. Exact source limits use repeated `--source '<repo-id>/<relative.md>'`. WikiQuery enforces these limits across transitive evidence. Do not infer a private access restriction from a directory name.

1. Inspect `ok`, `answer`, `evidence`, `originals`, `review`, and `fallback`.
2. Follow selected `originals[].path` or `uri` references; read the relevant original sections before relying on their claims. `hash` and `freshness` identify the checked original version.
3. Treat `review` as visible maintenance needs. `fallback:true` means the same interface used current original evidence instead of eligible stored wiki knowledge. It does not certify the stale wiki pages.
4. Report missing evidence or an unavailable WikiQuery. Do not silently start a parallel QMD or broad `rg` context search. Already supplied or returned primary paths remain directly readable; targeted literal checks in those sources are appropriate.

Keep the execution handle of a running query and follow that execution to completion. A query does not compile or create a saved answer unless the user requests saving. Do not invoke `maintain` or add `--save` for ordinary research.

## Evidence handoff

Return the relevant original paths and sections, a brief explanation of their relevance, the managed query used and its freshness/fallback result, and any remaining gaps or conflicts. Wiki text is derived evidence; original requirements, AGENTS, OpenSpec and ADRs retain their authority. A documentation lookup does not prove runtime behavior.

## Operations and compatibility

Use the [operations guide](../../../contextual-llm-wiki/OPERATIONS.md) for the installed runtime, maintenance, diagnostics and production acceptance status. Direct QMD belongs to index operations and diagnostics; historical QMD-backed `rag` envelopes remain compatibility interfaces for explicit callers, not a second standard context route. There is no additional `.rag/store`.

Read [runtime-transfer.md](references/runtime-transfer.md) only for an explicitly requested move or runtime transfer; its historical QMD commands do not override this context entry.
