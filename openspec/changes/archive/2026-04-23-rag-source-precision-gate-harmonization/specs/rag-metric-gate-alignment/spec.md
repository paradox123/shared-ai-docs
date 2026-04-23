## ADDED Requirements

### Requirement: Parent Child Metric Gate Consistency
The parent RAG specification MUST treat child specs `01..05` as the normative verification gate source and MUST not define conflicting blocking KPI semantics.

#### Scenario: Parent references child gate authority
- **WHEN** a reviewer validates verification semantics in the parent spec
- **THEN** the parent clearly states that the full command/assertion checklist in child specs is normative

### Requirement: Source Precision Classification
The specification set MUST classify `source_precision` as optional monitoring for Phase 1 unless child gate specs define it as blocking.

#### Scenario: Blocking versus optional metrics are unambiguous
- **WHEN** metric expectations are read across parent and child spec 04
- **THEN** blocking metrics remain `domain_hit_rate`, `file_hit_rate`, and `cross_domain_leakage`, and `source_precision` is explicitly non-blocking

### Requirement: Autonomous Review Closure Evidence
This change MUST include machine-checkable evidence that the consistency finding was resolved and re-reviewed.

#### Scenario: Evidence exists for finding closure
- **WHEN** implementation evidence is inspected
- **THEN** it includes command-level statuses for marker checks, metric-contract checks, and re-review confirmation
