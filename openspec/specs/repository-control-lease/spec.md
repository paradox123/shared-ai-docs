# repository-control-lease Specification

## Purpose
Define repository-derived human access, exclusive run-wide control, atomic
mutation fencing, revocation handling, and distinguishable human/service audit
for the isolated work-package pilot.

## Requirements
### Requirement: Repository provider is the sole Operator access authority
The pilot SHALL authenticate each request through a provider credential and derive human observation and contribution from current effective permission on the run's pinned repository. Caller-supplied actor identity SHALL NOT grant access. It SHALL store neither credentials nor a separate membership list. GitHub SHALL be the first adapter behind a provider-neutral contract; bot and installation identities SHALL NOT claim human control. Missing permissions, repository identity mismatch and provider failures SHALL fail closed.

#### Scenario: Reader observes without controlling
- **WHEN** a human has effective repository read permission
- **THEN** run, history and audit are readable but admission, claim and release are denied

#### Scenario: Spoofed actor or technical credential
- **WHEN** a reader supplies a contributor actor ID or a technical identity submits a control request
- **THEN** neither gains human contributor authorization

#### Scenario: Configuration points to a replacement repository
- **WHEN** configuration or the provider changes the numeric repository behind a local repository alias
- **THEN** existing runs retain their original binding and neither observation nor a repeated admission discloses their protected content to users authorized only for the replacement repository

### Requirement: One durable human Control Lease covers the run
The pilot SHALL atomically permit only one contributor to claim the run-wide Control Lease and SHALL bind it to immutable human provider identity. Disconnect, credential rotation for the same identity, and API restart SHALL NOT relinquish it. Release SHALL require the current authorized holder; a competing claim SHALL visibly conflict.

#### Scenario: Concurrent claims across API processes
- **WHEN** two contributors race to claim the same unowned run
- **THEN** one succeeds and one is rejected with current lease state, and exactly one claim event exists

#### Scenario: Same human reconnects elsewhere
- **WHEN** all holder clients stop and that human reconnects through another client and credential after API restart
- **THEN** the same lease and epoch remain visible and usable only by that human

### Requirement: All run mutations are fenced atomically
Every claim and release SHALL check freshly evaluated contribution permission, explicit current target attempt, expected run version, explicit expected head SHA, and lease epoch inside the serialized decision. Release SHALL additionally check human ownership. Rejected requests SHALL produce no requested mutation, workflow effect or canonical business event. An authorized observer SHALL receive the current decision state; unauthorized identities SHALL receive no protected run data. Security audit MAY record a sanitized rejection separately.

#### Scenario: Any fence is stale or missing
- **WHEN** a mutation has a stale attempt, version, head or epoch, or omits a required fence
- **THEN** it is rejected without applying the action and a read-authorized caller can retrieve the current decision state

### Requirement: Provider revocation invalidates control without a second ACL
The pilot SHALL revalidate on every new read connection and before every mutation after acquiring its run lock. Observed loss of contributor permission for the holder SHALL invalidate its lease, advance the epoch and record a distinct security event. Provider unavailability SHALL deny access without transferring control. Regrant SHALL NOT revive the old epoch.

#### Scenario: Holder loses contribution but retains read
- **WHEN** the provider downgrades the holder and that human next connects or mutates
- **THEN** it can only observe, its lease is revoked, and the requested mutation has no effect

#### Scenario: Holder loses all repository access
- **WHEN** the provider removes repository access and the identified holder reconnects
- **THEN** protected content is denied and the observed lease revocation is durable

### Requirement: Human actions and service evidence remain distinguishable
Canonical admission/control events and security audit SHALL identify humans with provider and immutable subject ID. Process and worker evidence SHALL explicitly identify service actors and SHALL NOT imply human authorization. Credentials and uncontrolled provider response bodies SHALL NOT be persisted or returned.

#### Scenario: Observer inspects control and worker evidence
- **WHEN** an observer reads a run containing human control and worker observations
- **THEN** the human provider identity and service actor are distinguishable and provider credentials do not occur in output
