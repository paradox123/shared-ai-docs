import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "extract_codex_session_evidence.py"


def response_item(payload, nested=False):
    return {
        "type": "response_item",
        "payload": {"item": payload} if nested else payload,
    }


def message(role, text, phase=None):
    payload = {
        "type": "message",
        "role": role,
        "content": [
            {
                "type": "input_text" if role == "user" else "output_text",
                "text": text,
            }
        ],
    }
    if phase:
        payload["phase"] = phase
    return payload


class ExtractCodexSessionEvidenceCliTests(unittest.TestCase):
    def run_script(self, manifest, *extra_args):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--manifest",
                str(manifest),
                *extra_args,
            ],
            capture_output=True,
            text=True,
        )

    def write_manifest(self, root, sessions):
        manifest = root / "manifest.json"
        manifest.write_text(
            json.dumps({"schema_version": 1, "sessions": sessions})
        )
        return manifest

    def test_extracts_only_advertised_lines_and_bounds_sensitive_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "session.jsonl"
            wrappers = (
                "<recommended_plugins>private plugin data</recommended_plugins>\n"
                "# AGENTS.md instructions for /private/path\n"
                "<INSTRUCTIONS>private repo rules</INSTRUCTIONS>\n"
                "<environment_context>private environment</environment_context>\n"
            )
            request = "Actual request " + "x" * 400
            records = [
                response_item(message("user", "outside advertised range")),
                response_item(message("user", wrappers + request)),
                response_item(
                    {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": '{"secret":"FUNCTION_SECRET"}',
                    },
                    nested=True,
                ),
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "input": (
                            "await tools.web__run({secret: 'CUSTOM_SECRET'}); "
                            "await tools.exec_command({cmd: 'hidden'});"
                        ),
                    }
                ),
                response_item(
                    message(
                        "user",
                        '<heartbeat automation_id="learn" state="running" '
                        'decision="continue" status="ok">first</heartbeat>',
                    )
                ),
                response_item(
                    message(
                        "user",
                        "<heartbeat>{\"automation_id\":\"learn\","
                        "\"state\":\"running\",\"decision\":\"continue\","
                        "\"status\":\"ok\"}</heartbeat>",
                    ),
                    nested=True,
                ),
                response_item(
                    message(
                        "assistant",
                        "Final result " + "y" * 400,
                        phase="final_answer",
                    ),
                    nested=True,
                ),
                response_item(
                    {
                        "type": "function_call",
                        "name": "outside_tool",
                        "arguments": "OUTSIDE_SECRET",
                    }
                ),
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session-1",
                        "thread_name": "Evidence session",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "state": "complete",
                            "review_line_start": 2,
                            "review_line_end": 7,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(manifest)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\n", result.stdout.strip())
            self.assertNotIn("SECRET", result.stdout)
            self.assertNotIn("private plugin data", result.stdout)
            self.assertNotIn("outside advertised range", result.stdout)
            output = json.loads(result.stdout)
            session = output["sessions"][0]
            self.assertEqual(session["user_summary"], request[:240])
            self.assertEqual(len(session["user_summary"]), 240)
            self.assertEqual(
                session["tool_names"],
                ["exec_command", "web__run", "exec_command"],
            )
            self.assertEqual(len(session["final_summary"]), 240)
            self.assertEqual(session["counts"]["inspected_lines"], 6)
            self.assertEqual(session["counts"]["heartbeat_messages"], 2)
            self.assertEqual(session["counts"]["tool_calls"], 3)
            self.assertEqual(
                session["heartbeat_groups"],
                [
                    {
                        "automation_id": "learn",
                        "state": "running",
                        "decision": "continue",
                        "status": "ok",
                        "count": 2,
                        "first_line": 5,
                        "last_line": 6,
                    }
                ],
            )

    def test_embedded_history_requires_manual_suffix_without_summaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "clone.jsonl"
            rollout.write_text(
                json.dumps(
                    response_item(message("user", "IMPORTED_PRIVATE_CONTENT"))
                )
                + "\n"
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "clone-session",
                        "thread_name": "Clone",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "state": "complete",
                            "review_line_start": 1,
                            "review_line_end": 1,
                            "embedded_session_metas": [
                                {
                                    "line_number": 1,
                                    "id": "source-session",
                                    "timestamp": "2026-08-01T00:00:00Z",
                                }
                            ],
                        },
                    }
                ],
            )

            result = self.run_script(manifest)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("IMPORTED_PRIVATE_CONTENT", result.stdout)
            session = json.loads(result.stdout)["sessions"][0]
            self.assertTrue(session["manual_suffix_selection_required"])
            self.assertEqual(session["embedded_session_ids"], ["source-session"])
            self.assertEqual(session["counts"]["inspected_lines"], 0)
            self.assertIsNone(session["user_summary"])
            self.assertEqual(session["tool_names"], [])
            self.assertIsNone(session["final_summary"])

    def test_redacts_free_text_heartbeat_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "heartbeat.jsonl"
            rollout.write_text(
                json.dumps(
                    response_item(
                        message(
                            "user",
                            '<heartbeat automation_id="learn" '
                            'decision="contact private@example.com">control</heartbeat>',
                        )
                    )
                )
                + "\n"
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "heartbeat-session",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 1,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(manifest)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("private@example.com", result.stdout)
            group = json.loads(result.stdout)["sessions"][0]["heartbeat_groups"][0]
            self.assertEqual(group["automation_id"], "learn")
            self.assertEqual(group["decision"], "[redacted]")

    def test_repeatable_session_filter_is_exact_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = []
            for session_id in ("allowed-a", "blocked", "allowed-b"):
                rollout = root / f"{session_id}.jsonl"
                rollout.write_text(
                    json.dumps(
                        response_item(message("user", f"request {session_id}"))
                    )
                    + "\n"
                )
                sessions.append(
                    {
                        "id": session_id,
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "state": "complete",
                            "review_line_start": 1,
                            "review_line_end": 1,
                            "embedded_session_metas": [],
                        },
                    }
                )
            manifest = self.write_manifest(root, sessions)

            result = self.run_script(
                manifest,
                "--session-id",
                "allowed-a",
                "--session-id",
                "allowed-b",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(
                [session["id"] for session in output["sessions"]],
                ["allowed-a", "allowed-b"],
            )
            self.assertNotIn("request blocked", result.stdout)
            self.assertEqual(output["counts"]["selected_sessions"], 2)
            self.assertEqual(output["counts"]["filtered_out_sessions"], 1)

            unknown = self.run_script(
                manifest, "--session-id", "missing-session"
            )
            self.assertNotEqual(unknown.returncode, 0)
            self.assertIn("unknown requested session", unknown.stderr)
            self.assertEqual(unknown.stdout, "")

    def test_session_filter_does_not_open_unselected_rollout_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            allowed = root / "allowed.jsonl"
            allowed.write_text(
                json.dumps(response_item(message("user", "allowed request")))
                + "\n"
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "allowed",
                        "status": "resolved",
                        "path": str(allowed),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 1,
                        },
                    },
                    {
                        "id": "not-allowed",
                        "status": "resolved",
                        "path": str(root / "missing.jsonl"),
                        "rollout_window": {
                            "review_line_start": 999,
                            "review_line_end": 1,
                        },
                    },
                ],
            )

            result = self.run_script(manifest, "--session-id", "allowed")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(result.stdout)["sessions"][0]["id"], "allowed"
            )

    def test_caps_total_json_and_reports_omitted_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = []
            for number in range(8):
                rollout = root / f"session-{number}.jsonl"
                records = [
                    response_item(
                        message(
                            "user",
                            f'<heartbeat automation_id="automation-{group}" '
                            f'state="state-{group}" decision="continue" '
                            f'status="ok">control</heartbeat>',
                        )
                    )
                    for group in range(12)
                ]
                rollout.write_text(
                    "".join(json.dumps(record) + "\n" for record in records)
                )
                sessions.append(
                    {
                        "id": f"session-{number}",
                        "thread_name": "z" * 240,
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "state": "complete",
                            "review_line_start": 1,
                            "review_line_end": 12,
                            "embedded_session_metas": [],
                        },
                    }
                )
            manifest = self.write_manifest(root, sessions)

            result = self.run_script(
                manifest, "--max-total-chars", "2000", "--pretty"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertLessEqual(len(result.stdout.rstrip("\n")), 2000)
            output = json.loads(result.stdout)
            self.assertGreater(output["omitted_sessions"]["count"], 0)
            self.assertEqual(
                output["omitted_sessions"]["count"],
                output["counts"]["omitted_sessions"],
            )
            self.assertEqual(
                output["counts"]["emitted_sessions"]
                + output["counts"]["omitted_sessions"],
                output["counts"]["resolved_sessions"],
            )

    def test_rejects_invalid_manifest_paths_ranges_and_too_small_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid_json = root / "invalid.json"
            invalid_json.write_text("not json")
            self.assertNotEqual(
                self.run_script(invalid_json).returncode,
                0,
            )

            missing_path_manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "missing",
                        "status": "resolved",
                        "path": str(root / "missing-rollout.jsonl"),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 1,
                        },
                    }
                ],
            )
            self.assertNotEqual(
                self.run_script(missing_path_manifest).returncode,
                0,
            )

            rollout = root / "range.jsonl"
            rollout.write_text("{}\n")
            bad_range_manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "range",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 3,
                            "review_line_end": 1,
                        },
                    }
                ],
            )
            self.assertNotEqual(
                self.run_script(bad_range_manifest).returncode,
                0,
            )
            self.assertNotEqual(
                self.run_script(
                    bad_range_manifest,
                    "--max-total-chars",
                    "1999",
                ).returncode,
                0,
            )

    def test_allows_the_resolver_empty_delta_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "empty-delta.jsonl"
            rollout.write_text("{}\n{}\n")
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "empty-delta",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "state": "open",
                            "review_line_start": 3,
                            "review_line_end": 2,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(manifest)

            self.assertEqual(result.returncode, 0, result.stderr)
            session = json.loads(result.stdout)["sessions"][0]
            self.assertEqual(session["counts"]["advertised_lines"], 0)
            self.assertEqual(session["counts"]["inspected_lines"], 0)


if __name__ == "__main__":
    unittest.main()
