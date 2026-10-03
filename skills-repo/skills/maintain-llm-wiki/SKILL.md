---
name: maintain-llm-wiki
description: Maintain selected, durable multi-source synthesis notes in DanielsVault as ordinary Markdown. Use when the user explicitly asks to create, save, revise or maintain LLM wiki knowledge, or to check its original-source freshness. Do not use for ordinary document retrieval, automatic full imports or QMD index maintenance.
---

# Maintain LLM Wiki

Preserve useful conclusions across sources. The agent reads and edits Markdown directly;
`wiki_sources.py` only records or compares direct original-source hashes.

## Locations and scope

- Vault: `/Users/dh/Documents/DanielsVault` (honor `DANIELSVAULT_ROOT` or an explicitly supplied vault).
- Active wiki: `<vault>/_shared/contextual-llm-wiki/common/wiki`.
- Knowledge pages: `notes/<topic>.md`; entry: `index.md`; completed work: `log.md`.
- Helper: this skill's `scripts/wiki_sources.py`. Resolve it from the skill location.
- Read the vault's `VAULT_AGENT_STRUCTURE.md`, relevant repository instructions and wiki `AGENTS.md`.
  For an explicitly supplied test wiki, use its equivalent paths; never redirect to production implicitly.

Resolve the requested topics, pages and originals. Keep each maintenance task bounded to that scope.
Do not invent a whole-vault import, source summaries for every file, or a provider/queue workflow.
Avoid simultaneous edits to the same page. Originals remain in their repositories and are never
moved, copied into a retrieval store, or edited by wiki maintenance.

## Check or research

```bash
python3 <skill>/scripts/wiki_sources.py check --vault <vault> --wiki <wiki> --page notes/<topic>.md
```

`--page` is repeatable; omit it to check all curated notes. Check is read-only and makes no model,
compiler or QMD calls. JSON reports each page as `unchanged`, `review` or `invalid`, and each source
as `unchanged`, `changed` or `missing`. Exit 1 means review need, invalid metadata or an input error.
Source hashes identify file versions; equal hashes do not prove the prose is correct.

For ordinary research, use `qmd` / `rag-documentation-research` with relevant original collections
and optional `contextual-wiki-common` hits. Before using a wiki claim, run the selected page check
and read its relevant originals. Changed, missing or invalid evidence requires current original
research and a visible limitation. A research question does not authorize saving or stamping notes.

## Create or revise selected knowledge

1. Find existing relevant pages via the wiki index, targeted QMD or exact filename search.
2. Read every original supporting the intended claims. Use relevant current passages, not old source
   summaries, compiler caches or a note cited by another note. If an original is missing, do not
   present its historical claims as currently verified.
3. Write a focused synthesis that explains the shared conclusion, implications, disagreement and
   remaining gaps. Attribute claims directly to original files with resolvable Markdown links.
   A page may join sources across repositories. Keep repository instructions and source authority.
4. A page contains a title, clear topic scope, useful synthesized knowledge and original links.
   Navigation links between notes are allowed; they create no transitive evidence dependency.
5. After content review, record all and only its supporting originals:

```bash
python3 <skill>/scripts/wiki_sources.py record --vault <vault> --wiki <wiki> \
  --page notes/<topic>.md --source <original-one> --source <original-two>
```

Original arguments can be absolute or vault relative; metadata stores normalized vault-relative
paths. Record requires one existing page and existing originals inside the vault, outside the wiki
and technical `.state`, `.llmwiki` or `.rag` mirrors. It atomically replaces only its own metadata;
it does not review, rewrite prose or index content. The generated frontmatter uses single-line JSON:

```yaml
---
title: Topic
reviewed_at: "2026-10-02T12:00:00+00:00"
wiki_sources: [{"path":"_shared/repo/docs/source.md","sha256":"<64 hex characters>"}]
---
```

6. Run `check` on the finished page. Inspect its prose and all links. Update `index.md` and `log.md`
   with the actual completed scope and unresolved gaps. If a selected page and sources are already
   unchanged and its content is still sound, avoid rewriting it merely to create activity.
7. Report the page, sources and verified scope. A successful page is no claim of global completeness.
   Independently verified pages can complete while another page remains unresolved. Never stamp
   unresolved claims as current just to make a checker green.

## Retrieval index

The existing QMD-only daily automation indexes originals and curated notes. Do not add wiki generation
to it. If the user needs an updated note searchable now, run the existing QMD maintenance separately
using the `qmd` skill. Index failure does not erase a reviewed note; disclose the retrieval limitation.
The obsolete compiler implementation, entrypoints and release updater have been removed.
Current operating examples: [wiki guide](../../../docs/rag/llm-wiki.md).
