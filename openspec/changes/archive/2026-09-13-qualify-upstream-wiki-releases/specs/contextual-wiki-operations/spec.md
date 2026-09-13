## ADDED Requirements

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
