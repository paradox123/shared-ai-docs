## ADDED Requirements

### Requirement: Repair interruptions remain in the same bounded round
A policy-authorized repair interruption MUST persist an answerable intervention instead of immediately completing the repair batch as a terminal handoff. Answer continuation MUST reuse the same repair batch, numbered round, attempt, writer, worktree, and open findings and MUST NOT allocate another automatic round merely because a human answered. Exhaustion after three unsuccessful automatic rounds remains an intervention boundary and MUST NOT start a fourth round.

#### Scenario: Repair needs a product decision inside round one
- **WHEN** the writing worker returns a valid product-decision intervention during repair round one
- **THEN** the attempt waits with its findings and invocation identity preserved and resumes inside round one after the correlated answer

#### Scenario: Three automatic rounds are exhausted
- **WHEN** the third repaired head remains unsuccessful
- **THEN** one exhaustion intervention is created with all attempts and findings and no fourth repair assignment starts before or after an answer
