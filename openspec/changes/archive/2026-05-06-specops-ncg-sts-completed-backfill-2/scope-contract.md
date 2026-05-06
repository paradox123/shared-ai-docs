# Scope Contract

## In Scope

1. Import the second bounded NCG STS Completed subset from `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/Completed/`.
2. Use the coherent late STS slice group:
   - `10 STS Backend Store Integration Rehearsal Gate`
   - `12 STS Vanity Domain Cutover to securitydev.auto-nagel-cloud.de`
   - `13 STS Certificate Runtime Startup Gate for Vanity Cutover`
   - `14 STS Vanity Cutover via pfSense TLS Termination and Gate Delta`
   - `15 STS Admin Plane VPN Reachability and Login Flow`
   - `16 STS Legacy Screen Design Parity for Account Flows`
   - `17 Frontend Handover Authorization Code Migration and React Reference Client`
3. Create one primary SpecOps `type: spec` entity note per selected source.
4. Update inventory, Control Spec and backlog counts for NCG docs Specs from 7/29 to 14/29.

## Out Of Scope

1. No edits to NCG source specs.
2. No runtime implementation or validation inside `ncg-backend` or `ncg-security-token`.
3. No import of active NCG root specs in this run.
4. No import of older non-STS NCG infrastructure specs in this run.
5. No OpenSpec relationship audit.

## Acceptance Targets

1. Exactly 7 new entity notes exist for batch `historical-001-ncg-sts-2`.
2. All 7 selected source paths are represented exactly once.
3. NCG docs Specs represented-source count increases from 7/29 to 14/29.
4. No duplicate NCG docs Specs source paths exist across SpecOps spec/document entities.
5. No `source_type: openspec_change_artifact` primary entity is created.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Count all NCG docs Specs source files.
2. Count NCG docs Specs sources represented in SpecOps entities.
3. Count batch `historical-001-ncg-sts-2`.
4. Run selected-source missing guard.
5. Run duplicate NCG docs Specs source guard.
6. Run negative OpenSpec artifact guard.
7. Run `openspec validate specops-ncg-sts-completed-backfill-2 --strict --json`.
8. Run `openspec status --change specops-ncg-sts-completed-backfill-2 --json`.
9. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. The active parent STS onboarding spec is referenced by `parent_source` because it is not imported in this run.
2. Runtime validation is not applicable because this change only creates SpecOps metadata/entity notes.
3. The selected Completed sources are treated as accepted because each source has an Accepted status header and no formal missing/decision/blocked markers.
