---
name: zoom-out
description: Tell the agent to zoom out and give broader context or a higher-level perspective. Use when you're unfamiliar with a section of code or need to understand how it fits into the bigger picture.
---

I don't know this area of code well. Go up a layer of abstraction. Give me a map of the relevant modules and callers, using the project's domain glossary vocabulary.

## Bounded reconnaissance order

1. Read applicable repo/subtree startup instructions first (`AGENTS.md` or equivalent), then the project overview, `CONTEXT.md`, domain glossary, and active spec/ADR paths those instructions name. Do not enumerate the tree before satisfying that order.
2. Build a bounded module map from declared entry points, package/project manifests, and the target directory. Prefer shallow directory/file listings and focused `rg -n` queries over broad `find` or full-repo file dumps.
3. Trace public interfaces to direct callers and tests. Expand one layer at a time only when it changes the map.
4. Read large files separately or paginate to EOF. Do not concatenate several full source/spec files into one command; a truncated batch is not evidence that any file was understood.
5. Return the map, the target's role, main inbound/outbound dependencies, and the few unresolved seams that need deeper inspection.

Stop when the target's place in the system is clear enough to answer the current question. This skill maps an unfamiliar area; it does not authorize a repo-wide architecture audit.
