# Design

The existing Codex agent directly reads selected originals and edits the common Markdown wiki. A small standard-library Python helper records and checks direct original hashes. It does not generate content, call a provider or maintain QMD.

The shared skill owns the explicit page-maintenance flow. QMD and the existing daily QMD-only automation own retrieval and index maintenance. Current guidance lives in docs/rag/llm-wiki.md. The obsolete compiler delivery tree and its scheduler are removed, with historical knowledge preserved outside indexed roots.

Content verification, helper checks and successful indexing are distinct evidence. Check result unchanged proves equal original bytes; successful indexing proves retrieval data maintenance. Neither substitutes for agent content review.
