#!/usr/bin/env python3
"""Local bookkeeping for ticket batches; never dispatches or delivers work."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


def read_json(path):
    return json.loads(path.read_text())


def file_digest(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {"sha256": digest.hexdigest(), "size": size}


def artifact_path(root, name):
    if (not isinstance(name, str) or not name or "\\" in name or name == "."
            or Path(name).is_absolute() or ".." in Path(name).parts or str(Path(name)) != name):
        raise ValueError("artifact names must be normalized relative file paths")
    root = root.resolve(strict=True)
    path = root
    for part in Path(name).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("artifact paths must not contain symbolic links")
    if path.exists() and not path.is_file():
        raise ValueError("artifact must be a regular file")
    return path


def manifest(root, files):
    if (not isinstance(files, list) or not files or not all(isinstance(name, str) for name in files)
            or len(files) != len(set(files))):
        raise ValueError("file list must be nonempty and unique")
    return {"status": "ready", "schema_version": 1,
            "files": {name: file_digest(artifact_path(root, name)) for name in sorted(files)}}


def verify(root, proof):
    if (not isinstance(proof, dict) or proof.get("schema_version") != 1
            or not isinstance(proof.get("files"), dict) or not proof["files"]):
        raise ValueError("invalid manifest")
    mismatches = []
    for name, expected in proof["files"].items():
        if (not isinstance(expected, dict) or type(expected.get("size")) is not int
                or expected["size"] < 0 or not isinstance(expected.get("sha256"), str)
                or len(expected["sha256"]) != 64
                or any(char not in "0123456789abcdef" for char in expected["sha256"])):
            raise ValueError("invalid manifest file digest")
        path = artifact_path(root, name)
        if not path.exists() or file_digest(path) != expected:
            mismatches.append(name)
    return {"status": "diverged" if mismatches else "ready", "mismatches": sorted(mismatches)}


def retain(root, proof, destination):
    root = root.resolve(strict=True)
    if destination.is_symlink():
        raise ValueError("retention destination must not be a symbolic link")
    destination = destination.resolve()
    if destination == root or root in destination.parents or destination in root.parents:
        raise ValueError("retention destination must be outside the source tree")
    checked = verify(root, proof)
    if checked["status"] != "ready":
        return checked
    if destination.exists():
        checked = verify(destination, proof)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        lock = destination.with_name(destination.name + ".lock")
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return {"status": "blocked", "reason": "retention locked; reconcile owner before retry"}
        try:
            os.close(descriptor)
            if destination.exists():
                checked = verify(destination, proof)
            else:
                with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".retention-") as directory:
                    staged = Path(directory) / "evidence"
                    staged.mkdir()
                    for name in proof["files"]:
                        target = staged / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(artifact_path(root, name), target)
                    checked = verify(staged, proof)
                    if checked["status"] == "ready":
                        staged.rename(destination)
        finally:
            lock.unlink()
    if checked["status"] == "ready":
        checked.update(destination=str(destination), file_count=len(proof["files"]))
    return checked


def merge_patch(current, patch):
    result = dict(current)
    for key, value in patch.items():
        result[key] = (merge_patch(result[key], value)
                       if isinstance(value, dict) and isinstance(result.get(key), dict) else value)
    return result


def atomic_json(path, value):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def validate_ledger(value):
    if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
            or value["schema_version"] != 1 or type(value.get("revision")) is not int
            or value["revision"] < 0):
        raise ValueError("unsupported ledger; explicit adoption required")
    batch = value.get("batch")
    if not isinstance(batch, dict) or any(
            not isinstance(batch.get(key), str) or not batch[key].strip()
            for key in ("id", "repository", "target")):
        raise ValueError("batch id, repository and explicit target are required")
    tickets = value.get("tickets")
    if not isinstance(tickets, dict) or any(not isinstance(row, dict) for row in tickets.values()):
        raise ValueError("tickets must be an object of ticket records")


def checkpoint(path, patch, expected):
    if not isinstance(patch, dict) or {"revision", "schema_version"}.intersection(patch):
        raise ValueError("patch must be an object without managed revision/schema fields")
    if path.is_symlink():
        raise ValueError("ledger must not be a symbolic link")
    lock = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {"status": "blocked", "reason": "ledger locked; reconcile owner before retry"}
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(str(os.getpid()))
        if path.exists():
            current = read_json(path)
            validate_ledger(current)
        else:
            current = {"schema_version": 1, "revision": 0}
        if current["revision"] != expected:
            return {"status": "blocked", "reason": "stale revision", "revision": current["revision"]}
        updated = merge_patch(current, patch)
        validate_ledger(updated)
        if "batch" in current and any(current["batch"].get(key) != updated["batch"][key]
                                       for key in ("id", "repository", "target")):
            raise ValueError("batch identity cannot be rebound")
        updated["revision"] = current["revision"] + 1
        atomic_json(path, updated)
        return {"status": "ready", "revision": updated["revision"]}
    finally:
        lock.unlink()


def compare_snapshots(previous, current):
    identity = {"ticket", "thread_id", "worktree", "branch", "target"}
    for snapshot in (previous, current):
        if not isinstance(snapshot, dict) or any(
                not isinstance(snapshot.get(key), str) or not snapshot[key].strip()
                for key in identity):
            return {"status": "blocked", "reason": "incomplete assignment"}
        if (not isinstance(snapshot.get("status"), str)
                or snapshot["status"] not in {"running", "ready", "blocked", "error"}):
            return {"status": "blocked", "reason": "invalid observation status"}
    ignored = {"wait_cursor", "observed_at"}
    changed = sorted(key for key in previous.keys() | current.keys()
                     if key not in ignored and previous.get(key) != current.get(key))
    status = "unchanged"
    if changed:
        if identity.intersection(changed):
            status = "diverged"
        elif current["status"] in {"blocked", "error"} or current.get("pending_action"):
            status = "blocked"
        else:
            status = "ready" if current["status"] == "ready" else "diverged"
    return {"status": status, "changed_fields": changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--previous", type=Path, required=True)
    compare.add_argument("--current", type=Path, required=True)
    checkpoint_parser = commands.add_parser("checkpoint")
    checkpoint_parser.add_argument("--ledger", type=Path, required=True)
    checkpoint_parser.add_argument("--patch", type=Path, required=True)
    checkpoint_parser.add_argument("--expect-revision", type=int, required=True)
    for name in ("manifest", "verify", "retain"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--files" if name == "manifest" else "--manifest", type=Path, required=True)
        if name == "retain":
            command.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "compare":
            result = compare_snapshots(read_json(args.previous), read_json(args.current))
        elif args.command == "checkpoint":
            result = checkpoint(args.ledger, read_json(args.patch), args.expect_revision)
        elif args.command == "manifest":
            result = manifest(args.root, read_json(args.files))
        elif args.command == "verify":
            result = verify(args.root, read_json(args.manifest))
        else:
            result = retain(args.root, read_json(args.manifest), args.destination)
    except (OSError, ValueError) as error:
        result = {"status": "error", "reason": str(error)}
    print(json.dumps(result))
    return 3 if result["status"] == "error" else 2 if result["status"] in {"blocked", "diverged"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
