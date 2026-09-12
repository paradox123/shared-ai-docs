## 1. Targeted admission and observation

- [x] 1.1 Prove parallel live attempts and authorized explicit command targeting through HTTP/CLI.
- [x] 1.2 Persist and expose FIFO acceptance order, redaction and idempotent command read-back.

## 2. Process control and recovery

- [x] 2.1 Deliver queued commands serially after active operation completion with correlated replies.
- [x] 2.2 Fence, stop and reconcile an interrupt before delivering it next.
- [x] 2.3 Implement reasoned operation/attempt cancellation and explicit rejection without retry or repair.
- [x] 2.4 Prove crash recovery, concurrent redelivery and history-only late output across fence epochs.

## 3. Acceptance

- [x] 3.1 Review touched code for DRY/SOLID/KISS and run relevant regression and strict OpenSpec checks.
- [x] 3.2 Document commands, requirement-by-requirement observed evidence and pilot limitations; update Ticket 07.
