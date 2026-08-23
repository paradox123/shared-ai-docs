## Context

The pilot's repository adapter, Cloudflare relay, durable local workflow, isolated implementation worker, exact-head verifier, independent reviews, repair loop, evidence-backed draft pull request, startup reconciliation, and macOS LaunchAgent are already implemented and archived as separate changes. The remaining risk is integration and configuration drift at the real `probare-crm` boundary: a syntactically valid private environment can still point at the wrong repository checkout, omit required workflow labels or webhook subscriptions, hide eligible backlog items, or start a service whose public relay cannot reach it.

The activation must be reversible, must not expose credentials or issue content in logs/evidence, and must stop at Daniel's pull-request review. The existing workflow and `RepositoryAdapter` remain the source of runtime behavior; activation tooling is an operator gate and evidence collector, not a second scheduler.

## Goals / Non-Goals

**Goals:**

- Fail closed before activation unless the private runtime, repository checkout, adapter identity/version, GitHub repository access, required workflow labels, allowed webhook event groups, complete open backlog, local LaunchAgent, Worker ingress, and distinct Tunnel route are coherent.
- Make label bootstrapping explicit and idempotent while keeping repository-specific names in one activation profile consumed by the adapter and readiness checker.
- Start the already installed local stack, expose the authorized backlog, and prove one real issue through all productive boundaries to an exact-head verified draft PR.
- Produce a bounded, redacted evidence manifest that correlates delivery, run/checkpoint, worker policy and skills, verification, reviews, label projection, and pull-request head.
- Preserve enough durable state for diagnosis and provide a rollback that stops new ingress without deleting evidence or live work.

**Non-Goals:**

- Adding another live repository, filtering issue types, changing issue ordering, or relaxing blockers and repository serialization.
- Reimplementing scheduling, verification, review, or publication behavior in activation scripts.
- Automatically choosing a product issue, accepting missing requirements, merging, deploying, releasing, deleting branches/worktrees, or draining/deleting Queue/DLQ state.
- Storing or printing tokens, secrets, webhook bodies, issue bodies, reviewer prose containing personal data, or arbitrary external error bodies.

## Decisions

### Add a fail-closed live readiness command at the operator boundary

`pilotctl live-readiness <private-env>` first reuses `verify-config`, then invokes a non-server pilot CLI mode with the parsed private environment. The mode checks the production adapter profile, repository checkout/origin and base ref, GitHub repository permissions, required labels, unfiltered open-issue visibility, ready backlog count, and webhook subscription. It emits only fixed keys, counts, bounded status codes, and hashes; failure output uses stable categories.

Alternative considered: document a sequence of `curl`, `gh`, and shell checks. That would duplicate policy, make redaction dependent on operator discipline, and be difficult to regression-test.

### Keep one activation profile beside the existing adapter binding

The six workflow labels and allowed GitHub event groups are declared once in a repository profile used to construct `RepositorySettings` and to evaluate readiness. The workflow core continues to compare canonical adapter meanings and contains no `probare-crm` paths or branches. Filesystem locations remain private environment values.

Alternative considered: hard-code a second list in `pilotctl` or its documentation. Duplicate configuration could report readiness for a state the runtime does not actually use.

### Separate read-only readiness from explicit label bootstrap

Readiness never mutates GitHub. `pilotctl ensure-live-labels` is a separate explicit, idempotent operator command that creates only missing workflow label definitions with documented descriptions/colors, then reruns readiness. Existing labels and issue assignments are preserved.

Alternative considered: create labels during every readiness check or service start. Hidden writes would make diagnosis and rollback harder and could partially activate an unintended repository.

### Validate webhook subscriptions as event groups, then leave action filtering to both relay and adapter

GitHub webhook configuration exposes event groups rather than per-action filters. Readiness therefore requires the active exact Worker ingress URL and the event groups implied by the adapter profile, while separately validating a distinct Tunnel URL for the Queue consumer's local hop. Cloudflare and the local adapter continue to enforce the narrower event/action pairs. The second-hop secret is validated only by an actual signed delivery; its value is never read back or compared in evidence.

