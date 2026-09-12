## 1. Control decisions

- [x] 1.1 Prove request/reject durability without granting rights, then implement HTTP/CLI and storage.
- [x] 1.2 Prove holder approval and recipient revalidation, then implement atomic transfer.
- [x] 1.3 Prove explicit forced takeover, fence rejection and twenty-way cross-process contention.

## 2. Old controller fencing

- [x] 2.1 Prove opened-session writes and pending/restarted adapter delivery are fenced while accepted effects survive.
- [x] 2.2 Prove pending live commands are invalidated without changing the running attempt/session/operation.

## 3. Acceptance

- [x] 3.1 Record public HTTP/CLI evidence and update operator documentation and ticket.
- [x] 3.2 Run full isolated suite, build, strict OpenSpec validation and diff check.
- [x] 3.3 Review standards and spec in independent agents; address findings and refactor, then rerun affected checks.
