# Microsoft Agent Framework OSS durability Gate 0

This workspace answers one question before the sibling product pilot exists: can
the pinned Microsoft Agent Framework Durable Extension tuple use a
production-capable, self-managed open-source backend without unavoidable
framework or managed-workflow-service charges?

Run the committed audit with:

```bash
python3 gate.py evaluate \
  --manifest manifest.json \
  --observed observed.json \
  --boundaries protected-boundaries.json \
  --evidence-root evidence
```

Exit `0` means `go`; exit `2` means the gate executed correctly and reached a
`no-go`; other nonzero exits are invocation failures. The CLI never starts a
probe until manifest, provenance, backend, licence, cost, and isolation checks
are all eligible.

At evaluation time the CLI re-observes Git HEAD, the gate and dirty-state
digests, .NET SDK/RID, configuration/contract files, package lock, and component
inventory. The checked-in `observed.json` is an auditable record, not a trusted
substitute for that live observation.

For an eligible backend, the gate launches two real OS worker processes. It
waits for worker one to durably record its first effect and checkpoint,
terminates that process itself, then starts worker two against the same
orchestration ledger. A `go` requires distinct observed PIDs, the same
orchestration identity, the continuation checkpoint, and each expected effect
exactly once. Ports, process names, state paths, the evidence path, and protected
before/after fingerprints are checked as isolation boundaries.

The directory is intentionally not the planned
`microsoft-agent-framework-work-package-pilot/`. A Gate 0 no-go leaves that
later application absent.
