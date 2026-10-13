# Existing request-path usage clarification

Date: 2026-10-13. Fixed base and executable W4 contents unchanged.
Affected files: wiki-review-run README.md and NCG-Automation.md.
Reviewed hashes respectively:
61a65bfb1fbd462e5476e23eee8cf7e20d8fd2a784fde803cae3aed7236f29eb and
ebf6bcc280776507e27ba5808ffd981f2a4ea4c34a1fde9c47d34589ab1aba5b.

The actual live source request was rejected before JSON/Git work because mktemp
returned macOS /var, an alias of /private/var. The same private file through its
canonical path succeeded with the original captured run and unchanged bytes.
The clarification documents the existing Read/NoLinks constraint; it adds no new
API, gate, helper logic, recovery authority or memory write. Actual live result
verification is separate from these structural receipts.

Sequential targeted reviews by the original independent reviewers:

- DRY review_dry: clean. README remains interface owner; the ordered workflow
  places its concise usage guidance in context without conflicting policy.
  Request bytes/current-run preservation covered; executable hashes match W4.
- SOLID review_solid: clean. Both hashes checked against Read/NoLinks. Canonical
  input, unchanged bytes/permissions/run and no recapture/weaker authority checked.
- KISS review_kiss: clean. Both hashes checked; concise guidance matches guard
  execution before JSON/Git and introduces no abstraction. First attempt hit a
  transient model-capacity error; the same reviewer completed the unchanged packet
  on retry. The failed attempt is not attributed as approval.

All unaffected W3 standards/structural coverage is explicitly retained. No test
repeat, edit, live system operation or state mutation by reviewers. Final identity
must incorporate these two documentation hashes plus separately dated live
evidence/closeout metadata; it must not relabel old no-live-run observations.
