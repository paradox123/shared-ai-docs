# Spec Deltas

## ADDED Requirements

### Requirement: KI Specs Dashboard Backfill

The SpecOps historical backfill MUST import every `ki-fuer-kmu/_specs` narrative source as a dashboard-visible SpecOps spec entity unless the exact source path already has an entity.

#### Scenario: Missing KI sources are imported
- **WHEN** the KI specs backfill completes
- **THEN** the 17 previously missing `ki-fuer-kmu/_specs` sources have new SpecOps spec entities

#### Scenario: Already imported KI sources are not duplicated
- **WHEN** the KI specs backfill encounters an exact source path that already exists in SpecOps entities
- **THEN** that source is counted as already done and is not imported a second time

#### Scenario: Dashboard visibility uses existing queries
- **WHEN** SpecOps dashboards query `_shared/SpecOps/Entities/specs` for `type = "spec"`
- **THEN** all 19 `ki-fuer-kmu/_specs` sources are discoverable through their entity notes

#### Scenario: Superseded sources remain historical
- **WHEN** a source begins with a `Superseded for Free Entry v2` notice
- **THEN** its entity status is `superseded` and its lifecycle is `legacy`
