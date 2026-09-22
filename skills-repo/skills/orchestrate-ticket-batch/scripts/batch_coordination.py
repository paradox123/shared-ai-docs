"""Managed local bookkeeping; never executes external tools."""

import copy
import json
import os
from pathlib import Path
import shutil
import uuid

from batch_state import atomic_json, classify_event, file_digest, read_json


class Blocked(Exception):
    pass


CLEANUP = ("evidence-preserved", "worktree-removed", "local-branch-removed", "remote-branch-removed", "worker-archived")


def report(packet_path, result_path, outcome, content_ref, target_ref=None):
    packet = read_json(packet_path)
    if not isinstance(packet, dict):
        raise ValueError("invalid command packet")
    identity = {key: packet.get(key) for key in ("batch_id", "ticket", "thread_id", "host_id", "request_id")}
    event = {**identity, "event_seq": 1, "phase": packet.get("phase"), "status": outcome,
             "result_path": str(result_path.resolve()), "content_ref": content_ref}
    classify_event(identity, event)
    if packet["phase"] in {"integrating", "delivering"} and outcome == "ready":
        event["target_ref"] = require_text(target_ref, "tested target revision")
    directory = Path(require_text(packet.get("report_dir"), "report directory"))
    if not directory.is_absolute() or directory.is_symlink():
        raise ValueError("absolute non-symlink report directory required")
    coordinator = require_object(packet.get("coordinator"), "coordinator")
    for key in ("thread_id", "host_id"):
        require_text(coordinator.get(key), key)
    evidence(str(result_path.resolve()))
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / ".report.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {"status": "blocked", "reason": "report locked; reconcile writer"}
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(str(os.getpid()))
        sequences = [int(p.stem) for p in directory.glob("*.json") if p.stem.isdigit()]
        sequence = max(sequences, default=0) + 1
        result_copy = directory / f"{sequence:06d}-result{result_path.suffix}"
        if result_copy.exists() or result_copy.is_symlink():
            raise Blocked("unpublished report result exists; reconcile interrupted report")
        with result_path.open("rb") as source, result_copy.open("xb") as dest:
            shutil.copyfileobj(source, dest)
            dest.flush()
            os.fsync(dest.fileno())
        event.update(event_seq=sequence, result_path=str(result_copy), result_sha256=file_digest(result_copy)["sha256"])
        event_path = directory / f"{sequence:06d}.json"
        atomic_json(event_path, event)
        return {"status": "ready", "event": str(event_path),
                "callback": {**coordinator, "prompt": "Worker result available: " + str(event_path)}}
    except Blocked as error:
        return {"status": "blocked", "reason": str(error)}
    finally:
        lock.unlink()


def require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value


