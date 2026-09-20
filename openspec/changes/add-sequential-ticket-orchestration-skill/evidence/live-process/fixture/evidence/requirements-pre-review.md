# Requirements verification before structural review

Verifier: `/root/live_completion`. Scope and exact source versions: [candidate-pre-review.json](candidate-pre-review.json). Base: `53f6d11f1a1c9fc1b7fd48b6250ff80aa2f5e26b`. Candidate is uncommitted; both Python files are additions. `REQUIREMENTS.md`, `AGENTS.md`, and `README.md` are unchanged context and included in its identity. Evidence files are excluded from the reviewed identity.

The stable public seam is the documented Python CLI: tests create actual JSON files, execute actual subprocesses, parse actual stdout and compare independently specified literal values. There are no mocked interfaces or providers. The initial two passing tests were insufficient: a counterexample returned no rows for padded/mixed-case `done` values. [02-normalized-filter-red.json](02-normalized-filter-red.json) records two behavioral failures and exit 1 before the repair. [snapshots/red](snapshots/red) preserves that exact reproducible state. The minimal repair normalizes before comparing status, in each existing format path. [03-normalized-filter-green.json](03-normalized-filter-green.json) proves the affected behavior then passed.

| Requirement | Expected versus directly observed | Evidence and limits |
| --- | --- | --- |
| R1 | Original positive IDs 2 and 10 are preserved; padded titles become `Second`/`Tenth`; ` DONE `, `Done`, and ` ToDo ` become lowercase statuses. Observed CLI output matches literals for JSON and CSV. | Tests `test_filter_matches_normalized_status_in_both_formats`, `test_todo_filter_matches_normalized_input_in_both_formats`, and `test_unfiltered_formats_preserve_quoted_multiline_titles_and_numeric_order`. [06-requirements-suite.json](06-requirements-suite.json), exact implementation/test hashes included. Invalid input is explicitly out of scope. |
| R2 | Unfiltered output includes both statuses, with numeric order 2 before 10. The done filter returns only 2 and 10 from an unsorted three-item input; the todo filter returns only 10 from mixed-case statuses. Both serializers select equal values/order. All expected literal results observed. | The preceding three tests exercise no filter, done, todo and nonlexical numeric ordering. Initial red demonstrated that normalized matching is meaningfully checked. |
| R3 | CSV has exactly `id,title,status`; commas, double quotes and embedded CRLF in a title survive parsing. JSON has exactly the three documented fields and the same values. Empty input and a nonmatching filter yield exactly the CSV header or `[]`. All assertions passed. | Roundtrip and empty-result tests in [06-requirements-suite.json](06-requirements-suite.json). Binary subprocess capture prevents test harness newline conversion from hiding CRLF loss. Exact expected strings are in the tests. |
| R4 | Input bytes before/after each public CLI invocation are identical, across both formats and filter paths. Inspected implementation imports only argparse/csv/io/json/pathlib, reads the input once and writes stdout; it performs no network operation or file write. JSON/CSV output contains no additional business fields. | `run_export` checks original bytes after each execution. Same suite is passing. No production service exists in this isolated fixture; inspection plus local process execution establish the bounded no-network/dependency constraint. |

All required fixture coverage is verified. This is an isolated standard-library example, not evidence of production operation. There is no input validation, external-service, performance, permission or deployment requirement to invent. No OpenSpec material exists in this fixture; the explicit local requirement document is unchanged.

## Repository standards ownership

| Rule source | Assigned owner/evidence |
| --- | --- |
| AGENTS: preserve behavior and execute public CLI tests | Requirements verification above; reviewers report any new defect and reopen affected coverage. |
| AGENTS: standard library only; no network/dependencies (also R4) | SOLID inspects dependency/ownership contracts; requirements inspection above. |
| AGENTS: safe-to-import CLI entrypoint | SOLID; [07-safe-import.json](07-safe-import.json) shows actual `python3 -c 'import ticket_export'` exit 0 with empty stdout/stderr. |
| AGENTS: explicit readable names, avoid speculative abstractions | KISS. |
| Shared code-review criteria: repeated domain decisions | DRY. |
| AGENTS: use actual shared change-accepted/code-review skills | Coordinator process evidence and separate sequential receipts, not a code smell. |
| README: local `python3 -m unittest -v`; no delivery | Actual suite above; no delivery authorized or performed. |
| Whitespace/change integrity | Final diff checks, including both untracked source additions explicitly. |

Applicability is substantive: new executable CLI code and behavior tests require the full DRY → SOLID → KISS workflow. Reviewers receive the fixed candidate and their own criteria; no approval or finding is predetermined.
