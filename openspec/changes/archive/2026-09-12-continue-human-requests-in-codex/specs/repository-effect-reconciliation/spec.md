## MODIFIED Requirements

### Requirement: Every controlled effect has durable identity and reconciliation
Each controlled Git, provider, session, continuation, handoff and opened-session interaction effect SHALL have an immutable intent with a stable operation ID before execution, an independently readable receipt, and a deterministic lookup and adoption rule. A replacement SHALL adopt one matching existing effect and execute only missing work. Committed history, original session observations and established session lineage SHALL remain intact.

#### Scenario: Worker dies in the external success gap
- **WHEN** the worker is killed after a Git, provider, session, continuation, handoff, or interaction effect succeeds but before its local activity result is saved
- **THEN** replacement deliveries adopt that same effect, its externally observed effect count stays one, and the public receipt and operation ID identify it
