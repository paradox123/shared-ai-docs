# Decision Review

Load this reference for non-trivial `grill-with-docs` sessions, especially when the artifact may lead to GitHub issues, PRDs, specs, ADRs, implementation tasks, or doc updates.

## Decision Map

Before asking user-facing questions, classify findings:

- settled by existing docs/ADRs/specs/code
- contradicted by existing docs/ADRs/specs/code
- missing but necessary for this artifact
- interesting but out of scope

Only ask about the "contradicted" or "missing but necessary" items.

## Question Gate

A grill question is allowed only when at least one of these is true:

- It exposes a contradiction between the current artifact and existing docs, ADRs, specs, code, or credible references.
- It asks for a not-yet-documented business rule Daniel must own.
- It asks for an architecture decision with meaningful trade-offs.
- It determines whether an ADR is needed.
- It changes acceptance criteria, scope, risk, data boundaries, customer claims, pricing/offer positioning, legal/security posture, or implementation ownership.
- It resolves overloaded domain language that would confuse future agents.

A grill question is forbidden when any of these is true:

- The answer is already in source-of-truth docs, ADRs, specs, or code.
- The agent can answer it by normal documentation/code/Vault/reference research.
- The answer would not change the current PRD, issue, spec, ADR, acceptance criteria, or implementation boundary.
- It only asks the user to confirm an obvious recommendation.
- It is a routine implementation detail that the implementation agent should decide later.

Prefer this question shape:

> I found ADR/spec/doc A says X, but the current artifact implies Y. This matters because Z. My recommended resolution is R. Should R become the rule for this artifact?

Avoid generic prompts like "What should X mean?" unless existing docs and research genuinely leave X unresolved.

## Capture Rules

Before creating downstream artifacts, make the capture decision explicit: "Glossary update: yes/no; ADR: yes/no; issue/spec capture: yes/no."

- Product/behavior requirement: OpenSpec, PRD, or issue acceptance criteria
- Operating decision or hard-to-reverse trade-off: ADR, only when ADR criteria are met
- One-off implementation detail: current issue/spec only
- Process convention for agents: `docs/agents/` or relevant agent guidance, not `CONTEXT.md`

## Closeout

Before creating GitHub issues, PRDs, specs, or implementation tasks, give a short grill closeout:

- resolved terms and decisions
- open questions intentionally deferred
- documentation capture performed or deliberately skipped, with reason
- recommended downstream artifact shape

Proceed only if the user already asked for the downstream artifact in the original prompt, or explicitly confirms continuing.
