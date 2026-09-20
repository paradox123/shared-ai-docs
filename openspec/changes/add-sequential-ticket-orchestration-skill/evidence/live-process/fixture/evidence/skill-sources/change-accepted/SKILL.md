---
name: change-accepted
description: Complete a concrete implemented change after contextual acceptance such as "akzeptiert", "Change accepted" or an equivalent closeout request, including an authorized coordinator's delegated request. Verify requirements, invoke code-review and continue only authorized delivery/archive actions. Design agreement and quoted acceptance text do not trigger closeout.
---

# Change Accepted

This is the shared technical completion entrypoint for direct and delegated work. It owns the transition from initial implementation evidence to technical completion, while [code-review](../code-review/SKILL.md) owns applicability and review methodology.

1. **Resolve the request.** Identify the concrete implemented change, repository/write set, existing evidence, original authorization and any delivery target/actions. Ordinary implementation ends with initial evidence and `awaiting-acceptance`; it does not trigger this workflow automatically. A fully authorized coordinator may issue the same completion request without another human gate. An explicit archive/finalization request can be an equivalent completion request. Do not infer a target or push/merge permission merely from "accepted". Ask only for genuinely ambiguous scope or missing authority needed for a concrete remaining action.
2. **Reuse current evidence.** Inspect the [completion record](../code-review/references/completion-record.md) if present. Repeated acceptance continues outstanding work; it does not restart valid verification. Apply code-review's central scope rule. For editorial-only work, run the relevant document checks and record why structural review is not required.
3. **Verify requirements first.** For substantive work, use [requirements-verification.md](references/requirements-verification.md). Repair gaps and refresh affected evidence before invoking structural review.
4. **Invoke code-review.** Pass the fixed scope/base/current identity, requirements evidence, repository standards and existing receipts. Let that skill run or reuse its checks. Do not add another generic review after it.
5. **Continue authorized closeout.** Require current technical-completion evidence before delivery/archive. Follow repository-specific integration, branch protection, OpenSpec and issue workflows within the original authority; existing explicit delegation persists. An orchestrated worker returns its record and waits for the coordinator's integration slot and exact delivery grant. A missing new target does not prevent finishing local technical checks. Do not ask again for actions already authorized.

For OpenSpec, use the repo-local archive skill only after technical completion, passing the record so archival reuses it. For another archive format, use that repository's workflow. Reconcile pure archive/path movements by content mapping; substantive edits reopen affected checks through the same owners. Finish with the actual technical and delivery state, evidence and remaining limitations. Never imply completion from edits or passing check counts alone.
