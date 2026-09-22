import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "batch_state.py"


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.ledger = self.root / "batch.json"
        self.revision = 0
        self.config = {
            "op": "init", "batch": {"id": "audit", "repository": str(self.root),
            "target": "release/audit", "authority": "user-request-1",
            "coordinator": {"thread_id": "coordinator", "host_id": "local"}},
            "tickets": {"11": {}, "12": {}, "13": {}},
            "limits": {"tickets": 2, "subagents": 2},
            "continuation": {"mode": "active-wait"}}

    def cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def operate(self, operation, expected=None):
        source = self.root / "operation.json"
        source.write_text(json.dumps(operation))
        code, result = self.cli("coordinate", "--ledger", self.ledger,
                                "--expect-revision", self.revision if expected is None else expected,
                                "--input", source)
        if code == 0 and "revision" in result:
            self.revision = result["revision"]
        return code, result

    def snapshot(self):
        code, result = self.cli("status", "--ledger", self.ledger)
        self.assertEqual(code, 0, result)
        return result

    def proof(self, name="proof.md", content="Observed and checked by coordinator"):
        path = self.root / name
        path.write_text(content)
        return str(path)

    def start_worker(self, key="11", allowance=1):
        code, result = self.operate({"op": "prepare", "ticket": key, "phase": "registering",
                                    "instruction": "Create isolated worker", "allowance": allowance})
        self.assertEqual(code, 0, result)
        packet = json.loads(Path(result["packet"]).read_text())
        worker = {"thread_id": "worker-" + key, "host_id": "local", "worktree": str(self.root / ("worktree-" + key)),
                  "branch": "codex/ticket-" + key, "base_sha": "target-a"}
        self.assertEqual(self.operate({"op": "record", "ticket": key, "request_id": packet["request_id"],
                         "outcome": "confirmed", "worker": worker, "evidence": self.proof()})[0], 0)
        code, result = self.operate({"op": "prepare", "ticket": key, "phase": "implementing",
                                    "instruction": "Implement and prove behavior"})
        self.assertEqual(code, 0, result)
        self.confirm_packet(result["packet"], key)
        return result["packet"]

    def confirm_packet(self, path, key="11"):
        packet = json.loads(Path(path).read_text())
        code, result = self.operate({"op": "record", "ticket": key, "request_id": packet["request_id"],
                                    "outcome": "confirmed", "evidence": self.proof()})
        self.assertEqual(code, 0, result)

    def worker_report(self, packet, content="revision-a", outcome="ready", target=None):
        args = ["report", "--packet", packet, "--result", self.proof("result.md", "Expected 3; observed 3"),
                "--status", outcome]
        if content:
            args.extend(["--content-ref", content])
        if target:
            args.extend(["--target-ref", target])
        return self.cli(*args)

    def complete_worker(self, key="11"):
        packet = self.start_worker(key)
        _, report = self.worker_report(packet)
        code, result = self.operate({"op": "consume", "ticket": key, "event": report["event"],
                                    "next": {"phase": "verifying", "instruction": "Complete scoped review",
                                             "content_ref": "revision-a", "evidence": self.proof()}})
        self.assertEqual(code, 0, result)
        self.confirm_packet(result["packet"], key)
        _, report = self.worker_report(result["packet"])
        code, result = self.operate({"op": "consume", "ticket": key, "event": report["event"],
                                    "next": {"phase": "awaiting-integration", "content_ref": "revision-a",
                                             "evidence": self.proof(), "completion_record": self.proof("completion.md")}})
        self.assertEqual(code, 0, result)

    def test_integration_is_exclusive_and_merge_requires_current_tested_target(self):
        self.operate(self.config)
        self.complete_worker("11")
        self.complete_worker("12")
        code, prepared = self.operate({"op": "prepare", "ticket": "11", "phase": "integrating",
                                      "instruction": "Prepare candidate; no merge", "target_ref": "target-a"})
        self.assertEqual(code, 0, prepared)
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "prepare", "ticket": "12", "phase": "integrating",
                                    "instruction": "Prepare", "target_ref": "target-a"})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)
        self.confirm_packet(prepared["packet"])
        _, report = self.worker_report(prepared["packet"], target="target-a")
        self.operate({"op": "consume", "ticket": "11", "event": report["event"]})
        decision = {"op": "prepare", "ticket": "11", "phase": "delivering", "instruction": "Merge exact head",
                    "content_ref": "revision-a", "target_ref": "target-a", "current_target_ref": "target-b",
                    "evidence": self.proof()}
        before = self.ledger.read_bytes()
        code, result = self.operate(decision)
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)
        decision["current_target_ref"] = "target-a"
        code, result = self.operate(decision)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["integration"], "11")
        grant = json.loads(Path(result["packet"]).read_text())
        self.assertEqual((grant["content_ref"], grant["target_ref"]), ("revision-a", "target-a"))

    def test_delivery_releases_capacity_only_after_verification_and_cleanup_is_resumable(self):
        self.config["tickets"]["12"]["depends_on"] = ["11"]
        self.operate(self.config)
        self.complete_worker()
        _, prepared = self.operate({"op": "prepare", "ticket": "11", "phase": "integrating",
                                    "instruction": "Prepare", "target_ref": "target-a"})
        self.confirm_packet(prepared["packet"])
        _, report = self.worker_report(prepared["packet"], target="target-a")
        _, grant = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                "next": {"phase": "delivering", "instruction": "Merge",
                                         "content_ref": "revision-a", "target_ref": "target-a",
                                         "current_target_ref": "target-a", "evidence": self.proof()}})
        self.confirm_packet(grant["packet"])
        _, report = self.worker_report(grant["packet"], target="target-a")
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                    "next": {"phase": "confirming", "content_ref": "revision-a", "evidence": self.proof()}})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["integration"], "11")
        self.assertTrue(result["tickets"]["11"]["slot"])
        code, result = self.operate({"op": "advance", "ticket": "11", "phase": "cleanup",
                                    "evidence": self.proof(), "quiescent": True,
                                    "delivery": {"target": "release/audit", "content_ref": "revision-a",
                                                 "merge_ref": "merge-a", "pr": "PR-11", "closed": True}})
        self.assertEqual(code, 0, result)
        self.assertIsNone(result["integration"])
        self.assertFalse(result["tickets"]["11"]["slot"])
        self.assertEqual(result["tickets"]["11"]["allowance"], 0)
        self.start_worker("12")
        code, result = self.operate({"op": "advance", "ticket": "11", "phase": "done", "evidence": self.proof()})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        for step in ("evidence-preserved", "worktree-removed", "local-branch-removed", "remote-branch-removed", "worker-archived"):
            code, action = self.operate({"op": "prepare", "ticket": "11", "phase": "cleanup",
                                         "step": step, "instruction": "Perform verified " + step, "evidence": self.proof()})
            self.assertEqual(code, 0, action)
            self.assertEqual(json.loads(Path(action["packet"]).read_text())["actor"], "coordinator")
            self.confirm_packet(action["packet"])
        code, result = self.operate({"op": "advance", "ticket": "11", "phase": "done", "evidence": self.proof()})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["tickets"]["11"]["next"], "done")

    def test_worker_report_copies_result_and_allocates_immutable_sequences(self):
        self.operate(self.config)
        packet = self.start_worker()
        code, result = self.worker_report(packet)
        self.assertEqual(code, 0, result)
        event_path = Path(result["event"])
        original = event_path.read_bytes()
        first = json.loads(original)
        self.assertEqual(first["event_seq"], 1)
        self.assertEqual(first["thread_id"], "worker-11")
        (self.root / "result.md").write_text("Changed working result")
        self.assertEqual(Path(first["result_path"]).read_text(), "Expected 3; observed 3")
        code, second = self.worker_report(packet, "revision-b")
        self.assertEqual(code, 0, second)
        self.assertEqual(json.loads(Path(second["event"]).read_text())["event_seq"], 2)
        self.assertEqual(event_path.read_bytes(), original)
        self.assertEqual(result["callback"]["thread_id"], "coordinator")

    def test_consumption_and_followup_are_atomic_and_redelivery_preserves_pending_send(self):
        self.operate(self.config)
        packet = self.start_worker()
        _, report = self.worker_report(packet)
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                    "next": {"phase": "verifying", "instruction": "Run change-accepted",
                                             "content_ref": "wrong-revision", "evidence": self.proof()}})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                    "next": {"phase": "verifying", "instruction": "Run change-accepted",
                                             "content_ref": "revision-a", "evidence": self.proof()}})
        self.assertEqual(code, 0, result)
        current = self.snapshot()
        self.assertEqual(current["tickets"]["11"]["phase"], "verifying")
        self.assertEqual(current["tickets"]["11"]["next"], "reconcile-dispatch")
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"]})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["event_status"], "stale")
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(result["tickets"]["11"]["next"], "reconcile-dispatch")

    def test_ready_report_requires_decision_and_modified_evidence_blocks_consumption(self):
        self.operate(self.config)
        packet = self.start_worker()
        _, report = self.worker_report(packet)
        event = json.loads(Path(report["event"]).read_text())
        Path(event["result_path"]).write_text("tampered")
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"]})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)
        Path(event["result_path"]).write_text("Expected 3; observed 3")
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"]})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["tickets"]["11"]["phase"], "implementing")
        self.assertEqual(result["tickets"]["11"]["next"], "inspect-evidence")

    def test_prepared_command_survives_unknown_send_and_binds_verified_worker(self):
        self.operate(self.config)
        code, result = self.operate({"op": "prepare", "ticket": "11", "phase": "registering",
                                    "instruction": "Create isolated worker for ticket 11", "allowance": 1})
        self.assertEqual(code, 0, result)
        packet = json.loads(Path(result["packet"]).read_text())
        request = packet["request_id"]
        self.assertEqual(packet["target"], "release/audit")
        self.assertEqual(packet["allowance"], 1)
        code, result = self.operate({"op": "record", "ticket": "11", "request_id": request,
                                    "outcome": "unknown", "evidence": self.proof()})
        self.assertEqual(code, 0, result)
        self.assertEqual(self.snapshot()["tickets"]["11"]["next"], "reconcile-dispatch")
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "prepare", "ticket": "11", "phase": "registering",
                                    "instruction": "Try again"})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)
        worker = {"thread_id": "worker-11", "host_id": "local", "worktree": str(self.root / "worktree-11"),
                  "branch": "codex/ticket-11", "base_sha": "target-a"}
        code, result = self.operate({"op": "record", "ticket": "11", "request_id": request,
                                    "outcome": "confirmed", "worker": worker, "evidence": self.proof()})
        self.assertEqual(code, 0, result)
        code, result = self.operate({"op": "prepare", "ticket": "11", "phase": "implementing",
                                    "instruction": "Implement and prove behavior"})
        self.assertEqual(code, 0, result)
        assigned = json.loads(Path(result["packet"]).read_text())
        self.assertEqual(assigned["thread_id"], "worker-11")
        self.assertNotEqual(assigned["request_id"], request)
        self.assertIn("message", assigned)
        for value in ("release/audit", assigned["request_id"], "Implement and prove behavior", "worker-11"):
            self.assertIn(value, assigned["message"])

    def test_initialize_returns_compact_context_and_rejects_stale_updates(self):
        code, result = self.operate(self.config)
        self.assertEqual((code, result["status"]), (0, "ready"))
        snapshot = self.snapshot()
        self.assertEqual(snapshot["target"], "release/audit")
        self.assertEqual(snapshot["available"], {"tickets": 2, "subagents": 2})
        self.assertEqual(snapshot["tickets"]["11"]["next"], "prepare-registering")
        before = self.ledger.read_bytes()
        code, result = self.operate(self.config, expected=0)
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_capacity_and_declared_conflicts_block_without_publishing_commands(self):
        self.config["tickets"].update({"14": {"depends_on": ["11"]},
                                       "15": {"conflicts": ["11"]}})
        self.operate(self.config)
        self.operate({"op": "prepare", "ticket": "11", "phase": "registering",
                      "instruction": "Ticket 11", "allowance": 2})
        for key, allowance in [("12", 1), ("14", 0), ("15", 0)]:
            before = self.ledger.read_bytes()
            files = set(self.root.rglob("*.commands/*.json"))
            code, result = self.operate({"op": "prepare", "ticket": key, "phase": "registering",
                                        "instruction": "Work", "allowance": allowance})
            self.assertEqual((code, result["status"]), (2, "blocked"), result)
            self.assertEqual(self.ledger.read_bytes(), before)
            self.assertEqual(set(self.root.rglob("*.commands/*.json")), files)
        code, result = self.operate({"op": "prepare", "ticket": "12", "phase": "registering",
                                    "instruction": "Work", "allowance": 0})
        self.assertEqual(code, 0, result)
        code, result = self.operate({"op": "prepare", "ticket": "13", "phase": "registering",
                                    "instruction": "Work"})
        self.assertEqual((code, result["status"]), (2, "blocked"))

    def test_repairs_and_capacity_changes_require_evidence_and_quiescence(self):
        self.config["limits"]["tickets"] = 1
        self.config["tickets"]["12"]["conflicts"] = ["11"]
        self.operate(self.config)
        packet = self.start_worker()
        _, report = self.worker_report(packet, outcome="blocked", content=None)
        self.operate({"op": "consume", "ticket": "11", "event": report["event"]})
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "capacity", "ticket": "11", "allowance": 0, "parked": True,
                                    "evidence": self.proof()})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)
        code, result = self.operate({"op": "capacity", "ticket": "11", "allowance": 0, "parked": True,
                                    "quiescent": True, "evidence": self.proof()})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["available"], {"tickets": 1, "subagents": 2})
        code, result = self.operate({"op": "prepare", "ticket": "12", "phase": "registering", "instruction": "Work"})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        code, result = self.operate({"op": "prepare", "ticket": "11", "phase": "repairing",
                                    "instruction": "Fix missing criterion A; reuse unchanged evidence", "allowance": 1,
                                    "quiescent": True, "evidence": self.proof()})
        self.assertEqual(code, 0, result)
        self.assertTrue(result["tickets"]["11"]["slot"])
        self.confirm_packet(result["packet"])
        _, report = self.worker_report(result["packet"], content="repaired-a")
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                    "next": {"phase": "verifying", "instruction": "Verify repaired criterion",
                                             "content_ref": "repaired-a", "evidence": self.proof()}})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["tickets"]["11"]["phase"], "verifying")

    def test_registration_cannot_reuse_another_workers_identity_or_checkout(self):
        self.operate(self.config)
        self.start_worker()
        _, result = self.operate({"op": "prepare", "ticket": "12", "phase": "registering", "instruction": "Create worker"})
        packet = json.loads(Path(result["packet"]).read_text())
        for worker in [
            {"thread_id": "worker-11", "host_id": "local", "worktree": str(self.root / "worktree-12"), "branch": "codex/12", "base_sha": "a"},
            {"thread_id": "worker-12", "host_id": "local", "worktree": str(self.root / "worktree-11"), "branch": "codex/12", "base_sha": "a"},
            {"thread_id": "worker-12", "host_id": "local", "worktree": str(self.root / "worktree-12"), "branch": "release/audit", "base_sha": "a"}]:
            before = self.ledger.read_bytes()
            code, response = self.operate({"op": "record", "ticket": "12", "request_id": packet["request_id"],
                                            "outcome": "confirmed", "worker": worker, "evidence": self.proof()})
            self.assertEqual((code, response["status"]), (2, "blocked"))
            self.assertEqual(self.ledger.read_bytes(), before)

    def test_followup_cannot_silently_release_reserved_subagents(self):
        self.operate(self.config)
        packet = self.start_worker()
        _, report = self.worker_report(packet)
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                    "next": {"phase": "verifying", "instruction": "Complete", "allowance": 0,
                                             "content_ref": "revision-a", "evidence": self.proof()}})
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_denied_merge_can_park_only_after_reconciled_cancellation(self):
        self.operate(self.config)
        self.complete_worker()
        _, prepared = self.operate({"op": "prepare", "ticket": "11", "phase": "integrating",
                                    "instruction": "Prepare", "target_ref": "target-a"})
        self.confirm_packet(prepared["packet"])
        _, report = self.worker_report(prepared["packet"], target="target-a")
        _, grant = self.operate({"op": "consume", "ticket": "11", "event": report["event"],
                                "next": {"phase": "delivering", "instruction": "Merge",
                                         "content_ref": "revision-a", "target_ref": "target-a",
                                         "current_target_ref": "target-a", "evidence": self.proof()}})
        self.confirm_packet(grant["packet"])
        decision = {"op": "capacity", "ticket": "11", "parked": True, "allowance": 0,
                    "quiescent": True, "evidence": self.proof()}
        code, result = self.operate(decision)
        self.assertEqual((code, result["status"]), (2, "blocked"))
        decision.update(grant_revoked=True, mutation_absent=True)
        code, result = self.operate(decision)
        self.assertEqual(code, 0, result)
        self.assertIsNone(result["integration"])
        self.assertEqual(result["tickets"]["11"]["phase"], "awaiting-integration")

    def test_status_exposes_decision_evidence_without_history_and_rejects_changed_packets(self):
        self.operate(self.config)
        packet = self.start_worker()
        _, report = self.worker_report(packet)
        self.operate({"op": "consume", "ticket": "11", "event": report["event"]})
        row = self.snapshot()["tickets"]["11"]
        self.assertIn("report", row)
        self.assertEqual(row["report"]["content_ref"], "revision-a")
        self.assertTrue(Path(row["report"]["result_path"]).exists())
        self.assertEqual(row["worker"]["thread_id"], "worker-11")
        self.assertNotIn("history", row)
        self.assertNotIn("instruction", row)
        Path(packet).write_text('{"instruction":"different command"}')
        code, result = self.cli("status", "--ledger", self.ledger)
        self.assertEqual((code, result["status"]), (2, "blocked"))

    def test_managed_ledger_rejects_generic_mutation_and_malformed_operations(self):
        self.operate(self.config)
        before = self.ledger.read_bytes()
        patch = self.root / "patch.json"
        patch.write_text('{"tickets":{"11":{"phase":"done"}}}')
        code, result = self.cli("checkpoint", "--ledger", self.ledger, "--expect-revision", self.revision, "--patch", patch)
        self.assertEqual((code, result["status"]), (3, "error"))
        for operation in [[], {"op": "prepare", "ticket": "11", "phase": [], "instruction": "Invalid phase"},
                          {"op": "capacity", "ticket": "11", "allowance": True}]:
            code, result = self.operate(operation)
            self.assertIn(code, (2, 3), result)
            self.assertEqual(self.ledger.read_bytes(), before)

    def test_observation_updates_recovery_facts_without_bypassing_workflow_state(self):
        self.operate(self.config)
        code, result = self.operate({"op": "observe", "ticket": "11", "facts": {"wait_cursor": "cursor-2", "usage": "unavailable"},
                                    "evidence": self.proof(), "continuation": {"mode": "callback", "evidence": "observed idle wake"}})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["continuation"]["mode"], "callback")
        self.assertEqual(result["tickets"]["11"]["facts"]["wait_cursor"], "cursor-2")
        before = self.ledger.read_bytes()
        code, result = self.operate({"op": "observe", "ticket": "11", "facts": {"phase": "done"}, "evidence": self.proof()})
        self.assertEqual((code, result["status"]), (3, "error"))
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_incomplete_managed_file_returns_an_error_without_rewriting_it(self):
        self.ledger.write_text('{"schema_version":2}')
        before = self.ledger.read_bytes()
        code, result = self.cli("status", "--ledger", self.ledger)
        self.assertEqual((code, result["status"]), (3, "error"))
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_status_identifies_blocked_dependencies_before_a_dispatch_attempt(self):
        self.config["tickets"]["12"]["depends_on"] = ["11"]
        self.operate(self.config)
        snapshot = self.snapshot()
        self.assertEqual(snapshot["tickets"]["12"]["next"], "wait-eligibility")
        self.assertEqual(snapshot["tickets"]["12"]["depends_on"], ["11"])
        self.assertIn("prerequisite", snapshot["tickets"]["12"]["reason"])


if __name__ == "__main__":
    unittest.main()
