## ADDED Requirements

### Requirement: Verify one unchanged expected head
The pilot SHALL execute trusted deterministic verification for the evidence-ready draft's expected head. It SHALL compare local head, branch, worktree cleanliness and authoritative provider head before and after execution, including failed commands. Any mutation SHALL block qualification. An ordinary check failure SHALL still run all three reviews for the unchanged head.

#### Scenario: Verification changes the head while failing
- **WHEN** a verification command commits a change and exits unsuccessfully
- **THEN** the run retains a head-drift blocker and never qualifies the old or new head

### Requirement: Review independently with validated head-bound provenance
The pilot SHALL run requirements, code-quality and architecture reviews in three fresh peer-blind read-only Codex sessions for the same head. Inputs SHALL include requirements, repository guidance, diff and current evidence, without peer results or writer conversation. Reviews SHALL use Terra/xhigh and pinned `code-review` for requirements/code-quality and `codebase-design` plus `domain-modeling` for architecture. Version, axis, head, pass/fail/not_applicable verdict, nonempty rationale and concrete findings SHALL be validated and retained with invocation/session/policy/skill provenance. Requirements SHALL NOT be not_applicable. Invalid or missing output SHALL block without fabricated repair findings.

#### Scenario: One axis is invalid
- **WHEN** a reviewer returns a wrong head, axis, malformed result or forbidden not_applicable
- **THEN** no qualification or automatic repair occurs and independent results remain observable

### Requirement: Qualify only the complete current head
Qualification SHALL require passing direct evidence, deterministic verification and every applicable review for exactly the current provider head. A new writer head SHALL invalidate all prior usable evidence, checks and verdicts while retaining their history. Qualification SHALL mean readiness for human review only and SHALL NOT create human approval, merge, deployment or release.

#### Scenario: Old results cannot qualify a changed head
- **WHEN** all old results pass but provider or local head changes
- **THEN** the run has no qualified head and exposes a concrete stale-head blocker

### Requirement: Repair with the original writer at most three times
Actionable failed-axis findings SHALL reach only the original writer session and worktree with requirements, guidance, reviewed head, prior attempt summaries and a numbered assignment. Ordinary repairs SHALL use Terra/xhigh/workspace-write; final round three SHALL use Sol/xhigh with final_repair_round. Each completed repair SHALL produce a new descendant commit on the existing branch, recapture evidence, update the one existing draft and run fresh verification and all three independent reviews. No fourth automatic repair SHALL start, including after restart or redelivery. Product decisions SHALL produce human handoff instead of invented requirements.

#### Scenario: First repair succeeds
- **WHEN** the same writer repairs actionable findings and the new head passes fresh evidence, checks and reviews
- **THEN** the original draft remains the only PR, the new head qualifies and round two never starts

#### Scenario: Three repairs fail
- **WHEN** fresh results after repair three remain unsuccessful
- **THEN** the run retains exactly three repairs and a concrete Human Request with branch, draft, evidence and open findings; replay starts no fourth repair

### Requirement: Preserve qualification through the operator system seam
Qualification rounds, dispatch identities, results, head invalidation and Human Requests SHALL be redacted and durably observable through authenticated run/history/export read-back. Worker replacement SHALL reconcile completed adapter operations without duplicate sessions or repair effects; uncertain external or interrupted deterministic work SHALL fail closed. Repository serialization and control fencing SHALL cover qualification work.

#### Scenario: Replacement replays a finished qualification
- **WHEN** API and worker restart after qualification
- **THEN** the same head, results and session identities remain readable without another review or writer invocation, after current-head validation
