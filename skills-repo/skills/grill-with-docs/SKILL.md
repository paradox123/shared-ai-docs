---
name: grill-with-docs
description: Decision-discovery review, also called grill-me, that challenges a plan, PRD, issue, spec, or design against existing domain language, ADRs, docs, code, and reference research. Use when user wants to expose material business rules, inconsistencies, missing acceptance criteria, or architecture decisions before downstream work.
---

<what-to-do>

Run a decision-discovery review of the plan, PRD, issue, spec, or design under discussion. Your job is to find material business rules, domain inconsistencies, missing acceptance criteria, and architecture decisions that must be made or documented.

Answer as much as possible yourself before asking the user. Start from the artifact and sources already named or clearly canonical for the topic. Use broader repository, Daniel's Vault, code, RAG/QMD, or external reference research only when a concrete contradiction or missing decision requires it.

When you do need user input, ask one question at a time, waiting for feedback before continuing. For each question, provide your recommended answer and the evidence or conflict that makes the question necessary.

If a question can be answered from the named artifact, source-of-truth docs, ADRs, code, Daniel's Vault, or reputable external references without broad discovery, answer it yourself instead of asking the user.

Do not ask questions just to continue the grill. If no material unresolved decision remains, summarize the resolved findings and move to the requested downstream artifact or stop.

If the user asks for "one question at a time", keep every grill turn to one main question. When the user asks for a plain-language explanation, translation, or example, answer that request and then restate the current question instead of silently advancing.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for source-of-truth domain docs. Most repos use root `CONTEXT.md` plus `docs/adr/`; multi-context repos use `CONTEXT-MAP.md` to route to context-specific glossary/ADR folders. Create docs lazily only when you have a resolved term or ADR-worthy decision to capture.

## During the session

### Start with a decision evidence pass

Before asking any question or closing the grill, read the smallest source set needed to know whether user input is actually necessary:

- the actual artifact being grilled: PRD, issue, OpenSpec change, proposal, design, tasks, or acceptance criteria
- directly named specs, docs, code files, issue links, or prior session references from the user prompt
- `CONTEXT-MAP.md` or `CONTEXT.md` only when domain terms are being clarified
- ADRs likely to govern the topic only when the artifact implies an architectural or operating decision
- a narrow search for exact terms, states, boundaries, or claims when the named sources leave ambiguity
- RAG/QMD, broader repo/code reads, or external references only after a specific question needs that evidence

Do not run a broad repository startup checklist just because one exists in `AGENTS.md`, unless you are about to edit code or the user explicitly asked for full repo orientation. Keep discovery tied to the artifact being grilled.

Use [decision-review.md](references/decision-review.md) for the full decision map, question gate, capture rules, and closeout checklist when the grill is non-trivial or about downstream artifacts.

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a new or changed canonical domain term is resolved and it is not already documented, update the appropriate `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

</supporting-info>
