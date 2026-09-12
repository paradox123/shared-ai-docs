"""Ticket 04: external process, worker and authorized Operator HTTP/CLI seam."""
import json
import os
from pathlib import Path
import subprocess
import time
import unittest
from tests import test_control_plane_black_box as harness


class FakeCodexTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def start_fake(self, scenario="blocked", open_mode="unsupported", capability_reason=None):
        port = harness.free_port()
        database = str(Path(self.scratch.name) / f'fake-{port}.sqlite')
        arguments = ['python3', str(harness.PILOT_ROOT / 'tests/fake_codex_provider.py'),
            '--port', str(port), '--database', database, '--scenario', scenario,
            '--open-mode', open_mode]
        if capability_reason is not None:
            arguments.extend(('--capability-reason', capability_reason))
        process = subprocess.Popen(arguments, start_new_session=True,
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

    def test_adapter_capability_is_redacted_before_public_session_projection(self):
        redaction_policy = json.loads(harness.FIXTURE.read_text())['redactionPolicy']
        secret = redaction_policy['controlledCanaries'][0]['value']
        marker = redaction_policy['marker']
        run_id, port = self.new_run(), self.start_fake(capability_reason=secret)
        worker = self.run_fake(run_id, port)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        status, run, raw = self.request('GET', f'/api/v1/runs/{run_id}', actor_id='actor-observer')
        self.assertEqual(200, status, raw)
        attempt = next(item for item in run['attempts'] if item.get('session'))
        self.assertEqual(marker, attempt['session']['openInCodex']['reason'])
        self.assertTrue(run['redaction']['occurred'])
        self.assertEqual(redaction_policy['version'], run['redaction']['policyVersion'])
        path = f"/api/v1/runs/{run_id}/attempts/{attempt['attemptId']}"
        status, detail, detail_raw = self.request('GET', path, actor_id='actor-observer')
        self.assertEqual(200, status, detail_raw)
        self.assertEqual(marker, detail['attempt']['session']['openInCodex']['reason'])
        _, history, history_raw = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
        started = next(event for event in history['events'] if event['eventType'] == 'AgentSessionStarted')
        self.assertTrue(started['redaction']['occurred'])
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        exit_code, selected, selected_raw = self.operator_cli(
            'attempt', '--run-id', run_id, '--attempt-id', attempt['attemptId'], '--actor-id', 'actor-observer')
        self.assertEqual(0, exit_code, selected_raw)
        self.assertEqual(marker, selected['attempt']['session']['openInCodex']['reason'])
        for surface in (raw, detail_raw, history_raw, selected_raw, worker.stdout, worker.stderr):
            self.assertNotIn(secret, surface)

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

    def fence(self, run):
        control = run['control']
        return (
            '--target-attempt-id', control['targetAttemptId'],
            '--expected-run-version', str(control['runVersion']),
            '--expected-head-sha', control['headSha'] or 'null',
            '--lease-epoch', str(control['leaseEpoch']),
        )

    def claim(self, run_id, run):
        exit_code, decision, _ = self.operator_cli(
            'claim', '--run-id', run_id, '--actor-id', 'actor-authorized', *self.fence(run))
        self.assertEqual(0, exit_code, decision)
        self.assertEqual('control-lease-claimed', decision['code'])
        return decision['current']

    def continuation(self, run_id, action, request, control, command_id, *extra):
        return self.operator_cli(
            action, '--run-id', run_id, '--actor-id', 'actor-authorized', *self.fence({'control': control}),
            '--request-id', request['requestId'], '--command-id', command_id, *extra)

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
        self.assertEqual(self.read_run(run_id)['control'], detail['control'])
        self.assertIn('repositoryExecution', detail)
        self.assertIn('effects', detail)
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

    def test_blocked_attempt_persists_human_request_across_api_restart(self):
        run_id, port = self.new_run(), self.start_fake()
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        before = self.agent_attempt(run_id)
        request = before['session']['humanRequest']
        self.assertEqual('open', request['state'])
        self.assertEqual(before['attemptId'], request['attemptId'])
        self.assertEqual(before['session']['sessionId'], request['sessionId'])
        self.assertEqual('awaiting-human', request['phase'])
        self.assertIn('resume', request['allowedActions'])
        self.assertIn('fork', request['allowedActions'])
        self.assertIn('fresh-retry', request['allowedActions'])
        self.assertTrue(request['evidence'])

        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        after = self.agent_attempt(run_id)
        self.assertEqual(request, after['session']['humanRequest'])

    def test_resume_fork_and_fresh_retry_are_publicly_fenced_and_exactly_once(self):
        import uuid
        for action in ('resume', 'fork', 'fresh-retry'):
            with self.subTest(action=action):
                run_id, port = self.new_run(), self.start_fake(open_mode='same-session')
                self.assertEqual(0, self.run_fake(run_id, port).returncode)
                before = self.read_run(run_id)
                source = self.agent_attempt(run_id)
                request = source['session']['humanRequest']
                claimed = self.claim(run_id, before)
                command_id = str(uuid.uuid4())
                exit_code, decision, raw = self.continuation(
                    run_id, action, request, claimed, command_id)
                self.assertEqual(0, exit_code, raw)
                self.assertEqual('continuation-applied', decision['code'])
                operation = decision['continuation']
                self.assertEqual('applied', operation['state'])
                self.assertEqual(source['attemptId'], operation['sourceAttemptId'])
                self.assertEqual(source['session']['sessionId'], operation['sourceSessionId'])

                # The original request's fences are stale now.  The same command
                # must nevertheless replay the durable outcome, not create a second
                # adapter-side session or history branch.
                replay_exit, replay, replay_raw = self.continuation(
                    run_id, action, request, claimed, command_id)
                self.assertEqual(0, replay_exit, replay_raw)
                self.assertEqual(operation, replay['continuation'])
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, diagnostics['continuationCount'])

                after = self.read_run(run_id)
                if action == 'resume':
                    self.assertEqual(source['attemptId'], operation['resultAttemptId'])
                    self.assertEqual(source['session']['sessionId'], operation['resultSessionId'])
                else:
                    target = next(a for a in after['attempts'] if a['attemptId'] == operation['resultAttemptId'])
                    self.assertNotEqual(source['session']['sessionId'], target['session']['sessionId'])
                    lineage = target['session']['lineage']
                    if action == 'fork':
                        self.assertEqual(source['session']['sessionId'], lineage['parentSessionId'])
                        self.assertEqual('fork', lineage['origin'])
                    else:
                        self.assertIsNone(lineage['parentSessionId'])
                        self.assertIsNone(lineage['origin'])
                        self.assertEqual([], target['session']['humanRequest']['evidence'])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertEqual(1, sum(event['eventType'] == 'HumanRequestContinuationApplied'
                    for event in history['events']))

    def test_continuation_adapter_receipts_are_bound_to_the_operation_and_new_session(self):
        import uuid
        cases = (
            ('fork', 'same-session', 'continuation-wrong-operation'),
            ('fork', 'same-session', 'continuation-reuses-source-session'),
            ('fresh-retry', 'same-session', 'continuation-reuses-source-session'),
            ('handoff', 'handoff-confirmation-required', 'continuation-reuses-source-session'),
        )
        for action, open_mode, scenario in cases:
            with self.subTest(action=action, scenario=scenario):
                run_id, port = self.new_run(), self.start_fake(scenario=scenario, open_mode=open_mode)
                self.assertEqual(0, self.run_fake(run_id, port).returncode)
                source = self.agent_attempt(run_id)
                request = source['session']['humanRequest']
                claimed = self.claim(run_id, self.read_run(run_id))
                exit_code, rejected, raw = self.continuation(
                    run_id, action, request, claimed, str(uuid.uuid4()))
                self.assertEqual(1, exit_code, raw)
                self.assertEqual('invalid-session-adapter-receipt', rejected['code'])
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, diagnostics['continuationCount'])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertEqual(0, sum(event['eventType'] == 'HumanRequestContinuationApplied'
                    for event in history['events']))

    def test_worker_redelivery_keeps_the_original_fake_attempt_after_a_fork(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake(open_mode='same-session')
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        source = self.agent_attempt(run_id)
        request = source['session']['humanRequest']
        claimed = self.claim(run_id, self.read_run(run_id))
        fork_exit, forked, fork_raw = self.continuation(
            run_id, 'fork', request, claimed, str(uuid.uuid4()))
        self.assertEqual(0, fork_exit, fork_raw)
        target_id = forked['continuation']['resultAttemptId']
        before = self.read_run(run_id)
        original_before = next(attempt for attempt in before['attempts']
            if attempt['attemptId'] == source['attemptId'])
        target_before = next(attempt for attempt in before['attempts']
            if attempt['attemptId'] == target_id)

        redelivery = self.run_fake(run_id, port)
        self.assertEqual(0, redelivery.returncode, redelivery.stdout + redelivery.stderr)
        after = self.read_run(run_id)
        original_after = next(attempt for attempt in after['attempts']
            if attempt['attemptId'] == source['attemptId'])
        target_after = next(attempt for attempt in after['attempts']
            if attempt['attemptId'] == target_id)
        self.assertEqual(before['state'], after['state'])
        self.assertEqual(original_before, original_after)
        self.assertEqual(target_before, target_after)
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['sessionCount'])
        self.assertEqual(1, diagnostics['continuationCount'])

    def test_opening_and_writing_the_selected_same_session_are_truthful_and_fenced(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake(open_mode='same-session')
        redaction_policy = json.loads(harness.FIXTURE.read_text())['redactionPolicy']
        secret = redaction_policy['controlledCanaries'][0]['value']
        second_secret = redaction_policy['controlledCanaries'][1]['value']
        marker = redaction_policy['marker']
        message = 'continue with ' + secret
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        before = self.read_run(run_id)
        source = self.agent_attempt(run_id)
        request = source['session']['humanRequest']
        self.assertNotIn('handoff', request['allowedActions'])
        open_command = str(uuid.uuid4())
        open_exit, opened, open_raw = self.operator_cli(
            'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
            '--request-id', request['requestId'], '--command-id', open_command,
            '--actor-id', 'actor-observer')
        self.assertEqual(0, open_exit, open_raw)
        self.assertEqual('applied', opened['operation']['state'])
        self.assertEqual('same-session', opened['capability']['mode'])
        after_open = self.read_run(run_id)
        selected = self.agent_attempt(run_id)
        self.assertEqual(before['state'], after_open['state'])
        self.assertEqual(before['control']['headSha'], after_open['control']['headSha'])
        self.assertEqual(source['session']['sessionId'], selected['session']['sessionId'])
        self.assertTrue(selected['session']['openedInCodex'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['openCount'])
        replay_exit, replay, replay_raw = self.operator_cli(
            'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
            '--request-id', request['requestId'], '--command-id', open_command,
            '--actor-id', 'actor-observer')
        self.assertEqual(0, replay_exit, replay_raw)
        self.assertEqual(opened['operation'], replay['operation'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['openCount'])

        claimed = self.claim(run_id, after_open)
        write_command = str(uuid.uuid4())
        write_exit, written, write_raw = self.continuation(
            run_id, 'write', request, claimed, write_command, '--message', message)
        self.assertEqual(0, write_exit, write_raw)
        self.assertEqual('continuation-applied', written['code'])
        self.assertEqual('applied', written['continuation']['state'])
        receipt_exit, receipt, receipt_raw = self.operator_cli(
            'continuation', '--run-id', run_id, '--command-id', write_command,
            '--actor-id', 'actor-observer')
        self.assertEqual(0, receipt_exit, receipt_raw)
        self.assertEqual(written['continuation'], receipt['operation'])
        self.assertEqual('continue with ' + marker, receipt['adapterReceipt']['message'])
        self.assertEqual(['message', 'tool-call', 'tool-result'],
            [event['type'] for event in receipt['adapterReceipt']['events']])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['interactionCount'])
        duplicate_exit, duplicate, duplicate_raw = self.continuation(
            run_id, 'write', request, claimed, write_command, '--message', 'continue with ' + second_secret)
        self.assertEqual(0, duplicate_exit, duplicate_raw)
        self.assertEqual(written['continuation'], duplicate['continuation'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['interactionCount'])

        current = written['current']
        stale = {
            'targetAttemptId': current['targetAttemptId'],
            'expectedRunVersion': current['runVersion'] - 1,
            'expectedHeadSha': current['headSha'],
            'leaseEpoch': current['leaseEpoch'],
            'requestId': request['requestId'],
            'commandId': str(uuid.uuid4()),
            'message': 'stale write',
        }
        status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/write', stale)
        self.assertEqual(409, status)
        self.assertEqual('stale-run-version', rejected['code'])
        status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/write',
            dict(stale, expectedRunVersion=current['runVersion'], commandId=str(uuid.uuid4()), message='other holder'),
            actor_id='actor-contributor')
        self.assertEqual(409, status)
        self.assertEqual('control-lease-required', rejected['code'])
        status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/write',
            dict(stale, expectedRunVersion=current['runVersion'], commandId=str(uuid.uuid4()),
                 requestId=str(uuid.uuid4()), message='wrong request'))
        self.assertEqual(409, status)
        self.assertEqual('human-request-not-open', rejected['code'])
        status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/write',
            dict(stale, expectedRunVersion=current['runVersion'], commandId=str(uuid.uuid4()), message=''))
        self.assertEqual(400, status)
        self.assertEqual('invalid-control-mutation', rejected['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['interactionCount'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        requested = next(event for event in history['events']
            if event['eventType'] == 'AgentInteractiveWriteRequested')
        self.assertTrue(requested['redaction']['occurred'])
        self.assertEqual(redaction_policy['version'], requested['redaction']['policyVersion'])
        self.assertEqual(marker, requested['redaction']['marker'])
        interaction = [event for event in history['events']
            if event['eventType'] == 'AgentInteractiveObservation']
        self.assertEqual(['message', 'tool-call', 'tool-result'],
            [event['payload']['type'] for event in interaction])
        self.assertTrue(all(event['payload']['attemptId'] == source['attemptId'] for event in interaction))
        run_after_write = self.read_run(run_id)
        self.assertTrue(run_after_write['redaction']['occurred'])
        self.assertEqual(redaction_policy['version'], run_after_write['redaction']['policyVersion'])
        self.assertEqual(marker, run_after_write['redaction']['marker'])
        for surface in (write_raw, receipt_raw, duplicate_raw, json.dumps(history), json.dumps(diagnostics)):
            self.assertNotIn(secret, surface)
            self.assertNotIn(second_secret, surface)

    def test_open_and_write_receipts_must_match_the_durable_operation(self):
        import uuid
        for scenario, action in (('open-wrong-operation', 'open'), ('interaction-wrong-operation', 'write'),
                                 ('interaction-wrong-message', 'write')):
            with self.subTest(scenario=scenario):
                run_id, port = self.new_run(), self.start_fake(scenario=scenario, open_mode='same-session')
                self.assertEqual(0, self.run_fake(run_id, port).returncode)
                source = self.agent_attempt(run_id)
                request = source['session']['humanRequest']
                if action == 'open':
                    exit_code, rejected, raw = self.operator_cli(
                        'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
                        '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
                        '--actor-id', 'actor-observer')
                    event_type = 'CodexSessionOpened'
                    diagnostics_key = 'openCount'
                else:
                    opened_exit, _, opened_raw = self.operator_cli(
                        'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
                        '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
                        '--actor-id', 'actor-observer')
                    self.assertEqual(0, opened_exit, opened_raw)
                    claimed = self.claim(run_id, self.read_run(run_id))
                    exit_code, rejected, raw = self.continuation(
                        run_id, 'write', request, claimed, str(uuid.uuid4()), '--message', 'bind this write')
                    event_type = 'AgentInteractiveWriteApplied'
                    diagnostics_key = 'interactionCount'
                self.assertEqual(1, exit_code, raw)
                self.assertEqual('invalid-session-adapter-receipt', rejected['code'])
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, diagnostics[diagnostics_key])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertEqual(0, sum(event['eventType'] == event_type for event in history['events']))
                if action == 'write':
                    self.assertEqual(0, sum(event['eventType'] == 'AgentInteractiveObservation'
                        for event in history['events']))

    def test_completion_receipts_require_the_adapter_contract_version(self):
        import uuid
        cases = (
            ('continuation-contract-incompatible', 'fork', 'HumanRequestContinuationApplied', 'continuationCount'),
            ('open-contract-incompatible', 'open', 'CodexSessionOpened', 'openCount'),
            ('interaction-contract-incompatible', 'write', 'AgentInteractiveWriteApplied', 'interactionCount'),
        )
        for scenario, action, event_type, diagnostics_key in cases:
            with self.subTest(scenario=scenario):
                run_id, port = self.new_run(), self.start_fake(scenario=scenario, open_mode='same-session')
                self.assertEqual(0, self.run_fake(run_id, port).returncode)
                source = self.agent_attempt(run_id)
                request = source['session']['humanRequest']
                if action == 'fork':
                    claimed = self.claim(run_id, self.read_run(run_id))
                    exit_code, rejected, raw = self.continuation(
                        run_id, action, request, claimed, str(uuid.uuid4()))
                elif action == 'open':
                    exit_code, rejected, raw = self.operator_cli(
                        'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
                        '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
                        '--actor-id', 'actor-observer')
                else:
                    opened_exit, _, opened_raw = self.operator_cli(
                        'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
                        '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
                        '--actor-id', 'actor-observer')
                    self.assertEqual(0, opened_exit, opened_raw)
                    claimed = self.claim(run_id, self.read_run(run_id))
                    exit_code, rejected, raw = self.continuation(
                        run_id, action, request, claimed, str(uuid.uuid4()), '--message', 'contract-bound write')
                self.assertEqual(1, exit_code, raw)
                self.assertEqual('invalid-session-adapter-receipt', rejected['code'])
                _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
                self.assertEqual(1, diagnostics[diagnostics_key])
                _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                self.assertEqual(0, sum(event['eventType'] == event_type for event in history['events']))
                if action == 'write':
                    self.assertEqual(0, sum(event['eventType'] == 'AgentInteractiveObservation'
                        for event in history['events']))

    def test_session_open_requires_read_authorization_without_adapter_effect(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake(open_mode='same-session')
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        source = self.agent_attempt(run_id)
        request = source['session']['humanRequest']
        for actor, expected_code in (('actor-unauthorized', 'repository-access-denied'),
                                     ('worker-bot', 'human-identity-required')):
            with self.subTest(actor=actor):
                exit_code, rejected, raw = self.operator_cli(
                    'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
                    '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
                    '--actor-id', actor)
                self.assertEqual(1, exit_code, raw)
                self.assertEqual(expected_code, rejected['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(0, diagnostics['openCount'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(0, sum(event['eventType'] == 'CodexSessionOpenRequested' for event in history['events']))

    def test_open_limitation_requires_a_separate_fenced_handoff(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake(open_mode='handoff-confirmation-required')
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        source = self.agent_attempt(run_id)
        request = source['session']['humanRequest']
        self.assertIn('handoff', request['allowedActions'])
        open_exit, limited, open_raw = self.operator_cli(
            'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
            '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
            '--actor-id', 'actor-observer')
        self.assertEqual(0, open_exit, open_raw)
        self.assertEqual('limitation', limited['operation']['state'])
        self.assertEqual('handoff-confirmation-required', limited['capability']['mode'])
        self.assertEqual('controlled-fake-requires-explicit-handoff', limited['capability']['reason'])
        limited_run = self.read_run(run_id)
        self.assertEqual(1, len([attempt for attempt in limited_run['attempts'] if attempt.get('session')]))
        self.assertEqual(source['session']['sessionId'], self.agent_attempt(run_id)['session']['sessionId'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(0, diagnostics['openCount'])
        self.assertEqual(0, diagnostics['continuationCount'])

        claimed = self.claim(run_id, limited_run)
        handoff_exit, handoff, handoff_raw = self.continuation(
            run_id, 'handoff', request, claimed, str(uuid.uuid4()))
        self.assertEqual(0, handoff_exit, handoff_raw)
        self.assertEqual('continuation-applied', handoff['code'])
        operation = handoff['continuation']
        target = next(attempt for attempt in self.read_run(run_id)['attempts']
            if attempt['attemptId'] == operation['resultAttemptId'])
        self.assertEqual('handoff', target['session']['lineage']['origin'])
        self.assertEqual(source['session']['sessionId'], target['session']['lineage']['parentSessionId'])
        self.assertNotEqual(source['session']['sessionId'], target['session']['sessionId'])
        target_request = target['session']['humanRequest']
        self.assertEqual(operation['resultRequestId'], target_request['requestId'])
        open_exit, opened, opened_raw = self.operator_cli(
            'open', '--run-id', run_id, '--attempt-id', target['attemptId'],
            '--request-id', target_request['requestId'], '--command-id', str(uuid.uuid4()),
            '--actor-id', 'actor-observer')
        self.assertEqual(0, open_exit, opened_raw)
        self.assertEqual('applied', opened['operation']['state'])
        self.assertEqual(target['session']['sessionId'], opened['operation']['sourceSessionId'])
        self.assertEqual('same-session', opened['capability']['mode'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['continuationCount'])
        self.assertEqual(1, diagnostics['openCount'])

    def test_api_replacement_adopts_a_continuation_success_gap_once(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake(
            scenario='continuation-success-gap', open_mode='same-session')
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        before = self.read_run(run_id)
        source = self.agent_attempt(run_id)
        request = source['session']['humanRequest']
        claimed = self.claim(run_id, before)
        command_id = str(uuid.uuid4())
        first_exit, first, _ = self.continuation(
            run_id, 'fork', request, claimed, command_id)
        self.assertEqual(1, first_exit)
        self.assertEqual('session-adapter-unavailable', first['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['continuationCount'])
        pending_payload = {
            'targetAttemptId': claimed['targetAttemptId'],
            'expectedRunVersion': claimed['runVersion'],
            'expectedHeadSha': claimed['headSha'],
            'leaseEpoch': claimed['leaseEpoch'],
            'requestId': request['requestId'],
            'commandId': command_id,
        }
        status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/fork',
            pending_payload, actor_id='actor-contributor')
        self.assertEqual(409, status)
        self.assertEqual('control-lease-required', rejected['code'])
        status, rejected, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/fork', pending_payload)
        self.assertEqual(409, status)
        self.assertEqual('stale-target-attempt', rejected['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['continuationCount'])

        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        retry_exit, retry, retry_raw = self.continuation(
            run_id, 'fork', request, claimed, command_id)
        self.assertEqual(0, retry_exit, retry_raw)
        self.assertEqual('continuation-applied', retry['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['continuationCount'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(1, sum(event['eventType'] == 'HumanRequestContinuationApplied'
            for event in history['events']))

    def test_api_replacement_adopts_an_interaction_success_gap_once(self):
        import uuid
        run_id, port = self.new_run(), self.start_fake(
            scenario='interaction-success-gap', open_mode='same-session')
        self.assertEqual(0, self.run_fake(run_id, port).returncode)
        source = self.agent_attempt(run_id)
        request = source['session']['humanRequest']
        open_exit, _, open_raw = self.operator_cli(
            'open', '--run-id', run_id, '--attempt-id', source['attemptId'],
            '--request-id', request['requestId'], '--command-id', str(uuid.uuid4()),
            '--actor-id', 'actor-observer')
        self.assertEqual(0, open_exit, open_raw)
        claimed = self.claim(run_id, self.read_run(run_id))
        command_id = str(uuid.uuid4())
        first_exit, first, _ = self.continuation(
            run_id, 'write', request, claimed, command_id, '--message', 'recover this message')
        self.assertEqual(1, first_exit)
        self.assertEqual('session-adapter-unavailable', first['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['interactionCount'])

        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        retry_exit, retry, retry_raw = self.continuation(
            run_id, 'write', request, claimed, command_id, '--message', 'recover this message')
        self.assertEqual(0, retry_exit, retry_raw)
        self.assertEqual('continuation-applied', retry['code'])
        _, diagnostics, _ = self.request('GET', '/diagnostics', port=port)
        self.assertEqual(1, diagnostics['interactionCount'])
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        self.assertEqual(1, sum(event['eventType'] == 'AgentInteractiveWriteApplied'
            for event in history['events']))

    def test_concurrent_api_schema_replacements_remain_available(self):
        cls = type(self)
        processes = []
        for _ in range(2):
            port = harness.free_port(excluded={cls.api_port})
            environment = {
                **os.environ,
                'WPCP_FIXTURE_ACCESS_TOKEN': cls.fixture_access_token,
                'WPCP_GITHUB_TEST_ORIGIN': cls.provider.origin,
            }
            process = subprocess.Popen([
                'dotnet', str(harness.API_DLL), '--connection-string', cls.connection_string,
                '--fixture', str(cls.fixture_path), '--urls', f'http://127.0.0.1:{port}',
            ], cwd=harness.PILOT_ROOT, env=environment, start_new_session=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.addCleanup(self.stop_process, process)
            processes.append((port, process))
        for port, process in processes:
            for _ in range(100):
                status, _, _ = self.request('GET', '/healthz', port=port)
                if status == 200:
                    break
                if process.poll() is not None:
                    self.fail('concurrent API replacement exited during schema evolution')
                time.sleep(.05)
            else:
                self.fail('concurrent API replacement never became healthy')

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
