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

    def test_structural_projection_emits_only_advertised_typed_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "structure.jsonl"
            long_tool_name = "tool_" + "x" * 200
            records = [
                response_item(message("user", "OUTSIDE_PRIVATE_CONTENT")),
                {
                    "type": "session_meta",
                    "payload": {
                        "id": "session-structure",
                        "cwd": "/PRIVATE/CWD",
                    },
                },
                response_item(message("user", "MESSAGE_SECRET")),
                response_item(
                    {
                        "type": "reasoning",
                        "summary": "REASONING_SECRET",
                    }
                ),
                response_item(
                    {
                        "type": "function_call",
                        "name": long_tool_name,
                        "arguments": '{"secret":"ARGUMENT_SECRET"}',
                    },
                    nested=True,
                ),
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "input": "await tools.exec_command('INPUT_SECRET')",
                    }
                ),
                response_item(
                    {
                        "type": "custom_tool_call_output",
                        "output": "OUTPUT_SECRET",
                    }
                ),
                response_item(message("user", "OUTSIDE_AFTER_PRIVATE")),
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session-structure",
                        "thread_name": "PRIVATE THREAD NAME",
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

            result = self.run_script(
                manifest,
                "--session-id",
                "session-structure",
                "--structural-projection",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\n", result.stdout.strip())
            for secret in (
                "PRIVATE",
                "SECRET",
                "OUTSIDE",
                "tools.exec_command",
            ):
                self.assertNotIn(secret, result.stdout)
            output = json.loads(result.stdout)
            self.assertEqual(output["mode"], "structural_projection")
            session = output["sessions"][0]
            self.assertNotIn("thread_name", session)
            self.assertEqual(session["review_line_start"], 2)
            self.assertEqual(session["review_line_end"], 7)
            self.assertEqual(
                session["counts"],
                {
                    "advertised_lines": 6,
                    "inspected_lines": 6,
                    "emitted_records": 6,
                    "omitted_records": 0,
                },
            )
            expected_keys = {
                "line_number",
                "record_type",
                "payload_type",
                "role",
                "phase",
                "tool_name",
                "session_id",
            }
            self.assertTrue(session["records"])
            self.assertTrue(
                all(set(record) == expected_keys for record in session["records"])
            )
            self.assertEqual(
                [record["line_number"] for record in session["records"]],
                [2, 3, 4, 5, 6, 7],
            )
            self.assertEqual(session["records"][0]["session_id"], "session-structure")
            self.assertEqual(session["records"][1]["payload_type"], "message")
            self.assertEqual(session["records"][1]["role"], "user")
            self.assertEqual(session["records"][2]["payload_type"], "reasoning")
            self.assertIsNone(session["records"][2]["tool_name"])
            self.assertEqual(len(session["records"][3]["tool_name"]), 120)
            self.assertEqual(session["records"][4]["tool_name"], "exec")
            self.assertIsNone(session["records"][5]["tool_name"])

    def test_structural_projection_requires_exact_resolved_ids_and_its_own_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "repo"
            (repo_root / ".git").mkdir(parents=True)
            rollout = root / "session.jsonl"
            rollout.write_text("{}\n")
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "resolved-session",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 1,
                            "embedded_session_metas": [],
                        },
                    },
                    {
                        "id": "unresolved-session",
                        "status": "missing",
                    },
                ],
            )

            invocations = (
                (("--structural-projection",), "requires exact --session-id"),
                (
                    (
                        "--session-id",
                        "missing-session",
                        "--structural-projection",
                    ),
                    "unknown requested session",
                ),
                (
                    (
                        "--session-id",
                        "unresolved-session",
                        "--structural-projection",
                    ),
                    "not resolved",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--structural-projection",
                        "--cwd-root",
                        str(repo_root),
                    ),
                    "cannot be combined",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--structural-projection",
                        "--list-clone-boundaries",
                    ),
                    "cannot be combined",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--structural-projection",
                        "--clone-suffix-start",
                        "resolved-session=1",
                    ),
                    "cannot be combined",
                ),
            )
            for invocation, error_text in invocations:
                with self.subTest(invocation=invocation):
                    result = self.run_script(manifest, *invocation)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error_text, result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_structural_projection_honors_repeatable_exact_filters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = []
            for session_id in ("allowed-a", "blocked", "allowed-b"):
                rollout = root / f"{session_id}.jsonl"
                if session_id != "blocked":
                    rollout.write_text(
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {"id": session_id},
                            }
                        )
                        + "\n"
                    )
                sessions.append(
                    {
                        "id": session_id,
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
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
                "--structural-projection",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(
                [session["id"] for session in output["sessions"]],
                ["allowed-a", "allowed-b"],
            )
            self.assertEqual(output["counts"]["selected_sessions"], 2)
            self.assertEqual(output["counts"]["filtered_out_sessions"], 1)

    def test_structural_projection_caps_records_and_reports_omissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "large.jsonl"
            records = [
                {
                    "type": "event_msg",
                    "payload": {"type": f"event_{number:03d}"},
                }
                for number in range(100)
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "large-session",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 100,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(
                manifest,
                "--session-id",
                "large-session",
                "--structural-projection",
                "--max-total-chars",
                "2000",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertLessEqual(len(result.stdout.rstrip("\n")), 2000)
            output = json.loads(result.stdout)
            session = output["sessions"][0]
            self.assertEqual(session["counts"]["inspected_lines"], 100)
            self.assertGreater(session["counts"]["omitted_records"], 0)
            self.assertEqual(
                session["counts"]["emitted_records"]
                + session["counts"]["omitted_records"],
                100,
            )
            self.assertEqual(
                output["counts"]["emitted_records"]
                + output["counts"]["omitted_records"],
                output["counts"]["inspected_records"],
            )

    def test_tool_call_projection_emits_only_bounded_sanitized_call_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "tool-calls.jsonl"
            long_command = (
                "API_TOKEN=custom-secret rg needle " + ("x" * 1000)
            )
            custom_input = (
                "const r = await tools.exec_command({"
                f"cmd: {json.dumps(long_command)}, "
                f"workdir: {json.dumps(str(Path.home() / 'project'))}, "
                "yield_time_ms: 10000}); text(r.output);"
            )
            records = [
                {
                    "type": "session_meta",
                    "payload": {
                        "id": "session-tools",
                        "cwd": "/PRIVATE/MANIFEST/CWD",
                    },
                },
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "call_id": "call-custom",
                        "input": custom_input,
                    }
                ),
                response_item(
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "call-custom",
                        "output": json.dumps(
                            {
                                "status": "failed",
                                "exit_code": 7,
                                "output": "CUSTOM_OUTPUT_BODY_SECRET",
                            }
                        ),
                    }
                ),
                response_item(
                    {
                        "type": "function_call",
                        "name": "exec_command",
                        "call_id": "call-direct",
                        "arguments": json.dumps(
                            {
                                "cmd": "tool --token direct-secret check",
                                "cwd": str(Path.home() / "legacy-project"),
                            }
                        ),
                    },
                    nested=True,
                ),
                response_item(
                    {
                        "type": "function_call_output",
                        "call_id": "call-direct",
                        "output": {
                            "status": "completed",
                            "exitCode": 0,
                            "output": "DIRECT_OUTPUT_BODY_SECRET",
                        },
                    }
                ),
                response_item(
                    {
                        "type": "function_call",
                        "name": "web__run",
                        "call_id": "call-web",
                        "arguments": '{"secret":"WEB_ARGUMENT_SECRET"}',
                    }
                ),
                response_item(
                    {
                        "type": "function_call_output",
                        "call_id": "call-web",
                        "output": json.dumps(
                            {
                                "status": "completed",
                                "output": "WEB_OUTPUT_BODY_SECRET",
                            }
                        ),
                    }
                ),
                response_item(message("user", "OUTSIDE_PRIVATE_CONTENT")),
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session-tools",
                        "thread_name": "PRIVATE THREAD NAME",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "state": "complete",
                            "review_line_start": 1,
                            "review_line_end": 7,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(
                manifest,
                "--session-id",
                "session-tools",
                "--tool-call-projection",
                "session-tools=2",
                "--tool-call-projection",
                "session-tools=4",
                "--tool-call-projection",
                "session-tools=6",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            for secret in (
                "custom-secret",
                "direct-secret",
                "CUSTOM_OUTPUT_BODY_SECRET",
                "DIRECT_OUTPUT_BODY_SECRET",
                "WEB_ARGUMENT_SECRET",
                "WEB_OUTPUT_BODY_SECRET",
                "OUTSIDE_PRIVATE_CONTENT",
                "PRIVATE THREAD NAME",
                "/PRIVATE/MANIFEST/CWD",
            ):
                self.assertNotIn(secret, result.stdout)
            output = json.loads(result.stdout)
            self.assertEqual(output["mode"], "tool_call_projection")
            self.assertEqual(output["counts"]["projected_tool_calls"], 3)
            calls = output["tool_calls"]
            self.assertEqual(
                [(call["session_id"], call["line_number"]) for call in calls],
                [
                    ("session-tools", 2),
                    ("session-tools", 4),
                    ("session-tools", 6),
                ],
            )
            self.assertEqual(
                set(calls[0]),
                {
                    "session_id",
                    "line_number",
                    "nested_call_index",
                    "tool_name",
                    "command",
                    "cwd",
                    "paired_status",
                    "paired_exit_code",
                },
            )
            self.assertEqual(calls[0]["nested_call_index"], 1)
            self.assertEqual(calls[0]["tool_name"], "exec_command")
            self.assertIn("API_TOKEN=[redacted]", calls[0]["command"])
            self.assertLessEqual(len(calls[0]["command"]), 600)
            self.assertEqual(calls[0]["cwd"], "~/project")
            self.assertEqual(calls[0]["paired_status"], "failed")
            self.assertEqual(calls[0]["paired_exit_code"], 7)
            self.assertEqual(calls[1]["tool_name"], "exec_command")
            self.assertIsNone(calls[1]["nested_call_index"])
            self.assertEqual(
                calls[1]["command"], "tool --token [redacted] check"
            )
            self.assertEqual(calls[1]["cwd"], "~/legacy-project")
            self.assertEqual(calls[1]["paired_status"], "completed")
            self.assertEqual(calls[1]["paired_exit_code"], 0)
            self.assertEqual(calls[2]["tool_name"], "web__run")
            self.assertIsNone(calls[2]["nested_call_index"])
            self.assertIsNone(calls[2]["command"])
            self.assertIsNone(calls[2]["cwd"])
            self.assertEqual(calls[2]["paired_status"], "completed")
            self.assertIsNone(calls[2]["paired_exit_code"])

    def test_tool_call_projection_selects_indexed_calls_from_batched_exec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "batched-tool-calls.jsonl"
            first_command = (
                "API_TOKEN=first-secret rg 'tools.fake_call(' first"
            )
            custom_input = (
                "const results = await Promise.all(["
                "tools.exec_command({"
                f"cmd: {json.dumps(first_command)}, "
                f"workdir: {json.dumps(str(Path.home() / 'first-project'))}"
                "}), "
                "/* tools.comment_call({secret: 'COMMENT SECRET'}) */"
                "tools.web__run({search_query: [{q: 'PRIVATE QUERY'}]}), "
                "tools.exec_command({"
                "cmd: 'tool --token second-secret check', "
                f"cwd: {json.dumps(str(Path.home() / 'second-project'))}"
                "})"
                "]);"
            )
            records = [
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "call_id": "call-batch",
                        "input": custom_input,
                    }
                ),
                response_item(
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "call-batch",
                        "output": json.dumps(
                            {
                                "status": "completed",
                                "exit_code": 0,
                                "output": "PRIVATE OUTPUT BODY",
                            }
                        ),
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
                        "id": "session-batch",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 2,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(
                manifest,
                "--session-id",
                "session-batch",
                "--tool-call-projection",
                "session-batch=1#1",
                "--tool-call-projection",
                "session-batch=1#2",
                "--tool-call-projection",
                "session-batch=1#3",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            for secret in (
                "first-secret",
                "second-secret",
                "COMMENT SECRET",
                "PRIVATE QUERY",
                "PRIVATE OUTPUT BODY",
            ):
                self.assertNotIn(secret, result.stdout)
            output = json.loads(result.stdout)
            calls = output["tool_calls"]
            self.assertEqual(
                [
                    (
                        call["line_number"],
                        call["nested_call_index"],
                        call["tool_name"],
                    )
                    for call in calls
                ],
                [
                    (1, 1, "exec_command"),
                    (1, 2, "web__run"),
                    (1, 3, "exec_command"),
                ],
            )
            self.assertEqual(
                calls[0]["command"],
                "API_TOKEN=[redacted] rg 'tools.fake_call(' first",
            )
            self.assertEqual(calls[0]["cwd"], "~/first-project")
            self.assertIsNone(calls[1]["command"])
            self.assertIsNone(calls[1]["cwd"])
            self.assertEqual(
                calls[2]["command"], "tool --token [redacted] check"
            )
            self.assertEqual(calls[2]["cwd"], "~/second-project")
            self.assertTrue(
                all(call["paired_status"] is None for call in calls)
            )
            self.assertTrue(
                all(call["paired_exit_code"] is None for call in calls)
            )

            legacy = self.run_script(
                manifest,
                "--session-id",
                "session-batch",
                "--tool-call-projection",
                "session-batch=1",
            )
            self.assertNotEqual(legacy.returncode, 0)
            self.assertIn("requires an explicit nested index", legacy.stderr)
            self.assertEqual(legacy.stdout, "")

    def test_tool_call_projection_ignores_regex_literal_lookalikes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "regex-lookalike.jsonl"
            records = [
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "call_id": "call-regex",
                        "input": (
                            "const pattern = "
                            '/tools.exec_command({cmd:"REGEX_PRIVATE"})/; '
                            "await tools.web__run({});"
                        ),
                    }
                ),
                response_item(
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "call-regex",
                        "output": '{"status":"completed"}',
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
                        "id": "session-regex",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 2,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(
                manifest,
                "--session-id",
                "session-regex",
                "--tool-call-projection",
                "session-regex=1",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("REGEX_PRIVATE", result.stdout)
            call = json.loads(result.stdout)["tool_calls"][0]
            self.assertEqual(call["tool_name"], "web__run")
            self.assertEqual(call["nested_call_index"], 1)
            self.assertEqual(call["paired_status"], "completed")

    def test_tool_call_projection_does_not_treat_property_division_as_regex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "property-division.jsonl"
            rollout.write_text(
                json.dumps(
                    response_item(
                        {
                            "type": "custom_tool_call",
                            "name": "exec",
                            "input": (
                                "const ratio = holder.return / "
                                "tools.exec_command({cmd: 'real division'}) / 2; "
                                "await tools.web__run({});"
                            ),
                        }
                    )
                )
                + "\n"
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session-division",
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

            result = self.run_script(
                manifest,
                "--session-id",
                "session-division",
                "--tool-call-projection",
                "session-division=1",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires an explicit nested index", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_tool_call_projection_scans_executable_template_expressions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "template-expression.jsonl"
            records = [
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "call_id": "call-template",
                        "input": (
                            "const label = `result:"
                            "${await tools.exec_command({cmd: 'echo template'})}"
                            "`; text(label); await tools.web__run({});"
                        ),
                    }
                ),
                response_item(
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "call-template",
                        "output": '{"status":"completed","exit_code":0}',
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
                        "id": "session-template",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 2,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            result = self.run_script(
                manifest,
                "--session-id",
                "session-template",
                "--tool-call-projection",
                "session-template=1#1",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            call = json.loads(result.stdout)["tool_calls"][0]
            self.assertEqual(call["tool_name"], "exec_command")
            self.assertEqual(call["command"], "echo template")
            self.assertEqual(call["nested_call_index"], 1)
            self.assertIsNone(call["paired_status"])
            self.assertIsNone(call["paired_exit_code"])

            legacy = self.run_script(
                manifest,
                "--session-id",
                "session-template",
                "--tool-call-projection",
                "session-template=1",
            )
            self.assertNotEqual(legacy.returncode, 0)
            self.assertIn("requires an explicit nested index", legacy.stderr)
            self.assertEqual(legacy.stdout, "")

    def test_tool_call_projection_rejects_ambiguous_dynamic_tool_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "ambiguous-tool-calls.jsonl"
            sources = (
                (
                    "await tools?.exec_command({cmd: 'optional object'}); "
                    "await tools.web__run({});"
                ),
                (
                    "await tools.exec_command?.({cmd: 'optional call'}); "
                    "await tools.web__run({});"
                ),
                (
                    "await tools['exec_command']({cmd: 'bracket call'}); "
                    "await tools.web__run({});"
                ),
                (
                    "const nested = tools; "
                    "await nested.exec_command({cmd: 'aliased call'}); "
                    "await tools.web__run({});"
                ),
            )
            records = [
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "call_id": f"call-ambiguous-{index}",
                        "input": source,
                    }
                )
                for index, source in enumerate(sources, start=1)
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session-ambiguous",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": len(records),
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            for line_number in range(1, len(records) + 1):
                with self.subTest(line_number=line_number):
                    result = self.run_script(
                        manifest,
                        "--session-id",
                        "session-ambiguous",
                        "--tool-call-projection",
                        f"session-ambiguous={line_number}",
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "ambiguous nested tool syntax", result.stderr
                    )
                    self.assertEqual(result.stdout, "")

    def test_tool_call_projection_rejects_invalid_or_ambiguous_nested_indices(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "nested-index-errors.jsonl"
            records = [
                response_item(
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "input": (
                            "await tools.exec_command({cmd: 'first'}); "
                            "await tools.web__run({});"
                        ),
                    }
                ),
                response_item(
                    {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": '{"cmd":"direct"}',
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
                        "id": "session-index-errors",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 1,
                            "review_line_end": 2,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            invocations = (
                ("session-index-errors=1#0", "nested index must be positive"),
                (
                    "session-index-errors=1#three",
                    "nested index must be an integer",
                ),
                (
                    "session-index-errors=1#1#2",
                    "must use <session-id>=<line>#<nested-index>",
                ),
                ("session-index-errors=1#3", "nested index 3 is out of range"),
                (
                    "session-index-errors=2#1",
                    "nested indices apply only to custom tool calls",
                ),
            )
            for projection, error_text in invocations:
                with self.subTest(projection=projection):
                    result = self.run_script(
                        manifest,
                        "--session-id",
                        "session-index-errors",
                        "--tool-call-projection",
                        projection,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error_text, result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_tool_call_projection_requires_exact_ids_and_rejects_other_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "repo"
            (repo_root / ".git").mkdir(parents=True)
            rollout = root / "session.jsonl"
            rollout.write_text(
                json.dumps(
                    response_item(
                        {
                            "type": "function_call",
                            "name": "exec_command",
                            "arguments": '{"cmd":"true"}',
                        }
                    )
                )
                + "\n"
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "resolved-session",
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

            invocations = (
                (
                    ("--tool-call-projection", "resolved-session=1"),
                    "requires exact --session-id",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--tool-call-projection",
                        "other-session=1",
                    ),
                    "missing matching --session-id",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--tool-call-projection",
                        "resolved-session=1",
                        "--structural-projection",
                    ),
                    "cannot be combined",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--tool-call-projection",
                        "resolved-session=1",
                        "--cwd-root",
                        str(repo_root),
                    ),
                    "cannot be combined",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--tool-call-projection",
                        "resolved-session=1",
                        "--list-clone-boundaries",
                    ),
                    "cannot be combined",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--tool-call-projection",
                        "resolved-session=1",
                        "--clone-suffix-start",
                        "resolved-session=1",
                    ),
                    "cannot be combined",
                ),
                (
                    (
                        "--session-id",
                        "resolved-session",
                        "--tool-call-projection",
                        "invalid-value",
                    ),
                    "must use <session-id>=<line>",
                ),
            )
            for invocation, error_text in invocations:
                with self.subTest(invocation=invocation):
                    result = self.run_script(manifest, *invocation)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error_text, result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_tool_call_projection_rejects_out_of_range_and_non_tool_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "session.jsonl"
            records = [
                response_item(message("user", "OUTSIDE_BEFORE")),
                response_item(message("user", "inside request")),
                response_item(
                    {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": '{"cmd":"true"}',
                    }
                ),
                response_item(
                    {
                        "type": "function_call_output",
                        "output": '{"exit_code":0}',
                    }
                ),
                response_item(message("user", "OUTSIDE_AFTER")),
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session",
                        "status": "resolved",
                        "path": str(rollout),
                        "rollout_window": {
                            "review_line_start": 2,
                            "review_line_end": 4,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            invocations = (
                ("session=1", "outside advertised range"),
                ("session=5", "outside advertised range"),
                ("session=2", "is not a tool call"),
                ("session=4", "is not a tool call"),
            )
            for projection, error_text in invocations:
                with self.subTest(projection=projection):
                    result = self.run_script(
                        manifest,
                        "--session-id",
                        "session",
                        "--tool-call-projection",
                        projection,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error_text, result.stderr)
                    self.assertEqual(result.stdout, "")

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

    def test_clone_boundary_map_and_explicit_suffix_exclude_imported_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rollout = root / "clone.jsonl"
            records = [
                {
                    "type": "session_meta",
                    "payload": {"id": "clone-session"},
                },
                {
                    "type": "session_meta",
                    "payload": {"id": "source-session"},
                },
                response_item(message("user", "IMPORTED_PRIVATE_CONTENT")),
                response_item(
                    message("assistant", "imported final", phase="final_answer")
                ),
                {"type": "event_msg", "payload": {"type": "task_complete"}},
                {"type": "event_msg", "payload": {"type": "task_started"}},
                response_item(message("user", "Actual clone request")),
                response_item(
                    {
                        "type": "function_call",
                        "name": "exec_command",
                        "arguments": '{"secret":"DO_NOT_EMIT"}',
                    }
                ),
                response_item(
                    message("assistant", "clone final", phase="final_answer")
                ),
            ]
            rollout.write_text(
                "".join(json.dumps(record) + "\n" for record in records)
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
                            "review_line_end": len(records),
                            "embedded_session_metas": [
                                {
                                    "line_number": 2,
                                    "id": "source-session",
                                    "timestamp": "2026-08-01T00:00:00Z",
                                }
                            ],
                        },
                    }
                ],
            )

            boundaries = self.run_script(
                manifest,
                "--session-id",
                "clone-session",
                "--list-clone-boundaries",
            )

            self.assertEqual(boundaries.returncode, 0, boundaries.stderr)
            self.assertNotIn("PRIVATE", boundaries.stdout)
            boundary_session = json.loads(boundaries.stdout)["sessions"][0]
            self.assertTrue(boundary_session["manual_suffix_selection_required"])
            boundary_map = boundary_session["clone_boundary_map"]
            self.assertEqual(
                boundary_map["task_complete"]["lines"],
                [5],
            )
            self.assertEqual(
                boundary_map["task_started"]["lines"],
                [6],
            )
            self.assertEqual(
                boundary_map["substantive_user"]["lines"],
                [3, 7],
            )

            suffix = self.run_script(
                manifest,
                "--session-id",
                "clone-session",
                "--clone-suffix-start",
                "clone-session=6",
            )

            self.assertEqual(suffix.returncode, 0, suffix.stderr)
            self.assertNotIn("IMPORTED_PRIVATE_CONTENT", suffix.stdout)
            self.assertNotIn("DO_NOT_EMIT", suffix.stdout)
            suffix_session = json.loads(suffix.stdout)["sessions"][0]
            self.assertFalse(suffix_session["manual_suffix_selection_required"])
            self.assertTrue(suffix_session["embedded_history_excluded"])
            self.assertEqual(suffix_session["selected_suffix_start"], 6)
            self.assertEqual(suffix_session["user_summary"], "Actual clone request")
            self.assertEqual(suffix_session["tool_names"], ["exec_command"])
            self.assertEqual(suffix_session["final_summary"], "clone final")

            unfiltered = self.run_script(
                manifest,
                "--clone-suffix-start",
                "clone-session=6",
            )
            self.assertNotEqual(unfiltered.returncode, 0)
            self.assertIn("require exact --session-id", unfiltered.stderr)

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

    def test_path_selectors_union_repeated_roots_and_worktree_tails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd_roots = [root / "repo-a", root / "repo-b"]
            (cwd_roots[0] / ".git").mkdir(parents=True)
            cwd_roots[1].mkdir(parents=True)
            (cwd_roots[1] / ".git").write_text("gitdir: ../metadata\n")
            worktree_root = Path.home() / ".codex" / "worktrees"
            sessions = []
            session_cwds = {
                "cwd-exact": cwd_roots[0],
                "cwd-descendant": cwd_roots[1] / "packages" / "api",
                "worktree-exact": worktree_root / "slot-a" / "repo-a",
                "worktree-descendant": (
                    worktree_root / "slot-b" / "repo-b" / "src"
                ),
                "blocked": root / "unrelated",
            }
            for session_id, cwd in session_cwds.items():
                rollout = root / f"{session_id}.jsonl"
                if session_id != "blocked":
                    rollout.write_text(
                        json.dumps(
                            response_item(
                                message("user", f"request {session_id}")
                            )
                        )
                        + "\n"
                    )
                sessions.append(
                    {
                        "id": session_id,
                        "status": "resolved",
                        "path": str(rollout),
                        "meta": {"cwd": str(cwd)},
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
                "--cwd-root",
                str(cwd_roots[0]),
                "--cwd-root",
                str(cwd_roots[1]),
                "--worktree-tail",
                "repo-a",
                "--worktree-tail",
                "repo-b",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(
                [session["id"] for session in output["sessions"]],
                [
                    "cwd-exact",
                    "cwd-descendant",
                    "worktree-exact",
                    "worktree-descendant",
                ],
            )
            self.assertEqual(output["counts"]["selected_sessions"], 4)
            self.assertEqual(output["counts"]["filtered_out_sessions"], 1)
            self.assertNotIn("request blocked", result.stdout)

            no_match_root = root / "missing-repo"
            (no_match_root / ".git").mkdir(parents=True)
            no_match = self.run_script(
                manifest,
                "--cwd-root",
                str(no_match_root),
                "--worktree-tail",
                "missing-tail",
            )

            self.assertEqual(no_match.returncode, 0, no_match.stderr)
            no_match_output = json.loads(no_match.stdout)
            self.assertEqual(no_match_output["sessions"], [])
            self.assertEqual(
                no_match_output["counts"],
                {
                    "manifest_sessions": 5,
                    "selected_sessions": 0,
                    "filtered_out_sessions": 5,
                    "resolved_sessions": 0,
                    "skipped_unresolved_sessions": 0,
                    "emitted_sessions": 0,
                    "omitted_sessions": 0,
                },
            )

    def test_path_selectors_fail_closed_on_unsafe_values_and_mixed_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_root = root / "repo"
            (repo_root / ".git").mkdir(parents=True)
            rollout = root / "session.jsonl"
            rollout.write_text(
                json.dumps(response_item(message("user", "request"))) + "\n"
            )
            manifest = self.write_manifest(
                root,
                [
                    {
                        "id": "session",
                        "status": "resolved",
                        "path": str(rollout),
                        "meta": {"cwd": str(repo_root)},
                        "rollout_window": {
                            "state": "complete",
                            "review_line_start": 1,
                            "review_line_end": 1,
                            "embedded_session_metas": [],
                        },
                    }
                ],
            )

            unsafe_roots = (
                ("relative/repo", "absolute"),
                (str(Path("/")), "too broad"),
                (str(Path("/tmp")), "too broad"),
                (str(Path.home()), "too broad"),
                (str(root / "repo" / ".." / "other"), "must not contain"),
                (str(root / "not-a-repo"), "existing repository root"),
            )
            for unsafe_root, error_text in unsafe_roots:
                with self.subTest(cwd_root=unsafe_root):
                    result = self.run_script(
                        manifest, "--cwd-root", unsafe_root
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error_text, result.stderr)
                    self.assertEqual(result.stdout, "")

            for invalid_tail in ("", ".", "..", "org/repo", "../repo"):
                with self.subTest(worktree_tail=invalid_tail):
                    result = self.run_script(
                        manifest, "--worktree-tail", invalid_tail
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("single repository names", result.stderr)
                    self.assertEqual(result.stdout, "")

            mixed_invocations = (
                (
                    "--cwd-root",
                    str(repo_root),
                    "--session-id",
                    "session",
                ),
                (
                    "--worktree-tail",
                    "repo",
                    "--list-clone-boundaries",
                ),
                (
                    "--cwd-root",
                    str(repo_root),
                    "--clone-suffix-start",
                    "session=1",
                ),
            )
            for invocation in mixed_invocations:
                with self.subTest(invocation=invocation):
                    result = self.run_script(manifest, *invocation)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "path selectors cannot be combined",
                        result.stderr,
                    )
                    self.assertEqual(result.stdout, "")

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
