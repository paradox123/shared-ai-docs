# Parent-first Orchestration Output

Route decision: the parent is oversized, so the next workflow mode is
`spec-orchestrator`, followed by `child-spec-hardening`. The output stays at
the planning and hardening control-surface level.

Generated artifacts: Child Specs, exact Child Index, Coverage Matrix,
Dependencies, Hardening Queue and one leading next child state. App code and
secret handling are outside this output.
