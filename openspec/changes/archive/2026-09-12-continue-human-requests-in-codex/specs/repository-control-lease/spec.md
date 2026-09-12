## MODIFIED Requirements

### Requirement: All run mutations are fenced atomically
Every claim, release, Human Request decision, Handoff confirmation, and writing interaction in an opened session SHALL check freshly evaluated contribution permission, explicit current target request and attempt, expected run version, explicit expected head SHA, and lease epoch inside the serialized decision. Claim is the bootstrap exception to lease ownership; all other mutations SHALL additionally check human ownership. Rejected requests SHALL produce no requested mutation, workflow effect or canonical business event. An authorized observer SHALL receive the current decision state; unauthorized identities SHALL receive no protected run data. Security audit MAY record a sanitized rejection separately.

#### Scenario: Any fence is stale or missing
- **WHEN** a mutation has a stale request, attempt, version, head or epoch, or omits a required fence
- **THEN** it is rejected without applying the action and a read-authorized caller can retrieve the current decision state

#### Scenario: Stale continuation cannot create a session or write
- **WHEN** a competing human submits Resume, Fork, Fresh Retry, Handoff, or an opened-session write with a stale fence or without the current Control Lease
- **THEN** no adapter operation, session, interaction, canonical business event, head change, or external effect is applied
