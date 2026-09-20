"""Read-only correspondence check for the second completion request."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
evidence = root / "evidence"
start = json.loads((evidence / "repeat-request-start.json").read_text())
skills = json.loads((evidence / "skill-source-manifest.json").read_text())
active_skill_hashes = {}
for name, record in skills["sources"].items():
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    assert actual == record["sha256"], "Active skill instructions changed: " + name
    active_skill_hashes[name] = actual

current_source_hashes = {
    name: hashlib.sha256((root / name).read_bytes()).hexdigest()
    for name in start["existing_source_hashes"]
}
assert current_source_hashes == start["existing_source_hashes"]
for name, digest in current_source_hashes.items():
    assert hashlib.sha256((evidence / "snapshots/final" / name).read_bytes()).hexdigest() == digest

unchanged_evidence = []
for name, expected in start["existing_evidence_hashes"].items():
    content = (evidence / name).read_bytes()
    if name == "events.jsonl":
        prior_lines = []
        for line in content.splitlines(keepends=True):
            event = json.loads(line)
            if event.get("utc") == start["utc"] and event.get("event") == start["event"]:
                break
            prior_lines.append(line)
        assert hashlib.sha256(b"".join(prior_lines)).hexdigest() == expected, "Prior events changed"
    else:
        assert hashlib.sha256(content).hexdigest() == expected, "Prior evidence changed: " + name
        unchanged_evidence.append(name)

prior_audit = json.loads(json.loads((evidence / "15-final-evidence-correspondence.json").read_text())["stdout"])
for name, expected in prior_audit["receipt_hashes"].items():
    assert hashlib.sha256((evidence / name).read_bytes()).hexdigest() == expected

print(json.dumps({
    "active_skill_sources_unchanged": active_skill_hashes,
    "source_and_contract_files_unchanged": current_source_hashes,
    "final_snapshot_matches": True,
    "prior_receipts_match_original_audit": True,
    "prior_evidence_files_byte_preserved": unchanged_evidence,
    "prior_event_prefix_byte_preserved": True,
    "note": "No application CLI tests or structural reviews executed by this integrity audit."
}, indent=2))
