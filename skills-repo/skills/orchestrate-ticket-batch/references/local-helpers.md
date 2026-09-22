# Managed coordination CLI

Use `python3 <resolved-skill>/scripts/batch_state.py`. Standard library only; no task, Git or scheduler calls. New batches use schema 2. Old schema-1 helpers remain available; never point generic `checkpoint` at a managed ledger. Keep the ledger, generated packets and reports together outside **all** disposable worktrees. Hosts need access to these absolute paths.

## Initialize and inspect

Write an operation JSON file with actual values:

```json
{
  "op": "init",
  "batch": {
    "id": "audit-batch", "repository": "/absolute/repository",
    "target": "release/audit", "authority": "original user request reference",
    "coordinator": {"thread_id": "confirmed-coordinator-id", "host_id": "local"}
  },
  "tickets": {"11": {}, "12": {"depends_on": ["11"]}, "13": {"conflicts": ["11"]}},
  "limits": {"tickets": 3, "subagents": 3},
  "continuation": {"mode": "active-wait"}
}
```

`continuation.mode` is `active-wait`, `callback`, `heartbeat` or `manual`; background modes also require `evidence` describing observed idle wake or authorized scheduled recovery. Recording a mode does not configure it. Declare semantic dependencies/conflicts from inspection; an unresolved dependency outside the batch blocks dispatch. Ticket order is the tie-breaker.

```sh
python3 "$SKILL_DIR/scripts/batch_state.py" coordinate --ledger "$BATCH_DIR/state.json" --expect-revision 0 --input "$BATCH_DIR/operation.json"
python3 "$SKILL_DIR/scripts/batch_state.py" status --ledger "$BATCH_DIR/state.json"
```

Every subsequent coordinate call uses the latest returned revision. Status gives identities, current packet, pending dispatch, report/evidence references, capacity and next decision without history/full instructions. A proposed next step is not authorization or proof of eligibility. Check the relevant evidence and live facts.

## Prepare and record an external command

Operation `prepare` requires `ticket`, `phase` and a task-specific `instruction`. It generates a request ID, durable packet with ready-to-use `message`, and pending dispatch in the ledger. Dispatch only after success and only from the current packet. A packet file alone is not sufficient: interrupted publication may leave an orphan that is absent from the ledger. There is no automatic retry or exactly-once transport guarantee.

| Phase | Prerequisite / additional input |
| --- | --- |
| registering | Queued eligible ticket; optional `allowance` (default 0) reserves nested-agent capacity. Use packet message with create_thread and explicit target/worktree settings. |
| implementing | Directly verified registration recorded; send packet message to the recorded worker. |
| verifying | Implementation/repair ready; `content_ref` matching that report and absolute `evidence` path for inspected substantive acceptance. |
| repairing | Report from implementation, verification, prior repair or integration; `quiescent: true`, `evidence`; instruction names findings and evidence delta. |
| integrating | Technically accepted awaiting-integration ticket; `target_ref`. Reserves one integration holder. Repeat preparation after target movement requires the current ready report's `content_ref` and `evidence`. |
| delivering | Integration ready; matching `content_ref`, tested `target_ref`, separately observed `current_target_ref`, and `evidence`. |
| cleanup | Delivered/quiescent ticket in cleanup; `step`, fresh preflight `evidence`, and instruction describing the exact coordinator mutation. Never send cleanup to the worker. |

Example after inspecting implementation evidence:

```json
{"op":"prepare","ticket":"11","phase":"verifying","instruction":"Complete change X; inspect criteria A/B and reuse valid proofs.","content_ref":"actual-head-or-manifest","evidence":"/absolute/acceptance.md"}
```

After the tool call, use `record` with `ticket`, exact `request_id`, `outcome` (`confirmed`, `unknown`, `not-sent`) and an absolute `evidence` file recording the actual tool result/reconciliation. `confirmed` clears pending dispatch. The others retain it. For proven `not-sent`, send the **same packet** if still authorized, then record its outcome; never prepare a replacement. With unknown outcome, inspect destination/remote state first. A tool timeout is not proof of non-delivery.

Registration confirmation additionally supplies `worker`: real `thread_id`, `host_id`, absolute `worktree`, owned `branch`, `base_sha`. A provisional client ID is insufficient: leave creation unknown and use identity recovery. Worker identity, branch and checkout cannot be reused by another ticket. Registration's initial report is the normal task result, before a bound implementation packet exists.

