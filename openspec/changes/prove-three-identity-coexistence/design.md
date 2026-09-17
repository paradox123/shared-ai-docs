## Context

Owning Git root: `shared-ai-docs`; initial and user-confirmed delivery branch: `main`; baseline `f6f5d15677dc4cb0a11cdc12f0738b51492f2f18`. The initial tree was clean. The routing gate found no matching active change.

The user subsequently selected `paradox123/probare-crm#3` and one person playing all three roles. The CRM main checkout is clean at `c32e056f3d242008d15f6e0c7b5333c7572ed186`. Its delivery target is a separate clone on `codex/probare-issue-3-issue14-test`. CRM has no OpenSpec directory; its accepted GitHub issue and PRD are the repository's requirements artifacts.

## Goals / Non-Goals

**Goals:** implement and verify issue 3 on the requested test branch; use the real pilot where its contracts support this case; retain public observations and disclose every unsupported gate.

**Non-Goals:** changing production data, real mail, LangGraph operations or provider governance; impersonating additional humans; creating a human approval with an agent; merging the test branch.

## Decisions

- Use a separate clone rather than switching the existing CRM checkout, so the active LangGraph pilot remains independent.
- Use isolated PostgreSQL and adapter state outside both source trees. Tokens come from the existing credential store and remain private runtime inputs.
- Use the public Operator and native session gateway for continuation. No native application database writes or fabricated run-history records.
- Record the same authenticated provider subject for all role actions. Release/reclaim by that subject cannot establish cross-identity takeover.
- Preserve the original acceptance gates: one person's rehearsal and code qualification cannot establish a three-person approval, external definition governance, or replacement approval. Missing gates produce Stop, not a fabricated Go.

## Risks / Trade-offs

- The original Ticket 14 mentions an unchanged CRM repository. The user's later instruction explicitly authorizes only an isolated test branch implementation; main, mailbox data and services remain protected.
- Existing real adapter turns are bounded and prepare a human continuation. Larger implementation work may require several explicit turns in the same session.
- Existing slices have no trustworthy interactive human-approval authority or external agent-definition approval verifier. Record these as unproven; do not add a Boolean or reuse a human token to pretend the gates passed.
- The independently running LangGraph pilot may change its own runtime. Fingerprints show observed drift, not its cause; report drift separately and never stop the service to manufacture a passing snapshot.
