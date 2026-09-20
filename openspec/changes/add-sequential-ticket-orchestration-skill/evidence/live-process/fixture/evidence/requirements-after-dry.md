# Requirements evidence after DRY repair

Verifier `/root/live_completion`; exact current contents and source versions in [candidate-after-dry.json](candidate-after-dry.json). This supplements [requirements-pre-review.md](requirements-pre-review.md) without replacing its historical observations.

Accepted DRY-001: the two serializers duplicated the same normalization, selection, projection and sorting policy. [dry-repair.delta.diff](dry-repair.delta.diff) records the only production change: `prepare_rows` now computes each normalized status once, selects and projects the rows, then sorts them. `main` computes those rows once before choosing CSV serialization or `json.dumps`. The internal `export_json` wrapper is removed; only the documented CLI is a public contract. All tests, README, requirements and local standards remain byte-identical.

Affected coverage was reopened before the same DRY reviewer was asked to inspect the delta:

| Coverage | Current observed result |
| --- | --- |
| R1 normalization, title trimming and original IDs | Known literal outputs still match for both formats, mixed-case/padded statuses and IDs 2/10. |
| R2 shared selection and numeric ordering | Both done/todo filters and unfiltered output return the expected literal values and numeric order. |
| R3 serializer contracts | Exact header/three fields, comma/quote/CRLF title roundtrip and both empty-result paths still pass. Serializers retain standard-library handling. |
| R4 input integrity/no external dependencies | All CLI calls still assert unchanged input bytes. The inspected delta adds no dependency, network or write path. |
| Safe-import standard | A fresh actual `python3 -c 'import ticket_export'` exits 0, stdout/stderr empty. |

[10-after-dry-repair-tests.json](10-after-dry-repair-tests.json) records the six real CLI tests against the new source hash, all passing (exit 0). [11-after-dry-safe-import.json](11-after-dry-safe-import.json) records the import result. The same expected/observed details and explicit limits in the preceding requirement map remain applicable; the assertions and source requirements are unchanged. No required coverage is unverified. The DRY delta receipt is still required before the next reviewer can start.
