# free-entry-v2-s1 Specification

## Purpose
Accepted S1 specification for the Free Entry v2 vertical architecture spike. It captures the implemented .NET runner, SurveyStub handoff, dummy bundle readiness, isolated harness workspaces, Docker harness, and secret-redaction requirements proven by the archived OpenSpec change `2026-05-05-free-entry-v2-s1-vertical-spike`.
## Requirements
### Requirement: S1 runner MUST create canonical run artifacts in an isolated workspace
The S1 runner MUST write all run artifacts under the explicitly supplied workspace and MUST isolate each harness case in its own subworkspace.

#### Scenario: local fallback success writes canonical artifacts
- **GIVEN** case `001-success-local-fallback.yaml`
- **WHEN** the harness runs the case
- **THEN** the process exits with `0`
- **AND** `survey/answers.json`, `survey/import-manifest.json`, `run-manifest.json` and `agent/agent-config.json` exist under the case run folder
- **AND** `provider_ready=false`, `bundle_readiness_status=ready` and `agent_mode=preflight_only`

### Requirement: S1 runner MUST import SurveyStub handoff answers deterministically
The runner MUST support the S1 SurveyStub handoff contract for `server_rendered` cases and MUST block invalid handoffs before any ROI/RAG follow-up.

#### Scenario: server handoff succeeds
- **GIVEN** case `002-success-server-handoff.yaml`
- **WHEN** SurveyStub returns a valid handoff package
- **THEN** the process exits with `0`
- **AND** `render_mode=server_rendered`
- **AND** `survey_import_status=imported`

#### Scenario: server handoff integrity fails
- **GIVEN** case `005-invalid-survey-handoff-blocks.yaml`
- **WHEN** SurveyStub returns a hash, signature, version or token failure
- **THEN** the process exits with `20`
- **AND** `survey_import_status=blocked_integrity_failed`
- **AND** no ROI/RAG follow-up path starts

### Requirement: S1 runner MUST validate dummy bundle fixtures before workbench success
The runner MUST validate the S1 dummy bundle manifest, signature stub, expected files and hashes before reporting workbench success.

#### Scenario: valid dummy bundle installs workbench stub
- **GIVEN** a valid `valid-free-entry-s1` bundle fixture
- **WHEN** the runner validates and installs the bundle
- **THEN** `bundle_readiness_status=ready`
- **AND** the workbench/vault stub exists

#### Scenario: invalid dummy bundle blocks workbench success
- **GIVEN** case `004-invalid-bundle-blocks.yaml`
- **WHEN** a hash mismatch or missing expected file is detected
- **THEN** the process exits with `30`
- **AND** `bundle_readiness_status` is blocked
- **AND** `workbench_status=blocked`

### Requirement: S1 harness MUST enforce secret redaction locally and in Docker
The harness MUST assert that configured test-secret values do not appear in logs, manifests, summaries or errors.

#### Scenario: secret redaction case passes without leaks
- **GIVEN** case `006-secret-redaction.yaml`
- **WHEN** test secrets are present in environment and fixtures
- **THEN** the process exits with `0`
- **AND** no forbidden secret value appears in generated S1 artifacts
