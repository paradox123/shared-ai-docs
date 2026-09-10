from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GATE_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = GATE_ROOT / "tests" / "fixtures"


class GateCliTests(unittest.TestCase):
    def invoke_gate(
        self,
        manifest: dict[str, object],
        observed: dict[str, object],
        boundaries: dict[str, object] | None = None,
        evidence_root_override: Path | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object], Path]:
        test_state_root = GATE_ROOT / ".test-state"
        test_state_root.mkdir(exist_ok=True)
        temp_dir = tempfile.TemporaryDirectory(dir=test_state_root)
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        manifest_path = root / "manifest.json"
        observed_path = root / "observed.json"
        boundaries_path = root / "boundaries.json"
        evidence_root = evidence_root_override or root / "evidence"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        observed_path.write_text(json.dumps(observed), encoding="utf-8")
        boundaries_path.write_text(
            json.dumps(
                boundaries
                or {"schemaVersion": "maf-oss-gate-boundaries/v1", "boundaries": []}
            ),
            encoding="utf-8",
        )
        live_result = subprocess.run(
            [
                sys.executable,
                str(GATE_ROOT / "gate.py"),
                "observe",
                "--manifest",
                str(manifest_path),
            ],
            cwd=GATE_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        live = json.loads(live_result.stdout)["observed"]
        placeholders = {
            "sourceRevision": "522e1d98afff58c251c4402578cb4d1187f91a84",
            "gateSourceDigest": "b" * 64,
            "dirtyStateDigest": "c" * 64,
            "packageLockSha256": "a" * 64,
            "componentInventorySha256": "d" * 64,
        }
        manifest_fields = {
            "sourceRevision": (manifest["source"], "revision"),
            "gateSourceDigest": (manifest["source"], "gateSourceDigest"),
            "dirtyStateDigest": (manifest["source"], "dirtyStateDigest"),
            "packageLockSha256": (manifest["packageLock"], "sha256"),
            "componentInventorySha256": (
                manifest["componentInventory"],
                "sha256",
            ),
        }
        for observed_name, placeholder in placeholders.items():
            parent, manifest_name = manifest_fields[observed_name]
            if parent.get(manifest_name) == placeholder:
                parent[manifest_name] = live[observed_name]
            if observed.get(observed_name) == placeholder:
                observed[observed_name] = live[observed_name]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        observed_path.write_text(json.dumps(observed), encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(GATE_ROOT / "gate.py"),
                "evaluate",
                "--manifest",
                str(manifest_path),
                "--observed",
                str(observed_path),
                "--boundaries",
                str(boundaries_path),
                "--evidence-root",
                str(evidence_root),
            ],
            cwd=GATE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        return completed, json.loads(completed.stdout), root

    def test_matching_stale_manifest_and_observation_are_rejected(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        stale_revision = "0" * 40
        manifest["source"]["revision"] = stale_revision
        observed["sourceRevision"] = stale_revision

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn("provenance.source-revision-mismatch", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_component_inventory_drift_is_rejected_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["components"][0]["version"] = "1.16.1"

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn("manifest.component-inventory-mismatch", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_occupied_port_is_rejected_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            port = occupied.getsockname()[1]
            manifest["probe"]["ports"] = [port]

            completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn(f"isolation.port-in-use:{port}", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_occupied_process_namespace_is_rejected_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        occupied_name = "maf-oss-gate-occupied-fixture-process"
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)", occupied_name]
        )
        self.addCleanup(process.kill)
        manifest["probe"]["workerProcessNames"] = [
            occupied_name,
            "maf-oss-gate-free-fixture-process",
        ]

        completed, result, _ = self.invoke_gate(manifest, observed)

        process.terminate()
        process.wait(timeout=5)
        self.assertEqual(2, completed.returncode)
        self.assertIn(
            f"isolation.process-name-in-use:{occupied_name}", result["failures"]
        )
        self.assertFalse(result["probe"]["started"])

    def test_json_schema_and_backend_revision_validation_fail_closed(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["components"][0]["licence"] = {}
        manifest["backend"]["revision"] = "main"

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertTrue(
            any(value.startswith("manifest.schema:") for value in result["failures"])
        )
        self.assertIn("manifest.backend-revision-not-pinned", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_arbitrary_probe_json_is_not_durability_evidence(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["probe"]["command"] = [
            sys.executable,
            "tests/fixtures/successful-probe.py",
        ]

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go", result["decision"])
        self.assertIn("probe.worker-one-checkpoint-missing", result["failures"])

    def test_evidence_path_may_not_overlap_protected_boundary(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as protected_dir:
            protected_path = Path(protected_dir)
            boundaries = {
                "schemaVersion": "maf-oss-gate-boundaries/v1",
                "boundaries": [
                    {
                        "name": "protected",
                        "path": str(protected_path),
                        "mode": "metadata-and-content-hash",
                    }
                ],
            }

            completed, result, _ = self.invoke_gate(
                manifest,
                observed,
                boundaries,
                evidence_root_override=protected_path / "evidence",
            )

            self.assertEqual(2, completed.returncode)
            self.assertIn(
                "isolation.evidence-path-overlap:protected", result["failures"]
            )
            self.assertFalse((protected_path / "evidence").exists())

    def test_evidence_write_failure_returns_structured_no_go(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )

        completed, result, _ = self.invoke_gate(
            manifest,
            observed,
            evidence_root_override=GATE_ROOT / "README.md",
        )

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go", result["decision"])
        self.assertIn("evidence.write-failed:NotADirectoryError", result["failures"])
        self.assertNotIn("evidenceDirectory", result)

    def test_human_report_correlates_all_required_dimensions(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["backend"]["compatibleWithTuple"] = False

        _, result, _ = self.invoke_gate(manifest, observed)

        report = (
            Path(result["evidenceDirectory"])
            .joinpath("report.md")
            .read_text(encoding="utf-8")
        )
        for expected in (
            manifest["source"]["revision"],
            manifest["packageLock"]["sha256"],
            manifest["runtime"]["dotnetSdk"],
            manifest["configuration"]["version"],
            manifest["configuration"]["contractVersion"],
            manifest["backend"]["revision"],
        ):
            self.assertIn(expected, report)

    def test_source_revision_drift_fails_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        observed["sourceRevision"] = "0000000000000000000000000000000000000000"

        marker = Path(tempfile.gettempdir()) / "maf-oss-gate-drift-probe-marker"
        marker.unlink(missing_ok=True)
        self.addCleanup(marker.unlink, missing_ok=True)
        manifest["probe"]["command"] = [
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text('started')",
        ]

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go", result["decision"])
        self.assertIn("provenance.source-revision-mismatch", result["failures"])
        self.assertFalse(result["probe"]["started"])
        self.assertFalse(marker.exists())

    def test_forbidden_component_fails_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["components"].append(
            {
                "name": "Temporal",
                "kind": "backend",
                "version": "1.0.0",
                "source": "https://github.com/temporalio/temporal",
                "licence": {
                    "spdx": "MIT",
                    "source": "https://github.com/temporalio/temporal/blob/main/LICENSE",
                },
                "unavoidableServiceCost": {
                    "amount": 0,
                    "amountStatus": "zero",
                    "currency": "EUR",
                    "period": "none",
                    "source": "https://github.com/temporalio/temporal",
                },
            }
        )

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn("dependency.forbidden:Temporal", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_missing_licence_and_cost_data_fail_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        component = manifest["components"][0]
        del component["licence"]
        del component["unavoidableServiceCost"]

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn(
            "manifest.component-licence-missing:Microsoft.Agents.AI.DurableTask",
            result["failures"],
        )
        self.assertIn(
            "manifest.component-cost-missing:Microsoft.Agents.AI.DurableTask",
            result["failures"],
        )
        self.assertFalse(result["probe"]["started"])

    def test_incompatible_backend_fails_before_probe(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["backend"].update(
            {
                "name": "Durable Task Scheduler",
                "type": "managed-service",
                "productionCapable": True,
                "selfManaged": False,
                "openSource": False,
                "compatibleWithTuple": True,
                "unavoidableServiceCost": {
                    "amount": None,
                    "amountStatus": "variable-paid",
                    "currency": "EUR",
                    "period": "operation",
                    "source": "https://azure.microsoft.com/pricing/details/durable-task-scheduler/",
                },
            }
        )

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn("backend.not-self-managed", result["failures"])
        self.assertIn("backend.not-open-source", result["failures"])
        self.assertIn("backend.managed-service", result["failures"])
        self.assertIn("backend.unavoidable-service-cost", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_each_provenance_dimension_is_correlated_before_probe(self) -> None:
        cases = {
            "gateSourceDigest": "provenance.gate-source-digest-mismatch",
            "dirtyStateDigest": "provenance.dirty-state-digest-mismatch",
            "dotnetSdk": "provenance.dotnet-sdk-mismatch",
            "rid": "provenance.rid-mismatch",
            "configurationVersion": "provenance.configuration-version-mismatch",
            "contractVersion": "provenance.contract-version-mismatch",
            "packageLockSha256": "provenance.package-lock-sha256-mismatch",
            "componentInventorySha256": "provenance.component-inventory-sha256-mismatch",
        }
        for field, expected_failure in cases.items():
            with self.subTest(field=field):
                manifest = json.loads(
                    (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
                )
                observed = json.loads(
                    (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
                )
                observed[field] = "different"

                completed, result, _ = self.invoke_gate(manifest, observed)

                self.assertEqual(2, completed.returncode)
                self.assertIn(expected_failure, result["failures"])
                self.assertFalse(result["probe"]["started"])

    def test_floating_and_duplicate_components_are_rejected(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["components"][0]["version"] = "latest"
        manifest["components"].append(dict(manifest["components"][0]))

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn(
            "manifest.component-version-not-pinned:Microsoft.Agents.AI.DurableTask",
            result["failures"],
        )
        self.assertIn(
            "manifest.component-duplicate:Microsoft.Agents.AI.DurableTask",
            result["failures"],
        )
        self.assertFalse(result["probe"]["started"])

    def test_no_go_writes_correlated_evidence_and_unchanged_fingerprints(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["backend"]["compatibleWithTuple"] = False
        with tempfile.TemporaryDirectory() as protected_dir:
            protected_path = Path(protected_dir) / "protected.txt"
            protected_path.write_text("unchanged", encoding="utf-8")
            boundaries = {
                "schemaVersion": "maf-oss-gate-boundaries/v1",
                "boundaries": [
                    {
                        "name": "test-protected-boundary",
                        "path": str(protected_path),
                        "mode": "metadata-and-content-hash",
                    }
                ],
            }

            completed, result, _ = self.invoke_gate(manifest, observed, boundaries)

            evidence_dir = Path(result["evidenceDirectory"])
            decision = json.loads(
                (evidence_dir / "decision.json").read_text(encoding="utf-8")
            )
            report = (evidence_dir / "report.md").read_text(encoding="utf-8")
            fingerprint = decision["boundaries"]["test-protected-boundary"]
            self.assertEqual(2, completed.returncode)
            self.assertRegex(decision["manifestDigest"], r"^[0-9a-f]{64}$")
            self.assertEqual(fingerprint["before"], fingerprint["after"])
            self.assertTrue(fingerprint["unchanged"])
            self.assertIn("backend.incompatible-with-tuple", report)

    def test_eligible_backend_runs_probe_and_requires_two_worker_continuation(
        self,
    ) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(0, completed.returncode)
        self.assertEqual("go", result["decision"])
        self.assertTrue(result["probe"]["started"])
        self.assertRegex(result["probe"]["orchestrationId"], r"^gate-")
        self.assertEqual(
            ["maf-oss-gate-worker-1", "maf-oss-gate-worker-2"],
            result["probe"]["workers"],
        )
        self.assertEqual(
            {"after-worker-stop": 1, "before-worker-stop": 1},
            result["probe"]["effects"],
        )
        self.assertTrue(
            Path(result["evidenceDirectory"]).joinpath("decision.json").exists()
        )

    def test_probe_that_changes_a_protected_boundary_is_no_go(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as protected_dir:
            protected_path = Path(protected_dir) / "protected.txt"
            protected_path.write_text("before", encoding="utf-8")
            payload = {
                "orchestrationId": "fixture-run-1",
                "workers": ["fixture-worker-1", "fixture-worker-2"],
                "checkpoints": ["worker-1-checkpoint", "worker-2-complete"],
                "effects": {"before-worker-stop": 1, "after-worker-stop": 1},
                "continued": True,
            }
            manifest["probe"]["command"] = [
                sys.executable,
                "-c",
                (
                    "import json; from pathlib import Path; "
                    f"Path({str(protected_path)!r}).write_text('after'); "
                    f"print(json.dumps({payload!r}))"
                ),
            ]
            boundaries = {
                "schemaVersion": "maf-oss-gate-boundaries/v1",
                "boundaries": [
                    {
                        "name": "protected",
                        "path": str(protected_path),
                        "mode": "metadata-and-content-hash",
                    }
                ],
            }

            completed, result, _ = self.invoke_gate(manifest, observed, boundaries)

            self.assertEqual(2, completed.returncode)
            self.assertEqual("no-go", result["decision"])
            self.assertIn("boundary.changed:protected", result["failures"])
            self.assertFalse(result["boundaries"]["protected"]["unchanged"])

    def test_committed_audit_is_no_go_without_starting_the_probe(self) -> None:
        manifest = json.loads((GATE_ROOT / "manifest.json").read_text(encoding="utf-8"))
        observed = json.loads((GATE_ROOT / "observed.json").read_text(encoding="utf-8"))

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go", result["decision"])
        self.assertEqual(
            {
                "backend.managed-service",
                "backend.not-self-managed",
                "backend.not-open-source",
                "backend.unavoidable-service-cost",
            },
            set(result["failures"]),
        )
        self.assertFalse(result["probe"]["started"])

    def test_required_manifest_contract_fields_fail_closed(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        manifest["schemaVersion"] = "unexpected"
        manifest["backend"]["compatibilityEvidence"] = []
        manifest["backend"]["storageDependencies"] = []

        completed, result, _ = self.invoke_gate(manifest, observed)

        self.assertEqual(2, completed.returncode)
        self.assertIn("manifest.schema-version-invalid", result["failures"])
        self.assertIn(
            "manifest.backend-compatibility-evidence-missing", result["failures"]
        )
        self.assertIn(
            "manifest.backend-storage-dependencies-missing", result["failures"]
        )
        self.assertFalse(result["probe"]["started"])

    def test_gate_state_path_may_not_overlap_a_protected_boundary(self) -> None:
        manifest = json.loads(
            (FIXTURES / "eligible-manifest.json").read_text(encoding="utf-8")
        )
        observed = json.loads(
            (FIXTURES / "matching-observed.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as protected_dir:
            protected_path = Path(protected_dir)
            manifest["probe"]["statePaths"] = [str(protected_path / "gate-state")]
            boundaries = {
                "schemaVersion": "maf-oss-gate-boundaries/v1",
                "boundaries": [
                    {
                        "name": "protected-runtime",
                        "path": str(protected_path),
                        "mode": "metadata-and-content-hash",
                    }
                ],
            }

            completed, result, _ = self.invoke_gate(manifest, observed, boundaries)

            self.assertEqual(2, completed.returncode)
            self.assertIn(
                "isolation.state-path-overlap:protected-runtime", result["failures"]
            )
            self.assertFalse(result["probe"]["started"])


if __name__ == "__main__":
    unittest.main()
