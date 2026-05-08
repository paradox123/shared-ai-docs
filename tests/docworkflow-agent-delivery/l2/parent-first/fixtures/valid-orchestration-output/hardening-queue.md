| Child | Next State | leading_next | Required Hardening | Dependencies | Next Action |
|---|---|---:|---|---|---|
| DWT-C1 | `ready_for_hardening` | true | Add full contract, write-set, verification and handoff sync. | Parent fixture | `child-spec-hardening` |
| DWT-C2 | `needs_hardening` | false | Wait for DWT-C1 contract output. | DWT-C1 | `child-spec-hardening` after DWT-C1 |
