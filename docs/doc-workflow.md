# Documentation & Planning Workflow

Documentation and implementation planning follow a structured pipeline of three skills, each handling a distinct phase.

## Pipeline

```
Prompt (Kernanforderungen)
  |  Iteration 0
  v
doc-coauthoring ──── Spec / RFC / Proposal / Decision Doc
  |  "refine the plan"
  v
refine-plan ──────── Implementation Plan mit Verification Test Cases
  |  Implementierung
  v
retro-plan ───────── Retrospektive mit Follow-up Deltas
```

## Skills

### doc-coauthoring

**Purpose:** Co-author specs, proposals, RFCs, decision docs through structured collaboration.

**Stages:**
1. Context Gathering — user dumps context, Claude asks clarifying questions
2. Refinement & Structure — section-by-section brainstorming, curation, drafting
3. Reader Testing — verify doc works for readers via fresh Claude instance

**Triggers:** "write a doc", "draft a proposal", "create a spec", "write up", "PRD", "design doc", "decision doc", "RFC", "refine requirements", "write requirements"

### refine-plan

**Purpose:** Convert a spec or raw requirements into an actionable implementation plan.

**Input:** Finished spec from doc-coauthoring, or raw requirements directly.

**Output:** Iterative implementation plan with verification test cases.

**Triggers:** "refine the plan", "refine requirements", "iterative plan", "detailed implementation plan"

### retro-plan

**Purpose:** Review implementation results against the plan and improve future planning.

**Modes:** Interim ("retro the plan") or Final ("final retro the plan")

**Output:** Quality assessment, root causes, follow-up deltas, skill/prompt update deltas.

## Marker System

All three skills share a common marker system for tracking gaps:

| Marker | Meaning | Used in |
|--------|---------|---------|
| `[MISSING ...]` | Information needed but not yet provided | doc-coauthoring, refine-plan |
| `[DECISION ...]` | Choice between options needed | doc-coauthoring, refine-plan |
| `[REVIEW ...]` | Content needs verification/review | doc-coauthoring |

**Rules:**
- Markers can be **blocking** (must resolve before ready) or **non-blocking** (explicitly marked)
- User resolves markers with `=>` notation (e.g., `[DECISION REST vs GraphQL] => REST`)
- A document/plan is **ready** when no blocking markers remain

## Iteration System

Both doc-coauthoring and refine-plan use append-only iterations:

- **Iteration 0**: User's initial prompt / core requirements
- **Iteration N**: Each refinement round
- Never overwrite prior iterations

## History Table

Every document and plan maintains a history table at the bottom:

```markdown
| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-03-20 | 0 | User | Initial requirements |
| 2026-03-20 | 1 | Claude | Context gathered, structure proposed |
| 2026-03-21 | 2 | Claude | Resolved [DECISION API layer], drafted core sections |
```

## SessionId

Each document tracks the Claude session ID at the file bottom for conversation continuity.

## File Conventions

| Phase | File Pattern | Example |
|-------|-------------|---------|
| Spec | `<working-dir>/<name>.md` | `auth-spec.md` |
| Plan | `<working-dir>/<name>-plan.md` | `auth-plan.md` |
| Retro | Appended to plan file or separate | `auth-plan.md` (inline) |

## Transitions

### Spec -> Plan
When a spec document is ready (no blocking `[MISSING]`/`[DECISION]` markers, Reader Testing passed), the user says **"refine the plan"** to start deriving an implementation plan with `refine-plan`.

### Plan -> Implementation
When the implementation plan has no blocking markers, it includes verification test cases automatically. The user proceeds with implementation.

### Implementation -> Retro
After implementation (or during), the user says **"retro the plan"** (interim) or **"final retro the plan"** (final) to run a retrospective with `retro-plan`.
