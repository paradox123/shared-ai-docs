## ADDED Requirements

### Requirement: Initial implementation can request policy-authorized intervention
The initial implementation result contract MUST support one schema-valid intervention for contradictory or incomplete product requirements, material scope expansion, missing access to a human-operable surface, or unavoidable manual evidence. The implementer MUST continue autonomously for small reversible implementation and presentation details and MUST NOT synthesize a product decision or continue indefinitely after returning an intervention.

#### Scenario: Initial implementation needs a product decision
- **WHEN** the writing worker cannot choose between materially different product behaviors from the existing assignment
- **THEN** it returns a complete structured intervention and the run pauses before publication or further worker activity

#### Scenario: Initial implementation faces a reversible detail
- **WHEN** only a small reversible implementation or presentation choice is unspecified
- **THEN** the worker chooses within repository guidance and continues without an intervention
