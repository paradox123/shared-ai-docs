## Context

Ticket 10 supplies the real AgentSessionAdapter and native continuation. Ticket 05
supplies repository reconciliation; Ticket 09 supplies redacted public history.
The new path must not relabel agent prose or process logs as business evidence.

## Goals / Non-Goals

Implement Ticket 11 through the worker command and authenticated run projection.
No merge, review approval, deployment or changes to LangGraph. Controlled provider
tests prove protocol behavior separately from any live GitHub/Codex acceptance.

## Decisions

- Add an exclusive publication worker mode. PostgreSQL owns immutable assignment,
  phase reports and dispatch intent. The existing real Agent Framework workflow
  owns the agent session; no second model orchestrator or conversation store.
- A deterministic Python adapter executes bounded argv probes and Git/GitHub
  operations. The operator supplies a trusted plan outside the agent checkout;
  every criterion has kind, phases, surface and expected business read-back.
  Commands have explicit output assertions; a zero exit alone cannot qualify.
- Validate the provider identity, local/remote/provider base and branch before
  start. Required prerequisite categories and per-phase surface probes run before
  model work. Failures become public explicit blockers.
- Commit safe source changes before executing evidence, then require the same
  clean head after evidence and before publication. Evidence commands receive
  that SHA. Redact configured canaries and recognizable credentials before output.
- Persist the sanitized evidence/body and immutable head before provider dispatch.
  Read remote ref and all matching PRs on every delivery; adopt only the exact
  draft/body/base/head. A previously dispatched but absent PR is uncertain and
  cannot authorize another create. This trades unattended retries for uniqueness.
- REST uses request/response/read-back, UI interaction/screenshot/read-back,
  idempotency request/response/repeat/read-back and documents generate/render/
  inspect/read-back. Screenshot phases require readable image bytes and a public
  URL with matching bytes. Logs and dashboard output are supplemental only.

## Risks / Trade-offs

- Trusted executable assertions can be authored incorrectly: retain commands,
  expectations and observations beside criteria for human review.
- Provider ambiguity or loss of create reply: fail closed and reconcile by read,
  without a second create. Git push uses an exact ref and expected previous SHA.
- Secret discovery is bounded: configured values plus recognizable credential
  patterns; opaque images are published only from pre-redacted trusted surfaces.
- Additive PostgreSQL table/projection requires stopping old worker binaries
  before upgrading; tests use disposable databases and local Git remotes.
