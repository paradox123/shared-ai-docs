# Auto Resolve Review

## Goal
Convert review findings into immediate, bounded edits and re-review loops until stable.

## Steps
1. Review target artifact and emit findings with file/line evidence.
2. Fix all autonomous findings immediately.
3. Run a strict content-quality review of the whole spec, not only a section/checklist or data-contract review.
4. Re-review touched regions and linked normative sections.
5. Assign an implementation-readiness verdict automatically after spec edits.
6. Repeat until no autonomous findings remain.
7. Escalate only true decision/missing-information blockers.

## Content-quality checks
- Is the described behavior correct for the stated problem and user/context?
- Are the requirements necessary, in scope, and free of hidden scope creep?
- Are normal paths, edge cases, failure paths, dependencies, and constraints complete enough for implementation?
- Are the requirements, examples, terminology, parent/child scope, acceptance criteria, and verification commands mutually consistent?
- Are requirements unambiguous enough that an implementer does not need to choose between materially different meanings?
- Is the requested behavior feasible in the declared technical/runtime environment?
- Is every important requirement testable or otherwise verifiable with concrete evidence?
- Are important requirements traceable to source intent, parent scope, acceptance criteria, verification commands, and downstream artifacts?
- Are requirements atomic enough that partial delivery cannot appear complete?
- Are operational lifecycle concerns covered when relevant: migration, fallback, rollback, observability, compatibility, ownership, and closeout evidence?

## Semantic/domain checks
- Can downstream code interpret every produced artifact without hidden context?
- Do data contracts include stable identity/provenance/version/status fields when the downstream flow needs them?
- Are failure states and blocked paths explicit and testable?
- Could an implementation satisfy the written checks while violating intended behavior?

Domain-specific examples are examples, not universal required fields. Only require a field such as a question identifier when the spec's own flow needs that identity downstream.

## Boundary
Do not escalate for simple wording/consistency/contract-alignment fixes that are safely inferable.
Do escalate when the fix requires a new product, scope, architecture, security, legal, or data-contract decision.
