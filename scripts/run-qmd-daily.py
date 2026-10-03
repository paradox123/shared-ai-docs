#!/usr/bin/env python3
"""Run the existing DanielsVault QMD collection and index maintenance only."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


RECONCILE = (
    Path(__file__).resolve().parents[2]
    / "danielsvault-rag"
    / "scripts"
    / "sync-qmd-collections.py"
)


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run_step(artifacts: Path, name: str, command: list[str], timeout: int) -> dict:
    try:
        with subprocess.Popen(
            command,
            cwd="/",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        ) as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                code = process.returncode
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                stdout, stderr = process.communicate()
                code = 124
                stderr += f"\nTimed out after {timeout} seconds.\n"
    except OSError as error:
        code = 127
        stdout = ""
        stderr = f"Could not start {command[0]}: {error}\n"
    (artifacts / f"{name}.stdout").write_text(stdout, encoding="utf-8")
    (artifacts / f"{name}.stderr").write_text(stderr, encoding="utf-8")
    return {"exitCode": code, "stdout": f"{name}.stdout", "stderr": f"{name}.stderr"}


def db_blocker() -> str | None:
    index_path = os.environ.get("INDEX_PATH")
    db = Path(index_path) if index_path else Path(
        os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    ) / "qmd" / "index.sqlite"
    directory = db.parent
    if db.exists() and not os.access(db, os.W_OK):
        return f"QMD database is not writable: {db}"
    if directory.exists() and not os.access(directory, os.W_OK):
        return f"QMD database directory is not writable: {directory}"
    if not directory.exists() and not os.access(directory.parent, os.W_OK):
        return f"QMD database directory cannot be created under: {directory.parent}"
    return None


def counts(status_text: str) -> dict:
    values = {}
    for key, pattern in {
        "documents": r"Total:\s+([\d,]+) files indexed",
        "vectors": r"Vectors:\s+([\d,]+) embedded",
        "pendingEmbeddings": r"Pending:\s+([\d,]+) need embedding",
    }.items():
        match = re.search(pattern, status_text)
        values[key] = int(match.group(1).replace(",", "")) if match else None
    if values["pendingEmbeddings"] is None and values["documents"] is not None:
        values["pendingEmbeddings"] = 0
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    args = parser.parse_args()
    artifacts = args.artifacts.expanduser().resolve()
    artifacts.mkdir(parents=True, exist_ok=False)
    print(json.dumps({"artifacts": str(artifacts)}), flush=True)
    report = {
        "ok": False,
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "artifacts": str(artifacts),
        "steps": {},
    }

    def finish(error: str | None = None) -> int:
        report["completedAt"] = datetime.now(timezone.utc).isoformat()
        if error:
            report["error"] = error
        write_json(artifacts / "report.json", report)
        print(json.dumps(report, ensure_ascii=False), flush=True)
        return 0 if report["ok"] else 1

    qmd = shutil.which("qmd")
    node = shutil.which("node")
    if not qmd or not node:
        return finish("QMD or Node.js is not available on PATH")
    blocker = db_blocker()
    if blocker:
        return finish(blocker)

    steps = report["steps"]
    steps["baselineStatus"] = run_step(artifacts, "baseline-status", [qmd, "status"], 120)
    if steps["baselineStatus"]["exitCode"] != 0:
        return finish("QMD baseline status failed")

    check_command = [sys.executable, str(RECONCILE)]
    steps["reconcileCheck"] = run_step(artifacts, "reconcile-check", check_command, 300)
    if steps["reconcileCheck"]["exitCode"] != 0:
        return finish("QMD collection reconciliation check failed")
    try:
        reconciliation = json.loads((artifacts / "reconcile-check.stdout").read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return finish("QMD collection reconciliation did not return valid JSON")
    if reconciliation.get("status") != "ok" or reconciliation.get("conflicts"):
        return finish("QMD collection reconciliation reported a conflict")
    report["collections"] = {
        "unchanged": len(reconciliation.get("unchanged", [])),
        "missing": reconciliation.get("missing", []),
    }
    if reconciliation.get("missing"):
        steps["reconcileApply"] = run_step(
            artifacts, "reconcile-apply", check_command + ["--apply"], 300
        )
        if steps["reconcileApply"]["exitCode"] != 0:
            return finish("QMD collection reconciliation apply failed")
        steps["reconcileVerify"] = run_step(
            artifacts, "reconcile-verify", check_command, 300
        )
        if steps["reconcileVerify"]["exitCode"] != 0:
            return finish("QMD collection reconciliation verification failed")
        try:
            verified = json.loads((artifacts / "reconcile-verify.stdout").read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return finish("QMD collection verification did not return valid JSON")
        if verified.get("status") != "ok" or verified.get("missing") or verified.get("conflicts"):
            return finish("QMD collections remain missing or conflicted after reconciliation")

    steps["update"] = run_step(artifacts, "update", [qmd, "update"], 3600)
    if steps["update"]["exitCode"] == 0:
        steps["embed"] = run_step(artifacts, "embed", [qmd, "embed"], 7200)
    else:
        steps["embed"] = {"skipped": "update failed"}
    steps["finalStatus"] = run_step(artifacts, "final-status", [qmd, "status"], 120)
    if steps["finalStatus"]["exitCode"] == 0:
        status_text = (artifacts / "final-status.stdout").read_text(encoding="utf-8")
        report["index"] = counts(status_text)
    report["ok"] = all(
        steps[name].get("exitCode") == 0 for name in ("update", "embed", "finalStatus")
    )
    return finish(None if report["ok"] else "QMD update, embedding, or final status failed")


if __name__ == "__main__":
    raise SystemExit(main())
