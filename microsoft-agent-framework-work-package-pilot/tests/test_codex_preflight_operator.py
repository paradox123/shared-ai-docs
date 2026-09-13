"""Runtime gate failure through the existing authenticated Operator boundary."""
import json
import os
from pathlib import Path
import sys
import unittest
from tests import test_control_plane_black_box as harness


class CodexPreflightOperatorTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def worker_arguments(self, run_id, config):
        path = Path(self.scratch.name) / (run_id + '.json')
        path.write_text(json.dumps(config))
        return ['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'runtime-preflight',
            '--codex-preflight-config', str(path), '--codex-state-root', str(Path(self.scratch.name) / 'codex'),
            '--codex-python', sys.executable]

    def test_gate_failure_survives_worker_replay_and_api_replacement(self):
        run_id = self.new_run()
        config = json.loads((harness.PILOT_ROOT / 'codex-runtime-pin.json').read_text())
        config['executable'] = sys.executable
        config['sha256'] = '0' * 64
        args = self.worker_arguments(run_id, config)
        worker = harness.command_output(args)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id)
        self.assertEqual('capability-unavailable', run['state'])
        activity = next(a for a in run['activities'] if a['activityType'] == 'real-codex-preflight')
        attempt = next(a for a in run['attempts'] if a['activityId'] == activity['activityId'])
        report = attempt['session']['observedResponse']
        self.assertEqual(['runtime-drift'], report['reasons'])
        self.assertEqual(run_id, report['runId'])
        self.assertEqual(attempt['attemptId'], report['attemptId'])
        self.assertFalse(report['issueWorkStarted'])
        self.assertIsNone(attempt['session']['sessionId'])
        self.assertEqual('unsupported', attempt['session']['openInCodex']['mode'])
        replay = harness.command_output(args)
        self.assertEqual(0, replay.returncode, replay.stdout + replay.stderr)
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        status, detail, raw = self.operator_cli('attempt', '--run-id', run_id,
            '--attempt-id', attempt['attemptId'], '--actor-id', 'actor-observer')
        self.assertEqual(0, status, raw)
        self.assertEqual(report, detail['attempt']['session']['observedResponse'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        captures = [e for e in history['events'] if e['eventType'] == 'AgentAdapterResponseObserved']
        self.assertEqual(1, len(captures))
        changed = list(args)
        changed[changed.index('--codex-state-root') + 1] = str(Path(self.scratch.name) / 'other-state')
        conflict = harness.command_output(changed)
        self.assertEqual(2, conflict.returncode, conflict.stdout)
        self.assertEqual('agent-assignment-conflict', json.loads(conflict.stdout)['code'])

    def test_missing_interpreter_is_a_visible_terminal_prerequisite_failure(self):
        run_id = self.new_run()
        config = json.loads((harness.PILOT_ROOT / 'codex-runtime-pin.json').read_text())
        args = self.worker_arguments(run_id, config)
        args[args.index('--codex-python') + 1] = str(Path(self.scratch.name) / 'missing-python')
        worker = harness.command_output(args)
        self.assertEqual(0, worker.returncode, worker.stdout)
        run = self.read_run(run_id)
        self.assertEqual('capability-unavailable', run['state'])
        attempt = next(a for a in run['attempts'] if a.get('session'))
        self.assertEqual(['gate-process-unavailable'], attempt['session']['observedResponse']['reasons'])

    @unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1', 'explicit authenticated endpoint probe')
    def test_real_capabilities_and_no_go_are_readable_under_the_original_run(self):
        run_id = self.new_run()
        config = json.loads((harness.PILOT_ROOT / 'codex-runtime-pin.json').read_text())
        config.update(probeEndpoint=True, rpcTimeoutSeconds=45)
        args = self.worker_arguments(run_id, config)
        worker = harness.command_output(args, timeout=120)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id, 'actor-observer')
        attempt = next(a for a in run['attempts'] if a.get('session'))
        report = attempt['session']['observedResponse']
        self.assertEqual('capability-unavailable', run['state'])
        self.assertEqual(['native-client-lease-fencing-unverified'], report['reasons'])
        self.assertEqual(attempt['attemptId'], report['attemptId'])
        self.assertEqual(run_id, report['runId'])
        for capability in ('startFresh', 'read', 'resume', 'fork', 'interrupt', 'outputSchema', 'sandbox', 'timeout', 'promptHook'):
            self.assertEqual('passed', report['capabilities'][capability]['status'], report)
        session = report['capabilities']['startFresh']['sessionId']
        self.assertEqual(session, attempt['session']['sessionId'])
        self.assertEqual(session, report['capabilities']['resume']['sessionId'])
        self.assertEqual(session, report['capabilities']['promptHook']['sessionId'])
        self.assertEqual('blocked', report['capabilities']['promptHook']['hookStatus'])
        self.assertFalse(report['capabilities']['promptHook']['leaseIntegrationVerified'])
        self.assertEqual(session, report['capabilities']['fork']['parentSessionId'])
        self.assertNotEqual(session, report['capabilities']['fork']['sessionId'])
        self.assertFalse(report['issueWorkStarted'])
        self.assertIsNone(attempt['session']['openInCodex']['url'])
        self.assertEqual('stopped', report['processStop']['status'])
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        replay = harness.command_output(args)
        self.assertEqual(0, replay.returncode, replay.stdout + replay.stderr)
        _, detail, _ = self.operator_cli('attempt', '--run-id', run_id, '--attempt-id', attempt['attemptId'])
        self.assertEqual(report, detail['attempt']['session']['observedResponse'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
        if destination := os.environ.get('WPCP_CODEX_EVIDENCE_DIR'):
            root = Path(destination)
            root.mkdir(parents=True, exist_ok=True)
            (root / 'real-runtime-public-proof.json').write_text(json.dumps({
                'report': report, 'attempt': detail, 'history': history,
                'limits': ['native app not opened: lease fencing unverified',
                           'no issue implementation', 'explicit local dispatch',
                           'controlled GitHub authorization provider']}, indent=2) + '\n')
