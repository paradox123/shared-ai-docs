# Pre-implementation Evidence Matrix

| Issue 03 criterion | Public observation surface | Expected result | Planned direct proof |
| --- | --- | --- | --- |
| Active OpenSpec change | OpenSpec CLI | Goal, scope, write-set, and verification are apply-ready and strictly valid before runtime edits | `openspec status`, apply instructions, and `openspec validate create-evidence-backed-draft-pr --strict` |
| Commit, push, one draft PR | Signed webhook plus workflow-state GET; controlled Git/GitHub boundaries | One safe head is pushed and exactly one draft PR is returned for the claimed issue | HTTP behavior test observes publication read-back and boundary effects; adapter contracts prove real command/API construction |
| Full criterion matrix | Draft PR body returned by workflow-state GET | Every issue criterion has verdict, interface, expected result, concrete proof, and the same head SHA | Body assertions over the productive HTTP response |
| REST, UI, recovery, idempotency evidence | Evidence qualifier and rendered body | Each kind requires its direct typed observations and embeds decisive excerpts | Parameterized behavior test submits known-good packages and reads the rendered evidence back |
| Negative gate | Evidence qualifier | Rejection plus absent forbidden business side effect are both present | Insufficient-package HTTP case omits side-effect read-back and observes durable rejection/no publication |
| Background work | Evidence qualifier | Eventually observable business result is present; enqueue/start/log alone fails | Insufficient-package HTTP case offers enqueue/log only and observes durable rejection/no publication |
| Infrastructure surrogate rejection | Signed webhook plus workflow-state GET | Health/build/start/2xx/log/static-initial evidence alone cannot publish | Parameterized insufficient packages produce `rejected` and zero source/PR effects |
| Embedded decisive evidence | Draft PR body returned by workflow-state GET | REST excerpts, screenshot references, and correlated logs appear beside their criteria | Body assertions through workflow-state read-back |
| Head binding and redaction | Pushed-head result plus workflow-state GET and controlled diff scan | Body/evidence use adapter-derived head; sensitive evidence is redacted and sensitive branch content blocks publication | Sufficient HTTP test compares returned head throughout; qualifier and Git adapter contracts exercise redaction/fail-closed behavior |
| Primary-seam behavior coverage | Signed webhook POST and workflow-state GET with real SQLite/LangGraph | Sufficient evidence publishes; deliberately insufficient evidence does not | Focused behavior tests use only HTTP read-back and controlled external boundaries |
