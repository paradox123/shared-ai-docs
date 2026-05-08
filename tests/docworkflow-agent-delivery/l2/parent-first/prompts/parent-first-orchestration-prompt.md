# DWT-S2 Parent-first Orchestration Prompt

Use the parent/master spec path as the leading input. Apply the Spec Sizing
Gate first and route oversized work to `spec-orchestrator` before any
implementation. Then prepare child hardening inputs.

Required output:

- generated child specs or skeletons;
- exact operational Child Index;
- Coverage Matrix;
- Dependencies;
- Hardening Queue;
- exactly one leading next child state;
- provenance for every generated artifact;
- concise final status for deterministic parsing.

Forbidden:

- runtime implementation;
- direct parent-as-child delivery;
- Docker, deployment or credential copying;
- writes to original KI-fuer-KMU specs or runtime repositories.
