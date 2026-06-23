# Codex Desktop Session Review

Use this reference only for Codex Desktop automation/session reviews, Learn-style fan-out reviews, or named skill-quality reviews that require Codex JSONL evidence. The goal is to keep `SKILL.md` compact while preserving the fragile startup and parsing details in one place.

## Startup Order

When the prompt supplies `Automation ID:`, `Automation memory:`, `Automation:`, or `Last run:`, treat those as authoritative inputs. Do not rediscover them with `rg`, `find`, `ls`, or home-directory probes.

Canonical bootstrap:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
sed -n '1,220p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml"
test -f "$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md" && \
  sed -n '1,260p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md" || \
  echo "(missing memory)"
sed -n '1,220p' "$CODEX_HOME_RESOLVED/session_index.jsonl"
```

If higher-priority instructions require loading this skill's `SKILL.md`, a repo startup file such as `VAULT_AGENT_STRUCTURE.md`, or both before task work, keep those reads minimal and isolated. The safe opening sequence is:

1. Read only the required skill/startup file(s); do not include memory, Codex-home probes, `find`, `rg`, `pwd`, `git`, or session reads in that same tool batch.
2. Read this reference.
3. Run the canonical automation bootstrap above.

For retrospective Learn-style reviews, the first visible outputs should be the automation file, memory status, and `session_index.jsonl`. If higher-priority host/runtime rules force a minimal skill load or a single named startup file first, satisfy only that requirement and immediately run this bootstrap. Record the forced read as precedence handling, not as avoidable discovery; still count any extra repo orientation beyond the required file as drift.

Do not start with repo orientation (`git status`, `pwd`, `ls`, README, OpenSpec, AGENTS), raw `$CODEX_HOME` probes, broad `find ~/.codex`, broad `rg ~/.codex`, or prompt-fragment searches. If you started that way, restart from the canonical bootstrap and keep only findings reproduced from the bounded path.

If another skill suggests a different startup order for a session-review automation, follow this reference and report the mismatch as a skill-conflict finding. Support skills should defer to this reference instead of copying the bootstrap.

## Memory And Cutoff

Normalize `$CODEX_HOME` before any memory read. An unset `$CODEX_HOME` means use `~/.codex`; it is not evidence that Codex state lives elsewhere.

If the normalized automation memory exists, derive the cutoff from `Processed window end` or `Last review` before parsing `session_index.jsonl`. Use a prompt-level `Last run:` only as a fallback.

Example cutoff parser:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}" python3 - <<'PY'
from pathlib import Path
import os, re
mem = Path(os.environ["CODEX_HOME_RESOLVED"]) / "automations" / "<automation-id>" / "memory.md"
text = mem.read_text() if mem.exists() else ""
m = re.search(r"Processed window end:\s*(\S+)", text) or re.search(r"Last review:\s*(\S+)", text)
print(m.group(1) if m else "<prompt-last-run-fallback>")
PY
```

Once the memory-backed cutoff is known, use that single timeline. Do not run duplicate extractors for both the prompt header and memory cutoff.

## Candidate Session Selection

Prefer bounded sources in this order:

1. `~/.codex/session_index.jsonl` filtered by timestamp and rough project/thread relevance.
2. Matching recent day folders under `~/.codex/sessions/YYYY/MM/DD/`.
3. `~/.codex/archived_sessions/*<id>*.jsonl` for indexed ids missing from the day folders.
4. Bounded session-file parsing on `session_meta.payload.timestamp`, never raw filename timestamps alone.

Current `session_index.jsonl` may contain only `id`, `thread_name`, and `updated_at`; use it as a coarse recency index. Resolve authoritative `cwd`, `timestamp`, and id from `session_meta` inside the session file.

Do not assume the indexed id is the filename prefix. Codex Desktop rollout files are often named like `rollout-<timestamp>-<id>.jsonl`, so prefix patterns such as `<id>*.jsonl` and `*/<id>*.jsonl` can miss valid sessions. When resolving indexed ids, scan the bounded day folder and match either `*<id>*.jsonl` or, more robustly, `session_meta.payload.id` inside each file before falling back to `archived_sessions`.

For automation worktree runs, match both configured `cwds` and worktree variants such as `~/.codex/worktrees/*/<repo-tail>`.

Exclude sibling automation fan-out runs unless they provide direct evidence of automation drift or the same repeated skill weakness. If sibling runs already prove the pattern, stop there instead of widening into unrelated sessions.

## Timestamp Handling

Normalize timestamps once in the bounded extractor. Fractional precision may vary.

```python
import re
from datetime import datetime

def parse_ts(raw):
    raw = raw.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    m = re.match(r"^(.*\.)(\d+)([+-]\d\d:\d\d)$", raw)
    if m:
        raw = m.group(1) + m.group(2)[:6].ljust(6, "0") + m.group(3)
    return datetime.fromisoformat(raw)
```

Do not pivot to broad filesystem discovery just because a first parser missed timestamp precision or record shape. Patch the bounded parser and rerun it.

## JSONL Shape

Codex Desktop session files usually use:

- `session_meta` for authoritative session id, timestamp, and `cwd`
- `response_item` payloads for messages and function calls
- message payloads with `payload.type == "message"` and `payload.role`
- function calls with `payload.type == "function_call"` or nested recorder variants

Skip wrapper-only user messages such as `<environment_context>...</environment_context>` and injected `# AGENTS.md instructions for ...` blocks when deriving the substantive user request.

Starter extractor:

```bash
python3 - <<'PY'
import json, glob, os

for path in sorted(glob.glob(os.path.expanduser("~/.codex/sessions/YYYY/MM/DD/*.jsonl"))):
    meta = None
    first_user = None
    calls = []
    with open(path) as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("type") == "session_meta":
                meta = obj["payload"]
                continue
            if obj.get("type") != "response_item":
                continue
            payload = obj.get("payload", {})
            if payload.get("type") == "message" and payload.get("role") == "user" and not first_user:
                texts = [item.get("text", "") for item in payload.get("content", []) if item.get("type") == "input_text"]
                text = " ".join(texts).strip()
                if text.startswith("<environment_context>") or text.startswith("# AGENTS.md instructions for "):
                    continue
                first_user = text[:220]
            elif payload.get("type") == "function_call":
                calls.append(payload.get("name"))
    if meta:
        print(meta.get("timestamp"), meta.get("cwd"), first_user, calls[:12], path)
PY
```

When a bounded extractor already prints session meta, first substantive prompt, and function-call names, do not open raw rollout files one by one unless you need a quoted evidence snippet.

If shell values such as `CODEX_HOME_RESOLVED`, `AUTOMATION_ID`, or cutoff are needed inside Python, export them or invoke Python as `VAR=value python3 ...`. A plain shell assignment before `python3 - <<'PY'` is not visible in `os.environ`.

## Automation-Instruction Findings

When the reviewed session is itself an automation run, decide whether the drift came from a weak reusable skill or from weak automation instructions.

Skills own reusable workflow knowledge. Automation prompts own task scope, project paths, state-file conventions, and required outputs. Automation prompts should not depend on a named task/todo tool without a fallback for runtimes where that tool is absent.

Do not auto-edit automations during an improve-skills run unless the user explicitly asked for it. Record high-value automation prompt changes as proposed diffs in the report and memory. If a task/todo tool is absent, persist the suggested action under `Pending automation prompt diffs` instead of searching the filesystem for a substitute tool.
