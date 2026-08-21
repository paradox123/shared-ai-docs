import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "resolve_codex_sessions.py"


class ResolveCodexSessionsCliTests(unittest.TestCase):
    def test_help_distinguishes_recent_output_from_review_cutoff(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "this does not establish a review cutoff", result.stdout
        )
        self.assertIn("Explicit trusted review cutoff", result.stdout)

    def test_returns_one_consistent_window_from_newest_structured_cutoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)

            rows = [
                {
                    "id": "session-qmd",
                    "thread_name": "Update QMD Index Daily",
                    "updated_at": "2026-07-27T05:10:32.116012Z",
                },
                {
                    "id": "session-ki",
                    "thread_name": "Keep ki-fuer-kmu docs up-to-date",
                    "updated_at": "2026-07-27T06:18:00.356988Z",
                },
            ]
            index_text = "".join(json.dumps(row) + "\n" for row in rows)
            (codex_home / "session_index.jsonl").write_text(index_text)

            for row in rows:
                rollout = sessions_day / f"rollout-example-{row['id']}.jsonl"
                rollout.write_text(
                    json.dumps(
                        {
                            "type": "session_meta",
                            "payload": {
                                "id": row["id"],
                                "timestamp": row["updated_at"],
                                "cwd": str(root / row["id"]),
                            },
                        }
                    )
                    + "\n"
                )

            memory = root / "memory.md"
            memory.write_text(
                "# Learn Memory\n\n"
                "Last review: 2026-07-26T07:00:52.759124Z\n"
                "Processed window end: 2026-07-26T06:00:00Z\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                    "--prompt-last-run",
                    "2026-07-26T07:00:50.878Z",
                    "--recent",
                    "120",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["schema_version"], 1)
            self.assertEqual(
                output["cutoff"]["chosen"], "2026-07-26T07:00:52.759124Z"
            )
            self.assertEqual(
                output["window"]["end_inclusive"],
                "2026-07-27T06:18:00.356988Z",
            )
            self.assertEqual(
                output["window"]["cursor_to_persist"],
                output["window"]["end_inclusive"],
            )
            self.assertTrue(output["window"]["safe_to_persist"])
            self.assertEqual(
                [session["id"] for session in output["sessions"]],
                ["session-qmd", "session-ki"],
            )
            self.assertEqual(
                output["snapshot"]["recent_index"][-1]["id"], "session-ki"
            )

    def test_resolves_only_the_newest_index_row_for_a_duplicate_session_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            rows = [
                {
                    "id": "session-1",
                    "thread_name": "Earlier title",
                    "updated_at": "2026-07-27T05:00:00Z",
                },
                {
                    "id": "session-1",
                    "thread_name": "Current title",
                    "updated_at": "2026-07-27T06:00:00Z",
                },
            ]
            (codex_home / "session_index.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows)
            )
            (sessions_day / "rollout-session-1.jsonl").write_text(
                json.dumps(
                    {
                        "type": "session_meta",
                        "payload": {
                            "id": "session-1",
                            "timestamp": "2026-07-27T04:59:59Z",
                            "cwd": str(root / "project"),
                        },
                    }
                )
                + "\n"
            )
            memory = root / "memory.md"
            memory.write_text(
                "Last review: 2026-07-26T07:00:00Z\n"
                "Processed window end: 2026-07-26T07:00:00Z\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(len(output["sessions"]), 1)
            self.assertEqual(output["sessions"][0]["thread_name"], "Current title")
            self.assertEqual(
                output["sessions"][0]["updated_at"], "2026-07-27T06:00:00Z"
            )
            self.assertEqual(
                output["diagnostics"],
                [
                    {
                        "code": "duplicate_index_rows_collapsed",
                        "sessions": [{"id": "session-1", "row_count": 2}],
                    }
                ],
            )

    def test_recent_zero_emits_no_visible_index_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            row = {
                "id": "session-1",
                "thread_name": "One session",
                "updated_at": "2026-07-27T06:00:00Z",
            }
            (codex_home / "session_index.jsonl").write_text(
                json.dumps(row) + "\n"
            )
            (sessions_day / "rollout-session-1.jsonl").write_text(
                json.dumps(
                    {
                        "type": "session_meta",
                        "payload": {
                            "id": "session-1",
                            "timestamp": "2026-07-27T05:59:59Z",
                            "cwd": str(root / "project"),
                        },
                    }
                )
                + "\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--prompt-last-run",
                    "2026-07-26T07:00:00Z",
                    "--recent",
                    "0",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["snapshot"]["recent_index"], [])
            self.assertEqual(
                [session["id"] for session in output["sessions"]],
                ["session-1"],
            )
            self.assertEqual(
                output["window"]["cursor_to_persist"],
                "2026-07-27T06:00:00Z",
            )
            self.assertTrue(output["window"]["safe_to_persist"])

    def test_flags_embedded_session_history_without_making_cursor_unsafe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "08" / "06"
            sessions_day.mkdir(parents=True)
            row = {
                "id": "session-clone",
                "thread_name": "Cloned task",
                "updated_at": "2026-08-06T07:30:19Z",
            }
            (codex_home / "session_index.jsonl").write_text(
                json.dumps(row) + "\n"
            )
            records = [
                {
                    "timestamp": "2026-08-06T07:30:18.638Z",
                    "type": "session_meta",
                    "payload": {
                        "id": "session-clone",
                        "timestamp": "2026-08-06T07:30:18.471Z",
                        "cwd": str(root / "project"),
                    },
                },
                {
                    "timestamp": "2026-08-06T07:30:18.639Z",
                    "type": "session_meta",
                    "payload": {
                        "id": "session-source",
                        "timestamp": "2026-08-05T10:42:31.746Z",
                        "cwd": str(root / "project"),
                    },
                },
                {
                    "timestamp": "2026-08-06T07:30:18.640Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "phase": "final_answer",
                        "content": [],
                    },
                },
            ]
            (sessions_day / "rollout-session-clone.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--prompt-last-run",
                    "2026-08-05T07:00:00Z",
                    "--compact",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\n", result.stdout.strip())
            output = json.loads(result.stdout)
            session = output["sessions"][0]
            self.assertNotIn(
                "physical_line_count", session["rollout_window"]
            )
            self.assertEqual(
                session["rollout_window"]["embedded_session_metas"],
                [
                    {
                        "line_number": 2,
                        "id": "session-source",
                        "timestamp": "2026-08-05T10:42:31.746Z",
                    }
                ],
            )
            self.assertIn(
                {
                    "code": "embedded_session_history_detected",
                    "session_id": "session-clone",
                    "embedded_session_ids": ["session-source"],
                },
                output["diagnostics"],
            )
            self.assertTrue(output["window"]["safe_to_persist"])

    def test_marks_open_or_post_window_rollouts_for_carry_forward(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            rows = [
                {
                    "id": "session-open",
                    "thread_name": "Open automation",
                    "updated_at": "2026-07-27T06:00:00Z",
                },
                {
                    "id": "session-resumed",
                    "thread_name": "Completed then resumed",
                    "updated_at": "2026-07-27T07:00:00Z",
                },
                {
                    "id": "session-metadata",
                    "thread_name": "Voice metadata",
                    "updated_at": "2026-07-27T08:00:00Z",
                },
            ]
            (codex_home / "session_index.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows)
            )

            def write_rollout(session_id, records):
                path = sessions_day / f"rollout-{session_id}.jsonl"
                meta = {
                    "timestamp": "2026-07-27T05:59:00Z",
                    "type": "session_meta",
                    "payload": {
                        "id": session_id,
                        "timestamp": "2026-07-27T05:59:00Z",
                        "cwd": str(root / session_id),
                    },
                }
                path.write_text(
                    "".join(
                        json.dumps(record) + "\n"
                        for record in [meta, *records]
                    )
                )

            write_rollout(
                "session-open",
                [
                    {
                        "timestamp": "2026-07-27T06:30:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "phase": "commentary",
                            "content": [],
                        },
                    }
                ],
            )
            write_rollout(
                "session-resumed",
                [
                    {
                        "timestamp": "2026-07-27T07:30:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "phase": "final",
                            "content": [],
                        },
                    },
                    {
                        "timestamp": "2026-07-27T08:30:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "name": "later_tool",
                        },
                    },
                ],
            )
            write_rollout("session-metadata", [])

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--prompt-last-run",
                    "2026-07-26T07:00:00Z",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            sessions = {session["id"]: session for session in output["sessions"]}
            self.assertEqual(
                sessions["session-open"]["rollout_window"]["state"], "open"
            )
            self.assertEqual(
                sessions["session-resumed"]["rollout_window"]["state"],
                "complete",
            )
            self.assertEqual(
                sessions["session-resumed"]["rollout_window"][
                    "records_after_window"
                ],
                1,
            )
            self.assertEqual(
                sessions["session-metadata"]["rollout_window"]["state"],
                "metadata_only",
            )
            self.assertEqual(
                [
                    entry["id"]
                    for entry in output["window"][
                        "carry_forward_to_persist"
                    ]
                ],
                ["session-open", "session-resumed"],
            )

    def test_reselects_carry_memory_session_older_than_cutoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            old_day = codex_home / "sessions" / "2026" / "07" / "26"
            new_day = codex_home / "sessions" / "2026" / "07" / "27"
            old_day.mkdir(parents=True)
            new_day.mkdir(parents=True)
            rows = [
                {
                    "id": "session-pending",
                    "thread_name": "Older open session",
                    "updated_at": "2026-07-26T06:00:00Z",
                },
                {
                    "id": "session-new",
                    "thread_name": "New session",
                    "updated_at": "2026-07-27T08:00:00Z",
                },
            ]
            (codex_home / "session_index.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows)
            )
            for day, row in ((old_day, rows[0]), (new_day, rows[1])):
                records = [
                    {
                        "timestamp": row["updated_at"],
                        "type": "session_meta",
                        "payload": {
                            "id": row["id"],
                            "timestamp": row["updated_at"],
                            "cwd": str(root / row["id"]),
                        },
                    },
                    {
                        "timestamp": "2026-07-27T07:30:00Z",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "phase": "final",
                            "content": [],
                        },
                    },
                ]
                (day / f"rollout-{row['id']}.jsonl").write_text(
                    "".join(json.dumps(record) + "\n" for record in records)
                )
            memory = root / "memory.md"
            memory.write_text(
                "Last review: 2026-07-27T07:00:00Z\n"
                "Processed window end: 2026-07-27T07:00:00Z\n"
                "Carry-forward sessions: "
                '[{"id":"session-pending","line_count":1,'
                '"last_activity_at":"2026-07-26T06:00:00Z"}]\n'
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            sessions = {session["id"]: session for session in output["sessions"]}
            self.assertEqual(
                sessions["session-pending"]["selection_reasons"],
                ["carry_forward"],
            )
            self.assertEqual(
                [
                    entry["id"]
                    for entry in output["window"][
                        "carry_forward_from_memory"
                    ]
                ],
                ["session-pending"],
            )
            self.assertNotIn(
                "session-pending",
                [
                    entry["id"]
                    for entry in output["window"][
                        "carry_forward_to_persist"
                    ]
                ],
            )

    def test_unchanged_carry_retires_and_exact_exclusion_precedes_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            rows = [
                {
                    "id": "session-stalled",
                    "thread_name": "Stalled prior session",
                    "updated_at": "2026-07-27T06:00:00Z",
                },
                {
                    "id": "session-current",
                    "thread_name": "Current Learn",
                    "updated_at": "2026-07-27T08:00:00Z",
                },
            ]
            (codex_home / "session_index.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows)
            )
            stalled_records = [
                {
                    "timestamp": "2026-07-27T05:59:00Z",
                    "type": "session_meta",
                    "payload": {
                        "id": "session-stalled",
                        "timestamp": "2026-07-27T05:59:00Z",
                        "cwd": str(root / "project"),
                    },
                },
                {
                    "timestamp": "2026-07-27T06:30:00Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "phase": "commentary",
                        "content": [],
                    },
                },
            ]
            (sessions_day / "rollout-session-stalled.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in stalled_records)
            )
            memory = root / "memory.md"
            memory.write_text(
                "Last review: 2026-07-27T07:00:00Z\n"
                "Processed window end: 2026-07-27T07:00:00Z\n"
                "Carry-forward sessions: "
                '[{"id":"session-stalled","line_count":2,'
                '"last_activity_at":"2026-07-27T06:30:00Z"},'
                '{"id":"session-current","line_count":1,'
                '"last_activity_at":"2026-07-27T08:00:00Z"}]\n'
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                    "--exclude-session-id",
                    "session-current",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(
                [session["id"] for session in output["sessions"]],
                ["session-stalled"],
            )
            self.assertEqual(
                output["window"]["carry_forward_to_persist"], []
            )
            self.assertEqual(
                [session["id"] for session in output["excluded_sessions"]],
                ["session-current"],
            )
            self.assertFalse(
                any(
                    item.get("code") == "missing_rollout"
                    for item in output["diagnostics"]
                )
            )

    def test_truncated_carry_is_unsafe_and_keeps_previous_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            row = {
                "id": "session-truncated",
                "thread_name": "Truncated carried session",
                "updated_at": "2026-07-27T08:00:00Z",
            }
            (codex_home / "session_index.jsonl").write_text(
                json.dumps(row) + "\n"
            )
            records = [
                {
                    "timestamp": "2026-07-27T06:00:00Z",
                    "type": "session_meta",
                    "payload": {
                        "id": row["id"],
                        "timestamp": "2026-07-27T06:00:00Z",
                        "cwd": str(root / "project"),
                    },
                },
                {
                    "timestamp": "2026-07-27T07:30:00Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "phase": "commentary",
                        "content": [],
                    },
                },
            ]
            (sessions_day / "rollout-session-truncated.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            memory = root / "memory.md"
            memory.write_text(
                "Last review: 2026-07-27T07:00:00Z\n"
                "Processed window end: 2026-07-27T07:00:00Z\n"
                "Carry-forward sessions: "
                '[{"id":"session-truncated","line_count":3,'
                '"last_activity_at":"2026-07-27T07:45:00Z"}]\n'
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            output = json.loads(result.stdout)
            self.assertFalse(output["window"]["safe_to_persist"])
            self.assertEqual(
                output["sessions"][0]["rollout_window"]["state"],
                "unknown",
            )
            self.assertEqual(
                output["window"]["carry_forward_to_persist"],
                [
                    {
                        "id": "session-truncated",
                        "line_count": 3,
                        "last_activity_at": "2026-07-27T07:45:00Z",
                    }
                ],
            )
            self.assertIn(
                {
                    "code": "unsafe_rollout_window",
                    "session_id": "session-truncated",
                    "state": "unknown",
                },
                output["diagnostics"],
            )

    def test_user_resume_after_final_remains_open_and_carried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            row = {
                "id": "session-resumed-after-final",
                "thread_name": "Resumed after final",
                "updated_at": "2026-07-27T08:00:00Z",
            }
            (codex_home / "session_index.jsonl").write_text(
                json.dumps(row) + "\n"
            )
            records = [
                {
                    "timestamp": "2026-07-27T06:00:00Z",
                    "type": "session_meta",
                    "payload": {
                        "id": row["id"],
                        "timestamp": "2026-07-27T06:00:00Z",
                        "cwd": str(root / "project"),
                    },
                },
                {
                    "timestamp": "2026-07-27T07:15:00Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "phase": "final",
                        "content": [],
                    },
                },
                {
                    "timestamp": "2026-07-27T07:30:00Z",
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "Continue"}],
                    },
                },
            ]
            (sessions_day / "rollout-session-resumed-after-final.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--prompt-last-run",
                    "2026-07-27T07:00:00Z",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(
                output["sessions"][0]["rollout_window"]["state"],
                "open",
            )
            self.assertEqual(
                [
                    entry["id"]
                    for entry in output["window"]["carry_forward_to_persist"]
                ],
                ["session-resumed-after-final"],
            )

    def test_invalid_carry_diagnostic_does_not_echo_memory_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            row = {
                "id": "session-valid",
                "thread_name": "Valid session",
                "updated_at": "2026-07-27T08:00:00Z",
            }
            (codex_home / "session_index.jsonl").write_text(
                json.dumps(row) + "\n"
            )
            (sessions_day / "rollout-session-valid.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-07-27T08:00:00Z",
                        "type": "session_meta",
                        "payload": {
                            "id": row["id"],
                            "timestamp": "2026-07-27T08:00:00Z",
                            "cwd": str(root / "project"),
                        },
                    }
                )
                + "\n"
            )
            secret = "sensitive-memory-value-" + ("x" * 5000)
            memory = root / "memory.md"
            memory.write_text(
                "Last review: 2026-07-27T07:00:00Z\n"
                "Processed window end: 2026-07-27T07:00:00Z\n"
                "Carry-forward sessions: "
                + json.dumps([{"id": secret}])
                + "\n"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                    "--compact",
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn(secret, result.stdout)
            output = json.loads(result.stdout)
            self.assertIn(
                {
                    "code": "invalid_carry_forward_entry",
                    "entry_index": 0,
                },
                output["diagnostics"],
            )

    def test_line_checkpoint_detects_same_timestamp_appends(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            sessions_day = codex_home / "sessions" / "2026" / "07" / "27"
            sessions_day.mkdir(parents=True)
            row = {
                "id": "session-same-ts",
                "thread_name": "Same timestamp appends",
                "updated_at": "2026-07-27T06:00:00Z",
            }
            (codex_home / "session_index.jsonl").write_text(
                json.dumps(row) + "\n"
            )
            records = [
                {
                    "timestamp": "2026-07-27T05:59:00Z",
                    "type": "session_meta",
                    "payload": {
                        "id": row["id"],
                        "timestamp": "2026-07-27T05:59:00Z",
                        "cwd": str(root / "project"),
                    },
                },
                {
                    "timestamp": "2026-07-27T06:30:00Z",
                    "type": "response_item",
                    "payload": {"type": "function_call", "name": "one"},
                },
                {
                    "timestamp": "2026-07-27T06:30:00Z",
                    "type": "response_item",
                    "payload": {"type": "function_call", "name": "two"},
                },
            ]
            (sessions_day / "rollout-session-same-ts.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            memory = root / "memory.md"
            memory.write_text(
                "Last review: 2026-07-27T07:00:00Z\n"
                "Processed window end: 2026-07-27T07:00:00Z\n"
                "Carry-forward sessions: "
                '[{"id":"session-same-ts","line_count":1,'
                '"last_activity_at":"2026-07-27T05:59:00Z"}]\n'
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--codex-home",
                    str(codex_home),
                    "--memory",
                    str(memory),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            session = output["sessions"][0]
            self.assertEqual(
                session["rollout_window"]["new_lines_at_window"], 2
            )
            self.assertEqual(
                output["window"]["carry_forward_to_persist"][0][
                    "line_count"
                ],
                3,
            )


if __name__ == "__main__":
    unittest.main()
