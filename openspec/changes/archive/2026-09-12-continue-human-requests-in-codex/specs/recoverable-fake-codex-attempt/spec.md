## MODIFIED Requirements

### Requirement: Operators select attempts and see truthful opening capabilities
An independently authenticated read-authorized Operator Client SHALL select a concrete attempt via HTTP and CLI and read its session status, provenance, original observation, processing outcome, durable Human Request and continuation lineage. History SHALL be independent of Codex App task visibility. The controlled fake adapter SHALL expose truthful per-attempt same-session, handoff-confirmation-required, or unsupported opening capability, with a concrete reason and no misleading production Codex URL. A capability that cannot safely display the original session SHALL provide no implicit fork.

#### Scenario: Second operator inspects failed attempt
- **WHEN** a second read-authorized operator selects the failed attempt after worker replacement and API restart
- **THEN** it reads the same session and immutable original result, separate processing rejection, durable Human Request and truthful Open in Codex capability without worker or database access

#### Scenario: Same-session capability opens the selected attempt only
- **WHEN** an Operator Client opens an attempt whose adapter declares same-session support
- **THEN** public read-back identifies exactly the persisted session as opened while its phase, expected head, external effects and session identity remain unchanged

#### Scenario: Unsupported opening does not silently fork
- **WHEN** an Operator Client opens an attempt whose adapter does not safely support same-session display
- **THEN** it receives the concrete capability limitation and no new session, fork or uncorrelated run is created before an explicit fenced Handoff decision

#### Scenario: Unauthorized attempt selection
- **WHEN** an operator without repository read permission requests an attempt
- **THEN** the request is rejected without exposing attempt or session contents
