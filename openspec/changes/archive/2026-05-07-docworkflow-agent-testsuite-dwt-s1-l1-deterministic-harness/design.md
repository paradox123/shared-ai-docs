# Design

## Boundary

DWT-S1 is deterministic. It may create shell validators, fixture directories and manifest checks, but it must not invoke Promptfoo, Inspect AI, Codex, Docker or runtime delivery.

The accepted `DWT-S0` result is `ADOPT_WITH_LIMITATIONS`. DWT-S1 must record that result as dependency context only. It must not require Codex credentials, Promptfoo execution, isolated npm cache setup or network registry availability, because those limitations belong to later agentic slices.

## Evidence

The runner writes `l1-summary.json` with per-case results, provenance checks, readiness checks, forbidden action observations and S0 dependency context.

Required case families:

- parent-only start contains no child artifacts,
- generated child-control surface has provenance,
- thin child cannot pass readiness,
- high-risk command without rehearsal blocks readiness,
- hidden fixture normalization fails,
- S0 Promptfoo limitations do not become L1 agent/auth/network assumptions.

`DWT-S2`, `DWT-S3` and `DWT-S5` remain dependency-blocked after this change.
