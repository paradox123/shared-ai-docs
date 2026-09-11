## 1. External attempt

- [x] 1.1 Prove and implement deterministic preparation, external fake session and redacted ordered transcript through worker/API processes.
- [x] 1.2 Prove worker death and concurrent redelivery adopt one session and reuse committed preparation/observations.

## 2. Diagnostics and operator surface

- [x] 2.1 Prove original blocked result survives downstream rejection and recovery after capture.
- [x] 2.2 Prove distinct failure categories including malformed contracts, schema, transport, timeout and unavailable infrastructure.
- [x] 2.3 Prove authenticated attempt selection in HTTP/CLI with truthful opening capabilities across API restart.

## 3. Completion

- [x] 3.1 Run regression and OpenSpec validation, inspect changes for unnecessary complexity, and document direct evidence and limits in issue/README.
