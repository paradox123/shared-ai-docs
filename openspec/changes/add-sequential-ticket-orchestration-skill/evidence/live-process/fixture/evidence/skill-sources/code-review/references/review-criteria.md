# Structural review criteria

Repository rules override these design heuristics. Treat code smells as hypotheses requiring a concrete benefit, not automatic violations. Inspect adjacent code as well as changed lines; preserve tested behavior and stay within the change's relevant context.

| Pass | Primary question | Typical observations |
| --- | --- | --- |
| DRY | Is knowledge or logic repeated in ways that create inconsistent maintenance? | Duplicated Code; repeated domain decisions or Switches; Data Clumps that repeatedly travel together. Consolidate only when the shared meaning and change reasons agree. |
| SOLID | Are responsibilities, contracts and dependencies coherent and replaceable? | Divergent Change; Shotgun Surgery; Feature Envy; Message Chains; Refused Bequest; interfaces forcing unrelated dependencies; type/contract and substitution violations. Deepen useful boundaries without inventing future requirements. |
| KISS | Is this the smallest clear structure supporting current requirements? | Mysterious Name; Speculative Generality; needless Middle Man; unnecessary branches or abstractions; Primitive Obsession where a small domain type simplifies actual behavior. Do not add a type solely because a primitive exists. |

Before dispatch, map applicable repository standards to the best fitting pass. Examples: duplicated domain constants to DRY; ownership, dependency, interface and error-handling contracts to SOLID; naming, readability and unused abstractions to KISS. Put remaining manually checked code standards explicitly in KISS's packet so they are not silently omitted. Formatting, typechecking and other tooling-enforced rules point to their actual check results. Behavioral/security requirements belong in preceding requirements verification; reviewers still report any concrete defect they discover and reopen that coverage.

Give each reviewer its assigned criteria and standards, not the other reviewers' conclusions as a desired answer. Require separate rule-backed violations and heuristic suggestions, with actionable evidence. A clean result is valid. If a finding concerns another dimension, identify that dimension for the implementing agent to route to its owner instead of launching another broad review.
