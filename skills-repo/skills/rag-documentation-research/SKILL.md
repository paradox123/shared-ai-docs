---
name: rag-documentation-research
description: Research DanielsVault knowledge through QMD, verify findings against original source files, and hand off grounded evidence for planning or implementation. Use for finding or synthesizing vault documentation; ordinary research does not maintain the index or save answers.
---

# DanielsVault Documentation Research

Start DanielsVault documentation searches with QMD over relevant original-source collections from `_shared/danielsvault-rag/qmd-collections.json`; optionally add the curated `contextual-wiki-common` collection. Use `qmd search` for exact names and identifiers and `qmd query` for natural-language questions. Pass `-c` for each selected collection to keep historical or copied wiki content out of the task. This skill owns source discovery and verification; after gathering evidence, continue the user's requested artifact or implementation. Explicit wiki ingestion, update or review work uses [maintain-llm-wiki](../maintain-llm-wiki/SKILL.md). WikiQuery is retired.

## Entry and source verification

Honor repository startup requirements and the task's explicit boundaries. Already named primary documents may be opened directly. Inside session-review automations, read the required automation/session state before knowledge retrieval.

Use the existing QMD index; this example searches the original `shared-ai-docs` collection:

```bash
qmd query '<specific question>' -c shared-ai-docs
```

Select collections according to the task and repository navigation rules; repeat `-c` for several originals or an optional curated-wiki collection. Do not infer a private access restriction from a directory name. QMD results are discovery aids: open the cited or retrieved originals and verify their relevant passages. Before relying on a curated wiki note, use the read-only `wiki_sources.py check --vault PATH --wiki PATH --page PAGE` interface described in the maintenance skill. For `review`, `invalid` or missing provenance, use current originals and state the note's limitation. `unchanged` confirms only the recorded original bytes; read relevant original passages before presenting claims. A useful note leads to its direct originals rather than a compiler dependency graph.

1. Inspect QMD results and identify the original paths supporting each relevant claim.
2. Read the relevant sections from those original files; check their current contents and follow repository instructions, OpenSpec requirements, and ADRs as applicable.
3. Use targeted literal checks in known sources when needed. If QMD has no useful result, state the gap and continue with already named sources or bounded discovery appropriate to the task.
4. Report the question/search used, relevant original paths and sections, and any missing evidence or conflicts. Do not claim that QMD search results alone establish source freshness.

Keep the execution handle of a running QMD query and follow that execution to completion. Retrieval does not update the index, create a saved answer or record a new reviewed timestamp. A read-only source check is permitted; do not run maintenance or save content for ordinary research.

## Evidence handoff

Return the relevant original paths and sections, a brief explanation of their relevance, the QMD search used, and any remaining gaps or conflicts. Search results are navigation hints; original requirements, AGENTS, OpenSpec and ADRs retain their authority. A documentation lookup does not prove runtime behavior.

## Operations and compatibility

Use the [operations guide](../../../docs/rag/llm-wiki.md) when the user asks about wiki operation. Explicit maintenance uses the shared maintenance skill. Use the QMD skill for index operations and diagnostics. Historical QMD-backed `rag` envelopes remain compatibility interfaces for explicit callers; there is no additional `.rag/store`.

Read [runtime-transfer.md](references/runtime-transfer.md) only for an explicitly requested move or runtime transfer; its historical commands do not override this QMD-first retrieval flow.