The Queue consumer uses a VPC Service fixed to `127.0.0.1:8788` behind the named Tunnel and calls only the webhook path. A normal Worker subrequest cannot reliably call a public Tunnel hostname on the same Cloudflare zone, while a tunnel-wide VPC Network binding rejects loopback destinations and would grant unnecessary routing choice. The fixed service is the narrowest available route; the existing internal HMAC remains mandatory at the receiver. Ingress explicitly publishes its `ArrayBuffer` envelope with Queue `contentType: "v8"`; the Queue default JSON encoding would otherwise erase the raw body and make delivery signatures impossible to reconstruct.

Alternative considered: infer webhook correctness from a reachable URL. Reachability alone does not prove that GitHub is subscribed to the required events or that signatures flow through the Queue/Tunnel hop.

### Derive the evidence manifest from productive read-back and current GitHub state

After a workflow reaches a terminal review state, `pilotctl capture-live-evidence` reads the local workflow endpoint and current GitHub pull request/labels, requires one common exact head, and writes a mode-`600` JSON manifest outside the repository by default. A separately curated, redacted summary may be committed to this change; raw bodies and secrets are never copied. The validator requires fresh deterministic verification, three independent verdicts, worker model/reasoning/skill provenance, delivery/run/checkpoint correlations, and the canonical PR evidence body before it can report `verified`. Evidence remains criterion-appropriate: UI criteria require screenshots, REST criteria require request/response/read-back, and documentation criteria require rendered-document read-back rather than ornamental UI artifacts.

Alternative considered: use screenshots or logs as the primary proof. They are useful supplements but cannot establish exact-head convergence or criterion coverage on their own.

### Require a GitHub privacy-safe repository-local author identity

The private bootstrap writes a repository-local author name and the GitHub-provided `<id>+<login>@users.noreply.github.com` address. Readiness verifies that local identity without printing it. This prevents GitHub's email-privacy gate from rejecting the implementation push after the worker and evidence gates have already completed.

Alternative considered: depend on the machine-global Git identity or disable GitHub privacy protection. Both would make production behavior depend on unrelated workstation state and weaken an account-level safety setting.

## Risks / Trade-offs

- [The live token lacks hook-administration or label-write permission] → Readiness reports a stable permission category and activation stops; the operator can provide the narrowly required access and retry.
- [The backlog contains an older eligible issue than the intended demonstration issue] → The scheduler remains authoritative and selects the deterministic frontier; activation does not bypass ordering or blockers.
- [A live worker produces a product question or exhausted review loop] → Preserve the draft/evidence and project `needs-info` or `ready-for-human`; do not mislabel the run as verified.
- [Cloudflare or the Mac becomes unavailable mid-run] → Queue retries, durable identities, LaunchAgent recovery, and startup reconciliation resume the same workflow; the manifest must show one converged run.
- [Evidence contains sensitive external text] → Capture only the bounded read model and allowlisted fields, apply existing redaction, scan the artifact, and fail closed on suspicious credential/email patterns.
- [Disabling only the local service causes Queue buildup] → Rollback disables GitHub webhook delivery first, then unloads the LaunchAgent; existing Queue/DLQ and durable local state are preserved and documented.

## Migration Plan

1. Strictly validate this change and add failing CLI behavior tests for readiness, label bootstrap, and exact-head evidence capture.
2. Add the shared production activation profile and implement the minimal operator commands without changing scheduler semantics.
3. Run the complete local test/quality suite, then inspect the real private configuration with secret-safe readiness.
4. Idempotently create only missing workflow labels, confirm the webhook and relay configuration, install/start the current LaunchAgent generation, and rerun readiness.
5. Allow the deterministic eligible frontier to start from a real GitHub event and monitor bounded public read-back until it reaches verified human review or a truthful handoff state.
6. Capture and curate the redacted live evidence, verify the current PR head and labels, and update issue 12.
7. Roll back, if required, by disabling the GitHub webhook and stopping/uninstalling the LaunchAgent (and optionally disabling the relay consumer) while retaining database, Queue/DLQ, worktree, branch, PR, and evidence state.

## Open Questions

None. The deterministic backlog frontier chooses the live issue; missing external permissions or an unavailable eligible issue are operational blockers, not authorization to weaken the contract.
