# Proposal

## Problem

Narrative source coverage is now complete for shared-ai-docs `_specs`, KI-fuer-KMU `_specs` and NCG docs Specs, but shared-ai-docs OpenSpec material is still only classified. The current filesystem also no longer matches the old phase 5 baseline because multiple accepted changes have since been archived.

## Change

Create a bounded relationship audit for the canonical OpenSpec specs under `shared-ai-docs/openspec/specs`. The run maps canonical OpenSpec specs to existing SpecOps targets and keeps archived OpenSpec change artifacts as evidence/relationship candidates instead of primary specs.

## Expected Outcome

1. All 11 canonical shared-ai-docs OpenSpec specs are mapped in a reference audit.
2. The source inventory and Control Spec distinguish canonical specs from archived change artifacts using current counts.
3. No new primary entity is created from an OpenSpec change artifact.
