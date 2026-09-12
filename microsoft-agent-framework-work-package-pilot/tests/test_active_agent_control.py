"""Ticket 07: public HTTP/CLI and independent worker/adapter process proof."""
import json
import subprocess
import os
import signal
import time
from pathlib import Path
import uuid
import unittest
from tests import test_control_plane_black_box as harness
from tests import test_fake_codex_attempt as fake


class ActiveAgentControlTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def setUp(self):
        self.proof_runs = []
        self.live_providers = {}

    def new_run(self):
        run_id = super().new_run()
        self.proof_runs.append(run_id)
        return run_id

    def tearDown(self):
        destination = os.environ.get('WPCP_ACTIVE_PROOF_DIR')
        if destination:
            directory = Path(destination)
            directory.mkdir(parents=True, exist_ok=True)
            proof = []
            for run_id in self.proof_runs:
                run = self.read_run(run_id, 'actor-observer')
                status, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
                self.assertEqual(200, status)
                proof.append({'run': run, 'history': history})
            text = json.dumps(proof, indent=2) + '\n'
            for canary in json.loads(harness.FIXTURE.read_text())['redactionPolicy']['controlledCanaries']:
                self.assertNotIn(canary['value'], text)
            (directory / f'{self._testMethodName}.json').write_text(text)

    def start_fake(self, scenario='normal'):
        port = harness.free_port()
        process = subprocess.Popen(['python3', str(harness.PILOT_ROOT / 'tests/live_codex_provider.py'),
            '--port', str(port), '--database', str(Path(self.scratch.name) / f'live-{port}.sqlite'),
            '--scenario', scenario], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(self.stop_process, process)
        self.live_providers[port] = process
        for _ in range(100):
            status, _, _ = self.request('GET', '/diagnostics', port=port)
            if status == 200:
                return port
            time.sleep(.05)
        self.fail('live provider not ready')

    fake_worker_args = fake.FakeCodexTests.fake_worker_args
    run_fake = fake.FakeCodexTests.run_fake
    fence = fake.FakeCodexTests.fence
    claim = fake.FakeCodexTests.claim

    def start_live(self, run_id, port, key):
        result = self.run_fake(run_id, port, '--live-activity-key', key)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def command(self, run_id, attempt_id, mode='queue', actor='actor-authorized', **extra):
        control = self.read_run(run_id)['control']
        body = dict(targetAttemptId=attempt_id, expectedRunVersion=control['runVersion'],
                    expectedHeadSha=control['headSha'], leaseEpoch=control['leaseEpoch'],
                    commandId=str(uuid.uuid4()), message=None if mode == 'cancel' else 'next instruction')
        body.update(extra)
        return self.request('POST', f'/api/v1/runs/{run_id}/agent-commands/{mode}', body, actor_id=actor)

    def live(self, run_id):
        return [a['liveOperation'] for a in self.read_run(run_id)['attempts'] if a.get('liveOperation')]

    def test_queue_replay_retains_order_and_redacts_cli_readback(self):
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        self.claim(run_id, self.read_run(run_id))
        target = self.live(run_id)[0]['attemptId']
        control = self.read_run(run_id)['control']
        secret = json.loads(harness.FIXTURE.read_text())['redactionPolicy']['controlledCanaries'][0]['value']
        body = dict(targetAttemptId=target, expectedRunVersion=control['runVersion'],
                    expectedHeadSha=control['headSha'], leaseEpoch=control['leaseEpoch'],
                    commandId=str(uuid.uuid4()), message=secret)
        route = f'/api/v1/runs/{run_id}/agent-commands/queue'
        status, first, _ = self.request('POST', route, body)
        self.assertEqual(202, status, first)
        status, replay, _ = self.request('POST', route, body)
        self.assertEqual(202, status, replay)
        self.assertEqual(first['command'], replay['command'])
        status, conflict, _ = self.request('POST', route, dict(body, message='substitution'))
        self.assertEqual(409, status, conflict)
        self.assertEqual('agent-command-conflict', conflict['code'])
        code, second, raw = self.operator_cli('queue', '--run-id', run_id,
            *self.fence(self.read_run(run_id)), '--command-id', str(uuid.uuid4()), '--message', 'second')
        self.assertEqual(0, code, raw)
        commands = self.live(run_id)[0]['commands']
        self.assertEqual([first['command']['commandId'], second['command']['commandId']],
                         [c['commandId'] for c in commands])
        self.assertEqual([1, 2], [c['queuePosition'] for c in commands])
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        code, detail, raw = self.operator_cli('attempt', '--run-id', run_id, '--attempt-id', target)
        self.assertEqual(0, code, raw)
        self.assertEqual(commands, detail['attempt']['liveOperation']['commands'])
        self.assertNotIn(secret, raw)
        self.assertTrue(any(e['redaction']['occurred'] for e in detail['events']))

    def deliver(self, run_id, port, *extra):
        result = self.run_fake(run_id, port, '--deliver-active', 'true', *extra)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def complete(self, port, operation):
        status, result, _ = self.request('POST', f"/operations/{operation['operationKey']}/complete", {}, port=port)
        self.assertEqual(200, status, result)

    def test_queue_delivers_one_response_at_a_time_after_completion(self):
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        self.claim(run_id, self.read_run(run_id))
        target = self.live(run_id)[0]['attemptId']
        self.command(run_id, target)
        self.command(run_id, target)
        initial = self.live(run_id)[0]['currentOperation']
        self.assertEqual('running', initial['processStatus'])
        self.deliver(run_id, port)
        _, diag, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diag['operationCount'])
        for index in range(2):
            self.complete(port, self.live(run_id)[0]['currentOperation'])
            self.deliver(run_id, port)
            active = self.live(run_id)[0]
            self.assertEqual(active['commands'][index]['commandId'], active['currentOperation']['commandId'])
            self.assertEqual('running', active['currentOperation']['processStatus'])
        self.complete(port, self.live(run_id)[0]['currentOperation'])
        self.deliver(run_id, port)
        active = self.live(run_id)[0]
        self.assertEqual(['completed', 'completed'], [c['state'] for c in active['commands']])
        _, diag, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(3, diag['operationCount'])
        self.assertEqual([], diag['alive'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        replies = [e['payload'] for e in history['events'] if e['eventType'] == 'ActiveAgentResponseObserved']
        self.assertEqual([None] + [c['commandId'] for c in active['commands']], [r['commandId'] for r in replies])

    def test_interrupt_stops_reconciles_and_runs_next_before_queue(self):
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        self.start_live(run_id, port, 'two')
        self.claim(run_id, self.read_run(run_id))
        first, other = self.live(run_id)
        target = first['attemptId']
        self.command(run_id, target)
        status, interrupt, _ = self.command(run_id, target, 'interrupt', reason='change direction')
        self.assertEqual(202, status, interrupt)
        accepted = next(a for a in self.live(run_id) if a['attemptId'] == target)
        self.assertEqual(first['fenceEpoch'] + 1, accepted['fenceEpoch'])
        status, competing, _ = self.command(run_id, target, 'interrupt', reason='another direction')
        self.assertEqual(409, status, competing)
        self.assertEqual('operation-stop-pending', competing['code'])
        self.deliver(run_id, port)
        active = next(a for a in self.live(run_id) if a['attemptId'] == target)
        self.assertEqual(interrupt['command']['commandId'], active['currentOperation']['commandId'])
        self.assertEqual('running', active['currentOperation']['processStatus'])
        self.assertEqual(other, next(a for a in self.live(run_id) if a['attemptId'] == other['attemptId']))
        _, diag, _ = self.request('GET', '/diagnostics', port=port)
        old = next(o for o in diag['operations'] if o['operationKey'] == first['currentOperation']['operationKey'])
        self.assertEqual('stopped', old['processStatus'])
        self.assertNotIn(old['operationKey'], diag['alive'])
        self.complete(port, active['currentOperation'])
        self.deliver(run_id, port)
        active = next(a for a in self.live(run_id) if a['attemptId'] == target)
        self.assertEqual(active['commands'][0]['commandId'], active['currentOperation']['commandId'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        types = [e['eventType'] for e in history['events']]
        self.assertLess(types.index('ActiveAgentEffectsReconciled'), types.index('ActiveAgentCommandDeliveryRequested'))
        self.assertFalse(any('Repair' in kind for kind in types))

    def test_cancel_scopes_preserve_parallel_attempt_without_automatic_retry(self):
        for scope in ('operation', 'attempt'):
            with self.subTest(scope=scope):
                run_id, port = self.new_run(), self.start_fake()
                self.start_live(run_id, port, 'one')
                self.start_live(run_id, port, 'two')
                self.claim(run_id, self.read_run(run_id))
                first, other = self.live(run_id)
                target = first['attemptId']
                self.command(run_id, target)
                status, cancelled, _ = self.command(run_id, target, 'cancel', reason='operator stopped scope', scope=scope)
                self.assertEqual(202, status, cancelled)
                pending_attempt = next(a for a in self.read_run(run_id)['attempts'] if a['attemptId'] == target)
                self.assertIsNone(pending_attempt['completedAt'], 'Cancellation completes only after the stop receipt')
                self.deliver(run_id, port)
                selected = next(a for a in self.live(run_id) if a['attemptId'] == target)
                self.assertEqual(other, next(a for a in self.live(run_id) if a['attemptId'] == other['attemptId']))
                self.assertEqual('completed', selected['commands'][-1]['state'])
                if scope == 'attempt':
                    self.assertEqual('cancelled', selected['state'])
                    self.assertEqual('rejected', selected['commands'][0]['state'])
                    self.assertEqual('attempt-cancelled', selected['commands'][0]['rejectionReason'])
                else:
                    self.assertEqual('running', selected['state'])
                    self.assertEqual(selected['commands'][0]['commandId'], selected['currentOperation']['commandId'])
                self.start_live(run_id, port, 'one')
                self.assertEqual(selected, next(a for a in self.live(run_id) if a['attemptId'] == target))
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertFalse(any('Repair' in e['eventType'] for e in history['events']))

    def paused_active(self, run_id, port, hook, *extra):
        log = Path(self.scratch.name) / f'{uuid.uuid4()}.log'
        output = log.open('w')
        self.addCleanup(output.close)
        process = subprocess.Popen(self.fake_worker_args(run_id, port, '--pause-at', hook, *extra),
            stdin=subprocess.PIPE, stdout=output, stderr=output, start_new_session=True, text=True)
        self.addCleanup(process.stdin.close)
        self.addCleanup(self.stop_process, process)
        for _ in range(200):
            if hook in log.read_text():
                return process
            if process.poll() is not None:
                self.fail('worker exited before crash boundary: ' + log.read_text())
            time.sleep(.05)
        self.fail('worker did not reach crash boundary: ' + log.read_text())

    def test_worker_replacement_adopts_process_and_command_receipts_once(self):
        from concurrent.futures import ThreadPoolExecutor
        for hook in ('after-active-response', 'after-active-stop', 'before-active-delivery', 'after-active-delivery'):
            with self.subTest(hook=hook):
                run_id, port = self.new_run(), self.start_fake()
                if hook == 'after-active-response':
                    worker = self.paused_active(run_id, port, hook, '--live-activity-key', 'one')
                else:
                    self.start_live(run_id, port, 'one')
                    self.claim(run_id, self.read_run(run_id))
                    target = self.live(run_id)[0]['attemptId']
                    mode = 'interrupt' if hook == 'after-active-stop' else 'queue'
                    options = dict(reason='recover interrupted operation') if mode == 'interrupt' else {}
                    self.command(run_id, target, mode, **options)
                    if mode == 'queue':
                        self.complete(port, self.live(run_id)[0]['currentOperation'])
                    worker = self.paused_active(run_id, port, hook, '--deliver-active', 'true')
                os.killpg(worker.pid, signal.SIGKILL)
                worker.wait(timeout=10)
                with ThreadPoolExecutor(max_workers=2) as pool:
                    list(pool.map(lambda _: self.deliver(run_id, port), range(2)))
                current = self.live(run_id)[0]
                self.assertEqual('running', current['currentOperation']['processStatus'])
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1 if hook == 'after-active-response' else 2, diagnostics['operationCount'])
                self.assertEqual([current['currentOperation']['operationKey']], diagnostics['alive'])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                delivered = [e for e in history['events'] if e['eventType'] == 'ActiveAgentCommandDeliveryRequested']
                self.assertEqual(0 if hook == 'after-active-response' else 1, len(delivered))

    def test_delayed_running_receipt_cannot_regress_completed_operation(self):
        run_id, port = self.new_run(), self.start_fake()
        worker = self.paused_active(run_id, port, 'after-active-response', '--live-activity-key', 'one')
        operation = self.live(run_id)[0]['currentOperation']
        self.complete(port, operation)
        self.deliver(run_id, port)
        before = self.live(run_id)[0]
        self.assertEqual('completed', before['state'])
        worker.stdin.write('\n')
        worker.stdin.flush()
        worker.wait(timeout=10)
        self.assertEqual(0, worker.returncode)
        self.assertEqual(before, self.live(run_id)[0], 'A late running receipt must not replace the completed response')

    def test_stop_before_delayed_start_and_late_output_are_history_only(self):
        for hook in ('before-active-dispatch', 'after-active-response'):
            with self.subTest(hook=hook):
                run_id, port = self.new_run(), self.start_fake()
                worker = self.paused_active(run_id, port, hook, '--live-activity-key', 'one')
                self.claim(run_id, self.read_run(run_id))
                old = self.live(run_id)[0]['currentOperation']
                target = self.live(run_id)[0]['attemptId']
                self.command(run_id, target, 'interrupt', reason='supersede old operation')
                self.deliver(run_id, port)
                before = self.live(run_id)[0]
                head = self.read_run(run_id)['control']['headSha']
                worker.stdin.write('\n')
                worker.stdin.flush()
                worker.wait(timeout=10)
                self.assertEqual(0, worker.returncode)
                self.assertEqual(before, self.live(run_id)[0])
                self.assertEqual(head, self.read_run(run_id)['control']['headSha'])
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(2, diagnostics['operationCount'])
                self.assertNotIn(old['operationKey'], diagnostics['alive'])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                late = [e for e in history['events'] if e['eventType'] == 'ActiveAgentLateOutputObserved']
                if hook == 'after-active-response':
                    self.assertEqual(1, len(late))
                    self.assertTrue(late[0]['payload']['historyOnly'])
                    self.assertEqual(old['operationKey'], late[0]['payload']['operationKey'])

    def test_conflicting_reconciliation_is_visible_and_blocks_delivery(self):
        run_id, port = self.new_run(), self.start_fake('conflicting-effects')
        self.start_live(run_id, port, 'one')
        self.claim(run_id, self.read_run(run_id))
        target = self.live(run_id)[0]['attemptId']
        self.command(run_id, target, 'interrupt', reason='wait for reconciled effects')
        self.run_fake(run_id, port, '--deliver-active', 'true')
        pending = self.live(run_id)[0]
        self.assertEqual('queued', pending['commands'][0]['state'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        rejected = [e for e in history['events'] if e['eventType'] == 'ActiveAgentReceiptRejected']
        self.assertEqual(1, len(rejected), 'Rejected reconciliation must remain observable to another operator')
        self.run_fake(run_id, port, '--deliver-active', 'true')
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['operationCount'])
        self.assertEqual([], diagnostics['alive'])
        self.assertEqual(pending, self.live(run_id)[0])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(1, sum(e['eventType'] == 'ActiveAgentReceiptRejected' for e in history['events']))

    def test_api_replacement_before_response_read_preserves_accepted_command(self):
        import http.client
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        self.claim(run_id, self.read_run(run_id))
        control = self.read_run(run_id)['control']
        target = self.live(run_id)[0]['attemptId']
        body = dict(targetAttemptId=target, expectedRunVersion=control['runVersion'],
            expectedHeadSha=control['headSha'], leaseEpoch=control['leaseEpoch'],
            commandId=str(uuid.uuid4()), message='survive lost response')
        route = f'/api/v1/runs/{run_id}/agent-commands/queue'
        connection = http.client.HTTPConnection('127.0.0.1', self.api_port, timeout=10)
        connection.request('POST', route, json.dumps(body), {'Content-Type': 'application/json',
            'X-Wpcp-Fixture-Access': self.fixture_access_token,
            'Authorization': 'Bearer ' + self.provider.tokens['actor-authorized']})
        response = connection.getresponse()
        self.assertEqual(202, response.status)
        cls = type(self)
        os.killpg(cls.api.pid, signal.SIGKILL)
        cls.api.wait(timeout=10)
        connection.close()
        cls.start_api(excluded_ports={cls.api_port})
        status, replay, _ = self.request('POST', route, body)
        self.assertEqual(202, status, replay)
        self.complete(port, self.live(run_id)[0]['currentOperation'])
        self.deliver(run_id, port)
        self.assertEqual(body['commandId'], self.live(run_id)[0]['currentOperation']['commandId'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(1, sum(e['eventType'] == 'ActiveAgentCommandAccepted' for e in history['events']))

    def test_invalid_commands_preserve_history_and_human_attribution(self):
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        self.claim(run_id, self.read_run(run_id))
        target = self.live(run_id)[0]['attemptId']
        _, before, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        cases = [('queue', dict(expectedRunVersion=1)), ('queue', dict(expectedHeadSha='f' * 40)),
            ('queue', dict(leaseEpoch=0)), ('queue', dict(targetAttemptId=str(uuid.uuid4()))),
            ('interrupt', dict(reason='')), ('cancel', dict(reason='stop', scope='run'))]
        for mode, extra in cases:
            status, _, _ = self.command(run_id, target, mode, **extra)
            self.assertIn(status, (400, 409))
        _, after, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(before['events'], after['events'])
        status, accepted, _ = self.command(run_id, target)
        self.assertEqual(202, status, accepted)
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        event = next(e for e in history['events'] if e['eventType'] == 'ActiveAgentCommandAccepted')
        self.assertEqual({'kind': 'human', 'provider': 'github', 'subjectId': '101'}, event['payload'].get('actor'))

    def test_live_attempt_cannot_acquire_fabricated_repository_provenance(self):
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        plan = dict(repository={'repositoryId': 'repo-1', 'fullName': 'pilot/fixture', 'providerRepositoryId': 9001},
            localPath=self.scratch.name, remoteName='origin', baseBranch='main',
            providerOrigin=f'http://127.0.0.1:{port}', agentOrigin=f'http://127.0.0.1:{port}',
            expectedBaseSha='a' * 40, predecessorIssueNumber=None)
        path = Path(self.scratch.name) / f'{run_id}-plan.json'
        path.write_text(json.dumps(plan))
        result = self.run_fake(run_id, port, '--repository-plan', str(path))
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertEqual('agent-assignment-conflict', json.loads(result.stdout)['code'])
        self.assertIsNone(self.read_run(run_id)['repositoryExecution'])

    def test_repository_registration_waits_for_live_process_even_after_worker_exit(self):
        live_run, managed_run, port = self.new_run(), self.new_run(), self.start_fake()
        self.start_live(live_run, port, 'one')
        path = Path(self.scratch.name) / f'{managed_run}-plan.json'
        path.write_text(json.dumps(dict(
            repository={'repositoryId': 'repo-1', 'fullName': 'pilot/fixture', 'providerRepositoryId': 9001},
            localPath=self.scratch.name, remoteName='origin', baseBranch='main',
            providerOrigin=f'http://127.0.0.1:{port}', agentOrigin=f'http://127.0.0.1:{port}',
            expectedBaseSha='a' * 40, predecessorIssueNumber=None)))
        result = self.run_fake(managed_run, port, '--repository-plan', str(path))
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertEqual('repository-registration-busy', json.loads(result.stdout)['code'])
        self.assertIsNone(self.read_run(managed_run)['repositoryExecution'])

    def test_unavailable_attempt_does_not_block_parallel_command_delivery(self):
        run_id, first_port, second_port = self.new_run(), self.start_fake(), self.start_fake()
        self.start_live(run_id, first_port, 'one')
        self.start_live(run_id, second_port, 'two')
        self.claim(run_id, self.read_run(run_id))
        first, second = self.live(run_id)
        self.command(run_id, second['attemptId'])
        self.complete(second_port, second['currentOperation'])
        self.stop_process(self.live_providers[first_port])
        self.run_fake(run_id, second_port, '--deliver-active', 'true')
        after = next(a for a in self.live(run_id) if a['attemptId'] == second['attemptId'])
        self.assertEqual(after['commands'][0]['commandId'], after['currentOperation']['commandId'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        unavailable = [e for e in history['events'] if e['eventType'] == 'ActiveAgentDeliveryUnavailable']
        self.assertEqual(1, len(unavailable))
        self.assertEqual(first['attemptId'], unavailable[0]['payload']['attemptId'])

    def test_stop_receipt_must_match_the_bound_process(self):
        run_id, port = self.new_run(), self.start_fake('wrong-process')
        self.start_live(run_id, port, 'one')
        self.claim(run_id, self.read_run(run_id))
        target = self.live(run_id)[0]['attemptId']
        self.command(run_id, target, 'interrupt', reason='check selected process')
        self.deliver(run_id, port)
        self.assertEqual('queued', self.live(run_id)[0]['commands'][0]['state'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['operationCount'])

    def test_parallel_attempts_require_explicit_authorized_target(self):
        run_id, port = self.new_run(), self.start_fake()
        self.start_live(run_id, port, 'one')
        self.start_live(run_id, port, 'two')
        run = self.read_run(run_id)
        attempts = [a for a in run['attempts'] if a.get('liveOperation')]
        self.assertEqual(2, len(attempts), 'Both independently addressed live attempts must be observable')
        self.claim(run_id, run)
        status, decision, _ = self.command(run_id, None)
        self.assertEqual(409, status, decision)
        self.assertEqual('explicit-target-required', decision['code'])
        for actor in ('actor-observer', 'actor-contributor'):
            status, decision, _ = self.command(run_id, attempts[0]['attemptId'], actor=actor)
            self.assertEqual(403, status, decision)
        status, decision, _ = self.command(run_id, attempts[0]['attemptId'])
        self.assertEqual(202, status, decision)
        self.assertEqual(attempts[0]['attemptId'], decision['command']['attemptId'])
        unchanged = self.read_run(run_id)['attempts']
        other = next(a for a in unchanged if a['attemptId'] == attempts[1]['attemptId'])
        self.assertEqual(attempts[1], other)


if __name__ == '__main__':
    unittest.main()
