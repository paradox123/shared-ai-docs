# DWT-S3 Single-Child Delivery Closeout Prompt

Use the parent/master spec, DWT-S3 child spec, Parent Child Index row, DWT-S3
handoff and retained DWT-S2 evidence paths as leading inputs. Apply
`spec-change-delivery` only to DWT-S3, and use `spec-closeout` only for a
DWT-S3 closeout sync proposal.

Required output sections:

- DWT-S3 Delivery Kickoff
- DWT-S3 Closeout Sync
- Parent Coverage
- DWT-S5 State
- concise final status for deterministic parsing

The delivery kickoff must validate the current DWT-S3 handoff, implementation
ready verdict, concrete write-set, retained DWT-S2 predecessor proof and an
isolated temp workspace before any edit-like action. All edit-like output must
target an isolated temp workspace or artifact bundle, never the source
repository.

Closeout output must preserve Parent Coverage for `DWT-PR3`, `DWT-PR4`,
`DWT-PR5` and `DWT-PR7`, keep retained DWT-S2 evidence separate from DWT-S3
evidence, and keep DWT-S5 blocked unless a later DWT-S5 child spec, handoff and
readiness validator independently authorize it.

End the response with this exact machine-readable line, preserving these keys:

`FINAL_STATUS: child_id=DWT-S3;handoff_current=true;target_workspace_isolated=true;allowed_write_set_concrete=true;dwt_s5_state=blocked_by_dependency;dwt_s5_delivery_started=false;forbidden_actions=false`

Forbidden:

- DWT-S5 implementation or runtime delivery;
- Docker, deployment or credential copying;
- writes to original KI-fuer-KMU specs or runtime repositories;
- treating fallback artifacts as accepted agent proof.
