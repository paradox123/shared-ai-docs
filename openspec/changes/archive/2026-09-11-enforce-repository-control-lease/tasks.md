## 1. Authorization
- [x] 1.1 Replace payload/fixture actor authority with provider-derived identity and effective repository permissions; prove observation, spoof rejection, technical identity rejection and fail-closed behavior through public endpoints.

## 2. Exclusive control
- [x] 2.1 Add durable run-wide claim/release and CLI support; prove concurrent claims across API processes and same-human reconnect/restart.
- [x] 2.2 Enforce all fences and fresh authorization atomically; prove stale/missing requests have no requested effects and return safe current state.
- [x] 2.3 Reconcile observed permission revocation and preserve epoch fencing across regrant; prove read and mutation paths.

## 3. Evidence and completion
- [x] 3.1 Expose typed human/service history and sanitized security audit; verify credentials/redaction through public readback.
- [x] 3.2 Review touched code for DRY/SOLID/KISS, run locked build, regression/black-box tests, OpenSpec strict validation and diff checks; record evidence and resolve Ticket 03.
