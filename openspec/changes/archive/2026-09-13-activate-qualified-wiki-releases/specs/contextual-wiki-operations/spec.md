## ADDED Requirements

### Requirement: Transactional local activation of qualified releases
The public update command MUST activate only the concrete candidate whose required checks all passed and whose full runtime contents still match qualification. Changes to wrapper, compiler build, installed dependencies or runtime MUST require renewed qualification. Adoption MUST require no renewed human approval. The active runtime MUST be a separate verified snapshot selected atomically, preserving the prior working runtime.

Activation MUST verify the actually selected release and commit through the running runtime and a bounded public wiki operation, including preserved pages, saved synthesis, provenance and reusable state from the prior runtime. An identity manifest alone MUST NOT prove activation. Existing production wiki data MUST remain unchanged during activation. Releases needing unsupported data migration MUST fail compatibility verification; any future supported data migration MUST include recoverable affected data before activation is allowed.

Concurrent updates and public wiki use MUST share an exclusive process-lifetime lock so no mixed runtime or overlapping state changes occur. Repeated activation of the same unchanged qualified runtime MUST be a no-op. Failed switching or functional verification MUST restore the prior selection and clearly report non-success and the retained active identity. Interrupted provisional activation MUST be recovered before subsequent public use. Success, no-op and deliberate activation failure MUST be demonstrated on the Mac without modifying knowledge maintenance or its scheduler.

#### Scenario: Activate only unchanged qualified bytes
- **WHEN** a candidate passes every check and its complete runtime matches the recorded qualification
- **THEN** the updater snapshots and activates that exact runtime without another human approval
- **AND** any changed candidate or incomplete check is rejected before replacing the prior runtime

#### Scenario: Verify activation and preserve knowledge
- **WHEN** the selection switches to the candidate
- **THEN** the running runtime reports the expected release and commit and reads prior-runtime fixture knowledge with checked original-source provenance
- **AND** saved synthesis and reusable state survive a no-op maintenance run and a controlled source correction is propagated using the prior compiler state, while production data remain untouched

#### Scenario: Fail or interrupt activation
- **WHEN** switching or the activation probe fails or is interrupted
- **THEN** the prior runtime is restored before ordinary use and the result reports failure and the retained identity

#### Scenario: Repeat or overlap activation
- **WHEN** the same unchanged candidate is supplied again
- **THEN** activation reports a no-op
- **AND** overlapping updates and wiki commands fail visibly as busy without overlapping runtime or state changes