def require_object(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def count(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"invalid {name}")
    return value


def load(path):
    data = read_json(path)
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise ValueError("managed schema 2 required; existing batches need explicit adoption")
    initialize(data)  # Validate the immutable configuration without altering persisted state.
    count(data.get("revision"), "revision", 1)
    if "integration" not in data or (data["integration"] is not None and data["integration"] not in data["tickets"]):
        raise ValueError("invalid integration holder")
    for row in data["tickets"].values():
        if ({"request", "pending", "receipt", "worker", "history", "delivered"} - set(row)
                or type(row.get("slot")) is not bool or type(row.get("delivered")) is not bool
                or not isinstance(row.get("history"), list)):
            raise ValueError("incomplete managed ticket")
        require_text(row.get("phase"), "phase")
        count(row.get("allowance"), "allowance")
        if row["request"]:
            packet = require_object(row["request"], "request")
            for field in ("packet", "id", "phase", "sha256"):
                require_text(packet.get(field), field)
            if file_digest(Path(packet["packet"]))["sha256"] != packet["sha256"]:
                raise Blocked("command packet was changed")
    validate_capacity(data)
    return data


def initialize(operation):
    batch = operation.get("batch")
    if not isinstance(batch, dict):
        raise ValueError("batch required")
    for key in ("id", "repository", "target", "authority"):
        require_text(batch.get(key), key)
    coordinator = require_object(batch.get("coordinator"), "coordinator")
    for key in ("thread_id", "host_id"):
        require_text(coordinator.get(key), key)
    tickets = operation.get("tickets")
    if not isinstance(tickets, dict) or not tickets:
        raise ValueError("nonempty ticket map required")
    limits = require_object(operation.get("limits", {"tickets": 3, "subagents": 3}), "limits")
    for key in ("tickets", "subagents"):
        count(limits.get(key), key, 1 if key == "tickets" else 0)
    continuation = require_object(operation.get("continuation", {"mode": "active-wait"}), "continuation")
    if require_text(continuation.get("mode"), "continuation mode") not in {"active-wait", "callback", "heartbeat", "manual"}:
        raise ValueError("unknown continuation mode")
    if continuation["mode"] in {"callback", "heartbeat"}:
        require_text(continuation.get("evidence"), "wake/authorization evidence")
    rows = {}
    for key, definition in tickets.items():
        require_text(key, "ticket")
        if not isinstance(definition, dict):
            raise ValueError("invalid ticket definition")
        for field in ("depends_on", "conflicts"):
            links = definition.get(field, [])
            if not isinstance(links, list) or any(not isinstance(item, str) or not item or item == key for item in links):
                raise ValueError("invalid ticket dependencies/conflicts")
        rows[key] = {**definition, "phase": "queued", "slot": False, "allowance": 0,
                     "worker": None, "request": None, "receipt": None,
                     "pending": None, "history": [], "delivered": False}
    return {"schema_version": 2, "revision": 0, "batch": batch, "tickets": rows,
            "limits": limits, "continuation": continuation, "integration": None}


def evidence(value):
    path = Path(require_text(value, "evidence path"))
    if not path.is_absolute() or not path.is_file():
        raise ValueError("existing absolute evidence file required")
    return {"path": str(path), **file_digest(path)}


def ticket(data, operation):
    key = operation.get("ticket")
    if not isinstance(key, str) or key not in data["tickets"]:
        raise ValueError("unknown ticket")
    return key, data["tickets"][key]


def eligibility(data, key):
    row = data["tickets"][key]
    if any(not data["tickets"].get(dep, {}).get("delivered") for dep in row.get("depends_on", [])):
        raise Blocked("prerequisite not delivered")
    for other, candidate in data["tickets"].items():
        if other == key or candidate["phase"] == "queued" or candidate["delivered"]:
            continue
        if other in row.get("conflicts", []) or key in candidate.get("conflicts", []):
            raise Blocked("declared conflict with undelivered worker")


def validate_capacity(data):
    for field, limit in (("slot", "tickets"), ("allowance", "subagents")):
        if sum(row[field] for row in data["tickets"].values()) > data["limits"][limit]:
            raise Blocked(f"{limit} capacity exceeded")


def checked_receipt(row):
    receipt = row["receipt"]
    if not receipt:
        return None
    if file_digest(Path(receipt["path"]))["sha256"] != receipt["sha256"]:
        raise Blocked("consumed event was changed")
    return read_json(Path(receipt["path"]))


def ready_evidence(row, operation):
    report = checked_receipt(row)
    if not report or report["status"] != "ready":
        raise Blocked("current ready report required")
    if operation.get("content_ref") != report["content_ref"]:
        raise Blocked("decision content does not match reported revision")
    if file_digest(Path(report["result_path"]))["sha256"] != report["result_sha256"]:
        raise Blocked("reported result was changed")
    return {"content_ref": report["content_ref"], "evidence": evidence(operation.get("evidence"))}


def prepare(data, operation, path):
    key, row = ticket(data, operation)
    if row["pending"]:
        raise Blocked("reconcile pending dispatch before preparing another command")
    phase = require_text(operation.get("phase"), "phase")
    if (row["phase"], phase) not in {("queued", "registering"), ("registering", "implementing"),
                                    ("implementing", "verifying"), ("awaiting-integration", "integrating"),
                                    ("integrating", "integrating"), ("integrating", "delivering"),
                                    ("cleanup", "cleanup"), ("implementing", "repairing"),
                                    ("verifying", "repairing"), ("repairing", "repairing"),
                                    ("repairing", "verifying"), ("integrating", "repairing")}:
        raise Blocked("phase transition not permitted")
    if phase == "repairing":
        if not checked_receipt(row) or operation.get("quiescent") is not True:
            raise Blocked("repair requires inspected report and quiescent worker")
        row["repair_evidence"] = evidence(operation.get("evidence"))
        row["repair_rounds"] = row.get("repair_rounds", 0) + 1
    if phase == "verifying":
        row["acceptance"] = ready_evidence(row, operation)
    if phase == "integrating":
        if data["integration"] not in {None, key}:
            raise Blocked("another ticket holds integration")
        if row["phase"] == "integrating":
            ready_evidence(row, operation)
        require_text(operation.get("target_ref"), "target revision")
        data["integration"] = key
    if phase == "delivering":
        accepted = ready_evidence(row, operation)
        report = checked_receipt(row)
        target = require_text(operation.get("target_ref"), "target revision")
        if data["integration"] != key or report.get("target_ref") != target or operation.get("current_target_ref") != target:
            raise Blocked("merge grant requires held integration and current tested target")
        row["acceptance"] = {**accepted, "target_ref": target}
    if phase == "cleanup":
        step = require_text(operation.get("step"), "cleanup step")
        done = row.get("cleanup", {})
        if step not in CLEANUP or step in done:
            raise Blocked("unknown or already completed cleanup step")
        if step != "evidence-preserved" and "evidence-preserved" not in done:
            raise Blocked("retain evidence before cleanup")
        if step == "worker-archived" and any(item not in done for item in CLEANUP[:-1]):
            raise Blocked("verify resource cleanup before archival")
        evidence(operation.get("evidence"))
    if phase != "registering" and not row["worker"]:
        raise Blocked("confirmed worker required")
    if not row["slot"] and phase != "cleanup":
        eligibility(data, key)
    instruction = require_text(operation.get("instruction"), "instruction")
    allowance = count(operation.get("allowance", row["allowance"]), "allowance")
    if phase != "registering" and allowance != row["allowance"]:
        if operation.get("quiescent") is not True:
            raise Blocked("changed allowance requires confirmed quiescence")
        row["capacity_evidence"] = evidence(operation.get("evidence"))
    if phase == "cleanup" and allowance:
        raise Blocked("cleanup holds no subagent allowance")
    request_id = uuid.uuid4().hex
    packet_path = path.parent / (path.name + ".commands") / (request_id + ".json")
    packet = {"batch_id": data["batch"]["id"], "ticket": key, "request_id": request_id,
              "phase": phase, "target": data["batch"]["target"], "repository": data["batch"]["repository"],
              "authority": data["batch"]["authority"], "coordinator": data["batch"]["coordinator"],
              "allowance": allowance, "instruction": instruction,
              "actor": "coordinator" if phase in {"registering", "cleanup"} else "worker",
              "report_dir": str(path.parent / (path.name + ".reports") / request_id),
              **(row["worker"] or {})}
    for name in ("content_ref", "target_ref"):
        if name in operation:
            packet[name] = operation[name]
    if phase == "cleanup":
        packet["step"] = operation["step"]
    skill = Path(__file__).resolve().parents[1]
    policy = read_json(skill / "assets" / "phase-messages.json")[phase].replace("{skills}", str(skill.parent))
    header = {key: value for key, value in packet.items() if key not in {"instruction", "report_dir"}}
    packet["message"] = (json.dumps(header, ensure_ascii=False) + "\n\n" + instruction + "\n\n" + policy)
    if packet["actor"] == "worker":
        packet["message"] += (f"\n\nErgebnismeldung: {skill / 'references' / 'worker-events.md'}. "
                              f"Nutze das Auftragspaket {packet_path}; reserviertes Unteragentenlimit "
                              f"einschließlich verschachtelter Agenten: {allowance}. Keine periodischen Statusmeldungen. "
                              "Nach ready keine weiteren Kandidatenänderungen bis zum Folgeauftrag.")
    if row["request"]:
        row["history"].append({"request": row["request"], "receipt": row["receipt"]})
    row.update(phase=phase, slot=phase != "cleanup", allowance=allowance, receipt=None, report=None,
               request={"id": request_id, "packet": str(packet_path), "phase": phase},
               pending={"request_id": request_id, "outcome": "prepared"})
    if phase == "cleanup":
        row["request"]["step"] = operation["step"]
        row["request"]["preflight"] = evidence(operation["evidence"])
    return packet_path, packet


def advance(data, operation):
    key, row = ticket(data, operation)
    if row["pending"]:
        raise Blocked("reconcile pending dispatch before changing phase")
    if row["phase"] == "verifying" and operation.get("phase") == "awaiting-integration":
        row["acceptance"] = ready_evidence(row, operation)
        row["completion_record"] = evidence(operation.get("completion_record"))
        row["phase"] = "awaiting-integration"
    elif row["phase"] == "delivering" and operation.get("phase") == "confirming":
        ready_evidence(row, operation)
        report = checked_receipt(row)
        accepted = row["acceptance"]
        if (report["content_ref"] != accepted["content_ref"] or report.get("target_ref") != accepted["target_ref"]):
            raise Blocked("merge report differs from granted head/target")
        row["phase"] = "confirming"
    elif row["phase"] == "confirming" and operation.get("phase") == "cleanup":
        delivery = require_object(operation.get("delivery", {}), "delivery")
        if (operation.get("quiescent") is not True or delivery.get("closed") is not True
                or delivery.get("target") != data["batch"]["target"]
                or delivery.get("content_ref") != row["acceptance"]["content_ref"]):
            raise Blocked("verified delivery, closure and quiescence required")
        for name in ("merge_ref", "pr"):
            require_text(delivery.get(name), name)
        row["delivery"] = {**delivery, "evidence": evidence(operation.get("evidence"))}
        row.update(delivered=True, phase="cleanup", slot=False, allowance=0)
        if data["integration"] == key:
            data["integration"] = None
    elif row["phase"] == "cleanup" and operation.get("phase") == "done":
        if any(step not in row.get("cleanup", {}) for step in CLEANUP):
            raise Blocked("cleanup remains incomplete")
        row["done_evidence"] = evidence(operation.get("evidence"))
        row["phase"] = "done"
    else:
        raise Blocked("phase transition not permitted")


def record(data, operation):
    _, row = ticket(data, operation)
    pending = row["pending"]
    if not pending or operation.get("request_id") != pending["request_id"]:
        raise Blocked("no matching pending command")
    outcome = require_text(operation.get("outcome"), "dispatch outcome")
    if outcome not in {"unknown", "confirmed", "not-sent"}:
        raise ValueError("outcome must be confirmed, not-sent or unknown")
    proof = evidence(operation.get("evidence"))
    if outcome == "confirmed" and row["phase"] == "registering":
        worker = operation.get("worker")
        if not isinstance(worker, dict):
            raise ValueError("directly verified worker required; provisional IDs do not suffice")
        for key in ("thread_id", "host_id", "worktree", "branch", "base_sha"):
            require_text(worker.get(key), key)
        worker = {key: worker[key] for key in ("thread_id", "host_id", "worktree", "branch", "base_sha")}
        if not Path(worker["worktree"]).is_absolute() or worker["branch"] == data["batch"]["target"]:
            raise Blocked("isolated worktree and owned working branch required")
        for other in data["tickets"].values():
            assigned = other["worker"]
            if assigned and (assigned["branch"] == worker["branch"]
                             or Path(assigned["worktree"]).resolve() == Path(worker["worktree"]).resolve()
                             or (assigned["thread_id"], assigned["host_id"]) == (worker["thread_id"], worker["host_id"])):
                raise Blocked("worker identity, branch or worktree already assigned")
        row["worker"] = worker
    row["request"]["dispatch"] = {"outcome": outcome, "evidence": proof}
    if outcome == "confirmed":
        row["pending"] = None
        if row["phase"] == "cleanup":
            row.setdefault("cleanup", {})[row["request"]["step"]] = proof
    else:
        pending.update(outcome=outcome, evidence=proof)


def consume(data, operation, path):
    key, row = ticket(data, operation)
    if not row["request"] or not row["worker"]:
        raise Blocked("confirmed assignment required")
    event_path = Path(require_text(operation.get("event"), "event path"))
    event = read_json(event_path)
    assignment = {"batch_id": data["batch"]["id"], "ticket": key,
                  "request_id": row["request"]["id"],
                  **{name: row["worker"][name] for name in ("thread_id", "host_id")}}
    classified = classify_event(assignment, event, checked_receipt(row))
    if classified["status"] == "blocked":
        raise Blocked(classified["reason"])
    if classified["status"] in {"duplicate", "stale"}:
        return classified["status"], None
    if row["pending"]:
        raise Blocked("reconcile dispatch before consuming a new report")
    if event["phase"] != row["request"]["phase"]:
        raise Blocked("event phase differs from assigned phase")
    result_proof = evidence(event["result_path"])
    if result_proof["sha256"] != event.get("result_sha256"):
        raise Blocked("reported result was changed or lacks hash")
    row["receipt"] = evidence(str(event_path.resolve()))
    row["report_status"] = event["status"]
    row["report"] = {field: event[field] for field in
                     ("status", "content_ref", "result_path", "target_ref", "event_seq") if field in event}
    publication = None
    if "next" in operation:
        decision = operation["next"]
        if not isinstance(decision, dict):
            raise ValueError("next decision must be an object")
        if "instruction" in decision:
            publication = prepare(data, {**decision, "ticket": key}, path)
        else:
            advance(data, {**decision, "ticket": key})
    return "new", publication


def capacity(data, operation):
    key, row = ticket(data, operation)
    if row["pending"] or operation.get("quiescent") is not True:
        raise Blocked("capacity changes require reconciled dispatch and quiescence")
    if row["phase"] in {"queued", "done", "cleanup"}:
        raise Blocked("capacity belongs to active workers")
    parked = operation.get("parked", not row["slot"])
    if type(parked) is not bool:
        raise ValueError("parked must be boolean")
    allowance = count(operation.get("allowance", row["allowance"]), "allowance")
    if parked and allowance:
        raise Blocked("parked workers must release subagent allowance")
    if data["integration"] == key and parked:
        if (operation.get("grant_revoked") is not True or operation.get("mutation_absent") is not True
                or row["phase"] not in {"integrating", "delivering"}):
            raise Blocked("integration holder must reconcile/cancel grant before parking")
        data["integration"] = None
        row["request"]["cancelled"] = True
        row["phase"] = "awaiting-integration"
    if not parked and not row["slot"]:
        eligibility(data, key)
    row["capacity_evidence"] = evidence(operation.get("evidence"))
    row.update(slot=not parked, allowance=allowance)


def observe(data, operation):
    _, row = ticket(data, operation)
    facts = require_object(operation.get("facts", {}), "facts")
    if set(facts) - {"wait_cursor", "usage", "scope_notes", "deferred_closeout", "role_profile"}:
        raise ValueError("observation cannot modify workflow state")
    proof = evidence(operation.get("evidence"))
    row.setdefault("facts", {}).update(facts)
    row["observation_evidence"] = proof
    if "continuation" in operation:
        continuation = require_object(operation["continuation"], "continuation")
        mode = require_text(continuation.get("mode"), "continuation mode")
        if mode not in {"active-wait", "callback", "heartbeat", "manual"}:
            raise ValueError("unknown continuation mode")
        if mode in {"callback", "heartbeat"}:
            require_text(continuation.get("evidence"), "wake/authorization evidence")
        data["continuation"] = {**continuation, "proof": proof}


def context(data):
    rows = {}
    for key, row in data["tickets"].items():
        next_action = ("reconcile-dispatch" if row["pending"] else
                       "prepare-registering" if row["phase"] == "queued" else
                       "parked" if not row["slot"] and not row["delivered"] else
                       "prepare-implementing" if row["phase"] == "registering" else
                       "prepare-integration" if row["phase"] == "awaiting-integration" else
                       "verify-remote-delivery" if row["phase"] == "confirming" else
                       "cleanup" if row["phase"] == "cleanup" else
                       "done" if row["phase"] == "done" else
                       "inspect-evidence" if row["receipt"] else "wait-for-report")
        rows[key] = {"phase": row["phase"], "next": next_action,
                     "slot": row["slot"], "allowance": row["allowance"], "worker": row["worker"],
                     "report": row.get("report"), "receipt": row["receipt"], "pending": row["pending"]}
        if row["phase"] == "queued":
            try:
                eligibility(data, key)
                if sum(ticket["slot"] for ticket in data["tickets"].values()) >= data["limits"]["tickets"]:
                    raise Blocked("ticket capacity exhausted")
            except Blocked as error:
                rows[key].update(next="wait-eligibility", reason=str(error),
                                 depends_on=row.get("depends_on", []), conflicts=row.get("conflicts", []))
        if row["phase"] == "awaiting-integration" and row["slot"] and data["integration"] not in {None, key}:
            rows[key].update(next="wait-integration", reason="another ticket holds integration")
        for name in ("acceptance", "completion_record", "delivery", "cleanup", "repair_rounds", "facts"):
            if name in row:
                rows[key][name] = row[name]
        if row["request"]:
            rows[key]["request_id"] = row["request"]["id"]
            rows[key]["packet"] = row["request"]["packet"]
    return {"status": "ready", "revision": data["revision"], "target": data["batch"]["target"],
            "available": {"tickets": data["limits"]["tickets"] - sum(r["slot"] for r in data["tickets"].values()),
                          "subagents": data["limits"]["subagents"] - sum(r["allowance"] for r in data["tickets"].values())},
            "integration": data["integration"], "continuation": data["continuation"], "tickets": rows}


def status(path):
    try:
        return context(load(path))
    except Blocked as error:
        return {"status": "blocked", "reason": str(error)}


def coordinate(path, expected, operation):
    if path.is_symlink():
        raise ValueError("ledger must not be a symbolic link")
    if not isinstance(operation, dict):
        raise ValueError("operation must be an object")
    lock = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {"status": "blocked", "reason": "ledger locked; reconcile owner"}
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(str(os.getpid()))
        current = load(path) if path.exists() else None
        if (current["revision"] if current else 0) != expected:
            raise Blocked("stale revision")
        data = copy.deepcopy(current)
        publication = None
        if operation.get("op") == "init":
            if current is not None:
                raise Blocked("batch already initialized")
            data = initialize(operation)
        elif current is None:
            raise ValueError("initialize the batch first")
        elif operation.get("op") == "prepare":
            publication = prepare(data, operation, path.resolve())
        elif operation.get("op") == "record":
            record(data, operation)
        elif operation.get("op") == "advance":
            advance(data, operation)
        elif operation.get("op") == "capacity":
            capacity(data, operation)
        elif operation.get("op") == "observe":
            observe(data, operation)
        elif operation.get("op") == "consume":
            event_status, publication = consume(data, operation, path.resolve())
            if event_status != "new":
                return {**context(current), "event_status": event_status}
        else:
            raise ValueError("unknown coordination operation")
        validate_capacity(data)
        if publication:
            packet_path, packet = publication
            packet_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(packet_path, packet)
            data["tickets"][operation["ticket"]]["request"]["sha256"] = file_digest(packet_path)["sha256"]
        data["revision"] += 1
        atomic_json(path, data)
        result = context(data)
        if publication:
            result["packet"] = str(publication[0])
        return result
    except Blocked as error:
        return {"status": "blocked", "reason": str(error)}
    finally:
        lock.unlink()
