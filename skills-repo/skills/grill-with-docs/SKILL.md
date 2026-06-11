---
name: grill-with-docs
description: Grilling session, also called grill-me, that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions.
---

<what-to-do>

Run a decision-discovery review of the plan, PRD, issue, spec, or design under discussion. Your job is to find material business rules, domain inconsistencies, missing acceptance criteria, and architecture decisions that must be made or documented.

Answer as much as possible yourself before asking the user. Use the repository, Daniel's Vault documentation (`~/Documents/DanielsVault`), existing ADRs, specs, code, and external best-practice/reference-architecture research when relevant. Ask the user only for decisions that cannot be responsibly answered from those sources.

When you do need user input, ask one question at a time, waiting for feedback before continuing. For each question, provide your recommended answer and the evidence or conflict that makes the question necessary.

If a question can be answered by exploring docs, ADRs, code, Daniel's Vault, or reputable external references, answer it yourself instead of asking the user.

Do not ask questions just to continue the grill. If no material unresolved decision remains, summarize the resolved findings and move to the requested downstream artifact or stop.

If the user asks for "one question at a time", keep every grill turn to one main question. When the user asks for a plain-language explanation, translation, or example, answer that request and then restate the current question instead of silently advancing.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Start with a decision evidence pass

Before the first question, read enough source material to know whether a question is actually necessary:

- `CONTEXT-MAP.md` if present, otherwise root `CONTEXT.md` if present
- all ADRs likely to govern the topic, from root or context-specific `docs/adr/`
- the actual artifact being grilled: PRD, issue, OpenSpec change, proposal, design, tasks, or acceptance criteria
- directly named specs, docs, code files, issue links, or prior session references from the user prompt
- relevant Daniel's Vault/project documentation using RAG/QMD when available, otherwise `rg`
- a narrow search for the exact terms, states, boundaries, or claims being clarified
- external best practices or reference architectures when the decision depends on established outside patterns

Do not run a broad repository startup checklist just because one exists in `AGENTS.md`, unless you are about to edit code or the user explicitly asked for full repo orientation. Keep discovery tied to the artifact being grilled.

Build an internal decision map before asking anything:

- settled by existing docs/ADRs/specs/code
- contradicted by existing docs/ADRs/specs/code
- missing but necessary for this artifact
- interesting but out of scope

Only ask about the "contradicted" or "missing but necessary" items.

### Question gate

A grill question is allowed only when at least one of these is true:

- It exposes a contradiction between the current artifact and existing docs, ADRs, specs, code, or credible references.
- It asks for a business rule Daniel must own.
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

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

If the resolved item is not glossary material, say so and capture it in the appropriate artifact instead:

- Product/behavior requirement: OpenSpec, PRD, or GitHub issue acceptance criteria
- Operating decision or hard-to-reverse trade-off: ADR, only when the ADR criteria below are met
- One-off implementation detail: current issue/spec only
- Process convention for agents: `docs/agents/` or the relevant agent guidance, not `CONTEXT.md`

Before creating downstream artifacts, make the capture decision explicit: "Glossary update: yes/no; ADR: yes/no; issue/spec capture: yes/no."

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

### Close the grill before downstream work

Before creating GitHub issues, PRDs, specs, or implementation tasks, give a short grill closeout:

- Resolved terms and decisions
- Open questions intentionally deferred
- Documentation capture performed or deliberately skipped, with reason
- Recommended downstream artifact shape

Then proceed only if the user already asked for the downstream artifact in the original prompt, or explicitly confirms continuing.

</supporting-info>
