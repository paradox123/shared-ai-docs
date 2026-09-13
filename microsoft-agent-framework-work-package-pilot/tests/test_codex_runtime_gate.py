import json
import os
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
import signal
import time

ROOT = Path(__file__).resolve().parents[1]


class CodexRuntimeGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='wpcp-gate-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / 'config.json'
        self.run_id, self.attempt_id = str(uuid.uuid4()), str(uuid.uuid4())

    def gate_args(self):
        return [sys.executable, str(ROOT / 'codex_runtime_gate.py'),
            '--config', str(self.config), '--state-dir', str(self.root / 'state'),
            '--run-id', self.run_id, '--attempt-id', self.attempt_id]

    def gate(self, *extra):
        result = subprocess.run([*self.gate_args(), *extra],
            capture_output=True, text=True, timeout=90)
        self.assertEqual(2, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_runtime_drift_stops_before_executable_is_started(self):
        executable = self.root / 'must-not-start'
        marker = self.root / 'started'
        executable.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\n')
        executable.chmod(0o700)
        self.config.write_text(json.dumps({'executable': str(executable),
            'version': 'codex-cli 0.153.4', 'sha256': '0' * 64}))
        report = self.gate()
        self.assertEqual(['runtime-drift'], report['reasons'])
        self.assertEqual(self.run_id, report['runId'])
        self.assertEqual(self.attempt_id, report['attemptId'])
        self.assertFalse(marker.exists())

    def test_version_drift_stops_before_session_creation(self):
        executable = self.root / 'version-only'
        executable.write_text('#!/bin/sh\nprintf "codex-cli 0.0.0\\n"\n')
        executable.chmod(0o700)
        self.config.write_text(json.dumps({'executable': str(executable),
            'version': 'codex-cli 0.153.4',
            'sha256': hashlib.sha256(executable.read_bytes()).hexdigest()}))
        report = self.gate()
        self.assertEqual(['runtime-version-mismatch'], report['reasons'])
        self.assertNotIn('process', report)

    def test_invalid_configuration_is_a_visible_preflight_failure(self):
        self.config.write_text('{invalid')
        report = self.gate()
        self.assertEqual(['preflight-configuration-invalid'], report['reasons'])
        self.assertFalse(report['issueWorkStarted'])

    @unittest.skipUnless(os.environ.get('WPCP_REAL_CODEX_PROBE') == '1', 'explicit real-runtime probe')
    def test_real_session_capabilities_are_reported_without_enabling_unsafe_open(self):
        self.config.write_text((ROOT / 'codex-runtime-pin.json').read_text())
        report = self.gate()
        self.assertEqual('passed', report.get('capabilities', {}).get('startFresh', {}).get('status'))
        for capability in ('read', 'resume', 'fork', 'interrupt', 'outputSchema', 'tools', 'protocol'):
            self.assertIn(capability, report['capabilities'])
        self.assertEqual('no-go', report['decision'])
        self.assertFalse(report['issueWorkStarted'])
        self.assertEqual('passed', report['capabilities']['sandbox']['status'])
        self.assertTrue(report['capabilities']['sandbox']['outsideWriteDenied'])
        self.assertTrue(report['capabilities']['sandbox']['networkDenied'])
        self.assertEqual('passed', report['capabilities']['timeout']['status'])
        self.assertFalse(report['capabilities']['timeout']['lateOutputObserved'])

    @unittest.skipUnless(os.environ.get('WPCP_REAL_CODEX_PROBE') == '1', 'explicit real-runtime probe')
    def test_real_prompt_hook_blocks_input_with_correlated_session_and_turn(self):
        self.config.write_text((ROOT / 'codex-runtime-pin.json').read_text())
        report = self.gate()
        hook = report['capabilities'].get('promptHook', {})
        self.assertEqual('passed', hook.get('status'))
        self.assertEqual(report['capabilities']['startFresh']['sessionId'], hook['sessionId'])
        self.assertTrue(hook['turnId'])
        self.assertEqual('blocked', hook['hookStatus'])
        self.assertEqual('completed', hook['turnStatus'])
        self.assertFalse(hook['agentOutputObserved'])
        self.assertFalse(hook['leaseIntegrationVerified'])
        self.assertEqual('no-go', report['decision'])

    @unittest.skipUnless(os.environ.get('WPCP_REAL_CODEX_PROBE') == '1', 'explicit real-runtime probe')
    def test_replay_returns_original_probe_without_creating_another_session(self):
        self.config.write_text((ROOT / 'codex-runtime-pin.json').read_text())
        first = self.gate()
        second = self.gate()
        self.assertEqual(first['capabilities']['startFresh']['sessionId'],
                         second['capabilities']['startFresh']['sessionId'])
        self.assertEqual(first, second)

    @unittest.skipUnless(os.environ.get('WPCP_REAL_CODEX_PROBE') == '1', 'explicit real-runtime probe')
    def test_session_start_crash_stops_owned_process_and_replay_never_restarts(self):
        self.config.write_text((ROOT / 'codex-runtime-pin.json').read_text())
        process = subprocess.Popen([*self.gate_args(), '--pause-at', 'after-session-start'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                before = self.gate('--read')
                if before.get('faultHook') == 'after-session-start' or process.poll() is not None:
                    break
                time.sleep(.05)
            self.assertEqual('after-session-start', before.get('faultHook'))
            self.assertEqual('dispatching', before['sessionStartState'])
            group = before['process']['processGroupId']
            process.kill()
            process.wait(timeout=5)

            for _ in range(100):
                # macOS can return EPERM for a group containing only zombies.
                # Inspect actual process states; permission errors are not proof of stop.
                table = subprocess.run(['ps', '-axo', 'pid=,pgid=,stat='], capture_output=True,
                                       text=True, check=True).stdout
                live = [line for line in table.splitlines() if len(line.split()) == 3
                        and line.split()[1] == str(group) and 'Z' not in line.split()[2]]
                if not live:
                    break
                time.sleep(.05)
            else:
                self.fail('owned runtime group survived its adapter')
            recovered = self.gate()
            self.assertEqual(['session-start-uncertain'], recovered['reasons'])
            self.assertFalse(recovered['recovery']['newSessionStarted'])
            self.assertEqual(before['process'], recovered['process'])
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)

    @unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1', 'explicit authenticated endpoint probe')
    def test_real_endpoint_schema_and_completed_session_continuations(self):
        config = json.loads((ROOT / 'codex-runtime-pin.json').read_text())
        config['probeEndpoint'] = True
        config['rpcTimeoutSeconds'] = 45
        self.config.write_text(json.dumps(config))
        report = self.gate()
        self.assertEqual('passed', report['capabilities']['outputSchema']['status'], report)
        for capability in ('resume', 'fork', 'interrupt'):
            self.assertEqual('passed', report['capabilities'][capability]['status'], report)
