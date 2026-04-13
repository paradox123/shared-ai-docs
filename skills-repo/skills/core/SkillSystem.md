# Custom Skill System

**The MANDATORY configuration system for ALL skills.**

## THIS IS THE AUTHORITATIVE SOURCE

This document defines the **required structure** for every skill in the system.

## kebab-case Naming Convention (MANDATORY)

**All naming in the skill system MUST use kebab-case.** Exception: `CORE` retains uppercase as the always-loaded system skill.

| Component | Wrong | Correct |
|-----------|-------|---------|
| Skill directory | `CreateSkill`, `createskill` | `skill-creator` |
| YAML name | `name: CreateSkill` | `name: skill-creator` |
| Workflow files | TitleCase or lowercase ok inside skill | `Create.md`, `create.md` |
| Tool files | TitleCase or lowercase ok inside skill | `ManageServer.ts`, `manage-server.ts` |

## The Required Structure

Every SKILL.md has two parts:

### 1. YAML Frontmatter (Single-Line Description)

```yaml
---
name: skill-name
description: [What it does]. USE WHEN [intent triggers using OR]. [Additional capabilities].
---
```

**Rules:**
- `name` uses **kebab-case**
- `description` is a **single line** (not multi-line with `|`)
- `USE WHEN` keyword is **MANDATORY**
- Max 1024 characters

### 2. Markdown Body (Workflow Routing + Examples)

```markdown
# skill-name

[Brief description]

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **WorkflowOne** | "trigger phrase" | `Workflows/WorkflowOne.md` |

## Examples

**Example 1: [Use case]**
\`\`\`
User: "[Request]"
→ Invokes WorkflowOne workflow
→ [Result]
\`\`\`
```

## Directory Structure

```
skill-name/
├── SKILL.md              # Main skill file
├── quick-start-guide.md  # Context files in root
├── Tools/                # CLI tools (ALWAYS present)
│   └── ToolName.ts
└── Workflows/            # Work execution workflows
    └── Create.md
```

## Complete Checklist

- [ ] Skill directory uses kebab-case
- [ ] YAML `name:` uses kebab-case
- [ ] Single-line `description` with `USE WHEN` clause
- [ ] `## Workflow Routing` section with table format
- [ ] `## Examples` section with 2-3 usage patterns
- [ ] `Tools/` directory exists (even if empty)
