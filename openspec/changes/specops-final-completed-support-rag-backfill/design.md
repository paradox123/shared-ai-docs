# Design

## Classification Decisions

The final Completed group is intentionally mixed:

| Source group | Entity type | Reason |
|---|---|---|
| DanielsVault RAG phase 01-05 | `type: spec` | These files have accepted spec-style headers and phase scope statements. |
| CheckBuild Skill user guide | `type: document` | This is a guide for an implemented skill, related to the existing CheckBuild spec. |
| Nebenkosten Pipeline history | `type: document` | This is a historical/scratch history file with old blocker markers. |
| Nebenkosten Einzelabrechnung Implementierungsplan | `type: document` | This is an implementation-plan support artifact with old blocker markers and related existing specs. |

## Metadata Quality

1. RAG specs use `metadata_quality: explicit` because the sources include accepted headers and scope lines.
2. The CheckBuild guide uses `metadata_quality: inferred` because status is inferred from its relationship to the implemented CheckBuild spec and skill path.
3. Nebenkosten support documents use `metadata_quality: conflict` because Completed path status conflicts with old blocker/missing markers in the documents.

## Runtime

No runtime service is changed or started. Runtime validation is therefore not applicable for this documentation/entity-only change.

## Duplicate Strategy

Existing entities are detected by exact `source:` path across both `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/specs/` and `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/documents/`.
