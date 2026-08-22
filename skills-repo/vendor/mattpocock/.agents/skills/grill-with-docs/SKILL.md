---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Load `domain-modeling`, then interview the user one question at a time to sharpen the current plan or design while recording durable terms and decisions in the project's existing glossary and ADR structure.

Keep the interview on unresolved material decisions: product behavior, scope, constraints, safety, failure policy, and externally visible tradeoffs. Ask implementation questions only when the answer changes one of those decisions or the user explicitly wants a technical-design review. Otherwise record a reasonable implementation assumption in the spec and leave it to implementation.

After each answer, briefly update the working model and choose the single highest-value unresolved question. Do not repeat settled questions in different words.

Before asking another question, run an exit audit. Stop the interview and summarize the agreed decisions, assumptions, open risks, and documentation changes when any of these is true:

- no unresolved product, scope, safety, or externally visible decision remains;
- the remaining unknowns are implementation parameters that can be decided during delivery;
- another answer would not materially change the plan; or
- the user asks to stop or move on.

Do not wait for the user to notice that the interview has crossed into implementation detail. When the exit audit passes, finish the documentation handoff instead of asking another question.
