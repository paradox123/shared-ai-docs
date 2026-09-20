import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "batch_state.py"


class BatchStateCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def document(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value))
        return path

    def run_cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def snapshot(self, **changes):
        return {"ticket": "01", "thread_id": "worker-01", "worktree": "/tmp/work-01",
                "branch": "codex/ticket-01", "target": "release/wiki", "status": "running",
                "wait_cursor": "cursor-a", "observed_at": "2026-09-18T10:00:00Z", **changes}

    def test_cursor_only_change_does_not_request_followup(self):
        previous = self.document("previous.json", self.snapshot())
        current = self.document("current.json", self.snapshot(wait_cursor="cursor-b", observed_at="later"))
        code, result = self.run_cli("compare", "--previous", previous, "--current", current)
        self.assertEqual((code, result["status"]), (0, "unchanged"))
        self.assertEqual(result["changed_fields"], [])

    def test_readiness_requires_matching_assignment_and_complete_observation(self):
        previous = self.document("previous.json", self.snapshot())
        for changes, expected in [({"status": "ready"}, "ready"),
                                  ({"status": "ready", "branch": "codex/other"}, "diverged"),
                                  ({"status": "ready", "thread_id": ""}, "blocked"),
                                  ({"status": "blocked", "blocker": "check failed"}, "blocked")]:
            with self.subTest(changes=changes):
                current = self.document("current.json", self.snapshot(**changes))
                _, result = self.run_cli("compare", "--previous", previous, "--current", current)
                self.assertEqual(result["status"], expected)
                self.assertNotIn("check failed", json.dumps(result))

    def test_malformed_observation_status_returns_structured_blocker(self):
        previous = self.document("previous.json", self.snapshot())
        for status in ([], {}, None, 5):
            with self.subTest(status=status):
                current = self.document("current.json", self.snapshot(status=status))
                code, result = self.run_cli("compare", "--previous", previous, "--current", current)
                self.assertEqual((code, result["status"]), (2, "blocked"))
                self.assertEqual(result["reason"], "invalid observation status")

    def test_checkpoint_preserves_other_tickets_and_pending_actions(self):
        ledger = self.root / "memory.json"
        initial = self.document("initial.json", {
            "batch": {"id": "batch-01", "repository": "/tmp/repo", "target": "release/wiki"},
            "tickets": {"01": {"phase": "implementing", "pending_action": {"operation": "send"}},
                        "02": {"phase": "verifying", "custom_evidence": ["proof.md"]}},
            "custom_provenance": "user request"})
        code, result = self.run_cli("checkpoint", "--ledger", ledger, "--patch", initial,
                                    "--expect-revision", 0)
        self.assertEqual((code, result.get("revision")), (0, 1))
        patch = self.document("patch.json", {"tickets": {"01": {"wait_cursor": "new-cursor"}}})
        _, result = self.run_cli("checkpoint", "--ledger", ledger, "--patch", patch,
                                "--expect-revision", 1)
        saved = json.loads(ledger.read_text())
        self.assertEqual(result["revision"], 2)
        self.assertEqual(saved["tickets"]["01"]["pending_action"], {"operation": "send"})
        self.assertEqual(saved["tickets"]["02"]["custom_evidence"], ["proof.md"])
        self.assertEqual(saved["custom_provenance"], "user request")

    def test_stale_locked_or_invalid_checkpoint_leaves_ledger_untouched(self):
        ledger = self.document("memory.json", {
            "schema_version": 1, "revision": 4,
            "batch": {"id": "batch-01", "repository": "/tmp/repo", "target": "release/wiki"},
            "tickets": {"01": {"pending_action": {"operation": "merge", "uncertain": True}}}})
        original = ledger.read_bytes()
        for revision, patch_value in [(3, {"tickets": {"01": {"phase": "done"}}}),
                                       (4, {"batch": {"target": "main"}}),
                                       (4, {"tickets": None}), (4, {"revision": 50})]:
            with self.subTest(revision=revision, patch=patch_value):
                ledger.write_bytes(original)
                patch = self.document("patch.json", patch_value)
                code, result = self.run_cli("checkpoint", "--ledger", ledger, "--patch", patch,
                                            "--expect-revision", revision)
                self.assertIn(code, (2, 3))
                self.assertIn(result["status"], ("blocked", "error"))
                self.assertEqual(ledger.read_bytes(), original)
        ledger.write_bytes(original)
        lock = self.root / "memory.json.lock"
        lock.write_text("another writer")
        patch = self.document("patch.json", {"tickets": {"01": {"phase": "done"}}})
        code, result = self.run_cli("checkpoint", "--ledger", ledger, "--patch", patch,
                                    "--expect-revision", 4)
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(ledger.read_bytes(), original)
        self.assertEqual(lock.read_text(), "another writer")

    def test_manifest_identifies_explicit_artifacts_by_bytes(self):
        (self.root / "evidence.txt").write_bytes(b"abc")
        files = self.document("files.json", ["evidence.txt"])
        code, result = self.run_cli("manifest", "--root", self.root, "--files", files)
        self.assertEqual(code, 0)
        self.assertEqual(result.get("files"), {"evidence.txt": {
            "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            "size": 3}})

    def test_manifest_verification_detects_changed_and_missing_artifacts(self):
        artifact = self.root / "evidence.txt"
        artifact.write_bytes(b"abc")
        files = self.document("files.json", ["evidence.txt"])
        _, value = self.run_cli("manifest", "--root", self.root, "--files", files)
        proof = self.document("manifest.json", value)
        code, result = self.run_cli("verify", "--root", self.root, "--manifest", proof)
        self.assertEqual((code, result["status"]), (0, "ready"))
        artifact.write_bytes(b"different evidence")
        code, result = self.run_cli("verify", "--root", self.root, "--manifest", proof)
        self.assertEqual((code, result["status"]), (2, "diverged"))
        self.assertEqual(result["mismatches"], ["evidence.txt"])
        artifact.unlink()
        code, result = self.run_cli("verify", "--root", self.root, "--manifest", proof)
        self.assertEqual((code, result["status"]), (2, "diverged"))
        self.assertEqual(result["mismatches"], ["evidence.txt"])

    def test_manifest_rejects_empty_duplicate_escaping_and_symlink_paths(self):
        (self.root / "evidence.txt").write_bytes(b"abc")
        (self.root / "alias.txt").symlink_to(self.root / "evidence.txt")
        for names in [[], ["evidence.txt", "evidence.txt"], ["../outside"],
                      [str(self.root / "evidence.txt")], ["alias.txt"], ["."], [123]]:
            with self.subTest(names=names):
                files = self.document("files.json", names)
                code, result = self.run_cli("manifest", "--root", self.root, "--files", files)
                self.assertEqual((code, result["status"]), (3, "error"))

    def test_retention_is_verified_repeatable_and_never_overwrites_different_evidence(self):
        source = self.root / "worker"
        source.mkdir()
        (source / "evidence.txt").write_bytes(b"abc")
        files = self.document("files.json", ["evidence.txt"])
        _, value = self.run_cli("manifest", "--root", source, "--files", files)
        proof = self.document("manifest.json", value)
        destination = self.root / "durable"
        for _ in range(2):
            code, result = self.run_cli("retain", "--root", source, "--manifest", proof,
                                        "--destination", destination)
            self.assertEqual((code, result["status"]), (0, "ready"))
            self.assertEqual((destination / "evidence.txt").read_bytes(), b"abc")
        (destination / "evidence.txt").write_bytes(b"other accepted proof")
        code, result = self.run_cli("retain", "--root", source, "--manifest", proof,
                                    "--destination", destination)
        self.assertEqual((code, result["status"]), (2, "diverged"))
        self.assertEqual((destination / "evidence.txt").read_bytes(), b"other accepted proof")
        code, _ = self.run_cli("retain", "--root", source, "--manifest", proof,
                               "--destination", source / "inside")
        self.assertEqual(code, 3)
        self.assertFalse((source / "inside").exists())

    def test_malformed_existing_ledger_is_not_repaired_by_overwriting_it(self):
        for invalid_batch in (None, [], "not a batch"):
            with self.subTest(batch=invalid_batch):
                ledger = self.document("memory.json", {"schema_version": 1, "revision": 1,
                                                        "batch": invalid_batch, "tickets": {}})
                original = ledger.read_bytes()
                patch = self.document("patch.json", {
                    "batch": {"id": "batch-01", "repository": "/tmp/repo", "target": "release/wiki"}})
                code, result = self.run_cli("checkpoint", "--ledger", ledger, "--patch", patch,
                                            "--expect-revision", 1)
                self.assertEqual((code, result["status"]), (3, "error"))
                self.assertEqual(ledger.read_bytes(), original)

    def test_concurrent_checkpoints_keep_exactly_one_writer(self):
        ledger = self.document("memory.json", {"schema_version": 1, "revision": 1,
            "batch": {"id": "batch-01", "repository": "/tmp/repo", "target": "release/wiki"},
            "tickets": {"01": {"phase": "implementing"}}})
        processes = []
        for phase in ("verifying", "blocked"):
            patch = self.document(phase + ".json", {"tickets": {"01": {"phase": phase}}})
            processes.append(subprocess.Popen([sys.executable, str(SCRIPT), "checkpoint", "--ledger",
                str(ledger), "--patch", str(patch), "--expect-revision", "1"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        responses = [process.communicate() for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [0, 2], responses)
        saved = json.loads(ledger.read_text())
        self.assertEqual(saved["revision"], 2)
        self.assertIn(saved["tickets"]["01"]["phase"], {"verifying", "blocked"})

    def test_changed_source_never_publishes_retained_evidence(self):
        source = self.root / "worker"
        source.mkdir()
        artifact = source / "evidence.txt"
        artifact.write_bytes(b"abc")
        files = self.document("files.json", ["evidence.txt"])
        _, value = self.run_cli("manifest", "--root", source, "--files", files)
        proof = self.document("manifest.json", value)
        artifact.write_bytes(b"new unreviewed contents")
        destination = self.root / "durable"
        code, result = self.run_cli("retain", "--root", source, "--manifest", proof,
                                    "--destination", destination)
        self.assertEqual((code, result["status"]), (2, "diverged"))
        self.assertFalse(destination.exists())

    def test_invalid_json_and_unsupported_manifest_have_structured_errors(self):
        malformed = self.root / "malformed.json"
        malformed.write_text("{broken")
        code, result = self.run_cli("manifest", "--root", self.root, "--files", malformed)
        self.assertEqual((code, result["status"]), (3, "error"))
        for value in ([], {}, {"schema_version": 1, "files": {}},
                      {"schema_version": 2, "files": {"proof": {"size": 1, "sha256": "a" * 64}}}):
            proof = self.document("manifest.json", value)
            code, result = self.run_cli("verify", "--root", self.root, "--manifest", proof)
            self.assertEqual((code, result["status"]), (3, "error"))


if __name__ == "__main__":
    unittest.main()
