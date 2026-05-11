# Acceptance Criteria Matrix

| ID | Acceptance Target | Evidence |
|---|---|---|
| AC1 | Controller help command exits `0`. | Pass: help command ran successfully. |
| AC2 | Fixture suite exits `0` and covers positive, malformed, unsafe-path, timeout, blocked, and output-missing cases. | Pass: fixture command reports 6 passing controller fixture cases. |
| AC3 | Live minimal parent-child controller run exits `0`. | Pass: `20260511T120609Z-external-controller-mvp` controller command exited `0`. |
| AC4 | Live parent evidence is visible app-server evidence. | Pass: parent evidence status `launched`, visibility `visible_codex_app_session`. |
| AC5 | Live child evidence is visible app-server evidence launched by the controller, not by the parent session. | Pass: child response status `launched`; parent transcript commandExecution scan found zero child launcher/app-server commands. |
| AC6 | Child output equals `controller child reached\n`. | Pass: response `output_assertion.status` is `pass`. |
| AC7 | Response and summary artifacts preserve useful evidence paths for blocked/failed launches. | Pass: response includes launcher run dir, evidence, transcript, and stderr paths. |
| AC8 | Parent transcript does not contain a nested child `codex app-server --listen stdio://` launch. | Pass: commandExecution scan found `forbiddenCommandCount: 0`. |
| AC9 | Rejected requests write deterministic response and summary artifacts while launching no child process. | Pass: malformed and unsafe fixture cases return response `rejected`, summary `setup_error`, exit `2`. |
| AC10 | `git diff --check` passes. | Pass: final whitespace check exited `0`. |
