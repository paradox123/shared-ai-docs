"""Ticket 04: external process, worker and authorized Operator HTTP/CLI seam."""
import json
import os
from pathlib import Path
import subprocess
import time
import unittest
from tests import test_control_plane_black_box as harness


class FakeCodexTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def start_fake(self, scenario="blocked"):
        port = harness.free_port()
        database = str(Path(self.scratch.name) / f'fake-{port}.sqlite')
        process = subprocess.Popen(['python3', str(harness.PILOT_ROOT / 'tests/fake_codex_provider.py'),
            '--port', str(port), '--database', database, '--scenario', scenario], start_new_session=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self.stop_process, process)
        for _ in range(100):
            status, _, _ = self.request('GET', '/diagnostics', port=port)
            if status == 200:
                return port
            time.sleep(.05)
        self.fail('fake provider not ready')

    def fake_worker_args(self, run_id, port, *extra):
        return ['dotnet', str(harness.WORKER_DLL), '--connection-string', self.connection_string,
            '--fixture', str(self.fixture_path), '--run-id', run_id, '--worker-id', 'fake-worker',
            '--fake-agent-origin', f'http://127.0.0.1:{port}', *extra]

    def run_fake(self, run_id, port, *extra):
        return harness.command_output(self.fake_worker_args(run_id, port, *extra), timeout=30)

    def test_external_attempt_has_ordered_redacted_transcript(self):
        run_id = self.new_run()
        port = self.start_fake()
        secret = json.loads(harness.FIXTURE.read_text())['redactionPolicy']['controlledCanaries'][0]['value']
        worker = self.run_fake(run_id, port, '--evidence-note', secret)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id, 'actor-observer')
        self.assertEqual('blocked', run['state'])
        agent = [a for a in run['activities'] if a['activityType'] == 'fake-codex']
        self.assertEqual(1, len(agent))
        attempt = next(a for a in run['attempts'] if a['activityId'] == agent[0]['activityId'])
        self.assertEqual('blocked', attempt['state'])
        session = attempt['session']
        self.assertEqual('blocked', session['status'])
        self.assertEqual(attempt['attemptId'], session['operationKey'])
        _, history, raw = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
        external = [e for e in history['events'] if 'sourceSequence' in e['payload']]
        self.assertEqual([1, 2, 3, 4, 5], [e['payload']['sourceSequence'] for e in external])
        self.assertEqual(['message', 'tool-call', 'tool-result', 'artifact', 'result'],
            [e['payload']['type'] for e in external])
        for index, event in enumerate(external):
            self.assertEqual(session['sessionId'], event['payload']['sessionId'])
            self.assertEqual(attempt['attemptId'], event['payload']['attemptId'])
            self.assertEqual(external[index - 1]['eventId'] if index else session['startedEventId'],
                event['payload']['causedByEventId'])
            self.assertTrue(event['redaction']['occurred'])
        for surface in [raw, json.dumps(run), worker.stdout, worker.stderr]:
            self.assertNotIn(secret, surface)
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['sessionCount'])

    def paused_worker(self, run_id, port, hook, *extra):
        output_path = Path(self.scratch.name) / f'{run_id}-{hook}.log'
        output = output_path.open('w')
        self.addCleanup(output.close)
        process = subprocess.Popen(self.fake_worker_args(run_id, port, '--pause-at', hook, *extra),
            stdout=output, stderr=output, start_new_session=True)
        self.addCleanup(self.stop_process, process)
        for _ in range(200):
            if hook in output_path.read_text():
                return process
            if process.poll() is not None:
                self.fail('worker exited before crash boundary: ' + output_path.read_text())
            time.sleep(.05)
        self.fail('worker did not reach crash boundary: ' + output_path.read_text())

    def agent_attempt(self, run_id):
        return next(a for a in self.read_run(run_id)['attempts'] if a.get('session'))

    def test_replacement_adopts_one_session_before_and_after_mapping(self):
        from concurrent.futures import ThreadPoolExecutor
        import signal
        for hook in ('after-session-start', 'after-session-mapping'):
            with self.subTest(hook=hook):
                run_id, port = self.new_run(), self.start_fake()
                worker = self.paused_worker(run_id, port, hook)
                before = self.agent_attempt(run_id)
                _, original, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                _, external, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, external['sessionCount'])
                os.killpg(worker.pid, signal.SIGKILL)
                worker.wait(timeout=10)
                with ThreadPoolExecutor(max_workers=2) as pool:
                    deliveries = list(pool.map(lambda _: self.run_fake(run_id, port), range(2)))
                for result in deliveries:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                after = self.agent_attempt(run_id)
                self.assertEqual(before['attemptId'], after['attemptId'])
                self.assertEqual('blocked', after['state'])
                self.assertEqual(external['sessions'][0]['sessionId'], after['session']['sessionId'])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertEqual(original['events'], history['events'][:len(original['events'])])
                for kind in ('AgentPreparationCompleted', 'AgentSessionStarted', 'AgentResultObserved'):
                    self.assertEqual(1, sum(e['eventType'] == kind for e in history['events']))
                _, external, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, external['sessionCount'])

    def test_blocked_original_survives_downstream_rejection_and_capture_crash(self):
        import signal
        run_id, port = self.new_run(), self.start_fake()
        options = ('--reject-blocked', 'true')
        worker = self.paused_worker(run_id, port, 'after-result-observed', *options)
        before = self.agent_attempt(run_id)
        original = before['session']['originalResult']
        self.assertEqual('blocked', original['status'])
        self.assertEqual('running', before['state'])
        os.killpg(worker.pid, signal.SIGKILL)
        worker.wait(timeout=10)
        result = self.run_fake(run_id, port, *options)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        after = self.agent_attempt(run_id)
        self.assertEqual('semantic-rejection', after['state'])
        self.assertEqual('blocked', after['session']['status'])
        self.assertEqual(original, after['session']['originalResult'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        captured = [e for e in history['events'] if e['eventType'] == 'AgentResultObserved']
        rejected = [e for e in history['events'] if e['eventType'] == 'AgentResultRejected']
        self.assertEqual(1, len(captured))
        self.assertEqual(1, len(rejected))
        self.assertEqual(captured[0]['eventId'], rejected[0]['payload']['originalResultEventId'])
        self.assertLess(captured[0]['position'], rejected[0]['position'])

    def test_failure_categories_are_public_and_preserve_originals(self):
        secret = json.loads(harness.FIXTURE.read_text())['redactionPolicy']['controlledCanaries'][0]['value']
        for scenario, category in [('process-failure', 'process-failure'), ('timeout', 'timeout'),
            ('transport-failure', 'transport-failure'), ('contract-incompatible', 'contract-incompatible'),
            ('schema-failure', 'schema-failure'), ('malformed-json', 'schema-failure'),
            ('infrastructure-failure', 'infrastructure-failure')]:
            with self.subTest(scenario=scenario):
                run_id, port = self.new_run(), self.start_fake(scenario)
                result = self.run_fake(run_id, port, '--agent-timeout-ms', '500', '--evidence-note', secret)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                attempt = self.agent_attempt(run_id)
                self.assertEqual(category, attempt['state'])
                self.assertEqual(category, attempt['session']['failureCategory'])
                _, events, raw = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertEqual(category, events['events'][-1]['payload']['category'])
                if scenario not in ('timeout', 'transport-failure'):
                    self.assertIsNotNone(attempt['session']['responseEventId'])
                if scenario == 'schema-failure':
                    self.assertEqual('blocked', attempt['session']['originalResult']['status'])
                    self.assertNotIn('schemaVersion', attempt['session']['originalResult'])
                repeat = self.run_fake(run_id, port, '--agent-timeout-ms', '500')
                self.assertEqual(0, repeat.returncode, repeat.stdout + repeat.stderr)
                self.assertEqual(attempt, self.agent_attempt(run_id))
                for surface in (raw, result.stdout, result.stderr, json.dumps(attempt)):
                    self.assertNotIn(secret, surface)

    def test_attempt_selection_is_authorized_and_open_capability_is_truthful(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake()
        result = self.run_fake(run_id, port, '--reject-blocked', 'true')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        attempt = self.agent_attempt(run_id)
        path = f"/api/v1/runs/{run_id}/attempts/{attempt['attemptId']}"
        status, detail, _ = self.request('GET', path, actor_id='actor-observer')
        self.assertEqual(200, status, detail)
        self.assertEqual(attempt, detail['attempt'])
        self.assertEqual(run_id, detail['runId'])
        self.assertEqual('r1', detail['provenance']['sourceRevision'])
        self.assertTrue(detail['events'])
        self.assertTrue(all(e['payload'].get('attemptId') == attempt['attemptId'] for e in detail['events']))
        capability = detail['attempt']['session']['openInCodex']
        self.assertEqual('unsupported', capability['mode'])
        self.assertFalse(capability['sameSession'])
        self.assertFalse(capability['appTaskVisible'])
        self.assertEqual('fake-adapter-has-no-codex-app-session', capability['reason'])
        self.assertIsNone(capability['url'])
        for actor in ('actor-unauthorized', 'worker-bot'):
            status, _, raw = self.request('GET', path, actor_id=actor)
            self.assertEqual(403, status)
            self.assertNotIn(attempt['session']['sessionId'], raw)
        status, _, _ = self.request('GET', f'/api/v1/runs/{run_id}/attempts/{uuid.uuid4()}')
        self.assertEqual(404, status)
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        exit_code, selected, _ = self.operator_cli('attempt', '--run-id', run_id,
            '--attempt-id', attempt['attemptId'], '--actor-id', 'actor-observer')
        self.assertEqual(0, exit_code, selected)
        self.assertEqual(detail, selected)

    def test_unavailable_store_is_infrastructure_failure_without_fabricated_history(self):
        run_id, port = self.new_run(), self.start_fake()
        arguments = self.fake_worker_args(run_id, port)
        arguments[arguments.index('--connection-string') + 1] = (
            f'Host=127.0.0.1;Port={harness.free_port()};Database=missing;Username=missing;Timeout=1')
        result = harness.command_output(arguments, timeout=10)
        self.assertEqual(2, result.returncode)
        self.assertEqual('infrastructure-failure', json.loads(result.stdout)['category'])
        self.assertEqual('admitted', self.read_run(run_id)['state'])
        _, external, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(0, external['sessionCount'])

    def test_inconsistent_adapter_correlation_and_transcript_fail_closed(self):
        for scenario in ('wrong-operation', 'sequence-gap', 'conflicting-replay', 'null-event'):
            with self.subTest(scenario=scenario):
                run_id, port = self.new_run(), self.start_fake(scenario)
                result = self.run_fake(run_id, port)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                attempt = self.agent_attempt(run_id)
                self.assertEqual('schema-failure', attempt['state'])
                self.assertIsNotNone(attempt['session']['observedResponse'])
                _, external, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, external['sessionCount'])

    def test_redelivery_cannot_change_durable_adapter_assignment(self):
        run_id, original_port = self.new_run(), self.start_fake()
        self.assertEqual(0, self.run_fake(run_id, original_port).returncode)
        original = self.agent_attempt(run_id)
        different_port = self.start_fake()
        result = self.run_fake(run_id, different_port)
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual('agent-assignment-conflict', json.loads(result.stdout)['code'])
        self.assertEqual(original, self.agent_attempt(run_id))
        _, external, _ = self.request('GET', '/diagnostics', port=different_port)
        self.assertEqual(0, external['sessionCount'])


if __name__ == '__main__':
    unittest.main()
