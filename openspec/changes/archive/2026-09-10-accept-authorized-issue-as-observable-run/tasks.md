## 1. Foundation and behavioral test

- [x] 1.1 Create the isolated .NET solution/project layout, locked dependency configuration, dedicated PostgreSQL test fixture, and synthetic provider/redaction fixture without modifying the managed gate or LangGraph pilot.
- [x] 1.2 Add a black-box public-interface test that initially fails for authorized issue admission, idempotent/conflicting command reuse, separate Operator Client read-back, restart persistence, time/provenance/evidence fields, and canary redaction.

## 2. Canonical admission and read model

- [x] 2.1 Implement transactional PostgreSQL schema/bootstrap and the product-owned `ImplementationRun`, command inbox, canonical ordered event, activity, attempt, projection, provenance, and redaction records.
- [x] 2.2 Implement the capability-bound, fixture-authorized public start command with immutable correlation, identical-command convergence, visible conflicting reuse rejection, and no duplicate effect/event behavior.
- [x] 2.3 Implement public run/event read-back with acknowledged-position filtering, stable ordering, independent time axes, and framework/durability data constrained to supplemental execution evidence.

## 3. Independent observation and lifecycle proof

- [x] 3.1 Implement a separately runnable worker lifecycle reporter that persists ordered API/worker process and heartbeat observations with optional framework/Durable Task correlation without making them canonical history.
- [x] 3.2 Implement the separate HTTP-only Operator CLI and make the black-box test pass across API/worker restart without raw controlled canaries in public or persisted pilot records.

## 4. Verification and completion

- [x] 4.1 Run focused black-box tests, locked restore/build checks, existing managed-gate checks as applicable, `git diff --check`, and strict OpenSpec validation.
- [x] 4.2 Refactor the touched surface for DRY, SOLID, and KISS issues, rerun the relevant checks, and record direct public-surface evidence in the issue/change material.
