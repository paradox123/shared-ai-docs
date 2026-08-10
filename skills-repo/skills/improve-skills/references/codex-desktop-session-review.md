# Codex Desktop Session Review

Use this reference only for Codex Desktop automation/session reviews, Learn-style fan-out reviews, or named skill-quality reviews that require Codex JSONL evidence. The goal is to keep `SKILL.md` compact while preserving the fragile startup and parsing details in one place.

## Startup Order

When the prompt supplies `Automation ID:`, `Automation memory:`, `Automation:`, or `Last run:`, treat those as authoritative inputs. Do not rediscover them with `rg`, `find`, `ls`, or home-directory probes.

Canonical bootstrap:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
AUTOMATION_PATH="$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml"
MEMORY_PATH="$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md"
INDEX_PATH="$CODEX_HOME_RESOLVED/session_index.jsonl"
sed -n '1,220p' "$AUTOMATION_PATH"
if [ -f "$MEMORY_PATH" ]; then
  python3 - "$MEMORY_PATH" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(errors="replace")
cap = 16000
marker = "\n...[bounded memory excerpt; middle omitted]...\n"
if not text:
    print("(empty memory)")
else:
    visible = min(cap - len(marker) - 1, (len(text) * 2) // 3)
    first = (visible + 1) // 2
    last = visible - first
    suffix = text[-last:] if last else ""
    print(text[:first] + marker + suffix)
PY
else
  echo "(missing memory)"
fi
tail -n 120 "$INDEX_PATH"
```

Bound visible memory output by both position and characters, and always omit a middle segment instead of printing the complete file even when it fits below the cap. A line limit alone is not a real output bound because stored prompts and diffs can occupy one very long line. If the visible bootstrap still truncates, narrow the character cap; do not print more of the file. Parse full memory or index contents only inside a compact resolver that emits selected fields or rows.

Treat the visible index tail as a recency excerpt, not as a second authoritative snapshot. After any prompt-mandated bootstrap, capture the full index exactly once for candidate selection and derive both the selected rows and `review_window_end` from those captured bytes. If the live index changes later, leave that new state for the next run. Never select from a later live-index read and then replace its watermark with the earlier tail maximum, and never reread the live index to recompute the cursor.

Shell variables are scoped to one shell/tool call. "Resolve Codex home once" means choose one canonical value for the run, not assume `CODEX_HOME_RESOLVED` survives into another exec cell. Keep dependent operations in one shell when practical; otherwise repeat the same normalization at the start of each separate shell or pass the already-resolved path as an explicit quoted argument. Do not compensate with hard-coded home paths, environment dumps, or home-directory probes.

If the automation prompt explicitly requires the canonical automation reads before secondary skill/reference files, run the canonical bootstrap first, then load this reference and continue from the memory-backed cursor. Record that as prompt precedence, not avoidable discovery.

If higher-priority instructions require loading this skill's `SKILL.md`, a repo startup file such as `VAULT_AGENT_STRUCTURE.md`, or both before task work, keep those reads minimal and isolated. The safe opening sequence is:

1. Read only the required skill/startup file(s); do not include memory, Codex-home probes, `find`, `rg`, `pwd`, `git`, or session reads in that same tool batch.
2. Read this reference.
3. Run the canonical automation bootstrap above.

For retrospective Learn-style reviews, the first visible outputs should be the automation file, memory status, and a bounded recent excerpt of `session_index.jsonl`. Use a recent tail excerpt for the visible third read so the transcript shows the current window without dumping the full ledger or reading a stale beginning slice. The full index can be parsed immediately afterward through the bounded resolver. If higher-priority host/runtime rules force a minimal skill load or a single named startup file first, satisfy only that requirement and immediately run this bootstrap. Record the forced read as precedence handling, not as avoidable discovery; still count any extra repo orientation beyond the required file as drift.

Do not start with repo orientation (`git status`, `pwd`, `ls`, README, OpenSpec, AGENTS), raw `$CODEX_HOME` probes, full-file `cat` of `session_index.jsonl`, broad `find ~/.codex`, broad `rg ~/.codex`, or prompt-fragment searches. If you started that way, restart from the canonical bootstrap and keep only findings reproduced from the bounded path.

If another skill suggests a different startup order for a session-review automation, follow this reference and report the mismatch as a skill-conflict finding. Support skills should defer to this reference instead of copying the bootstrap.

## Memory And Cutoff

Normalize `$CODEX_HOME` before any memory read. An unset `$CODEX_HOME` means use `~/.codex`; it is not evidence that Codex state lives elsewhere.

Derive cutoff candidates from each present structured memory field (`Processed window end` and `Last review`) plus prompt `Last run:`. Normalize and compare all present candidates, then use the newest timestamp. Memory is authoritative only when its structured checkpoint is newer; never let stale memory widen a review that has a newer prompt timestamp.

Example cutoff parser:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}" python3 - <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import os, re
mem = Path(os.environ["CODEX_HOME_RESOLVED"]) / "automations" / "<automation-id>" / "memory.md"
text = mem.read_text() if mem.exists() else ""
prompt_raw = "<prompt-last-run-or-empty>"

def parse_ts(raw):
    raw = str(raw).strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    m = re.match(r"^(.*\.)(\d+)([+-]\d\d:\d\d)$", raw)
    if m:
        raw = m.group(1) + m.group(2)[:6].ljust(6, "0") + m.group(3)
    dt = datetime.fromisoformat(raw)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

candidates = []
for field in ("Processed window end", "Last review"):
    match = re.search(rf"{re.escape(field)}:\s*(\S+)", text)
    if match:
        candidates.append(match.group(1))
if prompt_raw and not prompt_raw.startswith("<"):
    candidates.append(prompt_raw)
print(max(candidates, key=parse_ts) if candidates else "<missing-cutoff>")
PY
```

Once the newer cutoff is known, use that single timeline. Do not run duplicate extractors for both the prompt header and memory cutoff.

Capture the review-window end from the same `session_index.jsonl` snapshot used for candidate selection, normally the greatest indexed `updated_at` visible in that snapshot. Filter evidence to `(cutoff, review_window_end]`, exclude the current maintenance thread from substantive evidence, and persist that captured watermark as `Processed window end`. Keep the actual completion time in a separate `Run time` field. Never use end-of-run wall clock as the processed cursor: sessions can arrive between the index scan and memory write, and advancing to completion time would skip them on the next run.

On macOS, capture completion time with portable BSD/GNU forms such as `date -u '+%Y-%m-%dT%H:%M:%SZ'` for UTC and `date '+%Y-%m-%d %H:%M %Z'` for a local display value. Do not use GNU-only `date -Iseconds` or `date -Is`; a failed timestamp command is not a reason to rebuild or rerun the session resolver.

`session_index.updated_at` is a selection timestamp, not a reliable completion timestamp. A rollout can start before `review_window_end`, remain open at that boundary, and append later without receiving a newer index row. Keep one top-level memory field named `Carry-forward sessions:` containing the resolver's compact JSON array of `{id, line_count, last_activity_at}` checkpoints, or `[]`. The resolver always reselects those ids even when their index rows are older than the next cutoff; line counts prevent same-timestamp appended records from being lost.

For the full-index pass, prefer the bundled resolver and persist its one invocation atomically:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
MEMORY_PATH="$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md"
PROMPT_LAST_RUN='<prompt Last run value>'
RESOLVER_ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-session-review.XXXXXX")"
RESOLVER_MANIFEST="$RESOLVER_ARTIFACT_DIR/resolver.stdout.json"
RESOLVER_STDERR="$RESOLVER_ARTIFACT_DIR/resolver.stderr.log"
RESOLVER_STATUS="$RESOLVER_ARTIFACT_DIR/resolver.exit-status"
resolver_exit_status=0
(
  set --
  if [ -n "${CODEX_THREAD_ID:-}" ]; then
    set -- --exclude-session-id "$CODEX_THREAD_ID"
  fi
  python3 ~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/improve-skills/scripts/resolve_codex_sessions.py \
    --codex-home "$CODEX_HOME_RESOLVED" \
    --memory "$MEMORY_PATH" \
    --prompt-last-run "$PROMPT_LAST_RUN" \
    --recent 0 \
    --compact \
    "$@"
) >"$RESOLVER_MANIFEST" 2>"$RESOLVER_STDERR" || resolver_exit_status=$?
printf '%s\n' "$resolver_exit_status" >"$RESOLVER_STATUS"
printf 'resolver_artifact_dir=%s\nresolver_status=%s\n' \
  "$RESOLVER_ARTIFACT_DIR" "$resolver_exit_status"
```

Use a temporary-directory template that ends in `XXXXXX`, and use a non-special status name such as `resolver_exit_status`; `status` is read-only in zsh. The printed artifact directory is cross-call state: reuse that exact quoted path after a yield or in a later tool call instead of scanning `/tmp` for the newest match. If the status file is absent, the status is nonzero, or the manifest is invalid, do not rerun the resolver and do not advance memory; inspect only bounded persisted diagnostics.

The canonical flow uses `--recent 0` because the visible bootstrap already displayed the recent index excerpt; suppressing that duplicate changes only the resolver's output payload. `--compact` keeps the persistence fields and the exact session path/line-range manifest while omitting file-wide counters that are not needed for routing. The resolver still captures the full index once, normalizes the prompt and structured-memory cutoffs, drives selection and watermarking from that snapshot, resolves selected rollout paths, and inspects only rollout records timestamped at or before the captured window end. Each resolved session gets a `rollout_window.state`; `open` means it has non-metadata records without a final after the most recent user message, including a session resumed after an older final, while `metadata_only` means it has only `session_meta` in the captured window. Malformed, unreadable, or checkpoint-truncated ranges are unsafe and must not advance the cursor. Records already appended after the window are counted but left for a later review. For a carried session, inspect only its advertised inclusive `review_line_start` to `review_line_end` delta; the full prefix is checkpoint context, not new evidence.

If a selected rollout contains another `session_meta` whose id differs from the selected outer id, the resolver emits `embedded_session_history_detected` plus `rollout_window.embedded_session_metas`. This normally means a cloned or forked task imported an earlier task's history. Do not count file-wide tools, failures, finals, or skill reads as new evidence. Identify a substantive post-clone user turn that is not already present in the embedded task and review only that suffix. If there is no such turn, classify the selected row as `clone_only`, exclude it from session totals and candidate counters, and still consume its index timestamp in the cursor. The resolver reports provenance but does not guess the import boundary or silently discard the row.

Treat `window.cursor_to_persist` and `window.carry_forward_to_persist` as one persistence bundle:

1. Treat a non-empty exported `CODEX_THREAD_ID` as the exact current maintenance session id and pass it with `--exclude-session-id "$CODEX_THREAD_ID"` so it is removed before resolution and carry calculations. Reading that already-exported variable is part of the resolver invocation, not a reason to print `env`, inspect tool inventory, or open the current rollout. If `CODEX_THREAD_ID` is unset, remove only the positively identified current thread from the returned carry list during memory writing; do not infer by title or cwd alone.
2. Persist the remaining JSON array verbatim on the top-level `Carry-forward sessions:` line. Do not carry metadata-only sessions unless the resolver emitted them because later records were observed.
3. A carried open session that adds no lines during the next bounded pass is retired after that clean follow-up. If it grows, its checkpoint advances; if it completes, it is removed. This guarantees continuation across an active review boundary without turning the resolver into an unbounded watcher for arbitrarily old resumed tasks.

Advance the cursor only when `window.safe_to_persist` is `true` **and** update `Carry-forward sessions:` in the same memory patch. Exit `2` means the snapshot was readable but incomplete or ambiguous and must not advance memory; exit `1` means the input or cutoff was unusable. Do not rerun the resolver merely to obtain a different watermark.

## Candidate Session Selection

Prefer bounded sources in this order:

1. `~/.codex/session_index.jsonl` filtered by timestamp and rough project/thread relevance.
2. Matching recent day folders under `~/.codex/sessions/YYYY/MM/DD/`.
3. `~/.codex/archived_sessions/*<id>*.jsonl` for indexed ids missing from the day folders.
4. Bounded session-file parsing on `session_meta.payload.timestamp`, never raw filename timestamps alone.

Current `session_index.jsonl` may contain only `id`, `thread_name`, and `updated_at`; use it as a coarse recency index. Resolve authoritative `cwd`, `timestamp`, and id from `session_meta` inside the session file.

Do not assume the indexed id is the filename prefix. Codex Desktop rollout files are often named like `rollout-<timestamp>-<id>.jsonl`, so prefix patterns such as `<id>*.jsonl` and `*/<id>*.jsonl` can miss valid sessions. When resolving indexed ids, scan the bounded day folder and match either `*<id>*.jsonl` or, more robustly, `session_meta.payload.id` inside each file before falling back to `archived_sessions`.

Use the bundled resolver before opening raw rollout files or falling back to `rg` over session folders. It scans only day folders derived from the captured index rows, verifies `session_meta.payload.id`, uses an exact-id filename fallback for sessions created on a different day, and checks `archived_sessions` last. A missing or ambiguous selected rollout makes the cursor unsafe to persist.

For automation worktree runs, match both configured `cwds` and worktree variants such as `~/.codex/worktrees/*/<repo-tail>`.

Exclude sibling automation fan-out runs unless they provide direct evidence of automation drift or the same repeated skill weakness. If sibling runs already prove the pattern, stop there instead of widening into unrelated sessions.

Do not treat the current maintenance session as prior work evidence. If `CODEX_THREAD_ID` is unavailable, title/cwd similarity alone is insufficient to exclude a selected row or open its rollout merely to prove that it is maintenance traffic. Keep an uncertain row in carry-forward state and report current-thread identification as unresolved rather than risking exclusion of a sibling task.

## Timestamp Handling

The bundled resolver owns timestamp normalization, including variable fractional precision and trailing `Z`; the evidence helper consumes its advertised line ranges and does not recalculate the window. If a new timestamp or record shape breaks either helper, add a focused regression and patch that bundled script. Do not pivot to an inline parser, broad filesystem discovery, or a second live-index snapshot.

## JSONL Shape

Codex Desktop session files usually use:

- `session_meta` for authoritative session id, timestamp, and `cwd`
- `response_item` payloads for messages and function calls
- message payloads with `payload.type == "message"` and `payload.role`, sometimes nested under `payload.item`
- legacy function calls with `payload.type == "function_call"` and arguments in `payload.arguments`
- custom-recorder calls with `payload.type == "custom_tool_call"` and recorder input in `payload.input`; these often use recorder name `exec`, while the actionable nested tool appears as `tools.<tool_name>(...)` inside that input
- corresponding outputs with `payload.type` equal to `function_call_output` or `custom_tool_call_output`
- assistant final messages with `phase` equal to either `final` or `final_answer`; normalize both instead of sampling raw files when one spelling returns no finals

Do not rebuild these parsing rules in an inline script. Persist the successful resolver's compact JSON stdout once, then run the bundled evidence extractor:

```bash
RESOLVER_MANIFEST='<exact printed resolver_artifact_dir>/resolver.stdout.json'
python3 ~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/improve-skills/scripts/extract_codex_session_evidence.py \
  --manifest "$RESOLVER_MANIFEST"
```

For a project or privacy allowlist, pass each exact resolver-selected id with repeatable `--session-id <id>`. Unknown, duplicate, or unresolved requested ids fail closed; do not remove the filter and widen the read. The helper opens only resolved sessions and exact inclusive `review_line_start`/`review_line_end` ranges advertised by that manifest.

The helper emits at most one 240-character substantive user summary, 12 normalized tool names, and one 240-character final per session, with no tool arguments or outputs, and caps the combined JSON near 20,000 characters. It normalizes direct and nested payloads, unwraps custom-recorder tool names, strips injected wrappers, and aggregates repeated `<heartbeat>` control inputs by bounded automation/state/decision/status fields instead of rendering every heartbeat as a task. If the resolver reports embedded session metadata, the helper emits `manual_suffix_selection_required` without summarizing the imported content; identify the genuine post-clone suffix before counting evidence.

Do not rerun the resolver merely because its stdout was not persisted for the helper. Fix the same invocation's persistence before future runs and inspect exact advertised lines only when a compact summary already identifies a finding that needs a precise failure, command, or result.

## Automation-Instruction Findings

When the reviewed session is itself an automation run, decide whether the drift came from a weak reusable skill or from weak automation instructions.

Skills own reusable workflow knowledge. Automation prompts own task scope, project paths, state-file conventions, and required outputs. Automation prompts should not depend on a named task/todo tool without a fallback for runtimes where that tool is absent.

Do not auto-edit automations during an improve-skills run unless the user explicitly asked for it. Record high-value automation prompt changes as proposed diffs in the report and memory. If a task/todo tool is absent, persist the suggested action under `Pending automation prompt diffs` instead of searching the filesystem for a substitute tool.
