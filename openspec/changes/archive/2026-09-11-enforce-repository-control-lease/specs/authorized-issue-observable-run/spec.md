## MODIFIED Requirements

### Requirement: An authorized synthetic issue command creates one durable implementation run
The pilot SHALL accept a synthetic issue start command only from a provider-authenticated human with current contributor permission on the pinned repository. The loopback-only pilot API SHALL additionally require its ephemeral fixture-access capability outside the payload and SHALL never persist or return credentials. Payload actor IDs SHALL NOT select the authenticated identity. It SHALL transactionally create exactly one ImplementationRun with immutable repository, issue, command, and run correlation, initial canonical event with typed human identity, admission activity and attempt before returning success.

#### Scenario: Authorized issue is accepted
- **WHEN** a provider-authenticated contributor submits a valid command for a configured synthetic issue
- **THEN** exactly one durable run and its correlated admission history are publicly readable

#### Scenario: Caller lacks permission or capability
- **WHEN** the caller lacks current contribution permission, provider authentication, or the harness capability
- **THEN** admission is denied without creating a run or an effect
