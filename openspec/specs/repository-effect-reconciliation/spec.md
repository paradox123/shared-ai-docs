# repository-effect-reconciliation Specification

## Purpose
Ensure managed repository runs start from an authoritative base, reconcile controlled external effects after crashes without duplication, and expose safe Operator recovery and repository ownership release.
## Requirements
### Requirement: Repository execution starts only on the authoritative base
Before a managed repository run starts an agent or missing external work, the worker SHALL persist and compare expected base SHA, actual locally available base SHA and freshly read provider head for the pinned repository. All three SHALL match exactly. A configured predecessor SHALL be provider-confirmed merged and closed. Missing, stale or inconsistent evidence SHALL produce a public preflight blocker without an agent start. Configuration redelivery SHALL NOT silently change repository identity or execution origins.

#### Scenario: Merged predecessor with stale local base
- **WHEN** the predecessor is merged and closed on the provider but the successor's local base is old
- **THEN** the successor exposes expected, provider and local SHAs and a stale-base blocker, creates no session, and starts only after local synchronization and a successful exact-base preflight

#### Scenario: Expected base or provider binding is wrong
- **WHEN** expected SHA or repository binding disagrees with authoritative evidence
- **THEN** execution fails closed and no Git, provider or session effect is created

### Requirement: Every controlled effect has durable identity and reconciliation
Each controlled Git, provider, session, continuation, handoff and opened-session interaction effect SHALL have an immutable intent with a stable operation ID before execution, an independently readable receipt, and a deterministic lookup and adoption rule. A replacement SHALL adopt one matching existing effect and execute only missing work. Committed history, original session observations and established session lineage SHALL remain intact.

#### Scenario: Worker dies in the external success gap
- **WHEN** the worker is killed after a Git, provider, session, continuation, handoff, or interaction effect succeeds but before its local activity result is saved
- **THEN** replacement deliveries adopt that same effect, its externally observed effect count stays one, and the public receipt and operation ID identify it

### Requirement: Uncertain effects become explicit human decisions
Unavailable, ambiguous and incompatible receipts SHALL NOT be treated as absence. Conflicts SHALL expose a concrete operation, reason and sanitized evidence without issuing another effect. Explicit adoption SHALL revalidate the selected receipt against immutable intent and SHALL NOT authorize an incompatible effect.

#### Scenario: Conflicting effect at the intended Git ref
- **WHEN** the run-specific ref points to a different SHA or its operation receipt is missing
- **THEN** the run exposes a human decision, creates no replacement effect, and rejects adoption until the external evidence matches the recorded intent

### Requirement: Recovery is available through fenced Operator commands
Retry, Retire, Reconcile and Adopt SHALL be available through authenticated public HTTP and CLI. Mutations SHALL require fresh contributor permission, the current holder and exact attempt/version/head/epoch fences. Accepted decisions SHALL be durable, observable and safe under repeated delivery. Reconcile SHALL only read external state; Retry SHALL preserve existing effect IDs; Adopt SHALL revalidate a selected receipt. Runtime database edits SHALL NOT be required.

#### Scenario: Operator recovers after API and worker replacement
- **WHEN** a holder submits a current recovery decision and the API and worker restart
- **THEN** the decision remains readable and the replacement processes it with the original operation identities

#### Scenario: Observer or stale holder attempts recovery
- **WHEN** a caller lacks contribution, ownership or a current fence
- **THEN** no recovery action, business event or external effect is applied

### Requirement: Repository ownership survives crashes and is released safely
At most one run SHALL own execution of a registered repository. Worker death SHALL retain durable ownership for recovery. A settled terminal or retired run SHALL clear active projections and release ownership; an unresolved effect SHALL retain ownership until it is reconciled. A worker SHALL NOT resurrect a retired run or bypass ownership using the standalone session path.

#### Scenario: Next run waits and retirement releases the repository
- **WHEN** one run owns the repository and a second is delivered
- **THEN** the second exposes the owning run and performs no effect until the first safely terminates or retires through the Operator surface

#### Scenario: Existing standalone execution predates repository preflight
- **WHEN** a run already has a standalone session or first repository registration races with another standalone delivery
- **THEN** existing sessions cannot acquire fabricated later base provenance, and registration cannot overlap the active standalone delivery

#### Scenario: Provider advances after all effects have succeeded
- **WHEN** the worker dies before finalization and the provider head advances after the recorded effects succeeded
- **THEN** replacement revalidates existing receipts against their historical immutable intent, completes result processing without creating a new effect, and releases ownership
