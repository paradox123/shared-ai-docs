# Critical requirements verification

Use after a completion request, or to establish missing evidence for an explicit standalone code-review request. This is also the owner of the former Spec comparison; do not append another blanket Spec review later.

Pin the current candidate and requirement sources. Compare each requirement with both the implementation and the most direct observable surface: public interface behavior, measured output, running UI, generated artifact or workflow invocation. Look for missing/partial behavior, incorrect implementation, unrequested scope and evidence that proves only startup or green test counts. Inspect substantive constraints that cannot be established by a screenshot through suitable tests and code inspection.

Challenge happy-path evidence with relevant counterexamples, failure paths and boundaries. Select these from actual requirements and risks, not a universal exhaustive checklist. Use representative fixtures early; disclose what mocks or synthetic providers cannot prove. Do not run remote mutations or production tests without the applicable authority.

Record expected versus observed results, evidence paths, exact candidate and verification limits per requirement using the completion record linked by code-review. If a requirement is absent or fails, repair within the authorized scope, run affected tests and refresh affected evidence before structural review starts. Do not invent missing product decisions or silently treat unverified behavior as passed. When direct verification is unavailable, explain why and what lower-level evidence exists; unresolved required coverage prevents technical completion.

The implementing agent may perform this separately requested critical verification; independence is a property of the structural reviewers, not an additional late phase named "independent review". A caller may explicitly assign an independent requirements verifier. Reviewers can discover behavioral defects later: reopen only affected requirements and review coverage, then refresh final checks. Preserve unchanged valid evidence.
