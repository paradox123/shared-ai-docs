# DWT-S2 Oversized Parent Fixture

This synthetic parent fixture intentionally contains only parent-level scope.
It has requirements for parent-first orchestration, child hardening, evidence
integrity and reporting, but it does not contain a child index, generated child
specs, handoffs, dependencies or a hardening queue.

## Parent Requirements

| Requirement | Summary |
|---|---|
| `DWT-PR1` | Split oversized work through child orchestration before implementation. |
| `DWT-PR2` | Block thin child skeletons from implementation readiness. |
| `DWT-PR5` | Preserve provenance and evidence truth. |
| `DWT-PR7` | Emit style and efficiency telemetry for downstream handoff. |
