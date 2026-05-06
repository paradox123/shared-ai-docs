# Design

This batch uses the same link-only pattern as the shared-ai-docs canonical OpenSpec audit, but applies it to the complete DanielsVault RAG OpenSpec source pool.

The RAG OpenSpec pool has two historical change groups:

1. `2026-04-22-rag-spec-hardening`, an administrative archive with blocked runtime evidence.
2. `rag-runtime-cli-delivery`, the later accepted runtime delivery that produced the canonical `rag-cli-runtime` spec.

Because the RAG narrative entities already exist, the OpenSpec files are mapped as relationship/evidence rows rather than promoted into new primary entities. Historical blocked evidence stays visible through the row notes and `metadata_quality` summary instead of being treated as current implementation risk.
