## 1. Change and Runtime Setup

- [x] 1.1 Strictly validate the active OpenSpec change before implementation.
- [x] 1.2 Create the isolated Python package, locked runtime/test dependencies, and ignored local database pattern.

## 2. Vertical Behavior Slices

- [x] 2.1 Add a failing HTTP behavior test for signed durable acceptance, then implement bounded raw-body authentication, allowlisting, and atomic inbox persistence.
- [x] 2.2 Add a failing behavior test for eligible issue claiming, then implement current-state eligibility, single-run ownership, persistent LangGraph checkpointing, and `agent-running` projection.
- [x] 2.3 Add failing behavior tests for duplicate/conflicting deliveries and all rejection classes, then implement idempotent and effect-free outcomes.
- [x] 2.4 Add a failing restart behavior test, then expose the productive workflow read model backed by persisted run, claim, delivery, and LangGraph checkpoint state.

## 3. Verification and Closeout

- [x] 3.1 Refactor the touched package and specs for DRY, SOLID, and KISS issues while preserving behavior.
- [x] 3.2 Run the complete behavior suite, direct HTTP evidence scenario, dependency audit, `git diff --check`, and strict OpenSpec validation.
- [x] 3.3 Record implementation evidence and update local issue 01 to reflect the directly verified acceptance criteria.
