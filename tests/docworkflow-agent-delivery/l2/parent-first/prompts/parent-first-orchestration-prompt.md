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

End the response with this exact machine-readable line, preserving these keys:

`FINAL_STATUS: child_index_generated=true;coverage_matrix_generated=true;dependencies_generated=true;hardening_queue_generated=true;implementation_allowed=false;writes_performed=false`

Forbidden:

- runtime implementation;
- direct parent-as-child delivery;
- Docker, deployment or credential copying;
- writes to original KI-fuer-KMU specs or runtime repositories.
