## ADDED Requirements

### Requirement: Independent reviews can request intervention without losing isolation
Each requirements, code-quality, or architecture review result contract MUST support one schema-valid intervention when its existing read-only mandate encounters a policy-authorized human decision or action. The affected review MUST preserve its axis, immutable head, findings, policy, and fresh invocation identity; it MUST NOT receive peer verdicts, write source, synthesize the answer, or let an influenced or stale review qualify a later head.

#### Scenario: One review axis needs a product decision
- **WHEN** a fresh head-bound reviewer finds contradictory acceptance behavior that cannot be classified as pass or actionable implementation failure without human input
- **THEN** that axis persists an intervention and the review batch pauses with its completed peer results retained and no verification projection

#### Scenario: Review resumes after an answer without a head change
- **WHEN** the same immutable head remains current after the answer
- **THEN** the affected axis receives only the bounded answer context and the batch can aggregate only after every required independent result is valid for that head
