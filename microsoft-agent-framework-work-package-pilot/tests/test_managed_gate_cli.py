from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


PILOT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PILOT_ROOT))
import managed_gate  # noqa: E402
import process_controller  # noqa: E402
import evidence  # noqa: E402
from schema_validation import validate  # noqa: E402


def eligible_config() -> dict[str, object]:
    return {
        "schemaVersion": "maf-managed-dts-gate/v1",
        "operatorApproval": {
            "accepted": True,
            "acceptedAt": "2026-09-06",
            "scope": "isolated-agent-framework-pilot",
        },
        "azure": {
            "subscriptionId": "3c8f1707-52b9-43cc-9486-30faab0af3f0",
            "tenantId": "3602223d-667f-4cff-a98a-6c4ecb75f18c",
            "resourceGroup": "rg-agent-framework-pilot",
            "schedulerName": "dh-agent-framework-pilot",
            "taskHubName": "agent-framework-pilot",
            "endpoint": "https://dh-agent-framew-c2f7endt.northeurope.durabletask.io",
            "authentication": "DefaultAzure",
            "developerPrincipalObjectId": "9f604eb0-2adb-47a0-9e5d-382bf6897c40",
            "budgetName": "agent-framework-pilot-5",
            "budgetAmount": 5,
            "ipAllowlist": ["92.211.110.7/32"],
            "connectionEnvFile": "TEST_INJECTED",
        },
        "packages": {
            "azureIdentity": "1.17.1",
            "agentFrameworkDurableTask": "1.16.0-preview.260730.1",
            "agentFrameworkWorkflows": "1.16.0",
            "durableTask": "1.18.0",
        },
        "provenance": {
            "sourceRevision": "b31fea73491294280d0a7615980da629a551ebac",
            "dotnetSdk": "10.0.203",
            "rid": "osx-arm64",
            "packageLockPath": "ManagedDurabilityProbe/packages.lock.json",
            "packageLockSha256": "fc558079f3b1947b020e10eeeef454700d4a6bcb2647cdc72da5d450fe60f4ef",
            "pilotSourceSha256": "a" * 64,
            "protectedBoundariesSha256": "c" * 64,
            "contractVersion": "v1",
        },
        "probe": {
            "command": [
                "dotnet",
                "run",
                "--no-build",
                "--project",
                "ManagedDurabilityProbe",
                "--",
            ],
            "expectedEffects": ["checkpoint-one", "checkpoint-two"],
            "workerNames": ["managed-probe-worker-1", "managed-probe-worker-2"],
            "entryTimeoutSeconds": 5,
            "completionTimeoutSeconds": 10,
        },
    }


def eligible_observation() -> dict[str, object]:
    return {
        "schemaVersion": "maf-managed-dts-observation/v1",
        "subscription": {
            "id": "3c8f1707-52b9-43cc-9486-30faab0af3f0",
            "tenantId": "3602223d-667f-4cff-a98a-6c4ecb75f18c",
            "quotaId": "FreeTrial_2014-09-01",
            "spendingLimit": "On",
        },
        "scheduler": {
            "resourceGroup": "rg-agent-framework-pilot",
            "name": "dh-agent-framework-pilot",
            "endpoint": "https://dh-agent-framew-c2f7endt.northeurope.durabletask.io",
            "sku": "Consumption",
            "state": "Succeeded",
            "publicNetworkAccess": "Enabled",
            "ipAllowlist": ["92.211.110.7/32"],
        },
        "taskHub": {"name": "agent-framework-pilot", "state": "Succeeded"},
        "budget": {
            "name": "agent-framework-pilot-5",
            "amount": 5,
            "timeGrain": "Monthly",
            "notificationThresholds": [50, 80, 100],
        },
        "role": "Durable Task Data Contributor",
        "principal": {
            "objectId": "9f604eb0-2adb-47a0-9e5d-382bf6897c40",
            "type": "user",
            "authenticationSource": "AzureCLI",
        },
        "provenance": {
            "sourceRevision": "b31fea73491294280d0a7615980da629a551ebac",
            "dotnetSdk": "10.0.203",
            "rid": "osx-arm64",
            "packageLockSha256": "fc558079f3b1947b020e10eeeef454700d4a6bcb2647cdc72da5d450fe60f4ef",
            "pilotSourceSha256": "a" * 64,
            "packages": {
                "azureIdentity": "1.17.1",
                "agentFrameworkDurableTask": "1.16.0-preview.260730.1",
                "agentFrameworkWorkflows": "1.16.0",
                "durableTaskClientAzureManaged": "1.18.0",
                "durableTaskWorkerAzureManaged": "1.18.0",
            },
        },
    }


