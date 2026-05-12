# Simplified Agent Delivery Checks

This test area now validates the simplified Agent Delivery workflow:

- one narrow active OpenSpec change is the implementation context,
- parent/master specs are reference-only,
- cleanup is manifest-driven,
- Skill MDs stay short and call validator commands instead of carrying long rule blocks.

Run:

```sh
tests/docworkflow-agent-delivery/scripts/run-simplified-agent-delivery-checks.sh
```

Active OpenSpec E2E:

```sh
tests/docworkflow-agent-delivery/scripts/run-active-openspec-e2e-checks.sh --keep
```

This E2E reads one large parent fixture, derives five narrow OpenSpec changes,
validates every slice, and writes `count.txt` with exact values `1` through `5`.

Retained fixtures:

- `active-scope/fixtures/valid-slice/`
- `active-scope/fixtures/parent-only.md`
- `e2e/active-openspec/fixtures/large-parent-spec.md`

Retired DWT, MD-E2E, visible-session, launcher/controller, and mock-runner artifacts were removed by `openspec/changes/simplify-agent-delivery-active-openspec/cleanup-manifest.json`.
