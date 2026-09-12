# Implementation evidence

## Delivered behavior

- A blocked or semantically rejected fake attempt persists a redacted, targeted
  Human Request with session, phase, head, evidence, allowed actions and lease
  context.
- Operator API/CLI support `resume`, `fork`, `fresh-retry`, explicit `handoff`,
  selected-session `open`, lease-fenced `write`, and independent receipt lookup.
- Continuation lineage, adapter receipts and pending intents survive API/worker
  replacement; a replacement API adopts a persisted intent without creating a
  second fake-provider session or interaction.

## Direct proof

| Check | Result |
| --- | --- |
| `dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore` | Passed: 0 warnings, 0 errors |
| `python3 -m unittest discover -s tests -q` | Passed: 72 tests |
| `python3 -m py_compile tests/fake_codex_provider.py` | Passed |
| `openspec validate continue-human-requests-in-codex --strict` | Passed |
| `git diff --check` | Passed |
| Two-axis spec/standards review | Passed: no actionable P1/P2 findings |

The black-box suite launches disposable PostgreSQL, the API, Operator CLI,
worker and fake provider as separate processes. Its Ticket 06 scenarios cover
restart-stable request read-back; Resume/Fork/Fresh Retry lineage; truthful
opening and handoff; lease/fence rejection; redacted write-back; schema-start
concurrency; continuation/interaction success-gap adoption; operation-key,
contract-version, write-message and new-session receipt rejection; redacted
command replay; and capability-canary redaction across API replacement.
