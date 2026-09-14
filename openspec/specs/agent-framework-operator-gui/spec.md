# agent-framework-operator-gui Specification

## Purpose
Accept GitHub requirements through the Operator GUI, retain their redacted immutable source snapshot under current human repository authorization, and recover them after restart without starting agent execution. Later workflow capabilities remain in the active GUI change.

## Requirements
### Requirement: GitHub submission intake precedes execution
The first intake slice SHALL accept an actual GitHub issue URL without a pre-existing run, synthetic issue catalogue or client-supplied execution plan. The server SHALL resolve the issue through GitHub, validate its configured immutable repository binding, the submitting human's current contributor access and the issue's `ready-for-agent` implementation authorization. It SHALL persist a redacted snapshot of title and body, provider issue identity, source URL and revision, repository binding, submitting human and admission time. A submission SHALL be visibly `admitted` with no ImplementationRun until the separately delivered execution slice starts one.

#### Scenario: Admit and rediscover a GitHub issue
- **WHEN** an authorized human submits an open ready-for-agent GitHub issue into an empty application database through the GUI
- **THEN** public detail and overview reads expose the provider's admitted title/body, provenance, repository and stable submission identity after service and browser restart, without starting agent processing

#### Scenario: Redelivery preserves the first snapshot
- **WHEN** the same logical issue is submitted again or concurrently, including after its source content changes
- **THEN** admission returns the original submission identity and snapshot without a duplicate or silent replacement

#### Scenario: Authorization and source errors are actionable
- **WHEN** a source is invalid, missing, a pull request, closed or lacks implementation authorization, or the human lacks current repository contribution access or the immutable repository identity mismatches
- **THEN** admission fails with a specific reason and no submitted content is persisted; public reads expose only submissions in repositories the authenticated human can currently read

#### Scenario: Browser reads a server-hosted submission
- **WHEN** an authenticated human accesses the GUI from a separate client over the server's public HTTP interface
- **THEN** submission and readback require no fixture capability, server-local filesystem or database access, and source content is redacted before persistence and rendered as untrusted text
