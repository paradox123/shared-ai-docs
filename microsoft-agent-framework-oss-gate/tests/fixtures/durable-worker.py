from __future__ import annotations

import argparse
import json
import os
import signal
import socket
from pathlib import Path


def append(path: Path, event: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


parser = argparse.ArgumentParser()
parser.add_argument("--gate-worker-name", required=True)
parser.add_argument("--gate-phase", required=True)
parser.add_argument("--gate-port", type=int, required=True)
parser.add_argument("--gate-orchestration-id", required=True)
parser.add_argument("--gate-ledger", type=Path, required=True)
args = parser.parse_args()


def event(kind: str, **values: object) -> dict[str, object]:
    return {
        "type": kind,
        "worker": args.gate_worker_name,
        "pid": os.getpid(),
        "orchestrationId": args.gate_orchestration_id,
        "port": args.gate_port,
        **values,
    }


listener = socket.socket()
listener.bind(("127.0.0.1", args.gate_port))
listener.listen()
append(args.gate_ledger, event("worker-start"))
if args.gate_phase == "before-termination":
    append(args.gate_ledger, event("effect", effect="before-worker-stop"))
    append(
        args.gate_ledger,
        event("checkpoint", checkpoint="before-worker-termination"),
    )
    signal.pause()
else:
    prior = [
        json.loads(line)
        for line in args.gate_ledger.read_text(encoding="utf-8").splitlines()
    ]
    if not any(
        item.get("type") == "checkpoint"
        and item.get("checkpoint") == "before-worker-termination"
        and item.get("orchestrationId") == args.gate_orchestration_id
        for item in prior
    ):
        raise SystemExit(3)
    append(args.gate_ledger, event("effect", effect="after-worker-stop"))
    append(
        args.gate_ledger,
        event("checkpoint", checkpoint="continued-after-worker-termination"),
    )
    append(args.gate_ledger, event("complete"))
