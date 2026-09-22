## 1. Contract and skill
- [x] 1.1 Recover bounded session evidence and define scope/specification.
- [x] 1.2 Author skill, message templates and recovery/ledger reference.
## 2. Recovery helper
- [x] 2.1 Verify CLI selection and failure behavior with red-green slices.
## 3. Validation and activation
- [x] 3.1 Forward-test orchestration decisions against isolated scenarios and review.
- [x] 3.2 Validate skill/OpenSpec, reread all resources, activate and inspect final diff.

## 4. Parallel batch extension
- [x] 4.1 Clarify material decisions and record the parallel batch contract before updating the delivered skill.
- [x] 4.2 Update skill, references, prompts and specification for bounded parallel work, serialized delivery and cleanup.
- [x] 4.3 Forward-test scheduling and cleanup scenarios; complete independent review and coherence checks.
- [x] 4.4 Validate and publish scoped skill changes to the shared repository.

## 5. Script support design
- [x] 5.1 Clarify first-release scope and adoption requirements in scripted-batch-design.md; record accepted decisions before specifying implementation.

## 6. Token-efficient batch workflow
- [x] 6.1 Implement local mechanical helpers through CLI behavior tests in red-green slices.
- [x] 6.2 Update review order, delta reviews, compact context, role profile, fixture/test timing and consolidated closeout in the skill and prompts.
- [x] 6.3 Critically verify helper failure paths and forward-test workflow decisions; repair findings before final independent review.
- [x] 6.4 Complete refactoring, validation and a requirement-by-requirement acceptance overview; verify active skill links.

## 7. Shared completion contract
- [x] 7.1 Record the accepted DRY → SOLID → KISS sequence with separate agents for all three repositories in ADR 0017 and completion-contract-design.md.
- [x] 7.2 Record applicability to substantive technical changes; editorial-only corrections retain appropriate document checks.
- [x] 7.3 Record acceptance-triggered completion after direct implementation and initial tests; authorized coordinators trigger the same workflow for fully delegated work. Finish the design interview and documentation handoff.
- [x] 7.4 Record code-review as the sole owner of DRY → SOLID → KISS, repository standards and review follow-up; place the Spec comparison in preceding critical requirements verification and keep callers as references.
- [x] 7.5 Specify and implement the common workflow and central code-review definition; migrate conflicting entrypoints/templates and repository guidance.
- [x] 7.6 Initially verify direct, standalone-review and orchestrated completion decisions, contextual trigger recognition, evidence reuse and affected revalidation through isolated scenarios and source/link checks.
- [x] 7.7 After contextual acceptance, run change-accepted for this migration, including critical verification and the central code-review workflow; preserve initial checks without claiming full technical completion early.

## 8. Worker-driven coordination (2026-09-21)
- [x] 8.1 Use the 2026-09-20 batch analysis to agree the bounded extension and update requirements in this existing change.
- [x] 8.2 Replace polling defaults and conflicting templates with worker events, durable receipts and explicit recovery modes.
- [x] 8.3 Add public-CLI event classification through red-green slices; preserve existing helper behavior.
- [x] 8.4 Integrate early evidence, bounded delegation, scoped repairs and milestone-only usage reporting.
- [x] 8.5 Validate helpers, OpenSpec, skill links and instruction decisions with isolated forward scenarios; record live-wakeup limitations.
- [ ] 8.6 After acceptance of the implemented extension, apply change-accepted for technical closeout; previous completion evidence covers only the earlier revisions.

Initial verification for section 8: [event-coordination-verification.md](event-coordination-verification.md).

## 9. Scripted coordination and shorter instructions
- [x] 9.1 Confirm branch/target and define managed CLI contract in scripted-coordination-design.md.
- [x] 9.2 Implement initialization, command preparation/outcome and compact status through public-CLI red-green slices.
- [x] 9.3 Implement durable worker reports, atomic event decisions, phase and capacity enforcement through public-CLI red-green slices.
- [x] 9.4 Replace superseded instructions and templates with the tested interface and conditional references.
- [x] 9.5 Verify lifecycle/recovery scenarios, regressions, source identity, instruction reduction and skill coherence.

Section 9 evidence and current content identity: [scripted-coordination-verification.md](scripted-coordination-verification.md).
