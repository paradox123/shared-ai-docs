---
name: documentation
description: NCG infrastructure documentation system. USE WHEN query infrastructure, find server details, search documentation, document changes, update architecture, create runbook, explain configuration. Integrates with Obsidian vault at DanielsVault/ncg/ncg-docs/docs/.
---

# Documentation - NCG Infrastructure Knowledge Base

**Auto-routes when user needs infrastructure information or wants to document changes.**

## Overview

The Documentation skill provides complete access to NCG operations documentation:
- Query server details, IPs, configurations
- Search across all infrastructure docs
- Document infrastructure changes in Obsidian vault
- Generate runbooks and procedures
- Track architecture updates

**Vault Location**: `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/`

**Structure**:
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/` - Operations documentation
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Dev/` - Development documentation
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/` - Project specifications
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Security/` - Security documentation

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **QueryInfrastructure** | "what is the IP", "where is", "show server" | `Workflows/QueryInfrastructure.md` |
| **DocumentChange** | "document this change", "update docs", "record deployment" | `Workflows/DocumentChange.md` |
| **GenerateRunbook** | "create runbook", "procedure for", "how to guide" | `Workflows/GenerateRunbook.md` |
| **SearchDocumentation** | "search docs", "find information about" | `Workflows/SearchDocumentation.md` |
| **ExplainConcept** | "explain", "what is", "how does work" | `Workflows/ExplainConcept.md` |

## Context Files

- **ServerMap.md** - Complete IP address and service mapping
- **VaultStructure.md** - Obsidian vault organization
- **DocumentationIndex.md** - Quick reference to all docs

## Tools

- **SearchVault.ts** - Full-text search across NCG documentation
- **UpdateChangelog.ts** - Append infrastructure changes to changelog
- **GenerateServerMap.ts** - Create current infrastructure diagram

## Examples

**Example 1: Query server IP**
```
User: "What's the IP of the dev database server?"
→ Invokes QueryInfrastructure workflow
→ Searches ServerMap.md for "dev-database"
→ Returns: "10.0.0.7"
```

**Example 2: Document deployment**
```
User: "Document deployment of backend v2.1.0 to dev"
→ Invokes DocumentChange workflow
→ Creates entry in ncg/ncg-docs/docs/Ops/CHANGELOG.md
→ Updates last deployment date
→ Commits to vault
```

**Example 3: Create runbook**
```
User: "Create a runbook for restarting all backend services"
→ Invokes GenerateRunbook workflow
→ Reads Dev-Environment.md and GitLab-CI-CD.md
→ Generates step-by-step procedure
→ Saves to Guides/Runbooks/RestartBackend.md
```

**Example 4: Search documentation**
```
User: "Find all references to MongoDB authentication"
→ Invokes SearchDocumentation workflow
→ Searches ncg/ncg-docs/docs/ for "MongoDB" + "authentication"
→ Returns relevant sections with file paths
```

---

## Quick Reference

**Server IPs (Most Common)**:
- Dev App: 10.0.0.10
- Dev DB: 10.0.0.7
- Dev Registry: 10.0.0.11
- Prod App: 10.1.0.10
- Prod DB: 10.1.0.8

**Documentation Locations**:
- Infrastructure: `ncg/ncg-docs/docs/Ops/Infrastructure/`
- Services: `ncg/ncg-docs/docs/Ops/Services/`
- Security: `ncg/ncg-docs/docs/Security/`
- Specifications: `ncg/ncg-docs/docs/Specs/`
- Development: `ncg/ncg-docs/docs/Dev/`
- Guides: `ncg/ncg-docs/docs/Ops/Guides/`
- Troubleshooting: `ncg/ncg-docs/docs/Ops/Troubleshooting/`
