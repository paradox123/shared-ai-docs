"""Verify correspondence of current source and existing completion evidence."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent.parent
evidence = root / "evidence"
manifest = json.loads((evidence / "candidate-after-dry.json").read_text())
actual = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
          for name in manifest["files"]}
assert actual == manifest["files"], "Current files differ from reviewed candidate"
identity = hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest()
assert identity == manifest["candidate_id"], "Candidate ID does not match files"
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
assert head == manifest["base"], "Fixture HEAD changed"

checks = ["10-after-dry-repair-tests.json", "11-after-dry-safe-import.json",
          "12-final-tracked-diff-check.json", "13-final-source-diff-check.json",
          "14-final-tests-diff-check.json"]
for name in checks:
    record = json.loads((evidence / name).read_text())
    assert record["files"] == actual, name + " has stale inputs"
    if "--no-index" in record["command"]:
        assert record["exit_code"] == 1 and not record["stdout"] and not record["stderr"], name
    else:
        assert record["exit_code"] == 0, name

reviewers = {"dry-delta-receipt.md": "/root/live_completion/dry_reviewer",
             "solid-receipt.md": "/root/live_completion/solid_reviewer",
             "kiss-receipt.md": "/root/live_completion/kiss_reviewer"}
receipt_hashes = {}
for name, reviewer in reviewers.items():
    content = (evidence / name).read_text()
    assert identity in content and reviewer in content and manifest["base"] in content, name
    for digest in actual.values():
        assert digest in content, name + " omits a source identity"
    receipt_hashes[name] = hashlib.sha256((evidence / name).read_bytes()).hexdigest()

print(json.dumps({"candidate_id": identity, "head": head, "files": actual,
                  "existing_checks_with_current_inputs": checks,
                  "reviewer_receipts": reviewers, "receipt_hashes": receipt_hashes,
                  "scope": "Content/evidence correspondence only; the coordinator separately reads coverage and findings."}, indent=2))
