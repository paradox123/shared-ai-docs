# portable-run-dossier Specification

## Purpose
Preserve authorized access to complete run evidence across disconnects and process
failure through acknowledged history cursors, redacted immutable artifacts, and
portable export with independent read-only restore.

## Requirements

### Requirement: Acknowledged history reconnect is complete and ordered
The pilot SHALL expose bounded canonical-history pages and a live SSE tail with
stable event IDs and positions. Each page SHALL distinguish its delivered cursor
from the committed high-water mark. Reconnecting strictly after the last processed
position SHALL yield every later authorized event once in stable order across
client, API and worker restart, including failed or canceled runs. Every new page
and live polling cycle SHALL revalidate repository read access.

#### Scenario: Large failed run survives disconnect and restart
- **WHEN** a client acknowledges position N, disconnects, API and worker restart,
  and a run emits more than 10,000 events and large output before failure
- **THEN** a second client reads all positions N+1 through the final event without
  gaps, duplicates or reordering through cursor pages and SSE

#### Scenario: Read access is revoked during observation
- **WHEN** the provider revokes an observer's repository permission
- **THEN** subsequent pages are denied and the live tail stops before further delivery

### Requirement: Artifacts preserve safe immutable evidence outside workflow state
The pilot SHALL persist artifact bytes outside workflow core state, referenced by
SHA-256 over the published bytes. Large original observations SHALL remain retrievable
without embedding their content in workflow projections. Every read SHALL verify
integrity; withheld, missing and corrupt artifacts SHALL have explicit policy-versioned
availability metadata and SHALL block the artifact prerequisite for qualification.

#### Scenario: Large text and binary artifacts are captured
- **WHEN** an adapter supplies large JSON/text observations or binary artifacts
- **THEN** immutable verified artifacts are publicly retrievable by authorized readers
  and workflow state carries only references to large content

#### Scenario: Artifact is removed or corrupted
- **WHEN** a referenced artifact is absent or its bytes do not match the manifest
- **THEN** artifact reads and the qualification prerequisite report the concrete failure
  and neither export nor restore hides the missing evidence

### Requirement: Redaction precedes every durable and public surface
The pilot SHALL remove configured secret, token, authorization, credential, email
and personal-name canaries before persistence, artifacts, logs, export and clients.
Encoded artifact bytes SHALL be inspected after decoding. Redaction or withholding
SHALL remain visible with its policy version, including failures and raw adapter
observations. Recovery SHALL reuse sanitized observations without leaking original input.

#### Scenario: Sensitive controlled input crosses a crash boundary
- **WHEN** canaries occur in command, output, exception, JSONL or artifact input and
  the worker dies after receipt before commit
- **THEN** recovery and all public reads contain only safe evidence, and bounded scans
  of pilot database, artifacts, logs and export contain zero raw controlled canaries

### Requirement: Portable run dossiers restore public evidence independently
The pilot SHALL export a versioned portable dossier containing canonical domain
history, projections, artifact manifest and bytes, runtime/adapter provenance and
framework correlations with public checksums. Explicit local restore into fresh
components SHALL reproduce those public history, projection and artifact checksums
without a proprietary dashboard or running framework. Historical restore SHALL
require current repository authorization for reads, be read-only, reject corrupt
core data and never overwrite a live run or execute restored workflow effects.

#### Scenario: Failed run is exported and restored
- **WHEN** an authorized reader exports a failed run and restores it into fresh
  local PostgreSQL, artifact storage and API components
- **THEN** public history, projection and available artifact checksums match the source
  and unavailable evidence remains visible and ineligible for qualification

#### Scenario: Dossier core data is corrupted or conflicts
- **WHEN** restore receives invalid history/projection checksums or an existing run ID
- **THEN** it rejects the dossier without replacing existing history or running work
