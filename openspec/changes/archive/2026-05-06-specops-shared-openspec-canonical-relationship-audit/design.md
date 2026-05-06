# Design

The Control Spec already defines the key rule: OpenSpec canonical specs may be related sources, while OpenSpec change artifacts must not be imported as default primary SpecOps specs. This batch applies that rule to the smallest coherent OpenSpec subset: canonical `openspec/specs/*/spec.md` files in this repository.

The relationship model is intentionally reference-first:

1. Canonical specs are listed in a dedicated audit table with exact paths.
2. Each row identifies the existing SpecOps target that owns the narrative/control context.
3. Existing legacy OpenSpec-derived primary coverage is retained and marked as an exception.
4. Archived change artifacts remain pending relationship/evidence candidates for a later XL-safe audit or automation slice.

No runtime code or dashboard query behavior is changed.