def eligible_probe_result() -> dict[str, object]:
    return {
        "started": True,
        "runId": "managed-gate-00000000-0000-4000-8000-000000000001",
        "runStartCount": 1,
        "workerPids": {
            "managed-probe-worker-1": 1001,
            "managed-probe-worker-2": 1002,
        },
        "workerOneExitCode": -9,
        "workerTwoExitCode": 0,
        "activityWorkers": {
            "checkpoint-one": ["managed-probe-worker-1"],
            "checkpoint-two": ["managed-probe-worker-1", "managed-probe-worker-2"],
        },
        "effects": {"checkpoint-one": 1, "checkpoint-two": 1},
        "ledger": [{"type": "run-start"}, {"type": "run-complete"}],
        "build": {
            "mode": "locked-dotnet-build",
            "workerAssemblySha256": "d" * 64,
        },
    }


class ManagedGateCliTests(unittest.TestCase):
    def invoke(
        self,
        config: dict[str, object],
        observation: dict[str, object],
        environment_lines: list[str] | None = None,
        boundaries: dict[str, object] | None = None,
        evidence_root_override: Path | None = None,
        observation_error: Exception | None = None,
        evidence_write_error: OSError | None = None,
        probe_error: Exception | None = None,
        boundary_digest_override: str | None = None,
    ) -> tuple[SimpleNamespace, dict[str, object]]:
        test_state = PILOT_ROOT / ".test-state"
        test_state.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=test_state)
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        config_path = root / "config.json"
        boundaries_path = root / "boundaries.json"
        if environment_lines is None:
            environment_lines = [
                "DURABLE_TASK_SCHEDULER_CONNECTION_STRING="
                f"Endpoint={config['azure'].get('endpoint')};"
                f"TaskHub={config['azure'].get('taskHubName')};Authentication=DefaultAzure"
            ]
        environment_path = root / "probe.env"
        environment_path.write_text("\n".join(environment_lines) + "\n", encoding="utf-8")
        config["azure"]["connectionEnvFile"] = str(environment_path)
        boundary_config = boundaries or {
            "schemaVersion": "maf-managed-boundaries/v1",
            "boundaries": [],
        }
        config["provenance"]["protectedBoundariesSha256"] = (
            boundary_digest_override or managed_gate.digest(boundary_config)
        )
        config_path.write_text(json.dumps(config), encoding="utf-8")
        boundaries_path.write_text(json.dumps(boundary_config), encoding="utf-8")
        evidence_root = evidence_root_override or root / "evidence"
        output = io.StringIO()
        fingerprints = {f"protected-{index}": "e" * 64 for index in range(8)}
        with contextlib.ExitStack() as stack:
            if observation_error is None:
                stack.enter_context(
                    patch.object(managed_gate, "observe", return_value=observation)
                )
            else:
                stack.enter_context(
                    patch.object(managed_gate, "observe", side_effect=observation_error)
                )
            if probe_error is None:
                stack.enter_context(
                    patch.object(
                        managed_gate,
                        "run_probe",
                        return_value=(eligible_probe_result(), []),
                    )
                )
            else:
                stack.enter_context(
                    patch.object(managed_gate, "run_probe", side_effect=probe_error)
                )
            stack.enter_context(
                patch.object(
                    managed_gate,
                    "capture_boundaries",
                    return_value=(fingerprints, []),
                )
            )
            if evidence_write_error is not None:
                stack.enter_context(
                    patch.object(
                        managed_gate,
                        "write_evidence",
                        side_effect=evidence_write_error,
                    )
                )
            with contextlib.redirect_stdout(output):
                returncode = managed_gate.main(
                    [
                        "evaluate",
                        "--config",
                        str(config_path),
                        "--boundaries",
                        str(boundaries_path),
                        "--evidence-root",
                        str(evidence_root),
                    ]
                )
        completed = SimpleNamespace(returncode=returncode, stderr="")
        return completed, json.loads(output.getvalue())

    def test_missing_operator_approval_is_rejected_before_probe(self) -> None:
        config = eligible_config()
        config["operatorApproval"]["accepted"] = False

        completed, result = self.invoke(config, eligible_observation())

        self.assertEqual(2, completed.returncode)
        self.assertIn("approval.operator-not-accepted", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_config_schema_violation_is_rejected_before_probe(self) -> None:
        config = eligible_config()
        config["unexpected"] = True

        completed, result = self.invoke(config, eligible_observation())

        self.assertEqual(2, completed.returncode)
        self.assertIn("config.schema:$.unexpected:additionalProperties", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_malformed_operator_approval_date_is_rejected(self) -> None:
        config = eligible_config()
        config["operatorApproval"]["acceptedAt"] = "not-a-date"

        completed, result = self.invoke(config, eligible_observation())

        self.assertEqual(2, completed.returncode)
        self.assertIn("config.schema:$.operatorApproval.acceptedAt:format-date", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_non_production_worker_command_is_rejected(self) -> None:
        config = eligible_config()
        config["probe"]["command"] = [
            sys.executable,
            "tests/fixtures/fake_worker.py",
        ]

        completed, result = self.invoke(config, eligible_observation())

        self.assertEqual(2, completed.returncode)
        self.assertIn("probe.production-command-mismatch", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_unapproved_boundary_inventory_is_rejected(self) -> None:
        completed, result = self.invoke(
            eligible_config(),
            eligible_observation(),
            boundary_digest_override="f" * 64,
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("boundaries.inventory-digest-mismatch", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_observation_failure_is_structured_no_go(self) -> None:
        completed, result = self.invoke(
            eligible_config(), eligible_observation(), observation_error=OSError("offline")
        )

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go-managed-pilot", result["decision"])
        self.assertIn("observation.failed:OSError", result["failures"])
        self.assertIn("evidenceDirectory", result)

    def test_observation_shape_failure_is_structured_no_go(self) -> None:
        completed, result = self.invoke(
            eligible_config(), eligible_observation(), observation_error=TypeError("shape")
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("observation.failed:TypeError", result["failures"])
        self.assertIn("evidenceDirectory", result)

    def test_probe_timeout_is_structured_no_go(self) -> None:
        completed, result = self.invoke(
            eligible_config(),
            eligible_observation(),
            probe_error=__import__("subprocess").TimeoutExpired("dotnet restore", 120),
        )

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go-managed-pilot", result["decision"])
        self.assertIn("probe.failed:TimeoutExpired", result["failures"])
        self.assertIn("evidenceDirectory", result)

    def test_evidence_write_failure_exits_nonzero(self) -> None:
        completed, result = self.invoke(
            eligible_config(),
            eligible_observation(),
            evidence_write_error=OSError("disk full"),
        )

        self.assertEqual(2, completed.returncode)
        self.assertEqual("no-go-managed-pilot", result["decision"])
        self.assertIn("evidence.write-failed:OSError", result["failures"])
        self.assertNotIn("evidenceDirectory", result)

    def test_second_evidence_write_failure_leaves_no_stale_go_artifact(self) -> None:
        test_state = PILOT_ROOT / ".test-state"
        test_state.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=test_state) as temporary:
            directory = evidence.create_evidence_directory(Path(temporary))
            original_write_text = Path.write_text

            def fail_report(path: Path, *args: object, **kwargs: object) -> int:
                if path.name == "report.md":
                    raise OSError("disk full during report")
                return original_write_text(path, *args, **kwargs)

            with patch.object(Path, "write_text", autospec=True, side_effect=fail_report):
                with self.assertRaises(OSError):
                    evidence.write_evidence(
                        directory,
                        {"decision": "go-managed-pilot", "failures": []},
                    )

            self.assertFalse(directory.exists())

    def test_evidence_schema_rejects_incomplete_artifact(self) -> None:
        schema = json.loads(
            PILOT_ROOT.joinpath("managed-gate-evidence.schema.json").read_text(
                encoding="utf-8"
            )
        )

        failures = validate({"schemaVersion": "maf-managed-dts-evidence/v1"}, schema)

        self.assertIn("$.decision:required", failures)
        self.assertIn("$.boundaries:required", failures)

    def assert_preflight_rejection(
        self,
        config: dict[str, object],
        observation: dict[str, object],
        failure: str,
    ) -> None:
        completed, result = self.invoke(config, observation)
        self.assertEqual(2, completed.returncode)
        self.assertIn(failure, result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_non_consumption_scheduler_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["scheduler"]["sku"] = "Dedicated"

        self.assert_preflight_rejection(
            eligible_config(), observation, "azure.scheduler-sku-not-consumption"
        )

    def test_inactive_trial_spending_limit_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["subscription"]["spendingLimit"] = "Off"

        self.assert_preflight_rejection(
            eligible_config(), observation, "azure.spending-limit-not-active"
        )

    def test_missing_budget_controls_are_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["budget"] = None

        self.assert_preflight_rejection(
            eligible_config(), observation, "azure.budget-unavailable"
        )

    def test_budget_amount_drift_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["budget"]["amount"] = 50

        self.assert_preflight_rejection(
            eligible_config(), observation, "azure.budget-amount-mismatch"
        )

    def test_azure_target_drift_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["taskHub"]["name"] = "wrong-hub"

        self.assert_preflight_rejection(
            eligible_config(), observation, "azure.task-hub-name-mismatch"
        )

    def test_stored_credential_configuration_is_rejected_before_probe(self) -> None:
        config = eligible_config()
        config["azure"]["clientSecret"] = "must-not-be-stored"

        self.assert_preflight_rejection(
            config, eligible_observation(), "security.stored-credential-field:clientSecret"
        )

    def test_stored_credential_in_environment_file_is_rejected(self) -> None:
        config = eligible_config()
        expected_connection = (
            "DURABLE_TASK_SCHEDULER_CONNECTION_STRING="
            f"Endpoint={config['azure']['endpoint']};"
            f"TaskHub={config['azure']['taskHubName']};Authentication=DefaultAzure"
        )

        completed, result = self.invoke(
            config,
            eligible_observation(),
            [expected_connection, "AZURE_CLIENT_SECRET=must-not-be-stored"],
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("security.credential-in-environment-file:AZURE_CLIENT_SECRET", result["failures"])
        self.assertFalse(result["probe"]["started"])

    def test_package_tuple_drift_is_rejected_before_probe(self) -> None:
        config = eligible_config()
        config["packages"]["durableTask"] = "1.19.0"

        self.assert_preflight_rejection(
            config, eligible_observation(), "provenance.durable-task-version-mismatch"
        )

    def test_observed_runtime_drift_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["provenance"]["dotnetSdk"] = "10.0.204"

        self.assert_preflight_rejection(
            eligible_config(), observation, "provenance.dotnet-sdk-mismatch"
        )

    def test_observed_package_lock_drift_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["provenance"]["packageLockSha256"] = "0" * 64

        self.assert_preflight_rejection(
            eligible_config(), observation, "provenance.package-lock-mismatch"
        )

    def test_observed_pilot_source_drift_is_rejected_before_probe(self) -> None:
        observation = eligible_observation()
        observation["provenance"]["pilotSourceSha256"] = "b" * 64

        self.assert_preflight_rejection(
            eligible_config(), observation, "provenance.pilot-source-mismatch"
        )

    def test_controller_replaces_worker_without_starting_a_second_run(self) -> None:
        config = eligible_config()
        config["probe"]["command"] = [sys.executable, "tests/fixtures/fake_worker.py"]
        with tempfile.TemporaryDirectory(dir=PILOT_ROOT / ".test-state") as temporary:
            result, failures = process_controller.run_probe(
                config, PILOT_ROOT, Path(temporary)
            )

        self.assertEqual([], failures)
        self.assertEqual(1, result["runStartCount"])
        self.assertEqual(
            {"checkpoint-one": 1, "checkpoint-two": 1},
            result["effects"],
        )
        self.assertEqual(
            {"managed-probe-worker-1", "managed-probe-worker-2"},
            set(result["workerPids"]),
        )
        self.assertEqual(2, len(set(result["workerPids"].values())))
        self.assertEqual(
            ["managed-probe-worker-1"],
            result["activityWorkers"]["checkpoint-one"],
        )
        self.assertEqual(
            ["managed-probe-worker-1", "managed-probe-worker-2"],
            result["activityWorkers"]["checkpoint-two"],
        )

    def test_success_writes_correlated_json_and_markdown_evidence(self) -> None:
        completed, result = self.invoke(eligible_config(), eligible_observation())

        self.assertEqual(0, completed.returncode, completed.stderr)
        evidence_directory = Path(result["evidenceDirectory"])
        decision = json.loads(
            evidence_directory.joinpath("decision.json").read_text(encoding="utf-8")
        )
        report = evidence_directory.joinpath("report.md").read_text(encoding="utf-8")
        self.assertEqual("maf-managed-dts-evidence/v1", decision["schemaVersion"])
        self.assertEqual("go-managed-pilot", decision["decision"])
        self.assertEqual(64, len(decision["configDigest"]))
        self.assertEqual(64, len(decision["observationDigest"]))
        self.assertTrue(decision["boundaries"]["unchanged"])
        for expected in (
            "Azure DTS Consumption",
            "DefaultAzure",
            "one durable run",
            "worker replacement",
            "exactly-once",
            "protected boundaries",
        ):
            self.assertIn(expected, report)

    def test_evidence_root_may_not_overlap_protected_boundary(self) -> None:
        test_state = PILOT_ROOT / ".test-state"
        test_state.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=test_state) as temporary:
            protected = Path(temporary) / "protected"
            protected.mkdir()
            evidence_root = protected / "evidence"
            boundaries = {
                "schemaVersion": "maf-managed-boundaries/v1",
                "boundaries": [
                    {
                        "name": "protected",
                        "path": str(protected),
                        "mode": "metadata-and-content-hash",
                    }
                ],
            }

            completed, result = self.invoke(
                eligible_config(),
                eligible_observation(),
                boundaries=boundaries,
                evidence_root_override=evidence_root,
            )

            self.assertEqual(2, completed.returncode)
            self.assertIn("isolation.evidence-path-overlap:protected", result["failures"])
            self.assertNotIn("evidenceDirectory", result)
            self.assertFalse(evidence_root.exists())


if __name__ == "__main__":
    unittest.main()
