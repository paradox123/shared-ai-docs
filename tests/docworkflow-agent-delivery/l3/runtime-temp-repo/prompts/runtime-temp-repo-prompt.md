# DWT-S5 Runtime Temp-Repo Delivery Prompt

Use the parent/master spec, DWT-S5 child spec, Parent Child Index row, DWT-S5
handoff, retained DWT-S3 evidence paths and synthetic fixture manifest as
leading inputs. Apply `spec-change-delivery` only to DWT-S5 and only against the
generated synthetic temp repo.

Required output sections:

- DWT-S5 Delivery Kickoff
- Runtime Gates
- Container Harness
- DWT-S5 Closeout Sync
- Parent Coverage
- concise final status for deterministic parsing

The delivery kickoff must validate the current DWT-S5 handoff, implementation
ready verdict, concrete write-set, retained DWT-S3 predecessor proof and the
synthetic fixture manifest before any edit-like or runtime action.

Runtime gate output must name the generated temp repo as target, record local
runtime and container/harness truth labels, and distinguish blocked auth,
provider, network or runtime prerequisites from pass evidence.

Closeout output must preserve Parent Coverage for `DWT-PR3`, `DWT-PR4` and
`DWT-PR5`, keep retained DWT-S3 evidence separate from DWT-S5 evidence, and
avoid authorizing any descendant child.

End the response with this exact machine-readable line, preserving these keys:

`FINAL_STATUS: child_id=DWT-S5;handoff_current=true;temp_repo_isolated=true;allowed_write_set_concrete=true;local_runtime_status=pass;container_harness_status=pass;descendant_release=false;forbidden_actions=false`

Forbidden:

- describing, copying, building, testing, deploying or editing any original
  runtime repository;
- credential copying or secret values;
- writing outside the generated temp repo or DWT-S5 harness write-set;
- treating fallback artifacts, blocked auth or blocked runtime as accepted L3
  runtime proof.
