---
name: context-bootstrap
description: Bootstraps NCG session context at startup by collecting repository structure, runnable commands, and architecture anchors from source and documentation. AUTO-LOAD at session start when the active repository is /Users/dh/Documents/Dev/NCG/ncg-backend.
---

# ContextBootstrap

Initializes NCG project context at agent startup so implementation sessions begin with deterministic baseline knowledge even when repository READMEs/AGENT files are sparse.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **Initialize** | "session start in /Users/dh/Documents/Dev/NCG/ncg-backend", "bootstrap context", "initialize context", "start session context" | `workflows/Initialize.md` |

## Rules

- Run automatically at startup only when current repository root is `/Users/dh/Documents/Dev/NCG/ncg-backend`.
- Primary source roots:
  - Source: `/Users/dh/Documents/Dev/NCG/ncg-backend`
  - Docs: `/Users/dh/Documents/DanielsVault/ncg`
  - Priority docs files (specific anchors):
    - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/README.md`
    - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Environments/Development/Dev-Environment.md`
    - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/GitLab-CI-CD.md`
    - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/Service-Dependency-Graph.md`
    - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Security/Secrets-Management.md`
    - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Security/Certificates.md`
- Gather baseline context in this order: repository structure, build/run/test commands, architecture/service boundaries, ops guides, active conventions.
- If `README.md` and/or `backend/sources/AGENT.md` are missing or shallow, infer commands and architecture from manifests/config/scripts and targeted documentation anchors.
- Return concise deterministic output with fixed headings (see workflow output contract).
- Do not invent commands; only include commands directly found in code/config/docs. Mark unknowns explicitly.
- Include a confidence note per section: `high` (directly documented), `medium` (inferred from config/code), or `low` (weak signal).

## Examples

**Example 1: Auto-start in NCG repo**
```
User starts agent in /Users/dh/Documents/Dev/NCG/ncg-backend
→ Invokes Initialize workflow
→ Returns startup context (structure, commands, architecture, docs anchors)
```

**Example 2: Manual invoke**
```
User: "initialize context"
→ Invokes Initialize workflow
→ Returns refreshed startup context for current NCG repository
```
