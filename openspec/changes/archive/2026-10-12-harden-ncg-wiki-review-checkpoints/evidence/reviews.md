# Attributable verification and review extracts

These compact extracts were prepared by the closeout owner after reading the original protected receipts. They are separate generated evidence, not new tests or substituted reviewer approvals. Private raw receipts, logs, probe entrypoints, manifest versions and red/green counterexamples are retained outside Git.

All final receipts cover fixed base `fc70c24fd7282516556040412bd098911c95f0df` and accepted V4 tree `bdadf6876c91b44a1d800bb4012854986656351a`, eleven paths identified in `content-manifest.json`. Sequence: critical requirements verification, independent DRY, independent SOLID, independent KISS. Bounded repairs reopened only affected coverage with the original reviewer.

- **Requirements**, `/root/acceptance_requirements`: V4 PASS after reading exact spec/tasks and recomputing all eleven hashes. V2 functional observations and V3 S1 proof remain attributed to their executions; V4 changes only accepted specification scope/task metadata. Expected/observed behaviors and limits are in `../completion.md`.
- **DRY**, `/root/closeout_dry`: V4 clean, no actionable finding. The original V2 pass covers cutoff authority, resolver/extractor ownership, shared extraction/clone/topic context and stable replay. V3 inspected the S1 RealPath delta; V4 directly reconciled restored spec scope and retained that source coverage.
- **SOLID**, `/root/closeout_solid`: V4 clean, original S1 [P2] resolved. Existing components now canonicalize to actual entry names before store exclusion, retaining ordinal containment. The actual V3 focused probe rejects the case alias before store or resolver effects. Original V2 CLI/error/snapshot/ownership/local-only boundary coverage remains retained. Distinct case-sensitive runtime branch remains source-inspected only.
- **KISS**, `/root/closeout_kiss`: fresh V4 PASS, all eleven hashes independently match. Actual C# file-based vertical slices, existing Python seam, CLI structure, truthful README/reference/contracts, generic public examples, privacy/scope discipline and audit boundary checked. No binding violation or material blocker. Optional future housekeeping: fallback usage at ReviewRun.cs:10 omits the already documented and implemented `resolve-clone`; no behavior repair required for this accepted candidate.

Reviewed lineage: V1 `ee862e4f603f8dbfb2eb341c369c492a9baec321` exposed R1; V2 `b3f74e38362827a8bc53de19ce5cd67e3e65b1ee` repaired R1 and exposed S1 in SOLID; V3 `bbc5322953f10f24cb629d50dd98fd99758c1126` repaired S1 but accidentally included concurrent future spec material; V4 restores only accepted scope while keeping V3 executable contents. No future work is approved by these receipts.

## Original protected receipt hashes

- `requirements-verification.v4.md`: SHA256 `510dfca4c609d89a78bc2187a4ec675d61459eaf0db683d890da2329a1278d77`.
- `review-dry.v4.md`: SHA256 `aec20919d9cec620384ff6c64cfef93b4d18e035b9bf58a32f4526caa2918702`.
- `review-solid.v4.md`: SHA256 `8f11cb60813bcdd632f234049897652b83128b1329395af4735198ae55b35c7d`.
- `review-kiss.v4.md`: SHA256 `71f50da2f2432dc830cb33af6defcd4ac4b4b7309586b3afacd3effb1b945d4e`.
