## ADDED Requirements

### Requirement: Completed Nebenkosten 2025 Backfill

The SpecOps historical backfill MUST import the selected completed Nebenkostenabrechnung 2025 source group as dashboard-visible SpecOps spec entities unless the exact source path already has an entity.

#### Scenario: Missing selected Completed sources are imported
- **WHEN** the Completed 1B backfill completes
- **THEN** the 13 previously missing selected sources have new SpecOps spec entities

#### Scenario: Existing BE2 Heiznebenkosten source is not duplicated
- **WHEN** the backfill encounters the existing `BE2 Heiznebenkosten Sonderverteilung` source path
- **THEN** the existing entity is counted as done and is not duplicated

#### Scenario: Completed coverage advances
- **WHEN** the run completes
- **THEN** Completed source coverage increases to 24/32

#### Scenario: Dashboard visibility uses existing queries
- **WHEN** SpecOps dashboards query `_shared/SpecOps/Entities/specs` for `type = "spec"`
- **THEN** the selected Nebenkosten 2025 completed sources are discoverable through their entity notes
