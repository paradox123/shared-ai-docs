## ADDED Requirements

### Requirement: External visible-session controller MVP

The Agent Delivery testsuite SHALL provide an external visible-session controller that launches one parent and one child Codex App session from outside app-server-backed parent turns, using controller-owned invocations of `AgentDeliverySessionLauncher.cs`.

#### Scenario: Controller launches parent and child externally

- **GIVEN** a controller run directory with a parent handoff and child handoff
- **WHEN** the controller runs in live mode with `--run-dir`, `--parent-handoff`, `--parent-target-id`, and `--initiating-project-cwd`
- **THEN** it SHALL launch the parent through `AgentDeliverySessionLauncher.cs --adapter codex-app-server`
- **AND** it SHALL wait for exactly one parent-published child request
- **AND** it SHALL launch the child through `AgentDeliverySessionLauncher.cs --adapter codex-app-server` from the controller process
- **AND** it SHALL write `controller/controller-summary.json` and `controller/responses/<request-id>.response.json`.

#### Scenario: Controller validates request safety before launch

- **GIVEN** a discovered child request
- **WHEN** the request has malformed JSON, mismatched ids, wrong adapter/mode/agent, mismatched initiating cwd, or paths escaping the configured run directory
- **THEN** the controller SHALL write response status `rejected`
- **AND** summary status SHALL be `setup_error`
- **AND** no child launcher command SHALL be executed.

#### Scenario: Controller preserves blocked and failed evidence

- **GIVEN** a child launcher result with retained `evidence.json`
- **WHEN** the child evidence status is `blocked`, `failed`, missing, incompatible, or the expected output assertion fails
- **THEN** the controller SHALL write deterministic response and summary statuses
- **AND** retained evidence paths SHALL be present when the launcher produced them
- **AND** blocked app-server initialize evidence SHALL NOT be converted into success.

#### Scenario: Fixture mode validates the state machine without live processes

- **GIVEN** a fixture directory containing positive, malformed-request, unsafe-path, missing-request, blocked-child, and missing-output cases
- **WHEN** the controller runs with `--fixture <dir>`
- **THEN** it SHALL validate the same request, result, output assertion, response, and summary semantics used by live mode
- **AND** it SHALL NOT start `codex`, `codex app-server`, or `AgentDeliverySessionLauncher.cs`.
