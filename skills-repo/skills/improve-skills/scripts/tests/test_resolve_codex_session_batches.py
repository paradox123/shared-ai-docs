"""Public CLI tests for bounded resolution of one frozen selection."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RESOLVER = Path(__file__).resolve().parents[1] / "resolve_codex_sessions.py"


class ResolverBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "codex"
        self.day = self.home / "sessions/2026/10/12"
        self.day.mkdir(parents=True)
        self.memory = self.root / "memory.md"
        self.memory.write_text("Processed window end: 2026-10-12T06:00:00Z\n")
        self.snapshot = self.root / "index.jsonl"

    def populate(self, count):
        rows = []
        for n in range(count):
            sid = f"session-{n:04}"
            stamp = "2026-10-12T07:00:00Z"
            rows.append({"id": sid, "updated_at": stamp})
            records = [
                {"timestamp": stamp, "type": "session_meta", "payload": {"id": sid, "cwd": str(self.root)}},
                {"timestamp": stamp, "type": "event_msg", "payload": {"type": "task_complete"}},
            ]
            (self.day / f"rollout-{sid}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        (self.home / "session_index.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))

    def run_cli(self, *extra):
        command = [sys.executable, str(RESOLVER), "--codex-home", str(self.home), "--memory", str(self.memory), "--compact", "--recent", "0", "--exclude-session-id", "maintenance", *extra]
        result = subprocess.run(command, text=True, capture_output=True, timeout=30)
        self.assertTrue(result.stdout, f"CLI emitted no manifest: {result.stderr}")
        return result.returncode, json.loads(result.stdout)

    def test_more_than_500_sessions_resolve_in_bounded_frozen_slices(self):
        self.populate(501)
        code, first = self.run_cli("--batch-offset", "0", "--max-sessions", "100", "--save-index-snapshot", str(self.snapshot))
        self.assertEqual(code, 0)
        self.assertEqual(len(first["sessions"]), 100)
        self.assertFalse(first["window"]["safe_to_persist"])
        self.assertEqual(first["batch"]["selection_count"], 501)
        digest = hashlib.sha256(self.snapshot.read_bytes()).hexdigest()
        (self.home / "session_index.jsonl").write_text("invalid new live index\n")
        all_ids = [r["id"] for r in first["sessions"]]
        for offset in (100, 200, 300, 400, 500):
            code, part = self.run_cli("--batch-offset", str(offset), "--max-sessions", "100", "--index-snapshot", str(self.snapshot), "--expected-index-sha256", digest)
            self.assertEqual(code, 0)
            self.assertEqual(part["batch"]["selection_plan_sha256"], first["batch"]["selection_plan_sha256"])
            self.assertLessEqual(len(part["sessions"]), 100)
            self.assertFalse(part["window"]["safe_to_persist"])
            all_ids.extend(r["id"] for r in part["sessions"])
        self.assertEqual(all_ids, [f"session-{n:04}" for n in range(501)])
        self.assertFalse(part["batch"]["has_more"])

    def test_legacy_call_keeps_total_limit_failure(self):
        self.populate(101)
        code, result = self.run_cli("--max-sessions", "100")
        self.assertEqual(code, 2)
        self.assertIn("too_many_sessions", [d["code"] for d in result["diagnostics"]])
        self.assertFalse(result["window"]["safe_to_persist"])
        self.assertEqual(result["sessions"], [])

    def test_old_carry_and_exclusion_survive_slice_boundaries(self):
        self.populate(3)
        self.memory.write_text("Processed window end: 2026-10-12T06:00:00Z\nCarry-forward sessions: " + json.dumps([{"id": "old-carried", "line_count": 0, "last_activity_at": "2026-10-11T07:00:00Z"}]) + "\n")
        (self.day / "rollout-old-carried.jsonl").write_text(json.dumps({"timestamp": "2026-10-11T07:00:00Z", "type": "session_meta", "payload": {"id": "old-carried", "cwd": str(self.root)}}) + "\n")
        code, first = self.run_cli("--batch-offset", "0", "--max-sessions", "1", "--exclude-session-id", "session-0001", "--save-index-snapshot", str(self.snapshot))
        self.assertEqual(code, 0)
        self.assertEqual(first["batch"]["selection_count"], 3)
        self.assertEqual(first["sessions"][0]["id"], "old-carried")
        self.assertEqual(first["sessions"][0]["selection_reasons"], ["carry_forward"])
        digest = hashlib.sha256(self.snapshot.read_bytes()).hexdigest()
        for offset, expected in [(1, "session-0000"), (2, "session-0002")]:
            code, result = self.run_cli("--batch-offset", str(offset), "--max-sessions", "1", "--exclude-session-id", "session-0001", "--index-snapshot", str(self.snapshot), "--expected-index-sha256", digest)
            self.assertEqual(code, 0)
            self.assertEqual(result["sessions"][0]["id"], expected)

    def test_empty_selection_requires_real_terminal_slice(self):
        self.populate(1)
        code, result = self.run_cli("--batch-offset", "0", "--exclude-session-id", "session-0000")
        self.assertEqual(code, 0)
        self.assertEqual(result["batch"]["selection_count"], 0)
        self.assertEqual(result["sessions"], [])
        self.assertFalse(result["batch"]["has_more"])
        self.assertFalse(result["window"]["safe_to_persist"])

    def test_unapproved_missing_carry_remains_unsafe_in_batch_mode(self):
        self.populate(1)
        self.memory.write_text("Processed window end: 2026-10-12T06:00:00Z\nCarry-forward sessions: " + json.dumps([{"id": "deleted-carried", "line_count": 2, "last_activity_at": "2026-10-11T07:00:00Z"}]) + "\n")
        code, result = self.run_cli("--batch-offset", "0", "--max-sessions", "1")
        self.assertEqual(code, 2)
        self.assertFalse(result["batch"]["safe_for_extraction"])
        self.assertEqual(result["sessions"][0]["status"], "missing")
        self.assertEqual(result["sessions"][0]["selection_reasons"], ["carry_forward"])


if __name__ == "__main__":
    unittest.main()
