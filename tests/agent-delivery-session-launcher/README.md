# Agent Delivery Session Launcher Fixtures

`valid-ready` is a synthetic implementation-ready child handoff used for queue, dry-run and unsupported-provider verification.

`invalid-stale` intentionally disagrees across target id, verdict, handoff pointer and write-set so the launcher must produce `blocked` evidence instead of a successful queue or launch.
