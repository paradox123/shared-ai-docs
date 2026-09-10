from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


def append(path: Path, event: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
        handle.flush()


parser = argparse.ArgumentParser()
parser.add_argument("--worker-name", required=True)
parser.add_argument("--run-id", required=True)
parser.add_argument("--ledger", type=Path, required=True)
parser.add_argument("--start-run", action="store_true")
args = parser.parse_args()

base = {"runId": args.run_id, "worker": args.worker_name, "pid": os.getpid()}
append(args.ledger, {**base, "type": "worker-start"})
if args.start_run:
    append(args.ledger, {**base, "type": "run-start"})
    append(args.ledger, {**base, "type": "activity-enter", "activity": "checkpoint-one"})
    append(args.ledger, {**base, "type": "effect", "effect": "checkpoint-one"})
    append(args.ledger, {**base, "type": "activity-complete", "activity": "checkpoint-one"})
    append(args.ledger, {**base, "type": "activity-enter", "activity": "checkpoint-two"})
    time.sleep(60)
else:
    append(args.ledger, {**base, "type": "activity-enter", "activity": "checkpoint-two"})
    append(args.ledger, {**base, "type": "effect", "effect": "checkpoint-two"})
    append(args.ledger, {**base, "type": "activity-complete", "activity": "checkpoint-two"})
    append(args.ledger, {**base, "type": "run-complete"})