## Consume a worker report and decide

Workers use `report` as described in [worker-events.md](worker-events.md). The coordinator supplies:

```json
{"op":"consume","ticket":"11","event":"/absolute/generated-event.json","next":{"phase":"verifying","instruction":"Complete change X","content_ref":"reported-contents","evidence":"/absolute/acceptance.md"}}
```

Omit `next` to record the result without acceptance or a phase change. Include it after inspection: with `instruction` it prepares a command; without it, it advances a local decision. The receipt and resulting command/phase share one ledger revision. A failed decision leaves both unchanged. Identity/phase mismatch, sequence conflicts/gaps, changed evidence and pending uncertain dispatch block progress; inspect only the affected worker. Duplicates/stale events leave the ledger unchanged and do not clear existing pending actions. Do not manually reset receipts or skip sequences.

`advance` uses the same decision fields independently after a report was consumed:

| To phase | From / required facts |
| --- | --- |
| awaiting-integration | verifying; matching `content_ref`, inspected `evidence`, current `completion_record` file |
| confirming | delivering; matching `content_ref`, inspected `evidence`; reported candidate and target must match the grant |
| cleanup | confirming; `quiescent: true`, `evidence`, and `delivery` containing exact `target`, accepted `content_ref`, actual `merge_ref`, `pr`, `closed: true` |
| done | cleanup; all cleanup outcomes confirmed plus final `evidence` |

Cleanup steps are `evidence-preserved`, `worktree-removed`, `local-branch-removed`, `remote-branch-removed`, `worker-archived`. Prepare/record each actual mutation, including unknown outcomes. Retention precedes deletion, archival follows resource cleanup. Live ownership checks remain in [parallel-delivery.md](parallel-delivery.md). Evidence files are assertions supplied by the coordinator: their existence/hash does not prove correctness or authority.

## Capacity and recovery

`capacity` takes `ticket`, `allowance`, optional `parked`, `quiescent: true` and `evidence`. It requires reconciled dispatch and enforces total reservations. Parking releases the ticket slot and requires allowance 0; dependency/conflict reservations remain. Resuming rechecks eligibility and limits. A changed allowance in a follow-up prepare also requires quiescence/evidence; tell the worker its new grant before further delegation.

Parking an integration holder additionally requires acknowledged `grant_revoked: true` and verified `mutation_absent: true`, documented in evidence. It returns to awaiting integration; prior grants do not revive. Unknown pending mutations cannot be released. Successful verified delivery releases integration and worker capacity independently of remaining cleanup.

Only the coordinator calls coordinate; workers own their report streams. The helper locks the ledger, rejects stale revisions, validates the whole operation before publishing a packet, and replaces state atomically. Inspect an existing lock's owner and interrupted operations before removing a stale lock. Never remove a live lock, patch around a blocker, or migrate a live ledger implicitly. Old/custom ledgers require explicit adoption and preservation of all uncertain actions.

Exit 0 means a local operation succeeded (or an event was duplicate/stale), 2 means blocked/diverged, 3 means invalid/unreadable input. Always inspect the result. Missing permission, truth of evidence, external target freshness and runtime wake behavior cannot be established by this helper.

For a meaningful observation, `observe` accepts `ticket`, `evidence`, and `facts` limited to `wait_cursor`, `usage`, `scope_notes`, `deferred_closeout`, `role_profile`. It can also update `continuation` using the same mode/evidence contract as initialization. Batch cursor-only updates with the next useful checkpoint; do not poll just to collect metrics. Observations cannot patch phases, requests or reservations.

## Existing evidence utilities

`manifest --root ROOT --files FILES.json` hashes an explicit nonempty list of relative regular-file paths. `verify --root ROOT --manifest MANIFEST.json` detects changed/missing bytes. `retain --root ROOT --manifest MANIFEST.json --destination DEST` verifies and copies outside the source tree without replacing different existing evidence. Check exit status and retain immutable revision-specific manifests. Include report assets, inspect retained artifacts and confirm the destination is outside every disposable worktree.

Legacy-only `compare`, `classify-event` and `checkpoint` remain for adopted older workflows; use `--help` for flags. They do not enforce the managed lifecycle. `checkpoint` preserves unknown fields with recursive object merges, so it must never be used as an alternate managed-state mutation path.
