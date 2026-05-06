# free-entry-v2-s2 Specification

## Purpose
Define the accepted S2 Survey Delivery and Answer Handoff contract for Free Entry v2: server-rendered survey sessions, local fallback, canonical answer artifacts with question references, short-lived handoff, import validation, retention status and local/Docker harness verification.
## Requirements
### Requirement: S2 capability MUST define a production-like survey handoff contract

S2 MUST provide the production-like Survey Delivery and Answer Handoff contract for Free Entry v2: server-rendered survey sessions, local fallback, canonical answer artifacts, short-lived handoff, import validation, retention status and Docker-backed verification.

#### Scenario: S2 contract is represented by executable harness artifacts
- **GIVEN** the S2 OpenSpec change
- **WHEN** implementation and verification run
- **THEN** the change provides runnable local and Docker harness evidence for the survey handoff contract

### Requirement: S2 Survey Delivery Service MUST support answer submission before handoff export

The service MUST expose session start, survey definition lookup, server-rendered HTML, answer submission, session completion, handoff answer export and import confirmation.

#### Scenario: server-rendered handoff succeeds after answer submission and completion
- **GIVEN** a `server_rendered` S2 harness case with a pinned survey definition and structured answers
- **WHEN** the harness starts a session, submits answers, completes the session and imports the handoff package
- **THEN** the process exits with `0`
- **AND** `survey_import_status=imported`
- **AND** the summary proves `survey_service_started`, `survey_definition_loaded`, `survey_answers_submitted`, `survey_session_completed`, `handoff_validated` and `answer_question_refs_validated`

### Requirement: S2 answer artifacts MUST bind answers to survey questions

`survey/answers.json` MUST contain structured answer objects with stable question references and MUST include `survey_definition_id` and `survey_definition_sha256`.

#### Scenario: question-answer link is preserved
- **GIVEN** S2 answer fixtures with known `question_id` values
- **WHEN** online or local fallback import succeeds
- **THEN** every answer contains `question_id`, `question_revision`, `question_path`, `question_prompt_snapshot`, `answer_type`, `answer_value`, `answered_at_utc` and `required`
- **AND** the import manifest sets `answer_question_refs_validated=true`

#### Scenario: unknown question blocks import
- **GIVEN** an answer that references a question not present in the active survey definition
- **WHEN** the runner validates the answer package
- **THEN** the process exits with `20`
- **AND** `survey_import_status=blocked_unknown_question`
- **AND** no ROI/RAG follow-up starts

#### Scenario: answer type mismatch blocks import
- **GIVEN** an answer whose `answer_type` does not match the active question definition
- **WHEN** the runner validates the answer package
- **THEN** the process exits with `20`
- **AND** `survey_import_status=blocked_answer_schema_invalid`

### Requirement: S2 integrity checks MUST use canonical hashes and payload binding

The runner MUST validate canonical `answers_sha256`, canonical `survey_definition_sha256` and a deterministic S2 fixture integrity proof before accepting a handoff.

#### Scenario: canonical hash mismatch blocks import
- **GIVEN** a handoff package with mismatched answer or definition hash
- **WHEN** the runner imports the package
- **THEN** the process exits with `20`
- **AND** `survey_import_status=blocked_integrity_failed`

### Requirement: S2 local fallback MUST produce equivalent canonical artifacts

Local fallback MUST use the same active survey definition and write canonical local artifacts without writing any handoff token.

#### Scenario: local fallback imports with synthetic local identifiers
- **GIVEN** a `local_fallback` S2 harness case
- **WHEN** the runner imports local answers
- **THEN** the process exits with `0`
- **AND** `survey_import_status=local_fallback_imported`
- **AND** `survey_session_id` starts with `local-session-`
- **AND** `handoff_id` starts with `local-handoff-`
- **AND** `server_delete_status=not_applicable_local_fallback`

### Requirement: S2 harness MUST enforce token and secret redaction

Handoff tokens and configured test-secret values MUST NOT appear in generated logs, manifests, answer artifacts or harness summaries.

#### Scenario: token redaction case passes without leaks
- **GIVEN** S2 token and secret test values in the environment and forbidden value list
- **WHEN** local and Docker harnesses run S2 cases
- **THEN** no forbidden token or secret appears in generated artifacts or summaries
