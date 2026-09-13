# contextual-wiki-operations Specification

## Purpose
Provide observable, serialized maintenance of the common contextual wiki. Preserve valid independent results across bounded failures, block affected or unverified evidence, retain local failure reports, and support safe QMD maintenance and idempotent repair.
## Requirements
### Requirement: Observable serialized maintenance with bounded failures
The maintenance helper MUST serialize runs, persist command stdout, stderr and exit status in a unique local artifact directory, and emit a compact machine-readable final report. It MUST validate result contracts rather than trusting exit codes alone. A bounded failure MUST block affected outputs and dependent work while permitting independent maintenance and safely executable QMD maintenance to continue. A partial run MUST report non-success, the failed work and what remains pending. Missing evidence, invalid responses and incomplete scans MUST NOT be treated as valid current knowledge or confirmed source removal. Shared failures MUST block every dependent operation. Repeated successful runs MUST preserve no-op behavior.

#### Scenario: Bounded source or compilation failure
- **WHEN** one source or dependent synthesis cannot be processed but other work is independent
- **THEN** affected knowledge is not exposed as verified current evidence
- **AND** independent maintenance can complete with a partial-failure report
- **AND** QMD work proceeds only over states whose eligibility can be established

#### Scenario: Repair after an isolated failure
- **WHEN** an established dependency branch fails while an independent source is corrected
- **THEN** the independent page is published and indexed, but directly and transitively dependent concepts and saved answers remain unavailable as current wiki evidence
- **AND** local run evidence records completed, unchanged, failed and pending work with a non-success exit
- **AND** after repair only pending compilation is retried and the next unchanged run is a no-op

#### Scenario: Shared failure or unknown dependencies
- **WHEN** a shared runtime or index fails, or the affected work cannot be safely separated
- **THEN** the operations depending on that failed prerequisite stop visibly
- **AND** neither empty output nor an incomplete scan is interpreted as success or mass removal

#### Scenario: Unchanged or concurrent run
- **WHEN** an unchanged wiki is maintained again
- **THEN** the no-op outcome is reported and QMD maintenance still completes
- **AND** a concurrent invocation fails visibly without overlapping mutations

### Requirement: Reproducible upstream wiki release qualification
The public installer MUST resolve a regular published release of `atomicstrata/llm-wiki-compiler` to an exact commit and prepare a new candidate separate from the active installation. Main-branch commits, bare tags without a published release and drafts MUST NOT qualify as release evidence; prereleases MUST be excluded by default. Bootstrap and runtime validation MUST use one shared release/commit definition, preserving the previously selected release when that definition is consolidated.

The candidate MUST use the dependency versions defined by the release manifest and lockfile without independent library updates or lockfile re-resolution. Existing integration patches MUST apply reproducibly without changing those dependency inputs. Missing or incompatible runtimes, patch conflicts and installation failures MUST produce an explicit non-success result while preserving the active installation.

Eligibility MUST require a successful build and all required upstream and managed CLI compatibility tests on bounded fixtures, including query, original-source provenance, freshness and maintenance. Every required test file MUST have evidence of actually executed successful tests; file existence, aggregate success, empty test files or externally filtered-away scenarios MUST NOT substitute for this evidence. Missing, pending, skipped or failed required checks MUST leave the candidate ineligible. Installation success alone MUST NOT qualify the candidate.

The persistent candidate report MUST associate release identity, exact commit, patch hashes, dependency input hashes and required check results with that concrete candidate. Interrupted or incomplete qualification MUST remain visibly ineligible. Successful and deliberately failing candidates MUST be verifiable through the public installer without changing existing wiki data, original source repositories or maintenance automation. Qualification MUST NOT itself activate a candidate; activation and rollback are separate operations.

#### Scenario: Install and qualify an isolated release candidate
- **WHEN** an operator selects a regular published upstream release
- **THEN** the public installer resolves its release tag to an exact commit and prepares a fresh candidate separate from the active installation
- **AND** the existing integration patches apply without changing the release manifest or lockfile, and installation uses the frozen lockfile
- **AND** build, upstream compatibility tests and managed CLI tests cover query, original-source provenance, freshness and maintenance on bounded fixtures
- **AND** the candidate report binds release identity, commit, patch hashes, dependency input hashes and required check results to that candidate
- **AND** missing runtimes, patch conflicts, installation failures and missing, pending or failed checks leave eligibility false and the active installation unchanged
- **AND** bootstrap and runtime validation read one shared release/commit definition, preserving the previously selected release before extension

#### Scenario: Reject an unpublished or preliminary revision
- **WHEN** a selected revision has only a main-branch commit, a bare tag, a draft release or a prerelease
- **THEN** it is not qualified as a regular published release candidate
- **AND** the active installation is retained

#### Scenario: Preserve upstream dependency inputs
- **WHEN** the same upstream revision is installed again, including after a library independently publishes a newer version
- **THEN** the release manifest and lockfile still determine the installed dependencies without re-resolution
- **AND** those files remain byte-identical through patching, installation, build and checks

#### Scenario: Required tests are absent or silently excluded
- **WHEN** a required file is missing, excluded by test-runner configuration, empty or has its scenarios filtered away
- **THEN** aggregate passing results cannot make the candidate eligible
- **AND** the required scenario executes or the missing execution evidence causes a non-success result

#### Scenario: Interrupted or failed qualification preserves the active installation
- **WHEN** patching, runtime validation, installation, build or a required test cannot complete successfully
- **THEN** the persistent report retains failed or incomplete work and the candidate remains ineligible
- **AND** existing installation files and production wiki data remain unchanged

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
