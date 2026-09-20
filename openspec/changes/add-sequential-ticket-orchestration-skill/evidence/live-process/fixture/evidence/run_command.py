"""Capture actual fixture commands and outputs as process evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
label, *command = sys.argv[1:]
started = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, cwd=root, text=True, capture_output=True)
ended = datetime.now(timezone.utc).isoformat()
files = ["ticket_export.py", "test_ticket_export.py", "REQUIREMENTS.md", "AGENTS.md", "README.md"]
record = {
    "agent_id": "/root/live_completion", "started_utc": started, "ended_utc": ended,
    "cwd": str(root), "command": command, "exit_code": result.returncode,
    "stdout": result.stdout, "stderr": result.stderr,
    "files": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files},
}
path = root / "evidence" / (label + ".json")
path.write_text(json.dumps(record, indent=2) + "\n")
with (root / "evidence/events.jsonl").open("a") as stream:
    stream.write(json.dumps({"utc": ended, "agent_id": "/root/live_completion", "event": "Command completed", "command": command, "exit_code": result.returncode, "evidence": str(path.relative_to(root))}) + "\n")
print(json.dumps(record, indent=2))
sys.exit(result.returncode)
