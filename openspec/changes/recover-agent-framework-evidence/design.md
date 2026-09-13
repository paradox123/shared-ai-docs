## Context

Issue 11 owns readiness, safe commit creation, evidence execution and immutable PR
intent. Its completed worker-result schema permits incomplete observations. The
result is already retained by the agent-session store, including artifact-backed
results. Publication serializes repository delivery and retains ownership only
while active or while a dispatched external effect remains uncertain.

## Goals / Non-Goals

Goals: precise semantic rejection, bounded deterministic recovery on one head,
separate durable observations, operator/PR read-back and terminal convergence.
Non-goals: another model implementation, review qualification, merging, changing
the canonical worker schema, or publishing incomplete evidence as a qualified PR.

## Decisions

- Use the trusted evidence plan as the semantic contract. Normalize schema phase
  spelling (`read_back` to `read-back`) and report all missing criterion/phase
  pairs; failed verdicts cannot supply passing phases. Schema validity remains a
  separate result. Agent assertions still require independent capture.
- Split safe preparation/commit from observational capture. Persist the capture
  head, original attempt/session correlation and qualification before capture.
  Subsequent commands must reuse this identity and never re-enter implementation
  or commit code. Existing valid publication intent stays immutable.
- Permit at most two capture rounds total. Missing worker observations make the
  first round an evidence correction; otherwise the first is ordinary capture.
  Retry failed capture as correction. Rerun the ordered trusted scenarios so a
  read-back or screenshot has its required context; do not splice agent claims
  into qualified evidence. Source/head/branch drift blocks immediately.
- Persist each numbered start before dispatch and each result separately using
  publication history. Replacement consumes an interrupted round and proceeds
  within the same bound; it cannot silently reset the budget or repeat that round.
- Exhaustion uses terminal `publication-blocked` with exact failed phases and
  next action. Existing repository-owner policy releases pre-dispatch blockers
  and successful drafts, but preserves uncertain dispatched PR ownership. Terminal
  publication resolves any prior native preparation Human Request in the same
  transaction; its original observation remains in history.

## Risks / Trade-offs

- Capture commands can change business fixture state → trusted plans must use
  repeatable synthetic scenarios; every round remains observable.
- Trusted command mutates source → check clean tree, branch and head before and
  after each phase, including failed commands; never commit recovery mutations.
- Capture tool survives its adapter/worker → independently supervise its process
  group with parent/owner liveness and a command deadline.
- Worker dies after dispatch → count the ambiguous round as interrupted rather
  than pretending it succeeded. Recovery requires a replacement worker command,
  matching the existing process-delivery model.
- Worker schema cannot express all document phases → report missing phases and
  capture them through the trusted plan without changing schema v3.

## Migration Plan

Add optional fields to the persisted publication JSON with defaults for old rows.
Stop old worker/API binaries during upgrade. Existing completed intents continue
their reconciliation path. No destructive schema migration. Do not downgrade
while recovery is active because old binaries do not enforce its bound.

## Open Questions

None. The user confirmed direct delivery on `main`. Controlled provider tests
cover deterministic faults, but acceptance also requires actual GitHub
authorization, push, draft creation/adoption and authoritative PR read-back.
Use an isolated private test repository; retain its issues and draft PRs as
reviewable evidence. The intentionally incomplete worker result remains
controlled. Tickets 13 and 14 do not own this missing publication proof.
