import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "batch_state.py"


class WorkerEventCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.assignment = {"batch_id": "batch-a", "ticket": "11", "thread_id": "worker-11",
                           "host_id": "local", "request_id": "implement-1"}
        self.event = {**self.assignment, "event_seq": 1, "phase": "implementing",
                      "status": "ready", "result_path": "/evidence/11/result.md",
                      "content_ref": "manifest-sha256:example"}

    def classify(self, event, previous=None, assignment=None):
        values = {"assignment": self.assignment if assignment is None else assignment, "event": event}
        if previous is not None:
            values["previous"] = previous
        args = []
        original = {}
        for name, value in values.items():
            path = self.root / (name + ".json")
            path.write_text(json.dumps(value))
            original[path] = path.read_bytes()
            args.extend(["--" + name, str(path)])
        result = subprocess.run([sys.executable, str(SCRIPT), "classify-event", *args],
                                capture_output=True, text=True)
        self.assertTrue(result.stdout.strip(), result.stderr)
        for path, data in original.items():
            self.assertEqual(path.read_bytes(), data)
        return result.returncode, json.loads(result.stdout)

    def test_first_event_is_new_without_granting_acceptance(self):
        code, result = self.classify(self.event)
        self.assertEqual((code, result["status"]), (0, "new"))
        self.assertEqual(set(result), {"status"})

    def test_redelivery_is_duplicate_but_changed_payload_is_blocked(self):
        for changes, expected in [({}, "duplicate"), ({"sent_at": "later"}, "duplicate"),
                                  ({"content_ref": "different-revision"}, "blocked")]:
            with self.subTest(changes=changes):
                code, result = self.classify({**self.event, **changes}, self.event)
                self.assertEqual(result["status"], expected)
                self.assertEqual(code, 2 if expected == "blocked" else 0)

    def test_stale_requests_and_sequences_never_advance_current_work(self):
        previous = {**self.event, "event_seq": 2}
        cases = [({**self.event, "request_id": "implement-old"}, previous, "stale"),
                 (self.event, previous, "stale"),
                 ({**self.event, "event_seq": 3}, previous, "new"),
                 ({**self.event, "event_seq": 4}, previous, "blocked"),
                 ({**self.event, "event_seq": 2}, None, "blocked")]
        for event, receipt, expected in cases:
            with self.subTest(event=event, receipt=receipt):
                code, result = self.classify(event, receipt)
                self.assertEqual((code, result["status"]),
                                 (2 if expected == "blocked" else 0, expected))

    def test_foreign_assignment_and_wrong_previous_receipt_are_blocked(self):
        for field in ("batch_id", "ticket", "thread_id", "host_id"):
            with self.subTest(field=field):
                _, result = self.classify({**self.event, field: "other"}, self.event)
                self.assertEqual(result["status"], "blocked")
                self.assertNotIn("other", json.dumps(result))
        _, result = self.classify(self.event, {**self.event, "request_id": "old"})
        self.assertEqual(result["status"], "blocked")

    def test_malformed_envelopes_and_unbound_ready_results_are_rejected(self):
        invalid = [None, [], {}, {**self.event, "event_seq": True},
                   {**self.event, "event_seq": 0}, {**self.event, "event_seq": "1"},
                   {**self.event, "status": "running"}, {**self.event, "status": []},
                   {**self.event, "result_path": ""}, {**self.event, "phase": " "},
                   {**self.event, "content_ref": None}]
        for event in invalid:
            with self.subTest(event=event):
                code, result = self.classify(event)
                self.assertEqual((code, result["status"]), (3, "error"))
        code, result = self.classify(self.event, assignment={})
        self.assertEqual((code, result["status"]), (3, "error"))

    def test_blocker_needs_no_candidate_revision_and_does_not_echo_details(self):
        event = {**self.event, "status": "blocked", "reason": "private detail"}
        del event["content_ref"]
        code, result = self.classify(event)
        self.assertEqual((code, result["status"]), (0, "new"))
        self.assertNotIn("private detail", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
